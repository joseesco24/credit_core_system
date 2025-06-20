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

__all__: list[str] = ["CreditRequestScoreClient"]

user_authentication_client_cache: TTLCache = TTLCache(ttl=3600, maxsize=20)


class CreditRequestScoreClient:
    def __init__(self: Self):
        self._env_provider: EnvProvider = EnvProvider()  # type: ignore
        self.base_url: str = str(self._env_provider.scoring_ms_base_url)
        self._httpx_client: httpx.AsyncClient = httpx.AsyncClient()

    def clear_cache(self: Self) -> None:
        user_authentication_client_cache.clear()

    @async_cached(user_authentication_client_cache)
    @retry(on=HTTPException, attempts=8, wait_initial=0.4, wait_exp_base=2)
    async def obtain_credit_request_score(self: Self) -> int:
        logging.debug("obtaining credit score from credit scoring api")
        url: str = urljoin(self.base_url, r"/integers/?num=1&min=1&max=10&col=1&base=10&format=plain&rnd=new")
        logging.debug(f"authentication client api url: {url}")
        try:
            raw_response: Response = await self._httpx_client.get(url=url, timeout=10)
        except Exception:
            logging.error("error unable to connect to credit scoring api")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        if raw_response.status_code != status.HTTP_200_OK:
            logging.error("the credit scoring api api didnt respond correctly")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            score: int = int(str(raw_response.text).strip())
        except Exception:
            logging.error("error parsing response from credit scoring api")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.clear_cache()
        logging.debug("credit score obtained from credit scoring api")
        return score
