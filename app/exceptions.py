from __future__ import annotations

from typing import Any


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        **extra: Any,
    ):
        self.status_code = status_code
        self.error_code = error_code or self._default_error_code(status_code)
        self.detail = detail
        self.extra = extra

    @staticmethod
    def _default_error_code(status_code: int) -> str:
        return {
            400: "invalid_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            422: "validation_error",
        }.get(status_code, "error")

    def to_dict(self) -> dict[str, Any]:
        payload = {"error_code": self.error_code, "message": self.detail}
        payload.update(self.extra)
        return payload
