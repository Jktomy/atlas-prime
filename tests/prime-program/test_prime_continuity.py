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
    validate_register,
)


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_FIXTURE = "CONT-FOUND-SILVERLIGHT-R01"


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

        repairing_board = next(
            entry for entry in self.board["entries"]
            if entry["quest_id"] == self.identities["quest_id"]
        )
        self.assertEqual(repairing_board["state"], "COMPLETE")
        self.assertEqual(repairing_board["next_gate"], "CLOSED")
        self.assertIn("RP-C01 through RP-C08 are COMPLETE", repairing_board["completion_basis"])
        self.assertFalse(
            any(entry["quest_id"] == self.identities["quest_id"] for entry in self.register["entries"])
        )
        self.assertEqual(self.register["register_revision"], 32)
        self.assertEqual(
            self.register["source_base_sha"],
            "40e58dcf33bae68f8c819c2f65c6474f52381718",
        )
        self.assertEqual(
            self.register["event_ids"][-1],
            "RP-C08-FINAL-REPAIRING-PRIME-COMPLETION-R01",
        )

        rp_c06 = next(
            campaign for campaign in self.identities["campaigns"]
            if campaign["campaign_id"] == "RP-C06"
        )
        rp_c07 = next(
            campaign for campaign in self.identities["campaigns"]
            if campaign["campaign_id"] == "RP-C07"
        )
        rp_c08 = next(
            campaign for campaign in self.identities["campaigns"]
            if campaign["campaign_id"] == "RP-C08"
        )
        self.assertEqual(rp_c06["state"], "COMPLETE")
        self.assertEqual(rp_c07["state"], "COMPLETE")
        self.assertEqual(rp_c08["state"], "COMPLETE")
        self.assertEqual(
            [mission["mission_id"] for mission in rp_c06["missions"]],
            [f"RP-C06-M{index:02d}" for index in range(1, 8)],
        )
        self.assertTrue(all(mission["state"] == "PROVEN" for mission in rp_c06["missions"]))

        found_board = next(
            entry for entry in self.board["entries"]
            if entry["quest_id"] == "QUEST-FOUND-SILVERLIGHT-R01"
        )
        found_continuity = next(
            entry for entry in self.register["entries"]
            if entry["continuity_id"] == ACTIVE_FIXTURE
        )
        self.assertEqual(found_board["state"], "IN_PROGRESS")
        self.assertEqual(found_board["next_gate"], "FS-C01-M04 — Prove the Light")
        self.assertEqual(found_continuity["campaign_id"], "FS-C01")
        self.assertEqual(found_continuity["mission_id"], "FS-C01-M04")
        self.assertEqual(
            found_continuity["gate_id"],
            "INVESTITURE_ACCOUNTING_LIVE_ACCEPTANCE_PROVEN",
        )
        self.assertEqual(found_continuity["revision"], 4)
        self.assertEqual(
            found_continuity["last_event_id"],
            "FS-C03-HERMES-BRIDGE-NAMING-R01",
        )

        prometheus_board = next(
            entry for entry in self.board["entries"]
            if entry["quest_id"] == "QUEST-PROMETHEUS-FIRE-20260701"
        )
        prometheus_continuity = next(
            entry for entry in self.register["entries"]
            if entry["continuity_id"] == "CONT-PROMETHEUS-FIRE-R01"
        )
        self.assertEqual(prometheus_board["state"], "IN_PROGRESS")
        self.assertEqual(
            prometheus_board["next_gate"],
            "PF-C01-M02 Preview — Preserve the Old Flame",
        )
        self.assertEqual(prometheus_continuity["quest_state"], "IN_PROGRESS")
        self.assertEqual(prometheus_continuity["campaign_id"], "PF-C01")
        self.assertEqual(prometheus_continuity["mission_id"], "PF-C01-M02")
        self.assertEqual(prometheus_continuity["gate_id"], "PF-C01-M02-PREVIEW")

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
            admitted = validate_quest_admission(self.board, candidate, root=root)
            self.assertEqual(admitted["quest_id"], "QUEST-LATER-VALID-R01")

            self_completed = copy.deepcopy(candidate)
            self_completed["entries"][-1].update({
                "state": "COMPLETE",
                "next_gate": "CLOSED",
                "completion_basis": "self asserted",
            })
            with self.assertRaisesRegex(ContinuityError, "QUEST_ADMISSION_STATE_INVALID"):
                validate_quest_admission(self.board, self_completed, root=root)

    def test_duplicate_or_unsafe_quest_admission_fails_closed(self) -> None:
        duplicate = copy.deepcopy(self.board)
        duplicate["entries"].append(copy.deepcopy(self.board["entries"][1]))
        with self.assertRaisesRegex(ContinuityError, "QUEST_BOARD_DUPLICATE"):
            validate_board(duplicate)
        unsafe = copy.deepcopy(self.board)
        unsafe["entries"][2]["source"] = "quests/../outside.md"
        with self.assertRaises(ContinuityError):
            validate_board(unsafe)

    def test_one_entry_plan_is_stale_bound_and_non_mutating(self) -> None:
        before = copy.deepcopy(self.register)
        entry_revision = next(
            entry["revision"]
            for entry in self.register["entries"]
            if entry["continuity_id"] == ACTIVE_FIXTURE
        )
        candidate = plan_one_entry_update(
            self.register,
            self.board,
            self.identities,
            continuity_id=ACTIVE_FIXTURE,
            expected_register_sha256=sha256(self.register),
            expected_entry_revision=entry_revision,
            event_id="FS-C01-M04-PREVIEW-R02",
            changes={"next_action": "Run the bounded FS-C01-M04 continuity update proof."},
        )
        self.assertEqual(self.register, before)
        self.assertEqual(candidate["register_revision"], before["register_revision"] + 1)
        changed = [
            after["continuity_id"]
            for prior, after in zip(before["entries"], candidate["entries"])
            if prior != after
        ]
        self.assertEqual(changed, [ACTIVE_FIXTURE])

        with self.assertRaisesRegex(ContinuityError, "REGISTER_STALE"):
            plan_one_entry_update(
                self.register,
                self.board,
                self.identities,
                continuity_id=ACTIVE_FIXTURE,
                expected_register_sha256="0" * 64,
                expected_entry_revision=entry_revision,
                event_id="FS-C01-M04-STALE-R01",
                changes={"next_action": "Rejected"},
            )
        with self.assertRaisesRegex(ContinuityError, "UPDATE_SCOPE_INVALID"):
            plan_one_entry_update(
                self.register,
                self.board,
                self.identities,
                continuity_id=ACTIVE_FIXTURE,
                expected_register_sha256=sha256(self.register),
                expected_entry_revision=entry_revision,
                event_id="FS-C01-M04-WIDEN-R01",
                changes={"quest_source": "quests/other.md"},
            )
        replay = copy.deepcopy(self.register)
        replay["event_ids"].append("FS-C01-M04-REPLAY-R01")
        with self.assertRaisesRegex(ContinuityError, "EVENT_REPLAY"):
            plan_one_entry_update(
                replay,
                self.board,
                self.identities,
                continuity_id=ACTIVE_FIXTURE,
                expected_register_sha256=sha256(replay),
                expected_entry_revision=entry_revision,
                event_id="FS-C01-M04-REPLAY-R01",
                changes={"next_action": "Rejected replay"},
            )

    def test_emberline_sunset_sunrise_and_argus_are_deterministic(self) -> None:
        self.assertEqual(render_emberline(self.register), render_emberline(copy.deepcopy(self.register)))
        snapshot = sunset(self.register, ACTIVE_FIXTURE)
        reconstructed = sunrise(snapshot, self.register)
        expected = next(
            entry for entry in self.register["entries"]
            if entry["continuity_id"] == ACTIVE_FIXTURE
        )
        self.assertEqual(reconstructed["next_gate"], expected["gate_id"])
        self.assertEqual(reconstructed["source"], expected["quest_source"])

        tampered = copy.deepcopy(snapshot)
        tampered["entry"]["next_action"] = "tampered"
        with self.assertRaisesRegex(ContinuityError, "SUNSET_DIGEST_MISMATCH"):
            sunrise(tampered, self.register)
        forged = copy.deepcopy(snapshot)
        forged["entry"]["gate_id"] = "ATTACKER_GATE"
        forged["sunset_sha256"] = sha256({
            key: forged[key] for key in ("schema_version", "register_sha256", "entry")
        })
        with self.assertRaisesRegex(ContinuityError, "SUNSET_ENTRY_MISMATCH"):
            sunrise(forged, self.register)

        self.assertEqual(
            [item["continuity_id"] for item in argus(self.register)],
            sorted(
                [entry["continuity_id"] for entry in self.register["entries"]],
                key=lambda identity: (
                    -len(next(
                        entry["blockers"] for entry in self.register["entries"]
                        if entry["continuity_id"] == identity
                    )),
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

    def test_identity_state_machine_rejects_self_promotion(self) -> None:
        invalid = copy.deepcopy(self.identities)
        invalid["campaigns"][0]["missions"][0]["state"] = "UNPROVEN"
        invalid["campaigns"][0]["state"] = "COMPLETE"
        with self.assertRaisesRegex(ContinuityError, "CAMPAIGN_COMPLETION_UNPROVEN"):
            validate_identity_register(invalid)
        transition = copy.deepcopy(self.identities)
        transition["state_rules"]["allowed_campaign_transitions"] = [
            "PENDING->IN_PROGRESS",
            "IN_PROGRESS->BLOCKED",
            "BLOCKED->IN_PROGRESS",
            "PENDING->COMPLETE",
        ]
        with self.assertRaises(ContinuityError):
            validate_identity_register(transition)
        mismatched = copy.deepcopy(self.identities)
        mismatched["campaigns"][0]["missions"][0]["mission_id"] = "RP-C02-M01"
        with self.assertRaisesRegex(ContinuityError, "MISSION_CAMPAIGN_MISMATCH"):
            validate_identity_register(mismatched)

    def test_command_surface_validates_and_anchors_restart(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(continuity_cli(["validate"]), 0)
        self.assertEqual(json.loads(output.getvalue())["result"], "PASS")

        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "sunset.json"
            sunrise_path = Path(temp) / "sunrise.json"
            self.assertEqual(
                continuity_cli([
                    "sunset",
                    "--continuity-id", ACTIVE_FIXTURE,
                    "--output", str(snapshot),
                ]),
                0,
            )
            self.assertEqual(
                continuity_cli([
                    "sunrise",
                    "--snapshot", str(snapshot),
                    "--output", str(sunrise_path),
                ]),
                0,
            )
            reconstructed = json.loads(sunrise_path.read_text(encoding="utf-8"))
            expected_gate = next(
                entry["gate_id"]
                for entry in self.register["entries"]
                if entry["continuity_id"] == ACTIVE_FIXTURE
            )
            self.assertEqual(reconstructed["next_gate"], expected_gate)

            candidate = Path(temp) / "candidate.json"
            entry_revision = next(
                entry["revision"]
                for entry in self.register["entries"]
                if entry["continuity_id"] == ACTIVE_FIXTURE
            )
            self.assertEqual(
                continuity_cli([
                    "plan-update",
                    "--continuity-id", ACTIVE_FIXTURE,
                    "--expected-register-sha256", sha256(self.register),
                    "--expected-entry-revision", str(entry_revision),
                    "--event-id", "FS-C01-M04-CLI-PREVIEW-R01",
                    "--changes-json", '{"next_action":"CLI preview only"}',
                    "--output", str(candidate),
                ]),
                0,
            )
            planned = json.loads(candidate.read_text(encoding="utf-8"))
            self.assertEqual(planned["register_revision"], self.register["register_revision"] + 1)

    def test_command_output_rejects_canonical_alias_and_clobber_paths(self) -> None:
        canonical_targets = (
            ROOT / "continuity" / "prime-continuity-register-r01.json",
            ROOT / "quest-board" / "quest-board-v1.json",
            ROOT / "continuity" / "quest-engine-identities-r01.json",
            ROOT / "generated" / ".." / "continuity" / "prime-continuity-register-r01.json",
        )
        for target in canonical_targets:
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, "OUTPUT_INSIDE_CANONICAL_REPOSITORY"):
                    continuity_cli(["emberline", "--output", str(target)])
        with tempfile.TemporaryDirectory() as temp:
            existing = Path(temp) / "existing.json"
            existing.write_text("preserve\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                continuity_cli(["argus", "--output", str(existing)])
            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve\n")


if __name__ == "__main__":
    unittest.main()
