from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from oathbringer_core import (
    CHANGE_METHOD, EXECUTION_ENVIRONMENT, FORGE_STANDARD, FORMAT_VERSION,
    OPERATOR_INTERFACE, RUNTIME_MODE, ExecutionContext, _require, validate_mission,
)
from oathbringer_support import (
    verify_package_member, verify_required_manifest, verify_workflow_source_blobs,
    wait_for_required_workflows,
)
from oathbringer_tree import (
    build_tree_elements, changed_paths_between, declared_changed_paths,
    _verify_changed_paths, _verify_pr_identity,
)


REPAIR_READBACK_TIMEOUT_SECONDS = 10.0
REPAIR_READBACK_POLL_SECONDS = 0.25


def _enter(context: ExecutionContext, stage: str, percent: int, message: str, json_mode: bool) -> None:
    context.ledger.enter(stage, percent, message)
    if json_mode:
        return
    if context.console is not None:
        context.console.stage_enter(stage, percent, message)
    else:
        print(f'[{percent:>3}%] {stage} — {message}', flush=True)


def _complete(context: ExecutionContext, detail: str, json_mode: bool) -> None:
    context.ledger.complete(detail)
    if json_mode:
        return
    if context.console is not None:
        context.console.stage_complete(detail)
    else:
        print(f'      ✓ {detail}', flush=True)


def _verify_authenticated_operator(mission: dict[str, Any], client: Any, context: ExecutionContext) -> str:
    user = client.get_authenticated_user()
    login = str(user.get('login') or '')
    expected = str(mission['authorization']['github_login'])
    _require(login.casefold() == expected.casefold(), f'authenticated GitHub login mismatch: expected {expected}; observed {login or "<empty>"}')
    context.remote_state['authenticated_github_login'] = login
    return login


def _wait_for_repair_head_convergence(
    mission: dict[str, Any],
    client: Any,
    context: ExecutionContext,
    *,
    commit_sha: str,
    pr_number: int,
) -> dict[str, Any]:
    """Wait briefly for GitHub's PR projection to catch the updated branch ref."""

    deadline = time.monotonic() + REPAIR_READBACK_TIMEOUT_SECONDS
    attempts = 0
    branch_head: str | None = None
    pr_head: str | None = None
    while True:
        attempts += 1
        branch_ref = client.get_ref(mission['branch'])
        branch_head = None if branch_ref is None else str(branch_ref['object']['sha'])
        pr = client.get_pull_request(pr_number)
        pr_head = str(pr['head']['sha'])
        context.remote_state.update({
            'repair_readback_attempts': attempts,
            'repair_readback_branch_head': branch_head,
            'repair_readback_pr_head': pr_head,
            'repair_readback_timeout_seconds': REPAIR_READBACK_TIMEOUT_SECONDS,
        })
        if branch_head == commit_sha and pr_head == commit_sha:
            context.remote_state['repair_readback_converged'] = True
            return pr
        if time.monotonic() >= deadline:
            context.remote_state['repair_readback_converged'] = False
            _require(
                False,
                f'REPAIR branch/PR head did not converge to {commit_sha} within '
                f'{REPAIR_READBACK_TIMEOUT_SECONDS:.3f}s; '
                f'branch={branch_head or "<missing>"}; pr={pr_head or "<missing>"}',
            )
        time.sleep(REPAIR_READBACK_POLL_SECONDS)


