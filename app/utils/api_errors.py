from fastapi import HTTPException

from typing import Any, Dict, Optional, Union

ErrorDetail = Optional[Union[str, Dict[str, str]]]

def raise_error_response(error: Union[Any, BaseException], detail: ErrorDetail = None, **args):
    error_body = dict(error.error)

    if detail is not None:
        error_body["detail"] = detail

    if args:
        error_body = {**error_body, **args}

    raise HTTPException(status_code=error.status_code, detail=error_body)


class NotFound:
    status_code = 404

    error = {
        "type": "not_found",
        "description": "O servidor não conseguiu encontrar o recurso requisitado."
    }

class Forbidden:
    status_code = 403

    error = {
        "type": "not_found",
        "description": "O usuário não possui acesso a este recurso"
    }


class GenericBadRequest:
    def __init__(self, error: Optional[Dict] = None) -> None:
        self.status_code = 400

        self.error = error if error else {
            "type": "invalid_resource",
            "description": "O recurso requisitado é inválido."
        }