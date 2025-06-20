import logging
from typing import Self
from typing import Union

from fastapi import HTTPException
from fastapi import status as HttpStatus
from sidecard.system.helpers.singleton_helper import Singleton

from src.modules.account.mysql_entites.account_entity import AccountEntitie
from src.modules.account.services.account_service import AccountService
from src.modules.credit_request.mappers.credit_request_mappers import CreditRequestMappers
from src.modules.credit_request.mysql_entites.credit_request_entity import CreditRequestEntitie
from src.modules.credit_request.mysql_repositories.credit_request_repositorie import CreditRequestRepositorie
from src.modules.credit_request.rest_clients.credit_request_score_client import CreditRequestScoreClient
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByAccountIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByStatusRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByUserIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestCreationRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto
from src.modules.user.mysql_entites.user_entity import UserEntitie
from src.modules.user.services.user_service import UserService
from src.sidecard.system.artifacts.i8n_provider import I8nProvider

__all__: list[str] = ["CreditRequestService"]


class CreditRequestService(metaclass=Singleton):
    __slots__ = ["_credit_request_score_client", "_credit_request_repositorie", "_user_service", "_account_service", "_i8n"]

    def __init__(self: Self):
        self._credit_request_score_client: CreditRequestScoreClient = CreditRequestScoreClient()
        self._credit_request_repositorie: CreditRequestRepositorie = CreditRequestRepositorie()
        self._user_service: UserService = UserService()
        self._account_service: AccountService = AccountService()
        self._i8n: I8nProvider = I8nProvider(module="credit_request")

    async def create_credit_request_orchestator(self: Self, credit_request_creation_request: CreditRequestCreationRequestDto) -> CreditRequestDataResponseDto:
        logging.debug("starting create_credit_request_orchestator")
        user: UserEntitie = self._user_service._found_user_by_id_or_fail(search_id=credit_request_creation_request.user_id)
        await self._user_service.check_if_user_is_valid_orchestator(user_id=user.id)
        account: AccountEntitie = self._account_service._found_account_by_id_or_fail(search_id=credit_request_creation_request.account_id)
        self._check_if_acount_belongs_to_user(user=user, account=account)
        new_credit_request_data: CreditRequestEntitie = self._create_new_credit_request(credit_request_creation_request=credit_request_creation_request)
        response = CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite=new_credit_request_data)
        logging.debug("ending create_credit_request_orchestator")
        return response

    async def get_credit_request_by_filters_orchestator(
        self: Self,
        id: Union[int, None] = None,
        account_id: Union[int, None] = None,
        user_id: Union[int, None] = None,
        score: Union[int, None] = None,
        status: Union[int, None] = None,
    ) -> list[CreditRequestDataResponseDto]:
        logging.debug("starting get_credit_request_by_filters_orchestator")
        credit_requests_data: list[CreditRequestEntitie] = self._credit_request_repositorie.search_credit_request_by_filters(
            id=id, account_id=account_id, user_id=user_id, score=score, status=status
        )
        response: list[CreditRequestDataResponseDto] = list(
            map(
                lambda credit_requests_entite: CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_requests_entite).model_dump(by_alias=True),
                credit_requests_data,
            )
        )  # type: ignore
        logging.debug("ending get_credit_request_by_filters_orchestator")
        return response

    async def get_credit_request_by_id_orchestator(self: Self, credit_request_by_id_request: CreditRequestByIdRequestDto) -> CreditRequestDataResponseDto:
        logging.debug("starting get_credit_request_by_id_orchestator")
        credit_request_data: CreditRequestEntitie = self._found_credit_request_by_id_or_fail(search_id=credit_request_by_id_request.id)
        response = CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite=credit_request_data)
        logging.debug("ending get_credit_request_by_id_orchestator")
        return response

    async def get_credit_request_by_user_id_orchestator(self: Self, credit_request_by_user_id_request: CreditRequestByUserIdRequestDto) -> list[CreditRequestDataResponseDto]:
        logging.debug("starting get_credit_request_by_user_id_orchestator")
        credit_requests_data: list[CreditRequestEntitie] = self._found_credit_request_by_user_id_or_fail(search_user_id=credit_request_by_user_id_request.user_id)
        response: list[CreditRequestDataResponseDto] = list(
            map(
                lambda credit_request_entite: CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite).model_dump(by_alias=True),
                credit_requests_data,
            )
        )  # type: ignore
        logging.debug("ending get_credit_request_by_user_id_orchestator")
        return response

    async def get_credit_request_by_account_id_orchestator(
        self: Self, credit_request_by_account_id_request: CreditRequestByAccountIdRequestDto
    ) -> list[CreditRequestDataResponseDto]:
        logging.debug("starting get_credit_request_by_account_id_orchestator")
        credit_requests_data: list[CreditRequestEntitie] = self._found_credit_request_by_account_id_or_fail(search_account_id=credit_request_by_account_id_request.account_id)
        response: list[CreditRequestDataResponseDto] = list(
            map(
                lambda credit_request_entite: CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite).model_dump(by_alias=True),
                credit_requests_data,
            )
        )  # type: ignore
        logging.debug("ending get_credit_request_by_account_id_orchestator")
        return response

    async def get_credit_request_by_status_orchestator(self: Self, credit_request_by_status_request: CreditRequestByStatusRequestDto) -> list[CreditRequestDataResponseDto]:
        logging.debug("starting get_credit_request_by_status_orchestator")
        credit_requests_data: list[CreditRequestEntitie] = self._found_credit_request_by_status_or_fail(search_status=credit_request_by_status_request.status)
        response: list[CreditRequestDataResponseDto] = list(
            map(
                lambda credit_request_entite: CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite).model_dump(by_alias=True),
                credit_requests_data,
            )
        )  # type: ignore
        logging.debug("ending get_credit_request_by_status_orchestator")
        return response

    async def set_credit_request_score_orchestator(self: Self, id: int, score: Union[int, None]) -> CreditRequestDataResponseDto:
        logging.debug("starting set_credit_request_score_orchestator")
        credit_request_data: CreditRequestEntitie = self._found_credit_request_by_id_or_fail(search_id=id)
        credit_request_data.score = score
        updated_credit_request: CreditRequestEntitie = self._credit_request_repositorie.update_credit_request(updated_credit_request=credit_request_data)
        response = CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite=updated_credit_request)
        logging.debug("ending set_credit_request_score_orchestator")
        return response

    async def set_credit_request_status_orchestator(self: Self, id: int, status: int) -> CreditRequestDataResponseDto:
        logging.debug("starting set_credit_request_status_orchestator")
        credit_request_data: CreditRequestEntitie = self._found_credit_request_by_id_or_fail(search_id=id)
        credit_request_data.status = status
        updated_credit_request: CreditRequestEntitie = self._credit_request_repositorie.update_credit_request(updated_credit_request=credit_request_data)
        response = CreditRequestMappers.credit_request_entitie_2_credit_request_response_dto(credit_request_entite=updated_credit_request)
        logging.debug("ending set_credit_request_status_orchestator")
        return response

    def _create_new_credit_request(self: Self, credit_request_creation_request: CreditRequestCreationRequestDto) -> CreditRequestEntitie:
        logging.debug("creating new credit request")
        new_credit_request: CreditRequestEntitie = self._credit_request_repositorie.create_credit_request(
            user_id=credit_request_creation_request.user_id, account_id=credit_request_creation_request.account_id, amount=credit_request_creation_request.amount
        )  # type: ignore
        logging.debug("new credit request created")
        return new_credit_request

    def _check_if_acount_belongs_to_user(self: Self, user: UserEntitie, account: AccountEntitie) -> None:
        if user.id != account.user_id:
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM001", user_id=user.id, account_id=account.id))

    def _found_credit_request_by_id_or_fail(self: Self, search_id: int) -> CreditRequestEntitie:
        credit_request_data_by_id: CreditRequestEntitie = self._credit_request_repositorie.search_credit_request_by_id(id=search_id)
        if not credit_request_data_by_id:
            logging.error("credit request not found by id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002", id=search_id))
        return credit_request_data_by_id

    def _found_credit_request_by_user_id_or_fail(self: Self, search_user_id: int) -> list[CreditRequestEntitie]:
        credit_request_data_by_user_id: list[CreditRequestEntitie] = self._credit_request_repositorie.search_credit_request_by_user_id(user_id=search_user_id)
        if not credit_request_data_by_user_id:
            logging.error("credit request not found by user id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM003", user_id=search_user_id))
        return credit_request_data_by_user_id

    def _found_credit_request_by_account_id_or_fail(self: Self, search_account_id: int) -> list[CreditRequestEntitie]:
        credit_request_data_by_account_id: list[CreditRequestEntitie] = self._credit_request_repositorie.search_credit_request_by_account_id(account_id=search_account_id)
        if not credit_request_data_by_account_id:
            logging.error("credit request not found by account id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM004", account_id=search_account_id))
        return credit_request_data_by_account_id

    def _found_credit_request_by_status_or_fail(self: Self, search_status: int) -> list[CreditRequestEntitie]:
        credit_request_data_by_status: list[CreditRequestEntitie] = self._credit_request_repositorie.search_credit_request_by_status(status=search_status)
        if not credit_request_data_by_status:
            logging.error("credit request not found by status")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM005", status=search_status))
        return credit_request_data_by_status
