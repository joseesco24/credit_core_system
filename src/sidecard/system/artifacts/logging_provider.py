import json
import logging
import sys
import traceback
from datetime import datetime
from types import FrameType
from types import TracebackType
from typing import Any
from typing import Dict
from typing import Self
from typing import Union

from loguru import logger
from loguru._recattrs import RecordException

from src.sidecard.system.artifacts.datetime_provider import DatetimeProvider
from src.sidecard.system.artifacts.env_provider import EnvProvider

__all__: list[str] = ["LoggingProvider"]


class LoggingProvider:
    _env_provider: EnvProvider = EnvProvider()  # type: ignore
    _level: str = _env_provider.app_logging_level.value
    _datetime_provider: DatetimeProvider = DatetimeProvider()

    _extras: Dict[str, str] = {
        "rqStartTime": _datetime_provider.get_current_time(),  # type: ignore
        "internalId": "397d4343-2855-4c92-b64b-58ee82006e0b",
        "externalId": "97c3cb45-453f-4bd0-b0d5-d06cd568be27",
        "version": "v1.2.0",
    }

    @classmethod
    def setup_pretty_logging(cls) -> None:
        """setup pretty logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        fmt: str = "[{extra[version]}][<fg #66a3ff>{extra[currentTime]}</fg #66a3ff>:<fg #fc03cf>{extra[externalId]}</fg #fc03cf>] <level>{level}</level>: {message} <fg #ff0404>+{extra[sinceLastLogMsDif]}</fg #ff0404> <fg #54ff04>{extra[sinceRqStartMsDif]}</fg #54ff04>"  # noqa # fmt: skip

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [cls._CustomInterceptHandler()]
        logging.root.setLevel(cls._level)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = list()
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {"sink": cls._pretty_log_sink, "serialize": False, "colorize": True, "format": fmt}

        logger.configure(patcher=lambda record: cls._pretty_record_patcher(record), extra=cls._extras, handlers=[loguru_configs])  # type: ignore

    @classmethod
    def _pretty_log_sink(cls, message: str) -> None:
        sys.stdout.write(message)
        sys.stdout.flush()

    @classmethod
    def _pretty_record_patcher(cls, record: logging.LogRecord) -> logging.LogRecord:
        end_time: datetime = cls._datetime_provider.get_current_time()
        last_log_time: datetime = record["extra"]["lastLogTime"]  # type: ignore
        start_time: datetime = record["extra"]["rqStartTime"]  # type: ignore

        elapsed_since_last_log: int = cls._datetime_provider.get_time_delta_in_ms(start_time=last_log_time, end_time=end_time)
        elapsed_miliseconds: int = cls._datetime_provider.get_time_delta_in_ms(start_time=start_time, end_time=end_time)

        record["extra"]["sinceLastLogMsDif"] = f"{elapsed_since_last_log}ms"  # type: ignore
        record["extra"]["sinceRqStartMsDif"] = f"{elapsed_miliseconds}ms"  # type: ignore

        if record["level"].name == "INFO" or record["level"].name == "DEBUG":  # type: ignore
            record["message"] = str(record["message"]).replace("\n", " ")  # type: ignore

        return record

    @classmethod
    def setup_structured_logging(cls) -> None:
        """setup structured logging
        this function overwrites the python root logger with a custom logger, so all the logs are
        written with the new overwritten configuration
        """

        fmt: str = "{message}"

        # ** info: overwriting all the loggers configs with the new one
        logging.root.handlers = [cls._CustomInterceptHandler()]
        logging.root.setLevel(cls._level)

        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = list()
            logging.getLogger(name).propagate = True

        # ** info: loguru configs
        loguru_configs: dict = {"sink": cls._structured_log_sink, "serialize": True, "colorize": False, "format": fmt}

        logger.configure(patcher=lambda record: cls._structured_record_patcher(record), extra=cls._extras, handlers=[loguru_configs])  # type: ignore

    @classmethod
    def _structured_log_sink(cls, message: str) -> None:
        serialized = cls._custom_serializer(message.record)  # type: ignore
        sys.stdout.write(serialized)
        sys.stdout.write("\n")
        sys.stdout.flush()

    @classmethod
    def _structured_record_patcher(cls, record: logging.LogRecord) -> logging.LogRecord:
        end_time: datetime = cls._datetime_provider.get_current_time()
        last_log_time: datetime = record["extra"]["lastLogTime"]  # type: ignore
        start_time: datetime = record["extra"]["rqStartTime"]  # type: ignore

        elapsed_since_last_log: int = cls._datetime_provider.get_time_delta_in_ms(start_time=last_log_time, end_time=end_time)
        elapsed_miliseconds: int = cls._datetime_provider.get_time_delta_in_ms(start_time=start_time, end_time=end_time)

        record["extra"]["sinceLastLogMsDif"] = elapsed_since_last_log  # type: ignore
        record["extra"]["sinceRqStartMsDif"] = elapsed_miliseconds  # type: ignore

        return record

    @classmethod
    def _custom_serializer(cls, record) -> str:
        req_ms_dif: int = record["extra"]["sinceRqStartMsDif"]
        log_ms_dif: int = record["extra"]["sinceLastLogMsDif"]

        subset: Dict[str, Any] = {
            "severity": record["level"].name,
            "message": record["message"],
            "externalId": record["extra"]["externalId"],
            "internalId": record["extra"]["internalId"],
            "rqStartTime": cls._datetime_provider.prettify_date_time_obj(date_time_obj=record["extra"]["rqStartTime"]),
            "currentTime": cls._datetime_provider.prettify_date_time_obj(date_time_obj=record["extra"]["currentTime"]),
            "lastLogTime": cls._datetime_provider.prettify_date_time_obj(date_time_obj=record["extra"]["lastLogTime"]),
            "sinceLastLogMsDif": f"{log_ms_dif}ms",
            "sinceRqStartMsDif": f"{req_ms_dif}ms",
            "version": record["extra"]["version"],
        }

        if record["exception"] is not None:
            error: RecordException = record["exception"]

            error_traceback: TracebackType = error.traceback
            error_message: str = error.value.args[0]
            error_type: str = error.type.__name__
            string_traceback: str

            string_traceback = "".join(traceback.format_tb(error_traceback))

            subset["erro"] = {"type": error_type, "message": error_message, "traceback": string_traceback}

        return json.dumps(subset)

    class _CustomInterceptHandler(logging.Handler):
        _datetime_provider: DatetimeProvider = DatetimeProvider()
        _last_log_time: datetime = _datetime_provider.get_current_time()

        def emit(self: Self, record: logging.LogRecord):
            level: Union[str, int]

            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame: FrameType = logging.currentframe()
            depth: int = 2

            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back  # type: ignore
                depth += 1

            current_time = self._datetime_provider.get_current_time()

            logger.opt(depth=depth, exception=record.exc_info).bind(currentTime=current_time, lastLogTime=self._last_log_time).log(level, record.getMessage())

            self._last_log_time = current_time
