from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Sequence

from oathbringer_core import (
    OathbringerError, ReceiptWriteError, WorkflowGateError, _require,
    _safe_relative_path, _validate_workflow_rule, _unique_strings,
)

def github_path_matches(path: str, pattern: str) -> bool:
    path = path.replace('\\', '/').lstrip('./')
    pattern = pattern.replace('\\', '/').lstrip('./')
    expression = ''
    index = 0
    while index < len(pattern):
        if pattern[index:index + 3] == '**/':
            expression += '(?:.*/)?'
            index += 3
        elif pattern[index:index + 2] == '**':
            expression += '.*'
            index += 2
        elif pattern[index] == '*':
            expression += '[^/]*'
            index += 1
        elif pattern[index] == '?':
            expression += '[^/]'
            index += 1
        else:
            expression += re.escape(pattern[index])
            index += 1
    return re.fullmatch(expression, path) is not None

def resolve_workflow_applicability(changed_paths: Sequence[str], workflow_rules: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    normalized = sorted({str(path).replace('\\', '/').lstrip('./') for path in changed_paths})
    for index, rule in enumerate(workflow_rules):
        _validate_workflow_rule(rule, index)
        name = str(rule['name'])
        _require(name not in result, f'duplicate workflow rule: {name}')
        patterns = rule.get('pull_request_paths')
        match: tuple[str, str] | None = None
        if patterns is not None:
            for path in normalized:
                for pattern in patterns:
                    if github_path_matches(path, str(pattern)):
                        match = (path, str(pattern))
                        break
                if match:
                    break
        applicable = patterns is None or match is not None
        result[name] = {'classification': 'REQUIRED' if applicable else 'NOT_APPLICABLE', 'applicable': applicable, 'reason': 'unfiltered pull_request trigger' if patterns is None else 'changed path matched pull_request path filter' if match else 'no changed path matched pull_request path filters', 'matched_path': None if match is None else match[0], 'matched_pattern': None if match is None else match[1], **rule}
    return result

def wait_for_required_workflows(client: Any, changed_paths: Sequence[str], workflow_rules: Sequence[dict[str, Any]], head_sha: str, *, sleep: Callable[[float], None]=time.sleep, monotonic: Callable[[], float]=time.monotonic, poll_seconds: float=3.0) -> dict[str, Any]:
    applicability = resolve_workflow_applicability(changed_paths, workflow_rules)
    required = {name: rule for name, rule in applicability.items() if rule['applicable']}
    if not required:
        return {'status': 'PASS', 'head_sha': head_sha, 'required': {}, 'not_applicable': applicability}
    started = monotonic()
    first_seen: dict[str, float] = {}
    completed: dict[str, dict[str, Any]] = {}
    while True:
        now = monotonic()
        elapsed = now - started
        runs = client.list_workflow_runs(head_sha)
        latest: dict[str, dict[str, Any]] = {}
        for run in runs:
            name = str(run.get('name') or run.get('workflowName') or '')
            if name not in required:
                continue
            if str(run.get('event') or '') != 'pull_request':
                continue
            if str(run.get('head_sha') or run.get('headSha') or '') != head_sha:
                continue
            key = (int(run.get('id') or run.get('databaseId') or 0), int(run.get('run_attempt') or run.get('runAttempt') or 0))
            prior = latest.get(name)
            prior_key = (-1, -1) if prior is None else (int(prior.get('id') or prior.get('databaseId') or 0), int(prior.get('run_attempt') or prior.get('runAttempt') or 0))
            if key >= prior_key:
                latest[name] = run
        for name, rule in required.items():
            run = latest.get(name)
            if run is None:
                if elapsed >= float(rule['appearance_grace_seconds']):
                    raise WorkflowGateError(f'required workflow did not appear for exact head: {name}')
                continue
            first_seen.setdefault(name, now)
            if str(run.get('status') or '').lower() == 'completed':
                if run.get('conclusion') != rule['expected_conclusion']:
                    raise WorkflowGateError(f"required workflow failed: {name} -> {run.get('conclusion')!r}")
                completed[name] = run
            elif now - first_seen[name] >= float(rule['completion_timeout_seconds']):
                raise WorkflowGateError(f'required workflow timed out: {name}')
        if len(completed) == len(required):
            return {'status': 'PASS', 'head_sha': head_sha, 'required': {name: {'rule': required[name], 'run': completed[name]} for name in sorted(required)}, 'not_applicable': {name: item for name, item in applicability.items() if not item['applicable']}, 'elapsed_seconds': elapsed}
        sleep(poll_seconds)

def atomic_write_json_with_sha256(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + '\n'
    token = f'{os.getpid()}-{time.time_ns()}'
    temp = destination.with_name(f'.{destination.name}.{token}.tmp')
    sidecar = destination.with_name(f'{destination.name}.sha256')
    side_temp = sidecar.with_name(f'.{sidecar.name}.{token}.tmp')
    try:
        temp.write_text(text, encoding='utf-8', newline='\n')
        os.replace(temp, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        side_temp.write_text(f'{digest}  {destination.name}\n', encoding='ascii', newline='\n')
        os.replace(side_temp, sidecar)
    except OSError as exc:
        for item in (temp, side_temp):
            try:
                item.unlink(missing_ok=True)
            except OSError:
                pass
        raise ReceiptWriteError(f'receipt write failed: {exc}') from exc
    return {'receipt_path': str(destination), 'receipt_sha256': digest, 'sidecar_path': str(sidecar)}

def verify_manifest_if_present(package_root: Path) -> bool:
    path = package_root / 'MANIFEST.json'
    if not path.is_file():
        return False
    manifest = json.loads(path.read_text(encoding='utf-8'))
    for item in manifest.get('files', []):
        relative = _safe_relative_path(item.get('path'), 'manifest path')
        member = (package_root / relative).resolve()
        _require(member.is_file(), f'manifest member missing: {relative}')
        _require(hashlib.sha256(member.read_bytes()).hexdigest() == item.get('sha256'), f'manifest hash mismatch: {relative}')
        _require(member.stat().st_size == int(item.get('size')), f'manifest size mismatch: {relative}')
    return True
