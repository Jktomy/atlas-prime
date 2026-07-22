from __future__ import annotations

import argparse
import json
import re
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
    "generated_diagnostics": Check(
        "generated_diagnostics",
        (PYTHON, "-B", "tools/build_index.py", "--diagnostics"),
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
BASELINE_CHECK_IDS = {"kernel", "repository_policy", "privacy", "source_validation", "generated_diagnostics"}
FULL_SHA = re.compile(r"[0-9a-fA-F]{40}")


def _starts(path: str, prefixes: Iterable[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _is_root_prime_source(path: str) -> bool:
    pure = PurePosixPath(path)
    return len(pure.parts) == 1 and pure.suffix.casefold() in {".md", ".json", ".yaml", ".yml"}


def _normalize_paths(paths: Sequence[object]) -> tuple[list[str], list[str]]:
    normalized: set[str] = set()
    malformed: set[str] = set()
    for value in paths:
        if not isinstance(value, str):
            malformed.add(f"<{type(value).__name__}>")
            continue
        raw = value
        parts = raw.split("/")
        pure = PurePosixPath(raw)
        canonical = pure.as_posix()
        if (
            not raw
            or raw != raw.strip()
            or "\\" in raw
            or "\x00" in raw
            or any(ord(character) < 32 for character in raw)
            or pure.is_absolute()
            or any(part in {"", ".", ".."} for part in parts)
            or canonical != raw
        ):
            malformed.add(raw or "<empty>")
            continue
        normalized.add(canonical)
    return sorted(normalized), sorted(malformed)


def classify_paths(paths: Sequence[object], *, full: bool = False) -> dict[str, object]:
    normalized, malformed = _normalize_paths(paths)
    case_groups: dict[str, list[str]] = {}
    for path in normalized:
        case_groups.setdefault(path.casefold(), []).append(path)
    case_collisions = sorted(
        path
        for group in case_groups.values()
        if len(group) > 1
        for path in group
    )
    if full or (not normalized and not malformed):
        return {
            "profile": "full",
            "checks": list(FULL_CHECK_IDS),
            "windows_required": True,
            "unclassified_paths": [],
            "malformed_paths": malformed,
            "case_collisions": case_collisions,
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
            if not path.startswith("generated/"):
                windows_required = True
            matched = True

        if _starts(path, ("tools/athena_routes/", "tests/athena-routes/", "schemas/athena")) or path == ".github/workflows/athena-bow-hosted.yml":
            selected.update({"athena_routes", "thread_engine", "prime_program"})
            windows_required = True
            matched = True

        if path.startswith("tools/oathbringer-foundry/"):
            selected.update({"atlas_sword_static", "prime_program"})
            windows_required = True
            matched = True

        if _starts(
            path,
            (
                "quests/",
                "quest-board/",
                "continuity/",
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
            if path.startswith("schemas/"):
                windows_required = True
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

    if unclassified or malformed:
        selected.update(FULL_CHECK_IDS)
        windows_required = True
        profile = "full-fail-closed"
    elif case_collisions:
        windows_required = True
        profile = "full" if selected == set(FULL_CHECK_IDS) else "targeted"
    elif selected == set(FULL_CHECK_IDS):
        profile = "full"
    else:
        profile = "targeted"

    ordered = [check_id for check_id in FULL_CHECK_IDS if check_id in selected]
    return {
        "profile": profile,
        "checks": ordered,
        "windows_required": windows_required,
        "unclassified_paths": unclassified,
        "malformed_paths": malformed,
        "case_collisions": case_collisions,
        "changed_paths": normalized,
    }


def _parse_git_name_status_z(payload: bytes) -> list[str]:
    try:
        fields = payload.decode("utf-8", errors="strict").split("\x00")
    except UnicodeDecodeError as exc:
        raise ValueError("git changed-path evidence is not UTF-8") from exc
    if fields == [""]:
        return []
    if not fields or fields[-1] != "":
        raise ValueError("git changed-path evidence is not NUL terminated")
    fields.pop()

    paths: list[str] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        if not re.fullmatch(r"[ACDMRTUXB](?:\d{1,3})?", status):
            raise ValueError(f"unsupported git change status: {status!r}")
        path_count = 2 if status[0] in {"R", "C"} else 1
        if index + path_count > len(fields):
            raise ValueError(f"incomplete git changed-path evidence for status {status!r}")
        status_paths = fields[index:index + path_count]
        if any(not path for path in status_paths):
            raise ValueError(f"empty git changed path for status {status!r}")
        paths.extend(status_paths)
        index += path_count
    return paths


def git_changed_paths(base: str, head: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-status", "-z", "--find-renames", "--find-copies-harder", f"{base}...{head}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return _parse_git_name_status_z(completed.stdout)


def _git_output(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_candidate_identity(base: str, head: str) -> dict[str, str]:
    if not FULL_SHA.fullmatch(base) or not FULL_SHA.fullmatch(head):
        raise SystemExit("--base and --head must be exact 40-character commit SHAs")
    base_sha = _git_output("rev-parse", "--verify", f"{base}^{{commit}}")
    head_sha = _git_output("rev-parse", "--verify", f"{head}^{{commit}}")
    checkout_sha = _git_output("rev-parse", "HEAD")
    merge_base_sha = _git_output("merge-base", base_sha, head_sha)
    if checkout_sha != head_sha:
        raise SystemExit(f"checked-out HEAD {checkout_sha} does not match exact candidate head {head_sha}")
    if merge_base_sha != base_sha:
        raise SystemExit(f"candidate is not based on exact base: expected {base_sha}, merge base is {merge_base_sha}")
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "merge_base_sha": merge_base_sha,
        "checkout_sha": checkout_sha,
    }


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
        if check_id == "generated_diagnostics":
            for line in completed.stdout.splitlines():
                if '"schema_id": "atlas.generated-projection-diagnostics.v1"' in line:
                    print(line, flush=True)
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

    identity = None if args.full else git_candidate_identity(args.base, args.head)
    paths = [] if args.full else git_changed_paths(args.base, args.head)
    plan = classify_paths(paths, full=args.full)
    if identity is not None:
        plan["identity"] = identity
    print(json.dumps(plan, indent=2, sort_keys=True))

    if args.github_output:
        write_github_output(args.github_output, plan)
    if not args.plan_only:
        execute_plan(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
