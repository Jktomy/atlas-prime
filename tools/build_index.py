#!/usr/bin/env python3
"""Build bounded Atlas Prime generated-index support reports.

This implementation is governed by:
specs/generated/atlas-generated-index-contract-v1.md

It uses the Python standard library only. It has no network, subprocess,
GitHub, delete, move, or rename capability.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
from pathlib import Path
import re
import sys
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

GENERATOR_VERSION = "1.0.0"

APPROVED_OUTPUTS: tuple[str, ...] = (
    "atlas-file-inventory.md",
    "atlas-metadata-inventory.md",
    "atlas-routing-inventory.md",
    "atlas-orphan-report.md",
    "atlas-duplicate-scope-report.md",
)

ROUTING_SURFACES: tuple[str, ...] = (
    "README.md",
    "bootstrap.md",
    "atlas-start-here.md",
    "atlas-index.md",
    "atlas-protocol-registry.md",
    "atlas-command-surface.md",
    "migration/atlas-codex/README.md",
    "migration/atlas-codex/migration-map.md",
    "specs/atlas-prime/codex-to-prime-migration-contract-v2.md",
)

SKIP_DIR_NAMES = frozenset({".git", ".github", "generated", "__pycache__"})

HIGH_CONFIDENCE_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?i)\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|"
        r"password|secret|private[_ -]?key)\b\s*[:=]\s*"
        r"[\"']?[A-Za-z0-9+/=_\-]{12,}"
    ),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:mfa|recovery code|seed phrase)\b\s*[:=]\s*\S+"
    ),
)

SENSITIVE_POLICY_TERMS: tuple[str, ...] = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private key",
    "mfa",
    "recovery code",
    "seed phrase",
    "phi",
    "raw finance evidence",
    "account data",
    "private runtime value",
    ".env",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_repo_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"Repository root is not a directory: {resolved}")
    return resolved


def normalize_output_dir(path: Path) -> Path:
    return path.expanduser().resolve()


def repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def read_utf8(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is not permitted in scanned source: {path}")
    return data.decode("utf-8")


def encode_utf8_lf(text: str) -> bytes:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized.encode("utf-8")


def resolve_generated_date(explicit: Optional[str]) -> str:
    if explicit:
        try:
            return dt.date.fromisoformat(explicit).isoformat()
        except ValueError as error:
            raise ValueError(
                f"--generated-date must be YYYY-MM-DD: {explicit}"
            ) from error

    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch:
        try:
            timestamp = int(source_date_epoch)
            return dt.datetime.fromtimestamp(
                timestamp, tz=dt.timezone.utc
            ).date().isoformat()
        except (ValueError, OverflowError, OSError) as error:
            raise ValueError("SOURCE_DATE_EPOCH must be a valid integer epoch") from error

    return dt.date.today().isoformat()


def validate_source_revision(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Source revision must not be empty")
    if len(normalized) > 160:
        raise ValueError("Source revision is too long")
    if not re.fullmatch(r"[A-Za-z0-9._/@:+\-]+", normalized):
        raise ValueError(
            "Source revision contains unsupported characters: "
            f"{normalized!r}"
        )
    return normalized


def iter_repo_markdown_files(repo_root: Path) -> Iterable[Path]:
    for path in sorted(repo_root.rglob("*.md")):
        relative_parts = path.relative_to(repo_root).parts
        if any(part in SKIP_DIR_NAMES for part in relative_parts):
            continue
        if path.is_file():
            yield path


def parse_simple_frontmatter(text: str) -> Optional[Dict[str, object]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end_index: Optional[int] = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return None

    data: Dict[str, object] = {}
    current_key: Optional[str] = None

    for raw_line in lines[1:end_index]:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped and not stripped.startswith("- "):
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                current_key = None
                continue
            data[key] = value.strip("'\"") if value else ""
            current_key = key
            continue

        if stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip("'\"")
            existing = data.get(current_key)
            if isinstance(existing, list):
                existing.append(item)
            elif existing in ("", None):
                data[current_key] = [item]
            else:
                data[current_key] = [str(existing), item]

    return data


def infer_source_area(relative: str) -> str:
    if "/" not in relative:
        return "root"
    return relative.split("/", 1)[0]


def sensitive_hint_status(text: str) -> str:
    if any(pattern.search(text) for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS):
        return "review"
    lowered = text.lower()
    if any(term in lowered for term in SENSITIVE_POLICY_TERMS):
        return "policy-reference"
    return "none"


def contains_high_confidence_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in HIGH_CONFIDENCE_SECRET_PATTERNS)


def flatten_metadata_value(value: object) -> str:
    if isinstance(value, list):
        return " ; ".join(str(item) for item in value)
    return str(value or "")


def safe_table_cell(value: object, *, limit: int = 500) -> str:
    text = flatten_metadata_value(value)
    if contains_high_confidence_secret(text):
        return "[REDACTED]"
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\\", "\\\\").replace("|", "\\|").replace("`", "'")
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text or "missing"


def load_routing_text(
    repo_root: Path,
    routing_surfaces: Sequence[str] = ROUTING_SURFACES,
) -> str:
    chunks: List[str] = []
    for relative in routing_surfaces:
        path = repo_root / relative
        if path.is_file():
            chunks.append(read_utf8(path))
    return "\n".join(chunks)


def collect_file_records(repo_root: Path) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for path in iter_repo_markdown_files(repo_root):
        relative = repo_relative(path, repo_root)
        text = read_utf8(path)
        frontmatter = parse_simple_frontmatter(text)
        records.append(
            {
                "path": relative,
                "area": infer_source_area(relative),
                "has_frontmatter": frontmatter is not None,
                "frontmatter": frontmatter or {},
                "sensitive_hint": sensitive_hint_status(text),
            }
        )
    return records


def generated_header(
    title: str,
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    return (
        f"# {title}\n\n"
        f"Generated: {generated_date}\n"
        f"Source revision: `{source_revision}`\n"
        f"Generator version: `{GENERATOR_VERSION}`\n"
        "Status: Generated support artifact\n\n"
        "> Generated indexes report. They do not govern.\n"
        "> Contract: `specs/generated/atlas-generated-index-contract-v1.md`.\n\n"
    )


def build_file_inventory(
    records: Sequence[Mapping[str, object]],
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    lines = [
        generated_header(
            "Atlas File Inventory",
            generated_date=generated_date,
            source_revision=source_revision,
        ),
        "| Path | Area | Metadata | Sensitive hint |",
        "|---|---|---|---|",
    ]
    for record in records:
        metadata = "yes" if record["has_frontmatter"] else "no"
        lines.append(
            f"| `{record['path']}` | {safe_table_cell(record['area'])} | "
            f"{metadata} | {safe_table_cell(record['sensitive_hint'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_metadata_inventory(
    records: Sequence[Mapping[str, object]],
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    lines = [
        generated_header(
            "Atlas Metadata Inventory",
            generated_date=generated_date,
            source_revision=source_revision,
        ),
        "| Path | Status | Source type | Canonical scope | Protected level |",
        "|---|---|---|---|---|",
    ]
    for record in records:
        frontmatter = record["frontmatter"]
        if not isinstance(frontmatter, dict) or not frontmatter:
            lines.append(
                f"| `{record['path']}` | missing | missing | missing | missing |"
            )
            continue
        lines.append(
            f"| `{record['path']}` | "
            f"{safe_table_cell(frontmatter.get('status'))} | "
            f"{safe_table_cell(frontmatter.get('source_type'))} | "
            f"{safe_table_cell(frontmatter.get('canonical_scope'))} | "
            f"{safe_table_cell(frontmatter.get('protected_level'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_routing_inventory(
    records: Sequence[Mapping[str, object]],
    routing_text: str,
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    lines = [
        generated_header(
            "Atlas Routing Inventory",
            generated_date=generated_date,
            source_revision=source_revision,
        ),
        "| Path | Routed by known Prime surfaces |",
        "|---|---|",
    ]
    for record in records:
        relative = str(record["path"])
        routed = "yes" if relative in routing_text else "no"
        lines.append(f"| `{relative}` | {routed} |")
    lines.append("")
    return "\n".join(lines)


def is_active_metadata(frontmatter: object) -> bool:
    if not isinstance(frontmatter, dict) or not frontmatter:
        return False
    status = str(frontmatter.get("status") or "").strip().lower()
    source_type = str(frontmatter.get("source_type") or "").strip().lower()
    if status in {"archive", "archived", "retired"}:
        return False
    if source_type in {"archive", "archived", "retired"}:
        return False
    return True


def build_orphan_report(
    records: Sequence[Mapping[str, object]],
    routing_text: str,
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    lines = [
        generated_header(
            "Atlas Orphan Candidate Report",
            generated_date=generated_date,
            source_revision=source_revision,
        ),
        (
            "An orphan candidate is not deletion approval. Review routing, "
            "support-file status, archive status, and metadata before action.\n"
        ),
        "| Path | Reason |",
        "|---|---|",
    ]
    for record in records:
        relative = str(record["path"])
        if not is_active_metadata(record["frontmatter"]):
            continue
        if relative in routing_text:
            continue
        lines.append(
            f"| `{relative}` | active metadata-bearing file not found in "
            "known Prime routing surfaces |"
        )
    lines.append("")
    return "\n".join(lines)


def normalize_scope(value: object) -> str:
    text = flatten_metadata_value(value).strip().lower()
    return re.sub(r"\s+", " ", text)


def build_duplicate_scope_report(
    records: Sequence[Mapping[str, object]],
    *,
    generated_date: str,
    source_revision: str,
) -> str:
    scopes: Dict[str, List[str]] = {}
    display_values: Dict[str, str] = {}

    for record in records:
        frontmatter = record["frontmatter"]
        if not isinstance(frontmatter, dict):
            continue
        raw_scope = frontmatter.get("canonical_scope")
        normalized = normalize_scope(raw_scope)
        if not normalized:
            continue
        scopes.setdefault(normalized, []).append(str(record["path"]))
        display_values.setdefault(normalized, safe_table_cell(raw_scope))

    lines = [
        generated_header(
            "Atlas Duplicate Canonical-Scope Report",
            generated_date=generated_date,
            source_revision=source_revision,
        ),
        "| Canonical scope | Files |",
        "|---|---|",
    ]
    duplicates_found = False
    for normalized, paths in sorted(scopes.items()):
        if len(paths) < 2:
            continue
        duplicates_found = True
        joined = "<br>".join(f"`{path}`" for path in sorted(paths))
        lines.append(f"| {display_values[normalized]} | {joined} |")
    if not duplicates_found:
        lines.append("| none | none |")
    lines.append("")
    return "\n".join(lines)


def build_repository_outputs(
    *,
    repo_root: Path,
    generated_date: str,
    source_revision: str,
    routing_surfaces: Sequence[str] = ROUTING_SURFACES,
) -> Dict[str, bytes]:
    root = normalize_repo_root(repo_root)
    date_value = resolve_generated_date(generated_date)
    revision = validate_source_revision(source_revision)
    records = collect_file_records(root)
    routing_text = load_routing_text(root, routing_surfaces)

    text_outputs = {
        "atlas-file-inventory.md": build_file_inventory(
            records,
            generated_date=date_value,
            source_revision=revision,
        ),
        "atlas-metadata-inventory.md": build_metadata_inventory(
            records,
            generated_date=date_value,
            source_revision=revision,
        ),
        "atlas-routing-inventory.md": build_routing_inventory(
            records,
            routing_text,
            generated_date=date_value,
            source_revision=revision,
        ),
        "atlas-orphan-report.md": build_orphan_report(
            records,
            routing_text,
            generated_date=date_value,
            source_revision=revision,
        ),
        "atlas-duplicate-scope-report.md": build_duplicate_scope_report(
            records,
            generated_date=date_value,
            source_revision=revision,
        ),
    }

    if set(text_outputs) != set(APPROVED_OUTPUTS):
        raise RuntimeError("Internal generated-output allowlist mismatch")

    return {
        filename: encode_utf8_lf(text_outputs[filename])
        for filename in APPROVED_OUTPUTS
    }


def validate_output_mapping(outputs: Mapping[str, bytes]) -> None:
    names = set(outputs)
    if names != set(APPROVED_OUTPUTS):
        missing = sorted(set(APPROVED_OUTPUTS) - names)
        extra = sorted(names - set(APPROVED_OUTPUTS))
        raise ValueError(
            f"Output mapping mismatch. Missing={missing}; extra={extra}"
        )
    for filename in names:
        if Path(filename).name != filename:
            raise ValueError(f"Output filename must be a basename: {filename}")


def write_outputs(output_dir: Path, outputs: Mapping[str, bytes]) -> None:
    validate_output_mapping(outputs)
    directory = normalize_output_dir(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    for filename in APPROVED_OUTPUTS:
        target = directory / filename
        if target.parent != directory:
            raise ValueError(f"Refusing output outside selected directory: {target}")
        target.write_bytes(outputs[filename])


def check_outputs(output_dir: Path, outputs: Mapping[str, bytes]) -> List[str]:
    validate_output_mapping(outputs)
    directory = normalize_output_dir(output_dir)
    mismatches: List[str] = []
    for filename in APPROVED_OUTPUTS:
        target = directory / filename
        if not target.is_file() or target.read_bytes() != outputs[filename]:
            mismatches.append(filename)
    return mismatches


def describe_outputs(output_dir: Path, outputs: Mapping[str, bytes]) -> List[str]:
    validate_output_mapping(outputs)
    directory = normalize_output_dir(output_dir)
    return [
        (
            f"{(directory / filename).as_posix()} "
            f"bytes={len(outputs[filename])} "
            f"sha256={sha256_bytes(outputs[filename])}"
        )
        for filename in APPROVED_OUTPUTS
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build bounded Atlas Prime generated-index support reports."
    )
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_root,
        help="Repository root to scan. Defaults to this script's repository.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to <repo-root>/generated.",
    )
    parser.add_argument(
        "--generated-date",
        default=None,
        help="ISO date YYYY-MM-DD. Authoritative runs must pass this explicitly.",
    )
    parser.add_argument(
        "--source-revision",
        default=os.environ.get("ATLAS_SOURCE_REVISION", "UNBOUND"),
        help="Source revision embedded in report headers.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and describe outputs without writing.",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Return success only when selected outputs are byte-current.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = normalize_repo_root(args.repo_root)
    output_dir = (
        normalize_output_dir(args.output_dir)
        if args.output_dir is not None
        else repo_root / "generated"
    )
    generated_date = resolve_generated_date(args.generated_date)
    source_revision = validate_source_revision(args.source_revision)

    outputs = build_repository_outputs(
        repo_root=repo_root,
        generated_date=generated_date,
        source_revision=source_revision,
    )

    if args.dry_run:
        for line in describe_outputs(output_dir, outputs):
            print(f"DRY RUN: {line}")
        print("No files were written.")
        return 0

    if args.check:
        mismatches = check_outputs(output_dir, outputs)
        if mismatches:
            for filename in mismatches:
                print(f"STALE OR MISSING: {(output_dir / filename).as_posix()}")
            return 1
        print("Generated indexes are current.")
        return 0

    write_outputs(output_dir, outputs)
    for line in describe_outputs(output_dir, outputs):
        print(f"WROTE: {line}")
    print("Atlas Prime generated-index build complete.")
    print("Generated indexes report. They do not govern.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
