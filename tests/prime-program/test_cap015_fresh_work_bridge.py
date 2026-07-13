from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class Cap015FreshWorkBridgeSourceTests(unittest.TestCase):
    def test_required_source_surface_exists_and_is_routed(self) -> None:
        required = (
            "governance/athena-fresh-work-origin-contract.md",
            "schemas/athena-fresh-work-origin-receipt-v1.schema.json",
            "schemas/athena-fresh-work-journey-receipt-v1.schema.json",
            "tools/athena_routes/fresh_work_bridge.py",
            "tests/athena-routes/test_fresh_work_bridge.py",
        )
        for relative in required:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())

        command_surface = (ROOT / "routing/command-surfaces.md").read_text(
            encoding="utf-8"
        )
        readme = (ROOT / "tools/athena_routes/README.md").read_text(
            encoding="utf-8"
        )
        for text in (command_surface, readme):
            self.assertIn("athena-fresh-work-origin-contract.md", text)
            self.assertIn("athena-fresh-work-origin-receipt-v1.schema.json", text)
            self.assertIn("athena-fresh-work-journey-receipt-v1.schema.json", text)
            self.assertIn("fresh_work_bridge", text)
            self.assertIn("CAP-015", text)

    def test_contract_is_construction_only_and_nonpromoting(self) -> None:
        contract = (ROOT / "governance/athena-fresh-work-origin-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('status: "CONSTRUCTION_ONLY_NOT_ACTIVATED"', contract)
        self.assertIn("do not prove", contract)
        self.assertIn("TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE", contract)
        self.assertIn("singular existing Thread Engine", contract)
        self.assertIn("separate reviewed authored reconciliation", contract)
        self.assertIn("no dispatch-capable implementation", contract)

        register = json.loads(
            (ROOT / "governance/capability-parity-register.json").read_text(
                encoding="utf-8"
            )
        )
        cap015 = next(item for item in register["capabilities"] if item["id"] == "CAP-015")
        self.assertEqual(cap015["capability_disposition"], "STILL_MISSING")
        self.assertEqual(cap015["activation_state"], "MISSING")

    def test_bridge_has_no_dispatch_writer_or_dynamic_trust_loader(self) -> None:
        path = ROOT / "tools/athena_routes/fresh_work_bridge.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])

        self.assertTrue(
            imported.isdisjoint(
                {
                    "subprocess",
                    "shutil",
                    "socket",
                    "requests",
                    "urllib",
                    "git",
                    "github",
                    "importlib",
                }
            )
        )
        for forbidden in (
            "execute_preview",
            "guided_publisher",
            "gh workflow",
            "workflow run",
            "create_tree",
            "create_commit",
            "update_ref",
            "create_pull_request",
            "merge_pull_request",
            "mark_pull_request_ready_for_review",
            "eval(",
            "exec(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertIn("READ_ONLY_CANDIDATE_NOT_EXECUTABLE", source)
        self.assertIn('"remote_dispatch_authority": False', source)
        self.assertIn('"guided_execute_invoked": False', source)
        self.assertIn("TRUSTED_ORIGIN_VERIFIER_UNAVAILABLE", source)

    def test_origin_and_journey_schemas_are_closed(self) -> None:
        origin = json.loads(
            (
                ROOT
                / "schemas/athena-fresh-work-origin-receipt-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        journey = json.loads(
            (
                ROOT
                / "schemas/athena-fresh-work-journey-receipt-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(origin["additionalProperties"])
        self.assertFalse(journey["additionalProperties"])
        self.assertEqual(origin["properties"]["authorizer"]["const"], "Jayson")
        self.assertEqual(origin["properties"]["semantic_invoker"]["const"], "Athena")
        self.assertEqual(
            origin["properties"]["originating_surface"]["const"],
            "CHATGPT_WORK",
        )
        forbidden = origin["properties"]["forbidden_fields_absent"]
        self.assertFalse(forbidden["additionalProperties"])
        self.assertTrue(
            all(value == {"const": True} for value in forbidden["properties"].values())
        )
        bridge_mutation = journey["properties"]["bridge_mutation"]
        self.assertFalse(bridge_mutation["additionalProperties"])
        self.assertTrue(
            all(value == {"const": False} for value in bridge_mutation["properties"].values())
        )


if __name__ == "__main__":
    unittest.main()
