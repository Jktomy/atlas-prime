from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.spear.cli import main
from tools.spear.models import GitError, PolicyError, SOURCE_METADATA_SCHEMA_PATH
from tools.spear.policy import load_source_metadata_schema, validate_markdown_source_metadata
from .helpers import DEST_POLICY_TEXT, POLICY, blob, cli_args, fixture, init_repo, run, write_packet

ROOT = Path(__file__).resolve().parents[2]


def commit_all(repo: Path, message: str) -> str:
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", message], repo)
    return run(["git", "rev-parse", "HEAD"], repo).strip()


class SourceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.tmp = Path(self.td.name)
        self.repo = self.tmp / "repo"
        self.commit = init_repo(self.repo)
        self.schema_identity, self.schema = load_source_metadata_schema(str(self.repo), self.commit)

    def tearDown(self):
        self.td.cleanup()

    def packet(self, name: str = "valid-create.json") -> dict:
        p = fixture(name)
        p["base_commit"] = self.commit
        return p

    def run_packet(self, packet: dict, out_name: str = "out"):
        path = self.tmp / (out_name + ".json")
        sha = write_packet(path, packet)
        return main(cli_args(self.repo, path, sha, self.tmp / out_name))

    def replace_operation_content(self, packet: dict, old: str, new: str) -> dict:
        mutated = copy.deepcopy(packet)
        content = mutated["operations"][0]["content_utf8"].replace(old, new)
        mutated["operations"][0]["content_utf8"] = content
        mutated["operations"][0]["content_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return mutated

    def test_three_authored_markdown_files_have_valid_metadata(self) -> None:
        for rel in ["athenas-spear.md", "tools/spear/operator-runbook.md", "tools/spear/recovery-runbook.md"]:
            content = (ROOT / rel).read_text(encoding="utf-8")
            metadata = validate_markdown_source_metadata(rel, content, self.schema, action="CREATE_FILE")
            self.assertEqual(metadata["status"], "PROPOSED")
            self.assertTrue(metadata["atlas_id"].startswith("spear.s0"))

    def test_missing_front_matter_malformed_duplicate_and_unsafe_fail(self) -> None:
        samples = [
            "# Missing\n",
            "---\ntitle: Missing close\n# Body\n",
            "---\ntitle: A\ntitle: B\n---\n# Body\n",
            "---\n!!python/object/apply:os.system ['echo unsafe']\n---\n# Body\n",
        ]
        for sample in samples:
            with self.assertRaises(PolicyError):
                validate_markdown_source_metadata("projects/spear/bad.md", sample, self.schema, action="CREATE_FILE")

    def test_metadata_schema_failure_and_active_status_on_create_fail(self) -> None:
        p = self.packet()
        content = p["operations"][0]["content_utf8"]
        bad = content.replace("atlas_id: spear.fixture.create", "atlas_id: INVALID ID")
        with self.assertRaises(PolicyError):
            validate_markdown_source_metadata("projects/spear/bad.md", bad, self.schema, action="CREATE_FILE")
        active = content.replace("status: PROPOSED", "status: ACTIVE")
        with self.assertRaises(PolicyError):
            validate_markdown_source_metadata("projects/spear/bad.md", active, self.schema, action="CREATE_FILE")

    def test_txt_operation_rejected_by_overlay(self) -> None:
        p = self.packet()
        p["operations"][0]["path"] = "projects/spear/not-markdown.txt"
        path = self.tmp / "txt.json"
        sha = write_packet(path, p)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, path, sha, self.tmp / "out-txt"))

    def test_valid_project_metadata_passes_real_destination_policy(self) -> None:
        self.assertEqual(self.run_packet(self.packet(), "valid-project-metadata"), 0)

    def test_disallowed_destination_metadata_source_type_fails(self) -> None:
        p = self.replace_operation_content(self.packet(), "source_type: REFERENCE", "source_type: TOOL_DOCUMENTATION")
        with self.assertRaises(PolicyError):
            self.run_packet(p, "bad-destination-source-type")

    def test_disallowed_destination_metadata_authority_class_fails(self) -> None:
        p = self.replace_operation_content(self.packet(), "authority_class: CONTINUITY_PROVENANCE", "authority_class: TOOL_CONTRACT")
        with self.assertRaises(PolicyError):
            self.run_packet(p, "bad-destination-authority-class")

    def test_packet_source_type_consistency_fails_closed(self) -> None:
        p = self.packet()
        p["operations"][0]["source_type"] = "AUTHORED_SOURCE"
        with self.assertRaises(PolicyError):
            self.run_packet(p, "bad-authored-continuity")
        p = self.packet()
        p["operations"][0]["source_type"] = "POINTER_ONLY"
        with self.assertRaises(PolicyError):
            self.run_packet(p, "bad-pointer-authority")
        p = self.packet()
        p["operations"][0]["source_type"] = "GENERATED_FIXTURE"
        with self.assertRaises(PolicyError):
            self.run_packet(p, "bad-generated-project")

    def test_current_valid_fixtures_comply_with_real_pinned_destination_policy(self) -> None:
        for fixture_name in ["valid-create.json", "valid-multi.json"]:
            p = self.packet(fixture_name)
            self.assertEqual(self.run_packet(p, "fixture-" + fixture_name.replace(".", "-")), 0)

    def test_extension_absent_from_official_destination_class_rejected(self) -> None:
        dest = DEST_POLICY_TEXT.replace("  - .md", "  - .json")
        (self.repo / "policies/destination/atlas-prime-destination-policy-v0.2.yaml").write_text(dest, encoding="utf-8")
        new_commit = commit_all(self.repo, "json-only-class")
        p = fixture("valid-create.json")
        p["base_commit"] = new_commit
        path = self.tmp / "class-ext.json"
        sha = write_packet(path, p)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, path, sha, self.tmp / "out-class-ext"))

    def test_source_metadata_schema_missing_at_pinned_commit_fails(self) -> None:
        (self.repo / SOURCE_METADATA_SCHEMA_PATH).unlink()
        new_commit = commit_all(self.repo, "remove-source-metadata-schema")
        p = fixture("valid-create.json")
        p["base_commit"] = new_commit
        path = self.tmp / "missing-schema.json"
        sha = write_packet(path, p)
        with self.assertRaises(GitError):
            main(cli_args(self.repo, path, sha, self.tmp / "out-missing-schema"))

    def test_source_metadata_schema_identity_matches_raw_git_bytes(self) -> None:
        identity, _ = load_source_metadata_schema(str(self.repo), self.commit)
        raw = subprocess.check_output(["git", "-C", str(self.repo), "show", f"{self.commit}:{SOURCE_METADATA_SCHEMA_PATH}"])
        blob_sha = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", f"{self.commit}:{SOURCE_METADATA_SCHEMA_PATH}"], text=True).strip()
        import hashlib
        self.assertEqual(identity.raw_byte_sha256, hashlib.sha256(raw).hexdigest())
        self.assertEqual(identity.raw_byte_size, len(raw))
        self.assertEqual(identity.git_blob_sha, blob_sha)

    def test_receipt_contains_source_metadata_schema_identity(self) -> None:
        p = self.packet()
        self.run_packet(p, "receipt")
        receipt = json.loads((self.tmp / "receipt" / "validation-receipt.json").read_text(encoding="utf-8"))
        ident = receipt["contract_identity"]["source_metadata_schema"]
        self.assertEqual(ident["path"], SOURCE_METADATA_SCHEMA_PATH)
        self.assertEqual(ident["repository_commit"], self.commit)
        self.assertEqual(len(ident["raw_byte_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
