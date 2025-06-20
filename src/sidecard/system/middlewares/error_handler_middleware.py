import contextvars
import logging
from typing import Callable
from typing import Dict
from typing import Self

from fastapi import status as HttpStatus
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import StreamingResponse

from src.sidecard.system.middlewares.base_middleware import BaseMiddleware

__all__: list[str] = ["ErrorHandlerMiddleware"]


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self: Self, request: Request, call_next: Callable) -> StreamingResponse:
        logging.debug("error handler middleware started")

        loguru_context: Dict = await self._set_values_from_request_context_to_dict(context=contextvars.copy_context(), context_key=r"loguru_context")
        internal_id = loguru_context[r"internalId"]

        try:
            response = await call_next(request)
            logging.debug("error handler middleware ended")
            return response
        except Exception:
            logging.exception(f"an error has occurred while processing the request {internal_id}")
            return JSONResponse(status_code=HttpStatus.HTTP_500_INTERNAL_SERVER_ERROR, content={r"detail": r"Internal Server Error"})  # type: ignore
