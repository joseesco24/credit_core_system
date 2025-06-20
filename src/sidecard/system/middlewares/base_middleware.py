from contextvars import Context
from typing import Dict
from typing import Self

__all__: list[str] = ["BaseMiddleware"]


class BaseMiddleware:
    async def _set_values_from_request_context_to_dict(self: Self, context: Context, context_key: str) -> Dict:
        kwargs: Dict = dict()
        for item in context.items():
            if item[0].name == context_key:
                kwargs = item[1]
                break
        return kwargs
