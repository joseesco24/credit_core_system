import logging
from typing import Any
from typing import Self
from typing import Union

from cachetools import TTLCache
from cachetools import cached
from sqlmodel import Session
from sqlmodel import select
from stamina import retry

from src.modules.account.mysql_entites.account_entity import AccountEntitie
from src.sidecard.system.artifacts.datetime_provider import DatetimeProvider
from src.sidecard.system.artifacts.env_provider import EnvProvider
from src.sidecard.system.artifacts.uuid_provider import UuidProvider
from src.sidecard.system.database_managers.mysql_manager import MySQLManager

__all__: list[str] = ["AccountRepositorie"]
account_provider_cache: TTLCache = TTLCache(ttl=240, maxsize=20)


class AccountRepositorie:
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
        account_provider_cache.clear()

    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def create_account(self: Self, user_id: int) -> AccountEntitie:
        logging.debug("creating new account with basic info")
        session: Session = self._session_manager.obtain_session()
        new_account: AccountEntitie = AccountEntitie(user_id=user_id, amount=0)  # type: ignore
        session.add(new_account)
        session.commit()
        session.refresh(new_account)
        self._clear_cache()
        logging.debug("new account with basic info created")
        return new_account

    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def update_account(self: Self, updated_account: AccountEntitie) -> AccountEntitie:
        logging.debug("updating account")
        session: Session = self._session_manager.obtain_session()
        session.add(updated_account)
        session.commit()
        session.refresh(updated_account)
        self._clear_cache()
        logging.debug("account updated")
        return updated_account

    @cached(account_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_account_by_filters(self: Self, id: Union[int, None] = None, user_id: Union[int, None] = None) -> list[AccountEntitie]:
        logging.debug("searching account by filters")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(AccountEntitie)
        if id is not None:
            query = query.where(AccountEntitie.id == id)
        if user_id is not None:
            query = query.where(AccountEntitie.user_id == user_id)
        query_result: list[AccountEntitie] = session.exec(statement=query).all()
        logging.debug("searching account by filters ended")
        return query_result

    @cached(account_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_account_by_id(self: Self, id: int) -> AccountEntitie:
        logging.debug(f"searching account by id {id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(AccountEntitie).where(AccountEntitie.id == id)
        query_result: AccountEntitie = session.exec(statement=query).first()
        logging.debug("searching account by id ended")
        return query_result

    @cached(account_provider_cache)
    @retry(on=Exception, attempts=4, wait_initial=0.08, wait_exp_base=2)
    def search_account_by_user_id(self: Self, user_id: int) -> list[AccountEntitie]:
        logging.debug(f"searching account by user id {user_id}")
        session: Session = self._session_manager.obtain_session()
        query: Any = select(AccountEntitie).where(AccountEntitie.user_id == user_id)
        query_result: list[AccountEntitie] = session.exec(statement=query).all()
        logging.debug("searching account by user id ended")
        return query_result