def execute_source_change(mission: dict[str, Any], package_root: Path, client: Any, context: ExecutionContext, *, json_mode: bool) -> dict[str, Any]:
    lane = mission['lane']
    _enter(context, 'LIVE_IDENTITY', 10, 'verify authenticated operator, repository, base, branch, and pull request state', json_mode)
    context.github_called = True
    login = _verify_authenticated_operator(mission, client, context)
    base_ref = client.get_ref(mission['base_branch'])
    _require(base_ref is not None, 'base branch does not exist')
    _require(base_ref['object']['sha'] == mission['expected_base'], 'base branch drift')
    if lane == 'BUILD':
        _require(client.get_ref(mission['branch']) is None, 'BUILD branch already exists')
        _require(not client.find_open_pull_requests(mission['branch'], mission['base_branch']), 'BUILD pull request already exists')
        parent_sha = mission['expected_base']
    else:
        branch_ref = client.get_ref(mission['branch'])
        _require(branch_ref is not None, 'REPAIR branch does not exist')
        _require(branch_ref['object']['sha'] == mission['expected_head'], 'REPAIR branch head drift')
        existing_pr = client.get_pull_request(mission['pull_request'])
        _verify_pr_identity(mission, existing_pr)
        parent_sha = mission['expected_head']
    _complete(context, f'authenticated as {login}; live identity and exact heads verified', json_mode)

    _enter(context, 'TREE_READBACK', 22, 'read exact base and candidate trees and bind workflow source blobs', json_mode)
    reference_tree_sha, reference_tree = client.get_tree_for_commit(mission['expected_base'])
    candidate_tree_sha, _candidate_tree = client.get_tree_for_commit(parent_sha)
    verify_workflow_source_blobs(mission['workflow_rules'], reference_tree)
    _complete(context, f'reference tree {reference_tree_sha}; parent tree {candidate_tree_sha}; workflow sources bound', json_mode)

    _enter(context, 'PAYLOAD_AND_BLOBS', 38, 'verify payload hashes and create exact GitHub blobs', json_mode)
    elements, payload_blobs = build_tree_elements(mission, package_root, reference_tree, client)
    context.mutation_performed = bool(payload_blobs)
    _complete(context, f'prepared {len(elements)} tree operations', json_mode)

    _enter(context, 'CANDIDATE_TREE', 52, 'construct and verify the complete candidate tree', json_mode)
    new_tree_sha = client.create_tree(candidate_tree_sha, elements)
    context.mutation_performed = True
    context.remote_state['candidate_tree_sha'] = new_tree_sha
    _, final_tree = client.get_tree(new_tree_sha)
    expected_paths = declared_changed_paths(mission['declared_paths'])
    observed_paths = changed_paths_between(reference_tree, final_tree)
    _require(observed_paths == expected_paths, f'candidate tree path mismatch: expected={expected_paths}; observed={observed_paths}')
    for path, blob in payload_blobs.items():
        _require(final_tree.get(path, {}).get('sha') == blob, f'candidate payload readback mismatch: {path}')
    _complete(context, f'candidate tree {new_tree_sha} matches declared final path set', json_mode)

    _enter(context, 'COMMIT', 64, 'create one single-parent GitHub commit', json_mode)
    commit_sha = client.create_commit(mission['commit_message'], new_tree_sha, parent_sha)
    context.remote_state['commit_sha'] = commit_sha
    _complete(context, f'created commit {commit_sha}', json_mode)

    _enter(context, 'BRANCH_AND_PR', 74, 'publish by fast-forward branch operation and bind the draft pull request', json_mode)
    if lane == 'BUILD':
        client.create_ref(mission['branch'], commit_sha)
        context.remote_state.update({'branch': mission['branch'], 'branch_head': commit_sha})
        pr = client.create_pull_request(mission['branch'], mission['base_branch'], mission['pull_request_contract'])
        pr_number = int(pr['number'])
        context.remote_state['pull_request'] = pr_number
    else:
        client.update_ref(mission['branch'], commit_sha)
        pr_number = int(mission['pull_request'])
        context.remote_state.update({'branch': mission['branch'], 'branch_head': commit_sha, 'pull_request': pr_number})
    _complete(context, f"draft pull request #{pr_number} bound to {mission['branch']}", json_mode)

    _enter(context, 'REMOTE_READBACK', 84, 'read back exact branch, commit, pull request, and changed files', json_mode)
    if lane == 'REPAIR':
        pr = _wait_for_repair_head_convergence(
            mission,
            client,
            context,
            commit_sha=commit_sha,
            pr_number=pr_number,
        )
    else:
        branch_ref = client.get_ref(mission['branch'])
        _require(branch_ref is not None and branch_ref['object']['sha'] == commit_sha, 'branch readback mismatch')
        pr = client.get_pull_request(pr_number)
        _require(str(pr['head']['sha']) == commit_sha, 'pull request head readback mismatch')
    _require(pr.get('state') == 'open', 'pull request did not remain open')
    _require(pr.get('draft') is True, 'source-changing Oathbringer must stop at a draft pull request')
    files = client.list_pull_request_files(pr_number)
    changed_paths = _verify_changed_paths(mission, [str(item['filename']) for item in files])
    _complete(context, f'remote readback verified at {commit_sha}', json_mode)

    _enter(context, 'WORKFLOW_GATE', 94, 'wait only for path-applicable exact-head workflows', json_mode)
    workflow_gate = wait_for_required_workflows(client, changed_paths, mission['workflow_rules'], commit_sha, progress=None if context.console is None else context.console.workflow_heartbeat)
    _complete(context, 'all applicable workflows passed or were classified not applicable', json_mode)
    _enter(context, 'STOP_BOUNDARY', 100, 'stop with the candidate isolated in the pull request', json_mode)
    _complete(context, str(mission['stop_boundary']), json_mode)
    return {'result': 'PASS', 'status': f'OATHBRINGER_{lane}_PASS', 'lane': lane, 'repository': mission['repository'], 'authenticated_github_login': login, 'branch': mission['branch'], 'pull_request': pr_number, 'commit_sha': commit_sha, 'expected_base': mission['expected_base'], 'prior_head': mission.get('expected_head'), 'changed_paths': changed_paths, 'payload_blobs': payload_blobs, 'workflow_gate': workflow_gate, 'stop_boundary': mission['stop_boundary']}


