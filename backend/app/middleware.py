import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.metrics import REQUEST_COUNT, REQUEST_LATENCY

logger = logging.getLogger("app")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.monotonic()

        response = await call_next(request)

        duration = time.monotonic() - start
        response.headers["X-Request-ID"] = request_id

        REQUEST_COUNT.labels(
            method=request.method, path=request.url.path, status_code=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, path=request.url.path).observe(duration)

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code}",
            extra={"request_id": request_id},
        )
        return response
