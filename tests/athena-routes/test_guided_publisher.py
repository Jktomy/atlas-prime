from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools.athena_routes.guided_publisher import (
    EXECUTE_SCHEMA,
    PREVIEW_SCHEMA,
    GuidedPublisherError,
    build_preview,
    execute_preview,
)
from tools.athena_routes.hosted import sha256_bytes, stable_json
from tools.athena_routes.hosted import expected_mission_branch
from tools.athena_routes.schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]
MAIN = "1" * 40
WORKFLOW_BLOB = "2" * 40
BRANCH = expected_mission_branch("RP-C01-GUIDED-PROOF-R01", MAIN)
MISSION_SHA = "4" * 64
CANDIDATE_TREE_SHA = "8" * 64
FINAL_PATHSET_SHA = "9" * 64


class FakeRunner:
    def __init__(self, *, main: str = MAIN, actor: str = "Jktomy", run_head: str = MAIN, branch_exists: bool = False, prior_pr: bool = False) -> None:
        self.main = main
        self.actor = actor
        self.run_head = run_head
        self.branch_exists = branch_exists
        self.prior_pr = prior_pr
        self.calls: list[tuple[list[str], str | None]] = []

    def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        input_text = kwargs.get("input")
        self.calls.append((list(args), input_text if isinstance(input_text, str) else None))
        joined = " ".join(args)
        if "repos/Jktomy/atlas-prime/commits/main" in joined:
            output = self.main
        elif "repos/Jktomy/atlas-prime/contents/.github/workflows/athena-bow-hosted.yml" in joined:
            output = WORKFLOW_BLOB
        elif args[-4:] == ["gh", "api", "user", "--jq"]:
            output = self.actor
        elif args[:4] == ["gh", "api", "user", "--jq"]:
            output = self.actor
        elif "repos/Jktomy/atlas-prime/git/ref/heads/" in joined:
            if self.branch_exists:
                return subprocess.CompletedProcess(args, 0, stdout="{}", stderr="")
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="HTTP 404: Not Found")
        elif args[:3] == ["gh", "pr", "list"]:
            output = '[{"number":99,"state":"CLOSED"}]' if self.prior_pr else "[]"
        elif args[:3] == ["gh", "workflow", "run"]:
            output = "https://github.com/Jktomy/atlas-prime/actions/runs/123"
        elif "repos/Jktomy/atlas-prime/actions/runs/123" in joined:
            output = json.dumps({
                "id": 123,
                "event": "workflow_dispatch",
                "head_sha": self.run_head,
                "actor": {"login": "Jktomy"},
                "triggering_actor": {"login": "Jktomy"},
            })
        else:
            raise AssertionError(f"unexpected command: {args}")
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")


def fake_package(*, base: str = MAIN, path: str = "proof/repairing-prime/guided-proof.md") -> SimpleNamespace:
    payload = b"# public clean guided proof\n"
    return SimpleNamespace(
        manifest_sha256="6" * 64,
        weave_sha256="7" * 64,
        weave={
            "base_sha": base,
            "weave_id": "RP-C01-GUIDED-PROOF-R01",
            "branch": BRANCH,
            "threads": [{
                "operation": "ADD",
                "path": path,
                "payload": "guided-proof.md",
            }],
        },
        payloads={"PAYLOADS/guided-proof.md": payload},
    )


def compiler_receipt(*_args: object, **kwargs: object) -> dict[str, object]:
    from pathlib import PurePosixPath

    from production_adapter.protected_paths import is_protected_path

    if is_protected_path(PurePosixPath("lifecycle/feathers/example.json")):
        raise AssertionError("guided compiler call lacks safe-declared scope")
    output_dir = kwargs["output_dir"]
    assert isinstance(output_dir, Path)
    output_dir.mkdir(parents=True, exist_ok=True)
    mission_name = "rp-c01-guided-proof-r01-mission.json"
    receipt_name = "rp-c01-guided-proof-r01-compile-receipt.json"
    payload_name = "PAYLOADS/guided-proof.md"
    mission = {
        "mission_sha256": MISSION_SHA,
        "candidate_tree_sha256": CANDIDATE_TREE_SHA,
        "final_pathset_sha256": FINAL_PATHSET_SHA,
    }
    mission_bytes = stable_json(mission).encode("utf-8")
    (output_dir / mission_name).write_bytes(mission_bytes)
    (output_dir / "PAYLOADS").mkdir()
    (output_dir / payload_name).write_bytes(b"# public clean guided proof\n")
    receipt: dict[str, object] = {
        "schema_version": "atlas-thread-engine-spear-compile-receipt-v1",
        "mission_sha256": MISSION_SHA,
        "compile_receipt_filename": receipt_name,
        "output_mission_filename": mission_name,
        "output_mission_sha256": sha256_bytes(mission_bytes),
        "output_inventory": [payload_name, receipt_name, mission_name],
    }
    (output_dir / receipt_name).write_text(stable_json(receipt), encoding="utf-8", newline="\n")
    return receipt


class GuidedPublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.carrier = self.root / "carrier.zip"
        self.carrier.write_bytes(b"immutable public-clean carrier")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def preview(self, *, runner: FakeRunner | None = None, package: SimpleNamespace | None = None) -> tuple[dict, FakeRunner]:
        selected_runner = runner or FakeRunner()
        selected_package = package or fake_package()
        receipt = build_preview(
            self.carrier,
            runner=selected_runner,
            package_reader=lambda _path, expected: selected_package
            if expected == sha256_bytes(self.carrier.read_bytes())
            else None,
            compiler=compiler_receipt,
        )
        return receipt, selected_runner

    def test_preview_is_closed_canonical_and_read_only(self) -> None:
        receipt, runner = self.preview()
        schema = json.loads(PREVIEW_SCHEMA.read_text(encoding="utf-8"))
        validate_schema(schema, receipt)
        self.assertEqual(receipt["canonical_main_sha"], MAIN)
        self.assertEqual(receipt["mission_sha256"], MISSION_SHA)
        self.assertEqual(receipt["candidate_tree_sha256"], CANDIDATE_TREE_SHA)
        self.assertEqual(receipt["final_pathset_sha256"], FINAL_PATHSET_SHA)
        self.assertEqual(len(receipt["compiled_inventory"]), 3)
        compiled = {item["path"]: item["sha256"] for item in receipt["compiled_inventory"]}
        self.assertEqual(compiled[receipt["compile_receipt_filename"]], receipt["compile_receipt_sha256"])
        self.assertEqual(compiled[receipt["output_mission_filename"]], receipt["output_mission_sha256"])
        self.assertEqual(receipt["deterministic_branch"], BRANCH)
        self.assertEqual(receipt["paths"][0]["payload_sha256"], sha256_bytes(b"# public clean guided proof\n"))
        self.assertTrue(all(value is False for value in receipt["forbidden_actions"].values()))
        self.assertTrue(all(call[0][:2] in (["gh", "api"], ["gh", "pr"]) for call in runner.calls))

    def test_preview_rejects_stale_base_before_compile(self) -> None:
        with self.assertRaisesRegex(GuidedPublisherError, "canonical main") as caught:
            self.preview(package=fake_package(base="8" * 40))
        self.assertEqual(caught.exception.code, "STALE_BASE")

    def test_preview_rejects_generated_source(self) -> None:
        with self.assertRaises(GuidedPublisherError) as caught:
            self.preview(package=fake_package(path="generated/atlas-file-inventory.md"))
        self.assertEqual(caught.exception.code, "GENERATED_SOURCE_MIXING")

    def test_preview_accepts_thread_engine_self_change(self) -> None:
        receipt, _ = self.preview(package=fake_package(path="tools/thread-engine/engine/thread_engine.py"))
        self.assertEqual(receipt["path_classification"], "SAFE_DECLARED")

    def test_preview_rejects_nondeterministic_branch_and_replay(self) -> None:
        wrong_branch = fake_package()
        wrong_branch.weave["branch"] = "source/athena-bow-" + "f" * 20
        with self.assertRaises(GuidedPublisherError) as mismatch:
            self.preview(package=wrong_branch)
        self.assertEqual(mismatch.exception.code, "GUIDED_BRANCH_MISMATCH")
        for runner, code in (
            (FakeRunner(branch_exists=True), "REPLAY_BRANCH_EXISTS"),
            (FakeRunner(prior_pr=True), "REPLAY_PR_EXISTS"),
        ):
            with self.subTest(code=code):
                with self.assertRaises(GuidedPublisherError) as caught:
                    self.preview(runner=runner)
                self.assertEqual(caught.exception.code, code)

    def test_execute_requires_exact_preview_confirmation(self) -> None:
        preview, runner = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        with self.assertRaises(GuidedPublisherError) as caught:
            execute_preview(
                path,
                self.carrier,
                self.root / "execute-invalid-confirmation.json",
                confirmed_preview_sha256="9" * 64,
                launch_nonce="guided-launch-nonce-000001",
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                runner=runner,
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(caught.exception.code, "PREVIEW_CONFIRMATION_MISMATCH")

    def test_execute_revalidates_and_dispatches_only_json_stdin(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        digest = sha256_bytes(path.read_bytes())
        runner = FakeRunner()
        receipt = execute_preview(
            path,
            self.carrier,
            self.root / "execute-dispatched.json",
            confirmed_preview_sha256=digest,
            launch_nonce="guided-launch-nonce-000002",
            public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            runner=runner,
            package_reader=lambda _path, _sha: fake_package(),
            compiler=compiler_receipt,
        )
        validate_schema(json.loads(EXECUTE_SCHEMA.read_text(encoding="utf-8")), receipt)
        dispatch_calls = [call for call in runner.calls if call[0][:3] == ["gh", "workflow", "run"]]
        self.assertEqual(len(dispatch_calls), 1)
        args, input_text = dispatch_calls[0]
        self.assertNotIn("arrow_b64", " ".join(args))
        self.assertNotIn(self.carrier.read_bytes().decode("ascii"), " ".join(args))
        submitted = json.loads(input_text or "null")
        self.assertEqual(submitted["arrow_sha256"], preview["carrier_sha256"])
        self.assertEqual(submitted["mission_lock_sha256"], preview["mission_lock_sha256"])
        self.assertEqual(receipt["preview_sha256"], digest)
        self.assertEqual(receipt["workflow_run_id"], 123)
        self.assertEqual(receipt["dispatch_transport"], "GH_WORKFLOW_JSON_STDIN")

    def test_execute_rejects_nonowner_and_preserves_run_mismatch_as_partial(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        digest = sha256_bytes(path.read_bytes())
        with self.assertRaises(GuidedPublisherError) as caught:
            execute_preview(
                path,
                self.carrier,
                self.root / "execute-nonowner.json",
                confirmed_preview_sha256=digest,
                launch_nonce="guided-launch-nonce-000003",
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                runner=FakeRunner(actor="not-owner"),
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(caught.exception.code, "OWNER_IDENTITY_REJECTED")
        partial = execute_preview(
            path,
            self.carrier,
            self.root / "execute-partial.json",
            confirmed_preview_sha256=digest,
            launch_nonce="guided-launch-nonce-000004",
            public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
            runner=FakeRunner(run_head="8" * 40),
            package_reader=lambda _path, _sha: fake_package(),
            compiler=compiler_receipt,
        )
        validate_schema(json.loads(EXECUTE_SCHEMA.read_text(encoding="utf-8")), partial)
        self.assertEqual(partial["result"], "PARTIAL")
        self.assertEqual(partial["stop_point"], "PARTIAL_STATE_PRESERVED")
        self.assertEqual(partial["rollback"], "PRESERVE_AND_REVIEW_NO_RETRY")

    def test_execute_rejects_preview_drift_and_short_nonce(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        digest = sha256_bytes(path.read_bytes())
        with self.assertRaises(GuidedPublisherError) as short_nonce:
            execute_preview(
                path,
                self.carrier,
                self.root / "execute-short-nonce.json",
                confirmed_preview_sha256=digest,
                launch_nonce="too-short",
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                runner=FakeRunner(),
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(short_nonce.exception.code, "LAUNCH_NONCE_REJECTED")
        self.carrier.write_bytes(b"edited carrier")
        with self.assertRaises(GuidedPublisherError) as drift:
            execute_preview(
                path,
                self.carrier,
                self.root / "execute-drift.json",
                confirmed_preview_sha256=digest,
                launch_nonce="guided-launch-nonce-000005",
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                runner=FakeRunner(),
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(drift.exception.code, "PREVIEW_DRIFT")

    def test_execute_requires_explicit_public_clean_confirmation(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        with self.assertRaises(GuidedPublisherError) as caught:
            execute_preview(
                path,
                self.carrier,
                self.root / "execute-privacy.json",
                confirmed_preview_sha256=sha256_bytes(path.read_bytes()),
                launch_nonce="guided-launch-nonce-000006",
                public_clean_confirmation="MISSING",
                runner=FakeRunner(),
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(caught.exception.code, "PRE_INGRESS_PRIVACY_REQUIRED")

    def test_execute_journals_partial_before_dispatch_and_on_post_dispatch_exceptions(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        digest = sha256_bytes(path.read_bytes())

        class RaisingRunner(FakeRunner):
            def __init__(self, stage: str) -> None:
                super().__init__()
                self.stage = stage

            def __call__(self, args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
                joined = " ".join(args)
                if self.stage == "dispatch" and args[:3] == ["gh", "workflow", "run"]:
                    raise OSError("ambiguous dispatch transport")
                if self.stage == "readback" and "actions/runs/123" in joined:
                    raise OSError("readback unavailable")
                return super().__call__(args, **kwargs)

        for stage, code in (("dispatch", "DISPATCH_TRANSPORT_AMBIGUOUS"), ("readback", "DISPATCH_READBACK_FAILED")):
            with self.subTest(stage=stage):
                receipt_path = self.root / f"execute-{stage}.json"
                receipt = execute_preview(
                    path,
                    self.carrier,
                    receipt_path,
                    confirmed_preview_sha256=digest,
                    launch_nonce=f"guided-launch-exception-{stage}-000001",
                    public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                    runner=RaisingRunner(stage),
                    package_reader=lambda _path, _sha: fake_package(),
                    compiler=compiler_receipt,
                )
                self.assertEqual(receipt["result"], "PARTIAL")
                self.assertEqual(receipt["error_code"], code)
                self.assertEqual(json.loads(receipt_path.read_text(encoding="utf-8")), receipt)

    def test_execute_reserves_new_sink_and_retains_intent_if_atomic_finalization_fails(self) -> None:
        preview, _ = self.preview()
        path = self.root / "preview.json"
        path.write_text(stable_json(preview), encoding="utf-8", newline="\n")
        digest = sha256_bytes(path.read_bytes())
        existing = self.root / "execute-existing.json"
        existing.write_text("do-not-overwrite\n", encoding="utf-8")
        runner = FakeRunner()
        with self.assertRaises(GuidedPublisherError) as caught:
            execute_preview(
                path,
                self.carrier,
                existing,
                confirmed_preview_sha256=digest,
                launch_nonce="guided-launch-existing-sink-000001",
                public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                runner=runner,
                package_reader=lambda _path, _sha: fake_package(),
                compiler=compiler_receipt,
            )
        self.assertEqual(caught.exception.code, "EXECUTE_RECEIPT_EXISTS")
        self.assertFalse(any(call[0][:3] == ["gh", "workflow", "run"] for call in runner.calls))

        target = self.root / "execute-finalize-failure.json"
        with patch("tools.athena_routes.guided_publisher.os.replace", side_effect=OSError("sink failure")):
            with self.assertRaises(GuidedPublisherError) as finalize:
                execute_preview(
                    path,
                    self.carrier,
                    target,
                    confirmed_preview_sha256=digest,
                    launch_nonce="guided-launch-finalize-failure-000001",
                    public_clean_confirmation="PUBLIC_CLEAN_CONFIRMED",
                    runner=FakeRunner(),
                    package_reader=lambda _path, _sha: fake_package(),
                    compiler=compiler_receipt,
                )
        self.assertEqual(finalize.exception.code, "EXECUTE_RECEIPT_FINALIZE_FAILED")
        intent = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(intent["result"], "PARTIAL")
        self.assertEqual(intent["error_code"], "DISPATCH_INTENT_JOURNALED")
        self.assertEqual(intent["rollback"], "PRESERVE_AND_REVIEW_NO_RETRY")


if __name__ == "__main__":
    unittest.main()
