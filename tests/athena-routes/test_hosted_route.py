from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]

from tools.athena_routes.hosted import (  # noqa: E402
    HostedRouteError,
    classify_paths,
    decode_carrier,
    expected_mission_branch,
    privacy_scan,
    preflight_hosted,
    required_environment,
    run_hosted,
    safe_error_code,
)


def base_environment(event_path: Path, carrier_sha256: str) -> dict[str, str]:
    return {
        "GITHUB_REPOSITORY": "Jktomy/atlas-prime",
        "GITHUB_REPOSITORY_OWNER": "Jktomy",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_EVENT_PATH": str(event_path),
        "GITHUB_ACTOR": "Jktomy",
        "GITHUB_TRIGGERING_ACTOR": "Jktomy",
        "GITHUB_WORKFLOW_REF": "Jktomy/atlas-prime/.github/workflows/athena-bow-hosted.yml@refs/heads/main",
        "GITHUB_WORKFLOW_SHA": "a" * 40,
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "1",
        "ATHENA_ARROW_SHA256": carrier_sha256,
        "ATHENA_PUBLIC_CLEAN_CONFIRMATION": "PUBLIC_CLEAN_CONFIRMED",
    }


def run_metadata() -> dict:
    return {
        "id": 12345,
        "run_attempt": 1,
        "created_at": "2026-07-12T00:00:00Z",
        "updated_at": "2026-07-12T00:00:01Z",
        "actor": {"login": "Jktomy"},
        "triggering_actor": {"login": "Jktomy"},
    }


def package(carrier_sha256: str, path: str = "proof/repairing-prime/hosted-bow-pilot-r01.txt") -> SimpleNamespace:
    mission_id = "RP-C01-HOSTED-BOW-PILOT-R01"
    base_sha = "b" * 40
    return SimpleNamespace(
        carrier_sha256=carrier_sha256,
        weave={
            "weave_id": mission_id,
            "base_sha": base_sha,
            "branch": expected_mission_branch(mission_id, base_sha),
            "threads": [{"path": path, "operation": "ADD", "payload": "pilot.txt", "thread_id": "pilot"}],
        },
        payloads={"PAYLOADS/pilot.txt": b"Repairing Prime hosted Bow harmless pilot.\n"},
    )


class FakeAdapterError(Exception):
    def __init__(self, receipt: dict, code: str = "ADAPTER_FAILURE") -> None:
        super().__init__(code)
        self.receipt = receipt
        self.code = code


def success_engine(carrier_sha256: str, *, path: str = "proof/repairing-prime/hosted-bow-pilot-r01.txt") -> tuple:
    observed = package(carrier_sha256, path)

    def read_package(_path: Path, _sha: str) -> SimpleNamespace:
        return observed

    def compile_package(_path: Path, *, output_dir: Path, **_kwargs: object) -> dict:
        output_dir.mkdir()
        (output_dir / "mission.json").write_text("{}\n", encoding="utf-8")
        receipt = {
            "output_mission_filename": "mission.json",
            "compile_receipt_filename": "compile-receipt.json",
            "mission_sha256": "c" * 64,
            "result": "SUCCESS",
        }
        (output_dir / "compile-receipt.json").write_text(
            json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8"
        )
        return receipt

    def execute_mission(_path: Path, **_kwargs: object) -> dict:
        return {
            "result": "SUCCESS",
            "head_sha": "d" * 40,
            "pr_readback": {
                "number": 101,
                "isDraft": True,
                "headRefName": observed.weave["branch"],
                "headRefOid": "d" * 40,
            },
        }

    return FakeAdapterError, execute_mission, compile_package, read_package


