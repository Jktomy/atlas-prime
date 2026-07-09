from __future__ import annotations

import ast
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def add_error(message: str) -> None:
    errors.append(message)


def expect_raises(expected: type[BaseException], func, message: str) -> None:
    try:
        func()
    except expected:
        return
    except Exception as exc:
        add_error(f"{message}: raised {type(exc).__name__}, expected {expected.__name__}")
        return
    add_error(f"{message}: did not raise")


for path in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(path.read_text("utf-8"), filename=str(path))
    except SyntaxError as exc:
        add_error(f"{path.relative_to(ROOT)} Python syntax: {exc}")

ps_files = sorted(ROOT.rglob("*.ps1")) + sorted(ROOT.rglob("*.psm1"))
for path in ps_files:
    data = path.read_bytes()
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        add_error(f"{path.relative_to(ROOT)} is not ASCII-only")
        continue

    hazard = re.compile(
        r"\$(?!(?:env|script|global|local|private|using):)"
        r"[A-Za-z_][A-Za-z0-9_]*:",
        flags=re.IGNORECASE,
    )
    for match in hazard.finditer(text):
        add_error(
            f"{path.relative_to(ROOT)} variable-colon hazard: {match.group(0)}"
        )

    forbidden = {
        "Read-Host": "second confirmation",
        "Invoke-Expression": "dynamic shell execution",
        "iex ": "dynamic shell execution",
        "[Environment]::Exit": "automatic host exit",
        "\nexit ": "automatic host exit",
    }
    for token, reason in forbidden.items():
        if token in text:
            add_error(f"{path.relative_to(ROOT)} contains {reason}: {token}")

runner_path = ROOT / "engine" / "Invoke-AtlasSword.ps1"
runner = runner_path.read_text("ascii")
for token in [
    "-AuditOnly is mandatory",
    "Invoke-AtlasOathbringerContract",
    "[switch]$Json",
    "[string]$ReceiptPath",
    "Resolve-Path -LiteralPath $MissionPath",
]:
    if token not in runner:
        add_error(f"runner missing required thin-client control: {token}")

for forbidden_runner_token in [
    "Test-Json",
    "ConvertFrom-Json",
    "ConvertTo-Json",
    "Test-AtlasManifest",
    "New-AtlasFreshCloneAuditPlan",
]:
    if forbidden_runner_token in runner:
        add_error(f"runner duplicates Python authority: {forbidden_runner_token}")

module_text = (ROOT / "engine" / "AtlasSword.Common.psm1").read_text("ascii")
for token in [
    "Resolve-AtlasPythonCommand",
    "[string[]]$Arguments",
    "[Parameter(Mandatory)][ref]$ExitCode",
    "'-S'",
    "'-B'",
    "'--audit-only'",
    "'--package-root'",
    "& ([string]$Python.FilePath) @Arguments",
    "$ExitCode.Value = $LASTEXITCODE",
]:
    if token not in module_text:
        add_error(f"module missing thin streaming control: {token}")

for forbidden_module_token in [
    "Test-Json",
    "ConvertFrom-Json",
    "ConvertTo-Json",
    "Test-AtlasManifest",
    "New-AtlasFreshCloneAuditPlan",
]:
    if forbidden_module_token in module_text:
        add_error(f"module duplicates Python authority: {forbidden_module_token}")

for source_text, source_name in [(runner, "runner"), (module_text, "module")]:
    for forbidden_call in [
        "gh pr create",
        "gh pr edit",
        "gh pr ready",
        "gh pr merge",
        "git push",
        "git commit",
    ]:
        if forbidden_call in source_text:
            add_error(f"{source_name} contains mutation command: {forbidden_call}")

schema = json.loads((ROOT / "mission.schema.json").read_text("utf-8"))
required = schema["required"]
for field in [
    "change_method",
    "execution_environment",
    "runtime_mode",
    "workflow_rules",
    "receipt_contract",
]:
    if field not in required:
        add_error(f"mission schema does not require {field}")
if "method_profile" in required or "method_profile" in schema["properties"]:
    add_error("mission schema still exposes retired method_profile")
if schema["properties"]["format_version"].get("const") != "1.2":
    add_error("mission schema format_version is not 1.2")
