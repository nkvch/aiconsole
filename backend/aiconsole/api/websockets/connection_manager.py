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

"""

Connection manager for websockets. Keeps track of all active connections

"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import WebSocket

if TYPE_CHECKING:
    from aiconsole.api.websockets.server_messages import BaseServerMessage

_log = logging.getLogger(__name__)
_active_connections: list["AICConnection"] = []


@dataclass(frozen=True)
class AcquiredLock:
    chat_id: str
    request_id: str


class AICConnection:
    _websocket: WebSocket
    open_chats_ids: set[str] = set()
    acquired_locks: list[AcquiredLock] = []

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def send(self, msg: "BaseServerMessage"):
        await self._websocket.send_json({"type": msg.get_type(), **msg.model_dump(mode="json")})


async def connect(websocket: WebSocket):
    await websocket.accept()
    connection = AICConnection(websocket)
    _active_connections.append(connection)
    _log.info("Connected")
    return connection


def disconnect(connection: AICConnection):
    _active_connections.remove(connection)
    _log.info("Disconnected")


async def send_message_to_chat(
    chat_id: str,
    msg: "BaseServerMessage",
    source_connection_to_ommit: AICConnection | None = None,
):
    # _log.debug(f"Sending message to {chat_id}: {msg}")
    for connection in _active_connections:
        if chat_id in connection.open_chats_ids and connection != source_connection_to_ommit:
            await connection.send(msg)


async def send_message_to_all(msg: "BaseServerMessage", source_connection_to_ommit: AICConnection | None = None):
    # _log.debug(f"Sending message to all: {msg}")
    for connection in _active_connections:
        if connection != source_connection_to_ommit:
            await connection.send(msg)
