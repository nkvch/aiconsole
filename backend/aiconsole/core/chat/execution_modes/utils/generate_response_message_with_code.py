import logging
from datetime import datetime
from typing import Type
from uuid import uuid4

from litellm import ModelResponse

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.chat.chat_mutations import (
    AppendToCodeToolCallMutation,
    AppendToContentMessageMutation,
    CreateMessageMutation,
    SetContentMessageMutation,
    SetIsStreamingMessageMutation,
    SetIsStreamingToolCallMutation,
)
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.convert_messages import convert_messages
from aiconsole.core.chat.execution_modes.utils.send_code import send_code
from aiconsole.core.gpt.function_calls import OpenAISchema
from aiconsole.core.gpt.gpt_executor import GPTExecutor
from aiconsole.core.gpt.request import GPTRequest
from aiconsole.core.gpt.tool_definition import ToolDefinition, ToolFunctionDefinition
from aiconsole.core.gpt.types import (
    CLEAR_STR,
    EnforcedFunctionCall,
    EnforcedFunctionCallFuncSpec,
)

_log = logging.getLogger(__name__)


async def generate_response_message_with_code(
    chat_mutator: ChatMutator,
    agent: AICAgent,
    system_message: str,
    language_classes: list[Type[OpenAISchema]],
    enforced_language: Type[OpenAISchema] | None = None,
):
    executor = GPTExecutor()

    # Assumes an existing message group that was created for us
    last_message_group = chat_mutator.chat.message_groups[-1]

    tools_requiring_closing_parenthesis: list[str] = []
    message_id = str(uuid4())

    await chat_mutator.mutate(
        CreateMessageMutation(
            message_group_id=last_message_group.id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            content="",
        )
    )

    try:
        await chat_mutator.mutate(
            SetIsStreamingMessageMutation(
                message_id=message_id,
                is_streaming=True,
            )
        )

        all_requested_formats: list[ToolDefinition] = []
        for message_group in chat_mutator.chat.message_groups:
            for message in message_group.messages:
                if message.requested_format:
                    all_requested_formats.append(message.requested_format)

        async for chunk_or_clear in executor.execute(
            GPTRequest(
                system_message=system_message,
                gpt_mode=agent.gpt_mode,
                messages=[message for message in convert_messages(chat_mutator.chat)],
                tools=[
                    *[
                        ToolDefinition(
                            type="function",
                            function=ToolFunctionDefinition(**language_cls.openai_schema()),
                        )
                        for language_cls in language_classes
                    ],
                    *all_requested_formats,
                ],
                tool_choice=(
                    EnforcedFunctionCall(
                        type="function", function=EnforcedFunctionCallFuncSpec(name=enforced_language.__name__)
                    )
                    if enforced_language
                    else None
                ),
                min_tokens=250,
                preferred_tokens=2000,
                temperature=0.2,
            )
        ):

            if chunk_or_clear == CLEAR_STR:
                await chat_mutator.mutate(SetContentMessageMutation(message_id=message_id, content=""))
                continue

            chunk: ModelResponse = chunk_or_clear

            # When does this happen?
            if not chunk.get("choices"):
                continue
            else:
                delta_content = chunk["choices"][0]["delta"].get("content")
                if delta_content:
                    await chat_mutator.mutate(
                        AppendToContentMessageMutation(
                            message_id=message_id,
                            content_delta=delta_content,
                        )
                    )

                message_location = chat_mutator.chat.get_message_location(message_id)
                if not message_location:
                    raise Exception(f"Message {message_id} should have been created")

                if executor.partial_response.choices[0].message.tool_calls and message_location.message.is_streaming:
                    await chat_mutator.mutate(
                        SetIsStreamingMessageMutation(
                            message_id=message_id,
                            is_streaming=False,
                        )
                    )

                await send_code(
                    executor.partial_response.choices[0].message.tool_calls,
                    chat_mutator,
                    tools_requiring_closing_parenthesis,
                    message_id,
                    language_classes=language_classes,
                )

    finally:
        await chat_mutator.mutate(
            SetIsStreamingMessageMutation(
                message_id=message_id,
                is_streaming=False,
            )
        )

        for tool_id in tools_requiring_closing_parenthesis:
            await chat_mutator.mutate(
                AppendToCodeToolCallMutation(
                    tool_call_id=tool_id,
                    code_delta=")",
                )
            )
        for tool_call in executor.partial_response.choices[0].message.tool_calls:
            await chat_mutator.mutate(
                SetIsStreamingToolCallMutation(
                    tool_call_id=tool_call.id,
                    is_streaming=False,
                )
            )
        _log.debug(f"tools_requiring_closing_parenthesis: {tools_requiring_closing_parenthesis}")
