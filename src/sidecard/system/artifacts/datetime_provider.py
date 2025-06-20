from calendar import month_name
from datetime import datetime
from typing import Self

from pytz import timezone

from src.sidecard.system.artifacts.env_provider import EnvProvider

__all__: list[str] = ["DatetimeProvider"]


class DatetimeProvider:
    __slots__ = ["_env_provider", "_timezone"]

    def __init__(self: Self) -> None:
        self._env_provider: EnvProvider = EnvProvider()  # type: ignore
        self._timezone = timezone(self._env_provider.app_time_zone)

    def get_month_literal(self: Self, month_number: int) -> str:
        return month_name[month_number].lower() if 1 <= month_number <= 12 else "undefined"

    def get_current_time(self: Self) -> datetime:
        return datetime.now(tz=self._timezone)

    def iso_string_to_datetime(self: Self, iso_string: str) -> datetime:
        return datetime.strptime(iso_string, "%Y-%m-%d %H:%M:%S.%f")

    def pretty_date_string_to_date(self: Self, iso_string: str) -> datetime:
        return datetime.strptime(iso_string, "%d/%m/%Y")

    def prettify_date_time_obj(self: Self, date_time_obj: datetime) -> str:
        return date_time_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

    def prettify_date_obj(self: Self, date_time_obj: datetime) -> str:
        return date_time_obj.strftime("%d/%m/%Y")

    def get_time_delta_in_ms(self: Self, start_time: datetime, end_time: datetime) -> int:
        return int((end_time - start_time).total_seconds() * 1000)
