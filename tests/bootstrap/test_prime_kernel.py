from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED_GENERATED = {
    "atlas-duplicate-scope-report.md",
    "atlas-file-inventory.md",
    "atlas-metadata-inventory.md",
    "atlas-orphan-report.md",
    "atlas-routing-inventory.md",
}

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
    "| Clean-clone recovery, protected runtime restoration, and recovery proof | `recovery/phoenix-recovery.md` |"
    in command_surfaces
)
assert (
    "| Prime-native source rollback and reviewed revert | `migration/rollback-map.md` |"
    in command_surfaces
)
assert (
    "| Backup, restore, recovery, rollback | `recovery/phoenix-recovery.md`, `migration/rollback-map.md` |"
    not in command_surfaces
)

generated_root = ROOT / "generated"
if generated_root.exists():
    generated_files = {
        path.relative_to(generated_root).as_posix()
        for path in generated_root.rglob("*")
        if path.is_file()
    }
    if generated_files != APPROVED_GENERATED:
        raise SystemExit(f"Prime generated path set is not approved: {sorted(generated_files)}")
    for name in APPROVED_GENERATED:
        text = (generated_root / name).read_text(encoding="utf-8")
        if "Status: Generated support artifact" not in text or "Generated indexes report. They do not govern." not in text:
            raise SystemExit(f"Prime generated boundary marker is missing: {name}")

for path in ROOT.rglob("*"):
    if path.is_file() and (path.suffix in {".pyc", ".pyo"} or "__pycache__" in path.parts):
        raise SystemExit(f"Runtime byproduct found: {path.relative_to(ROOT)}")

print("Prime kernel static checks: PASS")
