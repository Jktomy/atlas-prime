from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FOUNDRY_ROOT = ROOT / "tools" / "oathbringer-foundry"
sys.path.insert(0, str(FOUNDRY_ROOT))

from delivery_standard import (
    CommandResult,
    DeliveryError,
    MAX_ARCHIVE_BYTES,
    classify_branch_response,
    compile_with_evidence,
    parse_foundry_result,
    parse_ls_tree_record,
    retain_primary_success,
    validate_exact_audit,
    validate_workflow_platforms,
    verify_evidence,
)
from foundry import FoundryError, _operation_paths


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def foundry_success(lane: str) -> dict:
    return {
        "carrier_path": f"Oathbringer-{lane}.zip",
        "carrier_sha256": "a" * 64,
        "manifest_sha256": "b" * 64,
        "forge_receipt_sha256": "c" * 64,
        "member_count": 24,
        "bound_live_state_sha256": "d" * 64,
        "compiler_is_writer": False,
    }


def verify_generated(path: Path) -> dict:
    return verify_evidence(
        path,
        sidecar_path=path.with_suffix(path.suffix + ".sha256"),
        expected_sha256=file_digest(path),
    )


def write_self_consistent_archive(path: Path, receipt: dict, *, compression: int = zipfile.ZIP_STORED, extra: dict[str, bytes] | None = None) -> None:
    members = {
        "DELIVERY-RECEIPT.json": (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode(),
        "stdout.txt": b"",
        "stderr.txt": b"",
        **(extra or {}),
    }
    manifest = {
        "format_version": "1.0",
        "files": [
            {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            for name, data in sorted(members.items())
        ],
    }
    members["MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    members["SHA256SUMS.txt"] = "".join(
        f"{hashlib.sha256(members[name]).hexdigest()}  {name}\n" for name in sorted(members)
    ).encode()
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = compression
            archive.writestr(info, data)
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{file_digest(path)}  {path.name}\n", encoding="ascii", newline="\n"
    )


class ConsistentPRDeliveryStandardTests(unittest.TestCase):
    def test_git_ls_tree_sha_tab_path_parsing(self) -> None:
        parsed = parse_ls_tree_record("100644 blob " + "a" * 40 + "\tproof/path with spaces.txt\n")
        self.assertEqual(parsed["object_sha"], "a" * 40)
        self.assertEqual(parsed["path"], "proof/path with spaces.txt")
        for malformed in (
            "100644 blob " + "a" * 40 + " proof/no-tab.txt",
            "100644 blob short\tproof/x.txt",
            "100644 blob " + "a" * 40 + "\t",
        ):
            with self.subTest(malformed=malformed), self.assertRaises(DeliveryError):
                parse_ls_tree_record(malformed)

    def test_powershell_strict_mode_query_interpolation(self) -> None:
        launcher = FOUNDRY_ROOT / "Invoke-AtlasDeliveryStandard.ps1"
        source = launcher.read_text(encoding="utf-8")
        self.assertIn("Set-StrictMode -Version Latest", source)
        self.assertIn("${ProbePath}?ref=${ExactRef}", source)
        pwsh = shutil.which("pwsh")
        if pwsh is None:
            self.skipTest("pwsh is unavailable")
        result = subprocess.run([pwsh, "-NoProfile", "-File", str(launcher), "-ResolverSelfTest"], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        proof = json.loads(result.stdout)
        self.assertEqual(proof["workflow_platforms"], ["ubuntu-latest", "windows-latest"])
        self.assertTrue(proof["strict_mode_query"].endswith("?ref=" + "0" * 40))

    def test_package_only_result_blob_is_rejected_from_strict_operations(self) -> None:
        operation = {
            "path": "proof/x.txt",
            "operation": "ADD",
            "payload_path": "payload/x.txt",
            "payload_sha256": "b" * 64,
            "result_blob": "c" * 40,
        }
        with self.assertRaises(FoundryError):
            _operation_paths([operation])

    def test_real_foundry_diagnostic_is_preserved_before_json_parse(self) -> None:
        with self.assertRaisesRegex(DeliveryError, "Foundry rejected: exact base drift"):
            parse_foundry_result(CommandResult(1, "", "Foundry rejected: exact base drift\n"))
        with self.assertRaisesRegex(DeliveryError, "not-json from Foundry"):
            parse_foundry_result(CommandResult(0, "not-json from Foundry", ""))

    def test_audit_binding_accepts_exact_head_and_rejects_head_sha_alias(self) -> None:
        head = "d" * 40
        validate_exact_audit({"verdict": "GREEN", "exact_head": head}, head)
        with self.assertRaises(DeliveryError):
            validate_exact_audit({"verdict": "GREEN", "head_sha": head}, head)

    def test_missing_branch_and_404_are_explicit_states(self) -> None:
        self.assertEqual(classify_branch_response(None, "agent/x"), "MISSING")
        self.assertEqual(classify_branch_response({"ref": "refs/heads/agent/x"}, "agent/x"), "PRESENT")
        with self.assertRaises(DeliveryError):
            classify_branch_response({}, "agent/x")

    def test_nonessential_post_stop_probe_cannot_reverse_success(self) -> None:
        def broken_probe() -> None:
            raise RuntimeError("branch already removed")

        result = retain_primary_success({"result": "SUCCESS"}, broken_probe)
        self.assertEqual(result["result"], "SUCCESS")
        self.assertIn("branch already removed", result["post_stop_warning"])

    def test_outer_evidence_finishes_on_safe_failure_and_redacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-failure-") as temp_text:
            temp = Path(temp_text)

            def reject(_arguments, _cwd):
                token_shaped = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
                return CommandResult(1, "", f"authorization: {token_shaped}")

            evidence = temp / "failure.zip"
            with self.assertRaises(DeliveryError):
                compile_with_evidence(
                    input_root=temp,
                    source_root=ROOT,
                    output_dir=temp / "out",
                    evidence_zip=evidence,
                    platforms=("ubuntu-latest", "windows-latest"),
                    runner=reject,
                )
            self.assertEqual(verify_generated(evidence)["status"], "PASS")
            self.assertTrue(evidence.with_suffix(".zip.sha256").is_file())
            with zipfile.ZipFile(evidence) as archive:
                combined = archive.read("stderr.txt") + archive.read("DELIVERY-RECEIPT.json")
            self.assertNotIn(b"ghp_", combined)
            self.assertIn(b"[REDACTED]", combined)

    def test_exact_ubuntu_windows_applicability_is_truthful(self) -> None:
        self.assertEqual(
            validate_workflow_platforms(("ubuntu-latest", "windows-latest")),
            ("ubuntu-latest", "windows-latest"),
        )
        for platforms in (("ubuntu-latest",), ("windows-latest", "ubuntu-latest"), ("ubuntu", "windows")):
            with self.subTest(platforms=platforms), self.assertRaises(DeliveryError):
                validate_workflow_platforms(platforms)

    def test_harmless_build_repair_execute_operator_acceptance_and_determinism(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-lanes-") as temp_text:
            temp = Path(temp_text)
            for lane in ("BUILD", "REPAIR", "EXECUTE"):
                with self.subTest(lane=lane):
                    def accept(_arguments, _cwd, current=lane):
                        return CommandResult(0, json.dumps(foundry_success(current)), "")

                    first = temp / "one" / f"{lane.lower()}.zip"
                    second = temp / "two" / f"{lane.lower()}.zip"
                    result = compile_with_evidence(
                        input_root=temp,
                        source_root=ROOT,
                        output_dir=temp / "out",
                        evidence_zip=first,
                        platforms=("ubuntu-latest", "windows-latest"),
                        runner=accept,
                    )
                    compile_with_evidence(
                        input_root=temp,
                        source_root=ROOT,
                        output_dir=temp / "out",
                        evidence_zip=second,
                        platforms=("ubuntu-latest", "windows-latest"),
                        runner=accept,
                    )
                    self.assertEqual(result["result"], "SUCCESS")
                    self.assertEqual(result["foundry"]["carrier_name"], f"Oathbringer-{lane}.zip")
                    self.assertEqual(first.read_bytes(), second.read_bytes())
                    self.assertEqual(verify_generated(first)["status"], "PASS")

    def test_success_result_is_allowlisted_and_all_evidence_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-secret-contract-") as temp_text:
            temp = Path(temp_text)
            sample_value = "sensitive-" + "value-1234567890"

            def unexpected_success(_arguments, _cwd):
                result = foundry_success("BUILD")
                result["credential"] = sample_value
                return CommandResult(0, json.dumps(result), "")

            evidence = temp / "unknown-success.zip"
            with self.assertRaisesRegex(DeliveryError, "trusted result contract"):
                compile_with_evidence(
                    input_root=temp,
                    source_root=ROOT,
                    output_dir=temp / "out",
                    evidence_zip=evidence,
                    platforms=("ubuntu-latest", "windows-latest"),
                    runner=unexpected_success,
                )
            with zipfile.ZipFile(evidence) as archive:
                combined = b"\n".join(archive.read(name) for name in archive.namelist())
            self.assertNotIn(sample_value.encode(), combined)
            self.assertEqual(verify_generated(evidence)["status"], "PASS")

    def test_bearer_and_multivalue_credentials_are_fully_redacted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-secret-redaction-") as temp_text:
            temp = Path(temp_text)
            bearer = "bearer-" + "value-1234567890"
            multiword = "correct horse " + "battery staple"
            label = "pass" + "word"

            def reject(_arguments, _cwd):
                return CommandResult(1, "", f"Authorization: Bearer {bearer}\n{label}={multiword}\nFoundry stopped")

            evidence = temp / "failure.zip"
            with self.assertRaises(DeliveryError):
                compile_with_evidence(
                    input_root=temp,
                    source_root=ROOT,
                    output_dir=temp / "out",
                    evidence_zip=evidence,
                    platforms=("ubuntu-latest", "windows-latest"),
                    runner=reject,
                )
            with zipfile.ZipFile(evidence) as archive:
                combined = b"\n".join(archive.read(name) for name in archive.namelist())
            self.assertNotIn(bearer.encode(), combined)
            self.assertNotIn(multiword.encode(), combined)
            self.assertIn(b"Foundry stopped", combined)
            self.assertEqual(verify_generated(evidence)["status"], "PASS")

    def test_verifier_requires_independent_digest_and_sidecar_binding(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-sidecar-") as temp_text:
            temp = Path(temp_text)

            def accept(_arguments, _cwd):
                return CommandResult(0, json.dumps(foundry_success("BUILD")), "")

            evidence = temp / "success.zip"
            compile_with_evidence(
                input_root=temp,
                source_root=ROOT,
                output_dir=temp / "out",
                evidence_zip=evidence,
                platforms=("ubuntu-latest", "windows-latest"),
                runner=accept,
            )
            sidecar = evidence.with_suffix(".zip.sha256")
            expected = file_digest(evidence)
            self.assertEqual(verify_evidence(evidence, sidecar_path=sidecar, expected_sha256=expected)["status"], "PASS")
            with self.assertRaises(DeliveryError):
                verify_evidence(evidence, sidecar_path=temp / "missing.sha256", expected_sha256=expected)
            with self.assertRaises(DeliveryError):
                verify_evidence(evidence, sidecar_path=sidecar, expected_sha256="0" * 64)

    def test_self_consistent_forged_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-forged-") as temp_text:
            temp = Path(temp_text)
            evidence = temp / "forged.zip"
            write_self_consistent_archive(
                evidence,
                {"identity": "ATTACKER_FABRICATION", "result": "SUCCESS", "compiler_is_writer": True},
            )
            with self.assertRaises(DeliveryError):
                verify_generated(evidence)

    def test_archive_member_path_compression_count_and_json_depth_are_bounded(self) -> None:
        with tempfile.TemporaryDirectory(prefix="delivery-bounds-") as temp_text:
            temp = Path(temp_text)
            valid_receipt = {
                "format_version": "1.0",
                "identity": "CONSISTENT_PR_DELIVERY_STANDARD_R01",
                "result": "REJECTED",
                "workflow_platforms": ["ubuntu-latest", "windows-latest"],
                "compiler_is_writer": False,
                "direct_main_write": False,
                "credential_persistence": False,
                "evidence_contract": {
                    "archive_filename": "bounded.zip",
                    "sidecar_filename": "bounded.zip.sha256",
                    "required_members": ["DELIVERY-RECEIPT.json", "MANIFEST.json", "SHA256SUMS.txt", "stderr.txt", "stdout.txt"],
                    "verification": "SIDECAR_PLUS_INDEPENDENT_SHA256",
                },
                "diagnostic": "bounded rejection",
            }
            compressed = temp / "bounded.zip"
            write_self_consistent_archive(compressed, valid_receipt, compression=zipfile.ZIP_DEFLATED)
            with self.assertRaisesRegex(DeliveryError, "member is unsafe"):
                verify_generated(compressed)

            extra = temp / "extra.zip"
            extra_receipt = dict(valid_receipt)
            extra_receipt["evidence_contract"] = {**valid_receipt["evidence_contract"], "archive_filename": extra.name, "sidecar_filename": extra.name + ".sha256"}
            write_self_consistent_archive(extra, extra_receipt, extra={"../escape.txt": b"x"})
            with self.assertRaisesRegex(DeliveryError, "exact member contract"):
                verify_generated(extra)

            deep = temp / "deep.zip"
            nested: object = "leaf"
            for _ in range(20):
                nested = [nested]
            deep_receipt = dict(valid_receipt)
            deep_receipt["evidence_contract"] = {**valid_receipt["evidence_contract"], "archive_filename": deep.name, "sidecar_filename": deep.name + ".sha256"}
            deep_receipt["unexpected"] = nested
            write_self_consistent_archive(deep, deep_receipt)
            with self.assertRaisesRegex(DeliveryError, "depth limit"):
                verify_generated(deep)

            oversized = temp / "oversized.zip"
            oversized.write_bytes(b"0" * (MAX_ARCHIVE_BYTES + 1))
            oversized.with_suffix(".zip.sha256").write_text(
                f"{file_digest(oversized)}  {oversized.name}\n", encoding="ascii", newline="\n"
            )
            with self.assertRaisesRegex(DeliveryError, "oversized"):
                verify_generated(oversized)

            malformed = temp / "malformed.zip"
            malformed.write_bytes(b"not a zip")
            malformed.with_suffix(".zip.sha256").write_text(
                f"{file_digest(malformed)}  {malformed.name}\n", encoding="ascii", newline="\n"
            )
            with self.assertRaisesRegex(DeliveryError, "verification failed"):
                verify_generated(malformed)


if __name__ == "__main__":
    unittest.main()
