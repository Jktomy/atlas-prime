from __future__ import annotations

from pathlib import Path
from typing import Any

from oathbringer_core import (
    CHANGE_METHOD, EXECUTION_ENVIRONMENT, FORGE_STANDARD, FORMAT_VERSION,
    OPERATOR_INTERFACE, RUNTIME_MODE, ExecutionContext, _require, validate_mission,
)
from oathbringer_support import verify_manifest_if_present, wait_for_required_workflows
from oathbringer_tree import (
    build_tree_elements, changed_paths_between, declared_changed_paths,
    _verify_changed_paths, _verify_pr_identity,
)

def _enter(context: ExecutionContext, stage: str, percent: int, message: str, json_mode: bool) -> None:
    context.ledger.enter(stage, percent, message)
    if not json_mode:
        print(f'[{percent:>3}%] {stage} — {message}', flush=True)

def _complete(context: ExecutionContext, detail: str, json_mode: bool) -> None:
    context.ledger.complete(detail)
    if not json_mode:
        print(f'      ✓ {detail}', flush=True)

def execute_source_change(mission: dict[str, Any], package_root: Path, client: Any, context: ExecutionContext, *, json_mode: bool) -> dict[str, Any]:
    lane = mission['lane']
    _enter(context, 'LIVE_IDENTITY', 10, 'verify exact repository, base, branch, and pull request state', json_mode)
    context.github_called = True
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
    _complete(context, 'live identity and exact heads verified', json_mode)
    _enter(context, 'TREE_READBACK', 22, 'read exact base and candidate trees', json_mode)
    reference_tree_sha, reference_tree = client.get_tree_for_commit(mission['expected_base'])
    candidate_tree_sha, _candidate_tree = client.get_tree_for_commit(parent_sha)
    _complete(context, f'reference tree {reference_tree_sha}; parent tree {candidate_tree_sha}', json_mode)
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
        pr = client.create_pull_request(mission['branch'], mission['base_branch'], mission['pull_request_contract'])
    else:
        client.update_ref(mission['branch'], commit_sha)
        pr = client.get_pull_request(mission['pull_request'])
    pr_number = int(pr['number'])
    context.remote_state.update({'pull_request': pr_number, 'branch': mission['branch'], 'branch_head': commit_sha})
    _complete(context, f"draft pull request #{pr_number} bound to {mission['branch']}", json_mode)
    _enter(context, 'REMOTE_READBACK', 84, 'read back exact branch, commit, pull request, and changed files', json_mode)
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
    workflow_gate = wait_for_required_workflows(client, changed_paths, mission['workflow_rules'], commit_sha)
    _complete(context, 'all applicable workflows passed or were classified not applicable', json_mode)
    _enter(context, 'STOP_BOUNDARY', 100, 'stop with the candidate isolated in the pull request', json_mode)
    _complete(context, str(mission['stop_boundary']), json_mode)
    return {'result': 'PASS', 'status': f'OATHBRINGER_{lane}_PASS', 'lane': lane, 'repository': mission['repository'], 'branch': mission['branch'], 'pull_request': pr_number, 'commit_sha': commit_sha, 'expected_base': mission['expected_base'], 'prior_head': mission.get('expected_head'), 'changed_paths': changed_paths, 'payload_blobs': payload_blobs, 'workflow_gate': workflow_gate, 'stop_boundary': mission['stop_boundary']}

def execute_merge(mission: dict[str, Any], client: Any, context: ExecutionContext, *, json_mode: bool) -> dict[str, Any]:
    _enter(context, 'LIVE_IDENTITY', 15, 'verify the exact independently audited pull request head', json_mode)
    context.github_called = True
    pr = client.get_pull_request(mission['pull_request'])
    _verify_pr_identity(mission, pr)
    files = client.list_pull_request_files(mission['pull_request'])
    changed_paths = _verify_changed_paths(mission, [str(item['filename']) for item in files])
    _complete(context, f"pull request #{mission['pull_request']} exact head verified", json_mode)
    _enter(context, 'WORKFLOW_GATE', 45, 'verify all applicable exact-head workflows', json_mode)
    workflow_gate = wait_for_required_workflows(client, changed_paths, mission['workflow_rules'], mission['expected_head'])
    _complete(context, 'applicable workflow gate is green', json_mode)
    _enter(context, 'INDEPENDENT_AUDIT', 65, 'bind the GREEN independent audit receipt', json_mode)
    audit = mission['independent_audit']
    _require(audit['exact_head'] == mission['expected_head'], 'independent audit head mismatch')
    _complete(context, f"GREEN audit bound at {audit['exact_head']}", json_mode)
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
    base_ref = client.get_ref(mission['base_branch'])
    _require(base_ref is not None, 'base branch disappeared after merge')
    context.remote_state.update({'pull_request': mission['pull_request'], 'merge_sha': merge_sha, 'base_head': base_ref['object']['sha']})
    _complete(context, f"merged state and {mission['base_branch']} read back", json_mode)
    _enter(context, 'STOP_BOUNDARY', 100, 'stop after merged-main readback', json_mode)
    _complete(context, str(mission['stop_boundary']), json_mode)
    return {'result': 'PASS', 'status': 'OATHBRINGER_EXECUTE_PASS', 'lane': 'EXECUTE', 'repository': mission['repository'], 'pull_request': mission['pull_request'], 'audited_head': mission['expected_head'], 'merge_sha': merge_sha, 'base_head': base_ref['object']['sha'], 'changed_paths': changed_paths, 'workflow_gate': workflow_gate, 'stop_boundary': mission['stop_boundary']}

def execute_mission(mission: dict[str, Any], package_root: Path, client: Any, *, json_mode: bool=False, context: ExecutionContext | None=None) -> tuple[dict[str, Any], ExecutionContext]:
    context = context or ExecutionContext()
    _enter(context, 'PACKAGE_INTEGRITY', 3, 'verify carrier manifest when present', json_mode)
    manifest_verified = verify_manifest_if_present(package_root)
    _complete(context, f'package manifest verified={manifest_verified}', json_mode)
    _enter(context, 'MISSION_CONTRACT', 6, 'validate production mission and authority capsule', json_mode)
    validate_mission(mission)
    _complete(context, 'production mission contract validated', json_mode)
    if mission['lane'] == 'EXECUTE':
        result = execute_merge(mission, client, context, json_mode=json_mode)
    else:
        result = execute_source_change(mission, package_root, client, context, json_mode=json_mode)
    result.update({'format_version': FORMAT_VERSION, 'change_method': CHANGE_METHOD, 'execution_environment': EXECUTION_ENVIRONMENT, 'operator_interface': OPERATOR_INTERFACE, 'runtime_mode': RUNTIME_MODE, 'forge_standard': FORGE_STANDARD, 'manifest_verified': manifest_verified, 'stage_ledger': context.ledger.as_dict(), 'completion_flags': {'github_called': context.github_called, 'mutation_performed': context.mutation_performed, 'automatic_retry': False, 'automatic_rollback': False, 'token_persisted': False}})
    return (result, context)
