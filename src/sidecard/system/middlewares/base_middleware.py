# !/usr/bin/python3

# ** info: python imports
from typing import Dict

# ** info: typing imports
from typing import Self
from contextvars import Context

__all__: list[str] = ["BaseMiddleware"]


class BaseMiddleware:
    async def _set_values_from_request_context_to_dict(self: Self, context: Context, context_key: str) -> Dict:
        kwargs: Dict = dict()
        for item in context.items():
            if item[0].name == context_key:
                kwargs = item[1]
                break
        return kwargs
