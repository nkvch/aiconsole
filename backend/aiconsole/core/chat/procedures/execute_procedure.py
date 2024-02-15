"""
from uuid import uuid4

from aiconsole.api.websockets.do_process_chat import do_process_chat
from aiconsole.core.chat.locking import DefaultChatMutator
from aiconsole.core.chat.types import (
    ActorId,
    AICMessage,
    AICMessageGroup,
    AICToolCall,
    Chat,
    ChatOptions,
)


async def execute_procedure(command: str, output_format: str):
    chat_id = str(uuid4())
    request_id = str(uuid4())

    chat_id = str(uuid4())
    request_id = str(uuid4())

    chat = Chat(
        id=chat_id,
        name="",
        message_groups=[
            AICMessageGroup(
                id=str(uuid4()),
                role="user",
                task="",
                analysis="",
                actor_id=ActorId(type="user", id="user"),
                materials_ids=[],
                messages=[
                    AICMessage(
                        id=str(uuid4()),
                        timestamp="",
                        content=params.command,
                        requested_format=output_format,
                        tool_calls=[
                            AICToolCall(
                                id=str(uuid4()),
                                headline="",
                                type="output_format",
                                code=output_format,
                            )
                        ],
                    )
                ],
            )
        ],
        chat_options=ChatOptions(
            agent_id=None,
            materials_ids=[],
        ),
        last_modified=0,
    )

    chat_mutator = DefaultChatMutator(
        chat_id=chat_id,
        request_id=request_id,
        connection=None,  # Source connection is None because the originating mutations come from server
    )

    await do_process_chat(chat_mutator)

    output = extract_result(chat, output_format)

    return output

"""
