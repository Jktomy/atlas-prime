from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

FORMAT_VERSION = "2.0"
CHANGE_METHOD = "OATHBRINGER"
EXECUTION_ENVIRONMENT = "GITHUB"
OPERATOR_INTERFACE = "POWERSHELL"
FRAMEWORK_STATE = "PILOT_READY_PROOF_PENDING"
RUNTIME_MODE = "PRODUCTION_GITHUB_NATIVE"
FORGE_STANDARD = "SWORD_FORGE_STANDARD_V1"
LESSONS_SCHEMA = "prime-sword-lessons-v1"

class OathbringerError(RuntimeError):
    """Base production Oathbringer error."""

class GitHubApiError(OathbringerError):
    """GitHub API request failed."""

class WorkflowGateError(OathbringerError):
    """A required workflow did not appear, complete, or pass."""

class ReceiptWriteError(OathbringerError):
    """A receipt could not be written atomically."""

@dataclass
class StageLedger:
    current_stage: str = 'START'
    last_completed_stage: str = 'NONE'
    progress_percent: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    def enter(self, stage: str, progress_percent: int, message: str) -> None:
        if not stage or not 0 <= progress_percent <= 100:
            raise OathbringerError('invalid stage entry')
        self.current_stage = stage
        self.progress_percent = progress_percent
        self.history.append({'event': 'ENTER', 'stage': stage, 'progress_percent': progress_percent, 'message': message})

    def complete(self, detail: str) -> None:
        self.last_completed_stage = self.current_stage
        self.history.append({'event': 'COMPLETE', 'stage': self.current_stage, 'progress_percent': self.progress_percent, 'detail': detail})

    def fail(self, detail: str) -> None:
        self.history.append({'event': 'FAIL', 'stage': self.current_stage, 'progress_percent': self.progress_percent, 'detail': detail})

    def as_dict(self) -> dict[str, Any]:
        return {'current_stage': self.current_stage, 'last_completed_stage': self.last_completed_stage, 'progress_percent': self.progress_percent, 'history': self.history}

@dataclass
class ExecutionContext:
    ledger: StageLedger = field(default_factory=StageLedger)
    github_called: bool = False
    mutation_performed: bool = False
    remote_state: dict[str, Any] = field(default_factory=dict)
    console: Any | None = field(default=None, repr=False, compare=False)

def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OathbringerError(message)

def _sha1(value: Any, field_name: str, *, optional: bool=False) -> str | None:
    if value is None and optional:
        return None
    text = str(value or '')
    _require(re.fullmatch('[0-9a-f]{40}', text) is not None, f'{field_name} must be a lowercase SHA-1')
    return text

def _sha256(value: Any, field_name: str) -> str:
    text = str(value or '')
    _require(re.fullmatch('[0-9a-f]{64}', text) is not None, f'{field_name} must be a lowercase SHA-256')
    return text

def _safe_relative_path(value: Any, field_name: str) -> str:
    original = str(value or '')
    _require(bool(original), f'{field_name} must not be empty')
    _require('\\' not in original, f'{field_name} must use forward slashes')
    _require(not original.startswith('/'), f'{field_name} must be relative')
    parts = original.split('/')
    _require(all((part not in {'', '.', '..'} for part in parts)), f'{field_name} must not contain empty, . or .. segments')
    normalized = '/'.join(parts)
    _require(bool(normalized), f'{field_name} must not be empty')
    return normalized

def _safe_branch(value: Any, field_name: str='branch') -> str:
    branch = str(value or '')
    _require(bool(branch), f'{field_name} must not be empty')
    _require(not branch.startswith(('/', '-')), f'{field_name} has an invalid prefix')
    _require('..' not in branch and ' ' not in branch and ('~' not in branch), f'{field_name} is unsafe')
    _require(not branch.endswith(('/', '.')) and '@{' not in branch, f'{field_name} is unsafe')
    return branch

