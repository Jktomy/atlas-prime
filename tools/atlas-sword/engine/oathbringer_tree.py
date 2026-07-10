from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Sequence

from oathbringer_core import _require, _safe_relative_path

def _payload_bytes(package_root: Path, item: dict[str, Any]) -> bytes:
    relative = _safe_relative_path(item['payload_path'], 'payload_path')
    root = package_root.resolve()
    path = (root / relative).resolve()
    _require(path == root or root in path.parents, f'payload escapes package root: {relative}')
    _require(path.is_file(), f'payload file missing: {relative}')
    content = path.read_bytes()
    observed = hashlib.sha256(content).hexdigest()
    _require(observed == item['payload_sha256'], f'payload hash mismatch: {relative}')
    return content

def declared_changed_paths(declared: Sequence[dict[str, Any]]) -> list[str]:
    paths: set[str] = set()
    for item in declared:
        paths.add(str(item['path']))
        if item['operation'] in {'RENAME', 'MOVE'}:
            paths.add(str(item['source_path']))
    return sorted(paths)

def changed_paths_between(reference: dict[str, dict[str, Any]], candidate: dict[str, dict[str, Any]]) -> list[str]:
    paths = set(reference) | set(candidate)
    return sorted((path for path in paths if (reference.get(path, {}).get('sha'), reference.get(path, {}).get('mode')) != (candidate.get(path, {}).get('sha'), candidate.get(path, {}).get('mode'))))

def build_tree_elements(mission: dict[str, Any], package_root: Path, reference_tree: dict[str, dict[str, Any]], client: Any) -> tuple[list[dict[str, Any]], dict[str, str]]:
    elements: list[dict[str, Any]] = []
    payload_blobs: dict[str, str] = {}
    for item in mission['declared_paths']:
        operation = item['operation']
        target = item['path']
        reference_target = reference_tree.get(target)
        if operation == 'ADD':
            _require(reference_target is None, f'ADD target already exists in expected base: {target}')
            blob = client.create_blob(_payload_bytes(package_root, item))
            elements.append({'path': target, 'mode': item.get('mode', '100644'), 'type': 'blob', 'sha': blob})
            payload_blobs[target] = blob
        elif operation == 'REPLACE':
            _require(reference_target is not None, f'REPLACE target missing from expected base: {target}')
            _require(reference_target['sha'] == item['source_blob'], f'source blob drift for {target}')
            blob = client.create_blob(_payload_bytes(package_root, item))
            elements.append({'path': target, 'mode': reference_target.get('mode', '100644'), 'type': 'blob', 'sha': blob})
            payload_blobs[target] = blob
        elif operation == 'DELETE':
            _require(reference_target is not None, f'DELETE target missing from expected base: {target}')
            _require(reference_target['sha'] == item['source_blob'], f'source blob drift for {target}')
            elements.append({'path': target, 'mode': '100644', 'type': 'blob', 'sha': None})
        else:
            source = item['source_path']
            reference_source = reference_tree.get(source)
            _require(reference_source is not None, f'{operation} source missing from expected base: {source}')
            _require(reference_source['sha'] == item['source_blob'], f'source blob drift for {source}')
            _require(reference_target is None, f'{operation} destination exists in expected base: {target}')
            if item.get('payload_path') is not None:
                blob = client.create_blob(_payload_bytes(package_root, item))
            else:
                blob = str(reference_source['sha'])
            elements.append({'path': target, 'mode': item.get('mode', reference_source.get('mode', '100644')), 'type': 'blob', 'sha': blob})
            elements.append({'path': source, 'mode': '100644', 'type': 'blob', 'sha': None})
            payload_blobs[target] = blob
    return (elements, payload_blobs)

def _verify_pr_identity(mission: dict[str, Any], pr: dict[str, Any]) -> None:
    _require(pr.get('state') == 'open', 'pull request is not open')
    _require(str(pr['head']['ref']) == mission['branch'], 'pull request branch mismatch')
    _require(str(pr['head']['sha']) == mission['expected_head'], 'pull request head drift')
    _require(str(pr['base']['ref']) == mission['base_branch'], 'pull request base branch mismatch')
    _require(str(pr['base']['sha']) == mission['expected_base'], 'pull request base SHA drift')

def _verify_changed_paths(mission: dict[str, Any], observed: Sequence[str]) -> list[str]:
    expected = declared_changed_paths(mission['declared_paths'])
    actual = sorted(set(observed))
    _require(actual == expected, f'pull request changed-path mismatch: expected={expected}; observed={actual}')
    return expected
