from fastapi import APIRouter
from fastapi import Body
from fastapi import status as HttpStatus

from src.modules.user.rest_controllers_dtos.user_dtos import UserAuthenticationRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserAuthenticationResponseDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByDocumentRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByEmailRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserCreationRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto
from src.modules.user.services.user_service import UserService
from src.sidecard.system.artifacts.path_provider import PathProvider

__all__: list[str] = ["user_controller"]
_path_provider: PathProvider = PathProvider()
user_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("user"), tags=["Users"])
_user_service: UserService = UserService()


@user_controller.post(
    description="allow to create a new user",
    summary="allow to create a new user",
    path=_path_provider.build_posix_path("create"),
    response_model=UserDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def create_user(user_creation_request: UserCreationRequestDto = Body(...)) -> UserDataResponseDto:
    user_creation_response: UserDataResponseDto = await _user_service.create_user_orchestator(user_creation_request)
    return user_creation_response


@user_controller.post(
    description="allow to authenticate a user",
    summary="allow to authenticate a user",
    path=_path_provider.build_posix_path("authenticate"),
    response_model=UserAuthenticationResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def authenticate_user(user_authentication_request: UserAuthenticationRequestDto = Body(...)) -> UserAuthenticationResponseDto:
    user_by_email_response: UserAuthenticationResponseDto = await _user_service.authenticate_user_orchestator(user_authentication_request)
    return user_by_email_response


@user_controller.post(
    description="allow to get a user info by its email",
    summary="allow to get a user info by its email",
    path=_path_provider.build_posix_path("search-by-email"),
    response_model=UserDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def get_user_by_email(user_by_email_request: UserByEmailRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_service.get_user_by_email_orchestator(user_by_email_request)
    return user_by_email_response


@user_controller.post(
    description="allow to get a user info by its id",
    summary="allow to get a user info by its id",
    path=_path_provider.build_posix_path("search-by-id"),
    response_model=UserDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def get_user_by_id(user_by_id_request: UserByIdRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_service.get_user_by_id_orchestator(user_by_id_request)
    return user_by_email_response


@user_controller.post(
    description="allow to get a user info by its document",
    summary="allow to get a user info by its document",
    path=_path_provider.build_posix_path("search-by-document"),
    response_model=UserDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def get_user_by_document(user_by_document_request: UserByDocumentRequestDto = Body(...)) -> UserDataResponseDto:
    user_by_email_response: UserDataResponseDto = await _user_service.get_user_by_document_orchestator(user_by_document_request)
    return user_by_email_response
