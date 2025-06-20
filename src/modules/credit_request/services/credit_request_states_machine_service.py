import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Self

from fastapi import HTTPException
from fastapi import status as HttpStatus
from sidecard.system.artifacts.i8n_provider import I8nProvider
from sidecard.system.helpers.singleton_helper import Singleton

__all__: list[str] = ["CreditRequestStatesMachineService"]


class CreditRequestStatesMachineService(metaclass=Singleton):
    __slots__ = ["_current_file_path", "_states_machine_path", "_states_machine_config", "_i8n"]

    def __init__(self: Self):
        self._current_file_path: Path = Path(__file__).parent.resolve()
        self._states_machine_path: Path = Path(self._current_file_path, "..", "static", "credit_request_states_machine.json")
        self._states_machine_config = self._load_states_machine_config()
        self._i8n: I8nProvider = I8nProvider(module="credit_request_states_machine")

    def check_if_transition_is_allowed(self: Self, current_status: int, transition: int) -> tuple[int, list[str]]:
        transition_rules = self._get_transition_rules()
        transition_key = f"transition_{transition}"
        status_key = f"state_{current_status}"
        allowed_transitions = transition_rules.get(status_key, None)
        if allowed_transitions is None:
            raise HTTPException(status_code=HttpStatus.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM001"))
        transition_data = allowed_transitions.get(transition_key, None)
        if transition_data is None:
            raise HTTPException(status_code=HttpStatus.HTTP_409_CONFLICT, detail=self._i8n.message(message_key="EM002"))
        rules: list[str] = transition_data.get("rules", [])
        new_status: int = transition_data["new_status"]
        return new_status, rules

    def _load_states_machine_config(self) -> Dict[str, Any]:
        with open(self._states_machine_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _get_transition_rules(self: Self) -> Dict[str, Dict]:
        transitions = self._states_machine_config["transition_rules"]
        return transitions
