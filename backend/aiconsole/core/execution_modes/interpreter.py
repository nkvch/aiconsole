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

import logging
from uuid import uuid4

from aiconsole.core.assets.agents.agent import ExecutionModeContext
from aiconsole.core.chat.chat_outgoing_messages import (
    ResetMessageWSMessage,
    SequenceStage,
    UpdateMessageWSMessage,
    UpdateToolCallWSMessage,
)
from aiconsole.core.code_running.code_interpreters.language_map import language_map
from aiconsole.core.execution_modes.get_agent_system_message import get_agent_system_message
from aiconsole.core.gpt.create_full_prompt_with_materials import create_full_prompt_with_materials
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import GPTRequest, ToolDefinition, ToolFunctionDefinition
from aiconsole.core.gpt.types import CLEAR_STR
from aiconsole.utils.convert_messages import convert_messages
from openai_function_call import OpenAISchema
from pydantic import BaseModel, Field

_log = logging.getLogger(__name__)


class python(OpenAISchema):
    """
    When you send a message containing Python code to python, it will be executed in a stateful Jupyter notebook environment
    """

    code: str = Field(
        ...,
        description="python code to execute, it will be executed in a stateful Jupyter notebook environment",
        json_schema_extra={"type": "string"},
    )


class shell(OpenAISchema):
    """
    This function executes the given code on the user's system using the local environment and returns the output.
    """

    code: str = Field(..., json_schema_extra={"type": "string"})


class applescript(OpenAISchema):
    """
    This function executes the given code on the user's system using the local environment and returns the output.
    """

    code: str = Field(..., json_schema_extra={"type": "string"})


async def execution_mode_interpreter(
    context: ExecutionModeContext,
):
    global llm

    system_message = create_full_prompt_with_materials(
        intro=get_agent_system_message(context.agent),
        materials=context.relevant_materials,
    )

    _log.debug(f"System message:\n{system_message}")

    executor = GPTExecutor()

    class ToolCallStatus(BaseModel):
        id: str
        language: str | None = None
        code: str = ""
        end_with_code: str = ""

    tool_calls_data: dict[str, ToolCallStatus] = {}

    message_id = str(uuid4())
    await UpdateMessageWSMessage(
        stage=SequenceStage.START,
        id=message_id,
    ).send_to_chat(context.chat.id)

    try:
        async for chunk in executor.execute(
            GPTRequest(
                system_message=system_message,
                gpt_mode=context.agent.gpt_mode,
                messages=[message for message in convert_messages(context.chat)],
                tools=[
                    ToolDefinition(type="function", function=ToolFunctionDefinition(**python.openai_schema)),
                    ToolDefinition(type="function", function=ToolFunctionDefinition(**shell.openai_schema)),
                    ToolDefinition(type="function", function=ToolFunctionDefinition(**applescript.openai_schema)),
                ],
                min_tokens=250,
                preferred_tokens=2000,
            )
        ):
            if chunk == CLEAR_STR:
                if message_id:
                    await ResetMessageWSMessage(
                        id=message_id,
                    ).send_to_chat(context.chat.id)
                continue

            if "choices" not in chunk or len(chunk["choices"]) == 0:
                continue

            delta = chunk["choices"][0]["delta"]

            if "content" in delta and delta["content"]:
                await UpdateMessageWSMessage(
                    stage=SequenceStage.MIDDLE,
                    id=message_id,
                    text_delta=delta["content"],
                ).send_to_chat(context.chat.id)

            tool_calls = executor.partial_response.choices[0].message.tool_calls

            for tool_call in tool_calls:
                if tool_call.id not in tool_calls_data:
                    tool_calls_data[tool_call.id] = ToolCallStatus(id=tool_call.id)
                    await UpdateToolCallWSMessage(
                        stage=SequenceStage.START,
                        id=tool_call.id,
                    ).send_to_chat(context.chat.id)

                tool_call_data = tool_calls_data[tool_call.id]

                if tool_call.type == "function":
                    function_call = tool_call.function

                    async def send_language_if_needed(lang: str):
                        if tool_call_data.language is None:
                            tool_call_data.language = lang

                            await UpdateToolCallWSMessage(
                                stage=SequenceStage.MIDDLE,
                                id=tool_call.id,
                                language=tool_call_data.language,
                            ).send_to_chat(context.chat.id)

                    async def send_code_delta(code_delta: str):
                        if code_delta:
                            await UpdateToolCallWSMessage(
                                stage=SequenceStage.MIDDLE,
                                id=tool_call.id,
                                code_delta=code_delta,
                            ).send_to_chat(context.chat.id)

                    if function_call.arguments:
                        if function_call.name not in [python.__name__, shell.__name__, applescript.__name__]:
                            await send_language_if_needed("python")

                            _log.info(f"function_call: {function_call}")
                            _log.info(f"function_call.arguments: {function_call.arguments}")

                            code_delta = f"{function_call.name}("  # TODO: This won't work
                            await send_code_delta(code_delta)
                            tool_call_data.end_with_code = ")"
                        else:
                            arguments = function_call.arguments
                            languages = language_map.keys()

                            if tool_call_data.language is None and function_call.name in languages:
                                # Languge is in the name of the function call
                                await send_language_if_needed(function_call.name)

                            # This can now be both a string and a json object
                            if isinstance(arguments, str):
                                # We need to handle incorrect OpenAI responses, sometmes arguments is a string containing the code
                                if arguments and not arguments.startswith("{"):
                                    await send_language_if_needed("python")

                                    code_delta = arguments[len(tool_call_data.code) :]
                                    tool_call_data.code = arguments

                                    await send_code_delta(code_delta)
                            else:
                                if arguments and "code" in arguments:
                                    await send_language_if_needed("python")

                                    code_delta = arguments["code"][len(tool_call_data.code) :]
                                    tool_call_data.code = arguments["code"]

                                    await send_code_delta(code_delta)
    finally:
        for tool_call_id in tool_calls_data:
            tool_call_data = tool_calls_data[tool_call_id]
            if tool_call_data.end_with_code:
                await UpdateToolCallWSMessage(
                    stage=SequenceStage.MIDDLE,
                    id=tool_call_id,
                    code_delta=tool_call_data.end_with_code,
                ).send_to_chat(context.chat.id)
            await UpdateToolCallWSMessage(
                stage=SequenceStage.END,
                id=tool_call_id,
            ).send_to_chat(context.chat.id)

        await UpdateMessageWSMessage(
            stage=SequenceStage.END,
            id=message_id,
        ).send_to_chat(context.chat.id)
