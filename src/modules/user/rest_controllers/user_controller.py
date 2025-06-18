# !/usr/bin/python3

from fastapi import Body
from fastapi import APIRouter
from fastapi import status
from modules.user.services.user_service import UserService  # type: ignore
from src.sidecard.system.artifacts.path_provider import PathProvider  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByEmailRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserCreationRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByDocumentRequestDto  # type: ignore

__all__: list[str] = ["user_controller"]
_path_provider: PathProvider = PathProvider()
user_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("user"), tags=["Users"])
_user_core: UserService = UserService()


@user_controller.post(
    description="allow to create a new user",
    summary="allow to create a new user",
    path=_path_provider.build_posix_path("create"),
    response_model=UserDataResponseDto,
    status_code=status.HTTP_200_OK,
)
async def create_user(user_creation_request: UserCreationRequestDto = Body(...)) -> UserDataResponseDto:
    user_creation_response: UserDataResponseDto = await _user_core.create_user_orchestator(user_creation_request)
    return user_creation_response


@user_controller.post(
    description="allow to get a user info by its email",
    summary="allow to get a user info by its email",
    path=_path_provider.build_posix_path("search-by-email"),
    response_model=UserDataResponseDto,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_email(user_by_email_request: UserByEmailRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_core.get_user_by_email_orchestator(user_by_email_request)
    return user_by_email_response


@user_controller.post(
    description="allow to get a user info by its id",
    summary="allow to get a user info by its id",
    path=_path_provider.build_posix_path("search-by-id"),
    response_model=UserDataResponseDto,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(user_by_id_request: UserByIdRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_core.get_user_by_id_orchestator(user_by_id_request)
    return user_by_email_response


@user_controller.post(
    description="allow to get a user info by its document",
    summary="allow to get a user info by its document",
    path=_path_provider.build_posix_path("search-by-document"),
    response_model=UserDataResponseDto,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_document(user_by_document_request: UserByDocumentRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_core.get_user_by_document_orchestator(user_by_document_request)
    return user_by_email_response
