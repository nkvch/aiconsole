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


from fastapi.responses import JSONResponse

from aiconsole.api.endpoints.chats.chat import router

"""
import logging

from pydantic import BaseModel
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

_log = logging.getLogger(__name__)



class FetchCommandParams(BaseModel):
    command: str
    columns: list[str]


async def execute_command_actual(command: str, output_format: str, context_chat_id: str):
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


@router.post("/fetch_command")
async def fetch_command(params: FetchCommandParams):
    output_format = columns_to_output_format(params.columns)

    output = execute_command(params.command, output_format, context_chat_id)

    return JSONResponse(content=output.json())


class ExecuteCommandParams(BaseModel):
    command: str
    columns: list[str]


@router.post("/execute_command")
async def execute_command(params: ExecuteCommandParams):
    return JSONResponse(
        content={
            "command": params.command,
            "columns": params.columns,
        }
    )

"""


@router.post("/")
async def genui():
    return JSONResponse(
        content={
            "code": """
function Component() {
  // Initial state set to the current time
  const [_currentTime, _setCurrentTime] = React.useState(new Date());
  // useEffect to update the current time every second
  React.useEffect(() => {
    // Timer to update current time
    const _timer = setInterval(() => {
      _setCurrentTime(new Date());
    }, 1000);

    // Cleanup on unmount
    return () => clearInterval(_timer);
  }, []);

  // Format time as a string HH:MM:SS
  const _formatTime = (_date) => {
    return _date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false // 24 hour clock
    });
  };

  // Render the current time
  return (
    <div className="bg-blue" style={{ fontFamily: 'Monospace', fontSize: '24px', textAlign: 'center' }}>
      {_formatTime(_currentTime)}
    </div>
  );
}
"""
        }
    )
