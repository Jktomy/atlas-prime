from __future__ import annotations

import copy
import hashlib
import json
import re
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from tools.spear.cli import main
from tools.spear.compile import compile_packet, derive_branch
from tools.spear.git_adapter import blob_sha_at_commit
from tools.spear.models import COMPILER_VERSION, EXECUTION_STATE, ContractIdentity, GitError, PolicyError, StateError
from tools.spear.policy import effective_limits, load_controlling_policies, load_source_metadata_schema, load_spear_overlay_policy, load_spear_packet_schema
from tools.spear.validate import canonical_json_bytes, load_json_file, load_json_policy, validate_schema
from .helpers import POLICY, SCHEMA, blob, cli_args, fixture, init_repo, write_packet


class CompileAndIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.tmp = Path(self.td.name)
        self.repo = self.tmp / "repo"
        self.commit = init_repo(self.repo)
        self.packet_schema_identity, self.schema, _ = load_spear_packet_schema(str(self.repo), self.commit)
        self.overlay_identity, self.overlay, _ = load_spear_overlay_policy(str(self.repo), self.commit)
        self.controlling = load_controlling_policies(str(self.repo), self.commit)
        self.source_metadata_identity, self.source_metadata_schema = load_source_metadata_schema(str(self.repo), self.commit)
        self.limits = effective_limits(self.schema, self.overlay, self.controlling)
        self.identity = ContractIdentity(
            compiler_version=COMPILER_VERSION,
            packet_schema=self.packet_schema_identity,
            overlay_policy=self.overlay_identity,
            destination_policy=self.controlling["destination_identity"], protected_policy=self.controlling["protected_identity"],
            source_metadata_schema=self.source_metadata_identity,
        )

    def tearDown(self): self.td.cleanup()

    def packet_with_base(self, name: str) -> dict:
        p = fixture(name); p["base_commit"] = self.commit; return p

    def test_create_absent_passes_and_existing_create_fails_real_git(self) -> None:
        p = self.packet_with_base("valid-create.json")
        out = self.tmp / "out-create"; packet_path = self.tmp / "create.json"; packet_sha = write_packet(packet_path, p)
        self.assertEqual(main(cli_args(self.repo, packet_path, packet_sha, out)), 0)
        receipt = json.loads((out / "validation-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["execution_authorization_state"], EXECUTION_STATE)
        p["operations"][0]["path"] = "projects/spear/existing.md"
        packet_path = self.tmp / "create-existing.json"; packet_sha = write_packet(packet_path, p)
        with self.assertRaises(StateError): main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-existing"))

    def test_exact_update_passes_stale_and_absent_update_fail_real_git(self) -> None:
        p = self.packet_with_base("valid-update.json")
        p["operations"][0]["expected_blob_sha"] = blob(self.repo, self.commit, "projects/spear/existing.md")
        packet_path = self.tmp / "update.json"; packet_sha = write_packet(packet_path, p)
        self.assertEqual(main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-update")), 0)
        p["operations"][0]["expected_blob_sha"] = "f" * 40
        packet_path = self.tmp / "update-stale.json"; packet_sha = write_packet(packet_path, p)
        with self.assertRaises(StateError): main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-stale"))
        p = self.packet_with_base("valid-update.json"); p["operations"][0]["path"] = "projects/spear/absent.md"; p["operations"][0]["expected_blob_sha"] = "f" * 40
        packet_path = self.tmp / "update-absent.json"; packet_sha = write_packet(packet_path, p)
        with self.assertRaises(StateError): main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-absent"))

    def test_stale_base_missing_repository_and_invalid_base_commit_fail(self) -> None:
        p = self.packet_with_base("valid-create.json"); p["base_commit"] = "f" * 40
        packet_path = self.tmp / "stale-base.json"; packet_sha = write_packet(packet_path, p)
        with self.assertRaises(GitError): main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-stale-base"))
        p = self.packet_with_base("valid-create.json"); packet_path = self.tmp / "missing-repo.json"; packet_sha = write_packet(packet_path, p)
        args = cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-missing"); args[args.index("--repository") + 1] = str(self.tmp / "nope")
        with self.assertRaises(GitError): main(args)

    def test_invalid_git_object_not_treated_as_absent(self) -> None:
        tree_sha = __import__('subprocess').check_output(["git","-C",str(self.repo),"rev-parse",f"{self.commit}:projects/spear"], text=True).strip()
        with self.assertRaises(GitError) as ctx: blob_sha_at_commit(self.repo, self.commit, "projects/spear")
        self.assertEqual(ctx.exception.kind, "invalid_git_object")

    def test_branch_matches_policy_and_packet_cannot_supply_branch(self) -> None:
        p = self.packet_with_base("valid-create.json")
        branch = derive_branch(p, hashlib.sha256(canonical_json_bytes(p)).hexdigest(), self.controlling["future_branch_regex"])
        self.assertRegex(branch, r"^spear/[0-9]{8}-[0-9]{3}-[a-f0-9]{8}$")
        changed = copy.deepcopy(p)
        changed["title"] = "Changed title with same packet identity"
        changed["operations"][0]["content_utf8"] = changed["operations"][0]["content_utf8"].replace("probationary", "changed")
        changed["operations"][0]["content_sha256"] = hashlib.sha256(changed["operations"][0]["content_utf8"].encode("utf-8")).hexdigest()
        self.assertEqual(
            branch,
            derive_branch(changed, hashlib.sha256(canonical_json_bytes(changed)).hexdigest(), self.controlling["future_branch_regex"]),
        )
        p["branch_name"] = "spear/not-allowed"
        with self.assertRaises(Exception): validate_schema(p, self.schema)

    def test_transport_and_canonical_hash_semantics(self) -> None:
        p = self.packet_with_base("valid-create.json")
        a = json.dumps(p, sort_keys=True, indent=2).encode()+b"\n"
        b = json.dumps(p, sort_keys=False, separators=(",", ":")).encode()
        self.assertNotEqual(hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())
        self.assertEqual(hashlib.sha256(canonical_json_bytes(json.loads(a))).hexdigest(), hashlib.sha256(canonical_json_bytes(json.loads(b))).hexdigest())
        path = self.tmp / "packet.json"; path.write_bytes(a)
        with self.assertRaises(Exception): main(cli_args(self.repo, path, "0"*64, self.tmp / "out-bad-hash"))

    def test_compile_receipt_contains_contract_identities_and_auth_claim_boundary(self) -> None:
        p = self.packet_with_base("valid-create.json")
        result = compile_packet(p, self.overlay, self.controlling, self.limits, self.identity, base_state={"projects/spear/probationary-create.md": None}, transport_sha256="c"*64, source_metadata_schema=self.source_metadata_schema)
        receipt = result.receipt
        self.assertEqual(receipt["execution_authorization_state"], EXECUTION_STATE)
        self.assertEqual(receipt["authentication_state"], "UNVERIFIED_PACKET_CLAIM_ONLY")
        self.assertIsNone(receipt["authenticated_execution_actor"])
        self.assertIn("destination_policy", receipt["contract_identity"])
        self.assertIn("canonical_packet_sha256", receipt)
        self.assertIn("transport_sha256", receipt)

    def test_path_policy_runs_before_target_git_lookup(self) -> None:
        p = self.packet_with_base("valid-create.json")
        p["operations"][0]["path"] = "migration/blocked-before-lookup.md"
        packet_path = self.tmp / "blocked-path.json"
        packet_sha = write_packet(packet_path, p)
        with patch(
            "tools.spear.cli.blob_sha_at_commit",
            side_effect=AssertionError("target Git lookup occurred before path policy"),
        ) as target_lookup:
            with self.assertRaises(PolicyError):
                main(cli_args(self.repo, packet_path, packet_sha, self.tmp / "out-blocked"))
        target_lookup.assert_not_called()


if __name__ == "__main__": unittest.main()
