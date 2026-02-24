import logging
import time
from typing import Callable

from config import MiddlewareConfig, settings
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        logger.info(f"Incoming request: {request.method} {request.url.path}")

        response = await call_next(request)

        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code}"
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )


def setup_middleware(app: ASGIApp) -> ASGIApp:
    if settings.MIDDLEWARE_CORS:
        app.add_middleware(
            CORSMiddleware, **MiddlewareConfig.get_cors_middleware_config()
        )
        logger.info("CORS middleware enabled")

    if settings.MIDDLEWARE_GZIP:
        app.add_middleware(
            GZipMiddleware, **MiddlewareConfig.get_gzip_middleware_config()
        )
        logger.info("GZIP middleware enabled")

    if settings.MIDDLEWARE_TRUSTED_HOST:
        app.add_middleware(
            TrustedHostMiddleware, **MiddlewareConfig.get_trusted_hosts_config()
        )
        logger.info("Trusted host middleware enabled")

    if settings.ENV == "prod":
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("HTTPS redirect middleware enabled")

    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

    logger.info(
        "Additional middleware enabled: Timing, Logging, Security, Error Handling"
    )

    return app


async def get_request_id(request: Request) -> str:
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid

        request_id = str(uuid.uuid4())
    return request_id


async def log_request_details(request: Request, request_id: str):
    logger.info(
        f"Request ID: {request_id} | "
        f"Method: {request.method} | "
        f"Path: {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
