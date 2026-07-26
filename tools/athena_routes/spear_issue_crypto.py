from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
SCHEMA_VERSION = 'atlas.athena.spear-issue-ciphertext.v1'
INFO = b'atlas-prime/athena-spear-issue-ingress/v1'

class SpearIssueCryptoError(ValueError):
    pass

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')

def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode('ascii')

def _b64decode(value: str, label: str) -> bytes:
    try:
        return base64.b64decode(value.encode('ascii'), validate=True)
    except Exception as exc:
        raise SpearIssueCryptoError(f'invalid Base64 for {label}') from exc

def public_key_bytes(public_key: X25519PublicKey) -> bytes:
    return public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

def private_key_bytes(private_key: X25519PrivateKey) -> bytes:
    return private_key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())

def key_id(public_key_raw: bytes) -> str:
    if len(public_key_raw) != 32:
        raise SpearIssueCryptoError('X25519 public key must be 32 bytes')
    return 'x25519-sha256:' + sha256_bytes(public_key_raw)[:32]

def generate_keypair() -> tuple[str, str, str]:
    private = X25519PrivateKey.generate()
    public_raw = public_key_bytes(private.public_key())
    return (_b64encode(private_key_bytes(private)), _b64encode(public_raw), key_id(public_raw))

def _derive(shared_secret: bytes, salt: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=INFO).derive(shared_secret)

@dataclass(frozen=True)
class CiphertextEnvelope:
    schema_version: str
    key_id: str
    ephemeral_public_key_b64: str
    salt_b64: str
    nonce_b64: str
    aad_sha256: str
    plaintext_sha256: str
    ciphertext_b64: str

    def as_dict(self) -> dict[str, str]:
        return {'schema_version': self.schema_version, 'key_id': self.key_id, 'ephemeral_public_key_b64': self.ephemeral_public_key_b64, 'salt_b64': self.salt_b64, 'nonce_b64': self.nonce_b64, 'aad_sha256': self.aad_sha256, 'plaintext_sha256': self.plaintext_sha256, 'ciphertext_b64': self.ciphertext_b64}

def encrypt(plaintext: bytes, public_key_b64: str, *, expected_key_id: str, aad: dict[str, Any]) -> dict[str, str]:
    if not plaintext:
        raise SpearIssueCryptoError('plaintext is empty')
    recipient_raw = _b64decode(public_key_b64, 'public key')
    if len(recipient_raw) != 32 or key_id(recipient_raw) != expected_key_id:
        raise SpearIssueCryptoError('public key identity mismatch')
    recipient = X25519PublicKey.from_public_bytes(recipient_raw)
    ephemeral = X25519PrivateKey.generate()
    ephemeral_raw = public_key_bytes(ephemeral.public_key())
    salt = hashlib.sha256(ephemeral_raw + recipient_raw + INFO).digest()
    key = _derive(ephemeral.exchange(recipient), salt)
    nonce = hashlib.sha256(plaintext + canonical_json(aad) + ephemeral_raw).digest()[:12]
    aad_bytes = canonical_json(aad)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad_bytes)
    return CiphertextEnvelope(schema_version=SCHEMA_VERSION, key_id=expected_key_id, ephemeral_public_key_b64=_b64encode(ephemeral_raw), salt_b64=_b64encode(salt), nonce_b64=_b64encode(nonce), aad_sha256=sha256_bytes(aad_bytes), plaintext_sha256=sha256_bytes(plaintext), ciphertext_b64=_b64encode(ciphertext)).as_dict()

def decrypt(envelope: dict[str, Any], private_key_b64: str, *, expected_key_id: str, aad: dict[str, Any]) -> bytes:
    required = {'schema_version', 'key_id', 'ephemeral_public_key_b64', 'salt_b64', 'nonce_b64', 'aad_sha256', 'plaintext_sha256', 'ciphertext_b64'}
    if not isinstance(envelope, dict) or set(envelope) != required:
        raise SpearIssueCryptoError('ciphertext envelope shape rejected')
    if envelope['schema_version'] != SCHEMA_VERSION or envelope['key_id'] != expected_key_id:
        raise SpearIssueCryptoError('ciphertext envelope identity mismatch')
    private_raw = _b64decode(private_key_b64, 'private key')
    if len(private_raw) != 32:
        raise SpearIssueCryptoError('X25519 private key must be 32 bytes')
    private = X25519PrivateKey.from_private_bytes(private_raw)
    if key_id(public_key_bytes(private.public_key())) != expected_key_id:
        raise SpearIssueCryptoError('private key identity mismatch')
    ephemeral_raw = _b64decode(str(envelope['ephemeral_public_key_b64']), 'ephemeral key')
    salt = _b64decode(str(envelope['salt_b64']), 'salt')
    nonce = _b64decode(str(envelope['nonce_b64']), 'nonce')
    ciphertext = _b64decode(str(envelope['ciphertext_b64']), 'ciphertext')
    if len(ephemeral_raw) != 32 or len(salt) != 32 or len(nonce) != 12:
        raise SpearIssueCryptoError('ciphertext parameters rejected')
    aad_bytes = canonical_json(aad)
    if sha256_bytes(aad_bytes) != envelope['aad_sha256']:
        raise SpearIssueCryptoError('authenticated context mismatch')
    key = _derive(private.exchange(X25519PublicKey.from_public_bytes(ephemeral_raw)), salt)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, aad_bytes)
    except Exception as exc:
        raise SpearIssueCryptoError('ciphertext authentication failed') from exc
    if sha256_bytes(plaintext) != envelope['plaintext_sha256']:
        raise SpearIssueCryptoError('plaintext digest mismatch')
    return plaintext
