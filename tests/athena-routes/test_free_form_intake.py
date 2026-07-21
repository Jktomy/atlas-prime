from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from tools.athena_routes.free_form_intake import (
    FIELDS_SCHEMA,
    RECEIPT_SCHEMA,
    FreeFormIntakeError,
    construct_free_form_intake,
)
from tools.athena_routes.hosted import expected_mission_branch, sha256_bytes, stable_json
from tools.athena_routes.schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]
MAIN = "a" * 40
WORKFLOW_BLOB = "b" * 40
MISSION = "RP-C01-M08-FREE-FORM-LIVE-R01"


class FakeRunner:
    def __init__(self, *, main: str = MAIN, main_sequence: list[str] | None = None, branch_exists: bool = False, prior_pr: bool = False) -> None:
        self.main = main
        self.main_sequence = list(main_sequence or [])
        self.branch_exists = branch_exists
        self.prior_pr = prior_pr
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(list(args))
        joined = " ".join(args)
        if "repos/Jktomy/atlas-prime/commits/main" in joined:
            output = self.main_sequence.pop(0) if self.main_sequence else self.main
        elif "repos/Jktomy/atlas-prime/contents/.github/workflows/athena-bow-hosted.yml" in joined:
            output = WORKFLOW_BLOB
        elif "repos/Jktomy/atlas-prime/git/ref/heads/" in joined:
            if self.branch_exists:
                return subprocess.CompletedProcess(args, 0, stdout="{}", stderr="")
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="HTTP 404: Not Found")
        elif args[:3] == ["gh", "pr", "list"]:
            output = '[{"number":99,"state":"CLOSED"}]' if self.prior_pr else "[]"
        else:
            raise AssertionError(f"unexpected command: {args}")
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")


def read_package(path: Path, expected_sha: str) -> SimpleNamespace:
    raw = path.read_bytes()
    if sha256_bytes(raw) != expected_sha:
        raise AssertionError("carrier hash mismatch")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        weave_bytes = archive.read("SPEAR-WEAVE.json")
        manifest_bytes = archive.read("PACKAGE-MANIFEST.json")
        weave = json.loads(weave_bytes)
        payloads = {name: archive.read(name) for name in names if name.startswith("PAYLOADS/")}
    return SimpleNamespace(
        weave=weave,
        payloads=payloads,
        manifest_sha256=sha256_bytes(manifest_bytes),
        weave_sha256=sha256_bytes(weave_bytes),
    )


class CompilerFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class FakeCompiler:
    def __init__(self, *, drift_second: bool = False, fail_code: str | None = None) -> None:
        self.calls = 0
        self.drift_second = drift_second
        self.fail_code = fail_code

    def __call__(self, package_path: Path, **kwargs: object) -> dict[str, object]:
        from pathlib import PurePosixPath

        from production_adapter.protected_paths import is_protected_path

        if is_protected_path(PurePosixPath("lifecycle/feathers/example.json")):
            raise AssertionError("free-form compiler call lacks safe-declared scope")
        self.calls += 1
        if self.fail_code is not None:
            raise CompilerFailure(self.fail_code)
        output_dir = kwargs["output_dir"]
        assert isinstance(output_dir, Path)
        package = read_package(package_path, sha256_bytes(package_path.read_bytes()))
        output_dir.mkdir(parents=True, exist_ok=True)
        mission_name = package.weave["output_mission_filename"]
        receipt_name = package.weave["compile_receipt_filename"]
        path_identity = [
            {
                "operation": thread["operation"],
                "path": thread["path"],
                "payload_sha256": sha256_bytes(package.payloads[f"PAYLOADS/{thread['payload']}"]),
            }
            for thread in package.weave["threads"]
        ]
        candidate = sha256_bytes(stable_json(path_identity).encode("utf-8"))
        if self.drift_second and self.calls == 2:
            candidate = "d" * 64
        mission: dict[str, object] = {
            "mission_sha256": "0" * 64,
            "candidate_tree_sha256": candidate,
            "final_pathset_sha256": sha256_bytes(stable_json([item["path"] for item in path_identity]).encode("utf-8")),
        }
        mission["mission_sha256"] = sha256_bytes(stable_json(mission).encode("utf-8"))
        mission_bytes = stable_json(mission).encode("utf-8")
        (output_dir / mission_name).write_bytes(mission_bytes)
        (output_dir / "PAYLOADS").mkdir()
        output_inventory = [mission_name, receipt_name]
        for name, payload in sorted(package.payloads.items()):
            target = output_dir / name
            target.write_bytes(payload)
            output_inventory.append(name)
        receipt: dict[str, object] = {
            "schema_version": "atlas-thread-engine-spear-compile-receipt-v1",
            "mission_sha256": mission["mission_sha256"],
            "compile_receipt_filename": receipt_name,
            "output_mission_filename": mission_name,
            "output_mission_sha256": sha256_bytes(mission_bytes),
            "output_inventory": sorted(output_inventory),
        }
        (output_dir / receipt_name).write_bytes(stable_json(receipt).encode("utf-8"))
        return receipt


