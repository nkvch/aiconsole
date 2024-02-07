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
import traceback
from datetime import datetime
from typing import cast
from uuid import uuid4

from litellm import ModelResponse  # type: ignore
from pydantic import Field

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.chat.chat_mutations import (
    AppendToCodeToolCallMutation,
    AppendToContentMessageMutation,
    AppendToHeadlineToolCallMutation,
    AppendToOutputToolCallMutation,
    CreateMessageMutation,
    CreateToolCallMutation,
    SetCodeToolCallMutation,
    SetContentMessageMutation,
    SetHeadlineToolCallMutation,
    SetIsExecutingToolCallMutation,
    SetIsStreamingMessageMutation,
    SetIsStreamingToolCallMutation,
    SetLanguageToolCallMutation,
    SetOutputToolCallMutation,
)
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.execution_mode import (
    AcceptCodeContext,
    ExecutionMode,
    ProcessChatContext,
)
from aiconsole.core.chat.execution_modes.get_agent_system_message import (
    get_agent_system_message,
)
from aiconsole.core.chat.types import AICMessageGroup
from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from aiconsole.core.code_running.code_interpreters.language_map import language_map
from aiconsole.core.code_running.run_code import get_code_interpreter
from aiconsole.core.gpt.create_full_prompt_with_materials import (
    create_full_prompt_with_materials,
)
from aiconsole.core.gpt.function_calls import OpenAISchema
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import (
    GPTRequest,
    ToolDefinition,
    ToolFunctionDefinition,
)
from aiconsole.core.gpt.types import CLEAR_STR
from aiconsole.core.settings.settings import settings

_log = logging.getLogger(__name__)


class CodeTask(OpenAISchema):
    headline: str = Field(
        ...,
        description="Must have. Title of this task with maximum 15 characters.",
        json_schema_extra={"type": "string"},
    )


class python(CodeTask):
    """
    Execute python code in a stateful Jupyter notebook environment.
    You can execute shell commands by prefixing code lines with "!".
    """

    code: str = Field(
        ...,
        description="Python code to execute. It will be executed in the statefull Jupyter notebook environment. Always show result to the user.",
        json_schema_extra={"type": "string"},
    )


class applescript(CodeTask):
    """
    This function executes the given code on the user's system using the local environment and returns the output.
    """

    code: str = Field(..., json_schema_extra={"type": "string"})


async def _execution_mode_process(
    context: ProcessChatContext,
):
    # Assumes an existing message group that was created for us
    last_message_group = context.chat_mutator.chat.message_groups[-1]

    system_message = create_full_prompt_with_materials(
        intro=get_agent_system_message(context.agent),
        materials=context.rendered_materials,
    )

    executor = GPTExecutor()

    await _generate_response(last_message_group, context, system_message, executor, last_message_group)

    last_message = last_message_group.messages[-1]

    if last_message.tool_calls:
        # Run all code in the last message
        for tool_call in last_message.tool_calls:
            if settings().unified_settings.code_autorun:
                accept_context = AcceptCodeContext(
                    chat_mutator=context.chat_mutator,
                    tool_call_id=tool_call.id,
                    agent=context.agent,
                    materials=context.materials,
                    rendered_materials=context.rendered_materials,
                )
                await _execution_mode_accept_code(accept_context)


async def _run_code(context: ProcessChatContext, tool_call_id):
    tool_call_location = context.chat_mutator.chat.get_tool_call_location(tool_call_id)

    if not tool_call_location:
        raise Exception(f"Tool call {tool_call_id} should have been created")

    tool_call = tool_call_location.tool_call

    try:
        await context.chat_mutator.mutate(
            SetIsExecutingToolCallMutation(
                tool_call_id=tool_call_id,
                is_executing=True,
            )
        )

        await context.chat_mutator.mutate(
            SetOutputToolCallMutation(
                tool_call_id=tool_call_id,
                output="",
            )
        )

        try:
            context.rendered_materials

            assert tool_call.language is not None
            async for token in get_code_interpreter(tool_call.language, context.chat_mutator.chat.id).run(
                tool_call.code, context.materials
            ):
                await context.chat_mutator.mutate(
                    AppendToOutputToolCallMutation(
                        tool_call_id=tool_call_id,
                        output_delta=token,
                    )
                )
        except Exception:
            await connection_manager().send_to_chat(
                ErrorServerMessage(error=traceback.format_exc().strip()), context.chat_mutator.chat.id
            )

            await context.chat_mutator.mutate(
                AppendToOutputToolCallMutation(
                    tool_call_id=tool_call_id,
                    output_delta=traceback.format_exc().strip(),
                )
            )
    finally:
        await context.chat_mutator.mutate(
            SetIsExecutingToolCallMutation(
                tool_call_id=tool_call_id,
                is_executing=False,
            )
        )