if schema["properties"]["change_method"].get("const") != "OATHBRINGER":
    add_error("mission schema change_method is not OATHBRINGER")
if schema["properties"]["execution_environment"].get("const") != "POWERSHELL":
    add_error("mission schema execution_environment is not POWERSHELL")
workflow_required = schema["properties"]["workflow_rules"]["items"]["required"]
for field in ["event", "appearance_grace_seconds", "completion_timeout_seconds"]:
    if field not in workflow_required:
        add_error(f"workflow rule schema does not require {field}")

repo_pattern = schema["properties"]["repository"]["pattern"]
if re.fullmatch(repo_pattern, "Jktomy/atlas-prime") is None:
    add_error("repository schema rejects valid owner/repo")
if re.fullmatch(repo_pattern, "owner with space/repo") is not None:
    add_error("repository schema accepts whitespace")

path_pattern = (
    schema["properties"]["declared_paths"]["items"]["properties"]["path"]
    ["not"]["pattern"]
)
for unsafe_path in ["/absolute.md", "../escape.md", "a/../escape.md", r"a\b.md"]:
    if re.search(path_pattern, unsafe_path) is None:
        add_error(f"path schema misses unsafe path: {unsafe_path}")

expected_receipt_contract = {
    "write_on_interrupt": True,
    "write_on_failure": True,
    "completion_flags_required": True,
    "automatic_retry": False,
    "automatic_rollback": False,
    "interrupt_exit_code": 130,
    "failure_exit_code": 1,
}

contract_path = ROOT / "engine" / "oathbringer_contract.py"
spec = importlib.util.spec_from_file_location("oathbringer_contract", contract_path)
contract = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = contract
spec.loader.exec_module(contract)

examples = sorted((ROOT / "examples").glob("*.json"))
example_missions = []
for example in examples:
    mission = json.loads(example.read_text("utf-8"))
    example_missions.append((example, mission))
    missing = [name for name in required if name not in mission]
    if missing:
        add_error(f"{example.name} missing fields: {missing}")
    if "method_profile" in mission:
        add_error(f"{example.name} still contains retired method_profile")
    if mission.get("format_version") != "1.2":
        add_error(f"{example.name} is not schema 1.2")
    if mission.get("change_method") != "OATHBRINGER":
        add_error(f"{example.name} is not OATHBRINGER")
    if mission.get("execution_environment") != "POWERSHELL":
        add_error(f"{example.name} is not POWERSHELL")
    if mission.get("framework_state") != "PILOT_DISABLED":
        add_error(f"{example.name} is not PILOT_DISABLED")
    if mission.get("runtime_mode") != "AUDIT_ONLY":
        add_error(f"{example.name} is not AUDIT_ONLY")
    if mission.get("receipt_contract") != expected_receipt_contract:
        add_error(f"{example.name} receipt contract mismatch")
    expect_raises(
        expected=Exception,
        func=lambda mission=mission: contract.validate_mission(mission),
        message=f"{example.name} validate_mission should not raise",
    ) if False else None
    try:
        contract.validate_mission(mission)
    except Exception as exc:
        add_error(f"{example.name} rejected by Python validator: {exc}")

execute_mission = json.loads(
    (ROOT / "examples" / "execute.example.json").read_text("utf-8")
)
paths = contract.declared_path_names(execute_mission["declared_paths"])
applicability = contract.resolve_workflow_applicability(
    paths, execute_mission["workflow_rules"]
)
if applicability["Atlas Verify"]["classification"] != "REQUIRED":
    add_error("Atlas Verify was not classified REQUIRED")
if (
    applicability["Atlas Verify Generated Index Artifacts"]["classification"]
    != "NOT_APPLICABLE"
):
    add_error("generated-index workflow was not classified NOT_APPLICABLE")

add_plan = contract.build_add_path_audit_plan(execute_mission["declared_paths"])
if add_plan["commands"][0] != [
    "git",
    "ls-files",
    "--others",
    "--exclude-standard",
    "-z",
]:
    add_error("ADD audit does not begin with exact untracked enumeration")
if add_plan["commands"][1][:4] != ["git", "add", "-N", "--"]:
    add_error("ADD audit does not use intent-to-add after enumeration")

