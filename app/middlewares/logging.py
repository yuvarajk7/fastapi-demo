import sys
import logging
import time
from datetime import datetime
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from pydantic import BaseModel
import uuid



class RequestLogData(BaseModel):
    timestamp: datetime
    request_id: str
    method: str
    path: str
    status_code: int
    duration_ms: float
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

def default_log_handler(log_data: RequestLogData):
    logger = logging.getLogger("api_logger")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info(
        f"{log_data.method} {log_data.path} - "
        f"ID: {log_data.request_id} - "
        f"Status: {log_data.status_code} - "
        f"IP: {log_data.client_ip} - "
        f"UA: {log_data.user_agent} - "
        f"Duration: {log_data.duration_ms}ms"
    )

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter_ns()
        request_id = str(uuid.uuid4())
        response = await call_next(request)

        process_time_ms = round((time.perf_counter_ns() - start_time) / 1_000_000, 2)

        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        response.headers["X-Request-ID"] = request_id

        log_data = RequestLogData(
            timestamp = datetime.now(),
            request_id = request_id,
            method = request.method,
            path = request.url.path,
            status_code = response.status_code,
            duration_ms = process_time_ms,
            client_ip = request.client.host if request.client else None,
            user_agent = request.headers.get("user-agent", "")
        )
        default_log_handler(log_data)
        return  response