async def _generate_response(
    message_group: AICMessageGroup,
    context: ProcessChatContext,
    system_message: str,
    executor: GPTExecutor,
    last_message_group: AICMessageGroup | None = None,
):
    tools_requiring_closing_parenthesis: list[str] = []
    message_id = str(uuid4())
    # Load the messages from the chat in GPTRequestMessage format
    messages = [message for message in convert_messages(context.chat_mutator.chat, last_message_group)]

    await context.chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=message_group.id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content="",
        )
    )

    try:
        await context.chat_mutator.mutate(
            SetIsStreamingMessageMutation(
                message_id=message_id,
                is_streaming=True,
            )
        )
        async for chunk_or_clear in executor.execute(
            GPTRequest(
                system_message=system_message,
                gpt_mode=context.agent.gpt_mode,
                messages=messages,
                tools=[
                    ToolDefinition(
                        type="function",
                        function=ToolFunctionDefinition(**python.openai_schema()),
                    ),
                    ToolDefinition(
                        type="function",
                        function=ToolFunctionDefinition(**applescript.openai_schema()),
                    ),
                ],
                min_tokens=250,
                preferred_tokens=2000,
                temperature=0.2,
            )
        ):
            # What is this?
            if chunk_or_clear == CLEAR_STR:
                await context.chat_mutator.mutate(SetContentMessageMutation(message_id=message_id, content=""))
                continue

            chunk: ModelResponse = chunk_or_clear

            # When does this happen?
            if not chunk.get("choices"):
                continue
            else:
                delta_content = chunk["choices"][0]["delta"].get("content")
                if delta_content:
                    await context.chat_mutator.mutate(
                        AppendToContentMessageMutation(
                            message_id=message_id,
                            content_delta=delta_content,
                        )
                    )

                await _send_code(
                    executor.partial_response.choices[0].message.tool_calls,
                    context,
                    tools_requiring_closing_parenthesis,
                    message_id,
                )

    finally:
        for tool_id in tools_requiring_closing_parenthesis:
            await context.chat_mutator.mutate(
                AppendToCodeToolCallMutation(
                    tool_call_id=tool_id,
                    code_delta=")",
                )
            )
        for tool_call in executor.partial_response.choices[0].message.tool_calls:
            await context.chat_mutator.mutate(
                SetIsStreamingToolCallMutation(
                    tool_call_id=tool_call.id,
                    is_streaming=False,
                )
            )
        await context.chat_mutator.mutate(
            SetIsStreamingMessageMutation(
                message_id=message_id,
                is_streaming=False,
            )
        )
        _log.debug(f"tools_requiring_closing_parenthesis: {tools_requiring_closing_parenthesis}")


