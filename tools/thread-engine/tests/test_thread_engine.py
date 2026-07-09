from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.thread_engine import ThreadEngineError, execute_weave, sha256_bytes, sha256_file, tree_hash, validate_no_symlinks
from tools.build_package import build_package


def load_example(name: str) -> dict:
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def write_weave(directory: Path, data: dict) -> Path:
    path = directory / "weave.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def stable_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def snapshot_source() -> str:
    digest = hashlib.sha256()
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if path.name == "__pycache__" or path.name == ".pytest_cache" or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_file() and not path.is_symlink():
            digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\n")
    return digest.hexdigest()


class ThreadEngineTests(unittest.TestCase):
    def run_weave(self, data: dict, **kwargs) -> dict:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-test-") as tmp_text:
            tmp = Path(tmp_text)
            weave_path = write_weave(tmp, data)
            sandbox_root = tmp / "sandboxes"
            sandbox_root.mkdir()
            return execute_weave(
                weave_path,
                fixture_only=True,
                audit_only=True,
                sandbox_root=sandbox_root,
                package_root=ROOT,
                **kwargs,
            )

    def expect_rejection(self, data: dict, expected_text: str, error_code: str, error_stage: str, **kwargs) -> dict:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-test-") as tmp_text:
            tmp = Path(tmp_text)
            weave_path = write_weave(tmp, data)
            sandbox_root = tmp / "sandboxes"
            sandbox_root.mkdir()
            with self.assertRaises(ThreadEngineError) as raised:
                execute_weave(
                    weave_path,
                    fixture_only=True,
                    audit_only=True,
                    sandbox_root=sandbox_root,
                    package_root=ROOT,
                    **kwargs,
                )
            self.assertIn(expected_text, str(raised.exception))
            receipt = raised.exception.receipt
            self.assertEqual(receipt["schema_version"], "atlas-thread-engine-receipt-v1")
            self.assertEqual(receipt["result"], "REJECTED")
            self.assertEqual(receipt["error_code"], error_code)
            self.assertEqual(receipt["error_stage"], error_stage)
            self.assertEqual(receipt["stop_point"], error_stage)
            self.assertIn("last_completed_checkpoint", receipt)
            self.assertTrue(receipt["checkpoint_results"])
            self.assertFalse(receipt["github_called"])
            self.assertFalse(receipt["network_called"])
            self.assertFalse(receipt["repository_checkout_mutated"])
            self.assertFalse(receipt["production_adapter_present"])
            self.assertFalse(receipt["forbidden_action_confirmation"]["github_called"])
            return receipt

    def test_valid_add_replace_and_receipt(self) -> None:
        before = snapshot_source()
        receipt = self.run_weave(load_example("add-replace.example.json"))
        after = snapshot_source()
        self.assertEqual(before, after)
        self.assertEqual(receipt["result"], "SUCCESS")
        self.assertEqual(receipt["engine_state"], "PILOT_DISABLED")
        self.assertEqual(receipt["runtime_mode"], "FIXTURE_ONLY")
        self.assertFalse(receipt["forbidden_action_confirmation"]["github_called"])
        self.assertFalse(receipt["forbidden_action_confirmation"]["network_called"])
        self.assertFalse(receipt["forbidden_action_confirmation"]["repository_checkout_mutated"])
        self.assertFalse(receipt["forbidden_action_confirmation"]["production_adapter_present"])
        self.assertEqual([item["operation"] for item in receipt["thread_results"]], ["ADD", "REPLACE"])

    def test_explicit_fixture_and_audit_intent_required(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-test-") as tmp_text:
            weave_path = write_weave(Path(tmp_text), load_example("add-replace.example.json"))
            with self.assertRaises(ThreadEngineError) as raised:
                execute_weave(weave_path, fixture_only=False, audit_only=True, package_root=ROOT)
            self.assertEqual(raised.exception.error_code, "INTENT_REQUIRED")

    def test_module_cli_streams_are_json_clean(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-cli-") as tmp_text:
            tmp = Path(tmp_text)
            sandbox_root = tmp / "sandboxes"
            sandbox_root.mkdir()

            success = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "engine.thread_engine",
                    "--weave",
                    str(ROOT / "examples" / "add-replace.example.json"),
                    "--fixture-only",
                    "--audit-only",
                    "--sandbox-root",
                    str(sandbox_root),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(success.returncode, 0)
            self.assertEqual(success.stderr, "")
            success_receipt = json.loads(success.stdout)
            self.assertEqual(success_receipt["result"], "SUCCESS")

            rejected = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "engine.thread_engine",
                    "--weave",
                    str(ROOT / "examples" / "delete-authorized.example.json"),
                    "--fixture-only",
                    "--audit-only",
                    "--sandbox-root",
                    str(sandbox_root),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(rejected.stdout, "")
            rejected_receipt = json.loads(rejected.stderr)
            self.assertEqual(rejected_receipt["result"], "REJECTED")
            self.assertEqual(
                rejected_receipt["error_code"],
                "DELETE_AUTHORITY_REQUIRED",
            )
            self.assertNotIn("RuntimeWarning", rejected.stderr)

    def test_path_rejections(self) -> None:
        cases = [
            ({"threads": [{"thread_id": "x", "operation": "ADD", "path": "new.txt", "payload": "missing.txt", "payload_sha256": "0" * 64, "expected_output_sha256": "0" * 64}]}, "required regular file is absent", "REGULAR_FILE_REQUIRED", "CANDIDATE_STAGE"),
            ({"threads": [{"thread_id": "x", "operation": "ADD", "path": "/tmp/x"}]}, "absolute path", "PATH_REJECTED", "THREAD_SET_VERIFY"),
            ({"threads": [{"thread_id": "x", "operation": "ADD", "path": "../x"}]}, "traversal", "PATH_REJECTED", "THREAD_SET_VERIFY"),
            ({"threads": [{"thread_id": "x", "operation": "ADD", "path": "dir\\x"}]}, "backslash", "PATH_REJECTED", "THREAD_SET_VERIFY"),
            ({"threads": [{"thread_id": "x1", "operation": "ADD", "path": "A.txt"}, {"thread_id": "x2", "operation": "ADD", "path": "a.txt"}]}, "case-fold collision", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY"),
            ({"threads": [{"thread_id": "x", "operation": "ADD", "path": "one.txt"}, {"thread_id": "x", "operation": "ADD", "path": "two.txt"}]}, "duplicate thread_id", "THREAD_SET_REJECTED", "THREAD_SET_VERIFY"),
        ]
        for patch, expected, code, stage in cases:
            data = load_example("add-replace.example.json")
            data.update(patch)
            self.expect_rejection(data, expected, code, stage)

    def test_ordinary_bow_arrow_weave_rejects_prime_critical_path(self) -> None:
        data = load_example("add-replace.example.json")
        data["threads"][0]["path"] = "migration/codex-inheritance-manifest.md"
        self.expect_rejection(data, "protected path requires a separate route", "PROTECTED_PATH", "THREAD_SET_VERIFY")

    def test_add_and_replace_contract_rejections(self) -> None:
        data = load_example("add-replace.example.json")
        data["threads"][0]["path"] = "keep.txt"
        self.expect_rejection(data, "ADD target already exists", "THREAD_SET_REJECTED", "CANDIDATE_STAGE")

        data = load_example("add-replace.example.json")
        data["threads"][1]["path"] = "absent.txt"
        self.expect_rejection(data, "required regular file is absent", "REGULAR_FILE_REQUIRED", "CANDIDATE_STAGE")

        data = load_example("add-replace.example.json")
        data["threads"][1]["source_sha256"] = "0" * 64
        self.expect_rejection(data, "source hash mismatch", "SOURCE_HASH_MISMATCH", "CANDIDATE_STAGE")

        data = load_example("add-replace.example.json")
        data["threads"][0]["payload_sha256"] = "0" * 64
        self.expect_rejection(data, "payload hash mismatch", "PAYLOAD_HASH_MISMATCH", "CANDIDATE_STAGE")

        data = load_example("add-replace.example.json")
        data["expected_candidate_tree_sha256"] = "0" * 64
        self.expect_rejection(data, "candidate tree SHA-256 mismatch", "CANDIDATE_TREE_MISMATCH", "CANDIDATE_TREE_VERIFY")

    def test_regression_receipts_for_previous_failures(self) -> None:
        data = load_example("add-replace.example.json")
        data["threads"][1]["path"] = "absent.txt"
        first = self.expect_rejection(data, "required regular file is absent", "REGULAR_FILE_REQUIRED", "CANDIDATE_STAGE")
        second = self.expect_rejection(data, "required regular file is absent", "REGULAR_FILE_REQUIRED", "CANDIDATE_STAGE")
        self.assertEqual(stable_hash(first), stable_hash(second))

        data = load_example("add-replace.example.json")
        data["threads"] = [{"thread_id": "x", "operation": "ADD", "path": "new.txt", "payload": "missing.txt", "payload_sha256": "0" * 64, "expected_output_sha256": "0" * 64}]
        receipt = self.expect_rejection(data, "required regular file is absent", "REGULAR_FILE_REQUIRED", "CANDIDATE_STAGE")
        self.assertEqual(receipt["result"], "REJECTED")

    def test_delete_requires_runtime_authority(self) -> None:
        data = load_example("delete-authorized.example.json")
        self.expect_rejection(data, "DELETE lacks matching fixture authority", "DELETE_AUTHORITY_REQUIRED", "CANDIDATE_STAGE")
        self.expect_rejection(data, "DELETE lacks matching fixture authority", "DELETE_AUTHORITY_REQUIRED", "CANDIDATE_STAGE", allow_fixture_delete=True, delete_authority_id="WRONG")

    def test_resume_mismatch_stops(self) -> None:
        data = load_example("add-replace.example.json")
        data["resume_from"] = "THREAD_SET_VERIFY"
        self.expect_rejection(data, "resume_from mismatch", "RESUME_MISMATCH", "PACKAGE_AUDIT")

    def test_utf8_round_trip(self) -> None:
        text = "Gate 7B cafe \u2603"
        self.assertEqual(sha256_bytes(text.encode("utf-8")), hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_tree_hash_is_deterministic(self) -> None:
        self.assertEqual(tree_hash(ROOT / "fixtures" / "base"), tree_hash(ROOT / "fixtures" / "base"))

    def test_injected_symlink_classification_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-symlink-mock-") as tmp_text:
            root = Path(tmp_text)
            (root / "file.txt").write_text("content\n", encoding="utf-8")
            with self.assertRaises(ThreadEngineError) as raised:
                validate_no_symlinks(root, is_symlink=lambda item: item.name == "file.txt")
            self.assertEqual(raised.exception.error_code, "SYMLINK_REJECTED")

    def test_real_filesystem_symlink_rejected_or_capability_skip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-symlink-") as tmp_text:
            tmp = Path(tmp_text)
            package = tmp / "package"
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc", "*.pyo"))
            link = package / "fixtures" / "base" / "link.txt"
            try:
                os.symlink(package / "fixtures" / "base" / "keep.txt", link)
            except OSError as exc:
                self.skipTest(f"SKIP_PLATFORM_CAPABILITY: {type(exc).__name__}: {exc}")
            (tmp / "sandboxes").mkdir()
            with self.assertRaises(ThreadEngineError) as raised:
                execute_weave(
                    package / "examples" / "add-replace.example.json",
                    fixture_only=True,
                    audit_only=True,
                    sandbox_root=tmp / "sandboxes",
                    package_root=package,
                )
            self.assertEqual(raised.exception.error_code, "SYMLINK_REJECTED")

    def test_package_is_deterministic_and_manifest_valid(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas-thread-engine-package-") as tmp_text:
            tmp = Path(tmp_text)
            first = tmp / "one.zip"
            second = tmp / "two.zip"
            first_hash = build_package(ROOT, first)
            second_hash = build_package(ROOT, second)
            self.assertEqual(first_hash, second_hash)
            self.assertEqual(sha256_file(first), sha256_file(second))
            with zipfile.ZipFile(first, "r") as package:
                for info in package.infolist():
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual(info.external_attr, 0o100644 << 16)
                manifest = json.loads(package.read("PACKAGE-MANIFEST.json").decode("utf-8"))
                self.assertEqual(manifest["implementation_state"], "PILOT_DISABLED")
                self.assertEqual(manifest["runtime_mode"], "FIXTURE_ONLY")
                self.assertTrue(manifest["files"])
                for entry in manifest["files"]:
                    self.assertEqual(
                        hashlib.sha256(package.read(entry["path"])).hexdigest(),
                        entry["sha256"],
                    )


if __name__ == "__main__":
    unittest.main()
