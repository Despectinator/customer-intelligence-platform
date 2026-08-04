"""
Global exception handlers, registered on the FastAPI app in main.py.

The main thing this solves: without a catch-all handler, any unhandled
exception (a bug in app/ml/, a database hiccup, anything not already
wrapped in an HTTPException by the services layer) falls through to
FastAPI/Starlette's default error handling, which — depending on server
config — can leak internal details (file paths, exception messages,
sometimes a full traceback) to the client. That's a real information
disclosure risk, not a theoretical one.

This handler always logs the real exception server-side, but only
includes exception details in the HTTP response when settings.DEBUG is
True (local development). In production (DEBUG=False), the client gets a
generic message and nothing else — matching the {"success": false,
"message": "..."} error shape documented in docs/api/API-Design.md.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.exceptions.custom_exceptions import AppException

logger = logging.getLogger("app")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning("AppException on %s %s: %s", request.method, request.url.path, exc.message)
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # This is the real safety net: anything not already caught and
        # turned into a proper HTTPException by a route or service ends
        # up here, instead of leaking a raw traceback to the client.
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)

        if settings.DEBUG:
            message = f"{type(exc).__name__}: {exc}"
        else:
            message = "An unexpected error occurred. Please try again or contact support."

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": message},
        )
