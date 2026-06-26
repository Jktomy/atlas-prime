from __future__ import annotations

import base64
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from tools.spear.compile import compile_packet, prevalidate_operation_paths
from tools.spear.models import StateError
from tools.spear.s1_cli import main as s1_cli_main
from tools.spear.s1_git_adapter import BOT_EMAIL, BOT_NAME, CommitReadback, FakeS1GitAdapter, GitIdentity, commit_spec
from tools.spear.s1_pr_client import DraftPullRequestReadback, FakeS1PrClient, build_pr_body
from tools.spear.s1_receipts import bounded_receipt, canonical_json_bytes, receipt_artifact_identity
from tools.spear.s1_recovery import ExistingTransaction, TransactionIdentity, classify_existing_transaction
from tools.spear.s1_writer import (
    RuntimeContext,
    assert_apply_enabled,
    build_plan,
    check_disallowed_capability,
    decode_packet_from_envelope,
    load_compile_context,
    parse_and_validate_envelope,
    repository_packet_identity,
    run_disabled_transaction,
    validate_disabled_dual_activation,
    validate_dispatch_packet_id,
    validate_plan_timestamps,
)
from tools.spear.validate import validate_schema

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/spear"
GOLDEN = FIXTURES / "golden-transactions-v1.json"
RECEIPT_SCHEMA = ROOT / "schemas/spear/spear-execution-receipt-v1.schema.json"
ENVELOPE_SCHEMA = ROOT / "schemas/spear/spear-execution-envelope-v1.schema.json"
BRANCH_REGEX = r"^spear/[0-9]{8}-[0-9]{3}-[a-f0-9]{8}$"
BASE = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
WORKFLOW_SHA = "b" * 40


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fixture(name: str) -> dict:
    packet = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    packet["base_commit"] = BASE
    return packet


def _target_blobs(packet: dict) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for op in packet["operations"]:
        result[op["path"]] = op.get("expected_blob_sha") if op["action"] == "REPLACE_FILE_FULL" else None
    return result


def _manifest_hash(packet: dict, context, target_blobs: dict[str, str | None], transport_sha: str) -> str:
    validate_schema(packet, context.packet_schema)
    operations = prevalidate_operation_paths(packet, context.overlay_policy, context.controlling_policy, context.limits)
    base_state = {op["path"]: target_blobs.get(op["path"]) for op in operations}
    result = compile_packet(
        packet,
        context.overlay_policy,
        context.controlling_policy,
        context.limits,
        context.contract_identity,
        base_state=base_state,
        transport_sha256=transport_sha,
        source_metadata_schema=context.source_metadata_schema,
    )
    return result.receipt["manifest_sha256"]


