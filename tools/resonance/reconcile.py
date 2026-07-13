from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from tools.athena_routes.schema import SchemaValidationError, validate_schema


ROOT = Path(__file__).resolve().parents[2]
FINDING_SCHEMA = ROOT / "schemas" / "resonance-finding-v1.schema.json"
REGISTER_SCHEMA = ROOT / "schemas" / "aberration-register-v1.schema.json"


class ResonanceValidationError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def stable_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(value: Any) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    elif not isinstance(value, bytes):
        value = stable_json(value)
    return hashlib.sha256(value).hexdigest()


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_finding(finding: dict[str, Any], *, input_sha256: str) -> None:
    try:
        validate_schema(_schema(FINDING_SCHEMA), finding)
    except SchemaValidationError as exc:
        raise ResonanceValidationError("FINDING_SCHEMA_INVALID") from exc
    if finding["input_sha256"] != input_sha256:
        raise ResonanceValidationError("FINDING_INPUT_MISMATCH")
    if finding["independence"]["prior_lane_visibility"]:
        raise ResonanceValidationError("FINDING_NOT_INDEPENDENT")
    if finding["agent_identity"]["stormlight"] == "LOCAL":
        raise ResonanceValidationError("LOCAL_RUNTIME_PROOF_REQUIRED")
    if len({item["source"] for item in finding["evidence"]}) != len(finding["evidence"]):
        raise ResonanceValidationError("FINDING_EVIDENCE_DUPLICATE")
    for item in finding["evidence"]:
        source = PurePosixPath(item["source"])
        if source.is_absolute() or any(part in {"", ".", ".."} for part in source.parts):
            raise ResonanceValidationError("FINDING_EVIDENCE_INVALID")
        if item["evidence_type"] == "REPOSITORY_FILE":
            path = ROOT.joinpath(*source.parts)
            if not path.is_file() or sha256(path.read_bytes()) != item["sha256"]:
                raise ResonanceValidationError("FINDING_EVIDENCE_MISMATCH")
        elif not item["source"].startswith("fixture/") or item["sha256"] != sha256(finding["statement"].strip()):
            raise ResonanceValidationError("FINDING_EVIDENCE_MISMATCH")


def reconcile_findings(findings: list[dict[str, Any]], *, input_sha256: str, register_id: str) -> dict[str, Any]:
    if not findings:
        raise ResonanceValidationError("FINDINGS_REQUIRED")
    for finding in findings:
        validate_finding(finding, input_sha256=input_sha256)
    ids = [finding["finding_id"] for finding in findings]
    lanes = [finding["lane_id"] for finding in findings]
    if len(ids) != len(set(ids)):
        raise ResonanceValidationError("FINDING_ID_DUPLICATE")
    if len(lanes) != len(set(lanes)):
        raise ResonanceValidationError("LANE_REUSE_REJECTED")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        grouped[finding["claim_key"]].append(finding)
    records = []
    for claim_key in sorted(grouped):
        group = sorted(grouped[claim_key], key=lambda item: item["finding_id"])
        statements = [sha256(item["statement"].strip()) for item in group]
        if len(group) == 1:
            classification, recommendation = "NOVEL", "SEEK_SECOND_LANE"
            reason = "Only one sealed independent lane reported this claim."
        elif len(set(statements)) == 1:
            classification, recommendation = "CONSENSUS", "REVIEW_FOR_ACCEPTANCE"
            reason = "Independent lanes reported byte-equivalent normalized statements."
        else:
            classification, recommendation = "CONFLICT", "INVESTIGATE_CONFLICT"
            reason = "Independent lanes reported different statements for one claim key."
        records.append({
            "claim_key": claim_key,
            "classification": classification,
            "finding_ids": [item["finding_id"] for item in group],
            "statement_sha256s": statements,
            "athena_refraction": {"operator": "Athena", "recommendation": recommendation, "reason": reason, "is_final": False},
            "disposition": "OPEN_HUMAN_REVIEW",
            "human_decision": None,
        })
    register = {
        "schema_version": "atlas.aberration-register.v1",
        "register_id": register_id,
        "campaign": "RP-C04",
        "gate": "RESONANCE_EVIDENCE_RECONCILED",
        "gate_status": "EVIDENCE_RECONCILED",
        "input_sha256": input_sha256,
        "finding_sha256s": [sha256(item) for item in sorted(findings, key=lambda item: item["finding_id"])],
        "records": records,
        "local_model": {"status": "BLOCKED_RUNTIME_PROOF_ABSENT", "runtime_proof_sha256": None, "finding_ids": []},
        "promotion": "NONE",
    }
    try:
        validate_schema(_schema(REGISTER_SCHEMA), register)
    except SchemaValidationError as exc:
        raise ResonanceValidationError("REGISTER_SCHEMA_INVALID") from exc
    return register
