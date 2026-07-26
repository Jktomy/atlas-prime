from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTUM_SOURCE = ROOT / "quests" / "notums-watch.md"
QUEST_REGISTRY = ROOT / "continuity" / "mission-board-quest-registry-r01.json"
CONTINUITY = ROOT / "continuity" / "prime-continuity-register-r01.json"
COMMAND_SURFACES = ROOT / "routing" / "command-surfaces.md"
README = ROOT / "README.md"
START_HERE = ROOT / "atlas-start-here.md"
FROZEN_QUEST_BOARD = ROOT / "quest-board" / "quest-board-v1.json"
GENERATED_CHECKPOINT_README = ROOT / "tools" / "generated_checkpoint" / "README.md"


def _declared_route_paths(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("Notum source must begin with YAML front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError("Notum source front matter is not closed") from exc

    paths: list[str] = []
    active_key: str | None = None
    for line in lines[1:end]:
        if line in {"routes_from:", "routes_to:"}:
            active_key = line[:-1]
            continue
        if active_key and line.startswith("  - "):
            paths.append(line[4:])
            continue
        if line and not line.startswith(" "):
            active_key = None
    return paths


def _minimum_readback_paths(text: str) -> list[str]:
    try:
        section = text.split("Minimum readback route:", 1)[1].split("Use evidence labels:", 1)[0]
    except IndexError as exc:
        raise AssertionError("Notum source must retain a bounded minimum readback route") from exc
    return re.findall(r"`([^`]+)`", section)


class RefractSourceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notum_text = NOTUM_SOURCE.read_text(encoding="utf-8")
        cls.registry = json.loads(QUEST_REGISTRY.read_text(encoding="utf-8"))
        cls.continuity = json.loads(CONTINUITY.read_text(encoding="utf-8"))
        cls.command_surfaces = COMMAND_SURFACES.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")
        cls.start_here = START_HERE.read_text(encoding="utf-8")

    def test_notum_identity_matches_active_registry_and_continuity(self) -> None:
        match = re.search(r"^\*\*Quest ID:\*\* `([^`]+)`$", self.notum_text, re.MULTILINE)
        self.assertIsNotNone(match)
        source_id = match.group(1)

        registry_entry = next(
            entry for entry in self.registry["entries"]
            if entry["source"] == "quests/notums-watch.md"
        )
        continuity_entry = next(
            entry for entry in self.continuity["entries"]
            if entry["quest_source"] == "quests/notums-watch.md"
        )

        self.assertEqual(source_id, "QUEST-NOTUMS-WATCH-20260708")
        self.assertEqual(source_id, registry_entry["quest_id"])
        self.assertEqual(source_id, continuity_entry["quest_id"])

    def test_notum_active_routes_and_required_readback_paths_resolve(self) -> None:
        declared = _declared_route_paths(self.notum_text)
        readback = _minimum_readback_paths(self.notum_text)

        self.assertNotIn("atlas-index.md", declared + readback)
        self.assertNotIn("noctua.md", declared + readback)
        self.assertNotIn("quest-board/quest-board-v1.json", declared)
        self.assertIn("governance/noctua.md", declared)
        self.assertIn("routing/command-surfaces.md", declared)
        self.assertIn("routing/command-surfaces.md", readback)

        for relative_path in declared + readback:
            self.assertTrue(
                (ROOT / relative_path).is_file(),
                f"active Notum route does not resolve: {relative_path}",
            )

    def test_continuity_hash_binds_exact_notum_source_bytes(self) -> None:
        import hashlib

        continuity_entry = next(
            entry for entry in self.continuity["entries"]
            if entry["quest_id"] == "QUEST-NOTUMS-WATCH-20260708"
        )
        actual = hashlib.sha256(NOTUM_SOURCE.read_bytes()).hexdigest()
        self.assertEqual(continuity_entry["quest_source_sha256"], actual)

    def test_generated_checkpoint_surface_is_diagnostic_not_hosted(self) -> None:
        self.assertNotIn(
            ".github/workflows/generated-checkpoint-publisher.yml",
            self.command_surfaces,
        )
        self.assertIn(
            "python -B tools/build_index.py --diagnostics",
            self.command_surfaces,
        )
        self.assertIn(
            "no active hosted generated-checkpoint publisher exists",
            self.command_surfaces,
        )

        retained = GENERATED_CHECKPOINT_README.read_text(encoding="utf-8")
        self.assertIn("dormant compatibility source", retained)
        self.assertIn("There is no active hosted publisher workflow.", retained)

    def test_startup_surfaces_agree_on_repository_entry_sequence(self) -> None:
        self.assertIn(
            "This README is the repository entrypoint. Continue with `bootstrap.md`, then\n"
            "`atlas-start-here.md`, then `routing/command-surfaces.md`.",
            self.readme,
        )
        self.assertIn(
            "Start with `README.md`, then `bootstrap.md`, then `atlas-start-here.md`, "
            "then this surface.",
            self.command_surfaces,
        )

        ordered = [
            self.start_here.index("1. `README.md`"),
            self.start_here.index("2. `bootstrap.md`"),
            self.start_here.index("3. `routing/command-surfaces.md`"),
        ]
        self.assertEqual(ordered, sorted(ordered))

    def test_frozen_predecessor_is_not_promoted_to_active_authority(self) -> None:
        frozen = json.loads(FROZEN_QUEST_BOARD.read_text(encoding="utf-8"))
        self.assertEqual(frozen["state"], "FROZEN_PREDECESSOR_EVIDENCE")
        self.assertNotIn("quest-board/quest-board-v1.json", _declared_route_paths(self.notum_text))


if __name__ == "__main__":
    unittest.main()
