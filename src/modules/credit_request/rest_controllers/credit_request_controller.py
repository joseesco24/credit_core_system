from fastapi import APIRouter
from fastapi import Body
from fastapi import status as HttpStatus

from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByAccountIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByStatusRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByUserIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestCreationRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto
from src.modules.credit_request.services.credit_request_service import CreditRequestService
from src.sidecard.system.artifacts.path_provider import PathProvider

__all__: list[str] = ["credit_request_controller"]
_path_provider: PathProvider = PathProvider()
credit_request_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("credit-request"), tags=["Credit Request"])
_credit_request_service: CreditRequestService = CreditRequestService()


@credit_request_controller.post(
    description="allow to create a new credirt request",
    summary="allow to create a new credit request",
    path=_path_provider.build_posix_path("create"),
    response_model=CreditRequestDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def create_user(credit_request_creation_request: CreditRequestCreationRequestDto = Body(...)) -> CreditRequestDataResponseDto:
    credit_request_creation_response: CreditRequestDataResponseDto = await _credit_request_service.create_credit_request_orchestator(credit_request_creation_request)
    return credit_request_creation_response


@credit_request_controller.post(
    description="search credit request by id",
    summary="search credit request by id",
    path=_path_provider.build_posix_path("search-by-id"),
    response_model=CreditRequestDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def search_by_id(credit_request_by_id_request: CreditRequestByIdRequestDto = Body(...)) -> CreditRequestDataResponseDto:
    credit_request_data_response: CreditRequestDataResponseDto = await _credit_request_service.get_credit_request_by_id_orchestator(credit_request_by_id_request)
    return credit_request_data_response


@credit_request_controller.post(
    description="search credit request by user id",
    summary="search credit request by user id",
    path=_path_provider.build_posix_path("search-by-user-id"),
    response_model=list[CreditRequestDataResponseDto],
    status_code=HttpStatus.HTTP_200_OK,
)
async def search_by_user_id(credit_request_by_user_id_request: CreditRequestByUserIdRequestDto = Body(...)) -> list[CreditRequestDataResponseDto]:
    credit_request_data_response: list[CreditRequestDataResponseDto] = await _credit_request_service.get_credit_request_by_user_id_orchestator(credit_request_by_user_id_request)
    return credit_request_data_response


@credit_request_controller.post(
    description="search credit request by account id",
    summary="search credit request by account id",
    path=_path_provider.build_posix_path("search-by-account-id"),
    response_model=list[CreditRequestDataResponseDto],
    status_code=HttpStatus.HTTP_200_OK,
)
async def search_by_account_id(credit_request_by_account_id_request: CreditRequestByAccountIdRequestDto = Body(...)) -> list[CreditRequestDataResponseDto]:
    credit_request_data_response: list[CreditRequestDataResponseDto] = await _credit_request_service.get_credit_request_by_account_id_orchestator(
        credit_request_by_account_id_request
    )
    return credit_request_data_response


@credit_request_controller.post(
    description="search credit request by status",
    summary="search credit request by status",
    path=_path_provider.build_posix_path("search-by-status"),
    response_model=list[CreditRequestDataResponseDto],
    status_code=HttpStatus.HTTP_200_OK,
)
async def search_by_status(credit_request_by_status_request: CreditRequestByStatusRequestDto = Body(...)) -> list[CreditRequestDataResponseDto]:
    credit_request_data_response: list[CreditRequestDataResponseDto] = await _credit_request_service.get_credit_request_by_status_orchestator(credit_request_by_status_request)
    return credit_request_data_response