ledger = contract.StageLedger()
ledger.enter("EXAMPLE", 10)
ledger.complete("done")
if ledger.history[0]["event"] != "ENTER":
    add_error("stage ledger did not record entry before completion")
if ledger.last_completed_stage != "EXAMPLE":
    add_error("stage ledger completion mismatch")

interrupt = contract.classify_terminal_exception(KeyboardInterrupt(), ledger)
if interrupt["exit_code"] != 130 or not interrupt["receipt_required"]:
    add_error("interrupt receipt classification mismatch")
if interrupt["stage"]["last_completed_stage"] != "EXAMPLE":
    add_error("interrupt classification is not stage-aware")

invalid = copy.deepcopy(execute_mission)
invalid["method_profile"] = "OATHBRINGER"
expect_raises(
    contract.OathbringerContractError,
    lambda: contract.validate_mission(invalid),
    "retired method_profile was accepted",
)
invalid = copy.deepcopy(execute_mission)
invalid["format_version"] = "1.1"
expect_raises(
    contract.OathbringerContractError,
    lambda: contract.validate_mission(invalid),
    "schema 1.1 mission was accepted",
)

workflow_rules = copy.deepcopy(execute_mission["workflow_rules"])
workflow_rules[0]["appearance_grace_seconds"] = 2
workflow_rules[0]["completion_timeout_seconds"] = 2

same_run_refresh = contract.latest_matching_runs_by_name(
    [
        {
            "databaseId": 1,
            "workflowName": "Atlas Verify",
            "event": "pull_request",
            "headSha": execute_mission["expected_head"],
            "status": "in_progress",
            "conclusion": None,
            "updatedAt": "2026-07-08T00:00:00Z",
        },
        {
            "databaseId": 1,
            "workflowName": "Atlas Verify",
            "event": "pull_request",
            "headSha": execute_mission["expected_head"],
            "status": "completed",
            "conclusion": "success",
            "updatedAt": "2026-07-08T00:01:00Z",
        },
    ],
    workflow_rules,
    execute_mission["expected_head"],
)
if same_run_refresh["Atlas Verify"]["status"] != "completed":
    add_error("same-run refresh did not prefer newer status")

newer_run = contract.latest_matching_runs_by_name(
    [
        {
            "databaseId": 1,
            "workflowName": "Atlas Verify",
            "event": "pull_request",
            "headSha": execute_mission["expected_head"],
            "status": "completed",
            "conclusion": "failure",
        },
        {
            "databaseId": 2,
            "workflowName": "Atlas Verify",
            "event": "pull_request",
            "headSha": execute_mission["expected_head"],
            "status": "completed",
            "conclusion": "success",
        },
        {
            "databaseId": 3,
            "workflowName": "Atlas Verify",
            "event": "push",
            "headSha": execute_mission["expected_head"],
            "status": "completed",
            "conclusion": "success",
        },
        {
            "databaseId": 4,
            "workflowName": "Atlas Verify",
            "event": "pull_request",
            "headSha": "3333333333333333333333333333333333333333",
            "status": "completed",
            "conclusion": "success",
        },
    ],
    workflow_rules,
    execute_mission["expected_head"],
)
if newer_run["Atlas Verify"]["databaseId"] != 2:
    add_error("workflow selection did not enforce exact name/event/head with newer-run precedence")


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


clock = FakeClock()
success_runs = [
    {
        "databaseId": 2,
        "workflowName": "Atlas Verify",
        "event": "pull_request",
        "headSha": execute_mission["expected_head"],
        "status": "completed",
        "conclusion": "success",
    }
]
gate = contract.wait_for_required_workflows(
    paths,
    workflow_rules,
    lambda: success_runs,
    head_sha=execute_mission["expected_head"],
    sleep=clock.sleep,
    monotonic=clock.monotonic,
    poll_seconds=1,
)
if gate["status"] != "PASS":
    add_error("successful applicable workflow gate did not pass")

clock = FakeClock()
expect_raises(
    contract.WorkflowGateError,
    lambda: contract.wait_for_required_workflows(
        paths,
        workflow_rules,
        lambda: [],
        head_sha=execute_mission["expected_head"],
        sleep=clock.sleep,
        monotonic=clock.monotonic,
        poll_seconds=1,
    ),
    "missing applicable workflow did not fail within bounded appearance grace",
)

