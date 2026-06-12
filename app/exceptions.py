from __future__ import annotations

from typing import Any


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str | dict[str, Any],
        error_code: str | None = None,
        **extra: Any,
    ):
        self.status_code = status_code
        self.error_code = error_code or self._default_error_code(status_code)
        self.detail = self._normalize_detail(detail)
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

    def _normalize_detail(self, detail: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(detail, dict):
            return {"error_code": self.error_code, **detail}
        return {"error_code": self.error_code, "message": detail}

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.detail)
        payload.update(self.extra)
        return payload