def execute_merge(mission: dict[str, Any], package_root: Path, client: Any, context: ExecutionContext, *, json_mode: bool) -> dict[str, Any]:
    _enter(context, 'LIVE_IDENTITY', 15, 'verify authenticated operator and exact independently audited pull request head', json_mode)
    context.github_called = True
    login = _verify_authenticated_operator(mission, client, context)
    pr = client.get_pull_request(mission['pull_request'])
    _verify_pr_identity(mission, pr)
    files = client.list_pull_request_files(mission['pull_request'])
    changed_paths = _verify_changed_paths(mission, [str(item['filename']) for item in files])
    _, base_tree = client.get_tree_for_commit(mission['expected_base'])
    verify_workflow_source_blobs(mission['workflow_rules'], base_tree)
    _complete(context, f'authenticated as {login}; pull request #{mission["pull_request"]} exact head and workflow sources verified', json_mode)

    _enter(context, 'WORKFLOW_GATE', 45, 'verify all applicable exact-head workflows', json_mode)
    workflow_gate = wait_for_required_workflows(client, changed_paths, mission['workflow_rules'], mission['expected_head'], progress=None if context.console is None else context.console.workflow_heartbeat)
    _complete(context, 'applicable workflow gate is green', json_mode)

    _enter(context, 'INDEPENDENT_AUDIT', 65, 'verify and bind the packaged GREEN independent audit receipt', json_mode)
    audit = mission['independent_audit']
    audit_path = verify_package_member(package_root, audit['receipt_path'], audit['receipt_sha256'])
    audit_receipt = json.loads(audit_path.read_text(encoding='utf-8'))
    _require(audit_receipt.get('verdict') == 'GREEN', 'packaged independent audit receipt is not GREEN')
    _require(audit_receipt.get('exact_head') == mission['expected_head'], 'packaged independent audit receipt head mismatch')
    _complete(context, f"GREEN audit receipt bound at {audit['exact_head']}", json_mode)

    if pr.get('draft') is True:
        _enter(context, 'READY_TRANSITION', 76, 'mark the exact audited pull request ready', json_mode)
        client.mark_ready(str(pr['node_id']))
        context.mutation_performed = True
        context.remote_state.update({'pull_request': mission['pull_request'], 'ready_transition': True})
        pr = client.get_pull_request(mission['pull_request'])
        _require(pr.get('draft') is False, 'pull request remained draft after ready transition')
        _require(str(pr['head']['sha']) == mission['expected_head'], 'head moved during ready transition')
        _complete(context, 'pull request marked ready without head movement', json_mode)

    _enter(context, 'MERGE', 88, 'merge only the exact independently audited head', json_mode)
    merge = client.merge_pull_request(mission['pull_request'], mission['expected_head'], mission.get('merge_method', 'squash'))
    _require(merge.get('merged') is True, f"GitHub refused merge: {merge.get('message')}")
    context.mutation_performed = True
    merge_sha = str(merge['sha'])
    context.remote_state.update({'pull_request': mission['pull_request'], 'merge_sha': merge_sha})
    _complete(context, f'merged as {merge_sha}', json_mode)

    _enter(context, 'MERGED_READBACK', 97, 'read back merged pull request and canonical branch', json_mode)
    pr = client.get_pull_request(mission['pull_request'])
    _require(pr.get('merged') is True or pr.get('merged_at') is not None, 'pull request merge readback failed')
    if pr.get('merge_commit_sha') is not None:
        _require(str(pr['merge_commit_sha']) == merge_sha, 'pull request merge SHA readback mismatch')
    base_ref = client.get_ref(mission['base_branch'])
    _require(base_ref is not None, 'base branch disappeared after merge')
    context.remote_state.update({'pull_request': mission['pull_request'], 'merge_sha': merge_sha, 'base_head': base_ref['object']['sha']})
    _complete(context, f"merged state and {mission['base_branch']} read back", json_mode)
    _enter(context, 'STOP_BOUNDARY', 100, 'stop after merged-main readback', json_mode)
    _complete(context, str(mission['stop_boundary']), json_mode)
    return {'result': 'PASS', 'status': 'OATHBRINGER_EXECUTE_PASS', 'lane': 'EXECUTE', 'repository': mission['repository'], 'authenticated_github_login': login, 'pull_request': mission['pull_request'], 'audited_head': mission['expected_head'], 'merge_sha': merge_sha, 'base_head': base_ref['object']['sha'], 'changed_paths': changed_paths, 'workflow_gate': workflow_gate, 'stop_boundary': mission['stop_boundary']}


