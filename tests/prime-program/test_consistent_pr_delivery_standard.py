from __future__ import annotations

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
            self.assertEqual(verify_evidence(evidence)["status"], "PASS")
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
                        return CommandResult(0, json.dumps({"lane": current, "carrier_sha256": "a" * 64}), "")

                    first = temp / f"{lane.lower()}-one.zip"
                    second = temp / f"{lane.lower()}-two.zip"
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
                    self.assertEqual(result["foundry"]["lane"], lane)
                    self.assertEqual(first.read_bytes(), second.read_bytes())
                    self.assertEqual(verify_evidence(first)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