REPOSITORY = 'Jktomy/atlas-prime'
OWNER = 'Jktomy'
RECEIPT_MARKER = 'ATLAS_SPEAR_RECEIPT_V1'
MAX_CHUNKS = 24
SHA40 = re.compile('^[0-9a-f]{40}$')
SHA64 = re.compile('^[0-9a-f]{64}$')
MISSION_BLOCK = re.compile('```atlas-mission-v1\\s*(\\{.*?\\})\\s*```', re.DOTALL)

class SpearIssueIngressError(RuntimeError):

    def __init__(self, message: str, code: str, stage: str='PRE_MUTATION_REJECTION') -> None:
        super().__init__(message)
        self.code = code
        self.stage = stage

def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def _run(command: list[str], *, cwd: Path | None=None, allow_failure: bool=False) -> str:
    completed = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if completed.returncode != 0 and (not allow_failure):
        raise SpearIssueIngressError('bounded GitHub readback or execution failed', 'GITHUB_OPERATION_FAILED', 'READBACK')
    return completed.stdout.strip()

def _api_json(path: str) -> dict[str, Any] | list[Any]:
    raw = _run(['gh', 'api', path])
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpearIssueIngressError('GitHub response was not JSON', 'GITHUB_READBACK_INVALID', 'READBACK') from exc
    if not isinstance(value, (dict, list)):
        raise SpearIssueIngressError('GitHub response shape rejected', 'GITHUB_READBACK_INVALID', 'READBACK')
    return value

def _comment(comment_id: int) -> dict[str, Any]:
    value = _api_json(f'repos/{REPOSITORY}/issues/comments/{comment_id}')
    if not isinstance(value, dict) or value.get('id') != comment_id or (not isinstance(value.get('body'), str)):
        raise SpearIssueIngressError('Issue comment readback mismatch', 'COMMENT_READBACK_FAILED', 'READBACK')
    return value

def _issue(issue_number: int) -> dict[str, Any]:
    value = _api_json(f'repos/{REPOSITORY}/issues/{issue_number}')
    if not isinstance(value, dict) or value.get('number') != issue_number or (not isinstance(value.get('body'), str)):
        raise SpearIssueIngressError('Mission Issue readback mismatch', 'MISSION_READBACK_FAILED', 'READBACK')
    if value.get('pull_request') is not None:
        raise SpearIssueIngressError('pull-request comments cannot invoke Spear', 'PULL_REQUEST_COMMENT_REJECTED')
    return value

def _issue_comments(issue_number: int) -> list[dict[str, Any]]:
    raw = _run(['gh', 'api', '--paginate', '--slurp', f'repos/{REPOSITORY}/issues/{issue_number}/comments'])
    try:
        pages = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpearIssueIngressError('Issue comment history was not JSON', 'COMMENT_HISTORY_FAILED', 'READBACK') from exc
    if not isinstance(pages, list):
        raise SpearIssueIngressError('Issue comment history malformed', 'COMMENT_HISTORY_FAILED', 'READBACK')
    comments: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, list) or any((not isinstance(item, dict) for item in page)):
            raise SpearIssueIngressError('Issue comment history malformed', 'COMMENT_HISTORY_FAILED', 'READBACK')
        comments.extend(page)
    return comments

