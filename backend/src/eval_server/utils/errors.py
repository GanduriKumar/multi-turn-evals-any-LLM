from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError


class AppError(Exception):
    def __init__(self, message: str, *, code: str = "app_error", status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, message: str = "resource not found", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="not_found", status_code=404, details=details)


class BadRequestError(AppError):
    def __init__(self, message: str = "bad request", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="bad_request", status_code=400, details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "conflict", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="conflict", status_code=409, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "unauthorized", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="unauthorized", status_code=401, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "forbidden", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="forbidden", status_code=403, details=details)


class ProcessingError(AppError):
    def __init__(self, message: str = "processing error", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, code="processing_error", status_code=422, details=details)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    status: int
    error: ErrorBody
    trace_id: str


def _http_code_for_status(status_code: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_error",
    }.get(status_code, "http_error")


def _build_error_response(status_code: int, code: str, message: str, details: Optional[Dict[str, Any]] = None) -> JSONResponse:
    trace_id = str(uuid4())
    body = ErrorResponse(
        status=status_code,
        error=ErrorBody(code=code, message=message, details=details or {}),
        trace_id=trace_id,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def on_app_error(request: Request, exc: AppError):  # type: ignore[unused-ignore]
        return _build_error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError):  # type: ignore[unused-ignore]
        details = {"errors": exc.errors()}
        return _build_error_response(422, "validation_error", "validation failed", details)

    @app.exception_handler(HTTPException)
    async def on_http_error(request: Request, exc: HTTPException):  # type: ignore[unused-ignore]
        code = _http_code_for_status(exc.status_code)
        msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        det = None if isinstance(exc.detail, str) else {"detail": exc.detail}
        return _build_error_response(exc.status_code, code, msg, det)

    @app.exception_handler(Exception)
    async def on_unexpected_error(request: Request, exc: Exception):  # type: ignore[unused-ignore]
        # Avoid leaking internal details in message; include class name in details
        det = {"type": exc.__class__.__name__}
        return _build_error_response(500, "internal_error", "an unexpected error occurred", det)


__all__ = [
    "AppError",
    "NotFoundError",
    "BadRequestError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "ProcessingError",
    "ErrorResponse",
    "add_exception_handlers",
]
