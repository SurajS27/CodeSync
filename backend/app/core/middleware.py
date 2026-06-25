import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("codesync.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log details about every incoming HTTP request and response."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"HTTP {method} {path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms",
                extra={"metadata": f"middleware:{method}:{path}"},
            )
            return response
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"HTTP {method} {path} failed - Error: {str(e)} - Duration: {duration_ms:.2f}ms",
                exc_info=True,
                extra={"metadata": f"middleware:{method}:{path}"},
            )
            raise e
