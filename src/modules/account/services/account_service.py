import logging
from typing import Self
from typing import Union

from fastapi import HTTPException
from fastapi import status as HttpStatus
from sidecard.system.helpers.singleton_helper import Singleton

from src.modules.account.mappers.account_mappers import AccountMappers
from src.modules.account.mysql_entites.account_entity import AccountEntitie
from src.modules.account.mysql_repositories.account_repositorie import AccountRepositorie
from src.modules.account.rest_controllers_dtos.account_dtos import AccountByIdRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountByUserIdRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountCreationRequestDto
from src.modules.account.rest_controllers_dtos.account_dtos import AccountDataResponseDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto
from src.modules.user.services.user_service import UserService
from src.sidecard.system.artifacts.i8n_provider import I8nProvider

__all__: list[str] = ["AccountService"]


class AccountService(metaclass=Singleton):
    __slots__ = ["_account_repositorie", "_user_service", "_i8n"]

    def __init__(self: Self):
        self._account_repositorie: AccountRepositorie = AccountRepositorie()
        self._user_service: UserService = UserService()
        self._i8n: I8nProvider = I8nProvider(module="account")

    async def create_account_orchestator(self: Self, account_creation_request: AccountCreationRequestDto) -> AccountDataResponseDto:
        logging.debug("starting create_account_orchestator")
        user = await self._user_service.get_user_by_id_orchestator(UserByIdRequestDto(userId=account_creation_request.user_id))
        await self._user_service.check_if_user_is_valid_orchestator(user_id=user.id)
        new_account_data: AccountEntitie = self._create_new_account(account_creation_request=account_creation_request)
        response = AccountMappers.account_entitie_2_account_data_response_dto(account_entite=new_account_data)
        logging.debug("ending create_account_orchestator")
        return response

    async def get_account_by_filters_orchestator(self: Self, id: Union[int, None] = None, user_id: Union[int, None] = None) -> list[AccountDataResponseDto]:
        logging.debug("starting get_account_by_filters_orchestator")
        accounts_data: list[AccountEntitie] = self._account_repositorie.search_account_by_filters(id=id, user_id=user_id)
        response: list[AccountDataResponseDto] = list(
            map(lambda account_entite: AccountMappers.account_entitie_2_account_data_response_dto(account_entite).model_dump(by_alias=True), accounts_data)
        )  # type: ignore
        logging.debug("ending get_account_by_filters_orchestator")
        return response

    async def get_account_by_id_orchestator(self: Self, account_by_id_request: AccountByIdRequestDto) -> AccountDataResponseDto:
        logging.debug("starting get_account_by_id_orchestator")
        account_data: AccountEntitie = self._found_account_by_id_or_fail(search_id=account_by_id_request.id)
        response = AccountMappers.account_entitie_2_account_data_response_dto(account_entite=account_data)
        logging.debug("ending get_account_by_id_orchestator")
        return response

    async def get_accounts_by_user_id_orchestator(self: Self, account_by_user_id_request: AccountByUserIdRequestDto) -> list[AccountDataResponseDto]:
        logging.debug("starting get_accounts_by_user_id_orchestator")
        accounts_data: list[AccountEntitie] = self._found_accounts_by_user_id_or_fail(search_user_id=account_by_user_id_request.user_id)
        response: list[AccountDataResponseDto] = list(map(lambda account_entite: AccountMappers.account_entitie_2_account_data_response_dto(account_entite), accounts_data))
        logging.debug("ending get_accounts_by_user_id_orchestator")
        return response

    async def sum_to_account_amount_orchestator(self: Self, account_id: int, amount: float) -> AccountDataResponseDto:
        logging.debug("starting sum_to_account_amount_orchestator")
        account_data: AccountEntitie = self._found_account_by_id_or_fail(search_id=account_id)
        account_data.amount += amount
        updated_account: AccountEntitie = self._account_repositorie.update_account(updated_account=account_data)
        response = AccountMappers.account_entitie_2_account_data_response_dto(account_entite=updated_account)
        logging.debug("ending sum_to_account_amount_orchestator")
        return response

    def _create_new_account(self: Self, account_creation_request: AccountCreationRequestDto) -> AccountEntitie:
        logging.debug("creating new account")
        new_account: AccountEntitie = self._account_repositorie.create_account(user_id=account_creation_request.user_id)
        logging.debug("new account created")
        return new_account

    def _found_account_by_id_or_fail(self: Self, search_id: int) -> AccountEntitie:
        user_data_by_email: AccountEntitie = self._account_repositorie.search_account_by_id(id=search_id)
        if not user_data_by_email:
            logging.error("account not found by id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM001", id=search_id))
        return user_data_by_email

    def _found_accounts_by_user_id_or_fail(self: Self, search_user_id: int) -> list[AccountEntitie]:
        user_data_by_id: list[AccountEntitie] = self._account_repositorie.search_account_by_user_id(user_id=search_user_id)
        if not user_data_by_id:
            logging.error("account not found by user id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002", user_id=search_user_id))
        return user_data_by_id
