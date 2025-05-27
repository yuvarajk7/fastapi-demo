import time
from time import process_time_ns

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter_ns()

        response = await call_next(request)

        process_time_ms = round((time.perf_counter_ns() - start_time) / 1_000_000, 2)

        response.headers["X-Process-Time-Ms"] = str(process_time_ms)

        return  response

