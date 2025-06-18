import uuid
from typing import Self

__all__: list[str] = ["UuidProvider"]


class UuidProvider:
    def get_str_uuid(self: Self) -> str:
        return str(uuid.uuid4())

    @staticmethod
    def check_str_uuid(input_uuid: str) -> bool:
        try:
            uuid.UUID(input_uuid, version=4)
            return True
        except ValueError:
            return False
