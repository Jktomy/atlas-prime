from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.athena_routes.schema import validate_schema


ROOT = Path(__file__).resolve().parents[2]


class CloudAtlasProtectedRealmTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = (ROOT / "governance/cloud-atlas-protected-realm-contract.md").read_text(encoding="utf-8")
        self.schema = json.loads((ROOT / "schemas/cloud-atlas-protected-realm-v1.schema.json").read_text(encoding="utf-8"))
        self.realm = json.loads((ROOT / "governance/cloud-atlas-protected-realm-v1.json").read_text(encoding="utf-8"))
        self.quest = (ROOT / "quests/prime-ascendant.md").read_text(encoding="utf-8")

    def test_machine_contract_validates_and_has_exact_classes(self) -> None:
        validate_schema(self.schema, self.realm)
        self.assertEqual(self.realm["deployment_state"], "SOURCE_ARCHITECTURE_ONLY")
        self.assertEqual(
            {item["id"] for item in self.realm["data_classes"]},
            {
                "PROTECTED_ORIGINAL",
                "EXTRACTED_REPRESENTATION",
                "STRUCTURED_RECORD",
                "SANITIZED_SUMMARY",
                "PUBLIC_CLEAN_EXPORT",
                "DERIVED_INDEX_OR_EMBEDDING",
                "AUDIT_RECEIPT",
                "PROTECTED_POINTER",
            },
        )

    def test_service_identities_and_denials_are_separate(self) -> None:
        services = {item["id"]: item for item in self.realm["services"]}
        self.assertEqual(set(services), {"PRIME", "ORIGINAL_VAULT", "COPPERMIND", "EMBERDARK", "HARMONY", "PHOENIX", "SECRET_SYSTEM"})
        self.assertIn("DIRECT_CLIENT_SQL", services["COPPERMIND"]["never"])
        self.assertIn("UNRESTRICTED_VAULT_READ", services["HARMONY"]["never"])
        self.assertIn("VAULT_ACCESS_BY_COLOCATION", services["PHOENIX"]["never"])
        self.assertIn("COPPERMIND_RECORD", services["SECRET_SYSTEM"]["never"])
        self.assertIn("NO_BROWSER_OR_MODEL_UNRESTRICTED_SQL", self.realm["access_rules"])

    def test_provenance_export_recovery_and_degraded_modes_fail_closed(self) -> None:
        self.assertIn("Every derivative binds", self.contract)
        self.assertIn("Sanitization is an explicit, receipted transform", self.contract)
        self.assertIn("FAILED_OR_AMBIGUOUS_EXPORT_IS_QUARANTINED", self.realm["export_rules"])
        self.assertEqual(set(self.realm["recovery"].values()) - {"FORGE_ENCRYPTED_RECOVERY_DESTINATION_NOT_PRIMARY_RUNTIME"}, {"REQUIRED_UNPROVEN"})
        self.assertEqual(self.realm["degraded_modes"]["COPPERMIND_UNAVAILABLE"], "CANONICAL_SOURCE_ONLY")
        self.assertEqual(self.realm["degraded_modes"]["EMBERDARK_UNAVAILABLE"], "QUEUE_NO_REPLAY")
        self.assertEqual(self.realm["degraded_modes"]["ORIGINAL_VAULT_UNAVAILABLE"], "UNAVAILABLE_FAIL_CLOSED")

    def test_source_architecture_advances_no_runtime_gate(self) -> None:
        for marker in (
            "not a Project,\nQuest, database, host, or deployment claim",
            "No public endpoint, unrestricted SQL authority",
            "It does not advance PA-C01",
            "NO_POSTGRESQL_ACTIVATION",
            "NO_PGVECTOR_ACTIVATION",
            "NO_PROTECTED_IMPORT",
            "NO_SECRET_CREATION",
            "NO_GITEA_ACTIVATION",
            "NO_GATE_ADVANCEMENT",
        ):
            self.assertIn(marker, self.contract + self.quest + json.dumps(self.realm, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
