from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.atlas_lifecycle.jsonio import canonical_bytes, stable_record_id
from tools.atlas_lifecycle.projection import (
    INDEX_RELATIVE_PATH,
    build_website_index,
    check_website_index,
    compact_context,
    project_record,
    source_revision,
)
from tools.atlas_lifecycle.repository import validate_repository


EXPECTED_CONTEXT_KEYS = {
    "current_quest_position",
    "exact_source_references",
    "latest_valid_feather",
    "next_gate",
    "related_golden_wings",
    "source_fingerprint",
    "stale_projection_warnings",
    "unresolved_blockers",
}


def write_canonical(directory: Path, record: dict) -> dict:
    record["record_id"] = stable_record_id(record)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f'{record["record_id"]}.json').write_bytes(canonical_bytes(record))
    return record


CANONICAL_DIRS = (
    "feathers",
    "feather-archives",
    "golden-wings",
    "quest-emberlines",
    "quest-checkpoints",
    "sunsets",
    "sunrises",
    "continuity",
    "receipts",
    "events",
)


def copy_lifecycle_source(repo: Path) -> None:
    shutil.copytree(ROOT / "lifecycle", repo / "lifecycle")
    for name in CANONICAL_DIRS:
        shutil.rmtree(repo / "lifecycle" / name, ignore_errors=True)


