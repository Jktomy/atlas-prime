from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    check_id: str
    command: tuple[str, ...]


PYTHON = sys.executable
CHECKS: dict[str, Check] = {
    "kernel": Check("kernel", (PYTHON, "-B", "tests/bootstrap/test_prime_kernel.py")),
    "repository_policy": Check(
        "repository_policy",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/repository-policy", "-p", "test_*.py", "-v"),
    ),
    "privacy": Check(
        "privacy",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/privacy", "-p", "test_*.py", "-v"),
    ),
    "lifecycle": Check(
        "lifecycle",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/lifecycle", "-p", "test_*.py", "-v"),
    ),
    "thread_engine": Check(
        "thread_engine",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tools/thread-engine/tests", "-p", "test_*.py", "-v"),
    ),
    "thread_engine_static": Check(
        "thread_engine_static",
        (PYTHON, "-B", "tools/thread-engine/tests/static_checks.py"),
    ),
    "atlas_sword_static": Check(
        "atlas_sword_static",
        (PYTHON, "-B", "tools/atlas-sword/tests/static_checks.py"),
    ),
    "generators": Check(
        "generators",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/generators", "-p", "test_*.py", "-v"),
    ),
    "prime_program": Check(
        "prime_program",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/prime-program", "-p", "test_*.py", "-v"),
    ),
    "athena_routes": Check(
        "athena_routes",
        (PYTHON, "-B", "-m", "unittest", "discover", "-s", "tests/athena-routes", "-p", "test_*.py", "-v"),
    ),
    "source_validation": Check(
        "source_validation",
        (PYTHON, "-B", "tools/prime_checks/validate_prime.py"),
    ),
    "powershell_resolver": Check(
        "powershell_resolver",
        (
            "pwsh",
            "-NoProfile",
            "-Command",
            "$result = & ./tools/thread-engine/Invoke-AtlasThreadEngineProductionAdapter.ps1 -ResolverSelfTest | ConvertFrom-Json; "
            "if ($result.invocation -ne 'native-argument-array') { throw 'Prime production launcher did not use native argument-array invocation' }; "
            "if ($result.implementation_state -ne 'THREAD_ENGINE_ACTIVE_MISSION_SCOPED') { throw 'Prime production launcher did not report active mission-scoped state' }; "
            "Write-Host 'Prime production launcher active resolver proof: PASS'",
        ),
    ),
}

FULL_CHECK_IDS: tuple[str, ...] = tuple(CHECKS)
CHECKS["continuity"] = Check(
    "continuity",
    (PYTHON, "-B", "-m", "tools.prime_continuity.cli", "validate"),
)
CHECK_ORDER: tuple[str, ...] = (*FULL_CHECK_IDS, "continuity")
BASELINE_CHECK_IDS = {"kernel", "repository_policy", "privacy", "source_validation"}


