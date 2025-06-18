# !/usr/bin/python3

import logging
from typing import Self
from fastapi import HTTPException
from fastapi import status
from modules.user.mappers.user_mappers import UserMappers  # type: ignore
from modules.user.mysql_entites.user_entity import UserEntitie  # type: ignore
from src.sidecard.system.artifacts.i8n_provider import I8nProvider  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByIdRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserDataResponseDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByEmailRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserCreationRequestDto  # type: ignore
from modules.user.rest_controllers_dtos.user_dtos import UserByDocumentRequestDto  # type: ignore
from modules.user.mysql_repositories.user_repositorie import UserRepositorie  # type: ignore

__all__: list[str] = ["UserService"]


class UserService:
    __slots__ = ["_user_repositorie", "_i8n"]

    def __init__(self: Self):
        self._user_repositorie: UserRepositorie = UserRepositorie()
        self._i8n: I8nProvider = I8nProvider(module="user")

    async def create_user_orchestator(self: Self, user_creation_request: UserCreationRequestDto) -> UserDataResponseDto:
        logging.debug("starting create_user_orchestator")
        self._check_if_user_already_exists(user_creation_request=user_creation_request)
        new_user_data: UserEntitie = self._create_new_user(user_creation_request=user_creation_request)
        logging.debug("ending create_user_orchestator")
        return UserMappers.user_entitie_2_user_data_response_dto(user_entite=new_user_data)

    async def get_user_by_email_orchestator(self: Self, user_by_email_request: UserByEmailRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_email_orchestator")
        user_data: UserEntitie = self._found_user_by_email_or_fail(search_email=user_by_email_request.email)
        logging.debug("ending get_user_by_email_orchestator")
        return UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)

    async def get_user_by_id_orchestator(self: Self, user_by_id_request: UserByIdRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_id_orchestator")
        user_data: UserEntitie = self._found_user_by_id_or_fail(search_id=user_by_id_request.id)
        logging.debug("ending get_user_by_id_orchestator")
        return UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)

    async def get_user_by_document_orchestator(self: Self, user_by_document_request: UserByDocumentRequestDto) -> UserDataResponseDto:
        logging.debug("starting get_user_by_document_orchestator")
        user_data: UserEntitie = self._found_user_by_document_or_fail(search_document=user_by_document_request.document)
        logging.debug("ending get_user_by_document_orchestator")
        return UserMappers.user_entitie_2_user_data_response_dto(user_entite=user_data)

    def _check_if_user_already_exists(self: Self, user_creation_request: UserCreationRequestDto) -> None:
        logging.debug("checking if user exists")
        user_data_by_email: UserEntitie = self._user_repositorie.search_user_by_email(email=user_creation_request.email)
        if user_data_by_email:
            logging.error("user already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM001", email=user_creation_request.email))
        user_data_by_document: UserEntitie = self._user_repositorie.search_user_by_document(document=user_creation_request.document)
        if user_data_by_document:
            logging.error("user already exists")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM003", docuement=user_creation_request.document))
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002", email=search_email))
        return user_data_by_email

    def _found_user_by_id_or_fail(self: Self, search_id: int) -> UserEntitie:
        user_data_by_id: UserEntitie = self._user_repositorie.search_user_by_id(id=search_id)
        if not user_data_by_id:
            logging.error("user not found by id")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM005", id=search_id))
        return user_data_by_id

    def _found_user_by_document_or_fail(self: Self, search_document: int) -> UserEntitie:
        user_data_by_document: UserEntitie = self._user_repositorie.search_user_by_document(document=search_document)
        if not user_data_by_document:
            logging.error("user not found by document")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM004", document=search_document))
        return user_data_by_document
