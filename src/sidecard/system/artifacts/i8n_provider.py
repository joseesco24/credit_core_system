import json
from os.path import dirname
from os.path import join
from os.path import realpath
from typing import Dict
from typing import Self

from jinja2 import Template
from sidecard.system.artifacts.env_provider import EnvProvider

__all__: list[str] = ["I8nProvider"]


class I8nProvider:
    __slots__ = ["_locale_dir", "_messages_dict"]
    _env_provider: EnvProvider = EnvProvider()  # type: ignore

    def __init__(self: Self, module: str) -> None:
        self._locale_dir: str = join(dirname(realpath(__file__)), "..", "..", "..", "static", "i8n", self._get_locale_languaje())
        self._messages_dict: dict[str, str] = json.load(open(join(self._locale_dir, "messages.json")))[module]

    def _get_locale_languaje(self: Self) -> str:
        current_locale: str = self._env_provider.app_posix_locale.split(".")[0]  # type: ignore
        locale_languaje: str = current_locale if current_locale != "es_ES" else "en_US"
        return locale_languaje

    def message(self: Self, message_key: str, **kwargs) -> str:
        return self._get_message_from_dict(dict=self._messages_dict, key=message_key, **kwargs)

    def _get_message_from_dict(self: Self, dict: Dict, key: str, **kwargs) -> str:
        raw_message: str = dict[key] if key in dict else key
        return_message: Template = Template(raw_message).render(**kwargs) if bool(kwargs) else raw_message  # type: ignore
        return return_message.lower()  # type: ignore