class HostedRouteTests(unittest.TestCase):
    def test_only_sanitized_error_codes_cross_the_evidence_boundary(self) -> None:
        safe = HostedRouteError("private detail", "MALFORMED_CARRIER")
        unsafe = HostedRouteError("private detail", "unsafe detail: do-not-echo")
        self.assertEqual(safe_error_code(safe, "HOSTED_ROUTE_REJECTED"), "MALFORMED_CARRIER")
        self.assertEqual(safe_error_code(unsafe, "HOSTED_ROUTE_REJECTED"), "HOSTED_ROUTE_REJECTED")

    def test_strict_carrier_hash_and_size_rejections(self) -> None:
        data = b"immutable-arrow"
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual(decode_carrier(base64.b64encode(data).decode("ascii"), digest), data)
        for encoded, expected, code in (
            ("not-base64!", digest, "CARRIER_BASE64_REJECTED"),
            (base64.b64encode(data).decode("ascii"), "0" * 64, "CARRIER_SHA_REJECTED"),
            (base64.b64encode(b"x" * 48_001).decode("ascii"), hashlib.sha256(b"x" * 48_001).hexdigest(), "CARRIER_SIZE_REJECTED"),
        ):
            with self.assertRaises(HostedRouteError) as raised:
                decode_carrier(encoded, expected)
            self.assertEqual(raised.exception.code, code)

    def test_owner_event_and_pre_ingress_confirmation_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            event = Path(temporary) / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            env = base_environment(event, "0" * 64)
            required_environment(env)
            for key, value, code in (
                ("GITHUB_ACTOR", "someone-else", "OWNER_IDENTITY_REJECTED"),
                ("GITHUB_TRIGGERING_ACTOR", "someone-else", "OWNER_IDENTITY_REJECTED"),
                ("ATHENA_PUBLIC_CLEAN_CONFIRMATION", "", "TRUSTED_ENVIRONMENT_MISSING"),
            ):
                invalid = dict(env)
                invalid[key] = value
                with self.assertRaises(HostedRouteError) as raised:
                    required_environment(invalid)
                self.assertEqual(raised.exception.code, code)

    def test_hash_mismatch_receipt_records_observed_not_claimed_carrier(self) -> None:
        carrier = b"observed-arrow"
        observed = hashlib.sha256(carrier).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            result = preflight_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, "0" * 64),
                evidence_dir=root / "evidence",
                work_root=root / "work",
                run_metadata=run_metadata(),
                package_reader=lambda *_args: self.fail("hash mismatch must stop before package read"),
            )
        self.assertEqual(result["error_code"], "CARRIER_SHA_REJECTED")
        self.assertEqual(result["carrier_sha256"], observed)

    def test_route_detection_occurs_before_mutation(self) -> None:
        self.assertEqual(classify_paths(["proof/pilot.txt"]), ("ORDINARY", "ARROW_BOW_HOSTED"))
        self.assertEqual(classify_paths(["generated/atlas-file-inventory.md"]), ("GENERATED_SOURCE_MIXING", "ARROW_BOW_HOSTED"))
        self.assertEqual(classify_paths(["governance/change-routes.md"]), ("PROTECTED_AEGIS_REQUIRED", "AEGIS_BREAK_PROTECTED"))
        self.assertEqual(classify_paths(["tools/thread-engine/README.md"]), ("THREAD_ENGINE_SELF_CHANGE", "AEGIS_BREAK_TO_OATHBRINGER"))

    def test_privacy_scan_rejects_secret_shaped_payload_without_echo(self) -> None:
        clean = package("0" * 64)
        privacy_scan(clean)
        dirty = package("0" * 64)
        dirty.payloads = {"PAYLOADS/pilot.txt": b"api_key=do-not-echo"}
        with self.assertRaises(HostedRouteError) as raised:
            privacy_scan(dirty)
        self.assertEqual(raised.exception.code, "CARRIER_PRIVACY_REJECTED")
        self.assertNotIn("do-not-echo", str(raised.exception))

    def test_success_invokes_existing_compiler_and_adapter_and_stops_at_draft(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text('{"action":"workflow_dispatch"}\n', encoding="utf-8")
            receipt = run_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                receipt_path=root / "evidence" / "receipt.json",
                work_root=root / "work",
                run_metadata=run_metadata(),
                engine=success_engine(digest),
                replay_probe=lambda _branch: None,
            )
            self.assertEqual(receipt["result"], "SUCCESS")
            self.assertEqual(receipt["route"], "ARROW_BOW_HOSTED")
            self.assertEqual(receipt["stop_point"], "DRAFT_PR_READBACK")
            self.assertTrue(receipt["mutation"]["draft"])
            self.assertEqual(receipt["identity"]["token_mode"], "GITHUB_TOKEN")
            self.assertNotIn("ATHENA_ARROW_B64", json.dumps(receipt))

    def test_read_only_preflight_accepts_without_compiler_or_adapter(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        observed = package(digest)
        reads: list[str] = []

        def reader(_path: Path, _sha: str) -> SimpleNamespace:
            reads.append("package")
            return observed

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            result = preflight_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                evidence_dir=root / "evidence",
                work_root=root / "work",
                run_metadata=run_metadata(),
                package_reader=reader,
                replay_probe=lambda _branch: None,
            )
            self.assertTrue((root / "evidence" / "athena-hosted-route-request.json").is_file())
        self.assertEqual(result["result"], "ACCEPTED")
        self.assertEqual(result["stop_point"], "READ_ONLY_PREFLIGHT_COMPLETE")
        self.assertEqual(reads, ["package"])

    def test_nonowner_preflight_emits_sanitized_rejection_without_package_read(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            env = base_environment(event, digest)
            env["GITHUB_ACTOR"] = "someone-else"
            result = preflight_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=env,
                evidence_dir=root / "evidence",
                work_root=root / "work",
                run_metadata=run_metadata(),
                package_reader=lambda *_args: self.fail("non-owner carrier must not be read"),
            )
            persisted = json.loads((root / "evidence" / "athena-hosted-route-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(result["result"], "REJECTED")
        self.assertEqual(result["error_code"], "OWNER_IDENTITY_REJECTED")
        self.assertEqual(persisted["mutation"]["occurred"], False)

    def test_nondeterministic_branch_and_historical_replay_reject_pre_mutation(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            wrong_branch = package(digest)
            wrong_branch.weave["branch"] = "agent/caller-selected-branch"
            mismatch = preflight_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                evidence_dir=root / "mismatch-evidence",
                work_root=root / "mismatch-work",
                run_metadata=run_metadata(),
                package_reader=lambda *_args: wrong_branch,
                replay_probe=lambda _branch: self.fail("replay probe must follow branch validation"),
            )
            replay = preflight_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                evidence_dir=root / "replay-evidence",
                work_root=root / "replay-work",
                run_metadata=run_metadata(),
                package_reader=lambda *_args: package(digest),
                replay_probe=lambda _branch: (_ for _ in ()).throw(
                    HostedRouteError("historical PR exists", "REPLAY_PULL_REQUEST_EXISTS")
                ),
            )
        self.assertEqual(mismatch["error_code"], "REPLAY_BRANCH_MISMATCH")
        self.assertEqual(replay["error_code"], "REPLAY_PULL_REQUEST_EXISTS")
        self.assertFalse(mismatch["mutation"]["occurred"])
        self.assertFalse(replay["mutation"]["occurred"])

    def test_hosted_branch_matches_existing_thread_engine_source_namespace(self) -> None:
        branch = expected_mission_branch("RP-C01-HOSTED-BOW-PILOT-R01", "b" * 40)
        authority = (ROOT / "tools/thread-engine/production_adapter/authority.py").read_text(encoding="utf-8")
        self.assertTrue(branch.startswith("source/athena-bow-"))
        self.assertIn('branch.startswith("source/")', authority)

    def test_protected_route_blocks_before_compiler_or_adapter(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        calls: list[str] = []
        engine = list(success_engine(digest, path="governance/change-routes.md"))
        original_compile = engine[2]
        original_execute = engine[1]

        def compile_spy(*args: object, **kwargs: object) -> dict:
            calls.append("compile")
            return original_compile(*args, **kwargs)

        def execute_spy(*args: object, **kwargs: object) -> dict:
            calls.append("execute")
            return original_execute(*args, **kwargs)

        engine[1] = execute_spy
        engine[2] = compile_spy
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            receipt = run_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                receipt_path=root / "evidence" / "receipt.json",
                work_root=root / "work",
                run_metadata=run_metadata(),
                engine=tuple(engine),
                replay_probe=lambda _branch: None,
            )
        self.assertEqual(receipt["result"], "BLOCKED")
        self.assertEqual(receipt["route"], "AEGIS_BREAK_PROTECTED")
        self.assertEqual(receipt["stop_point"], "ROUTE_HANDOFF_REQUIRED")
        self.assertEqual(calls, [])

    def test_partial_adapter_state_is_preserved_and_blocks_retry(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        engine = list(success_engine(digest))

        def partial_adapter(_path: Path, **_kwargs: object) -> dict:
            raise FakeAdapterError(
                {
                    "result": "PARTIAL",
                    "error_code": "unsafe error detail",
                    "error_stage": "unsafe stage detail",
                    "branch": "agent/rp-c01-hosted-bow-pilot-r01",
                    "head_sha": "d" * 40,
                }
            )

        engine[1] = partial_adapter
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            receipt = run_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                receipt_path=root / "evidence" / "receipt.json",
                work_root=root / "work",
                run_metadata=run_metadata(),
                engine=tuple(engine),
                replay_probe=lambda _branch: None,
                remote_probe=lambda branch: {
                    "readback": "VERIFIED",
                    "branch_exists": True,
                    "head_sha": "d" * 40,
                    "pull_request": None,
                },
            )
            self.assertTrue((root / "evidence" / "thread-engine-evidence.json").is_file())
            persisted = "\n".join(path.read_text(encoding="utf-8") for path in (root / "evidence").iterdir())
        self.assertEqual(receipt["result"], "PARTIAL")
        self.assertEqual(receipt["error_code"], "THREAD_ENGINE_PARTIAL")
        self.assertEqual(receipt["stage"], "THREAD_ENGINE_PARTIAL")
        self.assertEqual(receipt["stop_point"], "PARTIAL_STATE_PRESERVED")
        self.assertEqual(receipt["rollback"]["pre_merge"], "PRESERVE_PARTIAL_STATE_AND_REVIEW")
        self.assertNotIn("unsafe error detail", persisted)
        self.assertNotIn("unsafe stage detail", persisted)

    def test_failures_after_push_and_pr_creation_are_conservative_partial(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        scenarios = (
            (
                "after-push",
                [{"checkpoint": "PUSH", "status": "completed"}, {"checkpoint": "DRAFT_PR", "status": "rejected"}],
                {"readback": "VERIFIED", "branch_exists": True, "head_sha": "d" * 40, "pull_request": None},
            ),
            (
                "after-pr",
                [{"checkpoint": "PUSH", "status": "completed"}, {"checkpoint": "DRAFT_PR", "status": "completed"}, {"checkpoint": "READBACK", "status": "rejected"}],
                {
                    "readback": "VERIFIED",
                    "branch_exists": True,
                    "head_sha": "d" * 40,
                    "pull_request": {"number": 101, "state": "OPEN", "isDraft": True, "headRefName": package(digest).weave["branch"], "headRefOid": "d" * 40},
                },
            ),
        )
        for label, checkpoints, remote in scenarios:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                event = root / "event.json"
                event.write_text("{}\n", encoding="utf-8")
                engine = list(success_engine(digest))

                def rejected_adapter(_path: Path, **_kwargs: object) -> dict:
                    raise FakeAdapterError({
                        "result": "REJECTED",
                        "error_code": "GH_COMMAND_FAILED",
                        "error_stage": "READBACK",
                        "message": "private diagnostic do-not-echo",
                        "checkpoint_results": checkpoints,
                    })

                engine[1] = rejected_adapter
                receipt = run_hosted(
                    base64.b64encode(carrier).decode("ascii"),
                    env=base_environment(event, digest),
                    receipt_path=root / "evidence" / "receipt.json",
                    work_root=root / "work",
                    run_metadata=run_metadata(),
                    engine=tuple(engine),
                    replay_probe=lambda _branch: None,
                    remote_probe=lambda _branch, observed=remote: observed,
                )
                persisted = "\n".join(path.read_text(encoding="utf-8") for path in (root / "evidence").iterdir())
                self.assertEqual(receipt["result"], "PARTIAL")
                self.assertTrue(receipt["mutation"]["occurred"])
                self.assertNotIn("private diagnostic do-not-echo", persisted)

    def test_failed_remote_absence_readback_and_post_return_failure_are_partial(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        for label, adapter, remote_probe in (
            (
                "absence-unavailable",
                lambda _path, **_kwargs: (_ for _ in ()).throw(FakeAdapterError({"result": "REJECTED", "error_code": "ADAPTER_REJECTED", "error_stage": "COMMIT", "checkpoint_results": []})),
                lambda _branch: (_ for _ in ()).throw(RuntimeError("readback unavailable")),
            ),
            (
                "post-return",
                lambda _path, **_kwargs: {"result": "SUCCESS", "head_sha": "d" * 40, "pr_readback": {"isDraft": True}},
                lambda branch: {"readback": "VERIFIED", "branch_exists": True, "head_sha": "d" * 40, "pull_request": {"number": 101, "state": "OPEN", "isDraft": True, "headRefName": branch, "headRefOid": "d" * 40}},
            ),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                event = root / "event.json"
                event.write_text("{}\n", encoding="utf-8")
                engine = list(success_engine(digest))
                engine[1] = adapter
                receipt = run_hosted(
                    base64.b64encode(carrier).decode("ascii"),
                    env=base_environment(event, digest),
                    receipt_path=root / "evidence" / "receipt.json",
                    work_root=root / "work",
                    run_metadata=run_metadata(),
                    engine=tuple(engine),
                    replay_probe=lambda _branch: None,
                    remote_probe=remote_probe,
                )
                self.assertEqual(receipt["result"], "PARTIAL")
                self.assertTrue(receipt["mutation"]["occurred"])

    def test_pre_push_failure_is_rejected_only_after_verified_absence(self) -> None:
        carrier = b"fake-arrow-zip"
        digest = hashlib.sha256(carrier).hexdigest()
        engine = list(success_engine(digest))

        def pre_push_failure(_path: Path, **_kwargs: object) -> dict:
            raise FakeAdapterError({"result": "REJECTED", "error_code": "COMMIT_REJECTED", "error_stage": "COMMIT", "checkpoint_results": []})

        engine[1] = pre_push_failure
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text("{}\n", encoding="utf-8")
            receipt = run_hosted(
                base64.b64encode(carrier).decode("ascii"),
                env=base_environment(event, digest),
                receipt_path=root / "evidence" / "receipt.json",
                work_root=root / "work",
                run_metadata=run_metadata(),
                engine=tuple(engine),
                replay_probe=lambda _branch: None,
                remote_probe=lambda _branch: {"readback": "VERIFIED", "branch_exists": False, "head_sha": None, "pull_request": None},
            )
        self.assertEqual(receipt["result"], "REJECTED")
        self.assertFalse(receipt["mutation"]["occurred"])

    def test_workflow_is_owner_only_thin_and_has_no_merge_or_force_route(self) -> None:
        workflow = (ROOT / ".github/workflows/athena-bow-hosted.yml").read_text(encoding="utf-8")
        self.assertIn("github.actor == github.repository_owner", workflow)
        self.assertIn("github.triggering_actor == github.repository_owner", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("needs: preflight", workflow)
        self.assertIn("--preflight-only", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("python -B -m tools.athena_routes.cli", workflow)
        self.assertNotRegex(workflow, r"uses:\s+[^\s]+@v\d")
        for forbidden in ("pull_request_target", "force-push", "git push", "gh pr create", "gh pr merge", "gh workflow run"):
            self.assertNotIn(forbidden, workflow)
        hosted = (ROOT / "tools/athena_routes/hosted.py").read_text(encoding="utf-8")
        for forbidden in ("git push", "gh pr create", "gh pr merge", "shell=True", "eval(", "exec("):
            self.assertNotIn(forbidden, hosted)


if __name__ == "__main__":
    unittest.main()
