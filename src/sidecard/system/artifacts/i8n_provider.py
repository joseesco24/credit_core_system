# !/usr/bin/python3
# type: ignore

# ** info: python imports
import json
import locale

# Jinja
from jinja2 import Template

# ** info: typing imports
from typing import Dict
from typing import Self
from os.path import join
from os.path import dirname
from os.path import realpath

__all__: list[str] = ["I8nProvider"]


class I8nProvider:
    __slots__ = ["_locale_dir", "_messages_dict", "_logs_dict"]

    def __init__(self: Self, module: str) -> None:
        self._locale_dir: str = join(dirname(realpath(__file__)), "..", "..", "..", "static", "i8n", self._get_locale_languaje())
        self._messages_dict: dict[str, str] = json.load(open(join(self._locale_dir, "messages.json")))[module]

    def _get_locale_languaje(self: Self) -> str:
        current_locale: str = locale.getlocale()[0]
        locale_languaje: str = current_locale if current_locale != "es_ES" else "en_US"
        return locale_languaje

    def message(self: Self, message_key: str, **kwargs) -> str:
        return self._get_message_from_dict(dict=self._messages_dict, key=message_key, **kwargs)

    def _get_message_from_dict(self: Self, dict: Dict, key: str, **kwargs) -> str:
        raw_message: str = dict[key] if key in dict else key
        return_message: Template = Template(raw_message).render(**kwargs) if bool(kwargs) else raw_message
        return return_message.lower()
