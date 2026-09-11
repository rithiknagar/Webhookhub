import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = request.headers.get(
            "X-Request-ID"
        )

        if not request_id or len(request_id) > 100:
            request_id = str(uuid.uuid4())

        logger.info(
            "request_started "
            "request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        response = await call_next(request)

        logger.info(
            "request_completed "
            "request_id=%s status_code=%s",
            request_id,
            response.status_code,
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response