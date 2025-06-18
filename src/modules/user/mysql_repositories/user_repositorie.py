import logging
from typing import Any
from typing import Self
from stamina import retry
from sqlmodel import Session
from sqlmodel import select
from cachetools import TTLCache
from cachetools import cached
from modules.user.mysql_entites.user_entity import UserEntitie
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.uuid_provider import UuidProvider
from src.sidecard.system.artifacts.datetime_provider import DatetimeProvider
from src.sidecard.system.database_managers.mysql_manager import MySQLManager

__all__: list[str] = ["UserRepositorie"]
user_provider_cache: TTLCache = TTLCache(ttl=240, maxsize=20)


class UserRepositorie:
    def __init__(self: Self) -> None:
        self._env_provider: EnvProvider = EnvProvider()  # type: ignore
        self._uuid_provider: UuidProvider = UuidProvider()
        self._datetime_provider: DatetimeProvider = DatetimeProvider()
        self._session_manager: MySQLManager = MySQLManager(
            password=self._env_provider.database_password,
            database=self._env_provider.database_name,
            username=self._env_provider.database_user,
            host=self._env_provider.database_host,
            port=self._env_provider.database_port,
            drivername=r"mysql+pymysql",
            query={"charset": "utf8"},
        )

    def _clear_cache(self: Self) -> None:
        user_provider_cache.clear()

    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def create_user(self: Self, email: str, name: str, last_name: str, document: int) -> UserEntitie:
        logging.debug("creating new user with basic info")
        session: Session = self._session_manager.obtain_session()
        new_user: UserEntitie = UserEntitie(email=email, name=name, last_name=last_name, document=document)  # type: ignore
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        self._clear_cache()
        logging.debug("new user with basic info created")
        return new_user

    @cached(user_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_user_by_id(self: Self, id: int) -> UserEntitie:
        logging.debug(f"searching user by id {id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(UserEntitie).where(UserEntitie.id == id)
        query_result: UserEntitie = session.exec(statement=query).first()
        logging.debug("searching user by id ended")
        return query_result

    @cached(user_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_user_by_document(self: Self, document: int) -> UserEntitie:
        logging.debug(f"searching user by document {document}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(UserEntitie).where(UserEntitie.document == document)
        query_result: UserEntitie = session.exec(statement=query).first()
        logging.debug("searching user by document ended")
        return query_result

    @cached(user_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_user_by_email(self: Self, email: str) -> UserEntitie:
        logging.debug(f"searching user by email {email}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(UserEntitie).where(UserEntitie.email == email)
        query_result: UserEntitie = session.exec(statement=query).first()
        logging.debug("searching user by email ended")
        return query_result
