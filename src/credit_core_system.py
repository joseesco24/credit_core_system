import sys
from os import path
from os.path import join

# ---------------------------------------------------------------------------------------------------------------------
# ** info: appending src path to the system paths for absolute imports from src path
# ---------------------------------------------------------------------------------------------------------------------

sys.path.append(join(path.dirname(path.realpath(__file__)), "..", "."))

# ---------------------------------------------------------------------------------------------------------------------
# ** info: continuing with the app setup
# ---------------------------------------------------------------------------------------------------------------------

import gc
import logging
from typing import Any
from typing import Dict

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import BaseRoute
from starlette.routing import Mount
from starlette.routing import Route

from src.modules.account.graphql_controllers.account_controller import account_gpl_controller
from src.modules.account.rest_controllers.account_controller import account_controller
from src.modules.credit_request.graphql_controllers.credit_request_controller import credit_request_gpl_controller
from src.modules.credit_request.rest_controllers.credit_request_controller import credit_request_controller
from src.modules.heart_beat.rest_controllers.heart_beat_controller import heart_beat_controller
from src.modules.user.graphql_controllers.user_controller import user_gpl_controller
from src.modules.user.rest_controllers.user_controller import user_controller
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.logging_provider import LoggingProvider
from src.sidecard.system.artifacts.path_provider import PathProvider
from src.sidecard.system.middlewares.error_handler_middleware import ErrorHandlerMiddleware
from src.sidecard.system.middlewares.logger_contextualizer_middleware import LoggerContextualizerMiddleware

# ---------------------------------------------------------------------------------------------------------------------
# ** info: building needed artifacts
# ---------------------------------------------------------------------------------------------------------------------

path_provider: PathProvider = PathProvider()
env_provider: EnvProvider = EnvProvider()  # type: ignore

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

routes: list[Route] = []

# ---------------------------------------------------------------------------------------------------------------------
# ** info: setting graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

routes.append(user_gpl_controller)
routes.append(account_gpl_controller)
routes.append(credit_request_gpl_controller)

# ---------------------------------------------------------------------------------------------------------------------
# ** info: mounting graphql based routers
# ---------------------------------------------------------------------------------------------------------------------

graphql_routers: list[BaseRoute] = [Mount(path=path_provider.build_posix_path("graphql"), routes=routes)]

# ---------------------------------------------------------------------------------------------------------------------
# ** info: initializing app metadata and documentation
# ---------------------------------------------------------------------------------------------------------------------

metadata: Dict[str, Any] = {
    "description": "a simple credit core backend implementation using fastapi as the main framework and a modular and hexagonal software architecture",
    "title": "Credit Core System",
    "version": "v1.2.0",
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
rest_router.include_router(router=account_controller)
rest_router.include_router(router=credit_request_controller)

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
