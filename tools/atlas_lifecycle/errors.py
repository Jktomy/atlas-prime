from __future__ import annotations


class LifecycleError(Exception):
    """Expected fail-closed lifecycle validation error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def sanitized(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}
