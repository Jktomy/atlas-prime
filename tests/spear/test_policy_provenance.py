from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.spear.cli import main
from tools.spear.models import GitError, PolicyError
from tools.spear.policy import DESTINATION_POLICY_PATH, PROTECTED_POLICY_PATH, load_controlling_policies, parse_policy_yaml
from .helpers import DEST_POLICY_TEXT, PROT_POLICY_TEXT, POLICY, SCHEMA, cli_args, fixture, init_repo, run, write_packet


def commit_all(repo: Path, message: str) -> str:
    run(["git", "add", "."], repo)
    run(["git", "commit", "-m", message], repo)
    return run(["git", "rev-parse", "HEAD"], repo).strip()


def write_policy(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def packet_for(repo: Path, commit: str) -> tuple[Path, str, dict]:
    p = fixture("valid-create.json")
    p["base_commit"] = commit
    packet_path = repo.parent / ("packet-" + commit[:8] + ".json")
    packet_sha = write_packet(packet_path, p)
    return packet_path, packet_sha, p


class PolicyProvenanceAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.tmp = Path(self.td.name)
        self.repo = self.tmp / "repo-a"
        self.commit = init_repo(self.repo)

    def tearDown(self):
        self.td.cleanup()

    def test_cross_repository_policy_substitution_argument_is_not_available(self) -> None:
        repo_b = self.tmp / "repo-b"
        commit_b = init_repo(repo_b)
        packet_path, packet_sha, _ = packet_for(self.repo, self.commit)
        args = cli_args(self.repo, packet_path, packet_sha, self.tmp / "out")
        args.extend(["--prime-repository", str(repo_b)])
        with self.assertRaises(SystemExit):
            main(args)

    def test_policy_commit_cannot_be_selected_separately_by_caller(self) -> None:
        packet_path, packet_sha, _ = packet_for(self.repo, self.commit)
        args = cli_args(self.repo, packet_path, packet_sha, self.tmp / "out")
        args.extend(["--prime-commit", self.commit])
        with self.assertRaises(SystemExit):
            main(args)

    def test_newer_base_plus_older_policy_fails_by_no_separate_policy_commit(self) -> None:
        write_policy(self.repo, DESTINATION_POLICY_PATH, DEST_POLICY_TEXT.replace("registered_operations:\n  - CREATE_FILE", "registered_operations:\n  - CREATE_FILE\n  - REPLACE_FILE_FULL"))
        newer = commit_all(self.repo, "newer-policy")
        packet_path, packet_sha, _ = packet_for(self.repo, newer)
        self.assertEqual(main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-newer")), 0)
        args = cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-rollback")
        args.extend(["--prime-commit", self.commit])
        with self.assertRaises(SystemExit):
            main(args)

    def test_older_base_plus_newer_main_fails_before_policy_load(self) -> None:
        write_policy(self.repo, DESTINATION_POLICY_PATH, DEST_POLICY_TEXT + "\n# newer\n")
        newer = commit_all(self.repo, "newer")
        packet_path, packet_sha, _ = packet_for(self.repo, self.commit)
        with self.assertRaises(GitError):
            main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-old"))

    def test_newly_protected_project_prefix_is_denied_without_python_change(self) -> None:
        protected = PROT_POLICY_TEXT.replace("protected_sets:\n", "protected_sets:\n- id: project-spear-block\n  level: HIGH\n  match:\n    prefixes:\n    - projects/spear/\n  normal_spear_mutation: DENY\n  required_route: TEST_ROUTE\n  controls: []\n")
        write_policy(self.repo, PROTECTED_POLICY_PATH, protected)
        new_commit = commit_all(self.repo, "protect-project-prefix")
        packet_path, packet_sha, _ = packet_for(self.repo, new_commit)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-prefix"))

    def test_newly_protected_exact_project_path_is_denied(self) -> None:
        protected = PROT_POLICY_TEXT.replace("protected_sets:\n", "protected_sets:\n- id: project-exact-block\n  level: HIGH\n  match:\n    exact:\n    - projects/spear/probationary-create.md\n  normal_spear_mutation: DENY\n  required_route: TEST_ROUTE\n  controls: []\n")
        write_policy(self.repo, PROTECTED_POLICY_PATH, protected)
        new_commit = commit_all(self.repo, "protect-project-exact")
        packet_path, packet_sha, _ = packet_for(self.repo, new_commit)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-exact"))

    def test_destination_path_class_operation_removed_is_denied(self) -> None:
        dest = DEST_POLICY_TEXT + "\npath_classes:\n- id: project-and-operation-source\n  precedence: 50\n  match:\n    prefixes:\n    - projects/\n  write_lane: SOURCE_PR\n  current_mutation: DENY\n  future_operations: []\n"
        write_policy(self.repo, DESTINATION_POLICY_PATH, dest)
        new_commit = commit_all(self.repo, "deny-project-class")
        packet_path, packet_sha, _ = packet_for(self.repo, new_commit)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-deny"))

    def test_required_registered_operation_removed_fails(self) -> None:
        dest = DEST_POLICY_TEXT.replace("  - CREATE_FILE\n", "")
        write_policy(self.repo, DESTINATION_POLICY_PATH, dest)
        new_commit = commit_all(self.repo, "remove-create")
        packet_path, packet_sha, _ = packet_for(self.repo, new_commit)
        with self.assertRaises(PolicyError):
            main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-reg"))

    def test_malformed_duplicate_and_unsafe_yaml_fail(self) -> None:
        with self.assertRaises(PolicyError):
            parse_policy_yaml(b"policy_id: x\npolicy_id: y\n")
        with self.assertRaises(PolicyError):
            parse_policy_yaml(b"policy_id: [unterminated\n")
        with self.assertRaises(PolicyError):
            parse_policy_yaml(b"!!python/object/apply:os.system ['echo unsafe']\n")

    def test_unknown_protection_mode_fails_closed(self) -> None:
        protected = PROT_POLICY_TEXT.replace("normal_spear_mutation: DENY", "normal_spear_mutation: ALLOW_PLAIN_WRITE")
        write_policy(self.repo, PROTECTED_POLICY_PATH, protected)
        new_commit = commit_all(self.repo, "unknown-mode")
        with self.assertRaises(PolicyError):
            load_controlling_policies(str(self.repo), new_commit)

    def test_permissive_overlay_cannot_override_official_denial(self) -> None:
        protected = PROT_POLICY_TEXT.replace("protected_sets:\n", "protected_sets:\n- id: project-spear-block\n  level: HIGH\n  match:\n    prefixes:\n    - projects/spear/\n  normal_spear_mutation: DENY\n  required_route: TEST_ROUTE\n  controls: []\n")
        write_policy(self.repo, PROTECTED_POLICY_PATH, protected)
        new_commit = commit_all(self.repo, "official-denial")
        permissive = self.tmp / "permissive.json"
        overlay = json.loads(Path(POLICY).read_text(encoding="utf-8"))
        overlay["ordinary_packet_allowed_prefixes"] = ["projects/spear/"]
        permissive.write_text(json.dumps(overlay, sort_keys=True), encoding="utf-8")
        packet_path, packet_sha, _ = packet_for(self.repo, new_commit)
        args = cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-permissive")
        args[args.index("--policy") + 1] = str(permissive)
        with self.assertRaises(PolicyError):
            main(args)

    def test_receipt_policy_hashes_match_raw_git_object_bytes(self) -> None:
        packet_path, packet_sha, _ = packet_for(self.repo, self.commit)
        out = self.tmp / "out-receipt"
        self.assertEqual(main(cli_args(self.repo, packet_path, packet_sha, out)), 0)
        receipt = json.loads((out / "validation-receipt.json").read_text(encoding="utf-8"))
        for key, rel in [("destination_policy", DESTINATION_POLICY_PATH), ("protected_policy", PROTECTED_POLICY_PATH)]:
            raw = subprocess.check_output(["git", "-C", str(self.repo), "show", f"{self.commit}:{rel}"])
            blob = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", f"{self.commit}:{rel}"], text=True).strip()
            ident = receipt["contract_identity"][key]
            self.assertEqual(ident["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(ident["git_blob_sha"], blob)
            self.assertEqual(ident["repository_commit"], self.commit)


if __name__ == "__main__":
    unittest.main()