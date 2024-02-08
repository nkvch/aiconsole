# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import cast

from aiconsole.core.code_running.code_interpreters.base_code_interpreter import (
    BaseCodeInterpreter,
)
from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from aiconsole.core.code_running.code_interpreters.language_map import language_map

code_interpreters: dict[str, dict[str, BaseCodeInterpreter]] = {}


async def get_code_interpreter(language_raw: str, chat_id: str) -> BaseCodeInterpreter:
    language_raw = language_raw.lower()

    if language_raw not in language_map:
        raise ValueError(f"Unknown or unsupported language: {language_raw}")

    language: LanguageStr = cast(LanguageStr, language_raw)

    if chat_id not in code_interpreters:
        code_interpreters[chat_id] = {}
    if language not in code_interpreters[chat_id]:
        code_interpreters[chat_id][language] = language_map[language]()
        await code_interpreters[chat_id][language].initialize()
    return code_interpreters[chat_id][language]


def reset_code_interpreters(chat_id: str | None = None):
    global code_interpreters

    interpreters: list[BaseCodeInterpreter] = []
    if chat_id is not None:
        if chat_id in code_interpreters:
            interpreters = list(code_interpreters[chat_id].values())
    else:
        for chat_interpreters in code_interpreters.values():
            for interpreter in chat_interpreters.values():
                interpreters.append(interpreter)
    for code_interpreter in interpreters:
        code_interpreter.terminate()

    if chat_id is not None and chat_id in code_interpreters:
        code_interpreters[chat_id] = {}
    else:
        code_interpreters = {}
