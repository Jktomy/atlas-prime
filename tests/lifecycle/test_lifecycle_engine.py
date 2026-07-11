from __future__ import annotations

import hashlib
import ast
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.errors import LifecycleError
from tools.atlas_lifecycle.evidence import verify_archive, verify_bound_evidence
from tools.atlas_lifecycle.jsonio import canonical_bytes, loads_bounded, stable_record_id
from tools.atlas_lifecycle.protection import enforce_clean_values
from tools.atlas_lifecycle.repository import validate_repository
from tools.atlas_lifecycle.schema import SchemaValidator


def digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def write_json(path: Path, value: dict, *, canonical: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_bytes(value) if canonical else json.dumps(value, indent=2).encode("utf-8") + b"\n"
    path.write_bytes(data)


class LifecycleEngineTests(unittest.TestCase):
    def test_engine_sources_parse_and_have_no_network_dynamic_import_or_write_surface(self) -> None:
        source_dir = ROOT / "tools/atlas_lifecycle"
        forbidden_imports = {"http", "importlib", "requests", "socket", "urllib"}
        forbidden_calls = ("eval(", "exec(", "__import__(", ".write_", ".write(", ".unlink(", ".mkdir(")
        for path in sorted(source_dir.glob("*.py")):
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))
            with self.subTest(source=path.name):
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        names = {alias.name.split(".", 1)[0] for alias in node.names}
                        self.assertTrue(names.isdisjoint(forbidden_imports))
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        self.assertNotIn(node.module.split(".", 1)[0], forbidden_imports)
                for call in forbidden_calls:
                    self.assertNotIn(call, text)
                self.assertNotIn("gh ", text)
                self.assertNotIn("api.github", text.casefold())

    def test_cli_validate_and_verify_are_read_only_and_deterministic(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        outputs = []
        for command in ("validate", "verify"):
            result = subprocess.run(
                [sys.executable, "-B", "-m", "tools.atlas_lifecycle", command],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "PASS")
            self.assertEqual(value["authority"], "READ_ONLY")
            self.assertEqual(value["engine_class"], "SCRIPT_ASSIST_LEVEL_1A")
            outputs.append(value["source_fingerprint"])
        self.assertEqual(outputs[0], outputs[1])
        after = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(after, before)

    def test_bounded_json_rejects_duplicates_floats_depth_and_nonfinite(self) -> None:
        cases = (
            (b'{"a":1,"a":2}', "DUPLICATE_JSON_KEY"),
            (b'{"a":1.5}', "FLOAT_FORBIDDEN"),
            (b'{"a":NaN}', "NONFINITE_FORBIDDEN"),
        )
        for data, code in cases:
            with self.subTest(code=code), self.assertRaises(LifecycleError) as raised:
                loads_bounded(data)
            self.assertEqual(raised.exception.code, code)
        nested: dict = {}
        cursor = nested
        for _ in range(70):
            cursor["a"] = {}
            cursor = cursor["a"]
        with self.assertRaises(LifecycleError) as raised:
            loads_bounded(json.dumps(nested).encode())
        self.assertEqual(raised.exception.code, "JSON_DEPTH_LIMIT")

    def test_schema_unknown_field_tamper_and_protected_value_reject(self) -> None:
        record = json.loads((ROOT / "lifecycle/fixtures/feather-quest-bound.json").read_text())
        record["unexpected"] = True
        with self.assertRaises(LifecycleError) as raised:
            SchemaValidator(ROOT / "lifecycle/schemas").validate_record(record)
        self.assertEqual(raised.exception.code, "SCHEMA_EXTRA_FIELD")

        forbidden_values = (
            "password=not-safe",
            "Bearer abcdefghijklmnopqrstuvwxyz",
            "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz1234",
            "AK" + "IA" + "ABCDEFGHIJKLMNOP",
            "C:\\private\\record.json",
            "/private/record.json",
        )
        for forbidden in forbidden_values:
            clean = json.loads((ROOT / "lifecycle/fixtures/sunset-non-quest.json").read_text())
            clean["completion_assessment"] = forbidden
            with self.subTest(forbidden=forbidden), self.assertRaises(LifecycleError) as raised:
                enforce_clean_values(clean)
            self.assertEqual(raised.exception.code, "PROTECTED_VALUE_REJECTED")

        original = json.loads((ROOT / "lifecycle/fixtures/feather-quest-bound.json").read_text())
        original["next_safe_action"] = "tampered"
        self.assertNotEqual(stable_record_id(original), original["record_id"])

    def test_repository_rejects_stale_main_parent_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            record = json.loads((repo / "lifecycle/fixtures/sunset-non-quest.json").read_text())
            record["authority"] = "CANONICAL_RECORD"
            record["record_id"] = stable_record_id(record)
            path = repo / "lifecycle/sunsets" / f'{record["record_id"]}.json'
            write_json(path, record, canonical=True)
            with self.assertRaises(LifecycleError) as raised:
                validate_repository(repo, check_stale=True, expected_head="f" * 40)
            self.assertEqual(raised.exception.code, "STALE_STATE")

            shutil.rmtree(repo / "lifecycle/sunsets")
            feather = json.loads((repo / "lifecycle/fixtures/feather-quest-bound.json").read_text())
            feather["authority"] = "CANONICAL_RECORD"
            feather["concurrency"]["expected_main_sha"] = "f" * 40
            feather["concurrency"]["expected_parent_feather"] = "FTR-AAAAAAAAAAAAAAAAAAAAAAAAAA"
            feather["record_id"] = stable_record_id(feather)
            write_json(repo / "lifecycle/feathers" / f'{feather["record_id"]}.json', feather, canonical=True)
            with self.assertRaises(LifecycleError) as raised:
                validate_repository(repo, check_stale=True, expected_head="f" * 40)
            self.assertEqual(raised.exception.code, "STALE_PARENT")

            shutil.rmtree(repo / "lifecycle/feathers")
            for index, summary in enumerate(("First receipt.", "Replayed receipt."), start=1):
                receipt = {
                    "schema_id": "atlas.lifecycle.receipt",
                    "schema_version": "1.0.0",
                    "record_id": "LCR-AAAAAAAAAAAAAAAAAAAAAAAAAA",
                    "authority": "CANONICAL_RECORD",
                    "operation_id": f"replay-fixture-{index}",
                    "trusted_contract": {
                        "schema_id": "atlas.lifecycle.receipt",
                        "schema_digest": "sha256:" + "1" * 64,
                        "contract_digest": "sha256:" + "2" * 64,
                    },
                    "subject": {
                        "record_id": "FTR-KC44ORGJ3XNOVTQJUEICBUEVMS",
                        "payload_digest": "sha256:" + "3" * 64,
                        "source_fingerprint": "sha256:" + "4" * 64,
                    },
                    "independent_sidecar": {
                        "sidecar_uri": f"evidence/sidecar-{index}.json",
                        "sidecar_digest": "sha256:" + "5" * 64,
                        "subject_digest_binding": "sha256:" + "3" * 64,
                    },
                    "verification_limits": {
                        "max_input_bytes": 100,
                        "max_archive_members": 10,
                        "max_member_bytes": 100,
                        "max_parse_depth": 10,
                    },
                    "verification_result": "PASS",
                    "diagnostic_summary": summary,
                    "replay_key": "sha256:" + "6" * 64,
                }
                receipt["record_id"] = stable_record_id(receipt)
                write_json(
                    repo / "lifecycle/receipts" / f'{receipt["record_id"]}.json',
                    receipt,
                    canonical=True,
                )
            with self.assertRaises(LifecycleError) as raised:
                validate_repository(repo)
            self.assertEqual(raised.exception.code, "REPLAY_IDENTIFIER")

    def test_archive_bounds_paths_collisions_special_files_and_ratio(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            safe = root / "safe.zip"
            with zipfile.ZipFile(safe, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("evidence/result.json", "{}")
            self.assertTrue(verify_archive(safe).startswith("sha256:"))

            attacks = []
            traversal = root / "traversal.zip"
            with zipfile.ZipFile(traversal, "w") as archive:
                archive.writestr("../escape", "x")
            attacks.append((traversal, "ARCHIVE_PATH"))

            long_path = root / "long-path.zip"
            with zipfile.ZipFile(long_path, "w") as archive:
                archive.writestr("a" * 1025, "x")
            attacks.append((long_path, "ARCHIVE_PATH"))

            deep_path = root / "deep-path.zip"
            with zipfile.ZipFile(deep_path, "w") as archive:
                archive.writestr("/".join(["a"] * 33), "x")
            attacks.append((deep_path, "ARCHIVE_PATH"))

            collision = root / "collision.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with zipfile.ZipFile(collision, "w") as archive:
                    archive.writestr("A.txt", "one")
                    archive.writestr("a.txt", "two")
            attacks.append((collision, "ARCHIVE_COLLISION"))

            link = root / "link.zip"
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(link, "w") as archive:
                archive.writestr(info, "target")
            attacks.append((link, "ARCHIVE_SPECIAL_FILE"))

            ratio = root / "ratio.zip"
            with zipfile.ZipFile(ratio, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("zeros.bin", b"0" * 100_000)
            attacks.append((ratio, "ARCHIVE_RATIO"))

            corrupt = root / "corrupt.zip"
            with zipfile.ZipFile(corrupt, "w", zipfile.ZIP_STORED) as archive:
                archive.writestr("result.txt", b"integrity")
            with zipfile.ZipFile(corrupt) as archive:
                member = archive.infolist()[0]
                offset = member.header_offset + 30 + len(member.filename.encode()) + len(member.extra)
            data = bytearray(corrupt.read_bytes())
            data[offset] ^= 0x01
            corrupt.write_bytes(data)
            attacks.append((corrupt, "ARCHIVE_MEMBER_INVALID"))

            for path, code in attacks:
                with self.subTest(code=code), self.assertRaises(LifecycleError) as raised:
                    verify_archive(path)
                self.assertEqual(raised.exception.code, code)

            with mock.patch("tools.atlas_lifecycle.evidence.MAX_ARCHIVE_MEMBERS", 0):
                with self.assertRaises(LifecycleError) as raised:
                    verify_archive(safe)
                self.assertEqual(raised.exception.code, "ARCHIVE_MEMBER_LIMIT")

    def _write_bundle(self, repo: Path, archive: Path, sidecar: Path, receipt: Path) -> str:
        subject_digest = verify_archive(archive)
        write_json(sidecar, {"schema_id": "atlas.lifecycle.sidecar.v1", "subject_digest": subject_digest})
        schema_digest = digest(repo / "lifecycle/schemas/lifecycle-receipt-v1.schema.json")
        contract_digest = digest(repo / "lifecycle/lifecycle-contract.md")
        value = {
            "schema_id": "atlas.lifecycle.receipt",
            "schema_version": "1.0.0",
            "record_id": "LCR-AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "authority": "NONCANONICAL_FIXTURE",
            "operation_id": "lifecycle-evidence-verification",
            "trusted_contract": {
                "schema_id": "atlas.lifecycle.receipt",
                "schema_digest": schema_digest,
                "contract_digest": contract_digest,
            },
            "subject": {
                "record_id": "FTR-KC44ORGJ3XNOVTQJUEICBUEVMS",
                "payload_digest": subject_digest,
                "source_fingerprint": "sha256:" + "1" * 64,
            },
            "independent_sidecar": {
                "sidecar_uri": "evidence/sidecar.json",
                "sidecar_digest": digest(sidecar),
                "subject_digest_binding": subject_digest,
            },
            "verification_limits": {
                "max_input_bytes": 1048576,
                "max_archive_members": 100,
                "max_member_bytes": 1048576,
                "max_parse_depth": 32,
            },
            "verification_result": "PASS",
            "diagnostic_summary": "Harmless evidence fixture verified.",
            "replay_key": "sha256:" + "2" * 64,
        }
        value["record_id"] = stable_record_id(value)
        write_json(receipt, value)
        return subject_digest

    def test_external_trust_root_accepts_exact_bundle_and_rejects_resigned_forgery(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
            bundle = Path(raw) / "bundle"
            bundle.mkdir()
            archive = bundle / "evidence.zip"
            sidecar = bundle / "sidecar.json"
            receipt = bundle / "receipt.json"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
                output.writestr("result.json", "{}")
            expected = self._write_bundle(repo, archive, sidecar, receipt)
            trust_root = repo / "lifecycle/trust-roots/fixture.json"
            write_json(
                trust_root,
                {
                    "schema_id": "atlas.lifecycle.trust-root.v1",
                    "expected_subject_digest": expected,
                    "trusted_schema_digest": digest(repo / "lifecycle/schemas/lifecycle-receipt-v1.schema.json"),
                    "trusted_contract_digest": digest(repo / "lifecycle/lifecycle-contract.md"),
                },
            )
            observed = verify_bound_evidence(
                archive,
                sidecar,
                receipt,
                repo / "lifecycle/schemas",
                repo / "lifecycle/lifecycle-contract.md",
                trust_root,
                repo / "lifecycle/trust-roots",
            )
            self.assertEqual(observed, expected)

            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
                output.writestr("result.json", '{"forged":true}')
            self._write_bundle(repo, archive, sidecar, receipt)
            with self.assertRaises(LifecycleError) as raised:
                verify_bound_evidence(
                    archive,
                    sidecar,
                    receipt,
                    repo / "lifecycle/schemas",
                    repo / "lifecycle/lifecycle-contract.md",
                    trust_root,
                    repo / "lifecycle/trust-roots",
                )
            self.assertEqual(raised.exception.code, "TRUSTED_SUBJECT_MISMATCH")


if __name__ == "__main__":
    unittest.main()
