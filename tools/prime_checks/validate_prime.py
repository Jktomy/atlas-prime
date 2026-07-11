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
    "governance/capability-parity-register.json",
    "governance/capability-acceptance-contract.md",
    "safety/atlas-safety-doctrine.md",
    "routing/command-surfaces.md",
    "projects/project-registry.md",
    "operations/operation-registry.md",
    "operations/artemis-runtime-and-routing.md",
    "operations/protocol-library.md",
    "methods/phoenix-blade.md",
    "infrastructure/atlas-infrastructure-source.md",
    "recovery/phoenix-recovery.md",
    "knowledge/atlas-source-compendium.md",
    "lifecycle/README.md",
    "lifecycle/architecture-decision-r01.md",
    "lifecycle/lifecycle-contract.md",
    "lifecycle/trust-roots/README.md",
    "lifecycle/schemas/common-v1.schema.json",
    "lifecycle/schemas/feather-v1.schema.json",
    "lifecycle/schemas/feather-archive-v1.schema.json",
    "lifecycle/schemas/golden-wing-v1.schema.json",
    "lifecycle/schemas/quest-emberline-v1.schema.json",
    "lifecycle/schemas/quest-checkpoint-v1.schema.json",
    "lifecycle/schemas/sunset-v1.schema.json",
    "lifecycle/schemas/sunrise-v1.schema.json",
    "lifecycle/schemas/continuity-v1.schema.json",
    "lifecycle/schemas/lifecycle-receipt-v1.schema.json",
    "lifecycle/schemas/website-index-v1.schema.json",
    "lifecycle/schemas/website-index-v2.schema.json",
    "tools/atlas_lifecycle/README.md",
    "tools/atlas_lifecycle/__main__.py",
    "tools/atlas_lifecycle/evidence.py",
    "tools/atlas_lifecycle/jsonio.py",
    "tools/atlas_lifecycle/repository.py",
    "tools/atlas_lifecycle/schema.py",
    "tools/atlas_lifecycle/projection.py",
    "tools/atlas_lifecycle/pilot.py",
    "proof/lifecycle/g3-d-beu-reduction-pilot-r01.json",
    "proof/lifecycle/g3-d-beu-reduction-pilot-r01.md",
    "quests/prime-reborn.md",
    "quests/prometheus-fire.md",
    "quests/notums-watch.md",
    "quests/found-silverlight.md",
    "quest-board/quest-board-v1.json",
    "migration/source-disposition-ledger.csv",
    "migration/source-disposition-summary.json",
    "schemas/capability-parity-register.schema.json",
    "tools/thread-engine/PRIME-PORT-STATUS.json",
    "tools/atlas-sword/engine/oathbringer_contract.py",
    "tools/oathbringer-foundry/foundry.py",
    "tools/oathbringer-foundry/cli.py",
    "tools/oathbringer-foundry/schema/foundry-mission-v1.schema.json",
    "methods/oathbringer-foundry.md",
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
    if summary["schema_version"] != "atlas-prime-source-disposition-summary-v2":
        raise SystemExit("disposition summary schema is not final")
    if summary["tracked_paths"] != 525 or summary["closed_paths"] != 525 or summary["open_paths"] != 0:
        raise SystemExit("disposition summary is not closed")
    final_statuses = {
        "MIGRATED",
        "MERGED_INTO_DESTINATION",
        "REMODELED_IN_PRIME",
        "REGENERATED_IN_PRIME",
        "ARCHIVED_IN_CODEX",
        "EXCLUDED_WITH_PROOF",
    }
    if {row["final_status"] for row in rows} != final_statuses:
        raise SystemExit("disposition ledger terminal status set is incomplete")
    for field in (
        "source_blob_sha1",
        "source_class",
        "current_authority",
        "prime_target",
        "migration_pr_or_ref",
        "migration_commit",
        "verification",
        "privacy_classification",
        "final_status",
    ):
        if any(not row[field].strip() for row in rows):
            raise SystemExit(f"disposition ledger has blank final field: {field}")

    board = json.loads((ROOT / "quest-board/quest-board-v1.json").read_text(encoding="utf-8"))
    if board["canonical_repository"] != "Jktomy/atlas-prime" or board["predecessor_workboard_route"] != "HISTORICAL_ONLY":
        raise SystemExit("Quest Board is not Prime-native")
    if board["state"] != "CANONICAL_ACTIVE":
        raise SystemExit("Quest Board is not canonical active")
    if {entry["source"] for entry in board["entries"]} != {
        "quests/prime-reborn.md",
        "quests/prometheus-fire.md",
        "quests/notums-watch.md",
        "quests/found-silverlight.md",
    }:
        raise SystemExit("Quest Board source set is incomplete")

    port = json.loads((ROOT / "tools/thread-engine/PRIME-PORT-STATUS.json").read_text(encoding="utf-8"))
    if port["implementation_state"] != "THREAD_ENGINE_ACTIVE_MISSION_SCOPED":
        raise SystemExit("Prime Thread Engine is not active mission-scoped")
    if port["standing_authority"] or port["automatic_merge"] or port["direct_main"]:
        raise SystemExit("Prime Thread Engine permanent invariants are violated")
    if port["canonical_repository"] != "Jktomy/atlas-prime" or port["harmless_pilot_state"] != "PROVEN_MERGED" or port["spear_arrow_bow_state"] != "PROVEN_MERGED":
        raise SystemExit("Prime Thread Engine proof status is incomplete")

    repository = json.loads((ROOT / "policies/repository-policy.json").read_text(encoding="utf-8"))
    if repository["state"] != "CANONICAL_ACTIVE" or repository["canonical_repository"] != "Jktomy/atlas-prime":
        raise SystemExit("Prime repository policy is not canonical active")
    if repository["predecessor_role"] != "FROZEN_PREDECESSOR_ROLLBACK_EVIDENCE":
        raise SystemExit("Codex predecessor role is not final")

    capability_register = json.loads(
        (ROOT / "governance/capability-parity-register.json").read_text(encoding="utf-8")
    )
    capability_schema = json.loads(
        (ROOT / "schemas/capability-parity-register.schema.json").read_text(encoding="utf-8")
    )
    capabilities = capability_register.get("capabilities", [])
    allowed_dispositions = {
        "PRESERVED",
        "IMPROVED",
        "RESTORED",
        "REPLACED",
        "INTENTIONALLY_RETIRED",
        "BLOCKED",
        "STILL_MISSING",
    }
    if capability_register.get("schema_version") != "atlas-prime-capability-parity-register-v1":
        raise SystemExit("capability parity register schema identity is invalid")
    if capability_register.get("register_role") != "CANONICAL_CAPABILITY_DISPOSITION":
        raise SystemExit("capability parity register role is invalid")
    if (
        capability_register.get("predecessor_head")
        != "c892dc05ea56db0134a0e865f56d491f9c02ff85"
    ):
        raise SystemExit("capability parity predecessor evidence lock is invalid")
    if len(capabilities) != 28 or [item.get("id") for item in capabilities] != [
        f"CAP-{number:03d}" for number in range(1, 29)
    ]:
        raise SystemExit(
            "capability parity register does not contain the exact 28-record identity set"
        )
    if len({item.get("capability") for item in capabilities}) != 28:
        raise SystemExit("capability parity register contains duplicate capability names")
    if (
        set(capability_register.get("capability_disposition_vocabulary", []))
        != allowed_dispositions
    ):
        raise SystemExit("capability parity disposition vocabulary is invalid")
    observed_counts = {
        value: sum(
            item.get("capability_disposition") == value for item in capabilities
        )
        for value in allowed_dispositions
    }
    if observed_counts != capability_register.get("capability_disposition_counts"):
        raise SystemExit("capability parity disposition counts do not match the records")
    path_authority = capability_register.get("path_disposition_authority", {})
    if (
        path_authority.get("tracked_paths"),
        path_authority.get("closed_paths"),
        path_authority.get("open_paths"),
    ) != (525, 525, 0):
        raise SystemExit("path disposition evidence is not preserved exactly")
    schema_enum = set(
        capability_schema["properties"]["capabilities"]["items"]["properties"][
            "capability_disposition"
        ]["enum"]
    )
    if schema_enum != allowed_dispositions:
        raise SystemExit("capability schema and register disposition vocabularies differ")

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
