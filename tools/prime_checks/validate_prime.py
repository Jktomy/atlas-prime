from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED = (
    "README.md",
    "atlas-prime.md",
    "bootstrap.md",
    "governance/source-hierarchy.md",
    "governance/source-lifecycle.md",
    "safety/atlas-safety-doctrine.md",
    "routing/command-surfaces.md",
    "projects/project-registry.md",
    "operations/operation-registry.md",
    "operations/artemis-runtime-and-routing.md",
    "operations/protocol-library.md",
    "infrastructure/atlas-infrastructure-source.md",
    "recovery/phoenix-recovery.md",
    "knowledge/atlas-source-compendium.md",
    "quests/prime-reborn.md",
    "quests/prometheus-fire.md",
    "quests/notums-watch.md",
    "quest-board/quest-board-v1.json",
    "migration/source-disposition-ledger.csv",
    "migration/source-disposition-summary.json",
    "tools/thread-engine/PRIME-PORT-STATUS.json",
    "tools/atlas-sword/engine/oathbringer_contract.py",
    "tools/build_index.py",
)
DISPOSITIONS = {"KEEP", "MERGE", "REMODEL", "REGENERATE", "ARCHIVE", "EXCLUDE"}
SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\s*[:=]\s*[^\s`'\"<>{}]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"missing Prime program paths: {missing}")

    summary = json.loads((ROOT / "migration/source-disposition-summary.json").read_text(encoding="utf-8"))
    with (ROOT / "migration/source-disposition-ledger.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 525 or len({row["source_path"] for row in rows}) != 525:
        raise SystemExit("disposition ledger does not close 525 unique Codex paths")
    if any(row["disposition"] not in DISPOSITIONS for row in rows):
        raise SystemExit("disposition ledger contains an invalid disposition")
    if summary["tracked_paths"] != 525 or summary["closed_paths"] != 525 or summary["open_paths"] != 0:
        raise SystemExit("disposition summary is not closed")

    board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
    if board["canonical_repository"] != "Jktomy/atlas-prime" or board["predecessor_workboard_route"] != "ABSENT":
        raise SystemExit("Quest Board is not Prime-native")
    if {entry["source"] for entry in board["entries"]} != {
        "quests/prime-reborn.md",
        "quests/prometheus-fire.md",
        "quests/notums-watch.md",
    }:
        raise SystemExit("Quest Board source set is incomplete")

    port = json.loads((ROOT / "tools/thread-engine/PRIME-PORT-STATUS.json").read_text(encoding="utf-8"))
    if port["implementation_state"] != "THREAD_ENGINE_ACTIVE_MISSION_SCOPED":
        raise SystemExit("Prime Thread Engine is not active mission-scoped")
    if port["standing_authority"] or port["automatic_merge"] or port["direct_main"]:
        raise SystemExit("Prime Thread Engine permanent invariants are violated")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.parts[-1].endswith((".pyc", ".pyo")):
            continue
        if "__pycache__" in path.parts:
            raise SystemExit(f"runtime byproduct found: {path.relative_to(ROOT)}")
        if path.suffix.lower() in {".md", ".json", ".yml", ".yaml", ".csv"}:
            text = path.read_text(encoding="utf-8")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    raise SystemExit(f"high-confidence secret pattern found: {path.relative_to(ROOT)}")

    print("Prime whole-program source validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
