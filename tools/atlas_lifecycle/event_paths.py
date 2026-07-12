from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from .errors import LifecycleError


EVENT_DIRECTORY = PurePosixPath("lifecycle/events")


def declared_event_path(record: dict[str, Any]) -> str:
    """Return the one route-declared immutable storage path for an event."""
    if record.get("schema_id") != "atlas.lifecycle.event":
        raise LifecycleError("EVENT_PATH_SCHEMA", "event storage paths apply only to lifecycle events")
    route = record.get("route")
    allowed = route.get("allowed_paths") if isinstance(route, dict) else None
    if not isinstance(allowed, list) or len(allowed) != 1 or not isinstance(allowed[0], str):
        raise LifecycleError("EVENT_PATH_CARDINALITY", "an event route must declare exactly one storage path")
    value = allowed[0]
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or "\\" in value
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.parent != EVENT_DIRECTORY
        or path.suffix != ".json"
        or path.name in {".json", "..json"}
    ):
        raise LifecycleError(
            "EVENT_PATH_INVALID",
            "event storage path must be one normalized JSON file directly beneath lifecycle/events",
        )
    return value


def bind_event_storage_path(
    record: dict[str, Any],
    repository_path: str,
    seen_paths: set[str],
) -> None:
    """Bind an event ID to its exact physical path and reject path reuse."""
    declared = declared_event_path(record)
    if repository_path != declared:
        raise LifecycleError("EVENT_PATH_MISMATCH", "canonical event path does not match its authorized route")
    folded = declared.casefold()
    if folded in seen_paths:
        raise LifecycleError("EVENT_PATH_COLLISION", "event storage path is reused or case-fold colliding")
    seen_paths.add(folded)
