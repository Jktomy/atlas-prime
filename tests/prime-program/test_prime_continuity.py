from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.prime_continuity.cli import main as continuity_cli
from tools.prime_continuity.engine import (
    ContinuityError,
    argus,
    plan_one_entry_update,
    render_emberline,
    sha256,
    sunrise,
    sunset,
    validate_board,
    validate_identity_register,
    validate_quest_admission,
    validate_quest_registry,
    validate_register,
)


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class PrimeContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = load("quest-board/quest-board-v1.json")
        self.registry = load("continuity/mission-board-quest-registry-r01.json")
        self.register = load("continuity/prime-continuity-register-r01.json")
        self.identities = load("continuity/quest-engine-identities-r01.json")

    def test_canonical_registry_frozen_board_register_and_identities_validate(self) -> None:
        validate_board(self.board)
        validate_quest_registry(self.registry, self.board)
        validate_register(self.register, self.board, registry=self.registry)
        validate_identity_register(self.identities)

        self.assertEqual(self.board["registry_role"], "FROZEN_PREDECESSOR_EVIDENCE")
        self.assertEqual(
            self.board["successor_registry"],
            "continuity/mission-board-quest-registry-r01.json",
        )
        self.assertEqual(self.registry["authority"], "CANONICAL_ADMITTED_QUEST_REGISTRY")
        self.assertFalse(self.registry["live_issue_availability_required_for_recovery"])
        self.assertEqual(self.registry["registry_revision"], 1)
        self.assertEqual(
            {entry["quest_id"] for entry in self.registry["entries"]},
            {
                "QUEST-PRIME-ASCENDANT-20260717",
                "QUEST-PROMETHEUS-FIRE-20260701",
                "QUEST-NOTUMS-WATCH-20260708",
            },
        )
        self.assertEqual(
            {entry["parent_issue_number"] for entry in self.registry["entries"]},
            {307, 308, 309},
        )
        self.assertEqual(
            {entry["quest_id"] for entry in self.register["entries"]},
            {entry["quest_id"] for entry in self.registry["entries"]},
        )
        self.assertEqual(self.register["quest_board_sha256"], sha256(self.board))
        self.assertEqual(self.register["quest_registry_sha256"], sha256(self.registry))
        self.assertEqual(
            self.register["event_ids"].count("MISSION-BOARD-QUEST-REGISTRY-CUTOVER-R01"),
            1,
        )
        self.assertEqual(len(self.identities["campaigns"]), 8)

    def test_frozen_board_cannot_admit_a_quest(self) -> None:
        candidate = copy.deepcopy(self.board)
        candidate["entries"].append(copy.deepcopy(candidate["entries"][0]))
        with self.assertRaisesRegex(ContinuityError, "QUEST_BOARD_FROZEN"):
            validate_quest_admission(self.board, candidate, self.board)

    def test_schema_driven_registry_accepts_later_quest_without_validator_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for entry in self.board["entries"]:
                source = root / entry["source"]
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(f"# {entry['quest_id']}\n", encoding="utf-8")
            later = root / "quests" / "later-valid-quest.md"
            later.write_text("# Later valid Quest\n", encoding="utf-8")

            candidate = copy.deepcopy(self.registry)
            candidate["registry_revision"] += 1
            candidate["entries"].append(
                {
                    "next_gate": "LQ-C01 Preview",
                    "owner": "Atlas / Source Governance",
                    "quest_id": "QUEST-LATER-VALID-R01",
                    "readiness_basis": "Schema-valid later Quest with one unique parent Mission.",
                    "source": "quests/later-valid-quest.md",
                    "state": "READY_FOR_CAMPAIGN_1_PREVIEW",
                    "parent_issue_number": 999,
                    "parent_mission_id": "MISSION-QUEST-PARENT-LATER-VALID-R01",
                    "parent_attempt_id": "MISSION-QUEST-PARENT-LATER-VALID-R01-ATTEMPT-01",
                    "parent_mission_state": "CAPTURED",
                    "parent_source_status": "NO_SOURCE_CHANGE_REQUIRED",
                }
            )
            admitted = validate_quest_admission(
                self.registry,
                candidate,
                self.board,
                root=root,
            )
            self.assertEqual(admitted["quest_id"], "QUEST-LATER-VALID-R01")

            stale = copy.deepcopy(candidate)
            stale["registry_revision"] = self.registry["registry_revision"] + 2
            with self.assertRaisesRegex(ContinuityError, "QUEST_ADMISSION_REVISION_INVALID"):
                validate_quest_admission(self.registry, stale, self.board, root=root)

    def test_registry_parent_and_cutover_tampering_fails_closed(self) -> None:
        duplicate = copy.deepcopy(self.registry)
        duplicate["entries"][1]["parent_issue_number"] = duplicate["entries"][0]["parent_issue_number"]
        with self.assertRaisesRegex(ContinuityError, "QUEST_REGISTRY_DUPLICATE"):
            validate_quest_registry(duplicate, self.board)

        wrong_predecessor = copy.deepcopy(self.registry)
        wrong_predecessor["cutover"]["predecessor_sha256"] = "0" * 64
        with self.assertRaisesRegex(ContinuityError, "QUEST_PREDECESSOR_DIGEST_MISMATCH"):
            validate_quest_registry(wrong_predecessor, self.board)

        missing = copy.deepcopy(self.registry)
        missing["entries"].pop()
        with self.assertRaises(ContinuityError):
            validate_quest_registry(missing, self.board)

    def test_register_rejects_registry_digest_and_coverage_drift(self) -> None:
        wrong_digest = copy.deepcopy(self.register)
        wrong_digest["quest_registry_sha256"] = "0" * 64
        with self.assertRaisesRegex(ContinuityError, "QUEST_REGISTRY_DIGEST_MISMATCH"):
            validate_register(wrong_digest, self.board, registry=self.registry)

        missing = copy.deepcopy(self.register)
        missing["entries"].pop()
        with self.assertRaisesRegex(ContinuityError, "CONTINUITY_REGISTRY_COVERAGE_MISMATCH"):
            validate_register(missing, self.board, registry=self.registry)

        wrong_state = copy.deepcopy(self.register)
        wrong_state["entries"][0]["quest_state"] = "BLOCKED"
        with self.assertRaisesRegex(ContinuityError, "CONTINUITY_REGISTRY_BINDING_MISMATCH"):
            validate_register(wrong_state, self.board, registry=self.registry)

    def test_duplicate_or_unsafe_source_paths_fail_closed(self) -> None:
        duplicate = copy.deepcopy(self.board)
        duplicate["entries"].append(copy.deepcopy(self.board["entries"][1]))
        with self.assertRaisesRegex(ContinuityError, "QUEST_BOARD_DUPLICATE"):
            validate_board(duplicate)
        unsafe = copy.deepcopy(self.board)
        unsafe["entries"][1]["source"] = "quests/../outside.md"
        with self.assertRaises(ContinuityError):
            validate_board(unsafe)

    def test_one_entry_plan_is_stale_bound_and_non_mutating(self) -> None:
        before = copy.deepcopy(self.register)
        target = next(
            entry
            for entry in self.register["entries"]
            if entry["continuity_id"] == "CONT-PROMETHEUS-FIRE-R01"
        )
        candidate = plan_one_entry_update(
            self.register,
            self.board,
            self.identities,
            continuity_id=target["continuity_id"],
            expected_register_sha256=sha256(self.register),
            expected_entry_revision=target["revision"],
            event_id="PF-C01-TEST-PREVIEW-R01",
            changes={"next_action": "Run the bounded continuity update proof."},
        )
        self.assertEqual(self.register, before)
        self.assertEqual(candidate["register_revision"], before["register_revision"] + 1)
        changed = [
            after["continuity_id"]
            for prior, after in zip(before["entries"], candidate["entries"])
            if prior != after
        ]
        self.assertEqual(changed, [target["continuity_id"]])

        with self.assertRaisesRegex(ContinuityError, "REGISTER_STALE"):
            plan_one_entry_update(
                self.register,
                self.board,
                self.identities,
                continuity_id=target["continuity_id"],
                expected_register_sha256="0" * 64,
                expected_entry_revision=target["revision"],
                event_id="PF-C01-STALE-R01",
                changes={"next_action": "Rejected"},
            )
        with self.assertRaisesRegex(ContinuityError, "UPDATE_SCOPE_INVALID"):
            plan_one_entry_update(
                self.register,
                self.board,
                self.identities,
                continuity_id=target["continuity_id"],
                expected_register_sha256=sha256(self.register),
                expected_entry_revision=target["revision"],
                event_id="PF-C01-WIDEN-R01",
                changes={"quest_source": "quests/other.md"},
            )

    def test_completed_quests_have_no_active_continuity_target(self) -> None:
        for continuity_id in (
            "CONT-REPAIRING-PRIME-R01",
            "CONT-FOUND-SILVERLIGHT-R01",
            "CONT-PRIME-CONTINUITY-PROOF-R01",
        ):
            with self.subTest(continuity_id=continuity_id):
                with self.assertRaisesRegex(ContinuityError, "ENTRY_STALE_OR_MISSING"):
                    plan_one_entry_update(
                        self.register,
                        self.board,
                        self.identities,
                        continuity_id=continuity_id,
                        expected_register_sha256=sha256(self.register),
                        expected_entry_revision=1,
                        event_id=f"{continuity_id}-REJECTED-R01",
                        changes={"next_action": "Rejected"},
                    )

    def test_emberline_sunset_sunrise_and_argus_are_deterministic(self) -> None:
        self.assertEqual(render_emberline(self.register), render_emberline(copy.deepcopy(self.register)))
        continuity_id = "CONT-PROMETHEUS-FIRE-R01"
        snapshot = sunset(self.register, continuity_id)
        reconstructed = sunrise(snapshot, self.register)
        expected = next(
            entry for entry in self.register["entries"] if entry["continuity_id"] == continuity_id
        )
        self.assertEqual(reconstructed["next_gate"], expected["gate_id"])
        self.assertEqual(reconstructed["source"], expected["quest_source"])
        tampered = copy.deepcopy(snapshot)
        tampered["entry"]["next_action"] = "tampered"
        with self.assertRaisesRegex(ContinuityError, "SUNSET_DIGEST_MISMATCH"):
            sunrise(tampered, self.register)
        self.assertEqual(argus(self.register), argus(copy.deepcopy(self.register)))
        self.assertEqual(argus(self.register)[0]["continuity_id"], "CONT-PROMETHEUS-FIRE-R01")

    def test_cli_validate_and_output_no_clobber(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(continuity_cli(["validate"]), 0)
        receipt = json.loads(output.getvalue())
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["registry_id"], "MISSION-BOARD-QUEST-REGISTRY-R01")
        self.assertEqual(receipt["frozen_predecessor"], "FROZEN_PREDECESSOR_EVIDENCE")

        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "argus.json"
            self.assertEqual(continuity_cli(["argus", "--output", str(target)]), 0)
            self.assertTrue(target.is_file())
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                continuity_cli(["argus", "--output", str(target)])


if __name__ == "__main__":
    unittest.main()
