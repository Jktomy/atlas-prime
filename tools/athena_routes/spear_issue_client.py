from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from .spear_issue_crypto import OWNER, RECEIPT_MARKER, REPOSITORY, SHA64, SpearIssueIngressError, _comment, _issue, _issue_comments, _keys, _main_sha, _mission_manifest, _post, _trusted_event, canonical_json, decrypt, encrypt, key_id, public_key_bytes, sha256_bytes, stable_json
KEY_REQUEST = 'ATLAS_SPEAR_KEY_REQUEST_V1'
CHUNK = 'ATLAS_SPEAR_CIPHERTEXT_CHUNK_V1'
PREVIEW = 'ATLAS_SPEAR_PREVIEW_V1'
EXECUTE = 'ATLAS_SPEAR_EXECUTE_V1'
RESUME = 'ATLAS_SPEAR_RESUME_V1'
MAX_CARRIER_BYTES = 524288
MAX_CHUNKS = 24
MAX_COMMENT_BYTES = 48000
MAX_ARCHIVE_ENTRIES = 128
MAX_EXPANDED_BYTES = 2097152
MAX_ENTRY_BYTES = 1048576
SENSITIVE = (re.compile(b'(?i)\\b(api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\\b\\s*[:=]\\s*(?:\\"[^\\"\\r\\n]{8,}\\"|\'[^\'\\r\\n]{8,}\'|[^\\s`\\"\'<>{}]{8,})'), re.compile(b'-----BEGIN [A-Z ]*PRIVATE KEY-----'), re.compile(b'(?i)(mfa|recovery code)\\s*[:=]\\s*[^\\s`\'\\"<>{}]+'))

class SpearIssueClientError(ValueError):
    pass

def _safe_archive_path(raw: str) -> str:
    path = PurePosixPath(raw)
    if not raw or raw.startswith('/') or '\\' in raw or any((part in {'', '.', '..'} for part in raw.split('/'))):
        raise SpearIssueClientError('unsafe archive path')
    if raw != path.as_posix():
        raise SpearIssueClientError('noncanonical archive path')
    return raw

def scan_public_clean_carrier(carrier: bytes) -> str:
    if not carrier or len(carrier) > MAX_CARRIER_BYTES:
        raise SpearIssueClientError('carrier size rejected')
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(carrier)) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > MAX_ARCHIVE_ENTRIES:
                raise SpearIssueClientError('archive entry count rejected')
            expanded = sum((info.file_size for info in infos if not info.is_dir()))
            if expanded > MAX_EXPANDED_BYTES:
                raise SpearIssueClientError('archive expanded size rejected')
            names: set[str] = set()
            folded: set[str] = set()
            for info in infos:
                if info.flag_bits & 1:
                    raise SpearIssueClientError('nested encrypted archive entry rejected')
                if info.file_size > MAX_ENTRY_BYTES:
                    raise SpearIssueClientError('archive member size rejected')
                name = _safe_archive_path(info.filename)
                if name in names or name.casefold() in folded:
                    raise SpearIssueClientError('duplicate archive path')
                names.add(name)
                folded.add(name.casefold())
                mode = info.external_attr >> 16 & 61440
                if mode not in {0, 32768} and (not info.is_dir()):
                    raise SpearIssueClientError('nonregular archive member')
                if info.is_dir():
                    continue
                value = archive.read(info)
                try:
                    value.decode('utf-8')
                except UnicodeDecodeError as exc:
                    raise SpearIssueClientError('carrier content must be public-clean UTF-8') from exc
                if any((pattern.search(value) for pattern in SENSITIVE)):
                    raise SpearIssueClientError('carrier failed local public-clean scan')
    except zipfile.BadZipFile as exc:
        raise SpearIssueClientError('carrier is not a valid ZIP') from exc
    return sha256_bytes(carrier)

