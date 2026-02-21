import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Middleware to add request context (request_id and timing) to each request
class RequestContextMiddleware(BaseHTTPMiddleware):
    # This middleware generates a unique request_id for each incoming request and tracks the duration of the request processing. It adds the request_id to the request state, which can be accessed by downstream handlers and agents for logging and tracing purposes.
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        # Add request_id to request state for access in handlers and agents
        request.state.request_id = request_id
        # Log the incoming request with request_id and agent context
        response = await call_next(request)

        duration = int((time.time() - start_time) * 1000)

        logging.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "agent": "api",
                "duration_ms": duration,
            },
        )

        return response
