from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def source(relative: str) -> str:
    return " ".join((ROOT / relative).read_text(encoding="utf-8").split())


class PrimeRepositoryProcessTests(unittest.TestCase):
    def test_direct_request_builds_one_complete_transaction_through_ready(self) -> None:
        bootstrap = source("bootstrap.md")
        contract = source("governance/repository-process-contract.md")
        for marker in (
            "one bounded transaction through an unchanged merge-ready PR",
            "complete-candidate construction",
            "candidate-caused repair",
            "actionable review repair",
            "exact-head Strikeforce",
            "ready-for-review transition",
        ):
            self.assertIn(marker, bootstrap)
        self.assertIn("one transaction identity", contract)
        self.assertIn("one complete candidate", contract)
        self.assertIn("zero or one consolidated repair", contract)

    def test_manual_merge_is_default_and_shardblade_requires_explicit_current_authority(self) -> None:
        for relative in (
            "bootstrap.md",
            "routing/command-surfaces.md",
            "safety/atlas-safety-doctrine.md",
            "governance/change-routes.md",
            "governance/shard-doctrine.md",
            "governance/source-lifecycle.md",
            "governance/repository-process-contract.md",
        ):
            with self.subTest(relative=relative):
                text = source(relative)
                self.assertIn("with Shardblade", text)

        contract = source("governance/repository-process-contract.md")
        shard = source("governance/shard-doctrine.md")
        self.assertIn("default normal route stops", contract)
        self.assertIn("Jayson to merge manually", contract)
        self.assertIn("one transaction-scoped machine permanence action", contract)
        self.assertIn("consumed by one success or terminal safe rejection", contract)
        self.assertIn("one transaction-scoped machine permanence action", shard)
        self.assertIn("cannot be reused", shard)
        self.assertIn("expected head SHA", shard)
        self.assertIn("compare-and-swap", shard)

    def test_goddess_mode_is_bounded_and_never_creates_permanence(self) -> None:
        aegis = source("governance/atlas-aegis.md")
        safety = source("safety/atlas-safety-doctrine.md")
        contract = source("governance/repository-process-contract.md")
        for text in (aegis, safety, contract):
            self.assertIn("Goddess Mode", text)
            self.assertIn("bounded", text)
        self.assertIn("never creates Shardblade authority", source("governance/shard-doctrine.md"))
        self.assertIn("It never grants permanence", source("governance/source-lifecycle.md"))
        self.assertIn("cannot widen", aegis)
        self.assertIn("duplicate branch or PR", aegis)

    def test_normal_and_fallback_publishers_remain_failure_isolated(self) -> None:
        contract = source("governance/repository-process-contract.md")
        routes = source("governance/change-routes.md")
        self.assertIn("singular normal publisher", contract)
        self.assertIn("independent alternate publisher", contract)
        self.assertIn("must not depend on one mutation implementation", contract)
        self.assertIn("one normal repository engine and one independent alternate publisher", routes)
        self.assertIn("must not share one mutation implementation", routes)

    def test_route_takeover_resumes_same_transaction_without_duplicate_work(self) -> None:
        contract = source("governance/repository-process-contract.md")
        recovery = source("recovery/elantris-recovery.md")
        self.assertIn("A blocked route does not authorize a replacement transaction", contract)
        self.assertIn("read-only reconciliation", contract)
        self.assertIn("does not create a second branch or PR", recovery)
        self.assertIn("never create a duplicate mission", recovery)

    def test_changed_bytes_after_ready_restart_exact_head_evidence(self) -> None:
        bootstrap = source("bootstrap.md").lower()
        safety = source("safety/atlas-safety-doctrine.md").lower()
        routes = source("governance/change-routes.md").lower()
        lifecycle = source("governance/source-lifecycle.md").lower()
        contract = source("governance/repository-process-contract.md").lower()

        self.assertIn("changed candidate byte", bootstrap)
        self.assertIn("candidate-byte change", safety)
        self.assertIn("changed candidate bytes", routes)
        self.assertIn("candidate bytes change", lifecycle)
        self.assertIn("replacement bytes invalidate", contract)
        for text in (safety, routes, lifecycle, contract):
            self.assertIn("replacement", text)
            self.assertIn("exact head", text)

    def test_shardblade_ambiguity_is_readback_only_never_blind_retry(self) -> None:
        shard = source("governance/shard-doctrine.md")
        recovery = source("recovery/elantris-recovery.md")
        self.assertIn("readback-only reconciliation", shard)
        self.assertIn("never a blind retry", shard)
        self.assertIn("Never blindly retry a merge", recovery)
        self.assertIn("canonical-main", shard)

    def test_generated_state_has_closed_outcomes(self) -> None:
        contract = source("governance/repository-process-contract.md")
        for marker in ("CURRENT", "STALE_ALLOWED", "STALE_BLOCKING"):
            self.assertIn(marker, contract)


if __name__ == "__main__":
    unittest.main()
