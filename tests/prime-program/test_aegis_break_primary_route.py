from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def tuple_assignment(source: str, name: str) -> tuple[str, ...]:
    module = ast.parse(source)
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                value = ast.literal_eval(node.value)
                if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
                    return value
    raise AssertionError(f"missing exact tuple assignment: {name}")


class AegisBreakPrimaryRouteTests(unittest.TestCase):
    def test_controlling_contract_defines_current_github_route(self) -> None:
        contract = text("governance/aegis-break-primary-route-contract.md")
        for marker in (
            "ATHENA_AEGIS_BREAK",
            "DIRECT_GITHUB_NATIVE_AEGIS_BREAK",
            "CURRENT_GITHUB_SPEAR_RETIRED",
            "one single-parent commit",
            "Jayson-controlled permanence",
            "future Gitea",
        ):
            self.assertIn(marker, contract)
        for forbidden in ("standing writer", "direct main", "force push", "automatic merge"):
            self.assertIn(forbidden, contract)

    def test_startup_and_command_surfaces_select_aegis_break(self) -> None:
        readme = text("README.md")
        bootstrap = text("bootstrap.md")
        commands = text("routing/command-surfaces.md")
        self.assertIn("Aegis Break -> exact GitHub-native atomic transaction", readme)
        self.assertIn("Aegis Break is Athena's primary method", bootstrap)
        self.assertIn("Aegis Break primary route", commands)
        self.assertIn("Direct GitHub-native construction is an Aegis Break route", commands)

    def test_sunset_router_auto_is_aegis_break_and_spear_fails_closed(self) -> None:
        source = text("tools/sunset_router/core.py")
        self.assertEqual(
            tuple_assignment(source, "ATHENA_CURRENT_ROUTES"),
            ("ATHENA_AEGIS_BREAK", "ATHENA_PHOENIX_BLADE"),
        )
        self.assertEqual(
            tuple_assignment(source, "ATHENA_HISTORICAL_ROUTES"),
            ("ATHENA_SPEAR_THREAD_ENGINE",),
        )
        self.assertIn('"CURRENT_GITHUB_SPEAR_RETIRED"', source)

    def test_github_direct_spear_workflow_is_absent_but_history_remains(self) -> None:
        self.assertFalse((ROOT / ".github/workflows/athena-spear-issue-ingress.yml").exists())
        self.assertTrue((ROOT / "tools/athena_routes/spear_issue_ingress.py").is_file())
        acceptance = text("governance/capability-acceptance-contract.md")
        parity = json.loads(text("governance/capability-parity-register.json"))
        cap015 = next(item for item in parity["capabilities"] if item["id"] == "CAP-015")
        self.assertIn("AJ-01 is `PROVEN`", acceptance)
        self.assertEqual(cap015["capability_disposition"], "RESTORED")
        self.assertIn("PR #102", cap015["current_state"])

    def test_status_separates_component_proof_from_current_route(self) -> None:
        status = json.loads(text("tools/thread-engine/PRIME-PORT-STATUS.json"))
        self.assertEqual(status["implementation_state"], "THREAD_ENGINE_ACTIVE_MISSION_SCOPED")
        self.assertEqual(status["spear_arrow_bow_state"], "PROVEN_MERGED")
        self.assertEqual(status["current_github_primary_method"], "ATHENA_AEGIS_BREAK")
        self.assertEqual(
            status["current_github_write_substrate"],
            "DIRECT_GITHUB_NATIVE_AEGIS_BREAK",
        )
        self.assertEqual(status["github_direct_spear_ingress"], "RETIRED_WORKFLOW_ABSENT")
        self.assertEqual(status["future_gitea_spear_state"], "PLANNING_ONLY_PA_C06")
        self.assertFalse(status["standing_authority"])
        self.assertFalse(status["direct_main"])
        self.assertFalse(status["automatic_merge"])

    def test_assurance_control_preserves_one_transaction_and_recovery_isolation(self) -> None:
        controls = json.loads(text("governance/assurance-controls.json"))["controls"]
        asc003 = next(item for item in controls if item["control_id"] == "ASC-003")
        self.assertIn("Aegis Break", asc003["objective"])
        self.assertIn("Candidate Seal", asc003["required_evidence"][0])
        self.assertTrue(
            any("Sword/Oathbringer" in item for item in asc003["required_evidence"])
        )


if __name__ == "__main__":
    unittest.main()
