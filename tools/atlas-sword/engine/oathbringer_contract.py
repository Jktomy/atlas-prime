from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence


FORMAT_VERSION = "1.2"
CHANGE_METHOD = "OATHBRINGER"
EXECUTION_ENVIRONMENT = "POWERSHELL"
FRAMEWORK_STATE = "PILOT_DISABLED"
RUNTIME_MODE = "AUDIT_ONLY"


class OathbringerContractError(RuntimeError):
    """Base error for audit-only Oathbringer contract failures."""


class WorkflowGateError(OathbringerContractError):
    """Raised when an applicable workflow is missing, failed, or timed out."""


class ReceiptWriteError(OathbringerContractError):
    """Raised when an atomic receipt cannot be written."""


@dataclass
class StageLedger:
    """Audit-only ledger that records stage entry before work begins."""

    current_stage: str = "START"
    last_completed_stage: str = "NONE"
    progress_percent: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def enter(self, stage: str, progress_percent: int, message: str | None = None) -> None:
        if not stage:
            raise OathbringerContractError("stage name must not be empty")
        if progress_percent < 0 or progress_percent > 100:
            raise OathbringerContractError("stage progress must be between 0 and 100")
        self.current_stage = stage
        self.progress_percent = progress_percent
        self.history.append(
            {
                "event": "ENTER",
                "stage": stage,
                "progress_percent": progress_percent,
                "message": message,
            }
        )

    def complete(self, detail: str | None = None) -> None:
        if self.current_stage == "START":
            raise OathbringerContractError("cannot complete a stage before entering it")
        self.last_completed_stage = self.current_stage
        self.history.append(
            {
                "event": "COMPLETE",
                "stage": self.current_stage,
                "progress_percent": self.progress_percent,
                "detail": detail,
            }
        )

    def fail(self, detail: str | None = None) -> None:
        self.history.append(
            {
                "event": "FAIL",
                "stage": self.current_stage,
                "progress_percent": self.progress_percent,
                "detail": detail,
            }
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "current_stage": self.current_stage,
            "last_completed_stage": self.last_completed_stage,
            "progress_percent": self.progress_percent,
            "history": self.history,
        }


def github_pattern_regex(pattern: str) -> re.Pattern[str]:
    pieces: list[str] = ["^"]
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                if index + 2 < len(pattern) and pattern[index + 2] == "/":
                    pieces.append("(?:.*/)?")
                    index += 3
                    continue
                pieces.append(".*")
                index += 2
                continue
            pieces.append("[^/]*")
            index += 1
            continue
        if char == "?":
            pieces.append("[^/]")
            index += 1
            continue
        pieces.append(re.escape(char))
        index += 1
    pieces.append("$")
    return re.compile("".join(pieces))


