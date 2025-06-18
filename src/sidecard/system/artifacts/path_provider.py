import posixpath
from typing import Self

__all__: list[str] = ["PathProvider"]


class PathProvider:
    def build_posix_path(self: Self, *args: str) -> str:
        partial_path: str = posixpath.join(*args)
        return f"/{partial_path}".strip()