def _unique_strings(values: Any, field_name: str) -> list[str]:
    _require(isinstance(values, list), f'{field_name} must be an array')
    result = [str(item) for item in values]
    _require(all(result), f'{field_name} contains an empty value')
    _require(len(result) == len(set(result)), f'{field_name} contains duplicates')
    return result

def _exact_keys(value: dict[str, Any], allowed: set[str], field_name: str) -> None:
    unknown = sorted(set(value) - allowed)
    _require(not unknown, f'{field_name} contains unknown fields: {unknown}')

def validate_mission(mission: dict[str, Any]) -> None:
    allowed = {'format_version', 'mission_id', 'sword_identity', 'forge_standard', 'package_manifest_required', 'lessons_register', 'lesson_applicability', 'change_method', 'execution_environment', 'operator_interface', 'framework_state', 'runtime_mode', 'lane', 'repository', 'base_branch', 'expected_base', 'expected_head', 'branch', 'pull_request', 'commit_message', 'pull_request_contract', 'declared_paths', 'workflow_rules', 'receipt_contract', 'authorization', 'independent_audit', 'merge_method', 'stop_boundary', 'forbidden_actions'}
    _exact_keys(mission, allowed, 'mission')
    required = {'format_version', 'mission_id', 'sword_identity', 'forge_standard', 'package_manifest_required', 'lessons_register', 'lesson_applicability', 'change_method', 'execution_environment', 'operator_interface', 'framework_state', 'runtime_mode', 'lane', 'repository', 'base_branch', 'expected_base', 'branch', 'declared_paths', 'workflow_rules', 'receipt_contract', 'authorization', 'stop_boundary', 'forbidden_actions'}
    missing = sorted(required - set(mission))
    _require(not missing, f'mission missing required fields: {missing}')
    _require(mission['format_version'] == FORMAT_VERSION, f'format_version must be {FORMAT_VERSION}')
    _require(mission['forge_standard'] == FORGE_STANDARD, f'forge_standard must be {FORGE_STANDARD}')
    _require(mission['package_manifest_required'] is True, 'production package manifest must be required')
    _require(mission['change_method'] == CHANGE_METHOD, 'change_method must be OATHBRINGER')
    _require(mission['execution_environment'] == EXECUTION_ENVIRONMENT, 'execution_environment must be GITHUB')
    _require(mission['operator_interface'] == OPERATOR_INTERFACE, 'operator_interface must be POWERSHELL')
    _require(mission['framework_state'] == FRAMEWORK_STATE, f'framework_state must be {FRAMEWORK_STATE}')
    _require(mission['runtime_mode'] == RUNTIME_MODE, f'runtime_mode must be {RUNTIME_MODE}')
    lane = str(mission['lane'])
    _require(lane in {'BUILD', 'REPAIR', 'EXECUTE'}, 'lane must be BUILD, REPAIR, or EXECUTE')
    _require(re.fullmatch('[^/\\s]+/[^/\\s]+', str(mission['repository'])) is not None, 'repository must be owner/repo')
    _safe_branch(mission['base_branch'], 'base_branch')
    branch = _safe_branch(mission['branch'])
    _require(branch != mission['base_branch'], 'mission branch must not be the base branch')
    _sha1(mission['expected_base'], 'expected_base')
    expected_head = _sha1(mission.get('expected_head'), 'expected_head', optional=True)

    lessons = mission['lessons_register']
    _require(isinstance(lessons, dict), 'lessons_register must be an object')
    _exact_keys(lessons, {'schema_version', 'path', 'source_sha256'}, 'lessons_register')
    _require(lessons.get('schema_version') == LESSONS_SCHEMA, f'lessons register must be {LESSONS_SCHEMA}')
    _safe_relative_path(lessons.get('path'), 'lessons_register.path')
    _sha256(lessons.get('source_sha256'), 'lessons_register.source_sha256')

    applicability = mission['lesson_applicability']
    _require(isinstance(applicability, list) and applicability, 'lesson_applicability must be non-empty')
    seen_lessons: set[str] = set()
    for index, item in enumerate(applicability):
        _require(isinstance(item, dict), f'lesson_applicability[{index}] must be an object')
        _exact_keys(item, {'lesson_id', 'status', 'reason'}, f'lesson_applicability[{index}]')
        lesson_id = str(item.get('lesson_id') or '')
        _require(re.fullmatch('SWORD-L[0-9]{3}', lesson_id) is not None, f'invalid lesson id: {lesson_id}')
        _require(lesson_id not in seen_lessons, f'duplicate lesson classification: {lesson_id}')
        seen_lessons.add(lesson_id)
        status = item.get('status')
        _require(status in {'APPLIED', 'NOT_APPLICABLE'}, f'invalid lesson status for {lesson_id}')
        if status == 'NOT_APPLICABLE':
            _require(bool(str(item.get('reason') or '').strip()), f'{lesson_id} requires a not-applicable reason')

    auth = mission['authorization']
    _require(isinstance(auth, dict), 'authorization must be an object')
    _exact_keys(auth, {'approved_preview', 'execution_authorized', 'authorizer', 'operator', 'github_login'}, 'authorization')
    _require(auth.get('approved_preview') is True, 'approved Preview is required')
    _require(auth.get('execution_authorized') is True, 'execution authorization is required')
    _require(str(auth.get('authorizer') or '').upper() == 'JAYSON', 'authorizer must be JAYSON')
    _require(str(auth.get('operator') or '').upper() == 'JAYSON', 'operator must be JAYSON')
    _require(re.fullmatch('[A-Za-z0-9-]+', str(auth.get('github_login') or '')) is not None, 'authorization.github_login is invalid')

    forbidden = set(_unique_strings(mission['forbidden_actions'], 'forbidden_actions'))
    required_forbidden = {'DIRECT_MAIN', 'FORCE_PUSH', 'SCOPE_WIDENING', 'TOKEN_PERSISTENCE'}
    _require(required_forbidden <= forbidden, f'forbidden_actions must include {sorted(required_forbidden)}')
    receipt = mission['receipt_contract']
    _require(isinstance(receipt, dict), 'receipt_contract must be an object')
    expected_receipt = {'write_on_interrupt': True, 'write_on_failure': True, 'write_on_success': True, 'automatic_retry': False, 'automatic_rollback': False, 'interrupt_exit_code': 130, 'failure_exit_code': 1}
    for key, value in expected_receipt.items():
        _require(receipt.get(key) == value, f'receipt contract mismatch for {key}')

    declared = mission['declared_paths']
    _require(isinstance(declared, list), 'declared_paths must be an array')
    if lane in {'BUILD', 'REPAIR'}:
        _require(bool(declared), 'source-changing lanes require declared_paths')
    seen_targets: set[str] = set()
    seen_sources: set[str] = set()
    allowed_path_keys = {'path', 'operation', 'payload_path', 'payload_sha256', 'source_path', 'source_blob', 'mode'}
    for index, item in enumerate(declared):
        _require(isinstance(item, dict), f'declared_paths[{index}] must be an object')
        _exact_keys(item, allowed_path_keys, f'declared_paths[{index}]')
        path = _safe_relative_path(item.get('path'), f'declared_paths[{index}].path')
        _require(path not in seen_targets, f'duplicate target path: {path}')
        seen_targets.add(path)
        operation = str(item.get('operation') or '')
        _require(operation in {'ADD', 'REPLACE', 'DELETE', 'RENAME', 'MOVE'}, f'invalid operation for {path}')
        if operation in {'ADD', 'REPLACE'}:
            _safe_relative_path(item.get('payload_path'), f'payload_path for {path}')
            _sha256(item.get('payload_sha256'), f'payload_sha256 for {path}')
        if operation in {'REPLACE', 'DELETE', 'RENAME', 'MOVE'}:
            _sha1(item.get('source_blob'), f'source_blob for {path}')
        if operation in {'RENAME', 'MOVE'}:
            source = _safe_relative_path(item.get('source_path'), f'source_path for {path}')
            _require(source != path, f'source and destination must differ: {path}')
            _require(source not in seen_sources, f'duplicate move source: {source}')
            seen_sources.add(source)
            if item.get('payload_path') is not None:
                _safe_relative_path(item.get('payload_path'), f'payload_path for {path}')
                _sha256(item.get('payload_sha256'), f'payload_sha256 for {path}')

    _require(isinstance(mission['workflow_rules'], list), 'workflow_rules must be an array')
    for index, rule in enumerate(mission['workflow_rules']):
        _validate_workflow_rule(rule, index)

    if lane == 'BUILD':
        _require(expected_head is None, 'BUILD expected_head must be null')
        _require(mission.get('pull_request') is None, 'BUILD pull_request must be null')
        pr_contract = mission.get('pull_request_contract')
        _require(isinstance(pr_contract, dict), 'BUILD requires pull_request_contract')
        _require(pr_contract.get('draft') is True, 'BUILD must create a draft pull request')
        _require(bool(str(pr_contract.get('title') or '').strip()), 'pull request title is required')
        _require(bool(str(mission.get('commit_message') or '').strip()), 'commit_message is required')
    elif lane == 'REPAIR':
        _require(expected_head is not None, 'REPAIR expected_head is required')
        _require(isinstance(mission.get('pull_request'), int) and mission['pull_request'] >= 1, 'REPAIR pull_request is required')
        _require(bool(str(mission.get('commit_message') or '').strip()), 'commit_message is required')
    else:
        _require(expected_head is not None, 'EXECUTE expected_head is required')
        _require(isinstance(mission.get('pull_request'), int) and mission['pull_request'] >= 1, 'EXECUTE pull_request is required')
        audit = mission.get('independent_audit')
        _require(isinstance(audit, dict), 'EXECUTE requires independent_audit')
        _exact_keys(audit, {'verdict', 'exact_head', 'receipt_path', 'receipt_sha256'}, 'independent_audit')
        _require(audit.get('verdict') == 'GREEN', 'independent audit verdict must be GREEN')
        _require(audit.get('exact_head') == expected_head, 'independent audit must bind expected_head')
        _safe_relative_path(audit.get('receipt_path'), 'independent_audit.receipt_path')
        _sha256(audit.get('receipt_sha256'), 'independent_audit.receipt_sha256')
        merge_method = str(mission.get('merge_method') or 'squash')
        _require(merge_method in {'merge', 'squash', 'rebase'}, 'invalid merge_method')

