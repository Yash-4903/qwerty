from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": str(exc.status_code), "message": str(exc.detail)}},
        )
    return await generic_exception_handler(request, exc)


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
        msg = "; ".join([f"{e.get('loc', [''])[-1]}: {e.get('msg')}" for e in errors])
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "validation_error", "message": msg}},
        )
    return await generic_exception_handler(request, exc)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s: %s", request.method, request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "An internal error occurred"}},
    )