def comment(marker: str, body: dict[str, Any]) -> str:
    value = marker + '\n' + json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    if len(value.encode('utf-8')) > MAX_COMMENT_BYTES:
        raise SpearIssueClientError('comment exceeds bounded size')
    return value

def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in pairs:
        if key in result:
            raise SpearIssueClientError(f'duplicate JSON key rejected: {key}')
        result[key] = item
    return result

def parse_comment(value: str, expected_marker: str | None=None) -> tuple[str, dict[str, Any]]:
    marker, separator, raw = value.partition('\n')
    if not separator or (expected_marker and marker != expected_marker):
        raise SpearIssueClientError('comment marker rejected')
    try:
        body = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise SpearIssueClientError('comment JSON rejected') from exc
    if not isinstance(body, dict):
        raise SpearIssueClientError('comment body must be an object')
    return (marker, body)

def key_request(*, mission_id: str, attempt_id: str, base_sha: str, request_id: str) -> str:
    return comment(KEY_REQUEST, {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': 'KEY_REQUEST', 'repository': 'Jktomy/atlas-prime', 'mission_id': mission_id, 'attempt_id': attempt_id, 'base_sha': base_sha, 'request_id': request_id, 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'authorizer': 'JAYSON', 'semantic_operator': 'ATHENA'})

def build_encrypted_comments(carrier: bytes, *, repository: str, issue_number: int, mission_id: str, attempt_id: str, base_sha: str, request_id: str, authorization_comment_id: int, authorization_comment_sha256: str, public_key_b64: str, key_id: str, max_chunk_characters: int=36000) -> dict[str, Any]:
    carrier_sha = scan_public_clean_carrier(carrier)
    aad = {'repository': repository, 'issue_number': issue_number, 'mission_id': mission_id, 'attempt_id': attempt_id, 'base_sha': base_sha, 'request_id': request_id, 'authorization_comment_id': authorization_comment_id, 'authorization_comment_sha256': authorization_comment_sha256, 'key_id': key_id, 'carrier_sha256': carrier_sha, 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'semantic_operator': 'ATHENA', 'authorizer': 'JAYSON'}
    encrypted = encrypt(carrier, public_key_b64, expected_key_id=key_id, aad=aad)
    encoded = encrypted.pop('ciphertext_b64')
    pieces = [encoded[index:index + max_chunk_characters] for index in range(0, len(encoded), max_chunk_characters)]
    if not pieces or len(pieces) > MAX_CHUNKS:
        raise SpearIssueClientError('ciphertext chunk count rejected')
    chunks: list[str] = []
    chunk_digests: list[str] = []
    for index, piece in enumerate(pieces):
        payload = {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': 'CIPHERTEXT_CHUNK', 'repository': repository, 'issue_number': issue_number, 'mission_id': mission_id, 'attempt_id': attempt_id, 'request_id': request_id, 'index': index, 'count': len(pieces), 'ciphertext_piece': piece, 'ciphertext_piece_sha256': sha256_bytes(piece.encode('ascii')), 'complete_ciphertext_sha256': sha256_bytes(encoded.encode('ascii'))}
        rendered = comment(CHUNK, payload)
        chunks.append(rendered)
        chunk_digests.append(sha256_bytes(rendered.encode('utf-8')))
    preview_template = {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': 'PREVIEW', **aad, 'crypto': encrypted, 'chunk_count': len(chunks), 'complete_ciphertext_sha256': sha256_bytes(encoded.encode('ascii')), 'chunk_body_sha256': chunk_digests, 'stop_point': 'READ_ONLY_PREVIEW_RECEIPT'}
    return {'chunks': chunks, 'preview_template': preview_template, 'carrier_sha256': carrier_sha}

def bind_chunk_comment_ids(preview_template: dict[str, Any], chunk_comment_ids: list[int]) -> str:
    body = dict(preview_template)
    if len(chunk_comment_ids) != body.get('chunk_count') or len(set(chunk_comment_ids)) != len(chunk_comment_ids):
        raise SpearIssueClientError('chunk comment identity mismatch')
    body['chunk_comment_ids'] = chunk_comment_ids
    return comment(PREVIEW, body)

def execute_request(*, preview_receipt_comment_id: int, preview_receipt_sha256: str, preview_id: str, seal_id: str, seal_sha256: str, mission_id: str, attempt_id: str, base_sha: str, request_id: str, authorization_comment_id: int, authorization_comment_sha256: str) -> str:
    return comment(EXECUTE, {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': 'EXECUTE', 'repository': 'Jktomy/atlas-prime', 'mission_id': mission_id, 'attempt_id': attempt_id, 'base_sha': base_sha, 'request_id': request_id, 'authorization_comment_id': authorization_comment_id, 'authorization_comment_sha256': authorization_comment_sha256, 'preview_receipt_comment_id': preview_receipt_comment_id, 'preview_receipt_sha256': preview_receipt_sha256, 'preview_id': preview_id, 'seal_id': seal_id, 'seal_sha256': seal_sha256, 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'semantic_operator': 'ATHENA', 'authorizer': 'JAYSON', 'stop_point': 'DRAFT_PR_READBACK'})

def resume_request(*, partial_receipt_comment_id: int, partial_receipt_sha256: str, preview_receipt_comment_id: int, preview_receipt_sha256: str, preview_id: str, seal_id: str, seal_sha256: str, mission_id: str, attempt_id: str, base_sha: str, request_id: str, authorization_comment_id: int, authorization_comment_sha256: str) -> str:
    return comment(RESUME, {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': 'RESUME', 'repository': 'Jktomy/atlas-prime', 'mission_id': mission_id, 'attempt_id': attempt_id, 'base_sha': base_sha, 'request_id': request_id, 'authorization_comment_id': authorization_comment_id, 'authorization_comment_sha256': authorization_comment_sha256, 'partial_receipt_comment_id': partial_receipt_comment_id, 'partial_receipt_sha256': partial_receipt_sha256, 'preview_receipt_comment_id': preview_receipt_comment_id, 'preview_receipt_sha256': preview_receipt_sha256, 'preview_id': preview_id, 'seal_id': seal_id, 'seal_sha256': seal_sha256, 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'semantic_operator': 'ATHENA', 'authorizer': 'JAYSON', 'stop_point': 'DRAFT_PR_READBACK'})

def main(argv: list[str] | None=None) -> int:
    parser = argparse.ArgumentParser(description='Build bounded encrypted Athena Spear Issue comments')
    parser.add_argument('--carrier', type=Path, required=True)
    parser.add_argument('--context', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    context = json.loads(args.context.read_text(encoding='utf-8'))
    result = build_encrypted_comments(args.carrier.read_bytes(), **context)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())

def _reject_request_replay(issue_number: int, request_id: str, modes: set[str]) -> None:
    for item in _issue_comments(issue_number):
        body = item.get('body')
        if (item.get('user') or {}).get('login') != 'github-actions[bot]':
            continue
        if not isinstance(body, str) or not body.startswith(RECEIPT_MARKER + '\n'):
            continue
        try:
            _marker, receipt = parse_comment(body, RECEIPT_MARKER)
        except Exception:
            continue
        if receipt.get('request_id') == request_id and receipt.get('mode') in modes and (receipt.get('result') in {'PREVIEW_ACCEPTED', 'EXECUTE_RESERVED', 'SUCCESS', 'PARTIAL', 'RECOVERED_SUCCESS'}):
            raise SpearIssueIngressError('request replay rejected', 'REQUEST_REPLAY')
COMMON_ENVELOPE_KEYS = {'schema_version', 'mode', 'repository', 'mission_id', 'attempt_id', 'base_sha', 'request_id', 'requesting_surface', 'semantic_operator', 'authorizer'}
MODE_ENVELOPE_KEYS = {'KEY_REQUEST': COMMON_ENVELOPE_KEYS, 'PREVIEW': COMMON_ENVELOPE_KEYS | {'issue_number', 'authorization_comment_id', 'authorization_comment_sha256', 'key_id', 'carrier_sha256', 'crypto', 'chunk_count', 'complete_ciphertext_sha256', 'chunk_body_sha256', 'chunk_comment_ids', 'stop_point'}, 'EXECUTE': COMMON_ENVELOPE_KEYS | {'authorization_comment_id', 'authorization_comment_sha256', 'preview_receipt_comment_id', 'preview_receipt_sha256', 'preview_id', 'seal_id', 'seal_sha256', 'stop_point'}, 'RESUME': COMMON_ENVELOPE_KEYS | {'authorization_comment_id', 'authorization_comment_sha256', 'partial_receipt_comment_id', 'partial_receipt_sha256', 'preview_receipt_comment_id', 'preview_receipt_sha256', 'preview_id', 'seal_id', 'seal_sha256', 'stop_point'}}
CHUNK_KEYS = {'schema_version', 'mode', 'repository', 'issue_number', 'mission_id', 'attempt_id', 'request_id', 'index', 'count', 'ciphertext_piece', 'ciphertext_piece_sha256', 'complete_ciphertext_sha256'}

def _validate_envelope(body: dict[str, Any], manifest: dict[str, Any], issue_number: int, expected_mode: str) -> None:
    allowed = MODE_ENVELOPE_KEYS.get(expected_mode)
    if allowed is None or set(body) != allowed:
        raise SpearIssueIngressError('envelope has unknown or missing properties', 'ENVELOPE_SCHEMA_REJECTED')
    expected = {'schema_version': 'atlas.athena.spear-issue-envelope.v1', 'mode': expected_mode, 'repository': REPOSITORY, 'mission_id': manifest['mission_id'], 'attempt_id': manifest['attempt_id'], 'base_sha': manifest['source_binding']['base_sha'], 'requesting_surface': 'CHATGPT_ATLAS_PROJECT', 'semantic_operator': 'ATHENA', 'authorizer': 'JAYSON'}
    for key, value in expected.items():
        if body.get(key) != value:
            raise SpearIssueIngressError(f'envelope identity mismatch: {key}', 'ENVELOPE_IDENTITY_REJECTED')
    if body.get('issue_number', issue_number) != issue_number:
        raise SpearIssueIngressError('envelope Issue identity mismatch', 'ENVELOPE_IDENTITY_REJECTED')
    request_id = body.get('request_id')
    if not isinstance(request_id, str) or not re.fullmatch('[A-Za-z0-9._:-]{12,160}', request_id):
        raise SpearIssueIngressError('request identity rejected', 'REQUEST_ID_REJECTED')

def _authorization(body: dict[str, Any]) -> dict[str, Any]:
    comment_id = body.get('authorization_comment_id')
    expected_sha = body.get('authorization_comment_sha256')
    if not isinstance(comment_id, int) or not isinstance(expected_sha, str) or (not SHA64.fullmatch(expected_sha)):
        raise SpearIssueIngressError('authorization binding rejected', 'AUTHORIZATION_BINDING_REJECTED')
    value = _comment(comment_id)
    if (value.get('user') or {}).get('login') != OWNER:
        raise SpearIssueIngressError('authorization author mismatch', 'AUTHORIZATION_BINDING_REJECTED')
    if sha256_bytes(value['body'].encode('utf-8')) != expected_sha:
        raise SpearIssueIngressError('authorization comment drifted', 'AUTHORIZATION_DRIFT')
    return value

def _reconstruct_preview(body: dict[str, Any], issue_number: int) -> tuple[bytes, dict[str, Any]]:
    private_b64, _public_b64, expected_key_id = _keys()
    if body.get('key_id') != expected_key_id:
        raise SpearIssueIngressError('envelope key identity mismatch', 'INGRESS_KEY_MISMATCH')
    ids = body.get('chunk_comment_ids')
    digests = body.get('chunk_body_sha256')
    if not isinstance(ids, list) or not isinstance(digests, list) or len(ids) != len(digests) or (not ids) or (len(ids) > MAX_CHUNKS):
        raise SpearIssueIngressError('chunk inventory rejected', 'CHUNK_INVENTORY_REJECTED')
    if len(set(ids)) != len(ids) or any((not isinstance(value, int) for value in ids)):
        raise SpearIssueIngressError('chunk identity collision', 'CHUNK_INVENTORY_REJECTED')
    pieces: list[str] = []
    complete_sha: str | None = None
    for index, (comment_id, expected_digest) in enumerate(zip(ids, digests)):
        value = _comment(comment_id)
        if (value.get('user') or {}).get('login') != OWNER:
            raise SpearIssueIngressError('chunk author mismatch', 'CHUNK_IDENTITY_REJECTED')
        if value.get('issue_url', '').split('/')[-1] not in {'', str(issue_number)}:
            raise SpearIssueIngressError('cross-Issue chunk rejected', 'CHUNK_IDENTITY_REJECTED')
        if sha256_bytes(value['body'].encode('utf-8')) != expected_digest:
            raise SpearIssueIngressError('chunk comment drifted', 'CHUNK_DRIFT')
        _marker, chunk = parse_comment(value['body'], CHUNK)
        if set(chunk) != CHUNK_KEYS:
            raise SpearIssueIngressError('chunk has unknown or missing properties', 'CHUNK_SCHEMA_REJECTED')
        if chunk.get('mode') != 'CIPHERTEXT_CHUNK' or chunk.get('request_id') != body['request_id']:
            raise SpearIssueIngressError('chunk request mismatch', 'CHUNK_IDENTITY_REJECTED')
        if chunk.get('index') != index or chunk.get('count') != len(ids):
            raise SpearIssueIngressError('chunk order mismatch', 'CHUNK_ORDER_REJECTED')
        piece = chunk.get('ciphertext_piece')
        if not isinstance(piece, str) or sha256_bytes(piece.encode('ascii')) != chunk.get('ciphertext_piece_sha256'):
            raise SpearIssueIngressError('chunk digest mismatch', 'CHUNK_HASH_REJECTED')
        if complete_sha is None:
            complete_sha = chunk.get('complete_ciphertext_sha256')
        elif complete_sha != chunk.get('complete_ciphertext_sha256'):
            raise SpearIssueIngressError('chunk carrier digest mismatch', 'CHUNK_HASH_REJECTED')
        pieces.append(piece)
    ciphertext_b64 = ''.join(pieces)
    if sha256_bytes(ciphertext_b64.encode('ascii')) != complete_sha or complete_sha != body.get('complete_ciphertext_sha256'):
        raise SpearIssueIngressError('complete ciphertext digest mismatch', 'CHUNK_HASH_REJECTED')
    crypto = body.get('crypto')
    if not isinstance(crypto, dict):
        raise SpearIssueIngressError('crypto envelope rejected', 'CRYPTO_ENVELOPE_REJECTED')
    crypto = dict(crypto)
    crypto['ciphertext_b64'] = ciphertext_b64
    aad_keys = ('repository', 'issue_number', 'mission_id', 'attempt_id', 'base_sha', 'request_id', 'authorization_comment_id', 'authorization_comment_sha256', 'key_id', 'carrier_sha256', 'requesting_surface', 'semantic_operator', 'authorizer')
    aad = {key: body[key] for key in aad_keys}
    carrier = decrypt(crypto, private_b64, expected_key_id=expected_key_id, aad=aad)
    if scan_public_clean_carrier(carrier) != body.get('carrier_sha256'):
        raise SpearIssueIngressError('carrier privacy or digest check failed', 'CARRIER_REJECTED')
    return (carrier, aad)
