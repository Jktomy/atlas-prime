from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

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
    validate_register,
)


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class PrimeContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.board = load("quest-board/quest-board-v1.json")
        self.register = load("continuity/prime-continuity-register-r01.json")
        self.identities = load("continuity/quest-engine-identities-r01.json")

    def test_canonical_board_register_and_identities_validate(self) -> None:
        validate_board(self.board)
        validate_register(self.register, self.board)
        validate_identity_register(self.identities)
        self.assertEqual(len(self.identities["campaigns"]), 8)
        self.assertEqual(
            {entry["quest_id"] for entry in self.register["entries"]},
            {entry["quest_id"] for entry in self.board["entries"] if entry["state"] != "COMPLETE"},
        )

    def test_schema_driven_board_accepts_later_quest_without_validator_edit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for entry in self.board["entries"]:
                existing = root / entry["source"]
                existing.parent.mkdir(parents=True, exist_ok=True)
                existing.write_text(f"# {entry['quest_id']}\n", encoding="utf-8")
            source = root / "quests" / "later-valid-quest.md"
            source.write_text("# Later valid Quest\n", encoding="utf-8")
            candidate = copy.deepcopy(self.board)
            candidate["entries"].append({
                "next_gate": "LQ-C01 Preview",
                "owner": "Atlas / Source Governance",
                "quest_id": "QUEST-LATER-VALID-R01",
                "source": "quests/later-valid-quest.md",
                "state": "READY_FOR_CAMPAIGN_1_PREVIEW",
            })
            validate_board(candidate, root=root)

    def test_duplicate_or_unsafe_quest_admission_fails_closed(self) -> None:
        duplicate = copy.deepcopy(self.board)
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][1]))
        with self.assertRaisesRegex(ContinuityError, "QUEST_BOARD_DUPLICATE"):
            validate_board(duplicate)
        unsafe = copy.deepcopy(self.board)
        unsafe["entries"][1]["source"] = "quests/../outside.md"
        with self.assertRaises(ContinuityError):
            validate_board(unsafe)

    def test_one_entry_plan_is_stale_bound_and_non_mutating(self) -> None:
        before = copy.deepcopy(self.register)
        candidate = plan_one_entry_update(
            self.register,
            continuity_id="CONT-REPAIRING-PRIME-R01",
            expected_register_sha256=sha256(self.register),
            expected_entry_revision=1,
            event_id="RP-C05-AJ07-PREVIEW-R01",
            changes={"next_action": "Run the bounded AJ-07 continuity update proof."},
        )
        self.assertEqual(self.register, before)
        self.assertEqual(candidate["register_revision"], before["register_revision"] + 1)
        changed = [
            after["continuity_id"]
            for prior, after in zip(before["entries"], candidate["entries"])
            if prior != after
        ]
        self.assertEqual(changed, ["CONT-REPAIRING-PRIME-R01"])
        with self.assertRaisesRegex(ContinuityError, "REGISTER_STALE"):
            plan_one_entry_update(
                self.register,
                continuity_id="CONT-REPAIRING-PRIME-R01",
                expected_register_sha256="0" * 64,
                expected_entry_revision=1,
                event_id="RP-C05-STALE-R01",
                changes={"next_action": "Rejected"},
            )
        with self.assertRaisesRegex(ContinuityError, "UPDATE_SCOPE_INVALID"):
            plan_one_entry_update(
                self.register,
                continuity_id="CONT-REPAIRING-PRIME-R01",
                expected_register_sha256=sha256(self.register),
                expected_entry_revision=1,
                event_id="RP-C05-WIDEN-R01",
                changes={"quest_source": "quests/other.md"},
            )

    def test_emberline_sunset_sunrise_and_argus_are_deterministic(self) -> None:
        self.assertEqual(render_emberline(self.register), render_emberline(copy.deepcopy(self.register)))
        snapshot = sunset(self.register, "CONT-REPAIRING-PRIME-R01")
        reconstructed = sunrise(snapshot)
        self.assertEqual(reconstructed["next_gate"], "QUEST_ENGINE_AND_CONTINUITY_PROVEN")
        self.assertEqual(reconstructed["source"], "quests/repairing-prime.md")
        tampered = copy.deepcopy(snapshot)
        tampered["entry"]["next_action"] = "tampered"
        with self.assertRaisesRegex(ContinuityError, "SUNSET_DIGEST_MISMATCH"):
            sunrise(tampered)
        self.assertEqual(argus(self.register), argus(copy.deepcopy(self.register)))
        self.assertEqual(
            [item["continuity_id"] for item in argus(self.register)],
            sorted(
                [entry["continuity_id"] for entry in self.register["entries"]],
                key=lambda identity: (
                    -len(next(entry["blockers"] for entry in self.register["entries"] if entry["continuity_id"] == identity)),
                    identity,
                ),
            ),
        )

    def test_register_rejects_digest_coverage_and_source_drift(self) -> None:
        wrong_board = copy.deepcopy(self.register)
        wrong_board["quest_board_sha256"] = "0" * 64
        with self.assertRaisesRegex(ContinuityError, "QUEST_BOARD_DIGEST_MISMATCH"):
            validate_register(wrong_board, self.board)
        missing = copy.deepcopy(self.register)
        missing["entries"].pop()
        with self.assertRaisesRegex(ContinuityError, "CONTINUITY_BOARD_COVERAGE_MISMATCH"):
            validate_register(missing, self.board)
        drifted = copy.deepcopy(self.register)
        drifted["entries"][0]["quest_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ContinuityError, "CONTINUITY_SOURCE_DIGEST_MISMATCH"):
            validate_register(drifted, self.board)


if __name__ == "__main__":
    unittest.main()
