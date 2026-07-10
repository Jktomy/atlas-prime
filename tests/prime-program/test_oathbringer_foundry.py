from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
FOUNDRY_ROOT = ROOT / "tools" / "oathbringer-foundry"
sys.path.insert(0, str(FOUNDRY_ROOT))

import foundry as foundry_module
from cli import REPLAY_LEDGER_NAME, _read_replay_ledger, _record_replay_ledger
from foundry import FoundryError, bind_live_state, compile_carrier, load_json, read_live_state, verify_carrier


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OathbringerFoundryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="oathbringer-foundry-")
        self.root = Path(self.temp.name)
        self.input_root = self.root / "input"
        (self.input_root / "payload").mkdir(parents=True)
        self.payload = self.input_root / "payload" / "harmless.txt"
        self.payload.write_text("Foundry harmless fixture.\n", encoding="utf-8", newline="\n")
        self.lessons_sha = digest(ROOT / "methods" / "sword-lessons.json")
        self.locked_source_paths = [
            {"path": "methods/sword-lessons.json", "sha256": self.lessons_sha},
            *[
                {"path": path, "sha256": digest(ROOT / path)}
                for path in foundry_module._engine_source_paths(ROOT)
            ],
        ]

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _mission(self, mode: str = "BUILD") -> dict:
        payload_sha = digest(self.payload)
        expected_head = None if mode == "BUILD" else "b" * 40
        pull_request = None if mode == "BUILD" else 91
        operations = [] if mode in {"RECOVERY", "EXECUTE"} else [
            {
                "path": "proof/foundry-harmless.txt",
                "operation": "ADD",
                "payload_path": "payload/harmless.txt",
                "payload_sha256": payload_sha,
            }
        ]
        oathbringer = None
        if mode != "RECOVERY":
            oathbringer = {
                "format_version": "2.0",
                "mission_id": "FOUNDRY-HARMLESS-TEST",
                "sword_identity": "foundry-test-r01",
                "forge_standard": "SWORD_FORGE_STANDARD_V1",
                "package_manifest_required": True,
                "lessons_register": {
                    "schema_version": "prime-sword-lessons-v1",
                    "path": "source/methods/sword-lessons.json",
                    "source_sha256": self.lessons_sha,
                },
                "lesson_applicability": [
                    {"lesson_id": f"SWORD-L{number:03d}", "status": "APPLIED"}
                    for number in range(1, 14)
                ],
                "change_method": "OATHBRINGER",
                "execution_environment": "GITHUB",
                "operator_interface": "POWERSHELL",
                "framework_state": "PILOT_READY_PROOF_PENDING",
                "runtime_mode": "PRODUCTION_GITHUB_NATIVE",
                "lane": mode,
                "repository": "Jktomy/atlas-prime",
                "base_branch": "main",
                "expected_base": "a" * 40,
                "expected_head": expected_head,
                "branch": "proof/foundry-harmless-r01",
                "pull_request": pull_request,
                "declared_paths": operations,
                "workflow_rules": [],
                "receipt_contract": {
                    "write_on_interrupt": True,
                    "write_on_failure": True,
                    "write_on_success": True,
                    "automatic_retry": False,
                    "automatic_rollback": False,
                    "interrupt_exit_code": 130,
                    "failure_exit_code": 1,
                },
                "authorization": {
                    "approved_preview": True,
                    "execution_authorized": True,
                    "authorizer": "JAYSON",
                    "operator": "JAYSON",
                    "github_login": "Jktomy",
                },
                "stop_boundary": "Stop at a harmless draft PR.",
                "forbidden_actions": ["DIRECT_MAIN", "FORCE_PUSH", "SCOPE_WIDENING", "TOKEN_PERSISTENCE"],
            }
            if mode == "BUILD":
                oathbringer["commit_message"] = "Proof: Foundry harmless BUILD"
                oathbringer["pull_request_contract"] = {"title": "Proof: Foundry harmless BUILD", "body": "Public-clean fixture.", "draft": True}
            elif mode == "REPAIR":
                oathbringer["commit_message"] = "Proof: Foundry harmless REPAIR"
            elif mode == "EXECUTE":
                audit = self.input_root / "audit" / "green.json"
                audit.parent.mkdir(parents=True, exist_ok=True)
                audit.write_text(json.dumps({"verdict": "GREEN", "exact_head": expected_head}) + "\n", encoding="utf-8", newline="\n")
                oathbringer["independent_audit"] = {"verdict": "GREEN", "exact_head": expected_head, "receipt_path": "audit/green.json", "receipt_sha256": digest(audit)}
                oathbringer["merge_method"] = "squash"
        return {
            "format_version": "1.0",
            "compiler_identity": "SWORD_FORGE_COMPILER_V1",
            "mode": mode,
            "mission_id": f"FOUNDRY-{mode}-TEST",
            "revision": "R01",
            "authority": {
                "authorizer": "JAYSON",
                "operator": "JAYSON",
                "repository": "Jktomy/atlas-prime",
                "execution_authorized": True,
                "merge_authorized": False,
            },
            "source_lock": {
                "base_branch": "main",
                "expected_base": "a" * 40,
                "expected_head": expected_head,
                "workflow_sources": [],
                "source_paths": [dict(item) for item in self.locked_source_paths],
            },
            "target_lock": {"branch": "proof/foundry-harmless-r01", "pull_request": pull_request},
            "operations": operations,
            "lesson_applicability": [
                {"lesson_id": f"SWORD-L{number:03d}", "status": "APPLIED"}
                for number in range(1, 14)
            ],
            "privacy_classification": "PUBLIC_CLEAN",
            "stop_boundary": "Stop at the declared lane boundary.",
            "rollback": "Preserve the carrier and open a new reviewed recovery or rollback PR.",
            "oathbringer_mission": oathbringer,
        }

    def _live(self, mission: dict) -> dict:
        return {
            "repository": "Jktomy/atlas-prime",
            "base_branch": "main",
            "base_sha": "a" * 40,
            "head_sha": mission["source_lock"]["expected_head"],
            "pull_request": mission["target_lock"]["pull_request"],
            "pull_request_branch": None if mission["mode"] == "BUILD" else mission["target_lock"]["branch"],
            "pull_request_base_branch": None if mission["mode"] == "BUILD" else "main",
            "pull_request_base_sha": None if mission["mode"] == "BUILD" else "a" * 40,
            "pull_request_state": None if mission["mode"] == "BUILD" else "open",
            "target_branch_exists": mission["mode"] != "BUILD",
            "open_pull_request_count": 0 if mission["mode"] == "BUILD" else 1,
            "github_login": "Jktomy",
            "workflow_blobs": {},
        }

    def _compile(self, mission: dict, name: str = "out"):
        return compile_carrier(
            mission,
            input_root=self.input_root,
            source_root=ROOT,
            output_dir=self.root / name,
            live_state=self._live(mission),
        )

    def test_repeated_compile_is_byte_identical_and_manifest_complete(self) -> None:
        mission = self._mission()
        first = self._compile(mission, "first")
        second = self._compile(mission, "second")
        self.assertEqual(first.carrier_sha256, second.carrier_sha256)
        self.assertEqual(first.carrier_path.read_bytes(), second.carrier_path.read_bytes())
        self.assertEqual(verify_carrier(first.carrier_path)["status"], "PASS")
        with zipfile.ZipFile(first.carrier_path) as archive:
            names = set(archive.namelist())
            self.assertIn("oathbringer-mission.json", names)
            self.assertIn("payload/harmless.txt", names)
            self.assertIn("source/methods/sword-lessons.json", names)
            self.assertIn("engine/oathbringer_github.py", names)
            self.assertIn("launcher/Invoke-OathbringerCarrier.ps1", names)
            self.assertIn("FORGE-RECEIPT.json", names)
            self.assertIn("MANIFEST.json", names)
            self.assertIn("SHA256SUMS.txt", names)
            self.assertTrue(all(info.compress_size == info.file_size for info in archive.infolist()))

    def test_carrier_embeds_a_valid_production_oathbringer_mission(self) -> None:
        result = self._compile(self._mission())
        extracted = self.root / "extracted"
        with zipfile.ZipFile(result.carrier_path) as archive:
            archive.extractall(extracted)
        sys.path.insert(0, str(extracted / "engine"))
        try:
            import oathbringer_core

            oathbringer_core.validate_mission(load_json(extracted / "oathbringer-mission.json"))
        finally:
            sys.path.pop(0)

    def test_recovery_compiles_without_claiming_an_executor_lane(self) -> None:
        result = self._compile(self._mission("RECOVERY"))
        with zipfile.ZipFile(result.carrier_path) as archive:
            self.assertNotIn("oathbringer-mission.json", archive.namelist())
            receipt = json.loads(archive.read("FORGE-RECEIPT.json"))
            self.assertEqual(receipt["mode"], "RECOVERY")
            self.assertFalse(receipt["compiler_is_writer"])

    def test_stale_live_base_and_replay_are_rejected(self) -> None:
        mission = self._mission()
        stale = self._live(mission)
        stale["base_sha"] = "c" * 40
        with self.assertRaisesRegex(FoundryError, "base SHA drift"):
            bind_live_state(mission, stale, ROOT)
        with self.assertRaisesRegex(FoundryError, "replayed mission"):
            compile_carrier(mission, input_root=self.input_root, source_root=ROOT, output_dir=self.root / "replay", live_state=self._live(mission), seen_mission_ids=[mission["mission_id"]])

    def test_existing_build_target_and_repair_pr_base_drift_are_rejected(self) -> None:
        build = self._mission()
        occupied = self._live(build)
        occupied["target_branch_exists"] = True
        with self.assertRaisesRegex(FoundryError, "target branch already exists"):
            bind_live_state(build, occupied, ROOT)
        repair = self._mission("REPAIR")
        stale = self._live(repair)
        stale["pull_request_base_sha"] = "c" * 40
        with self.assertRaisesRegex(FoundryError, "base SHA drift"):
            bind_live_state(repair, stale, ROOT)

    def test_payload_and_audit_paths_cannot_replace_carrier_material(self) -> None:
        mission = self._mission()
        mission["operations"][0]["payload_path"] = "engine/oathbringer_github.py"
        mission["oathbringer_mission"]["declared_paths"] = mission["operations"]
        with self.assertRaisesRegex(FoundryError, "must be under payload"):
            self._compile(mission)
        execute = self._mission("EXECUTE")
        execute["oathbringer_mission"]["independent_audit"]["receipt_path"] = "FORGE-RECEIPT.json"
        with self.assertRaisesRegex(FoundryError, "must be under audit"):
            self._compile(execute)

    def test_every_current_engine_source_is_locked(self) -> None:
        mission = self._mission()
        mission["source_lock"]["source_paths"].pop()
        with self.assertRaisesRegex(FoundryError, "every current engine file"):
            self._compile(mission)

    def test_production_replay_ledger_is_durable_and_fail_closed(self) -> None:
        ledger = self.root / "ledger" / REPLAY_LEDGER_NAME
        self.assertEqual(_read_replay_ledger(ledger), [])
        _record_replay_ledger(ledger, "FOUNDRY-ONE")
        self.assertEqual(_read_replay_ledger(ledger), ["FOUNDRY-ONE"])
        with self.assertRaisesRegex(FoundryError, "replayed mission"):
            _record_replay_ledger(ledger, "FOUNDRY-ONE")

    def test_live_binding_requires_exact_branch_and_actual_open_pull_set(self) -> None:
        branch = "proof/foundry-harmless-r01"
        with patch.object(foundry_module, "_gh_json", return_value=[{"ref": f"refs/heads/{branch}-suffix"}]):
            self.assertFalse(foundry_module._target_branch_exists("Jktomy/atlas-prime", branch))
        mission = self._mission("REPAIR")

        def read(path: str):
            if path.startswith("repos/Jktomy/atlas-prime/git/ref/heads/"):
                return {"object": {"sha": "a" * 40}}
            if path == "user":
                return {"login": "Jktomy"}
            if path.startswith("repos/Jktomy/atlas-prime/pulls?state=open"):
                return [{"number": 91, "head": {"ref": branch}, "base": {"ref": "main"}}]
            if path.startswith("repos/Jktomy/atlas-prime/git/matching-refs/"):
                return [{"ref": f"refs/heads/{branch}"}]
            if path == "repos/Jktomy/atlas-prime/pulls/91":
                return {"number": 91, "state": "open", "head": {"sha": "b" * 40, "ref": branch}, "base": {"sha": "a" * 40, "ref": "main"}}
            raise AssertionError(path)

        with patch.object(foundry_module, "_gh_json", side_effect=read):
            state = read_live_state(mission)
        self.assertEqual(state["open_pull_request_count"], 1)
        self.assertTrue(state["target_branch_exists"])

    def test_unsafe_paths_collisions_and_protected_material_fail_closed(self) -> None:
        mission = self._mission()
        mission["operations"][0]["path"] = "../escape.txt"
        mission["oathbringer_mission"]["declared_paths"] = mission["operations"]
        with self.assertRaisesRegex(FoundryError, "unsafe"):
            self._compile(mission)
        mission = self._mission()
        mission["operations"].append({"path": "Proof/FOUNDRY-HARMLESS.TXT", "operation": "ADD", "payload_path": "payload/harmless.txt", "payload_sha256": digest(self.payload)})
        mission["oathbringer_mission"]["declared_paths"] = mission["operations"]
        with self.assertRaisesRegex(FoundryError, "case-fold"):
            self._compile(mission)
        token_shaped_fixture = "gh" + "p_" + "abcdefghijklmnopqrstuvwxyz123456"
        self.payload.write_text(token_shaped_fixture + "\n", encoding="utf-8", newline="\n")
        mission = self._mission()
        with self.assertRaisesRegex(FoundryError, "protected"):
            self._compile(mission)
        for token in ("github_pat_" + "a" * 24, "sk-" + "a" * 24):
            self.payload.write_text(token + "\n", encoding="utf-8", newline="\n")
            with self.assertRaisesRegex(FoundryError, "protected"):
                self._compile(self._mission())
        mission = self._mission()
        mission["oathbringer_mission"]["commit_message"] = "sk-" + "b" * 24
        with self.assertRaisesRegex(FoundryError, "protected"):
            self._compile(mission)
        for raw, expected in ((b"\xef\xbb\xbfpublic\n", "without BOM"), (b"public\r\n", "LF line endings")):
            self.payload.write_bytes(raw)
            with self.assertRaisesRegex(FoundryError, expected):
                self._compile(self._mission())

    def test_archive_path_attack_is_rejected(self) -> None:
        bad = self.root / "bad.zip"
        with zipfile.ZipFile(bad, "w") as archive:
            archive.writestr("../escape.txt", "no")
        with self.assertRaisesRegex(FoundryError, "unsafe segment"):
            verify_carrier(bad)

    def test_archive_extra_member_is_rejected(self) -> None:
        carrier = self._compile(self._mission()).carrier_path
        altered = self.root / "altered.zip"
        shutil.copy2(carrier, altered)
        with zipfile.ZipFile(altered, "a") as archive:
            archive.writestr("undeclared.txt", "unexpected\n")
        with self.assertRaisesRegex(FoundryError, "undeclared"):
            verify_carrier(altered)

    def test_archive_casefold_and_compression_attacks_are_rejected(self) -> None:
        carrier = self._compile(self._mission()).carrier_path
        casefold = self.root / "casefold.zip"
        shutil.copy2(carrier, casefold)
        with zipfile.ZipFile(casefold, "a") as archive:
            archive.writestr("payload/HARMLESS.TXT", "collision\n")
        with self.assertRaisesRegex(FoundryError, "case-fold"):
            verify_carrier(casefold)
        compressed = self.root / "compressed.zip"
        with zipfile.ZipFile(carrier) as source, zipfile.ZipFile(compressed, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in source.infolist():
                info = zipfile.ZipInfo(item.filename)
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, source.read(item.filename))
        with self.assertRaisesRegex(FoundryError, "compression"):
            verify_carrier(compressed)

    def test_archive_encryption_flag_is_rejected(self) -> None:
        carrier = self._compile(self._mission()).carrier_path
        original = zipfile.ZipFile.infolist

        def encrypted(archive):
            infos = original(archive)
            infos[0].flag_bits |= 0x1
            return infos

        with patch.object(zipfile.ZipFile, "infolist", encrypted):
            with self.assertRaisesRegex(FoundryError, "encrypted"):
                verify_carrier(carrier)

    def test_source_has_no_mutating_client_or_secret_persistence(self) -> None:
        source = (FOUNDRY_ROOT / "foundry.py").read_text(encoding="utf-8")
        self.assertIn("read-only", source)
        self.assertIn('["gh", "api", path]', source)
        for token in ("git push", "gh pr create", "gh pr merge", "create_pull_request", "create_ref", "Authorization: Bearer"):
            self.assertNotIn(token, source)
        launcher = (FOUNDRY_ROOT / "Invoke-OathbringerFoundry.ps1").read_text(encoding="utf-8")
        self.assertIn("$PSScriptRoot", launcher)
        self.assertNotIn("Invoke-Expression", launcher)

    def test_cli_requires_a_fresh_read_only_snapshot(self) -> None:
        source = (FOUNDRY_ROOT / "cli.py").read_text(encoding="utf-8")
        self.assertNotIn('add_argument("--live-state"', source)
        self.assertNotIn('add_argument("--bind-live"', source)
        self.assertIn("live = read_live_state(mission)", source)
        self.assertIn("REPLAY_LEDGER_NAME", source)
        self.assertIn("_record_replay_ledger", source)
        launcher = (FOUNDRY_ROOT / "Invoke-OathbringerFoundry.ps1").read_text(encoding="utf-8")
        readme = (FOUNDRY_ROOT / "README.md").read_text(encoding="utf-8")
        doctrine = (ROOT / "methods" / "oathbringer-foundry.md").read_text(encoding="utf-8")
        for surface in (launcher, readme, doctrine):
            self.assertNotIn("--live-state", surface)
            self.assertNotIn("--bind-live", surface)


if __name__ == "__main__":
    unittest.main()
