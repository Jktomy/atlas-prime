from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

required = [
    "README.md",
    "bootstrap.md",
    "atlas-prime.md",
    "atlas-start-here.md",
    "quests/prime-reborn.md",
    "governance/source-hierarchy.md",
    "governance/protected-source-boundary.md",
    "governance/change-routes.md",
    "governance/cutover-boundary.md",
    "migration/predecessor-snapshot.md",
    "migration/codex-inheritance-manifest.md",
    "migration/rollback-map.md",
    "policies/repository-policy.json",
    "policies/protected-paths.json",
    "policies/operator-policy.json",
    "tools/thread-engine/PRIME-PORT-STATUS.json",
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    raise SystemExit(f"Missing required Prime kernel paths: {missing}")

repo_policy = json.loads((ROOT / "policies/repository-policy.json").read_text(encoding="utf-8"))
assert repo_policy["repository"] == "Jktomy/atlas-prime"
assert repo_policy["state"] == "SHADOW_CONSTRUCTION"
assert repo_policy["direct_main_allowed"] is False
assert repo_policy["force_push_allowed"] is False
assert repo_policy["automatic_merge_allowed"] is False
assert repo_policy["standing_writer_allowed"] is False

port = json.loads((ROOT / "tools/thread-engine/PRIME-PORT-STATUS.json").read_text(encoding="utf-8"))
assert port["implementation_state"] == "PORT_CANDIDATE_DISABLED"
assert port["production_execution_authorized"] is False
assert port["proof_required"] is True

if (ROOT / "generated").exists():
    raise SystemExit("The Prime bootstrap kernel must not include generated output.")

for path in ROOT.rglob("*"):
    if path.is_file() and (path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts):
        raise SystemExit(f"Runtime byproduct found: {path.relative_to(ROOT)}")

print("Prime kernel static checks: PASS")
