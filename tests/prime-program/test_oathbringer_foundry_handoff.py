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


ROOT = Path(__file__).resolve().parents[2]
FOUNDRY_ROOT = ROOT / "tools" / "oathbringer-foundry"
sys.path.insert(0, str(FOUNDRY_ROOT))

from handoff import HandoffError, build_operator_command, build_operator_handoff


class OathbringerFoundryHandoffTests(unittest.TestCase):
    def test_command_is_fixed_shape_and_only_binds_name_and_digest(self) -> None:
        first_name = "Oathbringer-Foundry-FIRST-R01.zip"
        second_name = "Oathbringer-Foundry-SECOND-R02.zip"
        first_digest = "a" * 64
        second_digest = "b" * 64
        first = build_operator_command(first_name, first_digest)
        second = build_operator_command(second_name, second_digest)
        normalized_first = first.replace(first_name, "<CARRIER>").replace(first_digest, "<SHA256>")
        normalized_second = second.replace(second_name, "<CARRIER>").replace(second_digest, "<SHA256>")
        self.assertEqual(normalized_first, normalized_second)
        self.assertEqual(first.count(first_name), 1)
        self.assertEqual(first.count(first_digest), 1)
        self.assertIn("PowerShell 7 or newer", first)
        self.assertIn("Atlas-Oathbringer-Evidence", first)
        self.assertNotIn("member_count", first)
        self.assertNotIn("foundry-mission", first)

    def test_command_verifies_complete_zip_before_extraction(self) -> None:
        command = build_operator_command("Oathbringer-Foundry-ORDER-R01.zip", "c" * 64)
        self.assertLess(command.index("Get-FileHash"), command.index("Expand-Archive"))
        self.assertLess(command.index("SHA-256 mismatch"), command.index("Expand-Archive"))
        self.assertLess(command.index("Expand-Archive"), command.index("Invoke-OathbringerCarrier.ps1"))
        self.assertIn("[Guid]::NewGuid()", command)
        self.assertIn("workspace retained for review", command)

    def test_invalid_name_and_digest_fail_closed(self) -> None:
        for name in ("../carrier.zip", "carrier.zip", "Oathbringer-Foundry-BAD-R1.zip", "Oathbringer-Foundry-BAD-R01.ps1"):
            with self.subTest(name=name):
                with self.assertRaises(HandoffError):
                    build_operator_command(name, "d" * 64)
        for digest in ("D" * 64, "d" * 63, "not-a-digest"):
            with self.subTest(digest=digest):
                with self.assertRaises(HandoffError):
                    build_operator_command("Oathbringer-Foundry-BAD-R01.zip", digest)

    def test_handoff_reports_one_download_and_actual_carrier_digest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="foundry-handoff-") as raw:
            carrier = Path(raw) / "Oathbringer-Foundry-HANDOFF-R01.zip"
            carrier.write_bytes(b"sealed-carrier-fixture")
            result = build_operator_handoff(carrier)
            self.assertEqual(result["carrier_sha256"], hashlib.sha256(carrier.read_bytes()).hexdigest())
            self.assertEqual(result["download_count"], 1)
            self.assertFalse(result["separate_script_download_required"])
            self.assertEqual(result["operator_interface"], "POWERSHELL_7_PASTE")

    def test_cli_registers_handoff_after_carrier_verification(self) -> None:
        source = (FOUNDRY_ROOT / "cli.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("handoff")', source)
        handoff_block = source[source.index('if args.command == "handoff"'):]
        self.assertLess(handoff_block.index("verify_carrier(args.carrier)"), handoff_block.index("build_operator_handoff(args.carrier)"))

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required for the operator-handoff regression")
    def test_paste_command_runs_one_zip_from_a_download_path_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas downloads with spaces ") as raw:
            download_root = Path(raw)
            carrier_name = "Oathbringer-Foundry-HANDOFF-TEST-R01.zip"
            carrier = download_root / carrier_name
            launcher = """[CmdletBinding()]\nparam([string]$ReceiptPath)\n[ordered]@{ status = 'PASS'; receipt = $ReceiptPath } | ConvertTo-Json -Compress | Set-Content -LiteralPath $ReceiptPath -Encoding utf8NoBOM\nexit 0\n"""
            with zipfile.ZipFile(carrier, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.writestr("launcher/Invoke-OathbringerCarrier.ps1", launcher)
            digest = hashlib.sha256(carrier.read_bytes()).hexdigest()
            command = build_operator_command(carrier_name, digest)
            environment = os.environ.copy()
            environment["ATLAS_OATHBRINGER_DOWNLOADS"] = str(download_root)
            completed = subprocess.run(
                [shutil.which("pwsh") or "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=environment,
            )
            self.assertEqual(completed.returncode, 0, msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
            receipt = download_root / "Atlas-Oathbringer-Evidence" / "Oathbringer-Foundry-HANDOFF-TEST-R01.receipt.json"
            self.assertTrue(receipt.is_file())
            self.assertEqual(json.loads(receipt.read_text(encoding="utf-8-sig"))["status"], "PASS")

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell 7 is required for the operator-handoff regression")
    def test_wrong_digest_rejects_before_evidence_or_extraction(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atlas wrong digest ") as raw:
            download_root = Path(raw)
            carrier_name = "Oathbringer-Foundry-WRONG-HASH-R01.zip"
            (download_root / carrier_name).write_bytes(b"not-the-authorized-carrier")
            command = build_operator_command(carrier_name, "e" * 64)
            environment = os.environ.copy()
            environment["ATLAS_OATHBRINGER_DOWNLOADS"] = str(download_root)
            completed = subprocess.run(
                [shutil.which("pwsh") or "pwsh", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=environment,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("SHA-256 mismatch", completed.stderr + completed.stdout)
            self.assertFalse((download_root / "Atlas-Oathbringer-Evidence").exists())


if __name__ == "__main__":
    unittest.main()
