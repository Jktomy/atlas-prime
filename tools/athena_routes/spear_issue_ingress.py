from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from tools.candidate_seal.core import build_candidate_seal
from .spear_issue_client import EXECUTE, KEY_REQUEST, PREVIEW, RESUME, RECEIPT_MARKER, REPOSITORY, SpearIssueIngressError, _authorization, _comment, _issue, _main_sha, _mission_manifest, _post, _reconstruct_preview, _reject_request_replay, _trusted_event, _validate_envelope, parse_comment, sha256_bytes, stable_json

def _load_thread_engine() -> tuple[Any, Any, Any, Any]:
    root = Path(__file__).resolve().parents[2]
    thread_engine = root / 'tools' / 'thread-engine'
    if str(thread_engine) not in sys.path:
        sys.path.insert(0, str(thread_engine))
    from spear_bridge.compiler import compile_package
    from production_adapter.adapter import AdapterError
    from production_adapter.resume import execute_sealed_mission, resume_exact_partial
    return (compile_package, AdapterError, execute_sealed_mission, resume_exact_partial)

def _candidate_files(mission: dict[str, Any], output_dir: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for operation in mission['operations']:
        if operation['operation'] == 'DELETE':
            raise SpearIssueIngressError('DELETE is unsupported in Spear Issue R01', 'SPEAR_ISSUE_DELETE_UNSUPPORTED_R01')
        payload = output_dir / 'PAYLOADS' / operation['payload']
        if not payload.is_file() or payload.is_symlink():
            raise SpearIssueIngressError('compiled payload is unavailable', 'COMPILE_OUTPUT_REJECTED')
        result[operation['path']] = payload.read_bytes()
    return result

def _git_tree(base_sha: str, candidate_files: dict[str, bytes], root: Path) -> str:
    checkout = root / 'tree-checkout'
    _run(['git', 'clone', '--no-tags', 'https://github.com/Jktomy/atlas-prime.git', str(checkout)])
    _run(['git', 'checkout', '--detach', base_sha], cwd=checkout)
    if _run(['git', 'status', '--porcelain=v1'], cwd=checkout):
        raise SpearIssueIngressError('read-only tree checkout is dirty', 'DIRTY_CHECKOUT')
    for path, data in candidate_files.items():
        target = checkout / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    _run(['git', 'add', '--', *sorted(candidate_files)], cwd=checkout)
    changed = _run(['git', 'diff', '--cached', '--name-only'], cwd=checkout).splitlines()
    if sorted(changed) != sorted(candidate_files):
        raise SpearIssueIngressError('staged candidate path set mismatch', 'PATH_SET_MISMATCH')
    tree = _run(['git', 'write-tree'], cwd=checkout)
    if not SHA40.fullmatch(tree):
        raise SpearIssueIngressError('candidate Git tree is invalid', 'TREE_REJECTED')
    return tree

def _compile_and_seal(carrier: bytes, body: dict[str, Any], manifest: dict[str, Any], issue_number: int, root: Path) -> dict[str, Any]:
    compile_package, _adapter_error, _execute, _resume = _load_thread_engine()
    package_path = root / 'spear-carrier.zip'
    package_path.write_bytes(carrier)
    output_dir = root / 'compiled'
    thread_engine = Path(__file__).resolve().parents[2] / 'tools' / 'thread-engine'
    if str(thread_engine) not in sys.path:
        sys.path.insert(0, str(thread_engine))
    from production_adapter.protected_paths import direct_spear_path_scope
    with direct_spear_path_scope():
        compile_receipt = compile_package(package_path, package_sha256=body['carrier_sha256'], output_dir=output_dir, disabled_proof=True, compile_only=True, read_only_remote_url='https://github.com/Jktomy/atlas-prime.git')
    mission_path = output_dir / compile_receipt['output_mission_filename']
    mission = json.loads(mission_path.read_text(encoding='utf-8'))
    if mission.get('mission_id') != manifest.get('mission_id') or mission.get('base_sha') != body.get('base_sha'):
        raise SpearIssueIngressError('compiled Mission identity mismatch', 'COMPILED_MISSION_REJECTED')
    if mission.get('branch') == 'main' or not str(mission.get('branch', '')).startswith('source/'):
        raise SpearIssueIngressError('compiled branch intent rejected', 'BRANCH_REJECTED')
    candidate_files = _candidate_files(mission, output_dir)
    tree = _git_tree(body['base_sha'], candidate_files, root)
    checks = {'carrier_public_clean': sha256_bytes(stable_json({'carrier_sha256': body['carrier_sha256']}).encode('utf-8')), 'spear_compile': sha256_bytes(stable_json(compile_receipt).encode('utf-8'))}
    mission_identity = {'repository': REPOSITORY, 'issue_number': issue_number, 'mission_id': mission['mission_id'], 'attempt_id': manifest['attempt_id'], 'objective': manifest['objective']}
    seal = build_candidate_seal(mission_identity, canonical_base_sha=mission['base_sha'], branch_intent=mission['branch'], candidate_files=candidate_files, expected_candidate_tree_sha=tree, expected_head_sha=None, prepublication_checks=checks, authorizer='JAYSON', operator='ATHENA', route='SPEAR_DIRECT_ISSUE', generated_state='CURRENT')
    context = {'issue_number': issue_number, 'attempt_id': manifest['attempt_id'], 'objective': manifest['objective'], 'expected_candidate_tree_sha': tree, 'expected_head_sha': None, 'prepublication_checks': checks, 'consumed_seal_ids': []}
    seal_path = root / 'candidate-seal.json'
    context_path = root / 'candidate-seal-context.json'
    seal_path.write_text(json.dumps(seal, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    context_path.write_text(json.dumps(context, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return {'package_path': package_path, 'output_dir': output_dir, 'mission_path': mission_path, 'mission': mission, 'compile_receipt': compile_receipt, 'candidate_files': candidate_files, 'candidate_tree': tree, 'seal': seal, 'seal_path': seal_path, 'context': context, 'context_path': context_path}

def _receipt_base(mode: str, result: str, issue_number: int, manifest: dict[str, Any], request_id: str) -> dict[str, Any]:
    return {'schema_version': 'atlas.athena.spear-issue-receipt.v1', 'mode': mode, 'result': result, 'repository': REPOSITORY, 'issue_number': issue_number, 'mission_id': manifest['mission_id'], 'attempt_id': manifest['attempt_id'], 'base_sha': manifest['source_binding']['base_sha'], 'request_id': request_id, 'route': 'SPEAR_DIRECT_ISSUE', 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'semantic_operator': 'ATHENA', 'authorizer': 'JAYSON', 'automatic_retry': False, 'forbidden_actions': {'direct_main': False, 'force_push': False, 'ready': False, 'merge': False, 'repository_settings': False, 'standing_authority': False, 'second_writer': False}}

def _preview(issue_number: int, triggering_comment: dict[str, Any], body: dict[str, Any], manifest: dict[str, Any], *, post: bool) -> dict[str, Any]:
    _validate_envelope(body, manifest, issue_number, 'PREVIEW')
    _authorization(body)
    if post:
        _reject_request_replay(issue_number, body['request_id'], {'PREVIEW'})
    if _main_sha() != body['base_sha']:
        raise SpearIssueIngressError('canonical base moved', 'STALE_BASE')
    carrier, _aad = _reconstruct_preview(body, issue_number)
    root = Path(tempfile.mkdtemp(prefix='atlas-spear-issue-preview-'))
    try:
        compiled = _compile_and_seal(carrier, body, manifest, issue_number, root)
        receipt = _receipt_base('PREVIEW', 'PREVIEW_ACCEPTED', issue_number, manifest, body['request_id'])
        receipt.update({'preview_id': 'spear-preview:' + sha256_bytes(stable_json({'request_id': body['request_id'], 'carrier_sha256': body['carrier_sha256'], 'seal_sha256': compiled['seal']['seal_sha256']}).encode('utf-8'))[:32], 'trigger_comment_id': triggering_comment['id'], 'trigger_comment_sha256': sha256_bytes(triggering_comment['body'].encode('utf-8')), 'carrier_sha256': body['carrier_sha256'], 'compile_receipt_sha256': sha256_bytes(stable_json(compiled['compile_receipt']).encode('utf-8')), 'candidate_tree': compiled['candidate_tree'], 'declared_paths': sorted(compiled['candidate_files']), 'seal': compiled['seal'], 'stop_point': 'READ_ONLY_PREVIEW_RECEIPT'})
        if post:
            written = _post(issue_number, RECEIPT_MARKER, receipt)
            receipt['receipt_comment_id'] = written['id']
            receipt['receipt_comment_sha256'] = sha256_bytes(written['body'].encode('utf-8'))
        receipt['_compiled'] = compiled
        return receipt
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise

def _find_preview_envelope(preview_receipt: dict[str, Any]) -> dict[str, Any]:
    trigger_id = preview_receipt.get('trigger_comment_id')
    expected = preview_receipt.get('trigger_comment_sha256')
    if not isinstance(trigger_id, int) or not isinstance(expected, str):
        raise SpearIssueIngressError('Preview receipt trigger binding rejected', 'PREVIEW_RECEIPT_REJECTED')
    comment_value = _comment(trigger_id)
    if (comment_value.get('user') or {}).get('login') != OWNER:
        raise SpearIssueIngressError('Preview envelope author mismatch', 'PREVIEW_DRIFT')
    if sha256_bytes(comment_value['body'].encode('utf-8')) != expected:
        raise SpearIssueIngressError('Preview envelope drifted', 'PREVIEW_DRIFT')
    _marker, body = parse_comment(comment_value['body'], PREVIEW)
    body['_trigger_comment'] = comment_value
    return body

def _execute(issue_number: int, body: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    _validate_envelope(body, manifest, issue_number, 'EXECUTE')
    _authorization(body)
    _reject_request_replay(issue_number, body['request_id'], {'EXECUTE', 'RESUME'})
    receipt_comment_id = body.get('preview_receipt_comment_id')
    expected_receipt_sha = body.get('preview_receipt_sha256')
    if not isinstance(receipt_comment_id, int) or not isinstance(expected_receipt_sha, str):
        raise SpearIssueIngressError('Preview receipt binding rejected', 'PREVIEW_RECEIPT_REJECTED')
    receipt_comment = _comment(receipt_comment_id)
    if sha256_bytes(receipt_comment['body'].encode('utf-8')) != expected_receipt_sha:
        raise SpearIssueIngressError('Preview receipt drifted', 'PREVIEW_DRIFT')
    _marker, preview_receipt = parse_comment(receipt_comment['body'], RECEIPT_MARKER)
    if preview_receipt.get('result') != 'PREVIEW_ACCEPTED' or preview_receipt.get('preview_id') != body.get('preview_id'):
        raise SpearIssueIngressError('Preview receipt is not accepted', 'PREVIEW_RECEIPT_REJECTED')
    if preview_receipt.get('seal', {}).get('seal_id') != body.get('seal_id') or preview_receipt.get('seal', {}).get('seal_sha256') != body.get('seal_sha256'):
        raise SpearIssueIngressError('candidate seal binding rejected', 'CANDIDATE_SEAL_REJECTED')
    preview_body = _find_preview_envelope(preview_receipt)
    trigger = preview_body.pop('_trigger_comment')
    current = _preview(issue_number, trigger, preview_body, manifest, post=False)
    compiled = current.pop('_compiled')
    if current['seal'] != preview_receipt['seal'] or current['preview_id'] != preview_receipt['preview_id']:
        raise SpearIssueIngressError('Preview reproduction drifted', 'PREVIEW_DRIFT')
    reservation = _receipt_base('EXECUTE', 'EXECUTE_RESERVED', issue_number, manifest, body['request_id'])
    reservation.update({'preview_id': body['preview_id'], 'seal_id': body['seal_id'], 'seal_sha256': body['seal_sha256'], 'carrier_sha256': preview_receipt['carrier_sha256'], 'stop_point': 'RESERVED_BEFORE_REMOTE_MUTATION'})
    reservation_written = _post(issue_number, RECEIPT_MARKER, reservation)
    compile_package, AdapterError, execute_sealed_mission, _resume = _load_thread_engine()
    try:
        adapter = execute_sealed_mission(compiled['mission_path'], package_root=compiled['output_dir'], seal_path=compiled['seal_path'], context_path=compiled['context_path'], mission_sha256=compiled['mission']['mission_sha256'], work_root=compiled['output_dir'].parent / 'adapter-work')
        result = _receipt_base('EXECUTE', 'SUCCESS', issue_number, manifest, body['request_id'])
        result.update({'preview_id': body['preview_id'], 'seal_id': body['seal_id'], 'seal_sha256': body['seal_sha256'], 'reservation_comment_id': reservation_written['id'], 'adapter_receipt_sha256': sha256_bytes(stable_json(adapter).encode('utf-8')), 'branch': adapter.get('branch', compiled['mission']['branch']), 'head_sha': adapter.get('head_sha'), 'pull_request': (adapter.get('pr_readback') or {}).get('number'), 'stop_point': 'DRAFT_PR_READBACK'})
    except AdapterError as exc:
        if not exc.receipt or exc.receipt.get('result') != 'PARTIAL':
            raise
        result = _receipt_base('EXECUTE', 'PARTIAL', issue_number, manifest, body['request_id'])
        result.update({'preview_id': body['preview_id'], 'seal_id': body['seal_id'], 'seal_sha256': body['seal_sha256'], 'reservation_comment_id': reservation_written['id'], 'partial_receipt': exc.receipt, 'stop_point': 'BLOCKED_RESUMABLE'})
    written = _post(issue_number, RECEIPT_MARKER, result)
    result['receipt_comment_id'] = written['id']
    return result

def _bound_receipt(body: dict[str, Any], id_field: str, sha_field: str) -> tuple[dict[str, Any], dict[str, Any]]:
    comment_id = body.get(id_field)
    expected_sha = body.get(sha_field)
    if not isinstance(comment_id, int) or not isinstance(expected_sha, str) or (not SHA64.fullmatch(expected_sha)):
        raise SpearIssueIngressError('receipt binding rejected', 'RECEIPT_BINDING_REJECTED')
    value = _comment(comment_id)
    if (value.get('user') or {}).get('login') != 'github-actions[bot]':
        raise SpearIssueIngressError('receipt author mismatch', 'RECEIPT_BINDING_REJECTED')
    if sha256_bytes(value['body'].encode('utf-8')) != expected_sha:
        raise SpearIssueIngressError('receipt comment drifted', 'RECEIPT_DRIFT')
    _marker, receipt = parse_comment(value['body'], RECEIPT_MARKER)
    return (value, receipt)

def _resume_request(issue_number: int, body: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    _validate_envelope(body, manifest, issue_number, 'RESUME')
    _authorization(body)
    _reject_request_replay(issue_number, body['request_id'], {'RESUME'})
    _partial_comment, partial_issue_receipt = _bound_receipt(body, 'partial_receipt_comment_id', 'partial_receipt_sha256')
    _preview_comment, preview_receipt = _bound_receipt(body, 'preview_receipt_comment_id', 'preview_receipt_sha256')
    if partial_issue_receipt.get('result') != 'PARTIAL' or not isinstance(partial_issue_receipt.get('partial_receipt'), dict):
        raise SpearIssueIngressError('exact PARTIAL receipt is required', 'PARTIAL_RECEIPT_REJECTED')
    if preview_receipt.get('result') != 'PREVIEW_ACCEPTED' or preview_receipt.get('preview_id') != body.get('preview_id'):
        raise SpearIssueIngressError('accepted Preview receipt is required', 'PREVIEW_RECEIPT_REJECTED')
    seal = preview_receipt.get('seal')
    if not isinstance(seal, dict) or seal.get('seal_id') != body.get('seal_id') or seal.get('seal_sha256') != body.get('seal_sha256'):
        raise SpearIssueIngressError('resume candidate seal mismatch', 'CANDIDATE_SEAL_REJECTED')
    preview_body = _find_preview_envelope(preview_receipt)
    trigger = preview_body.pop('_trigger_comment')
    current = _preview(issue_number, trigger, preview_body, manifest, post=False)
    compiled = current.pop('_compiled')
    if current['seal'] != seal or current['preview_id'] != body['preview_id']:
        raise SpearIssueIngressError('resume Preview reproduction drifted', 'PREVIEW_DRIFT')
    partial_path = compiled['output_dir'].parent / 'partial-receipt.json'
    partial_path.write_text(json.dumps(partial_issue_receipt['partial_receipt'], indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _compile, AdapterError, _execute, resume_exact_partial = _load_thread_engine()
    try:
        recovered = resume_exact_partial(compiled['mission_path'], partial_receipt_path=partial_path, seal_path=compiled['seal_path'])
    except AdapterError as exc:
        blocked = _receipt_base('RESUME', 'BLOCKED', issue_number, manifest, body['request_id'])
        blocked.update({'preview_id': body['preview_id'], 'seal_id': body['seal_id'], 'seal_sha256': body['seal_sha256'], 'error_code': exc.code, 'stop_point': 'BLOCKED_RESUMABLE'})
        _post(issue_number, RECEIPT_MARKER, blocked)
        return blocked
    result = _receipt_base('RESUME', 'RECOVERED_SUCCESS', issue_number, manifest, body['request_id'])
    result.update({'preview_id': body['preview_id'], 'seal_id': body['seal_id'], 'seal_sha256': body['seal_sha256'], 'head_sha': recovered.get('head_sha'), 'pull_request': (recovered.get('pull_request') or {}).get('number'), 'stop_point': 'DRAFT_PR_READBACK'})
    _post(issue_number, RECEIPT_MARKER, result)
    return result

def _key_advertisement(issue_number: int, body: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    _validate_envelope(body, manifest, issue_number, 'KEY_REQUEST')
    _private, public_b64, expected_id = _keys()
    receipt = _receipt_base('KEY_REQUEST', 'KEY_ADVERTISEMENT', issue_number, manifest, body['request_id'])
    receipt.update({'key_id': expected_id, 'public_key_b64': public_b64, 'algorithm': {'key_agreement': 'X25519', 'kdf': 'HKDF-SHA-256', 'aead': 'AES-256-GCM'}, 'stop_point': 'PUBLIC_KEY_READBACK'})
    _post(issue_number, RECEIPT_MARKER, receipt)
    return receipt

def main(argv: list[str] | None=None) -> int:
    parser = argparse.ArgumentParser(description='Athena Direct Spear Mission-comment ingress')
    parser.add_argument('--mode', choices=('key', 'preview', 'execute', 'resume'), required=True)
    args = parser.parse_args(argv)
    issue_event, triggering, raw_body, _environment = _trusted_event()
    issue_number = int(issue_event['number'])
    current_issue = _issue(issue_number)
    manifest = _mission_manifest(current_issue)
    try:
        if args.mode == 'key':
            _marker, body = parse_comment(raw_body, KEY_REQUEST)
            result = _key_advertisement(issue_number, body, manifest)
        elif args.mode == 'preview':
            _marker, body = parse_comment(raw_body, PREVIEW)
            result = _preview(issue_number, triggering, body, manifest, post=True)
            result.pop('_compiled', None)
        elif args.mode == 'execute':
            _marker, body = parse_comment(raw_body, EXECUTE)
            result = _execute(issue_number, body, manifest)
        else:
            _marker, body = parse_comment(raw_body, RESUME)
            result = _resume_request(issue_number, body, manifest)
        sys.stdout.write(stable_json({'result': result.get('result'), 'mode': args.mode, 'stop_point': result.get('stop_point')}))
        return 0
    except SpearIssueIngressError as exc:
        failure = _receipt_base(args.mode.upper(), 'REJECTED' if exc.stage != 'BLOCKED_RESUMABLE' else 'BLOCKED', issue_number, manifest, 'UNKNOWN')
        failure.update({'error_code': exc.code, 'stop_point': exc.stage})
        try:
            _post(issue_number, RECEIPT_MARKER, failure)
        except SpearIssueIngressError:
            pass
        sys.stderr.write(stable_json({'result': failure['result'], 'error_code': exc.code, 'stop_point': exc.stage}))
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