class LifecycleProjectionTests(unittest.TestCase):
    def test_main_context_and_index_commands_are_check_only(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        context = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "tools.atlas_lifecycle",
                "context",
                "--quest-id",
                "repairing-prime",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        context_value = json.loads(context.stdout)
        self.assertEqual(set(context_value), EXPECTED_CONTEXT_KEYS)
        emberlines = []
        directory = ROOT / "lifecycle/quest-emberlines"
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                value = json.loads(path.read_text(encoding="utf-8"))
                if value.get("quest_id") == "repairing-prime":
                    emberlines.append(value)
        self.assertEqual(len(emberlines), 1)
        self.assertEqual(
            context_value["current_quest_position"],
            emberlines[0]["current_position"],
        )
        self.assertEqual(
            context_value["latest_valid_feather"],
            emberlines[0]["latest_feather_id"],
        )
        self.assertTrue(context_value["stale_projection_warnings"])

        index = subprocess.run(
            [sys.executable, "-B", "-m", "tools.atlas_lifecycle", "index", "build"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        index_value = json.loads(index.stdout)
        self.assertEqual(index_value["mode"], "CHECK_ONLY")
        self.assertEqual(index_value["index_status"], "MISSING")
        self.assertEqual(index_value["index_path"], INDEX_RELATIVE_PATH.as_posix())
        after = subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(after, before)

    def _quest_snapshot(self, repo: Path):
        copy_lifecycle_source(repo)
        main_sha = "a" * 40
        feather = json.loads((repo / "lifecycle/fixtures/feather-quest-bound.json").read_text())
        feather["authority"] = "CANONICAL_RECORD"
        feather["concurrency"]["expected_main_sha"] = main_sha
        feather = write_canonical(repo / "lifecycle/feathers", feather)

        infrastructure_feather = json.loads(
            (repo / "lifecycle/fixtures/feather-infrastructure.json").read_text()
        )
        infrastructure_feather["authority"] = "CANONICAL_RECORD"
        infrastructure_feather["quest_scope"] = {
            "scope_type": "NON_QUEST",
            "work_scope": "Harmless independent infrastructure context.",
        }
        infrastructure_feather["concurrency"]["expected_main_sha"] = main_sha
        infrastructure_feather["concurrency"]["expected_quest_revision"] = None
        infrastructure_feather = write_canonical(
            repo / "lifecycle/feathers", infrastructure_feather
        )

        emberline = {
            "schema_id": "atlas.lifecycle.quest-emberline",
            "schema_version": "1.0.0",
            "record_id": "QEM-AAAAAAAAAAAAAAAAAAAAAAAAAA",
            "authority": "CANONICAL_RECORD",
            "quest_id": "found-silverlight",
            "project_id": "project-codex",
            "operation_ids": ["operation-source-governance"],
            "quest_revision": 1,
            "prior_emberline_id": None,
            "current_position": "Gate remains in progress at a verified restart point.",
            "unresolved_blockers": ["One harmless fixture blocker remains."],
            "next_gate": "Complete the declared fixture acceptance checklist.",
            "latest_feather_id": feather["record_id"],
            "concurrency": {
                "expected_main_sha": main_sha,
                "expected_parent_feather": feather["record_id"],
                "expected_quest_revision": 0,
                "declared_source_fingerprint": "sha256:" + "7" * 64,
            },
            "durable_source_references": [
                {
                    "ref_id": "found-silverlight-source",
                    "authority": "CANONICAL_SOURCE",
                    "uri": "quests/found-silverlight.md",
                }
            ],
            "protected_data": {
                "classification": "INTERNAL_CLEAN",
                "clean_summary": "Fixture contains no protected values.",
                "protected_pointers": [],
            },
        }
        emberline = write_canonical(repo / "lifecycle/quest-emberlines", emberline)

        wing = json.loads((repo / "lifecycle/fixtures/golden-wing-multi-context.json").read_text())
        wing["authority"] = "CANONICAL_RECORD"
        wing["supporting_feather_ids"] = [
            feather["record_id"],
            infrastructure_feather["record_id"],
        ]
        wing = write_canonical(repo / "lifecycle/golden-wings", wing)

        protected_feather = json.loads(
            (repo / "lifecycle/fixtures/feather-protected-domain.json").read_text()
        )
        protected_feather["authority"] = "CANONICAL_RECORD"
        protected_feather["concurrency"]["expected_main_sha"] = main_sha
        protected_feather = write_canonical(
            repo / "lifecycle/feathers", protected_feather
        )

        protected = json.loads((repo / "lifecycle/fixtures/sunset-protected-domain.json").read_text())
        protected["authority"] = "CANONICAL_RECORD"
        protected["concurrency"]["expected_main_sha"] = main_sha
        protected["latest_feather_id"] = protected_feather["record_id"]
        protected = write_canonical(repo / "lifecycle/sunsets", protected)
        snapshot = validate_repository(repo, check_stale=True, expected_head=main_sha)
        return snapshot, feather, emberline, wing, protected

    def test_compact_context_and_projection_reconstruct_clean_restart(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            snapshot, feather, emberline, wing, protected = self._quest_snapshot(repo)
            context = compact_context(
                snapshot,
                quest_id="found-silverlight",
                projection_warning="website lifecycle index is stale",
            )
            self.assertEqual(set(context), EXPECTED_CONTEXT_KEYS)
            self.assertEqual(context["current_quest_position"], emberline["current_position"])
            self.assertEqual(context["latest_valid_feather"], feather["record_id"])
            self.assertEqual(context["unresolved_blockers"], emberline["unresolved_blockers"])
            self.assertEqual(context["next_gate"], emberline["next_gate"])
            self.assertEqual(context["related_golden_wings"], [wing["record_id"]])
            self.assertEqual(
                context["stale_projection_warnings"], ["website lifecycle index is stale"]
            )
            self.assertTrue(context["exact_source_references"])

            first = build_website_index(
                snapshot,
                source_revision_sha="b" * 40,
                source_timestamp="2026-01-01T00:00:00+00:00",
                schema_dir=repo / "lifecycle/schemas",
            )
            second = build_website_index(
                snapshot,
                source_revision_sha="b" * 40,
                source_timestamp="2026-01-01T00:00:00+00:00",
                schema_dir=repo / "lifecycle/schemas",
            )
            self.assertEqual(canonical_bytes(first, max_nodes=2_000_000), canonical_bytes(second, max_nodes=2_000_000))
            self.assertEqual(
                hashlib.sha256(canonical_bytes(first, max_nodes=2_000_000)).hexdigest(),
                hashlib.sha256(canonical_bytes(second, max_nodes=2_000_000)).hexdigest(),
            )
            self.assertEqual(first["authority"], "GENERATED_NONCANONICAL_PROJECTION")
            self.assertEqual(len(first["records"]), 6)
            protected_projection = next(
                item for item in first["records"] if item["record_id"] == protected["record_id"]
            )
            self.assertTrue(protected_projection["protected_warning"])
            self.assertNotIn("source_path", json.dumps(first))
            self.assertEqual(project_record(feather)["record_type"], "FEATHER")

    def test_check_only_index_detects_missing_current_stale_invalid_and_unrelated_commit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            copy_lifecycle_source(repo)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
            subprocess.run(["git", "add", "lifecycle"], cwd=repo, check=True)
            env = {
                **os.environ,
                "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
                "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
            }
            subprocess.run(
                [
                    "git", "-c", "user.name=Atlas Fixture", "-c",
                    "user.email=fixture@example.invalid", "commit", "-q", "-m", "lifecycle source",
                ],
                cwd=repo,
                check=True,
                env=env,
            )
            lifecycle_revision, lifecycle_timestamp = source_revision(repo)
            check, _ = check_website_index(repo)
            self.assertEqual(check.status, "MISSING")
            self.assertEqual(check.source_revision, lifecycle_revision)
            self.assertEqual(check.source_timestamp, lifecycle_timestamp)

            output = repo / INDEX_RELATIVE_PATH
            output.parent.mkdir(parents=True)
            output.write_bytes(check.expected_bytes)
            current, _ = check_website_index(repo)
            self.assertEqual(current.status, "CURRENT")

            output.write_bytes(check.expected_bytes + b" ")
            stale, _ = check_website_index(repo)
            self.assertEqual(stale.status, "STALE")
            output.write_text("not-json\n", encoding="utf-8")
            invalid, _ = check_website_index(repo)
            self.assertEqual(invalid.status, "INVALID")

            output.unlink()
            outside = repo / "outside-index.json"
            outside.write_bytes(check.expected_bytes)
            try:
                output.symlink_to(outside)
            except OSError:
                pass
            else:
                linked, _ = check_website_index(repo)
                self.assertEqual(linked.status, "INVALID")
                self.assertEqual(outside.read_bytes(), check.expected_bytes)
                output.unlink()

            (repo / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
            subprocess.run(["git", "add", "unrelated.txt"], cwd=repo, check=True)
            subprocess.run(
                [
                    "git", "-c", "user.name=Atlas Fixture", "-c",
                    "user.email=fixture@example.invalid", "commit", "-q", "-m", "unrelated",
                ],
                cwd=repo,
                check=True,
                env={
                    **os.environ,
                    "GIT_AUTHOR_DATE": "2026-01-02T00:00:00+00:00",
                    "GIT_COMMITTER_DATE": "2026-01-02T00:00:00+00:00",
                },
            )
            self.assertEqual(source_revision(repo), (lifecycle_revision, lifecycle_timestamp))

            shallow = Path(raw) / "shallow"
            subprocess.run(
                ["git", "clone", "-q", "--depth", "1", repo.as_uri(), str(shallow)],
                check=True,
            )
            self.assertEqual(source_revision(shallow), (lifecycle_revision, lifecycle_timestamp))


if __name__ == "__main__":
    unittest.main()
