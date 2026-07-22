from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class FoundSilverlightDoctrineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quest = (ROOT / "quests/found-silverlight.md").read_text(encoding="utf-8")
        self.contract = (ROOT / "governance/investiture-accounting-contract.md").read_text(encoding="utf-8")
        self.route = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
        self.board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
        self.continuity = json.loads(
            (ROOT / "continuity/prime-continuity-register-r01.json").read_text(encoding="utf-8")
        )

    def test_stable_lineage_advances_only_through_doctrine(self) -> None:
        self.assertIn("Quest ID:** `QUEST-FOUND-SILVERLIGHT-R01`", self.quest)
        self.assertIn("## Campaign FS-C01 — Infuse the Gemstone", self.quest)
        self.assertIn("**State:** `PROVEN`", self.quest)
        for gate in (
            "INVESTITURE_ACCOUNTING_DOCTRINE_ACCEPTED",
            "APPEND_ONLY_INVESTITURE_LEDGER_CONSTRUCTION_PROVEN",
            "INVESTITURE_RECEIPT_AND_LIFECYCLE_BINDING_PROVEN",
            "INVESTITURE_ACCOUNTING_LIVE_ACCEPTANCE_PROVEN",
            "INVESTITURE_ACCOUNTING_INDEPENDENTLY_PROVEN",
        ):
            self.assertIn(gate, self.quest)
            self.assertIn(gate, self.contract)
        self.assertIn("Accepted historical Mission: FS-C01-M03 — Bind the Receipts", self.quest)
        self.assertIn("Unfinished successor work: FS-C01-M04 — Prove the Light", self.quest)
        self.assertIn("Runtime deployment: NOT STARTED", self.quest)
        self.assertIn("External-system action: NOT AUTHORIZED", self.quest)

    def test_accounting_identity_and_non_overlap_are_exact(self) -> None:
        identity = (ROOT / "governance/investiture-source-identity-contract.md").read_text(encoding="utf-8")
        self.assertIn("One trusted provider/runtime-reported model token equals one BEU", self.contract)
        for light in ("Spirallight", "Chromelight", "Emberlight"):
            self.assertIn(f"`{light}`", self.contract)
        for state in ("MEASURED", "PARTIAL", "UNAVAILABLE", "ZERO_MODEL"):
            self.assertIn(f"`{state}`", self.contract)
        self.assertIn("`ESTIMATED`\nis not an accepted accounting state", self.contract)
        self.assertIn("`AUTHORITATIVE_TOTAL`", self.contract)
        self.assertIn("`DISJOINT_LEAVES`", self.contract)
        self.assertIn("There is\nno hybrid Light", self.contract)
        self.assertIn("Only an exact `USAGE_REPORTED` event may contribute BEU", self.contract)
        self.assertIn("never\nrecount it", self.contract)
        self.assertIn("consumes exactly zero\nBEU", self.contract)
        self.assertIn("accounting Light identities\n  derived only from trusted provider/runtime evidence", self.quest)
        self.assertIn("independent provider, model, runtime-control, work-surface, route, engine", self.quest)
        self.assertIn("`governance/investiture-accounting-contract.md`", identity)
        self.assertIn("continuity event history preserved", identity)
        self.assertNotIn("will be modernized", identity)
        self.assertNotIn("provider/runtime identities", self.quest)

    def test_private_storage_and_live_acceptance_remain_external(self) -> None:
        self.assertIn("require an explicit Jayson-selected external\nstore root", self.contract)
        self.assertIn("Prime supplies no default", self.contract)
        self.assertIn("never emits the absolute path", self.contract)
        self.assertIn("protected external store\nselected by Jayson", self.contract)
        self.assertIn("one bounded real model task", self.contract)
        self.assertIn("does not choose a private\nstorage location", self.contract)
        for forbidden_claim in ("runtime activated", "provider activated", "external store selected"):
            self.assertNotIn(forbidden_claim, self.contract.lower())

    def test_stormlight_is_retired_without_rewriting_legacy_evidence(self) -> None:
        identity = (ROOT / "governance/investiture-source-identity-contract.md").read_text(encoding="utf-8")
        legacy_schema = (ROOT / "schemas/chromelight-evidence-register-v1.schema.json").read_text(encoding="utf-8")
        legacy_proof = (ROOT / "proof/repairing-prime/rp-c03-chromelight-evidence-r01.json").read_text(encoding="utf-8")
        self.assertIn("Stormlight historical migration boundary", self.quest)
        self.assertIn("frozen legacy `stormlight`", self.contract)
        self.assertIn("`Stormlight` is retired", identity)
        self.assertIn('"stormlight"', legacy_schema)
        self.assertIn('"stormlight"', legacy_proof)
        self.assertIn("never rewritten or converted", self.contract)

    def test_board_continuity_and_route_are_exact(self) -> None:
        board_entry = next(
            item for item in self.board["entries"] if item["quest_id"] == "QUEST-FOUND-SILVERLIGHT-R01"
        )
        self.assertEqual(board_entry["state"], "COMPLETE")
        self.assertEqual(board_entry["next_gate"], "CLOSED")
        self.assertNotIn(
            "CONT-FOUND-SILVERLIGHT-R01",
            {item["continuity_id"] for item in self.continuity["entries"]},
        )
        fs_event = "FS-C01-M02-M03-CONSTRUCTION-ACCEPTANCE-R01"
        later_event = "RP-C08-CAP015-ARCHITECTURE-REALIGNMENT-R02"
        naming_event = "FS-C03-HERMES-BRIDGE-NAMING-R01"
        sunset_event = "FOUND-SILVERLIGHT-DECOMPOSITION-SUNSET-R01"
        self.assertEqual(self.continuity["event_ids"].count(fs_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(later_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(naming_event), 1)
        self.assertEqual(self.continuity["event_ids"].count(sunset_event), 1)
        self.assertLess(self.continuity["event_ids"].index(fs_event), self.continuity["event_ids"].index(later_event))
        self.assertLess(self.continuity["event_ids"].index(later_event), self.continuity["event_ids"].index(naming_event))
        self.assertLess(self.continuity["event_ids"].index(naming_event), self.continuity["event_ids"].index(sunset_event))

    def test_sunset_has_one_successor_per_responsibility_without_advancement(self) -> None:
        for successor in (
            "Codex / Operation Source Governance bounded Mission family",
            "Prime Ascendant / Operation Glass Codex",
            "Prime Ascendant / Operation Harmony",
        ):
            self.assertEqual(self.quest.count(f"| {successor} |"), 1)
        self.assertIn("FS-C01-M01 through M03 remain `PROVEN`", self.quest)
        self.assertIn("FS-C01-M04 remains `UNFINISHED`", self.quest)
        self.assertIn("Apple Reminders remains authoritative", self.quest)
        self.assertIn("Hermes remains the proposed macOS bridge vessel", self.quest)
        self.assertIn("Runtime deployment: NOT STARTED", self.quest)
        self.assertIn("External-system action: NOT AUTHORIZED", self.quest)
        self.assertIn("governance/investiture-accounting-contract.md", self.route)

    def test_repairing_prime_identity_register_is_not_widened(self) -> None:
        identities = json.loads(
            (ROOT / "continuity/quest-engine-identities-r01.json").read_text(encoding="utf-8")
        )
        self.assertEqual(identities["quest_id"], "QUEST-REPAIRING-PRIME-R01")
        self.assertNotIn("FS-C01", {campaign["campaign_id"] for campaign in identities["campaigns"]})


if __name__ == "__main__":
    unittest.main()