def fields(*, changes: list[dict[str, str]] | None = None, main: str = MAIN) -> dict[str, object]:
    return {
        "schema_version": "atlas.athena.free-form-mission-fields.v1",
        "repository": "Jktomy/atlas-prime",
        "expected_main_sha": main,
        "mission_id": MISSION,
        "carrier_nonce": "rp-c01-m08-free-form-carrier-nonce-0001",
        "objective": "Construct one ordinary public-clean proof payload.",
        "commit_message": "proof: add free-form intake evidence",
        "pr_title": "RP-C01: M08 free-form intake live R01",
        "pr_body": "Fresh owner-guided M08 free-form intake proof.",
        "changes": changes if changes is not None else [{"operation": "ADD", "path": "proof/repairing-prime/rp-c01-m08-free-form-live-r01.md", "content": "# public clean proof\n"}],
        "authorizer": "Jayson",
        "semantic_operator": "Codex SOL Goal",
        "requesting_surface": "Codex",
        "origin_classification": "OWNER_GUIDED_LOCAL_NOT_FRESH_WORK_ORIGIN",
        "requested_route": "GUIDED_HOSTED_BOW",
        "stop_boundary": "DRAFT_PR_READBACK",
        "public_clean_confirmation": "PUBLIC_CLEAN_CONFIRMED",
    }


class FreeFormIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_fields(self, value: dict[str, object], name: str = "fields.json", *, indent: int | None = 2) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, indent=indent), encoding="utf-8", newline="")
        return path

    def construct(self, value: dict[str, object] | None = None, *, name: str = "artifact", runner: FakeRunner | None = None, compiler: FakeCompiler | None = None) -> tuple[dict[str, object], FakeRunner]:
        selected_runner = runner or FakeRunner()
        receipt = construct_free_form_intake(
            self.write_fields(value or fields(), f"{name}-fields.json"),
            self.root / name,
            runner=selected_runner,
            package_reader=read_package,
            compiler=compiler or FakeCompiler(),
        )
        return receipt, selected_runner

    def test_constructs_closed_atomic_preview_and_retained_canonical_outputs_without_mutation(self) -> None:
        receipt, runner = self.construct()
        artifact = self.root / "artifact"
        self.assertEqual({item.name for item in artifact.iterdir()}, {"carrier.zip", "compiled", "preview.json", "intake-receipt.json"})
        validate_schema(json.loads(FIELDS_SCHEMA.read_text(encoding="utf-8")), fields())
        validate_schema(json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8")), receipt)
        self.assertEqual((artifact / "intake-receipt.json").read_bytes(), stable_json(receipt).encode("utf-8"))
        self.assertEqual(receipt["carrier_sha256"], sha256_bytes((artifact / "carrier.zip").read_bytes()))
        self.assertEqual(receipt["preview_sha256"], sha256_bytes((artifact / "preview.json").read_bytes()))
        self.assertEqual(receipt["deterministic_branch"], expected_mission_branch(MISSION, MAIN))
        self.assertEqual(receipt["origin_classification"], "OWNER_GUIDED_LOCAL_NOT_FRESH_WORK_ORIGIN")
        self.assertEqual(receipt["promotion_boundary"], "LIVE_HOSTED_ACCEPTANCE_AND_SEPARATE_AUTHORED_RECONCILIATION_REQUIRED")
        self.assertTrue(all(value is False for value in receipt["forbidden_actions"].values()))
        self.assertTrue(all(call[:2] == ["gh", "api"] or call[:3] == ["gh", "pr", "list"] for call in runner.calls))

    def test_carrier_preview_receipt_and_compiled_bytes_are_deterministic_after_normalization(self) -> None:
        changes = [
            {"operation": "ADD", "path": "proof/zeta.md", "content": "zeta\r\nline\r\n"},
            {"operation": "ADD", "path": "proof/alpha.md", "content": "alpha\rline\n"},
        ]
        first = fields(changes=changes)
        first["objective"] = "One\r\nobjective"
        second = fields(changes=list(reversed(changes)))
        second["objective"] = "One\nobjective"
        first_receipt, _ = self.construct(first, name="first")
        second_receipt, _ = self.construct(second, name="second")
        for relative in ("carrier.zip", "preview.json", "intake-receipt.json"):
            self.assertEqual((self.root / "first" / relative).read_bytes(), (self.root / "second" / relative).read_bytes())
        first_compiled = {path.relative_to(self.root / "first" / "compiled").as_posix(): path.read_bytes() for path in (self.root / "first" / "compiled").rglob("*") if path.is_file()}
        second_compiled = {path.relative_to(self.root / "second" / "compiled").as_posix(): path.read_bytes() for path in (self.root / "second" / "compiled").rglob("*") if path.is_file()}
        self.assertEqual(first_compiled, second_compiled)
        self.assertEqual(first_receipt, second_receipt)

    def test_rejects_stale_generated_and_replay_without_output(self) -> None:
        cases = [
            (fields(main="c" * 40), FakeRunner(), "STALE_BASE"),
            (fields(changes=[{"operation": "ADD", "path": "generated/x.md", "content": "x"}]), FakeRunner(), "GENERATED_SOURCE_MIXING"),
            (fields(), FakeRunner(branch_exists=True), "REPLAY_BRANCH_EXISTS"),
            (fields(), FakeRunner(prior_pr=True), "REPLAY_PR_EXISTS"),
        ]
        for index, (value, runner, code) in enumerate(cases):
            with self.subTest(code=code):
                output = self.root / f"rejected-{index}"
                with self.assertRaises(FreeFormIntakeError) as caught:
                    construct_free_form_intake(self.write_fields(value, f"rejected-{index}.json"), output, runner=runner, package_reader=read_package, compiler=FakeCompiler())
                self.assertEqual(caught.exception.code, code)
                self.assertFalse(output.exists())

    def test_accepts_thread_engine_self_change(self) -> None:
        receipt, _ = self.construct(fields(changes=[{"operation": "ADD", "path": "tools/thread-engine/x.py", "content": "x"}]), name="self-change")
        self.assertEqual(receipt["path_classification"], "SAFE_DECLARED")

    def test_rejects_main_drift_between_construction_and_preview(self) -> None:
        output = self.root / "drifted-main"
        runner = FakeRunner(main_sequence=[MAIN, "c" * 40])
        with self.assertRaises(FreeFormIntakeError) as caught:
            construct_free_form_intake(self.write_fields(fields(), "drifted-main.json"), output, runner=runner, package_reader=read_package, compiler=FakeCompiler())
        self.assertEqual(caught.exception.code, "STALE_BASE")
        self.assertFalse(output.exists())

    def test_rejects_unknown_duplicate_private_and_unsafe_fields_before_publication(self) -> None:
        unknown = fields()
        unknown["unexpected"] = True
        missing = fields()
        del missing["mission_id"]
        invalid_mission = fields()
        invalid_mission["mission_id"] = "not lowercase"
        duplicate = self.root / "duplicate.json"
        duplicate.write_text('{"schema_version":"atlas.athena.free-form-mission-fields.v1","schema_version":"duplicate"}', encoding="utf-8")
        cases: list[tuple[Path, str]] = [
            (self.write_fields(unknown, "unknown.json"), "MISSION_FIELDS_SCHEMA_REJECTED"),
            (self.write_fields(missing, "missing.json"), "MISSION_FIELDS_SCHEMA_REJECTED"),
            (self.write_fields(invalid_mission, "invalid-mission.json"), "MISSION_FIELDS_SCHEMA_REJECTED"),
            (duplicate, "DUPLICATE_JSON_KEY"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "proof/private.md", "content": "secret=do-not-publish"}]), "private.json"), "MISSION_PRIVACY_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "../escape.md", "content": "x"}]), "traversal.json"), "MISSION_PATH_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "/absolute.md", "content": "x"}]), "absolute.json"), "MISSION_PATH_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "proof\\bad.md", "content": "x"}]), "backslash.json"), "MISSION_PATH_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "Proof/X.md", "content": "x"}, {"operation": "ADD", "path": "proof/x.md", "content": "y"}]), "collision.json"), "MISSION_PATH_COLLISION"),
            (self.write_fields(fields(changes=[]), "empty.json"), "MISSION_CHANGE_COUNT_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "DELETE", "path": "proof/x.md", "content": "x"}]), "delete.json"), "MISSION_FIELDS_SCHEMA_REJECTED"),
            (self.write_fields(fields(changes=[{"operation": "ADD", "path": "proof/x.md", "content": "bad\u0000text"}]), "nul.json"), "MISSION_TEXT_REJECTED"),
        ]
        for index, (path, code) in enumerate(cases):
            with self.subTest(code=code):
                output = self.root / f"invalid-{index}"
                with self.assertRaises(FreeFormIntakeError) as caught:
                    construct_free_form_intake(path, output, runner=FakeRunner(), package_reader=read_package, compiler=FakeCompiler())
                self.assertEqual(caught.exception.code, code)
                self.assertFalse(output.exists())

    def test_rejects_output_collision_oversize_compile_failure_and_retained_drift_atomically(self) -> None:
        existing = self.root / "existing"
        existing.mkdir()
        with self.assertRaises(FreeFormIntakeError) as collision:
            construct_free_form_intake(self.write_fields(fields(), "existing-fields.json"), existing, runner=FakeRunner(), package_reader=read_package, compiler=FakeCompiler())
        self.assertEqual(collision.exception.code, "OUTPUT_DIRECTORY_EXISTS")
        oversized = fields(changes=[{"operation": "ADD", "path": f"proof/{index}.md", "content": "x" * 200000} for index in range(4)])
        for name, value, compiler, code in (
            ("oversized", oversized, FakeCompiler(), "MISSION_CONTENT_SIZE_REJECTED"),
            ("add-existing", fields(), FakeCompiler(fail_code="THREAD_REJECTED"), "THREAD_REJECTED"),
            ("replace-missing", fields(changes=[{"operation": "REPLACE", "path": "proof/missing.md", "content": "x"}]), FakeCompiler(fail_code="SOURCE_REJECTED"), "SOURCE_REJECTED"),
            ("drift", fields(), FakeCompiler(drift_second=True), "RETAINED_COMPILE_DRIFT"),
        ):
            with self.subTest(code=code):
                output = self.root / name
                with self.assertRaises(FreeFormIntakeError) as caught:
                    construct_free_form_intake(self.write_fields(value, f"{name}.json"), output, runner=FakeRunner(), package_reader=read_package, compiler=compiler)
                self.assertEqual(caught.exception.code, code)
                self.assertFalse(output.exists())

    def test_rejects_canonical_repository_output(self) -> None:
        with self.assertRaises(FreeFormIntakeError) as caught:
            construct_free_form_intake(self.write_fields(fields(), "inside.json"), ROOT / ".free-form-intake-test-output", runner=FakeRunner(), package_reader=read_package, compiler=FakeCompiler())
        self.assertEqual(caught.exception.code, "OUTPUT_INSIDE_CANONICAL_REPOSITORY")


if __name__ == "__main__":
    unittest.main()
