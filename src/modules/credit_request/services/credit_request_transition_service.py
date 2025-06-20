import logging
from types import FunctionType
from typing import Self

from fastapi import HTTPException
from fastapi import status as HttpStatus
from sidecard.system.helpers.singleton_helper import Singleton

from src.modules.account.mysql_entites.account_entity import AccountEntitie
from src.modules.account.services.account_service import AccountService
from src.modules.credit_request.mysql_entites.credit_request_entity import CreditRequestEntitie
from src.modules.credit_request.rest_clients.credit_request_score_client import CreditRequestScoreClient
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestByIdRequestDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_dtos import CreditRequestDataResponseDto
from src.modules.credit_request.rest_controllers_dtos.credit_request_transition_dtos import CreditRequestMakeTransitionRequestDto
from src.modules.credit_request.services.credit_request_service import CreditRequestService
from src.modules.credit_request.services.credit_request_states_machine_service import CreditRequestStatesMachineService
from src.sidecard.system.artifacts.i8n_provider import I8nProvider

__all__: list[str] = ["CreditRequestTransitionService"]


class CreditRequestTransitionService(metaclass=Singleton):
    __slots__ = ["_credit_request_states_machine_service", "_credit_request_score_client", "_credit_request_service", "_user_service", "_account_service", "_i8n"]

    def __init__(self: Self):
        self._credit_request_states_machine_service: CreditRequestStatesMachineService = CreditRequestStatesMachineService()
        self._credit_request_score_client: CreditRequestScoreClient = CreditRequestScoreClient()
        self._credit_request_service: CreditRequestService = CreditRequestService()
        self._account_service: AccountService = AccountService()
        self._i8n: I8nProvider = I8nProvider(module="credit_request")

    async def credit_request_make_transition_orchestator(self: Self, credit_request_make_transition_request: CreditRequestMakeTransitionRequestDto) -> CreditRequestDataResponseDto:
        logging.debug("starting credit_request_make_transition_orchestator")
        credit_request: CreditRequestEntitie = self._credit_request_service._found_credit_request_by_id_or_fail(search_id=credit_request_make_transition_request.id)
        transition = credit_request_make_transition_request.transition
        current_status = credit_request.status
        account: AccountEntitie = self._account_service._found_account_by_id_or_fail(search_id=credit_request.account_id)
        new_status, rules = self._credit_request_states_machine_service.check_if_transition_is_allowed(current_status=current_status, transition=transition)
        await self._execute_rules(credit_request=credit_request, account=account, rules=rules)
        await self._make_transition(id=credit_request.id, new_status=new_status)
        response = await self._credit_request_service.get_credit_request_by_id_orchestator(CreditRequestByIdRequestDto(requestId=credit_request_make_transition_request.id))
        logging.debug("ending credit_request_make_transition_orchestator")
        return response

    async def _execute_rules(self: Self, credit_request: CreditRequestEntitie, account: AccountEntitie, rules: list[str]) -> None:
        for rule in rules:
            await self._execute_rule(rule=rule, credit_request=credit_request, account=account)

    async def _execute_rule(self: Self, rule: str, credit_request: CreditRequestEntitie, account: AccountEntitie) -> None:
        method: FunctionType = self._get_rule_(treatment=rule)
        await method(credit_request=credit_request, account=account)

    def _get_rule_(self, treatment: str) -> FunctionType:
        treatments = {"make_transfer": self._make_transfer, "fetch_score": self._fetch_score, "clear_score": self._clear_score, "check_score": self._check_score}
        return treatments[treatment]

    async def _check_score(self: Self, credit_request: CreditRequestEntitie, account: AccountEntitie) -> None:
        if credit_request.score is None:
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM001"))
        if credit_request.score < 5:  # type: ignore
            raise HTTPException(status_code=HttpStatus.HTTP_404_NOT_FOUND, detail=self._i8n.message(message_key="EM002"))

    async def _clear_score(self: Self, credit_request: CreditRequestEntitie, account: AccountEntitie) -> None:
        await self._credit_request_service.set_credit_request_score_orchestator(id=credit_request.id, score=None)

    async def _fetch_score(self: Self, credit_request: CreditRequestEntitie, account: AccountEntitie) -> None:
        score: int = await self._credit_request_score_client.obtain_credit_request_score()
        await self._credit_request_service.set_credit_request_score_orchestator(id=credit_request.id, score=score)

    async def _make_transfer(self: Self, credit_request: CreditRequestEntitie, account: AccountEntitie) -> None:
        await self._account_service.sum_to_account_amount_orchestator(account_id=account.id, amount=credit_request.amount)

    async def _make_transition(self: Self, id: int, new_status: int) -> None:
        await self._credit_request_service.set_credit_request_status_orchestator(id=id, status=new_status)
