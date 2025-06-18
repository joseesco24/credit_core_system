# !/usr/bin/python3

# ** info: python imports
import gc
import sys
import logging
from os import path
from typing import Any
from typing import Dict

# ** info: typing imports
from typing import List
from os.path import join

# ---------------------------------------------------------------------------------------------------------------------
# ** info: appending src path to the system paths for absolute imports from src path
# ---------------------------------------------------------------------------------------------------------------------

sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# ---------------------------------------------------------------------------------------------------------------------
# ** info: continuing with the app setup
# ---------------------------------------------------------------------------------------------------------------------

# ** info: uvicorn imports
import uvicorn
from fastapi import FastAPI
from fastapi import APIRouter
from starlette.routing import Mount
from starlette.routing import Route
from starlette.routing import BaseRoute

# ** info: fastapi imports
from fastapi.middleware.cors import CORSMiddleware

# ** info: starlette imports
from starlette.middleware.base import BaseHTTPMiddleware
from src.sidecard.system.artifacts.env_provider import EnvProvider  # type: ignore
from src.sidecard.system.artifacts.path_provider import PathProvider  # type: ignore

# ** info: sidecards.artifacts imports
from src.sidecard.system.artifacts.logging_provider import LoggingProvider  # type: ignore

# ---------------------------------------------------------------------------------------------------------------------
# ** info: building needed artifacts
# ---------------------------------------------------------------------------------------------------------------------

path_provider: PathProvider = PathProvider()
env_provider: EnvProvider = EnvProvider()  # type: ignore

# ---------------------------------------------------------------------------------------------------------------------
# ** info: continuing with the app setup
# ---------------------------------------------------------------------------------------------------------------------

from src.modules.user.rest_controllers.user_controller import user_controller
from src.sidecard.system.middlewares.error_handler_middleware import ErrorHandlerMiddleware  # type: ignore
from src.modules.heart_beat.rest_controllers.heart_beat_controller import heart_beat_controller
from src.sidecard.system.middlewares.logger_contextualizer_middleware import LoggerContextualizerMiddleware  # type: ignore

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up global app logging
# ---------------------------------------------------------------------------------------------------------------------

if env_provider.app_logging_mode == "structured":
    LoggingProvider.setup_structured_logging()
    logging.info(f"logger setup on {env_provider.app_logging_mode.lower()} mode")
else:
    LoggingProvider.setup_pretty_logging()
    logging.info(f"logger setup on {env_provider.app_logging_mode.lower()} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

routes: List[Route] = []

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

# routes.append(user_gpl_router)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: mounting graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

graphql_routers: List[BaseRoute] = [Mount(path=path_provider.build_posix_path("graphql"), routes=routes)]

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app metadata and documentation
# ---------------------------------------------------------------------------------------------------------------------

metadata: Dict[str, Any] = {
    "description": "The SAR Core Microservice is the incharge of provide some of the most important capabilities of the SAR system, as wastes collect request management, waste management and clients management",  # noqa # fmt: skip
    "summary": "Service incharge of managing wastes, collect request, and system parameters.",
    "title": "Sar Python Microservice",
    "version": "v1.0.0",
}

credit_core_system: FastAPI
if env_provider.app_swagger_docs is True:
    credit_core_system = FastAPI(routes=graphql_routers, docs_url=path_provider.build_posix_path("rest", "docs"), redoc_url=None, swagger_ui_parameters={"defaultModelsExpandDepth": -1}, **metadata)  # noqa # fmt: skip
    logging.warning("swagger docs active")
else:
    credit_core_system = FastAPI(routes=graphql_routers, docs_url=None, redoc_url=None, **metadata)
    logging.warning("swagger docs inactive")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting rest base router
# ---------------------------------------------------------------------------------------------------------------------

rest_router: APIRouter = APIRouter(prefix=path_provider.build_posix_path("rest"))

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting rest routers
# ---------------------------------------------------------------------------------------------------------------------

rest_router.include_router(router=heart_beat_controller)
rest_router.include_router(router=user_controller)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: mounting rest based routers
# ---------------------------------------------------------------------------------------------------------------------

credit_core_system.include_router(rest_router)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up app middlewares
# ---------------------------------------------------------------------------------------------------------------------

credit_core_system.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=ErrorHandlerMiddleware())
credit_core_system.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=LoggerContextualizerMiddleware())
credit_core_system.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ---------------------------------------------------------------------------------------------------------------------
# ** info: erasing unnecessary artifacts builded during the app setup
# ---------------------------------------------------------------------------------------------------------------------

del path_provider
gc.collect()

# ---------------------------------------------------------------------------------------------------------------------
# ** info: hot reload notification
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    logging.info(f"application started in {env_provider.app_environment_mode.lower()} mode")
if __name__ != "__main__":
    logging.info(f"application reloaded in {env_provider.app_environment_mode.lower()} mode")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting up uvicorn asgi server with fast api app
# ---------------------------------------------------------------------------------------------------------------------

uvicorn_server_configs: Dict[str, Any] = {
    "app": credit_core_system if env_provider.app_environment_mode == "production" else "credit_core_system:credit_core_system",
    "log_level": "debug" if env_provider.app_environment_mode != "production" else "error",
    "use_colors": False if env_provider.app_environment_mode == "production" else True,
    "reload": False if env_provider.app_environment_mode == "production" else True,
    "reload_excludes": ["**/*.pyc", "**/*.pyc.*", "**/*.pyo"],
    "reload_includes": ["**/*.py", "**/*.graphql"],
    "port": env_provider.app_server_port,
    "access_log": False,
    "host": "0.0.0.0",
}

logging.info(f"logger level set to {env_provider.app_logging_level.value} mode")
logging.info(f"application starting on port {env_provider.app_server_port}")
logging.info(f"application timezone set to {env_provider.app_time_zone.value}")
logging.info(f"application locale set to {env_provider.app_posix_locale.value}")

# ---------------------------------------------------------------------------------------------------------------------
# ** info: running app using the previous uvicorn asgi server settings
# ---------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(**uvicorn_server_configs)

if env_provider.app_environment_mode == "production":
    logging.debug("application ended")
