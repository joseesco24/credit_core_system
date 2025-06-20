import logging
from typing import Any
from typing import Self
from typing import Union

from cachetools import TTLCache
from cachetools import cached
from sqlmodel import Session
from sqlmodel import select
from stamina import retry

from src.modules.credit_request.mysql_entites.credit_request_entity import CreditRequestEntitie
from src.sidecard.system.artifacts.datetime_provider import DatetimeProvider
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.uuid_provider import UuidProvider
from src.sidecard.system.database_managers.mysql_manager import MySQLManager

__all__: list[str] = ["CreditRequestRepositorie"]
credit_request_provider_cache: TTLCache = TTLCache(ttl=240, maxsize=20)


class CreditRequestRepositorie:
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
        credit_request_provider_cache.clear()

    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def create_credit_request(self: Self, user_id: int, account_id: int, amount: float) -> CreditRequestEntitie:
        logging.debug("creating new credit request with basic info")
        session: Session = self._session_manager.obtain_session()
        new_credit_request: CreditRequestEntitie = CreditRequestEntitie(user_id=user_id, account_id=account_id, status=0, amount=amount)  # type: ignore
        session.add(new_credit_request)
        session.commit()
        session.refresh(new_credit_request)
        self._clear_cache()
        logging.debug("new anew credit request with basic info created")
        return new_credit_request

    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def update_credit_request(self: Self, updated_credit_request: CreditRequestEntitie) -> CreditRequestEntitie:
        logging.debug("updating credit request")
        session: Session = self._session_manager.obtain_session()
        session.add(updated_credit_request)
        session.commit()
        session.refresh(updated_credit_request)
        self._clear_cache()
        logging.debug("credit request updated")
        return updated_credit_request

    @cached(credit_request_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_credit_request_by_filters(
        self: Self,
        id: Union[int, None] = None,
        account_id: Union[int, None] = None,
        user_id: Union[int, None] = None,
        score: Union[int, None] = None,
        status: Union[int, None] = None,
    ) -> list[CreditRequestEntitie]:
        logging.debug("searching credit request by filters")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(CreditRequestEntitie)
        if id is not None:
            query = query.where(CreditRequestEntitie.id == id)
        if account_id is not None:
            query = query.where(CreditRequestEntitie.account_id == account_id)
        if user_id is not None:
            query = query.where(CreditRequestEntitie.user_id == user_id)
        if score is not None:
            query = query.where(CreditRequestEntitie.score == score)
        if status is not None:
            query = query.where(CreditRequestEntitie.status == status)
        query_result: list[CreditRequestEntitie] = session.exec(statement=query).all()
        logging.debug("searching credit request by filters ended")
        return query_result

    @cached(credit_request_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_credit_request_by_id(self: Self, id: int) -> CreditRequestEntitie:
        logging.debug(f"searching credit request by id {id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(CreditRequestEntitie).where(CreditRequestEntitie.id == id)
        query_result: CreditRequestEntitie = session.exec(statement=query).first()
        logging.debug("searching credit request by id ended")
        return query_result

    @cached(credit_request_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_credit_request_by_status(self: Self, status: int) -> list[CreditRequestEntitie]:
        logging.debug(f"searching credit request by user status {status}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(CreditRequestEntitie).where(CreditRequestEntitie.status == status)
        query_result: list[CreditRequestEntitie] = session.exec(statement=query).all()
        logging.debug("searching credit request by status ended")
        return query_result

    @cached(credit_request_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_credit_request_by_account_id(self: Self, account_id: int) -> list[CreditRequestEntitie]:
        logging.debug(f"searching credit request by account id {account_id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(CreditRequestEntitie).where(CreditRequestEntitie.account_id == account_id)
        query_result: list[CreditRequestEntitie] = session.exec(statement=query).all()
        logging.debug("searching credit request by account id ended")
        return query_result

    @cached(credit_request_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_credit_request_by_user_id(self: Self, user_id: int) -> list[CreditRequestEntitie]:
        logging.debug(f"searching credit request by user id {user_id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(CreditRequestEntitie).where(CreditRequestEntitie.user_id == user_id)
        query_result: list[CreditRequestEntitie] = session.exec(statement=query).all()
        logging.debug("searching credit request by user id ended")
        return query_result
