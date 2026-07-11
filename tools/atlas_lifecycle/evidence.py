from __future__ import annotations

import hashlib
import io
import stat
import zipfile
import zlib
from pathlib import Path, PurePosixPath

from .errors import LifecycleError
from .jsonio import load_bounded, loads_bounded, read_bounded, stable_record_id
from .limits import (
    MAX_ARCHIVE_BYTES,
    MAX_ARCHIVE_MEMBER_BYTES,
    MAX_ARCHIVE_MEMBERS,
    MAX_ARCHIVE_PATH_BYTES,
    MAX_ARCHIVE_PATH_DEPTH,
    MAX_ARCHIVE_TOTAL_BYTES,
    MAX_COMPRESSION_RATIO,
)
from .schema import SchemaValidator


def _digest(path: Path) -> str:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise LifecycleError("DIGEST_INPUT_BOUNDARY", "digest input is unavailable or exceeds the trusted limit")
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return f"sha256:{hasher.hexdigest()}"


def verify_archive(path: Path) -> str:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise LifecycleError("ARCHIVE_BOUNDARY", "archive is unavailable or exceeds the trusted size limit")
    try:
        with path.open("rb") as handle:
            archive_bytes = handle.read(MAX_ARCHIVE_BYTES + 1)
    except OSError as exc:
        raise LifecycleError("ARCHIVE_BOUNDARY", "archive is unavailable or exceeds the trusted size limit") from exc
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise LifecycleError("ARCHIVE_BOUNDARY", "archive is unavailable or exceeds the trusted size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_MEMBERS:
                raise LifecycleError("ARCHIVE_MEMBER_LIMIT", "archive member count exceeds the trusted limit")
            seen: set[str] = set()
            total = 0
            actual_total = 0
            for member in members:
                pure = PurePosixPath(member.filename)
                if (
                    not member.filename
                    or "\\" in member.filename
                    or len(member.filename.encode("utf-8")) > MAX_ARCHIVE_PATH_BYTES
                    or len(pure.parts) > MAX_ARCHIVE_PATH_DEPTH
                    or pure.is_absolute()
                    or any(part in {"", ".", ".."} for part in pure.parts)
                ):
                    raise LifecycleError("ARCHIVE_PATH", "archive contains an unsafe member path")
                folded = member.filename.casefold()
                if folded in seen:
                    raise LifecycleError("ARCHIVE_COLLISION", "archive contains a case-fold path collision")
                seen.add(folded)
                mode = member.external_attr >> 16
                file_type = stat.S_IFMT(mode)
                if member.flag_bits & 0x1:
                    raise LifecycleError("ARCHIVE_ENCRYPTED", "encrypted archive members are forbidden")
                if stat.S_ISLNK(mode) or file_type not in {0, stat.S_IFREG, stat.S_IFDIR}:
                    raise LifecycleError("ARCHIVE_SPECIAL_FILE", "archive links and special files are forbidden")
                if member.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                    raise LifecycleError("ARCHIVE_MEMBER_SIZE", "archive member exceeds the trusted size limit")
                total += member.file_size
                if total > MAX_ARCHIVE_TOTAL_BYTES:
                    raise LifecycleError("ARCHIVE_TOTAL_SIZE", "archive expanded size exceeds the trusted limit")
                if member.file_size and member.compress_size == 0:
                    raise LifecycleError("ARCHIVE_RATIO", "archive compression ratio exceeds the trusted limit")
                if member.compress_size and member.file_size / member.compress_size > MAX_COMPRESSION_RATIO:
                    raise LifecycleError("ARCHIVE_RATIO", "archive compression ratio exceeds the trusted limit")
                if member.is_dir():
                    if member.file_size:
                        raise LifecycleError("ARCHIVE_DIRECTORY_DATA", "archive directory member contains data")
                    continue
                actual_size = 0
                try:
                    with archive.open(member, "r") as handle:
                        while True:
                            block = handle.read(min(1024 * 1024, MAX_ARCHIVE_MEMBER_BYTES - actual_size + 1))
                            if not block:
                                break
                            actual_size += len(block)
                            actual_total += len(block)
                            if actual_size > MAX_ARCHIVE_MEMBER_BYTES:
                                raise LifecycleError("ARCHIVE_MEMBER_SIZE", "archive member exceeds the trusted size limit")
                            if actual_total > MAX_ARCHIVE_TOTAL_BYTES:
                                raise LifecycleError("ARCHIVE_TOTAL_SIZE", "archive expanded size exceeds the trusted limit")
                except (EOFError, NotImplementedError, OSError, RuntimeError, zipfile.BadZipFile, zlib.error) as exc:
                    raise LifecycleError("ARCHIVE_MEMBER_INVALID", "archive member failed bounded integrity readback") from exc
                if actual_size != member.file_size:
                    raise LifecycleError("ARCHIVE_SIZE_MISMATCH", "archive member size does not match bounded readback")
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise LifecycleError("MALFORMED_ARCHIVE", "archive is not a valid ZIP") from exc
    return f"sha256:{hashlib.sha256(archive_bytes).hexdigest()}"


def verify_bound_evidence(
    archive_path: Path,
    sidecar_path: Path,
    receipt_path: Path,
    schema_dir: Path,
    contract_path: Path,
    trust_root_path: Path,
    trusted_root_dir: Path,
) -> str:
    evidence_paths = {
        archive_path.resolve(),
        sidecar_path.resolve(),
        receipt_path.resolve(),
    }
    if len(evidence_paths) != 3:
        raise LifecycleError("EVIDENCE_PATH_ALIAS", "archive, sidecar, and receipt must be independent files")
    root = trusted_root_dir.resolve()
    if trusted_root_dir.is_symlink() or not root.is_dir():
        raise LifecycleError("TRUST_ROOT_LOCATION", "repository-controlled trust-root directory is invalid")
    trust_path = trust_root_path.resolve()
    try:
        lexical_relative = trust_root_path.absolute().relative_to(trusted_root_dir.absolute())
    except ValueError as exc:
        raise LifecycleError(
            "TRUST_ROOT_LOCATION",
            "trust root must come from the repository-controlled trust-root directory",
        ) from exc
    cursor = trusted_root_dir.absolute()
    for part in lexical_relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise LifecycleError("TRUST_ROOT_LOCATION", "trust-root path may not traverse a link")
    try:
        trust_path.relative_to(root)
    except ValueError as exc:
        raise LifecycleError(
            "TRUST_ROOT_LOCATION",
            "trust root must come from the repository-controlled trust-root directory",
        ) from exc
    if trust_root_path.is_symlink() or not trust_path.is_file():
        raise LifecycleError("TRUST_ROOT_UNAVAILABLE", "trusted expectation is unavailable")
    trust = load_bounded(trust_path)
    if set(trust) != {
        "schema_id",
        "expected_subject_digest",
        "trusted_contract_digest",
        "trusted_schema_digest",
    } or trust.get("schema_id") != "atlas.lifecycle.trust-root.v1":
        raise LifecycleError("TRUST_ROOT_CONTRACT", "trusted expectation has an invalid contract")

    subject_digest = verify_archive(archive_path)
    if trust["expected_subject_digest"] != subject_digest:
        raise LifecycleError("TRUSTED_SUBJECT_MISMATCH", "archive does not match the external trusted expectation")
    sidecar_bytes = read_bounded(sidecar_path)
    sidecar = loads_bounded(sidecar_bytes, label=sidecar_path.name)
    if set(sidecar) != {"schema_id", "subject_digest"} or sidecar.get("schema_id") != "atlas.lifecycle.sidecar.v1":
        raise LifecycleError("UNTRUSTED_SIDECAR", "sidecar does not match the trusted contract")
    if sidecar.get("subject_digest") != subject_digest:
        raise LifecycleError("SIDECAR_SUBJECT_MISMATCH", "sidecar does not bind the verified archive")
    receipt = load_bounded(receipt_path)
    SchemaValidator(schema_dir).validate_record(receipt)
    if stable_record_id(receipt) != receipt.get("record_id"):
        raise LifecycleError("STABLE_ID_MISMATCH", "receipt ID does not match its canonical payload")
    contract = receipt["trusted_contract"]
    binding = receipt["independent_sidecar"]
    subject = receipt["subject"]
    actual_schema_digest = _digest(schema_dir / "lifecycle-receipt-v1.schema.json")
    actual_contract_digest = _digest(contract_path)
    if (
        trust["trusted_schema_digest"] != actual_schema_digest
        or trust["trusted_contract_digest"] != actual_contract_digest
        or contract["schema_digest"] != actual_schema_digest
        or contract["contract_digest"] != actual_contract_digest
    ):
        raise LifecycleError("TRUST_ANCHOR_MISMATCH", "receipt is not bound to the independently trusted contract")
    if subject["payload_digest"] != subject_digest or binding["subject_digest_binding"] != subject_digest:
        raise LifecycleError("RECEIPT_SUBJECT_MISMATCH", "receipt does not bind the verified archive")
    if binding["sidecar_digest"] != f"sha256:{hashlib.sha256(sidecar_bytes).hexdigest()}":
        raise LifecycleError("RECEIPT_SIDECAR_MISMATCH", "receipt does not bind the independent sidecar")
    return subject_digest
