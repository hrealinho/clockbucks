import time
import uuid
import threading
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("clockbucks.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Log request
        start_time = time.time()
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        # Add request ID to state
        request.state.request_id = request_id

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_seconds": round(duration, 4),
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "duration_seconds": round(duration, 4),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add CSP header for non-docs pages
        if not request.url.path.startswith("/docs") and not request.url.path.startswith(
            "/redoc"
        ):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'"
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        cutoff = current_time - self.period

        with self._lock:
            self.clients = {
                ip: [t for t in times if t > cutoff]
                for ip, times in self.clients.items()
            }

            recent = self.clients.get(client_ip, [])

            if len(recent) >= self.calls:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={
                        "Retry-After": str(self.period),
                        "X-RateLimit-Limit": str(self.calls),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + self.period)),
                    },
                )

            recent.append(current_time)
            self.clients[client_ip] = recent

        response = await call_next(request)

        with self._lock:
            remaining = max(0, self.calls - len(self.clients.get(client_ip, [])))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.period))

        return response
