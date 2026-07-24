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
    "governance/mission-control-interaction-contract.md",
    "migration/predecessor-snapshot.md",
    "migration/codex-inheritance-manifest.md",
    "migration/rollback-map.md",
    "policies/repository-policy.json",
    "policies/protected-paths.json",
    "policies/operator-policy.json",
    "tools/thread-engine/PRIME-PORT-STATUS.json",
    "tools/thread-engine/production_adapter/activation.py",
]

missing = [p for p in required if not (ROOT / p).is_file()]
if missing:
    raise SystemExit(f"Missing required Prime kernel paths: {missing}")

repo_policy = json.loads((ROOT / "policies/repository-policy.json").read_text(encoding="utf-8"))
assert repo_policy["repository"] == "Jktomy/atlas-prime"
assert repo_policy["state"] == "CANONICAL_ACTIVE"
assert repo_policy["canonical_repository"] == "Jktomy/atlas-prime"
assert repo_policy["predecessor_repository"] == "Jktomy/atlas-codex"
assert repo_policy["predecessor_role"] == "FROZEN_PREDECESSOR_ROLLBACK_EVIDENCE"
assert repo_policy["direct_main_allowed"] is False
assert repo_policy["force_push_allowed"] is False
assert repo_policy["automatic_merge_allowed"] is False
assert repo_policy["standing_writer_allowed"] is False

port = json.loads((ROOT / "tools/thread-engine/PRIME-PORT-STATUS.json").read_text(encoding="utf-8"))
assert port["implementation_state"] == "THREAD_ENGINE_ACTIVE_MISSION_SCOPED"
assert port["production_execution_authorized"] is True
assert port["proof_required"] is False
assert port["standing_authority"] is False
assert port["automatic_merge"] is False
assert port["direct_main"] is False
assert port["codex_workboard_route"] == "ABSENT"
assert port["protected_path_policy"] == "PRIME_NATIVE_JSON_ENFORCED"
assert port["activation_route"] == "AEGIS_BREAK_TO_OATHBRINGER"
assert port["canonical_repository"] == "Jktomy/atlas-prime"
assert port["harmless_pilot_state"] == "PROVEN_MERGED"
assert port["spear_arrow_bow_state"] == "PROVEN_MERGED"
assert port["next_gate"] == "NORMAL_PRIME_OPERATION"

protected = json.loads((ROOT / "policies/protected-paths.json").read_text(encoding="utf-8"))
for required_path in ("migration/**", "quest-board/**", "generated/**", "tools/thread-engine/**"):
    assert required_path in protected["critical_paths"]

rollback = (ROOT / "migration/rollback-map.md").read_text(encoding="utf-8")
command_surfaces = (ROOT / "routing/command-surfaces.md").read_text(encoding="utf-8")
start_here = (ROOT / "atlas-start-here.md").read_text(encoding="utf-8")
interaction = (ROOT / "governance/mission-control-interaction-contract.md").read_text(encoding="utf-8")

for required_fragment in (
    'status: "CANONICAL_ACTIVE"',
    "Prime remains the sole active canonical source after cutover.",
    "`Jktomy/atlas-codex` is frozen predecessor and rollback evidence only.",
    "It is never the normal rollback target and never regains active source authority.",
    "Restore the last independently verified Prime state through a new exact",
    "reviewed revert or restoration PR.",
    "Do not force-reset `main`. Do not restore Codex canonical authority.",
    "Keep Prime canonical.",
    "Thread Engine self-change or emergency",
    "disablement uses Aegis Break → Oathbringer",
    "Rollback is proven only after exact restoration and independent readback.",
):
    assert required_fragment in rollback

for forbidden_fragment in (
    'status: "SHADOW_CONSTRUCTION"',
    "Restore the exact predecessor tree",
    "Keep Codex canonical",
    "Return source authority",
):
    assert forbidden_fragment not in rollback

assert (
    "| Clean-clone recovery, protected runtime restoration, and recovery proof | `recovery/elantris-recovery.md` |"
    in command_surfaces
)
assert (
    "| Prime-native source rollback and reviewed revert | `migration/rollback-map.md` |"
    in command_surfaces
)
assert (
    "| Backup, restore, recovery, rollback | `recovery/elantris-recovery.md`, `migration/rollback-map.md` |"
    not in command_surfaces
)

interaction_path = "`governance/mission-control-interaction-contract.md`"
assert interaction_path in start_here
assert (
    start_here.index("`routing/command-surfaces.md`")
    < start_here.index(interaction_path)
    < start_here.index("`safety/atlas-safety-doctrine.md`")
)
assert (
    "| Mission Control, Decision Boxes, Preview-first interaction, and final copy-paste action surfaces | "
    "`governance/mission-control-interaction-contract.md`;"
    in command_surfaces
)
assert 'status: "CANONICAL_ACTIVE"' in interaction
assert "merged Prime defines the exact doctrine" in start_here
assert "saved memory" in start_here

generated_root = ROOT / "generated"
if generated_root.exists() and any(path.is_file() for path in generated_root.rglob("*")):
    raise SystemExit("Committed generated projection reports are retired from the active tree")

for path in ROOT.rglob("*"):
    if path.is_file() and (path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts):
        raise SystemExit(f"Runtime byproduct found: {path.relative_to(ROOT)}")

print("Prime kernel static checks: PASS")
