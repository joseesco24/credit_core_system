from fastapi import APIRouter
from fastapi import Body
from fastapi import status as HttpStatus

from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_transition_dtos import CreditRequestMakeTransitionRequestDto
from src.modules.credit_request.services.credit_request_transition_service import CreditRequestTransitionService
from src.sidecard.system.artifacts.path_provider import PathProvider

__all__: list[str] = ["credit_request_transition_controller"]
_path_provider: PathProvider = PathProvider()
credit_request_transition_controller: APIRouter = APIRouter(prefix=_path_provider.build_posix_path("credit-request-transition"), tags=["Credit Request Transition"])
_credit_request_service: CreditRequestTransitionService = CreditRequestTransitionService()


@credit_request_transition_controller.post(
    description="allow to change the status of a credit request",
    summary="allow to change the status of a credit request",
    path=_path_provider.build_posix_path("make-transition"),
    response_model=CreditRequestDataResponseDto,
    status_code=HttpStatus.HTTP_200_OK,
)
async def create_user(credit_request_make_transition_request: CreditRequestMakeTransitionRequestDto = Body(...)) -> CreditRequestDataResponseDto:
    credit_request_creation_response: CreditRequestDataResponseDto = await _credit_request_service.credit_request_make_transition_orchestator(
        credit_request_make_transition_request
    )
    return credit_request_creation_response
