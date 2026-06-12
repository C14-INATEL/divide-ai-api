from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import users, auth, groups, debts
from app.database import Base, engine
from app.exceptions import AppException
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DivideAi API",
    description="Documentação da API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)


def _http_error_code(status_code: int) -> str:
    return {
        400: "invalid_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        422: "validation_error",
    }.get(status_code, "error")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.to_dict()})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        content = {"error": exc.detail}
    else:
        content = {
            "error": {
                "error_code": _http_error_code(exc.status_code),
                "message": str(exc.detail),
            }
        }
    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(loc) for loc in error["loc"][1:]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "error_code": "validation_error",
                "message": "Request validation failed",
                "errors": errors,
            }
        },
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(debts.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # A Lista VIP
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, DELETE, etc
    allow_headers=["*"], # Permite que o Token passe
)