def execute_mission(mission: dict[str, Any], package_root: Path, client: Any, *, mission_relative_path: str | None=None, json_mode: bool=False, context: ExecutionContext | None=None) -> tuple[dict[str, Any], ExecutionContext]:
    context = context or ExecutionContext()
    _enter(context, 'MISSION_CONTRACT', 3, 'validate production mission and authority capsule', json_mode)
    validate_mission(mission)
    _complete(context, 'production mission contract validated', json_mode)

    _enter(context, 'PACKAGE_INTEGRITY', 6, 'verify required carrier manifest and all bound mission evidence', json_mode)
    _require(bool(mission_relative_path), 'production mission path must be bound to the package manifest')
    manifest = verify_required_manifest(package_root)
    members = set(manifest['members'])
    required_members = {str(mission_relative_path), mission['lessons_register']['path']}
    required_members.update(str(item['payload_path']) for item in mission['declared_paths'] if item.get('payload_path'))
    if mission['lane'] == 'EXECUTE':
        required_members.add(mission['independent_audit']['receipt_path'])
    missing = sorted(required_members - members)
    _require(not missing, f'bound package members are absent from MANIFEST.json: {missing}')
    mission_file = verify_package_member(package_root, str(mission_relative_path), next(item['sha256'] for item in json.loads((package_root / 'MANIFEST.json').read_text(encoding='utf-8'))['files'] if item['path'] == mission_relative_path))
    _require(json.loads(mission_file.read_text(encoding='utf-8')) == mission, 'invoked mission bytes do not match the manifest-bound mission')
    lessons = mission['lessons_register']
    verify_package_member(package_root, lessons['path'], lessons['source_sha256'])
    _complete(context, f"manifest verified with {manifest['member_count']} members; mission, payload, lessons, and audit evidence bound", json_mode)

    if mission['lane'] == 'EXECUTE':
        result = execute_merge(mission, package_root, client, context, json_mode=json_mode)
    else:
        result = execute_source_change(mission, package_root, client, context, json_mode=json_mode)
    result.update({'format_version': FORMAT_VERSION, 'change_method': CHANGE_METHOD, 'execution_environment': EXECUTION_ENVIRONMENT, 'operator_interface': OPERATOR_INTERFACE, 'runtime_mode': RUNTIME_MODE, 'forge_standard': FORGE_STANDARD, 'manifest_verified': True, 'manifest_member_count': manifest['member_count'], 'mission_manifest_path': mission_relative_path, 'stage_ledger': context.ledger.as_dict(), 'completion_flags': {'github_called': context.github_called, 'mutation_performed': context.mutation_performed, 'automatic_retry': False, 'automatic_rollback': False, 'token_persisted': False}})
    return (result, context)
