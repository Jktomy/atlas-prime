from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .compile import compile_packet
from .git_adapter import assert_git_repository, blob_sha_at_commit, resolve_ref
from .models import BASE_BRANCH, COMPILER_VERSION, ContractIdentity, GitError, PolicyError
from .policy import (
    effective_limits,
    load_controlling_policies,
    load_source_metadata_schema,
    load_spear_overlay_policy,
    load_spear_packet_schema,
)
from .validate import (
    canonical_json_bytes,
    parse_base64_packet,
    parse_packet_file,
    validate_schema,
)

BOOTSTRAP_MAX_PACKET_BYTES = 1024 * 1024


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def _write_tree(root: Path, files: dict[str, str]) -> None:
    resolved_root = root.resolve()
    for rel, content in sorted(files.items()):
        target = (resolved_root / rel).resolve()
        if resolved_root not in target.parents and target != resolved_root:
            raise ValueError("proposed file path escaped output root")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_output_root(output_root: str, protected_roots: list[Path]) -> Path:
    raw = Path(output_root)
    resolved = raw.resolve(strict=False)
    for repo in protected_roots:
        repo_resolved = repo.resolve(strict=True)
        if resolved == repo_resolved or _is_relative_to(resolved, repo_resolved):
            raise PolicyError("output root may not equal or be inside a protected repository")
    if raw.exists():
        if raw.is_symlink():
            raise PolicyError("output root may not be a symlink")
        existing = list(raw.iterdir())
        if existing:
            raise PolicyError("output root must be absent or empty")
        for child in raw.rglob("*"):
            if child.is_symlink() or child.is_file():
                raise PolicyError("preexisting output root content is not allowed")
    return resolved


def build_base_state(repository: Path, base_commit: str, operations: list[dict]) -> dict[str, str | None]:
    state: dict[str, str | None] = {}
    for op in operations:
        path = op["path"]
        state[path] = blob_sha_at_commit(repository, base_commit, path)
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Athena's Spear S0 offline packet compiler")
    parser.add_argument("--packet", help="Path to UTF-8 JSON packet")
    parser.add_argument("--packet-b64", help="Base64-encoded UTF-8 JSON packet")
    parser.add_argument("--packet-sha256", required=True, help="Expected SHA-256 of exact decoded packet bytes")
    parser.add_argument("--repository", required=True, help="Target Atlas Prime checkout and source of controlling policy Git objects")
    parser.add_argument("--atlas-codex-repository", help="Canonical predecessor repository, used only for output-root protection")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args(argv)

    if bool(args.packet) == bool(args.packet_b64):
        raise SystemExit("provide exactly one of --packet or --packet-b64")

    repository = assert_git_repository(args.repository)
    protected_roots = [repository]
    if args.atlas_codex_repository:
        protected_roots.append(assert_git_repository(args.atlas_codex_repository))
    out = validate_output_root(args.output_root, protected_roots)

    if args.packet:
        packet, transport_sha, raw_packet = parse_packet_file(args.packet, args.packet_sha256, max_bytes=BOOTSTRAP_MAX_PACKET_BYTES)
    else:
        packet, transport_sha, raw_packet = parse_base64_packet(args.packet_b64, args.packet_sha256, max_bytes=BOOTSTRAP_MAX_PACKET_BYTES)

    if args.base_ref != BASE_BRANCH:
        raise PolicyError("S0 base ref must be main")
    resolved = resolve_ref(repository, args.base_ref)
    if resolved != packet["base_commit"]:
        raise GitError("stale_base_commit", "resolved main does not match packet base_commit")

    packet_schema_identity, schema, _schema_bytes = load_spear_packet_schema(str(repository), packet["base_commit"])
    overlay_identity, overlay, _overlay_bytes = load_spear_overlay_policy(str(repository), packet["base_commit"])
    validate_schema(packet, schema)
    controlling = load_controlling_policies(str(repository), packet["base_commit"])
    source_metadata_identity, source_metadata_schema = load_source_metadata_schema(str(repository), packet["base_commit"])
    limits = effective_limits(schema, overlay, controlling)
    if len(raw_packet) > limits["max_decoded_packet_bytes"]:
        raise PolicyError("decoded packet exceeds effective policy limit")
    base_state = build_base_state(repository, packet["base_commit"], packet["operations"])

    contract_identity = ContractIdentity(
        compiler_version=COMPILER_VERSION,
        packet_schema=packet_schema_identity,
        overlay_policy=overlay_identity,
        destination_policy=controlling["destination_identity"],
        protected_policy=controlling["protected_identity"],
        source_metadata_schema=source_metadata_identity,
    )
    result = compile_packet(
        packet,
        overlay,
        controlling,
        limits,
        contract_identity,
        base_state=base_state,
        transport_sha256=transport_sha,
        source_metadata_schema=source_metadata_schema,
    )

    if out.exists() and any(out.iterdir()):
        raise SystemExit("output root must be absent or empty")
    out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "normalized-packet.json", result.normalized_packet)
    _write_json(out / "operation-manifest.json", result.operation_manifest)
    _write_json(out / "validation-receipt.json", result.receipt)
    _write_tree(out / "proposed-tree", result.proposed_files)
    print(json.dumps({"compiler_version": __version__, "status": result.receipt["status"], "execution": result.receipt["execution_authorization_state"], "manifest_sha256": result.receipt["manifest_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