clock = FakeClock()
queued_run = [
    {
        "databaseId": 2,
        "workflowName": "Atlas Verify",
        "event": "pull_request",
        "headSha": execute_mission["expected_head"],
        "status": "in_progress",
        "conclusion": None,
    }
]
expect_raises(
    contract.WorkflowGateError,
    lambda: contract.wait_for_required_workflows(
        paths,
        workflow_rules,
        lambda: queued_run,
        head_sha=execute_mission["expected_head"],
        sleep=clock.sleep,
        monotonic=clock.monotonic,
        poll_seconds=1,
    ),
    "incomplete applicable workflow did not fail on completion timer",
)

failed_run = [
    {
        "databaseId": 2,
        "workflowName": "Atlas Verify",
        "event": "pull_request",
        "headSha": execute_mission["expected_head"],
        "status": "completed",
        "conclusion": "failure",
    }
]
expect_raises(
    contract.WorkflowGateError,
    lambda: contract.wait_for_required_workflows(
        paths,
        workflow_rules,
        lambda: failed_run,
        head_sha=execute_mission["expected_head"],
    ),
    "failed applicable workflow did not fail closed",
)

duplicate_rules = [workflow_rules[0], copy.deepcopy(workflow_rules[0])]
expect_raises(
    contract.OathbringerContractError,
    lambda: contract.resolve_workflow_applicability(paths, duplicate_rules),
    "duplicate workflow-rule rejection failed",
)

with tempfile.TemporaryDirectory() as temp_dir:
    receipt_path = Path(temp_dir) / "receipt.json"
    write = contract.atomic_write_json_with_sha256(receipt_path, {"result": "PASS"})
    observed = receipt_path.read_bytes()
    digest = __import__("hashlib").sha256(observed).hexdigest()
    if digest != write["receipt_sha256"]:
        add_error("receipt SHA-256 readback mismatch")
    sidecar = Path(write["sidecar_path"]).read_text("ascii")
    if not sidecar.startswith(f"{digest}  receipt.json"):
        add_error("receipt SHA-256 sidecar content mismatch")

    calls = {"count": 0}

    def flaky_replace(source: Path, destination: Path) -> None:
        calls["count"] += 1
        if calls["count"] == 1:
            exc = PermissionError("simulated Windows replace lock")
            exc.winerror = 32
            raise exc
        os.replace(source, destination)

    retry_path = Path(temp_dir) / "retry-receipt.json"
    contract.atomic_write_json_with_sha256(
        retry_path,
        {"result": "PASS"},
        replace=flaky_replace,
        sleep=lambda _seconds: None,
    )
    if calls["count"] != 3:
        add_error("bounded replace retry did not retry only the transient JSON replace")

json_run = subprocess.run(
    [
        sys.executable,
        "-S",
        "-B",
        str(contract_path),
        "--mission",
        str(ROOT / "examples" / "build.example.json"),
        "--audit-only",
        "--json",
    ],
    check=False,
    capture_output=True,
    text=True,
)
if json_run.returncode != 0:
    add_error(f"JSON mode failed: {json_run.stderr or json_run.stdout}")
else:
    try:
        parsed = json.loads(json_run.stdout)
        if parsed.get("change_method") != "OATHBRINGER":
            add_error("JSON mode did not preserve parseable structured result")
    except json.JSONDecodeError as exc:
        add_error(f"JSON mode was not parseable: {exc}")
    if "ATLAS SWORD" in json_run.stdout:
        add_error("JSON mode included terminal decoration")

byproducts = []
for path in ROOT.rglob("*"):
    if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}:
        byproducts.append(str(path.relative_to(ROOT)))
if byproducts:
    add_error(f"runtime byproducts present: {byproducts}")

if errors:
    print("STATIC CHECKS: FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("STATIC CHECKS: PASS")
print(f"PowerShell files checked: {len(ps_files)}")
print(f"Mission examples checked: {len(examples)}")
print("Oathbringer contract fixtures: PASS")
print("Schema 1.2 / receipt / workflow timer fixtures: PASS")
