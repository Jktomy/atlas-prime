#!/usr/bin/env python3
"""Build deterministic Atlas projection diagnostics.

This tool is bounded by governance/source-lifecycle.md.

It reads repository Markdown and normally evaluates the five approved reports
inside temporary storage. An explicit output directory remains available for
noncanonical inspection and historical compatibility. Projections report;
they do not govern.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

GENERATOR_FORMAT = "2"
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[1]

APPROVED_OUTPUTS: Tuple[str, ...] = (
    "atlas-duplicate-scope-report.md",
    "atlas-file-inventory.md",
    "atlas-metadata-inventory.md",
    "atlas-orphan-report.md",
    "atlas-routing-inventory.md",
)

ROUTING_SURFACES: Tuple[str, ...] = (
    "README.md",
    "bootstrap.md",
    "atlas-start-here.md",
    "routing/command-surfaces.md",
    "projects/project-registry.md",
    "operations/operation-registry.md",
    "quest-board/quest-board-v1.json",
)

SKIP_DIRS = frozenset({".git", ".github"})

SENSITIVE_REVIEW_PATTERNS = (
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key)\s*[:=]",
    r"(?i)(password|secret|token)\s*[:=]\s*[^\s`'\"<>{}]+",
    r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)(mfa|recovery code)\s*[:=]\s*[^\s`'\"<>{}]+",
)

SENSITIVE_POLICY_TERMS = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private key",
    "mfa",
    "recovery code",
    "phi",
    "raw finance evidence",
    "private runtime value",
    ".env",
)

SourceDocument = Tuple[str, Path, bytes, str]


def normalized_repo_path(path: Path, repo_root: Path) -> str:
    """Return a stable POSIX repository-relative path."""

    return path.relative_to(repo_root).as_posix()


def read_text_strict(path: Path) -> str:
    """Read strict UTF-8 and fail rather than replacing invalid bytes."""

    return path.read_bytes().decode("utf-8")


def iter_repo_markdown_files(repo_root: Path) -> Iterable[Tuple[str, Path]]:
    """Yield source Markdown in normalized repository-relative order."""

    candidates: List[Tuple[str, Path]] = []
    for path in repo_root.rglob("*.md"):
        relative = path.relative_to(repo_root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if relative.parts and relative.parts[0] == "generated":
            continue
        candidates.append((relative.as_posix(), path))

    for item in sorted(candidates, key=lambda value: value[0]):
        yield item


def load_source_documents(repo_root: Path) -> List[SourceDocument]:
    documents: List[SourceDocument] = []
    for relative, path in iter_repo_markdown_files(repo_root):
        text = path.read_bytes().decode("utf-8")
        normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized_raw = normalized_text.encode("utf-8")
        documents.append((relative, path, normalized_raw, normalized_text))
    return documents


def compute_source_fingerprint(documents: Sequence[SourceDocument]) -> str:
    """Hash normalized source paths and LF-normalized UTF-8 bytes."""

    digest = hashlib.sha256()
    digest.update(f"ATLAS_GENERATED_INDEX_SOURCE_V{GENERATOR_FORMAT}\0".encode("ascii"))
    for relative, _path, raw, _text in documents:
        encoded_path = relative.encode("utf-8")
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return digest.hexdigest()


def parse_simple_frontmatter(text: str) -> Optional[Dict[str, object]]:
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return None

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return None

    data: Dict[str, object] = {}
    current_key: Optional[str] = None

    for raw_line in lines[1:end_index]:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if ":" in stripped and not stripped.startswith("- "):
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            data[key] = "" if value == "" else value.strip("'\"")
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
    if relative.startswith("projects/"):
        return "projects"
    if relative.startswith("operations/"):
        return "operations"
    if relative.startswith("governance/"):
        return "governance"
    if relative.startswith("quests/") or relative.startswith("quest-board/"):
        return "quests"
    if relative.startswith("infrastructure/"):
        return "infrastructure"
    if relative.startswith("recovery/"):
        return "recovery"
    if relative.startswith("routing/"):
        return "routing"
    if relative.startswith("safety/"):
        return "safety"
    if relative.startswith("knowledge/"):
        return "knowledge"
    if relative.startswith("protocols/"):
        return "protocols"
    if relative.startswith("artemis/"):
        return "artemis"
    if relative.startswith("templates/"):
        return "templates"
    if relative.startswith("tools/"):
        return "tools"
    if relative.startswith("atlas-prime-addenda/"):
        return "atlas-prime-addenda"
    if relative.startswith("session-harvests/"):
        return "session-harvests"
    if relative.startswith("app-harvests/"):
        return "app-harvests"
    if "/" not in relative:
        return "root"
    return relative.split("/", 1)[0]


def load_routing_text(repo_root: Path) -> str:
    chunks: List[str] = []

    for relative in ROUTING_SURFACES:
        path = repo_root / relative
        if path.exists():
            chunks.append(read_text_strict(path))

    return "\n".join(chunks)


def sensitive_hint_status(text: str) -> str:
    for pattern in SENSITIVE_REVIEW_PATTERNS:
        if re.search(pattern, text):
            return "review"

    lowered = text.lower()
    if any(term in lowered for term in SENSITIVE_POLICY_TERMS):
        return "policy-reference"

    return "none"


def generated_header(title: str, source_fingerprint: str) -> str:
    return (
        f"# {title}\n\n"
        f"Source fingerprint: sha256:{source_fingerprint}\n"
        f"Generator format: {GENERATOR_FORMAT}\n"
        "Status: Generated support artifact\n\n"
        "> Generated indexes report. They do not govern.\n"
        "> See `governance/source-lifecycle.md`.\n\n"
    )


def collect_file_records(documents: Sequence[SourceDocument]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []

    for relative, _path, _raw, text in documents:
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


def build_file_inventory(
    records: Sequence[Mapping[str, object]], source_fingerprint: str
) -> str:
    lines = [generated_header("Atlas File Inventory", source_fingerprint)]
    lines.append("| Path | Area | Metadata | Sensitive hint |")
    lines.append("|---|---|---|---|")

    for record in records:
        metadata = "yes" if record["has_frontmatter"] else "no"
        sensitive = str(record["sensitive_hint"])
        lines.append(
            f"| `{record['path']}` | {record['area']} | {metadata} | {sensitive} |"
        )

    lines.append("")
    return "\n".join(lines)


def build_metadata_inventory(
    records: Sequence[Mapping[str, object]], source_fingerprint: str
) -> str:
    lines = [generated_header("Atlas Metadata Inventory", source_fingerprint)]
    lines.append("| Path | Status | Source type | Canonical scope | Protected level |")
    lines.append("|---|---|---|---|---|")

    for record in records:
        frontmatter = record["frontmatter"]
        if not isinstance(frontmatter, dict) or not frontmatter:
            lines.append(f"| `{record['path']}` | missing | missing | missing | missing |")
            continue

        status = str(frontmatter.get("status") or "")
        source_type = str(frontmatter.get("source_type") or "")
        canonical_scope = str(frontmatter.get("canonical_scope") or "")
        protected_level = str(frontmatter.get("protected_level") or "")

        lines.append(
            f"| `{record['path']}` | {status or 'missing'} | "
            f"{source_type or 'missing'} | {canonical_scope or 'missing'} | "
            f"{protected_level or 'missing'} |"
        )

    lines.append("")
    return "\n".join(lines)


def build_routing_inventory(
    records: Sequence[Mapping[str, object]],
    routing_text: str,
    source_fingerprint: str,
) -> str:
    lines = [generated_header("Atlas Routing Inventory", source_fingerprint)]
    lines.append("| Path | Routed by known surfaces |")
    lines.append("|---|---|")

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

    if status in {"archive", "retired"}:
        return False

    if source_type in {"archive", "retired"}:
        return False

    return True


def build_orphan_report(
    records: Sequence[Mapping[str, object]],
    routing_text: str,
    source_fingerprint: str,
) -> str:
    lines = [generated_header("Atlas Orphan Candidate Report", source_fingerprint)]
    lines.append(
        "An orphan candidate is not deletion approval. "
        "Review routing, support-file status, archive status, and metadata before action.\n"
    )
    lines.append("| Path | Reason |")
    lines.append("|---|---|")

    for record in records:
        relative = str(record["path"])
        frontmatter = record["frontmatter"]

        if not is_active_metadata(frontmatter):
            continue

        if relative in routing_text:
            continue

        lines.append(
            f"| `{relative}` | active metadata-bearing file not found in routing surfaces |"
        )

    lines.append("")
    return "\n".join(lines)


def normalize_scope(value: object) -> str:
    if isinstance(value, list):
        value = " ".join(str(item) for item in value)

    text = str(value or "")
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def build_duplicate_scope_report(
    records: Sequence[Mapping[str, object]], source_fingerprint: str
) -> str:
    scopes: Dict[str, List[str]] = {}

    for record in records:
        frontmatter = record["frontmatter"]
        if not isinstance(frontmatter, dict):
            continue

        scope = normalize_scope(frontmatter.get("canonical_scope"))
        if not scope:
            continue

        scopes.setdefault(scope, []).append(str(record["path"]))

    lines = [
        generated_header("Atlas Duplicate Canonical-Scope Report", source_fingerprint)
    ]
    lines.append("| Canonical scope | Files |")
    lines.append("|---|---|")

    duplicates_found = False

    for scope, paths in sorted(scopes.items()):
        if len(paths) < 2:
            continue

        duplicates_found = True
        joined = "<br>".join(f"`{path}`" for path in sorted(paths))
        lines.append(f"| {scope} | {joined} |")

    if not duplicates_found:
        lines.append("| none | none |")

    lines.append("")
    return "\n".join(lines)


def build_outputs(repo_root: Path) -> Tuple[Dict[str, str], str]:
    documents = load_source_documents(repo_root)
    source_fingerprint = compute_source_fingerprint(documents)
    records = collect_file_records(documents)
    routing_text = load_routing_text(repo_root)

    outputs = {
        "atlas-duplicate-scope-report.md": build_duplicate_scope_report(
            records, source_fingerprint
        ),
        "atlas-file-inventory.md": build_file_inventory(records, source_fingerprint),
        "atlas-metadata-inventory.md": build_metadata_inventory(
            records, source_fingerprint
        ),
        "atlas-orphan-report.md": build_orphan_report(
            records, routing_text, source_fingerprint
        ),
        "atlas-routing-inventory.md": build_routing_inventory(
            records, routing_text, source_fingerprint
        ),
    }

    if tuple(sorted(outputs)) != APPROVED_OUTPUTS:
        raise ValueError("Generated output set does not match the approved output set.")

    return outputs, source_fingerprint


def output_bytes(content: str) -> bytes:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized.encode("utf-8")


def build_diagnostic_receipt(repo_root: Path) -> Dict[str, object]:
    """Reproduce all five projections twice and verify temporary byte identity."""

    first, source_fingerprint = build_outputs(repo_root)
    second, repeated_fingerprint = build_outputs(repo_root)
    if source_fingerprint != repeated_fingerprint or first != second:
        raise ValueError("Repeated generated projection build was not byte-identical.")

    records: List[Dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="atlas-projection-diagnostics-") as raw:
        diagnostic_root = Path(raw)
        for filename in APPROVED_OUTPUTS:
            data = output_bytes(first[filename])
            target = diagnostic_root / filename
            target.write_bytes(data)
            if target.read_bytes() != data:
                raise ValueError(f"Temporary diagnostic readback failed: {filename}")
            records.append(
                {
                    "path": filename,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size": len(data),
                }
            )

    return {
        "schema_id": "atlas.generated-projection-diagnostics.v1",
        "result": "PASS",
        "generator_format": GENERATOR_FORMAT,
        "source_fingerprint": f"sha256:{source_fingerprint}",
        "temporary_storage": True,
        "output_count": len(records),
        "outputs": records,
    }


def write_outputs(
    outputs: Mapping[str, str], output_dir: Path, *, dry_run: bool = False
) -> Dict[str, str]:
    output_dir = output_dir.resolve()
    hashes: Dict[str, str] = {}

    for filename in APPROVED_OUTPUTS:
        if filename not in outputs:
            raise ValueError(f"Missing approved output: {filename}")

        target = output_dir / filename
        if target.parent != output_dir:
            raise ValueError(f"Refusing nested or escaped output path: {target}")

        data = output_bytes(outputs[filename])
        hashes[filename] = hashlib.sha256(data).hexdigest()

        if dry_run:
            print(f"DRY RUN: would write {target}")
            continue

        output_dir.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(data.decode("utf-8"))
        print(f"WROTE: {target}")

    return hashes


def compare_outputs(
    outputs: Mapping[str, str], compare_dir: Path
) -> Tuple[str, List[str]]:
    changed: List[str] = []

    for filename in APPROVED_OUTPUTS:
        expected = output_bytes(outputs[filename])
        target = compare_dir / filename
        if not target.is_file() or target.read_bytes() != expected:
            changed.append(filename)

    return ("CURRENT" if not changed else "STALE", changed)


def write_hash_file(hashes: Mapping[str, str], path: Path) -> None:
    lines = [f"{hashes[name]}  {name}" for name in APPROVED_OUTPUTS]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def write_status_file(
    path: Path,
    *,
    status: str,
    changed: Sequence[str],
    source_fingerprint: str,
) -> None:
    lines = [
        f"ATLAS_GENERATED_INDEX_STATUS={status}",
        f"SOURCE_FINGERPRINT=sha256:{source_fingerprint}",
        f"GENERATOR_FORMAT={GENERATOR_FORMAT}",
        f"CHANGED_FILES={','.join(changed) if changed else 'NONE'}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic Atlas generated index support artifacts."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="Repository root to scan.",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Build twice in temporary storage and emit one machine-readable receipt.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for the five generated Markdown outputs.",
    )
    parser.add_argument(
        "--compare-dir",
        type=Path,
        help="Optional committed-output directory to compare without failing on drift.",
    )
    parser.add_argument(
        "--hash-file",
        type=Path,
        help="Optional SHA256SUMS output path for the five generated Markdown files.",
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        help="Optional machine-readable status output path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute and report without writing generated Markdown.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    implicit_diagnostics = not any(
        (args.output_dir, args.compare_dir, args.hash_file, args.status_file)
    )
    if args.diagnostics or implicit_diagnostics:
        if any((args.output_dir, args.compare_dir, args.hash_file, args.status_file)):
            raise SystemExit("--diagnostics cannot be combined with materialization options")
        try:
            receipt = build_diagnostic_receipt(repo_root)
        except Exception as exc:
            receipt = {
                "schema_id": "atlas.generated-projection-diagnostics.v1",
                "result": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            print(json.dumps(receipt, sort_keys=True))
            return 1
        print(json.dumps(receipt, sort_keys=True))
        return 0

    output_dir = (args.output_dir or (repo_root / "generated")).resolve()

    outputs, source_fingerprint = build_outputs(repo_root)
    hashes = write_outputs(outputs, output_dir, dry_run=args.dry_run)

    status = "NOT_CHECKED"
    changed: List[str] = []
    if args.compare_dir is not None:
        status, changed = compare_outputs(outputs, args.compare_dir.resolve())

    if args.hash_file is not None and not args.dry_run:
        write_hash_file(hashes, args.hash_file.resolve())

    if args.status_file is not None and not args.dry_run:
        write_status_file(
            args.status_file.resolve(),
            status=status,
            changed=changed,
            source_fingerprint=source_fingerprint,
        )

    print(f"Source fingerprint: sha256:{source_fingerprint}")
    print(f"Generator format: {GENERATOR_FORMAT}")
    print(f"Generated index status: {status}")
    if changed:
        print("Changed generated outputs:")
        for filename in changed:
            print(f"- {filename}")
    print("Atlas generated index build complete.")
    print("Generated indexes report. They do not govern.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