def _validate_workflow_rule(rule: Any, index: int) -> None:
    _require(isinstance(rule, dict), f'workflow_rules[{index}] must be an object')
    _exact_keys(rule, {'name', 'event', 'workflow_path', 'workflow_blob', 'appearance_grace_seconds', 'completion_timeout_seconds', 'expected_conclusion', 'pull_request_paths'}, f'workflow_rules[{index}]')
    _require(bool(str(rule.get('name') or '')), f'workflow_rules[{index}].name is required')
    _require(rule.get('event') == 'pull_request', f'workflow_rules[{index}].event must be pull_request')
    path = _safe_relative_path(rule.get('workflow_path'), f'workflow_rules[{index}].workflow_path')
    _require(path.startswith('.github/workflows/'), 'workflow_path must be under .github/workflows')
    _sha1(rule.get('workflow_blob'), f'workflow_rules[{index}].workflow_blob')
    _require(int(rule.get('appearance_grace_seconds', 0)) >= 1, 'appearance grace must be positive')
    _require(int(rule.get('completion_timeout_seconds', 0)) >= 1, 'completion timeout must be positive')
    _require(rule.get('expected_conclusion') == 'success', 'workflow expected_conclusion must be success')
    patterns = rule.get('pull_request_paths')
    if patterns is not None:
        _require(bool(_unique_strings(patterns, f'workflow_rules[{index}].pull_request_paths')), 'path filters must be non-empty')
