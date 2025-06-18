# !/usr/bin/python3
# type: ignore

# ** info: typing imports
from typing import Self

# ** info: ariadne imports
from ariadne import format_error

# ** info: graphql imports
from graphql import GraphQLError

__all__: list[str] = ["error_formatter"]


class ErrorFormatter:
    def __init__(self: Self) -> None:
        pass

    @staticmethod
    def formatter(error: GraphQLError, debug: bool) -> dict:
        if debug is True:
            formatted: dict = format_error(error=error, debug=True)  # type: ignore
            return formatted

        formatted: dict = error.formatted  # type: ignore
        del formatted["locations"]
        del formatted["path"]

        return formatted


error_formatter: ErrorFormatter = ErrorFormatter()
