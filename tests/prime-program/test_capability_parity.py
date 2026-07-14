from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = ROOT / "governance/capability-parity-register.json"
SCHEMA_PATH = ROOT / "schemas/capability-parity-register.schema.json"
ARCHITECTURE = ROOT / "governance/athena-route-architecture-r01.md"
DISPOSITIONS = (
    "PRESERVED",
    "IMPROVED",
    "RESTORED",
    "REPLACED",
    "INTENTIONALLY_RETIRED",
    "BLOCKED",
    "STILL_MISSING",
)


class CapabilityParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.records = {
            record["id"]: record for record in self.register["capabilities"]
        }

    def test_register_is_exactly_the_frozen_28_capability_set(self) -> None:
        records = self.register["capabilities"]
        self.assertEqual(len(records), 28)
        self.assertEqual(
            [record["id"] for record in records],
            [f"CAP-{number:03d}" for number in range(1, 29)],
        )
        self.assertEqual(len({record["capability"] for record in records}), 28)
        self.assertEqual(
            self.register["predecessor_head"],
            "c892dc05ea56db0134a0e865f56d491f9c02ff85",
        )

    def test_path_and_capability_dispositions_are_separate(self) -> None:
        authority = self.register["path_disposition_authority"]
        self.assertEqual(
            (
                authority["tracked_paths"],
                authority["closed_paths"],
                authority["open_paths"],
            ),
            (525, 525, 0),
        )
        self.assertIn(
            "never establishes capability parity",
            authority["authority_boundary"],
        )

    def test_disposition_vocabulary_and_counts_are_exact(self) -> None:
        self.assertEqual(
            tuple(self.register["capability_disposition_vocabulary"]),
            DISPOSITIONS,
        )
        observed = Counter(
            record["capability_disposition"]
            for record in self.register["capabilities"]
        )
        self.assertEqual(
            self.register["capability_disposition_counts"],
            {
                "PRESERVED": 4,
                "IMPROVED": 7,
                "RESTORED": 14,
                "REPLACED": 1,
                "INTENTIONALLY_RETIRED": 1,
                "BLOCKED": 0,
                "STILL_MISSING": 1,
            },
        )
        self.assertEqual(
            dict(observed),
            {
                key: value
                for key, value in self.register[
                    "capability_disposition_counts"
                ].items()
                if value
            },
        )
        self.assertEqual(sum(observed.values()), 28)
        self.assertEqual(
            set(
                self.schema["properties"]["capabilities"]["items"]["properties"]
                ["capability_disposition"]["enum"]
            ),
            set(DISPOSITIONS),
        )

    def test_cap015_is_restored_and_cap027_remains_missing(self) -> None:
        cap015 = self.records["CAP-015"]
        self.assertEqual(
            cap015["capability"],
            "Athena can reach Thread Engine through Spear",
        )
        self.assertEqual(cap015["capability_disposition"], "RESTORED")
        self.assertEqual(cap015["activation_state"], "ACTIVE")
        self.assertEqual(cap015["audit_severity"], "GREEN")
        self.assertIn("PR #39", cap015["required_proof"])
        self.assertIn("No external origin bridge", cap015["current_state"])

        cap027 = self.records["CAP-027"]
        self.assertEqual(cap027["capability_disposition"], "STILL_MISSING")
        self.assertEqual(cap027["activation_state"], "MISSING")
        self.assertIn("AJ-03", cap027["current_state"])
        self.assertIn("AJ-11", cap027["current_state"])
        self.assertIn("AJ-12", cap027["current_state"])

    def test_hosted_routes_belong_to_jayson_and_artemis(self) -> None:
        self.assertEqual(
            self.records["CAP-009"]["capability"],
            "Jayson/Artemis hosted Arrow/Bow intake",
        )
        self.assertEqual(
            self.records["CAP-010"]["capability"],
            "Human-friendly owner-guided Arrow/Bow intake",
        )
        for identity in ("CAP-009", "CAP-010", "CAP-011"):
            self.assertEqual(
                self.records[identity]["capability_disposition"],
                "RESTORED",
            )
            self.assertEqual(
                self.records[identity]["activation_state"],
                "ACTIVE",
            )
        self.assertIn(
            "not Athena's Spear route",
            self.records["CAP-009"]["current_state"],
        )

    def test_guarded_multi_file_source_pack_is_live_restored(self) -> None:
        proof = json.loads(
            (
                ROOT
                / "proof/repairing-prime/"
                "rp-c08-cap011-reconciliation-r01.json"
            ).read_text(encoding="utf-8")
        )
        cap011 = self.records["CAP-011"]
        self.assertEqual(cap011["capability_disposition"], "RESTORED")
        self.assertEqual(cap011["activation_state"], "ACTIVE")
        self.assertEqual(
            proof["capability"],
            {
                "id": "CAP-011",
                "disposition": "RESTORED",
                "activation_state": "ACTIVE",
            },
        )
        self.assertEqual(
            len(proof["hosted_multifile_evidence"]["authored_paths"]),
            2,
        )
        self.assertEqual(
            proof["hosted_multifile_evidence"]["detached_review"],
            "GREEN",
        )

    def test_generated_parity_and_publisher_are_restored_by_aj09(self) -> None:
        proof = json.loads(
            (
                ROOT
                / "proof/repairing-prime/"
                "rp-c06-generated-parity-acceptance-r01.json"
            ).read_text(encoding="utf-8")
        )
        for capability_id in ("CAP-019", "CAP-020"):
            self.assertEqual(
                self.records[capability_id]["capability_disposition"],
                "RESTORED",
            )
            self.assertEqual(
                self.records[capability_id]["activation_state"],
                "ACTIVE",
            )
        self.assertEqual(
            proof["acceptance_journey"],
            {"id": "AJ-09", "state": "PROVEN"},
        )

    def test_legacy_oathbringer_capability_is_replaced(self) -> None:
        cap017 = self.records["CAP-017"]
        self.assertEqual(cap017["capability_disposition"], "REPLACED")
        self.assertEqual(cap017["activation_state"], "ACTIVE")
        self.assertEqual(
            cap017["audit_status"],
            "PRODUCTION_ROUTE_LIVE_PROVEN",
        )

    def test_route_terms_are_not_conflated(self) -> None:
        change_routes = (ROOT / "governance/change-routes.md").read_text(
            encoding="utf-8"
        )
        command_surfaces = (ROOT / "routing/command-surfaces.md").read_text(
            encoding="utf-8"
        )
        phoenix = (ROOT / "methods/phoenix-blade.md").read_text(
            encoding="utf-8"
        )
        spear = (ROOT / "methods/athenas-spear.md").read_text(
            encoding="utf-8"
        )
        bow = (ROOT / "methods/artemis-bow-and-arrow.md").read_text(
            encoding="utf-8"
        )
        sword = (ROOT / "methods/atlas-sword.md").read_text(
            encoding="utf-8"
        )
        architecture = ARCHITECTURE.read_text(encoding="utf-8")

        for term in (
            "Authorizer",
            "Operator",
            "Delivery route",
            "launcher",
            "Normal repository engine",
            "Repository substrate",
            "AI-assisted work surface",
            "Provider, model, and runtime identity",
        ):
            self.assertIn(term, change_routes)

        self.assertIn("Spear is Athena's direct delivery route", spear)
        self.assertIn("Prime Thread Engine", spear)
        self.assertIn(
            "Phoenix Blade is Athena's direct repository-construction method",
            phoenix,
        )
        self.assertIn(
            "functional counterpart to Jayson's\nOathbringer route",
            phoenix,
        )
        self.assertIn("Bow and Arrow belong to Jayson and Artemis", bow)
        self.assertIn("They are not Athena's route", bow)
        self.assertIn("PowerShell is the thin interactive client", sword)

        self.assertIn(
            "Aegis Break -> direct GitHub-native or other bounded safe route",
            change_routes,
        )
        self.assertNotIn("Aegis Break -> Phoenix Blade", change_routes)
        self.assertIn(
            "Aegis Break selects or constructs a safe equivalent route",
            change_routes,
        )
        self.assertIn("not hardwired", change_routes)

        self.assertIn("Spear is Athena's Thread Engine route", architecture)
        self.assertIn("JAYSON / ARTEMIS", architecture)
        self.assertIn("No external platform-origin", architecture)

        self.assertIn("routes to **Phoenix Blade**", command_surfaces)
        self.assertIn(
            "does not need to invoke a separate preflight command",
            command_surfaces,
        )
        self.assertIn(
            "Direct Athena work does not require ChatGPT Work / Codex",
            command_surfaces,
        )


if __name__ == "__main__":
    unittest.main()