def github_path_matches(path: str, pattern: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return github_pattern_regex(pattern).fullmatch(normalized) is not None


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OathbringerContractError(message)


def _safe_relative_path(value: Any, field_name: str) -> str:
    path = str(value or "").replace("\\", "/").lstrip("./")
    _require(bool(path), f"{field_name} must not be empty")
    _require(not path.startswith("/"), f"{field_name} must be relative")
    _require("/../" not in f"/{path}/", f"{field_name} must not contain ..")
    _require("\\" not in str(value or ""), f"{field_name} must use forward slashes")
    return path


def _sha40_or_none(value: Any, field_name: str) -> None:
    if value is None:
        return
    _require(
        re.fullmatch(r"[0-9a-f]{40}", str(value)) is not None,
        f"{field_name} must be a lowercase SHA-1",
    )


def _sha256_or_none(value: Any, field_name: str) -> None:
    if value is None:
        return
    _require(
        re.fullmatch(r"[0-9a-f]{64}", str(value)) is not None,
        f"{field_name} must be a lowercase SHA-256",
    )


def validate_receipt_contract(contract: dict[str, Any]) -> None:
    expected = {
        "write_on_interrupt": True,
        "write_on_failure": True,
        "completion_flags_required": True,
        "automatic_retry": False,
        "automatic_rollback": False,
        "interrupt_exit_code": 130,
        "failure_exit_code": 1,
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise OathbringerContractError(
                f"receipt contract mismatch for {key}: expected {value!r}; "
                f"observed {contract.get(key)!r}"
            )


def validate_mission(mission: dict[str, Any]) -> None:
    required = [
        "format_version",
        "mission_id",
        "sword_identity",
        "change_method",
        "execution_environment",
        "lane",
        "framework_state",
        "runtime_mode",
        "repository",
        "expected_base",
        "declared_paths",
        "workflow_rules",
        "receipt_contract",
        "stop_boundary",
        "forbidden_actions",
    ]
    for field_name in required:
        _require(field_name in mission, f"mission missing required field: {field_name}")

    _require("method_profile" not in mission, "method_profile is retired in schema 1.2")
    _require(mission["format_version"] == FORMAT_VERSION, "format_version must be 1.2")
    _require(mission["change_method"] == CHANGE_METHOD, "change_method must be OATHBRINGER")
    _require(
        mission["execution_environment"] == EXECUTION_ENVIRONMENT,
        "execution_environment must be POWERSHELL",
    )
    _require(mission["framework_state"] == FRAMEWORK_STATE, "framework_state must be PILOT_DISABLED")
    _require(mission["runtime_mode"] == RUNTIME_MODE, "runtime_mode must be AUDIT_ONLY")
    _require(mission["lane"] in {"BUILD", "REPAIR", "EXECUTE"}, "invalid lane")
    _require(
        re.fullmatch(r"^[^/\s]+/[^/\s]+$", str(mission["repository"])) is not None,
        "repository must be owner/repo",
    )
    _require(
        re.fullmatch(r"[0-9a-f]{40}", str(mission["expected_base"])) is not None,
        "expected_base must be a lowercase SHA-1",
    )
    _sha40_or_none(mission.get("expected_head"), "expected_head")

    if mission.get("branch") is not None:
        _require(bool(str(mission["branch"])), "branch must not be empty when set")
    if mission.get("pull_request") is not None:
        _require(isinstance(mission["pull_request"], int), "pull_request must be an integer")
        _require(mission["pull_request"] >= 1, "pull_request must be positive")

    declared_paths = mission["declared_paths"]
    _require(isinstance(declared_paths, list) and declared_paths, "declared_paths must be non-empty")
    seen_paths: set[str] = set()
    for index, item in enumerate(declared_paths):
        _require(isinstance(item, dict), f"declared_paths[{index}] must be an object")
        path = _safe_relative_path(item.get("path"), f"declared_paths[{index}].path")
        _require(path not in seen_paths, f"duplicate declared path: {path}")
        seen_paths.add(path)
        _require(item.get("operation") in {"ADD", "REPLACE", "DELETE"}, f"invalid operation for {path}")
        _sha256_or_none(item.get("payload_sha256"), f"declared_paths[{index}].payload_sha256")
        _sha40_or_none(item.get("source_blob"), f"declared_paths[{index}].source_blob")

    workflow_rules = mission["workflow_rules"]
    _require(isinstance(workflow_rules, list), "workflow_rules must be an array")
    seen_workflows: set[str] = set()
    for index, rule in enumerate(workflow_rules):
        _validate_workflow_rule(rule, index=index)
        name = str(rule["name"])
        _require(name not in seen_workflows, f"duplicate workflow rule: {name}")
        seen_workflows.add(name)

    validate_receipt_contract(mission["receipt_contract"])
    forbidden = mission["forbidden_actions"]
    _require(isinstance(forbidden, list) and forbidden, "forbidden_actions must be non-empty")
    _require(len(forbidden) == len(set(str(item) for item in forbidden)), "forbidden_actions must be unique")


def declared_path_names(declared_paths: Sequence[dict[str, Any]]) -> list[str]:
    paths = [
        str(item["path"]).replace("\\", "/").lstrip("./")
        for item in declared_paths
    ]
    if len(paths) != len(set(paths)):
        raise OathbringerContractError("declared path set contains duplicates")
    return sorted(paths)


def _validate_workflow_rule(rule: dict[str, Any], index: int | None = None) -> None:
    prefix = f"workflow_rules[{index}]" if index is not None else "workflow rule"
    _require(isinstance(rule, dict), f"{prefix} must be an object")
    name = str(rule.get("name") or "")
    _require(bool(name), f"{prefix} name must not be empty")
    _require(str(rule.get("event") or "") == "pull_request", f"{prefix} event must be pull_request")
    _safe_relative_path(rule.get("workflow_path"), f"{prefix}.workflow_path")
    workflow_blob = str(rule.get("workflow_blob") or "")
    _require(
        re.fullmatch(r"[0-9a-f]{40}", workflow_blob) is not None,
        f"{prefix} has an invalid workflow blob",
    )
    appearance = int(rule.get("appearance_grace_seconds", 0))
    completion = int(rule.get("completion_timeout_seconds", 0))
    _require(appearance >= 1, f"{prefix} has an invalid appearance grace")
    _require(completion >= 1, f"{prefix} has an invalid completion timeout")
    _require(rule.get("expected_conclusion") == "success", f"{prefix} must expect success")
    patterns = rule.get("pull_request_paths")
    if patterns is not None:
        _require(isinstance(patterns, list) and patterns, f"{prefix} path filters must be null or non-empty")
        _require(
            len(patterns) == len(set(str(item) for item in patterns)),
            f"{prefix} contains duplicate path filters",
        )
        for item in patterns:
            _require(bool(str(item)), f"{prefix} path filters must not be empty")


def resolve_workflow_applicability(
    changed_paths: Sequence[str],
    workflow_rules: Sequence[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    normalized = sorted(
        {path.replace("\\", "/").lstrip("./") for path in changed_paths}
    )
    result: dict[str, dict[str, Any]] = {}

    for rule in workflow_rules:
        _validate_workflow_rule(rule)
        name = str(rule["name"])
        if name in result:
            raise OathbringerContractError(f"duplicate workflow rule: {name}")

        patterns = rule.get("pull_request_paths")
        if patterns is None:
            result[name] = {
                "classification": "REQUIRED",
                "applicable": True,
                "reason": "unfiltered pull_request trigger",
                "matched_path": None,
                "matched_pattern": None,
                "workflow_path": rule["workflow_path"],
                "workflow_blob": rule["workflow_blob"],
                "event": rule["event"],
                "appearance_grace_seconds": rule["appearance_grace_seconds"],
                "completion_timeout_seconds": rule["completion_timeout_seconds"],
                "expected_conclusion": rule["expected_conclusion"],
            }
            continue

        match: tuple[str, str] | None = None
        for path in normalized:
            for pattern_value in patterns:
                pattern = str(pattern_value)
                if github_path_matches(path, pattern):
                    match = (path, pattern)
                    break
            if match is not None:
                break

        result[name] = {
            "classification": "REQUIRED" if match else "NOT_APPLICABLE",
            "applicable": match is not None,
            "reason": (
                "changed path matched pull_request path filter"
                if match
                else "no changed path matched pull_request path filters"
            ),
            "matched_path": match[0] if match else None,
            "matched_pattern": match[1] if match else None,
            "workflow_path": rule["workflow_path"],
            "workflow_blob": rule["workflow_blob"],
            "event": rule["event"],
            "appearance_grace_seconds": rule["appearance_grace_seconds"],
            "completion_timeout_seconds": rule["completion_timeout_seconds"],
            "expected_conclusion": rule["expected_conclusion"],
        }

    return result


def _run_id(run: dict[str, Any]) -> int:
    return int(run.get("databaseId") or run.get("run_id") or run.get("id") or 0)


def _run_attempt(run: dict[str, Any]) -> int:
    return int(run.get("runAttempt") or run.get("run_attempt") or run.get("attempt") or 0)


def _run_updated(run: dict[str, Any]) -> str:
    return str(run.get("updatedAt") or run.get("updated_at") or run.get("completedAt") or "")


def _run_name(run: dict[str, Any]) -> str:
    return str(run.get("workflowName") or run.get("name") or "")


def _run_event(run: dict[str, Any]) -> str:
    return str(run.get("event") or run.get("eventName") or "")


def _run_head(run: dict[str, Any]) -> str:
    return str(run.get("headSha") or run.get("head_sha") or run.get("headSHA") or "")


def workflow_run_matches(
    run: dict[str, Any],
    rule: dict[str, Any],
    head_sha: str | None,
) -> bool:
    if _run_name(run) != str(rule["name"]):
        return False
    if _run_event(run) != str(rule["event"]):
        return False
    if head_sha is not None and _run_head(run) != head_sha:
        return False
    return True


def latest_matching_runs_by_name(
    runs: Sequence[dict[str, Any]],
    workflow_rules: Sequence[dict[str, Any]],
    head_sha: str | None,
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    rules_by_name = {str(rule["name"]): rule for rule in workflow_rules}
    for run in runs:
        name = _run_name(run)
        rule = rules_by_name.get(name)
        if rule is None or not workflow_run_matches(run, rule, head_sha):
            continue
        prior = latest.get(name)
        current_key = (_run_id(run), _run_attempt(run), _run_updated(run))
        prior_key = (
            _run_id(prior),
            _run_attempt(prior),
            _run_updated(prior),
        ) if prior else (-1, -1, "")
        if prior is None or current_key >= prior_key:
            latest[name] = dict(run)
    return latest


def wait_for_required_workflows(
    changed_paths: Sequence[str],
    workflow_rules: Sequence[dict[str, Any]],
    fetch_runs: Callable[[], Sequence[dict[str, Any]]],
    *,
    head_sha: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    poll_seconds: float = 2.0,
) -> dict[str, Any]:
    """Wait only for applicable workflow runs matching exact name, event, and head."""

    applicability = resolve_workflow_applicability(changed_paths, workflow_rules)
    required = {
        name: item
        for name, item in applicability.items()
        if item["classification"] == "REQUIRED"
    }
    not_applicable = {
        name: item
        for name, item in applicability.items()
        if item["classification"] == "NOT_APPLICABLE"
    }

    rules = [rule for rule in workflow_rules if str(rule["name"]) in required]
    started = monotonic()
    first_seen: dict[str, float] = {}
    completed: dict[str, dict[str, Any]] = {}

    while True:
        now = monotonic()
        elapsed = now - started
        latest = latest_matching_runs_by_name(list(fetch_runs()), rules, head_sha)

        for name, rule in required.items():
            run = latest.get(name)
            if run is None:
                if elapsed >= float(rule["appearance_grace_seconds"]):
                    raise WorkflowGateError(
                        f"applicable workflow did not appear within "
                        f"{rule['appearance_grace_seconds']} seconds for exact "
                        f"name/event/head: {name}/pull_request/{head_sha or '*'}"
                    )
                continue

            if name not in first_seen:
                first_seen[name] = now

            status = str(run.get("status") or "").lower()
            conclusion = run.get("conclusion")
            if status == "completed":
                if conclusion != rule["expected_conclusion"]:
                    raise WorkflowGateError(
                        f"applicable workflow failed: {name} -> {conclusion!r}"
                    )
                completed[name] = run
                continue

            completion_elapsed = now - first_seen[name]
            if completion_elapsed >= float(rule["completion_timeout_seconds"]):
                raise WorkflowGateError(
                    f"applicable workflow did not complete within "
                    f"{rule['completion_timeout_seconds']} seconds after appearance: {name}"
                )

        if len(completed) == len(required):
            return {
                "status": "PASS",
                "elapsed_seconds": elapsed,
                "head_sha": head_sha,
                "required": {
                    name: {
                        **rule,
                        "run": completed[name],
                        "first_seen_elapsed_seconds": first_seen[name] - started,
                    }
                    for name, rule in sorted(required.items())
                },
                "not_applicable": dict(sorted(not_applicable.items())),
            }

        sleep(poll_seconds)


def build_add_path_audit_plan(
    declared_paths: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    all_paths = declared_path_names(declared_paths)
    add_paths = sorted(
        str(item["path"]).replace("\\", "/").lstrip("./")
        for item in declared_paths
        if item["operation"] == "ADD"
    )
    return {
        "all_declared_paths": all_paths,
        "expected_untracked_add_paths": add_paths,
        "commands": [
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            ["git", "add", "-N", "--", *add_paths] if add_paths else None,
            ["git", "diff", "--check"],
            ["git", "diff", "--name-only", "-z"],
        ],
        "policy": (
            "assert exact untracked ADD set before intent-to-add; then audit the "
            "complete candidate path set before real staging"
        ),
    }


def classify_terminal_exception(
    exception: BaseException | str,
    ledger: StageLedger | None = None,
) -> dict[str, Any]:
    exception_name = (
        exception if isinstance(exception, str) else type(exception).__name__
    )
    stage = ledger.as_dict() if ledger is not None else StageLedger().as_dict()
    if exception_name == "KeyboardInterrupt":
        return {
            "status": "OATHBRINGER_INTERRUPTED_PRESERVED_PARTIAL_STATE",
            "stop_point": "INTERRUPTED_FAIL_CLOSED",
            "exit_code": 130,
            "ledger_title": "OATHBRINGER INTERRUPT LEDGER",
            "receipt_required": True,
            "stage": stage,
        }
    return {
        "status": "OATHBRINGER_FAILED_PRESERVED_PARTIAL_STATE",
        "stop_point": "FAIL_CLOSED",
        "exit_code": 1,
        "ledger_title": "OATHBRINGER FAILURE LEDGER",
        "receipt_required": True,
        "stage": stage,
    }


def build_receipt(
    *,
    mission: dict[str, Any] | None,
    ledger: StageLedger,
    status: str,
    detail: str | None,
    exit_code: int,
) -> dict[str, Any]:
    return {
        "receipt_version": "1.0",
        "format_version": FORMAT_VERSION,
        "change_method": CHANGE_METHOD,
        "execution_environment": EXECUTION_ENVIRONMENT,
        "runtime_mode": RUNTIME_MODE,
        "status": status,
        "detail": detail,
        "exit_code": exit_code,
        "mission_id": None if mission is None else mission.get("mission_id"),
        "sword_identity": None if mission is None else mission.get("sword_identity"),
        "repository": None if mission is None else mission.get("repository"),
        "expected_base": None if mission is None else mission.get("expected_base"),
        "expected_head": None if mission is None else mission.get("expected_head"),
        "stage_ledger": ledger.as_dict(),
        "completion_flags": {
            "receipt_written": True,
            "mutation_performed": False,
            "github_called": False,
            "automatic_retry": False,
            "automatic_rollback": False,
        },
    }


def is_transient_windows_replace_lock(exception: OSError) -> bool:
    return getattr(exception, "winerror", None) in {5, 32, 33}


def replace_with_bounded_retry(
    source: Path,
    destination: Path,
    *,
    replace: Callable[[Path, Path], None] = os.replace,
    sleep: Callable[[float], None] = time.sleep,
    attempts: int = 5,
) -> None:
    for attempt in range(attempts):
        try:
            replace(source, destination)
            return
        except OSError as exc:
            if not is_transient_windows_replace_lock(exc) or attempt == attempts - 1:
                raise
            sleep(0.05 * (2**attempt))


def atomic_write_json_with_sha256(
    path: Path,
    payload: dict[str, Any],
    *,
    replace: Callable[[Path, Path], None] = os.replace,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    token = f"{os.getpid()}-{time.time_ns()}"
    temp_json = destination.with_name(f".{destination.name}.{token}.tmp")
    temp_sidecar = destination.with_name(f".{destination.name}.{token}.sha256.tmp")
    sidecar = destination.with_name(f"{destination.name}.sha256")

    try:
        temp_json.write_text(text, encoding="utf-8", newline="\n")
        replace_with_bounded_retry(temp_json, destination, replace=replace, sleep=sleep)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        temp_sidecar.write_text(f"{digest}  {destination.name}\n", encoding="ascii", newline="\n")
        replace_with_bounded_retry(temp_sidecar, sidecar, replace=replace, sleep=sleep)
    except OSError as exc:
        for temp_path in (temp_json, temp_sidecar):
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
        raise ReceiptWriteError(f"receipt write failed: {exc}") from exc

    return {
        "receipt_path": str(destination),
        "receipt_sha256": digest,
        "sidecar_path": str(sidecar),
        "sidecar_sha256": hashlib.sha256(sidecar.read_bytes()).hexdigest(),
    }


def verify_manifest_if_present(package_root: Path) -> bool:
    manifest_path = package_root / "MANIFEST.json"
    if not manifest_path.is_file():
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("files", []):
        member = package_root / str(entry["path"])
        if not member.is_file():
            raise OathbringerContractError(f"manifest member missing: {entry['path']}")
        observed = hashlib.sha256(member.read_bytes()).hexdigest()
        if observed != str(entry["sha256"]):
            raise OathbringerContractError(f"manifest hash mismatch: {entry['path']}")
        if member.stat().st_size != int(entry["size"]):
            raise OathbringerContractError(f"manifest size mismatch: {entry['path']}")
    return True


def audit_mission(
    mission: dict[str, Any],
    *,
    package_root: Path | None = None,
) -> dict[str, Any]:
    ledger = StageLedger()

    ledger.enter("PACKAGE_AUDIT", 5, "verify package manifest when present")
    manifest_verified = verify_manifest_if_present(package_root) if package_root else False
    ledger.complete(f"package manifest verified={manifest_verified}")

    ledger.enter("MISSION_SCHEMA", 20, "validate schema 1.2 mission")
    validate_mission(mission)
    ledger.complete("mission contract validated")

    paths = declared_path_names(mission["declared_paths"])
    ledger.enter("WORKFLOW_APPLICABILITY", 45, "classify path-applicable workflows")
    applicability = resolve_workflow_applicability(paths, mission["workflow_rules"])
    ledger.complete("workflow applicability classified")

    ledger.enter("RECEIPT_CONTRACT", 65, "classify receipt and terminal failure states")
    interrupt_classification = classify_terminal_exception(KeyboardInterrupt(), ledger)
    failure_classification = classify_terminal_exception(OathbringerContractError("fixture"), ledger)
    ledger.complete("receipt classifications prepared")

    ledger.enter("ADD_PATH_AUDIT_PLAN", 80, "build exact ADD audit plan")
    add_plan = build_add_path_audit_plan(mission["declared_paths"])
    ledger.complete("ADD audit plan prepared")

    ledger.enter("STOP_BOUNDARY", 100, "stop at audit-only boundary")
    ledger.complete(str(mission["stop_boundary"]))

    return {
        "result": "PASS",
        "mode": RUNTIME_MODE,
        "format_version": FORMAT_VERSION,
        "framework_state": FRAMEWORK_STATE,
        "change_method": CHANGE_METHOD,
        "execution_environment": EXECUTION_ENVIRONMENT,
        "sword_identity": mission["sword_identity"],
        "lane": mission["lane"],
        "repository": mission["repository"],
        "expected_base": mission["expected_base"],
        "expected_head": mission.get("expected_head"),
        "declared_paths": mission["declared_paths"],
        "workflow_rules": mission["workflow_rules"],
        "receipt_contract": mission["receipt_contract"],
        "stop_boundary": mission["stop_boundary"],
        "package_manifest_verified": manifest_verified,
        "changed_paths": paths,
        "workflow_applicability": applicability,
        "add_path_audit_plan": add_plan,
        "interrupt_classification": interrupt_classification,
        "failure_classification": failure_classification,
        "stage_ledger": ledger.as_dict(),
        "production_adapter_present": False,
        "mutation_performed": False,
        "github_called": False,
        "final_display": {
            "persistent": True,
            "automatic_exit": False,
            "second_confirmation_requested": False,
            "next_safe_gate": mission["stop_boundary"],
        },
    }


def render_terminal_result(result: dict[str, Any]) -> str:
    lines = [
        "=== ATLAS SWORD / OATHBRINGER AUDIT ===",
        f"Sword: {result.get('sword_identity')}",
        f"Mode: {result.get('mode')}",
        f"Change method: {result.get('change_method')}",
        f"Execution environment: {result.get('execution_environment')}",
        f"Repository: {result.get('repository')}",
        f"Base: {result.get('expected_base')}",
        f"Head: {result.get('expected_head')}",
        f"Result: {result.get('result')}",
        "",
        "Stages:",
    ]
    for item in result.get("stage_ledger", {}).get("history", []):
        lines.append(
            "[{event}][{progress_percent:>3}%][{stage}] {detail}{message}".format(
                event=item.get("event"),
                progress_percent=item.get("progress_percent", 0),
                stage=item.get("stage"),
                detail=item.get("detail") or "",
                message=item.get("message") or "",
            )
        )
    lines.append("")
    lines.append("Workflows:")
    for name, item in sorted(result.get("workflow_applicability", {}).items()):
        lines.append(f"- {name}: {item['classification']} ({item['reason']})")
    lines.extend(
        [
            "",
            f"Stop boundary: {result.get('stop_boundary')}",
            "Final display remains in the host; no automatic exit and no second confirmation.",
        ]
    )
    return "\n".join(lines)


def _failure_result(
    exception: BaseException,
    *,
    mission: dict[str, Any] | None,
    ledger: StageLedger,
) -> dict[str, Any]:
    ledger.fail(str(exception))
    classification = classify_terminal_exception(exception, ledger)
    return {
        "result": "FAIL",
        "mode": RUNTIME_MODE,
        "format_version": FORMAT_VERSION,
        "change_method": CHANGE_METHOD,
        "execution_environment": EXECUTION_ENVIRONMENT,
        "error": str(exception),
        "classification": classification,
        "mission_id": None if mission is None else mission.get("mission_id"),
        "sword_identity": None if mission is None else mission.get("sword_identity"),
        "stage_ledger": ledger.as_dict(),
        "mutation_performed": False,
        "github_called": False,
        "final_display": {
            "persistent": True,
            "automatic_exit": False,
            "second_confirmation_requested": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", required=True)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--receipt")
    parser.add_argument("--package-root")
    args = parser.parse_args()

    ledger = StageLedger()
    mission: dict[str, Any] | None = None
    try:
        if not args.audit_only:
            raise OathbringerContractError("--audit-only is mandatory")
        mission_path = Path(args.mission).resolve()
        mission = json.loads(mission_path.read_text(encoding="utf-8"))
        result = audit_mission(
            mission,
            package_root=Path(args.package_root).resolve() if args.package_root else None,
        )
        if args.receipt:
            receipt = build_receipt(
                mission=mission,
                ledger=StageLedger(**{k: v for k, v in result["stage_ledger"].items() if k != "history"}, history=result["stage_ledger"]["history"]),
                status="OATHBRINGER_AUDIT_PASS",
                detail=str(result["stop_boundary"]),
                exit_code=0,
            )
            result["receipt_write"] = atomic_write_json_with_sha256(Path(args.receipt), receipt)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else render_terminal_result(result))
        return 0
    except KeyboardInterrupt as exc:
        result = _failure_result(exc, mission=mission, ledger=ledger)
        if args.receipt:
            receipt = build_receipt(
                mission=mission,
                ledger=ledger,
                status=result["classification"]["status"],
                detail="operator interrupt",
                exit_code=130,
            )
            result["receipt_write"] = atomic_write_json_with_sha256(Path(args.receipt), receipt)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else render_terminal_result(result))
        return 130
    except Exception as exc:
        result = _failure_result(exc, mission=mission, ledger=ledger)
        if args.receipt:
            receipt = build_receipt(
                mission=mission,
                ledger=ledger,
                status=result["classification"]["status"],
                detail=str(exc),
                exit_code=1,
            )
            result["receipt_write"] = atomic_write_json_with_sha256(Path(args.receipt), receipt)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else render_terminal_result(result))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
