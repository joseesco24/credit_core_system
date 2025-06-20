import logging
from typing import Self
from typing import Union

from fastapi import HTTPException
from fastapi import status as HttpStatus
from sidecard.system.helpers.singleton_helper import Singleton

from src.modules.user.mappers.user_mappers import UserMappers
from src.modules.user.mysql_entites.user_entity import UserEntitie
from src.modules.user.mysql_repositories.user_repositorie import UserRepositorie
from src.modules.user.rest_clients.user_authentication_client import UserAuthenticationClient
from src.modules.user.rest_controllers_dtos.user_dtos import UserAuthenticationRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserAuthenticationResponseDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByDocumentRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByEmailRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserCreationRequestDto
from src.modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto
from src.sidecard.system.artifacts.i8n_provider import I8nProvider

__all__: list[str] = ["UserService"]


class UserService(metaclass=Singleton):
    __slots__ = ["_user_authentication_client", "_user_repositorie", "_i8n"]

    def __init__(self: Self):
        self._user_authentication_client: UserAuthenticationClient = UserAuthenticationClient()
        self._user_repositorie: UserRepositorie = UserRepositorie()
        self._i8n: I8nProvider = I8nProvider(module="user")

    async def create_user_orchestator(self: Self, user_creation_request: UserCreationRequestDto) -> UserDataResponseDto:
        logging.debug("starting create_user_orchestator")
        self._check_if_user_already_exists(user_creation_request=user_creation_request)
        new_user_data: UserEntitie = self._create_new_user(user_creation_request=user_creation_request)
        response = UserMappers.user_entitie_2_user_data_response_dto(user_entite=new_user_data)
        logging.debug("ending create_user_orchestator")
        return response

    async def get_user_by_filters_orchestator(
        self: Self,
        id: Union[int, None] = None,
        document: Union[int, None] = None,
        email: Union[str, None] = None,
        name: Union[str, None] = None,
        last_name: Union[str, None] = None,
        is_validated: Union[bool, None] = None,
    ) -> list[UserDataResponseDto]:
        logging.debug("starting get_user_by_filters_orchestator")
        users_data: list[UserEntitie] = self._user_repositorie.search_user_by_filters(
            id=id, document=document, email=email, name=name, last_name=last_name, is_validated=is_validated
        )
        response: list[UserDataResponseDto] = list(map(lambda user_entite: UserMappers.user_entitie_2_user_data_response_dto(user_entite).model_dump(by_alias=True), users_data))  # type: ignore
        logging.debug("ending get_user_by_filters_orchestator")
        return response

    async def authenticate_user_orchestator(self: Self, user_authentication_request: UserAuthenticationRequestDto) -> UserAuthenticationResponseDto:
        logging.debug("starting authenticate_user_orchestator")
        user_data: UserEntitie = self._found_user_by_id_or_fail(search_id=user_authentication_request.id)
        if user_data:
            logging.info("user is already valid")
            response = UserMappers.user_entitie_2_user_authentication_response_dto(user_entite=user_data)
            return response
        is_valid: bool = await self._user_authentication_client.obtain_user_autentication()
        user_data.is_validated = is_valid
        updated_user_data: UserEntitie = self._user_repositorie.update_user(updated_user=user_data)
        response = UserMappers.user_entitie_2_user_authentication_response_dto(user_entite=updated_user_data)
        logging.debug("ending authenticate_user_orchestator")
        return response

    async def check_if_user_is_valid_orchestator(self: Self, user_id: int) -> UserEntitie:
        logging.debug("starting check_if_user_is_valid_orchestator")
        user_entite: UserEntitie = self._found_user_by_id_or_fail(search_id=user_id)
        if not user_entite.is_validated:
            logging.error("user is not validated")
            raise HTTPException(status_code=HttpStatus.HTTP_403_FORBIDDEN, detail=self._i8n.message(message_key="EM006", email=user_entite.email))
        logging.debug("ending check_if_user_is_valid_orchestator")
        return user_entite

    async def get_user_by_email_orchestator(self: Self, user_by_email_request: UserByEmailRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_email_orchestator")
        user_data: UserEntitie = self._found_user_by_email_or_fail(search_email=user_by_email_request.email)
        response = UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)
        logging.debug("ending get_user_by_email_orchestator")
        return response

    async def get_user_by_id_orchestator(self: Self, user_by_id_request: UserByIdRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_id_orchestator")
        user_data: UserEntitie = self._found_user_by_id_or_fail(search_id=user_by_id_request.id)
        response = UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)
        logging.debug("ending get_user_by_id_orchestator")
        return response

    async def get_user_by_document_orchestator(self: Self, user_by_document_request: UserByDocumentRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_document_orchestator")
        user_data: UserEntitie = self._found_user_by_document_or_fail(search_document=user_by_document_request.document)
        response = UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)
        logging.debug("ending get_user_by_document_orchestator")
        return response

    def _check_if_user_already_exists(self: Self, user_creation_request: UserCreationRequestDto) -> None:
        logging.debug("checking if user exists")
        user_data_by_email: UserEntitie = self._user_repositorie.search_user_by_email(email=user_creation_request.email)
        if user_data_by_email:
            logging.error("user already exists")
            raise HTTPException(status_code=HttpStatus.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM001", email=user_creation_request.email))
        user_data_by_document: UserEntitie = self._user_repositorie.search_user_by_document(document=user_creation_request.document)
        if user_data_by_document:
            logging.error("user already exists")
            raise HTTPException(status_code=HttpStatus.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM003", docuement=user_creation_request.document))
        logging.debug("user does not exist")

    def _create_new_user(self: Self, user_creation_request: UserCreationRequestDto) -> UserEntitie:
        logging.debug("creating new user")
        new_user: UserEntitie = self._user_repositorie.create_user(
            email=user_creation_request.email, name=user_creation_request.name, last_name=user_creation_request.last_name, document=user_creation_request.document
        )
        logging.debug("new user created")
        return new_user

    def _found_user_by_email_or_fail(self: Self, search_email: str) -> UserEntitie:
        user_data_by_email: UserEntitie = self._user_repositorie.search_user_by_email(email=search_email)
        if not user_data_by_email:
            logging.error("user not found by email")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002", email=search_email))
        return user_data_by_email

    def _found_user_by_id_or_fail(self: Self, search_id: int) -> UserEntitie:
        user_data_by_id: UserEntitie = self._user_repositorie.search_user_by_id(id=search_id)
        if not user_data_by_id:
            logging.error("user not found by id")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM005", id=search_id))
        return user_data_by_id

    def _found_user_by_document_or_fail(self: Self, search_document: int) -> UserEntitie:
        user_data_by_document: UserEntitie = self._user_repositorie.search_user_by_document(document=search_document)
        if not user_data_by_document:
            logging.error("user not found by document")
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM004", document=search_document))
        return user_data_by_document
