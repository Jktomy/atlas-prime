from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from jsonschema import Draft202012Validator

from tools.spear.s1_contracts import (
    S1ContractError,
    load_s1_contracts,
    validate_dual_activation,
    validate_execution_context,
    validate_packet_envelope_binding,
)
from tools.spear.validate import load_json_file
from .helpers import DEST_POLICY_TEXT, PROT_POLICY_TEXT

ROOT = Path(__file__).resolve().parents[2]
ACTIVATION = ROOT / "policies/operations/spear/spear-s1-activation-v1.json"


def run(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(args, cwd=str(cwd), text=True, encoding="utf-8")


class S1ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        run(["git", "init", "-b", "main"], self.repo)
        run(["git", "config", "user.email", "spear@example.test"], self.repo)
        run(["git", "config", "user.name", "Spear Test"], self.repo)
        self._write_contract_tree(
            activation=load_json_file(str(ACTIVATION)),
            destination_text=DEST_POLICY_TEXT,
        )
        run(["git", "add", "."], self.repo)
        run(["git", "commit", "-m", "initial contracts"], self.repo)
        self.commit = run(["git", "rev-parse", "HEAD"], self.repo).strip()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_contract_tree(self, *, activation: dict, destination_text: str) -> None:
        files = {
            "policies/destination/atlas-prime-destination-policy-v0.2.yaml": destination_text,
            "policies/protected-paths/protected-paths-v0.2.yaml": PROT_POLICY_TEXT,
            "policies/operations/spear/spear-s1-activation-v1.json": json.dumps(activation, indent=2, sort_keys=True) + "\n",
            "specs/spear/athenas-spear-s1-writer-contract-v1.md": "A2 contract fixture\n",
        }
        for relative, content in files.items():
            path = self.repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        a2_blob = run(["git", "hash-object", "specs/spear/athenas-spear-s1-writer-contract-v1.md"], self.repo).strip()
        activation["a2_contract"]["git_blob_sha"] = a2_blob
        (self.repo / "policies/operations/spear/spear-s1-activation-v1.json").write_text(
            json.dumps(activation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.a2_blob = a2_blob

    def _load_raw(self) -> tuple[dict, dict]:
        activation = load_json_file(str(self.repo / "policies/operations/spear/spear-s1-activation-v1.json"))
        from tools.spear.policy import load_controlling_policies
        controlling = load_controlling_policies(str(self.repo), self.commit)
        return activation, controlling

    def test_disabled_dual_gate_passes_without_write_authority(self) -> None:
        with patch("tools.spear.s1_contracts.A2_CONTRACT_BLOB", self.a2_blob):
            result = load_s1_contracts(str(self.repo), self.commit, require_enabled=False)
        self.assertEqual(result["state"], "S1_DISABLED_DUAL_GATE_VALIDATED")

    def test_activation_policy_alone_cannot_enable_writes(self) -> None:
        activation, controlling = self._load_raw()
        activation.update({
            "enabled": True, "mode": "ACTIVATED", "status": "ACTIVE",
            "activation_reference": "preview:example",
            "repository_writes_authorized": True,
            "authorized_operations": ["CREATE_FILE", "REPLACE_FILE_FULL"],
        })
        controlling["destination"]["status"] = "ACTIVE"
        with self.assertRaises(S1ContractError) as context:
            validate_dual_activation(activation, controlling, require_enabled=True)
        self.assertEqual(context.exception.code, "destination_write_authority")

    def test_destination_policy_alone_cannot_enable_writes(self) -> None:
        activation, controlling = self._load_raw()
        controlling["destination"]["status"] = "ACTIVE"
        controlling["destination"]["authority"]["repository_writes_authorized"] = True
        controlling["destination"]["authority"]["execution_authorized_operations"] = ["CREATE_FILE", "REPLACE_FILE_FULL"]
        with self.assertRaises(S1ContractError) as context:
            validate_dual_activation(activation, controlling, require_enabled=True)
        self.assertEqual(context.exception.code, "s1_disabled")

    def test_dual_gate_requires_exact_operation_agreement(self) -> None:
        activation, controlling = self._load_raw()
        activation.update({
            "enabled": True, "mode": "ACTIVATED", "status": "ACTIVE",
            "activation_reference": "preview:example",
            "repository_writes_authorized": True,
            "authorized_operations": ["CREATE_FILE", "REPLACE_FILE_FULL"],
        })
        controlling["destination"]["status"] = "ACTIVE"
        controlling["destination"]["authority"]["repository_writes_authorized"] = True
        controlling["destination"]["authority"]["execution_authorized_operations"] = ["CREATE_FILE"]
        with self.assertRaises(S1ContractError) as context:
            validate_dual_activation(activation, controlling, require_enabled=True)
        self.assertEqual(context.exception.code, "destination_operation_authority")

    def test_exact_dual_gate_can_be_validated_without_executing(self) -> None:
        activation, controlling = self._load_raw()
        activation.update({
            "enabled": True, "mode": "ACTIVATED", "status": "ACTIVE",
            "activation_reference": "preview:example",
            "repository_writes_authorized": True,
            "authorized_operations": ["CREATE_FILE", "REPLACE_FILE_FULL"],
        })
        controlling["destination"]["status"] = "ACTIVE"
        controlling["destination"]["authority"]["repository_writes_authorized"] = True
        controlling["destination"]["authority"]["execution_authorized_operations"] = ["CREATE_FILE", "REPLACE_FILE_FULL"]
        self.assertEqual(
            validate_dual_activation(activation, controlling, require_enabled=True),
            "S1_DUAL_ACTIVATION_VALIDATED",
        )

    def test_actor_event_repository_and_packet_binding_are_exact(self) -> None:
        activation, _ = self._load_raw()
        validate_execution_context(activation, actor="Jktomy", event="workflow_dispatch", repository="Jktomy/atlas-prime")
        with self.assertRaises(S1ContractError):
            validate_execution_context(activation, actor="other", event="workflow_dispatch", repository="Jktomy/atlas-prime")
        packet = {"packet_id": "spear-example-001", "base_commit": "a" * 40, "base_branch": "main", "target_repository": "Jktomy/atlas-prime"}
        envelope = {"packet_id": "spear-example-001", "expected_base_commit": "a" * 40}
        validate_packet_envelope_binding(envelope, packet)
        envelope["packet_id"] = "different"
        with self.assertRaises(S1ContractError):
            validate_packet_envelope_binding(envelope, packet)

    def test_execution_schemas_are_valid_draft_2020_12(self) -> None:
        for name in [
            "spear-execution-envelope-v1.schema.json",
            "spear-execution-preview-v1.schema.json",
            "spear-execution-receipt-v1.schema.json",
        ]:
            schema = load_json_file(str(ROOT / "schemas/spear" / name))
            Draft202012Validator.check_schema(schema)


if __name__ == "__main__":
    unittest.main()
