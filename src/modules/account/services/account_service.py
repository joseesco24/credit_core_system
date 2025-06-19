import logging
from typing import List
from typing import Self
from typing import Union
from fastapi import HTTPException
from fastapi import status
from modules.user.services.user_service import UserService
from modules.account.mappers.account_mappers import AccountMappers
from sidecard.system.helpers.singleton_helper import Singleton
from src.sidecard.system.artifacts.i8n_provider import I8nProvider
from modules.account.mysql_entites.account_entity import AccountEntitie
from modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto
from modules.account.rest_controllers_dtos.account_dtos import AccountByIdRequestDto
from modules.account.rest_controllers_dtos.account_dtos import AccountDataResponseDto
from modules.account.rest_controllers_dtos.account_dtos import AccountByUserIdRequestDto
from modules.account.rest_controllers_dtos.account_dtos import AccountCreationRequestDto
from modules.account.mysql_repositories.account_repositorie import AccountRepositorie

__all__: list[str] = ["AccountService"]


class AccountService(metaclass=Singleton):
    __slots__ = ["_account_repositorie", "_user_service", "_i8n"]

    def __init__(self: Self):
        self._account_repositorie: AccountRepositorie = AccountRepositorie()
        self._user_service: UserService = UserService()
        self._i8n: I8nProvider = I8nProvider(module="account")

    async def create_account_orchestator(self: Self, account_creation_request: AccountCreationRequestDto) -> AccountDataResponseDto:
        logging.debug("starting create_account_orchestator")
        await self._user_service.get_user_by_id_orchestator(UserByIdRequestDto(userId=account_creation_request.user_id))
        new_account_data: AccountEntitie = self._create_new_account(account_creation_request=account_creation_request)
        logging.debug("ending create_account_orchestator")
        return AccountMappers.account_entitie_2_account_data_response_dto(account_entite=new_account_data)

    async def get_account_by_filters_orchestator(self: Self, id: Union[int, None] = None, user_id: Union[int, None] = None) -> List[UserDataResponseDto]:
        logging.debug("starting get_account_by_filters_orchestator")
        accounts_data: List[AccountEntitie] = self._account_repositorie.search_account_by_filters(id=id, user_id=user_id)
        logging.debug("ending get_account_by_filters_orchestator")
        return list(map(lambda account_entite: AccountMappers.account_entitie_2_account_data_response_dto(account_entite).model_dump(by_alias=True), accounts_data))  # type: ignore

    async def get_account_by_id_orchestator(self: Self, account_by_id_request: AccountByIdRequestDto) -> AccountDataResponseDto:
        logging.debug("starting get_account_by_id_orchestator")
        account_data: AccountEntitie = self._found_account_by_id_or_fail(id=account_by_id_request.id)
        logging.debug("ending get_account_by_id_orchestator")
        return AccountMappers.account_entitie_2_account_data_response_dto(account_entite=account_data)

    async def get_accounts_by_user_id_orchestator(self: Self, account_by_user_id_request: AccountByUserIdRequestDto) -> List[AccountDataResponseDto]:
        logging.debug("starting get_accounts_by_user_id_orchestator")
        accounts_data: List[AccountEntitie] = self._found_accounts_by_user_id_or_fail(user_id=account_by_user_id_request.user_id)
        logging.debug("ending get_accounts_by_user_id_orchestator")
        return list(map(lambda account_entite: AccountMappers.account_entitie_2_account_data_response_dto(account_entite), accounts_data))  # type: ignore

    async def sum_to_account_amount_orchestator(self: Self, account_id: int, amount: float) -> AccountDataResponseDto:
        logging.debug("starting sum_to_account_amount_orchestator")
        account_data: AccountEntitie = self._found_account_by_id_or_fail(id=account_id)
        account_data.amount += amount
        updated_account: AccountEntitie = self._account_repositorie.update_account(updated_account=account_data)
        logging.debug("ending sum_to_account_amount_orchestator")
        return AccountMappers.account_entitie_2_account_data_response_dto(account_entite=updated_account)

    def _create_new_account(self: Self, account_creation_request: AccountCreationRequestDto) -> AccountEntitie:
        logging.debug("creating new account")
        new_account: AccountEntitie = self._account_repositorie.create_account(user_id=account_creation_request.user_id)
        logging.debug("new account created")
        return new_account

    def _found_account_by_id_or_fail(self: Self, id: int) -> AccountEntitie:
        user_data_by_email: AccountEntitie = self._account_repositorie.search_account_by_id(id=id)
        if not user_data_by_email:
            logging.error("account not found by id")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM001", id=id))
        return user_data_by_email

    def _found_accounts_by_user_id_or_fail(self: Self, user_id: int) -> List[AccountEntitie]:
        user_data_by_id: List[AccountEntitie] = self._account_repositorie.search_account_by_user_id(user_id=user_id)
        if not user_data_by_id:
            logging.error("account not found by user id")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002", user_id=user_id))
        return user_data_by_id
