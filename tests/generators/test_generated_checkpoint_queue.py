from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from pathlib import Path

from tools.generated_checkpoint.queue import (
    MAX_OPEN_PULL_REQUESTS,
    PROJECTION_FIELDS,
    QUERY_FIELDS,
    QUERY_LIMIT,
    QueueError,
    classify_open_pull_requests,
    main,
    stable_json,
)


class GeneratedCheckpointQueueTests(unittest.TestCase):
    RECEIPT_KEYS = {
        "schema_id", "schema_version", "repository", "event_name",
        "event_base_sha", "current_main_sha", "workflow_ref",
        "workflow_source_sha", "workflow_run_id", "workflow_run_attempt",
        "actor", "triggering_actor", "repository_owner",
        "credential_principal", "credential_mode", "query", "result",
        "open_checkpoint_count", "checkpoint", "mutation_authorized",
        "error_code", "receipt_sha256",
    }
    QUERY_KEYS = {
        "state", "limit", "max_accepted_entries", "requested_fields",
        "projection_fields", "returned_count", "snapshot_sha256",
    }
    CHECKPOINT_KEYS = {
        "number", "is_draft", "author_login", "author_is_bot",
        "head_repository", "head_repository_owner", "head_branch",
        "head_sha", "base_branch", "base_sha", "title", "mission_id",
        "source_fingerprint", "publisher_workflow_run_id",
        "publisher_workflow_run_attempt", "replay_identity_sha256",
        "canonical_body_prefix_sha256",
    }

    def context(
        self,
        *,
        base: str = "b" * 40,
        current_main: str | None = None,
    ) -> dict[str, str]:
        current_main = current_main or base
        return {
            "repository": "Jktomy/atlas-prime",
            "event_name": "push",
            "event_base_sha": base,
            "current_main_sha": current_main,
            "workflow_ref": "Jktomy/atlas-prime/.github/workflows/generated-checkpoint-publisher.yml@refs/heads/main",
            "workflow_source_sha": base,
            "workflow_run_id": "29367921654",
            "workflow_run_attempt": "1",
            "actor": "Jktomy",
            "triggering_actor": "Jktomy",
            "repository_owner": "Jktomy",
            "credential_principal": "github-actions[bot]",
            "credential_mode": "GITHUB_TOKEN",
        }

    def entry(
        self,
        *,
        number: int = 192,
        mission: str = "RP-C08-TEST",
        draft: bool = True,
        replay: str = "0123456789abcdef" * 4,
        head: str | None = None,
        head_sha: str = "a" * 40,
        base: str = "main",
        base_sha: str = "c" * 40,
        title: str | None = None,
        body: str | None = None,
        body_base_sha: str | None = None,
        body_mission: str | None = None,
        author_login: str | None = "app/github-actions",
        author_is_bot: bool | None = True,
        cross_repository: bool = False,
        head_repository: str | None = "Jktomy/atlas-prime",
        head_owner: str | None = "Jktomy",
        state: str = "OPEN",
        suffix: str = "",
    ) -> dict[str, object]:
        body_mission = body_mission or mission
        body_base_sha = body_base_sha or base_sha
        head = head or f"generated/checkpoint-{mission.lower()}-{replay[:12]}"
        title = title or f"generated: deterministic checkpoint {mission}"
        body = body or (
            f"Hosted RP-C06 generated checkpoint `{body_mission}`.\n\n"
            f"- Exact base: `{body_base_sha}`\n"
            f"- Source fingerprint: `sha256:{'d' * 64}`\n"
            "- Workflow run: `29350853465` attempt `1`\n"
            f"- Replay identity: `sha256:{replay}`\n"
            "- Ubuntu/Windows register parity: exact\n"
            "- Route: singular Thread Engine; draft PR readback stop\n"
            "- Quest/capability promotion: none\n"
            f"{suffix}"
        )
        return {
            "number": number,
            "state": state,
            "isDraft": draft,
            "isCrossRepository": cross_repository,
            "authorLogin": author_login,
            "authorIsBot": author_is_bot,
            "headRefName": head,
            "headRefOid": head_sha,
            "headRepositoryNameWithOwner": head_repository,
            "headRepositoryOwnerLogin": head_owner,
            "baseRefName": base,
            "baseRefOid": base_sha,
            "title": title,
            "body": body,
        }

    def unrelated(self, *, number: int = 189) -> dict[str, object]:
        return self.entry(
            number=number,
            head=f"source/ordinary-repair-{number}",
            title=f"proof: ordinary repair {number}",
            author_login="Jktomy",
            author_is_bot=False,
            body="Ordinary authored-source pull request.\n",
        )

    def assert_receipt_hash(self, receipt: dict[str, object]) -> None:
        observed = receipt["receipt_sha256"]
        candidate = deepcopy(receipt)
        candidate["receipt_sha256"] = "0" * 64
        expected = hashlib.sha256(stable_json(candidate).encode("utf-8")).hexdigest()
        self.assertEqual(observed, expected)

    def assert_receipt_shape(
        self,
        receipt: dict[str, object],
        *,
        checkpoint: bool,
    ) -> None:
        self.assertEqual(set(receipt), self.RECEIPT_KEYS)
        self.assertEqual(receipt["schema_id"], "atlas.generated-checkpoint.queue")
        self.assertEqual(receipt["schema_version"], "1.0.0")
        self.assertEqual(set(receipt["query"]), self.QUERY_KEYS)
        if checkpoint:
            self.assertEqual(set(receipt["checkpoint"]), self.CHECKPOINT_KEYS)
        else:
            self.assertIsNone(receipt["checkpoint"])
        self.assertNotIn("message", receipt)
        self.assertNotIn("error", receipt)

    def cli_args(self, path: Path) -> list[str]:
        context = self.context()
        return [
            "--pull-requests", str(path),
            "--repository", context["repository"],
            "--event-name", context["event_name"],
            "--event-base-sha", context["event_base_sha"],
            "--current-main-sha", context["current_main_sha"],
            "--workflow-ref", context["workflow_ref"],
            "--workflow-source-sha", context["workflow_source_sha"],
            "--workflow-run-id", context["workflow_run_id"],
            "--workflow-run-attempt", context["workflow_run_attempt"],
            "--actor", context["actor"],
            "--triggering-actor", context["triggering_actor"],
            "--repository-owner", context["repository_owner"],
            "--credential-principal", context["credential_principal"],
            "--credential-mode", context["credential_mode"],
        ]

    def test_clear_queue_ignores_unrelated_open_prs(self) -> None:
        result = classify_open_pull_requests([self.unrelated()], self.context())
        self.assertEqual(result["result"], "CLEAR")
        self.assertEqual(result["open_checkpoint_count"], 0)
        self.assertIsNone(result["checkpoint"])
        self.assertFalse(result["mutation_authorized"])
        self.assertEqual(result["query"]["returned_count"], 1)
        self.assert_receipt_shape(result, checkpoint=False)
        self.assert_receipt_hash(result)

    def test_one_exact_publisher_draft_defers_with_closed_hashed_provenance(self) -> None:
        publisher_entry = self.entry(suffix="\nDetached audit note may follow.\n")
        publisher_entry["body"] = publisher_entry["body"].replace("\n", "\r\n")
        result = classify_open_pull_requests(
            [publisher_entry],
            self.context(),
        )
        self.assertEqual(result["result"], "DEFERRED_OPEN_CHECKPOINT")
        self.assertEqual(result["open_checkpoint_count"], 1)
        checkpoint = result["checkpoint"]
        self.assertEqual(checkpoint["number"], 192)
        self.assertEqual(checkpoint["author_login"], "app/github-actions")
        self.assertEqual(checkpoint["head_repository"], "Jktomy/atlas-prime")
        self.assertEqual(checkpoint["mission_id"], "RP-C08-TEST")
        self.assertEqual(checkpoint["replay_identity_sha256"], "0123456789abcdef" * 4)
        self.assertNotIn("body", checkpoint)
        self.assertEqual(result["repository"], "Jktomy/atlas-prime")
        self.assertEqual(result["current_main_sha"], "b" * 40)
        self.assertEqual(result["event_base_sha"], "b" * 40)
        self.assertEqual(result["query"]["limit"], QUERY_LIMIT)
        self.assertEqual(result["query"]["max_accepted_entries"], MAX_OPEN_PULL_REQUESTS)
        self.assertEqual(result["query"]["requested_fields"], list(QUERY_FIELDS))
        self.assertEqual(result["query"]["projection_fields"], list(PROJECTION_FIELDS))
        self.assertRegex(result["query"]["snapshot_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(result["mutation_authorized"])
        self.assert_receipt_shape(result, checkpoint=True)
        self.assert_receipt_hash(result)

    def test_valid_stale_checkpoint_base_defers_against_newer_current_main(self) -> None:
        result = classify_open_pull_requests(
            [self.entry(base_sha="a" * 40)],
            self.context(base="b" * 40, current_main="c" * 40),
        )
        self.assertEqual(result["result"], "DEFERRED_OPEN_CHECKPOINT")
        self.assertEqual(result["checkpoint"]["base_sha"], "a" * 40)
        self.assertEqual(result["event_base_sha"], "b" * 40)
        self.assertEqual(result["current_main_sha"], "c" * 40)

    def test_stale_clear_event_rejects_before_parity(self) -> None:
        with self.assertRaises(QueueError) as raised:
            classify_open_pull_requests(
                [self.unrelated()],
                self.context(base="b" * 40, current_main="c" * 40),
            )
        self.assertEqual(
            raised.exception.code,
            "GENERATED_CHECKPOINT_QUEUE_STALE_BASE",
        )

    def test_multiple_open_generated_drafts_fail_closed(self) -> None:
        with self.assertRaises(QueueError) as raised:
            classify_open_pull_requests(
                [
                    self.entry(),
                    self.entry(number=193, mission="RP-C08-OTHER", replay="f" * 64),
                ],
                self.context(),
            )
        self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_QUEUE_MULTIPLE_OPEN")

    def test_forged_or_inconsistent_generated_identity_fails_closed(self) -> None:
        cases: dict[str, dict[str, object]] = {
            "marker mismatch": self.entry(title="ordinary title"),
            "opposite marker mismatch": self.entry(head="source/not-generated"),
            "not draft": self.entry(draft=False),
            "wrong base": self.entry(base="release"),
            "invalid head": self.entry(head_sha="not-a-sha"),
            "not open": self.entry(state="CLOSED"),
            "cross repository": self.entry(cross_repository=True),
            "wrong author": self.entry(author_login="Jktomy"),
            "non-bot author": self.entry(author_is_bot=False),
            "wrong repository": self.entry(head_repository="Other/atlas-prime"),
            "wrong owner": self.entry(head_owner="Other"),
            "body base mismatch": self.entry(body_base_sha="e" * 40),
            "body mission mismatch": self.entry(body_mission="RP-C08-OTHER"),
            "branch replay mismatch": self.entry(
                head="generated/checkpoint-rp-c08-test-ffffffffffff"
            ),
            "missing canonical provenance": self.entry(body="Generated-looking body.\n"),
            "invalid source fingerprint": self.entry(
                body=self.entry()["body"].replace("d" * 64, "not-a-digest")
            ),
            "invalid workflow attempt": self.entry(
                body=self.entry()["body"].replace("attempt `1`", "attempt `0`")
            ),
        }
        for label, item in cases.items():
            with self.subTest(label=label), self.assertRaises(QueueError):
                classify_open_pull_requests([item], self.context())

        unrelated_fork = self.unrelated()
        unrelated_fork["isCrossRepository"] = True
        unrelated_fork["authorLogin"] = None
        unrelated_fork["authorIsBot"] = None
        unrelated_fork["headRepositoryNameWithOwner"] = None
        unrelated_fork["headRepositoryOwnerLogin"] = None
        receipt = classify_open_pull_requests([unrelated_fork], self.context())
        self.assertEqual(receipt["result"], "CLEAR")

    def test_context_is_closed_exact_and_stale_base_rejects(self) -> None:
        cases = []
        wrong_actor = self.context()
        wrong_actor["actor"] = "Other"
        cases.append(wrong_actor)
        stale_workflow = self.context()
        stale_workflow["workflow_source_sha"] = "c" * 40
        cases.append(stale_workflow)
        extra = self.context()
        extra["extra"] = "rejected"
        cases.append(extra)
        for context in cases:
            with self.subTest(context=context), self.assertRaises(QueueError):
                classify_open_pull_requests([], context)

    def test_1001_sentinel_and_duplicate_numbers_fail_closed(self) -> None:
        accepted = [self.unrelated(number=index) for index in range(1, 1001)]
        receipt = classify_open_pull_requests(accepted, self.context())
        self.assertEqual(receipt["query"]["returned_count"], 1000)
        with self.assertRaises(QueueError) as raised:
            classify_open_pull_requests(
                accepted + [self.unrelated(number=1001)],
                self.context(),
            )
        self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_QUEUE_HISTORY")
        with self.assertRaises(QueueError) as raised:
            classify_open_pull_requests(
                [self.unrelated(number=1), self.unrelated(number=1)],
                self.context(),
            )
        self.assertEqual(raised.exception.code, "GENERATED_CHECKPOINT_QUEUE_DUPLICATE")

    def test_cli_emits_canonical_success_and_hashed_rejection_receipts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="generated-queue-") as raw:
            path = Path(raw) / "open-prs.json"
            path.write_text(json.dumps([self.entry()]), encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(self.cli_args(path)), 0)
            receipt = json.loads(stdout.getvalue())
            self.assertEqual(receipt["result"], "DEFERRED_OPEN_CHECKPOINT")
            self.assert_receipt_shape(receipt, checkpoint=True)
            self.assert_receipt_hash(receipt)

            path.write_text(
                json.dumps([self.unrelated(number=index) for index in range(1, 1002)]),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(self.cli_args(path)), 2)
            rejected = json.loads(stdout.getvalue())
            self.assertEqual(rejected["result"], "REJECTED")
            self.assertEqual(rejected["error_code"], "GENERATED_CHECKPOINT_QUEUE_HISTORY")
            self.assertFalse(rejected["mutation_authorized"])
            self.assertEqual(rejected["query"]["returned_count"], 1001)
            self.assert_receipt_shape(rejected, checkpoint=False)
            self.assert_receipt_hash(rejected)

            invalid = b'[{"number":1,"number":2}]'
            path.write_bytes(invalid)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(self.cli_args(path)), 2)
            rejected = json.loads(stdout.getvalue())
            self.assertEqual(rejected["error_code"], "GENERATED_CHECKPOINT_QUEUE_JSON")
            self.assertEqual(
                rejected["query"]["snapshot_sha256"],
                hashlib.sha256(invalid).hexdigest(),
            )
            self.assert_receipt_shape(rejected, checkpoint=False)
            self.assert_receipt_hash(rejected)

    def test_workflow_admission_query_and_deferred_topology_are_exact(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        validation_workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "prime-readonly-validation.yml"
        ).read_text(encoding="utf-8")
        queue_block = workflow.split("\n  queue:\n", 1)[1].split("\n  parity:\n", 1)[0]
        parity_block = workflow.split("\n  parity:\n", 1)[1].split("\n  reconcile:\n", 1)[0]
        reconcile_block = workflow.split("\n  reconcile:\n", 1)[1].split("\n  prepare:\n", 1)[0]
        prepare_block = workflow.split("\n  prepare:\n", 1)[1].split("\n  publish:\n", 1)[0]
        publish_block = workflow.split("\n  publish:\n", 1)[1]

        self.assertLess(queue_block.index("Admit exact publisher invocation"), queue_block.index("uses:"))
        for phrase in (
            'expectedRepository = "Jktomy/atlas-prime"',
            'expectedOwner = "Jktomy"',
            "$env:GITHUB_ACTOR",
            "$env:GITHUB_TRIGGERING_ACTOR",
            "$env:GITHUB_EVENT_NAME -ceq \"push\"",
            "$env:GITHUB_EVENT_NAME -ceq \"workflow_dispatch\"",
            '"refs/heads/main"',
            "$env:GITHUB_SHA",
            "$env:GITHUB_WORKFLOW_SHA",
            "$env:GENERATED_BASE_SHA",
            "git/ref/heads/main",
        ):
            self.assertIn(phrase, queue_block)
        self.assertIn("pull-requests: read", queue_block)
        self.assertNotIn("contents: write", queue_block)
        self.assertNotIn("pull-requests: write", queue_block)
        self.assertIn("--limit 1001", queue_block)
        self.assertIn(
            "--json number,state,isDraft,isCrossRepository,author,headRefName,headRefOid,headRepository,headRepositoryOwner,baseRefName,baseRefOid,title,body",
            queue_block,
        )
        self.assertIn("sort_by(.number) | map({", queue_block)
        self.assertIn("tools.generated_checkpoint.queue", queue_block)
        self.assertIn('"queue_result=DEFERRED_OPEN_CHECKPOINT"', queue_block)
        self.assertIn("needs: queue", parity_block)
        self.assertIn("needs.queue.result == 'success'", parity_block)
        self.assertIn("needs.queue.outputs.queue_result == 'CLEAR'", parity_block)
        self.assertIn("needs: parity", reconcile_block)
        self.assertIn("needs: reconcile", prepare_block)
        self.assertIn("- prepare", publish_block)
        self.assertIn("DRAFT_CREATED; required pull-request validation pending", publish_block)
        self.assertNotIn("\n  validate_exact_head:\n", workflow)
        self.assertNotIn("Validate generated exact head", workflow)
        self.assertNotIn("needs.publish.outputs.head_sha", workflow)
        self.assertIn("name: prime/integrity", validation_workflow)
        self.assertIn("name: prime/windows-compatibility", validation_workflow)
        for block in (parity_block, reconcile_block, prepare_block, publish_block):
            job_preamble = block.split("\n    steps:\n", 1)[0]
            self.assertNotIn("always()", job_preamble)
            self.assertNotIn("!cancelled()", job_preamble)
            self.assertNotIn("continue-on-error", block)

    def test_workflow_preserves_single_writer_and_no_automatic_permanence(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "generated-checkpoint-publisher.yml"
        ).read_text(encoding="utf-8")
        self.assertNotIn("paths-ignore:", workflow)
        self.assertNotIn('"generated/**"', workflow)
        self.assertEqual(workflow.count("contents: write"), 1)
        self.assertEqual(workflow.count("pull-requests: write"), 1)
        self.assertEqual(workflow.count("production_adapter.cli"), 1)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("actions: write", workflow)
        self.assertNotIn("persist-credentials: true", workflow)
        self.assertNotIn("gh workflow run", workflow)
        self.assertNotIn("gh pr close", workflow)
        self.assertNotIn("gh pr ready", workflow)
        self.assertNotIn("gh pr merge", workflow)
        self.assertNotIn("force-push", workflow)


if __name__ == "__main__":
    unittest.main()
