from enum import Enum
from pydantic import Field
from pydantic import HttpUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

__all__: list[str] = ["EnvProvider"]


class EnvironmentMode(str, Enum):
    development: str = "development"  # type: ignore
    production: str = "production"  # type: ignore


class LoggingLevel(str, Enum):
    debug: str = "DEBUG"  # type: ignore
    info: str = "INFO"  # type: ignore
    warning: str = "WARNING"  # type: ignore
    error: str = "ERROR"  # type: ignore
    critical: str = "CRITICAL"  # type: ignore


class LoggingMode(str, Enum):
    structured: str = "structured"  # type: ignore
    pretty: str = "pretty"  # type: ignore


class SupportedLocales(str, Enum):
    colombia: str = "es_CO.UTF-8"  # type: ignore
    usa: str = "en_US.UTF-8"  # type: ignore


class SupportedTimeZones(str, Enum):
    colombia: str = "America/Bogota"  # type: ignore
    usa: str = "America/New_York"  # type: ignore


class EnvProvider(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_environment_mode: EnvironmentMode = Field(..., validation_alias="APP_ENVIRONMENT_MODE")
    app_logging_mode: LoggingMode = Field(..., validation_alias="APP_LOGGING_MODE")
    app_logging_level: LoggingLevel = Field(..., validation_alias="APP_LOGGING_LEVEL")
    app_server_port: int = Field(..., validation_alias="APP_SERVER_PORT")
    app_swagger_docs: bool = Field(..., validation_alias="APP_SWAGGER_DOCS")
    app_posix_locale: SupportedLocales = Field(..., validation_alias="APP_POSIX_LOCALE")
    app_time_zone: SupportedTimeZones = Field(..., validation_alias="APP_TIME_ZONE")

    database_password: str = Field(..., validation_alias="DATABASE_PASSWORD")
    database_logs: bool = Field(..., validation_alias="DATABASE_LOGS")
    database_host: str = Field(..., validation_alias="DATABASE_HOST")
    database_name: str = Field(..., validation_alias="DATABASE_NAME")
    database_user: str = Field(..., validation_alias="DATABASE_USER")
    database_port: int = Field(..., validation_alias="DATABASE_PORT")

    identity_validation_ms_base_url: HttpUrl = Field(..., validation_alias="IDENTITY_VALIDATION_MS_BASE_URL")
    scoring_ms_base_url: HttpUrl = Field(..., validation_alias="SCORING_MS_BASE_URL")