def _post(issue_number: int, marker: str, body: dict[str, Any]) -> dict[str, Any]:
    rendered = marker + '\n' + stable_json(body)
    if len(rendered.encode('utf-8')) > 60000:
        raise SpearIssueIngressError('sanitized Issue receipt exceeds bounded size', 'RECEIPT_SIZE_REJECTED', 'RECEIPT')
    completed = subprocess.run(['gh', 'api', '--method', 'POST', f'repos/{REPOSITORY}/issues/{issue_number}/comments', '-f', f'body={rendered}'], check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise SpearIssueIngressError('sanitized Issue receipt could not be written', 'RECEIPT_WRITE_FAILED', 'RECEIPT')
    try:
        receipt = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SpearIssueIngressError('Issue receipt writeback was not JSON', 'RECEIPT_WRITE_FAILED', 'RECEIPT') from exc
    if not isinstance(receipt, dict) or not isinstance(receipt.get('id'), int) or receipt.get('body') != rendered:
        raise SpearIssueIngressError('Issue receipt writeback mismatch', 'RECEIPT_WRITE_FAILED', 'RECEIPT')
    return receipt

def _main_sha() -> str:
    value = _api_json(f'repos/{REPOSITORY}/commits/main')
    sha = value.get('sha') if isinstance(value, dict) else None
    if not isinstance(sha, str) or not SHA40.fullmatch(sha):
        raise SpearIssueIngressError('canonical main readback failed', 'MAIN_READBACK_FAILED', 'READBACK')
    return sha

def _mission_manifest(issue: dict[str, Any]) -> dict[str, Any]:
    match = MISSION_BLOCK.search(issue['body'])
    if not match:
        raise SpearIssueIngressError('Mission manifest is absent', 'MISSION_MANIFEST_REJECTED')
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise SpearIssueIngressError('Mission manifest is invalid JSON', 'MISSION_MANIFEST_REJECTED') from exc
    if not isinstance(value, dict) or value.get('repository') != REPOSITORY or value.get('issue_number') != issue['number']:
        raise SpearIssueIngressError('Mission manifest identity mismatch', 'MISSION_MANIFEST_REJECTED')
    return value

def _trusted_event() -> tuple[dict[str, Any], dict[str, Any], str, dict[str, str]]:
    required = ('GITHUB_EVENT_PATH', 'GITHUB_REPOSITORY', 'GITHUB_REPOSITORY_OWNER', 'GITHUB_ACTOR', 'GITHUB_TRIGGERING_ACTOR', 'GITHUB_SHA', 'GITHUB_WORKFLOW_REF', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT')
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SpearIssueIngressError('trusted workflow environment is incomplete', 'TRUSTED_ENVIRONMENT_MISSING')
    if os.environ['GITHUB_REPOSITORY'] != REPOSITORY or os.environ['GITHUB_REPOSITORY_OWNER'] != OWNER:
        raise SpearIssueIngressError('repository identity mismatch', 'REPOSITORY_IDENTITY_MISMATCH')
    if os.environ['GITHUB_ACTOR'] != OWNER or os.environ['GITHUB_TRIGGERING_ACTOR'] != OWNER:
        raise SpearIssueIngressError('owner actor is required', 'OWNER_IDENTITY_REJECTED')
    try:
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpearIssueIngressError('trusted event is unreadable', 'TRUSTED_EVENT_REJECTED') from exc
    issue = event.get('issue') if isinstance(event, dict) else None
    comment = event.get('comment') if isinstance(event, dict) else None
    if not isinstance(issue, dict) or not isinstance(comment, dict) or (not isinstance(comment.get('body'), str)):
        raise SpearIssueIngressError('trusted event shape rejected', 'TRUSTED_EVENT_REJECTED')
    if issue.get('pull_request') is not None:
        raise SpearIssueIngressError('pull-request comments cannot invoke Spear', 'PULL_REQUEST_COMMENT_REJECTED')
    current = _comment(int(comment['id']))
    if current.get('body') != comment.get('body'):
        raise SpearIssueIngressError('triggering comment was edited', 'COMMENT_DRIFT')
    if _main_sha() != os.environ['GITHUB_SHA']:
        raise SpearIssueIngressError('workflow source or canonical main drifted', 'WORKFLOW_SOURCE_DRIFT')
    return (issue, current, comment['body'], {name: os.environ[name] for name in required})

def _keys() -> tuple[str, str, str]:
    private_b64 = os.environ.get('ATLAS_SPEAR_INGRESS_PRIVATE_KEY_V1', '')
    public_b64 = os.environ.get('ATLAS_SPEAR_INGRESS_PUBLIC_KEY_V1', '')
    expected_id = os.environ.get('ATLAS_SPEAR_INGRESS_KEY_ID_V1', '')
    if not private_b64 or not public_b64 or (not expected_id):
        raise SpearIssueIngressError('Spear ingress environment key is unavailable', 'INGRESS_KEY_UNAVAILABLE')
    from .spear_issue_crypto import _b64decode
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    public_raw = _b64decode(public_b64, 'public key')
    private_raw = _b64decode(private_b64, 'private key')
    if len(private_raw) != 32 or len(public_raw) != 32:
        raise SpearIssueIngressError('Spear ingress key size mismatch', 'INGRESS_KEY_MISMATCH')
    derived_public = public_key_bytes(X25519PrivateKey.from_private_bytes(private_raw).public_key())
    if derived_public != public_raw or key_id(public_raw) != expected_id:
        raise SpearIssueIngressError('Spear ingress keypair identity mismatch', 'INGRESS_KEY_MISMATCH')
    return (private_b64, public_b64, expected_id)
