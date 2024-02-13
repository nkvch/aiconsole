import traceback

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.chat.chat_mutations import (
    AppendToOutputToolCallMutation,
    SetIsExecutingToolCallMutation,
    SetOutputToolCallMutation,
)
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.code_running.run_code import get_code_interpreter


async def run_code(
    chat_mutator: ChatMutator,
    materials: list[Material],
    tool_call_id,
):
    tool_call_location = chat_mutator.chat.get_tool_call_location(tool_call_id)

    if not tool_call_location:
        raise Exception(f"Tool call {tool_call_id} should have been created")

    tool_call = tool_call_location.tool_call

    try:
        await chat_mutator.mutate(
            SetIsExecutingToolCallMutation(
                tool_call_id=tool_call_id,
                is_executing=True,
            )
        )

        await chat_mutator.mutate(
            SetOutputToolCallMutation(
                tool_call_id=tool_call_id,
                output="",
            )
        )

        try:
            assert tool_call.language is not None
            async for token in (await get_code_interpreter(tool_call.language, chat_mutator.chat.id)).run(
                tool_call.code, materials
            ):
                await chat_mutator.mutate(
                    AppendToOutputToolCallMutation(
                        tool_call_id=tool_call_id,
                        output_delta=token,
                    )
                )
        except Exception:
            await connection_manager().send_to_chat(
                ErrorServerMessage(error=traceback.format_exc().strip()), chat_mutator.chat.id
            )

            await chat_mutator.mutate(
                AppendToOutputToolCallMutation(
                    tool_call_id=tool_call_id,
                    output_delta=traceback.format_exc().strip(),
                )
            )
    finally:
        await chat_mutator.mutate(
            SetIsExecutingToolCallMutation(
                tool_call_id=tool_call_id,
                is_executing=False,
            )
        )
