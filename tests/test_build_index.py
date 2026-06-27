#!/usr/bin/env python3
"""Tests for the bounded Atlas Prime generated-index builder."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = REPO_ROOT / "tools" / "build_index.py"

SPEC = importlib.util.spec_from_file_location("atlas_build_index", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load builder: {BUILDER_PATH}")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    path.write_bytes(normalized.encode("utf-8"))


class BuildIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir(parents=True)

        write_text(
            self.root / "README.md",
            """---
title: Root
status: ACTIVE
source_type: ROUTING
canonical_scope: Root routing surface
protected_level: HIGH
---

Routes `docs/source-a.md`.
""",
        )
        write_text(
            self.root / "docs" / "source-a.md",
            """---
title: Source A
status: ACTIVE
source_type: STANDARD
canonical_scope: Shared clean scope
protected_level: MEDIUM
---

Clean source.
""",
        )
        write_text(
            self.root / "docs" / "source-b.md",
            """---
title: Source B
status: ACTIVE
source_type: STANDARD
canonical_scope: Shared clean scope
protected_level: MEDIUM
---

Another source.
""",
        )
        write_text(
            self.root / "docs" / "no-metadata.md",
            "# No metadata\n",
        )
        write_text(
            self.root / "generated" / "old-report.md",
            "# Must not be scanned\n",
        )
        write_text(
            self.root / ".github" / "ignored.md",
            "# Must not be scanned\n",
        )

        self.date = "2026-06-27"
        self.revision = "0123456789abcdef"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self):
        return builder.build_repository_outputs(
            repo_root=self.root,
            generated_date=self.date,
            source_revision=self.revision,
            routing_surfaces=("README.md",),
        )

    def test_exact_output_allowlist(self) -> None:
        outputs = self.build()
        self.assertEqual(set(outputs), set(builder.APPROVED_OUTPUTS))
        self.assertEqual(len(outputs), 5)

    def test_generated_and_github_directories_are_excluded(self) -> None:
        outputs = self.build()
        inventory = outputs["atlas-file-inventory.md"].decode("utf-8")
        self.assertIn("docs/source-a.md", inventory)
        self.assertNotIn("generated/old-report.md", inventory)
        self.assertNotIn(".github/ignored.md", inventory)

    def test_fixed_inputs_are_byte_deterministic(self) -> None:
        first = self.build()
        second = self.build()
        self.assertEqual(first, second)

    def test_write_boundary_and_no_source_mutation(self) -> None:
        before = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        output_dir = Path(self.temp.name) / "preview" / "generated"
        outputs = self.build()
        builder.write_outputs(output_dir, outputs)

        actual = sorted(path.name for path in output_dir.iterdir() if path.is_file())
        self.assertEqual(actual, sorted(builder.APPROVED_OUTPUTS))

        after = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_check_mode_detects_stale_output(self) -> None:
        output_dir = Path(self.temp.name) / "check" / "generated"
        outputs = self.build()
        builder.write_outputs(output_dir, outputs)
        self.assertEqual(builder.check_outputs(output_dir, outputs), [])

        target = output_dir / "atlas-file-inventory.md"
        target.write_bytes(target.read_bytes() + b"stale\n")
        self.assertEqual(
            builder.check_outputs(output_dir, outputs),
            ["atlas-file-inventory.md"],
        )

    def test_unknown_output_is_refused(self) -> None:
        outputs = self.build()
        outputs["not-approved.md"] = b"no\n"
        with self.assertRaises(ValueError):
            builder.write_outputs(Path(self.temp.name) / "generated", outputs)

    def test_sensitive_metadata_value_is_redacted(self) -> None:
        secret_value = "api_" + "key=" + "ABCDEFGHIJKL123456789"
        write_text(
            self.root / "docs" / "secret-a.md",
            f"""---
title: Secret A
status: ACTIVE
source_type: STANDARD
canonical_scope: {secret_value}
protected_level: CRITICAL
---

Policy text.
""",
        )
        write_text(
            self.root / "docs" / "secret-b.md",
            f"""---
title: Secret B
status: ACTIVE
source_type: STANDARD
canonical_scope: {secret_value}
protected_level: CRITICAL
---

Policy text.
""",
        )

        outputs = self.build()
        metadata = outputs["atlas-metadata-inventory.md"].decode("utf-8")
        duplicates = outputs["atlas-duplicate-scope-report.md"].decode("utf-8")
        self.assertNotIn("ABCDEFGHIJKL123456789", metadata)
        self.assertNotIn("ABCDEFGHIJKL123456789", duplicates)
        self.assertIn("[REDACTED]", metadata)
        self.assertIn("[REDACTED]", duplicates)

    def test_source_date_epoch_is_supported(self) -> None:
        previous = os.environ.get("SOURCE_DATE_EPOCH")
        os.environ["SOURCE_DATE_EPOCH"] = "1782518400"
        try:
            self.assertEqual(
                builder.resolve_generated_date(None),
                "2026-06-27",
            )
        finally:
            if previous is None:
                os.environ.pop("SOURCE_DATE_EPOCH", None)
            else:
                os.environ["SOURCE_DATE_EPOCH"] = previous

    def test_invalid_revision_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            builder.validate_source_revision("bad revision with spaces")

    def test_table_cells_escape_markdown_delimiters(self) -> None:
        self.assertEqual(
            builder.safe_table_cell("alpha|beta`gamma"),
            "alpha\\|beta'gamma",
        )


if __name__ == "__main__":
    unittest.main()
