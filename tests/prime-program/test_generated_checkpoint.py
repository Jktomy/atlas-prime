from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.generated_checkpoint.core import (
    APPROVED_PATHS,
    CheckpointError,
    build_hash_register,
    compare_hash_registers,
    deterministic_branch,
    publish,
    validate_changed_paths,
    validate_pr_readback,
)


ROOT = Path(__file__).resolve().parents[2]


class GeneratedCheckpointTests(unittest.TestCase):
    def test_cross_platform_hash_register_is_byte_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            left_dir = Path(temp) / "linux"
            right_dir = Path(temp) / "windows"
            left = build_hash_register(ROOT, left_dir)
            right = build_hash_register(ROOT, right_dir)
            compare_hash_registers(left, right)
            self.assertEqual(
                (left_dir / "hash-register.json").read_bytes(),
                (right_dir / "hash-register.json").read_bytes(),
            )

    def test_identity_pathset_and_readback_fail_closed(self) -> None:
        base = "1" * 40
        branch = deterministic_branch(base, "fresh-public-nonce-01")
        self.assertEqual(branch, deterministic_branch(base, "fresh-public-nonce-01"))
        with self.assertRaises(CheckpointError):
            deterministic_branch(base, "short")
        with self.assertRaisesRegex(CheckpointError, "GENERATED_PATHSET_INVALID"):
            validate_changed_paths(["generated/atlas-file-inventory.md", "governance/source.md"])
        readback = {
            "number": 1,
            "url": "https://github.com/Jktomy/atlas-prime/pull/1",
            "state": "OPEN",
            "isDraft": True,
            "baseRefName": "main",
            "baseRefOid": base,
            "headRefName": branch,
            "headRefOid": "2" * 40,
            "files": [{"path": path} for path in APPROVED_PATHS],
        }
        validate_pr_readback(readback, branch=branch, head_sha="2" * 40, base_sha=base, expected_paths=APPROVED_PATHS)
        readback["isDraft"] = False
        with self.assertRaisesRegex(CheckpointError, "PR_READBACK_MISMATCH"):
            validate_pr_readback(readback, branch=branch, head_sha="2" * 40, base_sha=base, expected_paths=APPROVED_PATHS)

    def test_publisher_binds_exact_base_generated_only_draft(self) -> None:
        base = "1" * 40
        head = "2" * 40
        nonce = "fresh-public-nonce-02"
        branch = deterministic_branch(base, nonce)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            root.mkdir()
            (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
            receipt = Path(temp) / "evidence" / "receipt.json"
            committed = False

            def runner(arguments: list[str] | tuple[str, ...]) -> str:
                nonlocal committed
                args = list(arguments)
                if args[:3] == ["git", "rev-parse", "HEAD"]:
                    return head if committed else base
                if args[:3] == ["git", "status", "--porcelain"]:
                    return ""
                if args[:3] == ["git", "ls-remote", "origin"]:
                    return f"{base}\trefs/heads/main" if args[-1] == "refs/heads/main" else ""
                if args[:3] == ["gh", "pr", "list"]:
                    return "[]"
                if args[:3] == ["git", "diff", "--name-only"] or args[:4] == ["git", "diff", "--cached", "--name-only"]:
                    return "\n".join(APPROVED_PATHS)
                if args[:2] == ["git", "-c"] and "commit" in args:
                    committed = True
                    return ""
                if args[:3] == ["gh", "pr", "create"]:
                    return "https://github.com/Jktomy/atlas-prime/pull/999"
                if args[:3] == ["gh", "pr", "view"]:
                    return json.dumps({
                        "number": 999, "url": "https://github.com/Jktomy/atlas-prime/pull/999",
                        "state": "OPEN", "isDraft": True, "baseRefName": "main", "baseRefOid": base,
                        "headRefName": branch, "headRefOid": head,
                        "files": [{"path": path} for path in APPROVED_PATHS],
                    })
                return ""

            result = publish(root, repository="Jktomy/atlas-prime", base_sha=base, replay_nonce=nonce, run_id="12345", receipt_path=receipt, runner=runner)
            self.assertEqual(result["stop_point"], "DRAFT_PR_READBACK")
            self.assertEqual(result["forbidden_actions"], {"direct_main": False, "force_push": False, "ready": False, "merge": False, "second_writer": False})
            self.assertEqual(json.loads(receipt.read_text(encoding="utf-8")), result)

    def test_workflow_is_owner_triggered_and_stops_at_draft(self) -> None:
        text = (ROOT / ".github/workflows/generated-checkpoint-publisher.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("OWNER_REQUIRED", text)
        self.assertIn("pull-requests: write", text)
        self.assertNotIn("gh pr merge", text)
        self.assertNotIn("gh pr ready", text)
        self.assertNotIn("push --force", text)


if __name__ == "__main__":
    unittest.main()