async def _send_code(tool_calls, context, tools_requiring_closing_parenthesis, message_id):
    for index, tool_call in enumerate(tool_calls):
        # All tool calls with lower indexes are finished
        prev_tool = tool_calls[index - 1] if index > 0 else None
        if prev_tool and prev_tool.id in tools_requiring_closing_parenthesis:
            await context.chat_mutator.mutate(
                AppendToCodeToolCallMutation(
                    tool_call_id=prev_tool.id,
                    code_delta=")",
                )
            )

            tools_requiring_closing_parenthesis.remove(prev_tool.id)

        tool_call_info = context.chat_mutator.chat.get_tool_call_location(tool_call.id)

        if not tool_call_info:
            await context.chat_mutator.mutate(
                CreateToolCallMutation(
                    message_id=message_id,
                    tool_call_id=tool_call.id,
                    code="",
                    headline="",
                    language=None,
                    output=None,
                )
            )

            tool_call_info = context.chat_mutator.chat.get_tool_call_location(tool_call.id)

            if not tool_call_info:
                raise Exception(f"Tool call {tool_call.id} should have been created")

        tool_call_data = tool_call_info.tool_call

        if not tool_call_data:
            raise Exception(f"Tool call {tool_call.id} not found")

        await context.chat_mutator.mutate(
            SetIsStreamingToolCallMutation(
                tool_call_id=tool_call.id,
                is_streaming=True,
            )
        )

        async def send_language_if_needed(lang: LanguageStr):
            if tool_call_data.language is None:
                await context.chat_mutator.mutate(
                    SetLanguageToolCallMutation(
                        tool_call_id=tool_call.id,
                        language=lang,
                    )
                )

        async def send_headline_delta_for_headline(headline: str):
            if not headline.startswith(tool_call_data.headline):
                _log.warning(f"Reseting headline to: {headline}")
                await context.chat_mutator.mutate(
                    SetHeadlineToolCallMutation(
                        tool_call_id=tool_call.id,
                        headline=headline,
                    )
                )
            else:
                start_index = len(tool_call_data.headline)
                headline_delta = headline[start_index:]

                if headline_delta:
                    await context.chat_mutator.mutate(
                        AppendToHeadlineToolCallMutation(
                            tool_call_id=tool_call.id,
                            headline_delta=headline_delta,
                        )
                    )

        async def send_code_delta_for_code(code: str):
            if not code.startswith(tool_call_data.code):
                _log.warning(f"Reseting code to: {code}")
                await context.chat_mutator.mutate(
                    SetCodeToolCallMutation(
                        tool_call_id=tool_call.id,
                        code=code,
                    )
                )
            else:
                start_index = len(tool_call_data.code)
                code_delta = code[start_index:]

                if code_delta:
                    await context.chat_mutator.mutate(
                        AppendToCodeToolCallMutation(
                            tool_call_id=tool_call.id,
                            code_delta=code_delta,
                        )
                    )

        if tool_call.type == "function":
            function_call = tool_call.function

            if not function_call.arguments:
                continue

            if function_call.name in [
                python.__name__,
                applescript.__name__,
            ]:
                # Languge is in the name of the function call

                languages = language_map.keys()

                if tool_call_data.language is None and function_call.name in languages:
                    await send_language_if_needed(cast(LanguageStr, function_call.name))

                code = None
                headline = None

                if function_call.arguments_dict:
                    code = function_call.arguments_dict.get("code", None)
                    headline = function_call.arguments_dict.get("headline", None)
                else:
                    # Sometimes we don't have a dict, but it's still a json string

                    if not function_call.arguments.startswith("{"):
                        code = function_call.arguments

                if code:
                    await send_language_if_needed("python")
                    await send_code_delta_for_code(code)

                if headline:
                    await send_headline_delta_for_headline(headline)
            else:
                # We have a direct function call, without specifying the language

                await send_language_if_needed("python")

                if function_call.arguments_dict:
                    # ok we have a dict, those are probably arguments and the name of the function call is the name of the function

                    arguments_materialised = [
                        f"{key}={repr(value)}" for key, value in function_call.arguments_dict.items()
                    ]
                    code = f"{function_call.name}({', '.join(arguments_materialised)})"

                    await send_code_delta_for_code(code)
                else:
                    # We have a string in the arguments, thats probably the code
                    await send_code_delta_for_code(function_call.arguments)


async def _execution_mode_accept_code(
    context: AcceptCodeContext,
):
    tool_call_location = context.chat_mutator.chat.get_tool_call_location(context.tool_call_id)

    if not tool_call_location:
        raise Exception(f"Tool call {context.tool_call_id} should have been created")

    tool_call = tool_call_location.tool_call

    process_chat_context = ProcessChatContext(
        message_group_id=tool_call_location.message_group.id,
        chat_mutator=context.chat_mutator,
        agent=context.agent,
        materials=context.materials,
        rendered_materials=context.rendered_materials,
    )

    await _run_code(process_chat_context, tool_call_id=tool_call.id)

    # if is in last message and all tools have finished running, resume operation with the same agent
    if (
        tool_call_location.message_group.id == context.chat_mutator.chat.message_groups[-1].id
        and tool_call_location.message.id == context.chat_mutator.chat.message_groups[-1].messages[-1].id
    ):
        finished_running_code = all(
            (not tool_call.is_executing) and (tool_call.output is not None)
            for tool_call in tool_call_location.message.tool_calls
        )

        if finished_running_code:
            await _execution_mode_process(process_chat_context)


execution_mode = ExecutionMode(
    process_chat=_execution_mode_process,
    accept_code=_execution_mode_accept_code,
)