def _starts(path: str, prefixes: Iterable[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _is_root_prime_source(path: str) -> bool:
    pure = PurePosixPath(path)
    return len(pure.parts) == 1 and pure.suffix.casefold() in {".md", ".json", ".yaml", ".yml"}


def classify_paths(paths: Sequence[str], *, full: bool = False) -> dict[str, object]:
    normalized = sorted({PurePosixPath(path.strip()).as_posix() for path in paths if path.strip()})
    if full or not normalized:
        return {
            "profile": "full",
            "checks": list(FULL_CHECK_IDS),
            "windows_required": True,
            "unclassified_paths": [],
            "changed_paths": normalized,
        }

    selected = set(BASELINE_CHECK_IDS)
    unclassified: list[str] = []
    windows_required = False

    for path in normalized:
        matched = False

        if path.startswith(".github/workflows/"):
            selected.update(FULL_CHECK_IDS)
            windows_required = True
            matched = True

        if _starts(path, ("policies/", "tests/repository-policy/")) or path == "tools/thread-engine/production_adapter/protected_paths.py":
            selected.add("repository_policy")
            matched = True

        if _starts(path, ("lifecycle/", "tests/lifecycle/", "schemas/lifecycle/")) or path == "sunsetting-protocol.md":
            selected.update({"lifecycle", "prime_program"})
            matched = True

        if _starts(path, ("tools/thread-engine/", "schemas/thread-engine/")):
            selected.update({"repository_policy", "thread_engine", "thread_engine_static", "prime_program", "powershell_resolver"})
            windows_required = True
            matched = True

        if path.startswith("tools/atlas-sword/"):
            selected.update({"atlas_sword_static", "prime_program"})
            windows_required = True
            matched = True

        if _starts(path, ("tools/generated_checkpoint/", "tests/generators/", "generated/")) or path == "tools/build_index.py":
            selected.update({"generators", "prime_program"})
            if path.startswith("tools/generated_checkpoint/"):
                windows_required = True
            matched = True

        if _starts(path, ("tools/athena_routes/", "tests/athena-routes/", "schemas/athena")) or path == ".github/workflows/athena-bow-hosted.yml":
            selected.update({"athena_routes", "thread_engine", "prime_program"})
            matched = True

        if path.startswith("continuity/"):
            selected.add("continuity")
            matched = True

        if _starts(
            path,
            (
                "quests/",
                "quest-board/",
                "projects/",
                "operations/",
                "governance/",
                "recovery/",
                "proof/",
                "migration/",
                "routing/",
                "safety/",
                "schemas/",
                "tests/prime-program/",
            ),
        ) or _is_root_prime_source(path):
            selected.add("prime_program")
            matched = True

        if path.startswith("tests/privacy/"):
            selected.add("privacy")
            matched = True

        if path.startswith("tests/bootstrap/"):
            selected.add("kernel")
            matched = True

        if path.startswith("tools/prime_checks/"):
            selected.update(FULL_CHECK_IDS)
            windows_required = True
            matched = True

        if path.casefold().endswith(".ps1"):
            selected.add("powershell_resolver")
            windows_required = True
            matched = True

        if not matched:
            unclassified.append(path)

    if unclassified:
        selected = set(FULL_CHECK_IDS)
        windows_required = True
        profile = "full-fail-closed"
    elif set(FULL_CHECK_IDS).issubset(selected):
        selected = set(FULL_CHECK_IDS)
        profile = "full"
    else:
        profile = "targeted"

    ordered = [check_id for check_id in CHECK_ORDER if check_id in selected]
    return {
        "profile": profile,
        "checks": ordered,
        "windows_required": windows_required,
        "unclassified_paths": unclassified,
        "changed_paths": normalized,
    }


def git_changed_paths(base: str, head: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def write_github_output(path: str, plan: dict[str, object]) -> None:
    with open(path, "a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"windows_required={str(bool(plan['windows_required'])).lower()}\n")
        stream.write(f"profile={plan['profile']}\n")
        stream.write(f"check_count={len(plan['checks'])}\n")


def _bounded_failure_output(text: str, *, max_lines: int = 160) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    omitted = len(lines) - max_lines
    return f"[... {omitted} earlier lines omitted ...]\n" + "\n".join(lines[-max_lines:])


def execute_plan(plan: dict[str, object]) -> None:
    for check_id in plan["checks"]:
        check = CHECKS[str(check_id)]
        print(f"\n=== Prime validation: {check.check_id} ===", flush=True)
        completed = subprocess.run(
            check.command,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            print(f"Prime validation FAILED: {check.check_id}", file=sys.stderr)
            combined = "\n".join(value for value in (completed.stdout, completed.stderr) if value)
            if combined:
                print(_bounded_failure_output(combined), file=sys.stderr)
            raise subprocess.CalledProcessError(completed.returncode, check.command)
        print(f"Prime validation PASS: {check.check_id}", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan or run fail-closed targeted Prime validation.")
    parser.add_argument("--base", help="Base commit SHA for targeted validation.")
    parser.add_argument("--head", default="HEAD", help="Head commit SHA for targeted validation.")
    parser.add_argument("--full", action="store_true", help="Run the complete validation set.")
    parser.add_argument("--plan-only", action="store_true", help="Print the plan without executing it.")
    parser.add_argument("--github-output", help="Append plan outputs to the GitHub Actions output file.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.full and not args.base:
        raise SystemExit("--base is required unless --full is selected")

    paths = [] if args.full else git_changed_paths(args.base, args.head)
    plan = classify_paths(paths, full=args.full)
    print(json.dumps(plan, indent=2, sort_keys=True))

    if args.github_output:
        write_github_output(args.github_output, plan)
    if not args.plan_only:
        execute_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
