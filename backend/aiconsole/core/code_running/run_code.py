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
import asyncio
from typing import AsyncGenerator, cast

from aiconsole.core.assets.materials.material import Material
from aiconsole.core.code_running.code_interpreters.base_code_interpreter import (
    BaseCodeInterpreter,
)
from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from aiconsole.core.code_running.code_interpreters.language_map import language_map

code_interpreters: dict[str, dict[str, BaseCodeInterpreter]] = {}


_global_code_running_lock = asyncio.Lock()


async def run_in_code_interpreter(
    language: str, chat_id: str, code: str, materials: list[Material]
) -> AsyncGenerator[str, None]:
    async with _global_code_running_lock:
        interpreter = await get_code_interpreter(language, chat_id)
        return interpreter.run(code, materials)


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

    if chat_id:
        for code_interpreter in list(code_interpreters.get(chat_id, {}).values()):
            code_interpreter.terminate()
        code_interpreters[chat_id] = {}
    else:
        for chat_interpreters in code_interpreters.values():
            for code_interpreter in chat_interpreters.values():
                code_interpreter.terminate()
        code_interpreters = {}
