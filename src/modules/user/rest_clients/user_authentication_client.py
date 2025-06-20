import logging
from typing import Self
from urllib.parse import urljoin

import httpx
from asyncache import cached as async_cached
from cachetools import TTLCache
from fastapi import HTTPException
from fastapi import status
from httpx import Response
from stamina import retry

from src.sidecard.system.artifacts.env_provider import EnvProvider

__all__: list[str] = ["UserAuthenticationClient"]

user_authentication_client_cache: TTLCache = TTLCache(ttl=10, maxsize=20)


class UserAuthenticationClient:
    def __init__(self: Self):
        self._env_provider: EnvProvider = EnvProvider()  # type: ignore
        self.base_url: str = str(self._env_provider.identity_validation_ms_base_url)
        self._httpx_client: httpx.AsyncClient = httpx.AsyncClient()

    def clear_cache(self: Self) -> None:
        user_authentication_client_cache.clear()

    @async_cached(user_authentication_client_cache)
    @retry(on=HTTPException, attempts=8, wait_initial=0.4, wait_exp_base=2)
    async def obtain_user_autentication(self: Self) -> bool:
        logging.debug("obtaining user authentication from authentication api")
        url: str = urljoin(self.base_url, r"/integers/?num=1&min=0&max=1&col=1&base=10&format=plain&rnd=new")
        logging.debug(f"authentication client api url: {url}")
        try:
            raw_response: Response = await self._httpx_client.get(url=url, timeout=10)
        except Exception:
            logging.error("error unable to connect authentication api")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        if raw_response.status_code != status.HTTP_200_OK:
            logging.error("the authentication api didnt respond correctly")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            is_valid: bool = int(str(raw_response.text).strip()) == 1
        except Exception:
            logging.error("error parsing response from authentication api")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logging.debug("user authentication obtained from authentication api")
        return is_valid