def _envelope(packet: dict, context, target_blobs: dict[str, str | None], *, manifest: str | None = None) -> dict:
    raw = json.dumps(packet, sort_keys=True, separators=(",", ":")).encode("utf-8")
    preview = b"approved preview"
    now = datetime.now(timezone.utc)
    transport = _sha(raw)
    if manifest is None:
        manifest = _manifest_hash(packet, context, target_blobs, transport)
    return {
        "envelope_version": "1.0",
        "packet_id": packet["packet_id"],
        "packet_b64": base64.b64encode(raw).decode("ascii"),
        "packet_transport_sha256": transport,
        "preview_b64": base64.b64encode(preview).decode("ascii"),
        "approved_preview_sha256": _sha(preview),
        "approved_manifest_sha256": manifest,
        "expected_base_commit": BASE,
        "approval": {
            "source": "APPROVED_PREVIEW_EXECUTE",
            "reference": "Jayson:test",
            "approved_scope": "CREATE_DRAFT_PR_ONLY",
        },
        "execution_mode": "CREATE_DRAFT_PR_ONLY",
        "plan_created_at": (now - timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
        "plan_expires_at": (now + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "confirmation": "EXECUTE_APPROVED_PREVIEW_ONLY",
        "authority": {
            "draft_pr_only": True,
            "merge_authorized": False,
            "deletion_authorized": False,
            "migration_authorized": False,
            "promotion_authorized": False,
            "cutover_authorized": False,
        },
    }


def _context() -> RuntimeContext:
    return RuntimeContext("Jktomy", "workflow_dispatch", "Jktomy/atlas-prime", WORKFLOW_SHA, "101", "1")


def _assert_receipt_schema(testcase: unittest.TestCase, receipt: dict) -> None:
    schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
    testcase.assertEqual(list(Draft202012Validator(schema).iter_errors(receipt)), [])


class BadCommitGit(FakeS1GitAdapter):
    def __init__(self, *args, failure: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.failure = failure

    def read_commit_and_changed_paths(self, commit_sha: str) -> CommitReadback:
        good = super().read_commit_and_changed_paths(commit_sha)
        if self.failure == "parent":
            return replace(good, parents=(BASE, "d" * 40))
        if self.failure == "message":
            return replace(good, message=good.message + "\nchanged")
        if self.failure == "identity":
            return replace(good, author=GitIdentity("other", BOT_EMAIL, good.author.date))
        return replace(good, tree_sha="9" * 40)


class ExplodingGit(FakeS1GitAdapter):
    def read_remote_main(self) -> str:
        raise RuntimeError("raw protected detail must not appear")


class S1WriterA3BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compile_context = load_compile_context(str(ROOT), BASE)

    def _plan(self, packet: dict, *, target_blobs: dict[str, str | None] | None = None):
        blobs = _target_blobs(packet) if target_blobs is None else target_blobs
        reader = FakeS1GitAdapter(BASE, BASE, target_blobs=blobs)
        envelope = _envelope(packet, self.compile_context, blobs)
        plan = build_plan(
            dispatch_packet_id=packet["packet_id"],
            envelope=envelope,
            branch_regex=BRANCH_REGEX,
            compile_context=self.compile_context,
            target_reader=reader,
        )
        return plan, blobs, reader

    def _execute(self, packet: dict):
        plan, blobs, _ = self._plan(packet)
        git = FakeS1GitAdapter(BASE, BASE, target_blobs=blobs)
        pr = FakeS1PrClient()
        receipt = run_disabled_transaction(
            context=_context(), plan=plan, git=git, pr=pr, hard_disabled=False, now=datetime.now(timezone.utc)
        )
        return plan, git, pr, receipt

    def test_all_a3b_vectors_are_mapped_to_tests(self) -> None:
        suite = json.loads(GOLDEN.read_text(encoding="utf-8"))
        required = {item["vector_id"] for item in suite["vectors"] if item["implementation_gate"] == "A3B_WRITER_TEST"}
        mapped = {
            "GT-P01", "GT-P02", "GT-P03", "GT-R01", "GT-R02",
            "GT-N01", "GT-N02", "GT-N03", "GT-N11", "GT-N12",
            "GT-N13", "GT-N14", "GT-N15", "GT-N25", "GT-N26",
            "GT-N27", "GT-N28", "GT-N29", "GT-N30", "GT-N31",
            "GT-N32", "GT-N36",
        }
        self.assertEqual(required, mapped)

    def test_gt_p01_complete_create_transaction(self) -> None:
        packet = _fixture("valid-create.json")
        plan, git, pr, receipt = self._execute(packet)
        _assert_receipt_schema(self, receipt)
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")
        self.assertEqual(receipt["last_completed_gate"], "PR_VERIFIED")
        self.assertEqual(receipt["changed_files"], list(plan.changed_paths))
        self.assertEqual(len(git.branches), 1)
        self.assertEqual(pr.calls.count("create_draft_pr"), 1)
        readback = git.commits[git.next_commit_sha]
        self.assertEqual(readback.parents, (BASE,))
        self.assertTrue(readback.message.startswith(f"Spear: {packet['title']}\n"))
        self.assertIn(f"Packet-Transport-SHA256: {plan.packet_sha256}", readback.message)
        self.assertEqual(readback.author.name, BOT_NAME)
        self.assertEqual(readback.committer.email, BOT_EMAIL)

    def test_gt_p02_exact_replace_transaction(self) -> None:
        plan, _, _, receipt = self._execute(_fixture("valid-update.json"))
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")
        self.assertIsNotNone(plan.file_identities[0]["old_blob_sha"])

    def test_gt_p03_atomic_three_file_transaction(self) -> None:
        packet = _fixture("valid-multi.json")
        third = copy.deepcopy(packet["operations"][0])
        third["path"] = "projects/spear/third-atomic-create.md"
        third["content_utf8"] = third["content_utf8"].replace("probationary", "third atomic")
        third["content_sha256"] = _sha(third["content_utf8"].encode())
        packet["operations"].append(third)
        plan, git, _, receipt = self._execute(packet)
        self.assertEqual(len(plan.changed_paths), 3)
        self.assertEqual(len([c for c in git.calls if c.startswith("create_blob:")]), 3)
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")

    def test_noctua_01_historical_expired_plan_is_rejected(self) -> None:
        packet = _fixture("valid-create.json")
        blobs = _target_blobs(packet)
        envelope = _envelope(packet, self.compile_context, blobs)
        envelope["plan_created_at"] = "2020-01-01T00:00:00Z"
        envelope["plan_expires_at"] = "2020-01-02T00:00:00Z"
        with self.assertRaisesRegex(StateError, "PLAN_EXPIRED"):
            validate_plan_timestamps(envelope, now=datetime(2026, 6, 26, tzinfo=timezone.utc))

    def test_noctua_02_invalid_content_hash_never_reaches_mutation(self) -> None:
        packet = _fixture("valid-create.json")
        packet["operations"][0]["content_sha256"] = "0" * 64
        blobs = _target_blobs(packet)
        reader = FakeS1GitAdapter(BASE, BASE, target_blobs=blobs)
        envelope = _envelope(packet, self.compile_context, blobs, manifest="c" * 64)
        with self.assertRaisesRegex(StateError, "CONTENT_HASH_MISMATCH"):
            build_plan(dispatch_packet_id=packet["packet_id"], envelope=envelope, branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=reader)
        self.assertFalse(any(call.startswith("create_") for call in reader.calls))

    def test_noctua_02_protected_path_rejected_before_target_lookup(self) -> None:
        packet = _fixture("valid-create.json")
        packet["operations"][0]["path"] = ".github/workflows/hostile.md"
        reader = FakeS1GitAdapter(BASE, BASE)
        envelope = _envelope(packet, self.compile_context, {}, manifest="c" * 64)
        with self.assertRaisesRegex(StateError, "PATH_POLICY_REJECTED"):
            build_plan(dispatch_packet_id=packet["packet_id"], envelope=envelope, branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=reader)
        self.assertFalse(any(call.startswith("read_target_blob:") for call in reader.calls))

    def test_noctua_02_create_existing_and_stale_replace_are_rejected(self) -> None:
        create = _fixture("valid-create.json")
        path = create["operations"][0]["path"]
        blobs = {path: "1" * 40}
        with self.assertRaisesRegex(StateError, "CREATE_TARGET_EXISTS"):
            build_plan(dispatch_packet_id=create["packet_id"], envelope=_envelope(create, self.compile_context, blobs, manifest="c" * 64), branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs))
        update = _fixture("valid-update.json")
        stale = {update["operations"][0]["path"]: "2" * 40}
        with self.assertRaisesRegex(StateError, "TARGET_BLOB_MISMATCH"):
            build_plan(dispatch_packet_id=update["packet_id"], envelope=_envelope(update, self.compile_context, stale, manifest="c" * 64), branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=FakeS1GitAdapter(BASE, BASE, target_blobs=stale))

    def test_noctua_03_reused_packet_id_with_changed_packet_collides(self) -> None:
        packet = _fixture("valid-create.json")
        plan, git, pr, receipt = self._execute(packet)
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")
        pr.existing = pr.created
        changed = copy.deepcopy(packet)
        changed["title"] = "Changed replay title"
        changed_plan, blobs, _ = self._plan(changed)
        git.target_blobs = blobs
        collision = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=changed_plan, git=git, pr=pr, hard_disabled=False)
        self.assertIn("PACKET_ID_REUSE_COLLISION", collision["blocker_codes"])
        self.assertEqual(pr.calls.count("create_draft_pr"), 1)

    def test_noctua_04_existing_pr_metadata_must_match_exactly(self) -> None:
        packet = _fixture("valid-create.json")
        plan, git, pr, receipt = self._execute(packet)
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")
        original = pr.created
        assert original is not None
        pr.existing = replace(original, title="wrong title")
        second = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=pr, hard_disabled=False)
        self.assertIn("PR_METADATA_MISMATCH", second["blocker_codes"])
        pr.existing = replace(original, body="wrong body")
        third = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=pr, hard_disabled=False)
        self.assertIn("PR_METADATA_MISMATCH", third["blocker_codes"])

    def test_noctua_05_pr_body_is_exact_and_complete(self) -> None:
        packet = {
            "packet_id": "spear.test-001",
            "approval_basis": "APPROVED_PREVIEW_EXECUTE",
            "base_commit": "a" * 40,
        }
        body = build_pr_body(
            packet=packet,
            branch="spear/00000001-001-deadbeef",
            commit_sha="b" * 40,
            manifest_sha256="c" * 64,
            preview_sha256="d" * 64,
            transport_sha256="e" * 64,
            approval_reference="Jayson:exact-preview",
            changed_paths=["projects/spear/example.md"],
            contract_identities=[{
                "path": "specs/spear/contract.md",
                "repository_commit": "f" * 40,
                "git_blob_sha": "1" * 40,
                "sha256": "2" * 64,
            }],
            file_identities=[{
                "action": "CREATE_FILE",
                "path": "projects/spear/example.md",
                "old_blob_sha": None,
                "new_content_sha256": "3" * 64,
            }],
            validation_results=["S0_COMPILER_VALIDATED"],
            warning_codes=["REVIEW_REQUIRED"],
            protected_boundary="PASS",
            actor="Jktomy",
            event="workflow_dispatch",
            workflow_sha="4" * 40,
            run_id="101",
            run_attempt="1",
            repository="Jktomy/atlas-prime",
        )
        expected = """## Spear S1 draft PR

### Approved transaction identity

- Repository: `Jktomy/atlas-prime`
- Packet ID: `spear.test-001`
- Packet transport SHA-256: `eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`
- Approved normalized-manifest SHA-256: `cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc`
- Approved Preview SHA-256: `dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd`
- Approval basis: `APPROVED_PREVIEW_EXECUTE`
- Approval reference: `Jayson:exact-preview`
- Exact base commit: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Branch: `spear/00000001-001-deadbeef`
- Commit SHA: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`

### Workflow run identity

- Authenticated actor: `Jktomy`
- Event: `workflow_dispatch`
- Workflow commit: `4444444444444444444444444444444444444444`
- Run ID: `101`
- Run attempt: `1`

### Controlling contract identities

```json
[
  {
    "git_blob_sha": "1111111111111111111111111111111111111111",
    "path": "specs/spear/contract.md",
    "repository_commit": "ffffffffffffffffffffffffffffffffffffffff",
    "sha256": "2222222222222222222222222222222222222222222222222222222222222222"
  }
]
```

### Exact changed filenames

- `projects/spear/example.md`

### Old and new file identities

```json
[
  {
    "action": "CREATE_FILE",
    "new_content_sha256": "3333333333333333333333333333333333333333333333333333333333333333",
    "old_blob_sha": null,
    "path": "projects/spear/example.md"
  }
]
```

### Validation summary

- S0_COMPILER_VALIDATED

### Warnings

- `REVIEW_REQUIRED`

- Protected-boundary outcome: `PASS`
- Rollback posture: S1 does not execute rollback; Phoenix Reborn review remains separate.
- Requested Noctua audit: verify packet-to-PR fidelity, contracts, target state, branch, commit, PR metadata, checks, and receipt.

This draft pull request grants no merge, deletion, migration, source-promotion, or cutover authority.
Manual Noctua review and explicit Jayson approval are required before merge.
"""
        self.assertEqual(body, expected)

    def test_gt_r01_branch_pushed_pr_missing_recovery(self) -> None:
        packet = _fixture("valid-create.json")
        plan, git, pr, receipt = self._execute(packet)
        self.assertEqual(receipt["transaction_state"], "DRAFT_PR_CREATED")
        pr.created = None
        pr.existing = None
        recovered = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=pr, hard_disabled=False)
        self.assertEqual(recovered["transaction_state"], "DRAFT_PR_CREATED")

    def test_gt_r02_exact_completed_transaction_replay(self) -> None:
        packet = _fixture("valid-create.json")
        plan, git, pr, receipt = self._execute(packet)
        pr.existing = pr.created
        replay = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=pr, hard_disabled=False)
        self.assertEqual(replay["transaction_state"], "EXISTING_TRANSACTION_RETURNED")
        self.assertEqual(receipt["commit_sha"], replay["commit_sha"])

    def test_gt_n01_n02_n03_runtime_rejections(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        for context, code in [
            (replace(_context(), actor="other"), "ACTOR_NOT_AUTHORIZED"),
            (replace(_context(), event="push"), "EVENT_NOT_AUTHORIZED"),
            (replace(_context(), repository="other/repo"), "REPOSITORY_MISMATCH"),
        ]:
            result = run_disabled_transaction(now=datetime.now(timezone.utc), context=context, plan=plan, git=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs), pr=FakeS1PrClient(), hard_disabled=False)
            self.assertIn(code, result["blocker_codes"])

    def test_gt_n11_n12_n13_n14_n15_envelope_bindings(self) -> None:
        packet = _fixture("valid-create.json")
        blobs = _target_blobs(packet)
        valid = _envelope(packet, self.compile_context, blobs)
        schema = json.loads(ENVELOPE_SCHEMA.read_text())
        parse_and_validate_envelope(json.dumps(valid).encode(), schema, now=datetime.now(timezone.utc))
        variants = [
            ("packet_transport_sha256", "0" * 64, "PACKET_HASH_MISMATCH"),
            ("approved_preview_sha256", "0" * 64, "PREVIEW_HASH_MISMATCH"),
        ]
        for key, value, code in variants:
            bad = copy.deepcopy(valid)
            bad[key] = value
            if key == "packet_transport_sha256":
                with self.assertRaisesRegex(StateError, code):
                    build_plan(dispatch_packet_id=packet["packet_id"], envelope=bad, branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs))
            else:
                with self.assertRaisesRegex(StateError, code):
                    parse_and_validate_envelope(json.dumps(bad).encode(), schema, now=datetime.now(timezone.utc))
        bad_manifest = copy.deepcopy(valid)
        bad_manifest["approved_manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(StateError, "MANIFEST_HASH_MISMATCH"):
            build_plan(dispatch_packet_id=packet["packet_id"], envelope=bad_manifest, branch_regex=BRANCH_REGEX, compile_context=self.compile_context, target_reader=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs))

    def test_gt_n25_n26_n27_identity_helpers(self) -> None:
        plan, _, _ = self._plan(_fixture("valid-create.json"))
        identity = TransactionIdentity("Jktomy/atlas-prime", plan.packet["packet_id"], plan.packet_sha256, plan.manifest_sha256, plan.preview_sha256, BASE, plan.branch, "e" * 40, "7" * 40)
        self.assertEqual(repository_packet_identity("Jktomy/atlas-prime", "abc"), "Jktomy/atlas-prime+abc")
        with self.assertRaisesRegex(StateError, "PACKET_ID_REUSE_COLLISION"):
            classify_existing_transaction(ExistingTransaction(replace(identity, tree_sha="9" * 40), plan.branch, True, True, "e" * 40), identity)
        with self.assertRaisesRegex(StateError, "BRANCH_COLLISION"):
            classify_existing_transaction(ExistingTransaction(identity, "spear/99999999-001-abcdef12", True, True, "e" * 40), identity)

    def test_gt_n28_n29_n30_commit_readback_failures(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        expected_codes = {"parent": "COMMIT_PARENT_MISMATCH", "message": "COMMIT_MESSAGE_MISMATCH", "identity": "COMMIT_IDENTITY_MISMATCH"}
        for failure, code in expected_codes.items():
            result = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=BadCommitGit(BASE, BASE, target_blobs=blobs, failure=failure), pr=FakeS1PrClient(), hard_disabled=False)
            self.assertIn(code, result["blocker_codes"])

    def test_gt_n31_server_mutated_pr_metadata(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        result = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs), pr=FakeS1PrClient(mutate_created_body=True), hard_disabled=False)
        self.assertIn("PR_METADATA_MISMATCH", result["blocker_codes"])

    def test_gt_n32_uncertain_post_outcome_without_duplicate_create(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        pr = FakeS1PrClient(uncertain_on_create=True)
        result = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=FakeS1GitAdapter(BASE, BASE, target_blobs=blobs), pr=pr, hard_disabled=False)
        self.assertEqual(result["transaction_state"], "PR_STATE_UNCERTAIN")
        self.assertEqual(pr.calls.count("create_draft_pr"), 1)

    def test_gt_n36_human_merge_authority_remains_false(self) -> None:
        receipt = bounded_receipt(transaction_state="FAILED_WITH_RECEIPT", last_completed_gate="PR_VERIFIED", blocker_codes=["CHECKS_NOT_COMPLETE"])
        _assert_receipt_schema(self, receipt)
        self.assertFalse(receipt["authority"]["merge_authorized"])

    def test_hard_disabled_gate_revalidates_target_then_never_mutates(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        git = FakeS1GitAdapter(BASE, BASE, target_blobs=blobs)
        result = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=FakeS1PrClient())
        self.assertIn("S1_APPLY_DISABLED", result["blocker_codes"])
        self.assertTrue(any(call.startswith("read_target_blob:") for call in git.calls))
        self.assertFalse(any(call.startswith("create_blob:") for call in git.calls))

    def test_target_state_is_revalidated_before_mutation(self) -> None:
        plan, _, _ = self._plan(_fixture("valid-create.json"))
        git = FakeS1GitAdapter(BASE, BASE, target_blobs={plan.changed_paths[0]: "f" * 40})
        result = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=git, pr=FakeS1PrClient(), hard_disabled=False)
        self.assertIn("TARGET_BLOB_MISMATCH", result["blocker_codes"])
        self.assertFalse(any(call.startswith("create_blob:") for call in git.calls))

    def test_cli_produces_schema_valid_disabled_receipt(self) -> None:
        packet = _fixture("valid-create.json")
        blobs = _target_blobs(packet)
        envelope = _envelope(packet, self.compile_context, blobs)
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            path = tmp / "envelope.json"
            path.write_text(json.dumps(envelope), encoding="utf-8")
            rc = s1_cli_main([
                "--packet-id", packet["packet_id"], "--envelope", str(path), "--output-root", str(tmp / "out"),
                "--repository-path", str(ROOT), "--actor", "Jktomy", "--event", "workflow_dispatch",
                "--repository", "Jktomy/atlas-prime", "--workflow-sha", WORKFLOW_SHA, "--run-id", "10", "--run-attempt", "1",
                "--observed-at", datetime.now(timezone.utc).isoformat(),
            ])
            self.assertEqual(rc, 1)
            receipt = json.loads((tmp / "out/spear-s1-receipt-10-1/spear-s1-receipt.json").read_text())
            _assert_receipt_schema(self, receipt)
            self.assertIn("S1_APPLY_DISABLED", receipt["blocker_codes"])

    def test_unexpected_exception_is_redacted(self) -> None:
        plan, blobs, _ = self._plan(_fixture("valid-create.json"))
        receipt = run_disabled_transaction(now=datetime.now(timezone.utc), context=_context(), plan=plan, git=ExplodingGit(BASE, BASE, target_blobs=blobs), pr=FakeS1PrClient(), hard_disabled=False)
        _assert_receipt_schema(self, receipt)
        self.assertEqual(receipt["blocker_codes"], ["UNEXPECTED_EXCEPTION"])
        self.assertNotIn("raw protected detail", json.dumps(receipt))

    def test_envelope_duplicate_keys_and_dual_activation_fail_closed(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA.read_text())
        with self.assertRaises(StateError):
            parse_and_validate_envelope(b'{"packet_id":"a","packet_id":"b"}', schema, now=datetime.now(timezone.utc))
        validate_disabled_dual_activation(
            {"enabled": False, "mode": "DISABLED", "repository_writes_authorized": False, "authorized_operations": [], "authority": {"merge": False}},
            {"authority": {"repository_writes_authorized": False, "execution_authorized_operations": []}},
        )
        with self.assertRaisesRegex(StateError, "DUAL_ACTIVATION_MISMATCH"):
            validate_disabled_dual_activation({"enabled": True, "mode": "ACTIVATED"}, {"authority": {"repository_writes_authorized": False, "execution_authorized_operations": []}})

    def test_dispatch_packet_id_and_forbidden_capabilities(self) -> None:
        packet = {"packet_id": "spear-example-001"}
        raw = json.dumps(packet, sort_keys=True).encode()
        envelope = {"packet_id": packet["packet_id"], "packet_b64": base64.b64encode(raw).decode(), "packet_transport_sha256": _sha(raw)}
        decoded, _ = decode_packet_from_envelope(envelope)
        validate_dispatch_packet_id(packet["packet_id"], envelope, decoded)
        with self.assertRaisesRegex(StateError, "PACKET_IDENTITY_MISMATCH"):
            validate_dispatch_packet_id("different", envelope, decoded)
        with self.assertRaisesRegex(StateError, "S1_APPLY_DISABLED"):
            assert_apply_enabled()
        for capability in ["direct_main", "force_push", "merge", "delete", "settings_mutation", "pr_repair", "workflow_self_modification", "packet_selected_command"]:
            with self.assertRaisesRegex(StateError, "FORBIDDEN_CAPABILITY"):
                check_disallowed_capability(capability)

    def test_receipt_identity_and_canonical_json(self) -> None:
        self.assertEqual(receipt_artifact_identity("123", "2"), ("spear-s1-receipt-123-2", "spear-s1-receipt.json"))
        self.assertEqual(canonical_json_bytes({"b": 1, "a": 2}), canonical_json_bytes({"a": 2, "b": 1}))


if __name__ == "__main__":
    unittest.main()
