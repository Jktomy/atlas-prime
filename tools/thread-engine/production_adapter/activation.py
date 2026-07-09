from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ACTIVE_STATE = "THREAD_ENGINE_ACTIVE_MISSION_SCOPED"
DISABLED_STATE = "PORT_CANDIDATE_DISABLED"
STATUS_PATH = Path(__file__).resolve().parents[1] / "PRIME-PORT-STATUS.json"


class ActivationError(Exception):
    def __init__(self, message: str, code: str = "ACTIVATION_STATE_INVALID") -> None:
        super().__init__(message)
        self.code = code


def disabled_activation_state() -> dict[str, Any]:
    return {
        "implementation_state": DISABLED_STATE,
        "production_execution_authorized": False,
        "proof_required": True,
        "standing_authority": False,
        "automatic_merge": False,
        "direct_main": False,
    }


def load_activation_state(path: Path | None = None) -> dict[str, Any]:
    source = path or STATUS_PATH
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ActivationError(f"Prime Thread Engine activation state is unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise ActivationError("Prime Thread Engine activation state must be a JSON object")

    required_types = {
        "implementation_state": str,
        "production_execution_authorized": bool,
        "proof_required": bool,
        "standing_authority": bool,
        "automatic_merge": bool,
        "direct_main": bool,
    }
    for field, expected_type in required_types.items():
        if type(data.get(field)) is not expected_type:
            raise ActivationError(f"Prime Thread Engine activation field is invalid: {field}")

    if data["standing_authority"] or data["automatic_merge"] or data["direct_main"]:
        raise ActivationError("Prime Thread Engine activation state violates permanent safety invariants")

    state = data["implementation_state"]
    enabled = data["production_execution_authorized"]
    if state == DISABLED_STATE:
        if enabled or not data["proof_required"]:
            raise ActivationError("disabled Prime Thread Engine state is internally inconsistent")
    elif state == ACTIVE_STATE:
        if not enabled or data["proof_required"]:
            raise ActivationError("active Prime Thread Engine state is internally inconsistent")
    else:
        raise ActivationError(f"unrecognized Prime Thread Engine implementation state: {state}")
    return dict(data)


def production_execution_enabled(state: dict[str, Any]) -> bool:
    return state.get("implementation_state") == ACTIVE_STATE and state.get("production_execution_authorized") is True


def receipt_activation_fields(state: dict[str, Any]) -> dict[str, Any]:
    active = production_execution_enabled(state)
    return {
        "implementation_state": state.get("implementation_state", DISABLED_STATE),
        "adapter_mode": "DRAFT_PR_ONLY" if active else "DISABLED",
        "thread_engine_active": active,
        "production_execution_authorized": active,
        "authority_scope": "MISSION_SCOPED" if active else "NONE",
    }
