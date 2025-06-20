from fastapi import APIRouter
from fastapi import Body
from fastapi import status as HttpStatus

from src.modules.account.rest_controllers_dtos.account_dtos import AccountByIdRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountByUserIdRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountCreationRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountDataResponseDto
from src.modules.account.services.account_service import AccountService
from src.sidecard.system.artifacts.path_provider import PathProvider

__all__: list[str] = ["account_controller"]
_path_provider: PathProvider = PathProvider()
account_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("account"), tags=["Accounts"])
_account_service: AccountService = AccountService()


@account_controller.post(
    description="allow to create a new account",
    summary="allow to create a new account",
    path=_path_provider.build_posix_path("create"),
    response_model=AccountDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def create_account(account_creation_request: AccountCreationRequestDto = Body(...)) -> AccountDataResponseDto:
    account_creation_response: AccountDataResponseDto = await _account_service.create_account_orchestator(account_creation_request)
    return account_creation_response


@account_controller.post(
    description="allow to get a account info by its id",
    summary="allow to get a account info by its id",
    path=_path_provider.build_posix_path("search-by-id"),
    response_model=AccountDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def get_account_by_id(account_by_id_request: AccountByIdRequestDto = Body(...)) -> AccountDataResponseDto:
    account_by_id_response: AccountDataResponseDto = await _account_service.get_account_by_id_orchestator(account_by_id_request)
    return account_by_id_response


@account_controller.post(
    description="allow to get accounts info by user id",
    summary="allow to get accounts info by user id",
    path=_path_provider.build_posix_path("search-by-user-id"),
    response_model=list[AccountDataResponseDto],
    status_code=HttpStatus.HTTP_200_OK,
)
async def get_account_by_document(account_by_user_id_request: AccountByUserIdRequestDto = Body(...)) -> list[AccountDataResponseDto]:
    accounts_by_user_id_response: list[AccountDataResponseDto] = await _account_service.get_accounts_by_user_id_orchestator(account_by_user_id_request)
    return accounts_by_user_id_response
