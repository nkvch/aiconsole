import os
from contextlib import asynccontextmanager
from datetime import datetime
from time import sleep
from typing import Any
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient

from aiconsole.api.endpoints.projects.services import ProjectDirectory
from aiconsole.api.websockets.client_messages import (
    AcceptCodeClientMessage,
    AcquireLockClientMessage,
    CloseChatClientMessage,
    InitChatMutationClientMessage,
    OpenChatClientMessage,
    ProcessChatClientMessage,
    ReleaseLockClientMessage,
)
from aiconsole.app import app
from aiconsole.core.chat.chat_mutations import (
    CreateMessageGroupMutation,
    CreateMessageMutation,
)
from aiconsole.core.settings import project_settings

_PROJECT_PATH = "./"
_CHAT_ID = str(uuid4())
_REQUEST_ID = str(uuid4())
_MESSAGE_GROUP_ID = str(uuid4())
_MESSAGE = "Run factorial of 5"
_EXPECTED_OUTPUT = "The factorial of 5 is 120."


@pytest.fixture(autouse=True)
def setup_envs() -> None:
    os.environ["CORS_ORIGIN"] = "http://localhost:3000"


@pytest.fixture
def project_directory() -> ProjectDirectory:
    return ProjectDirectory()


@pytest.fixture
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.mark.asyncio
async def test_should_calculate_factorial_of_given_number(
    project_directory: ProjectDirectory, background_tasks: BackgroundTasks
):
    # 1. Create project or switch to existing one
    # 2. Create chat and open it
    # 3. Send messages to chat (doProcess)
    # 4. Check responses
    # 5. Do the same process 100 times
    # 6. Caching mechanism (files / redis)

    async with _initialize_project_with_chat(project_directory, background_tasks) as websocket:
        await ProcessChatClientMessage(request_id=_REQUEST_ID, chat_id=_CHAT_ID).send(websocket)

        tool_call_id = _get_tool_call_id(websocket)

        await AcceptCodeClientMessage(request_id=_REQUEST_ID, chat_id=_CHAT_ID, tool_call_id=tool_call_id).send(
            websocket
        )

        result = _get_generated_code_output(websocket)
        assert result == _EXPECTED_OUTPUT


@asynccontextmanager
async def _initialize_project_with_chat(project_directory: ProjectDirectory, background_tasks: BackgroundTasks) -> Any:
    client = TestClient(app())
    await project_settings.init()

    await project_directory.switch_or_save_project(directory=_PROJECT_PATH, background_tasks=background_tasks)
    try:
        with client.websocket_connect("/ws") as websocket:
            await OpenChatClientMessage(chat_id=_CHAT_ID).send(websocket)
            _wait_for_websocket_response("ChatOpenedServerMessage", websocket)

            await AcquireLockClientMessage(
                request_id=_REQUEST_ID,
                chat_id=_CHAT_ID,
            ).send(websocket)
            _wait_for_websocket_response("NotifyAboutChatMutationServerMessage", websocket)

            await InitChatMutationClientMessage(
                request_id=_REQUEST_ID,
                chat_id=_CHAT_ID,
                mutation=CreateMessageGroupMutation(
                    message_group_id=_MESSAGE_GROUP_ID,
                    agent_id="user",
                    username="",
                    email="",
                    role="user",
                    task="",
                    materials_ids=[],
                    analysis="",
                ),
            ).send(websocket)

            await InitChatMutationClientMessage(
                request_id=_REQUEST_ID,
                chat_id=_CHAT_ID,
                mutation=CreateMessageMutation(
                    message_group_id=_MESSAGE_GROUP_ID,
                    message_id=str(uuid4()),
                    timestamp=str(datetime.now()),
                    content=_MESSAGE,
                ),
            ).send(websocket)
            await ReleaseLockClientMessage(
                request_id=_REQUEST_ID,
                chat_id=_CHAT_ID,
            ).send(websocket)

            yield websocket
    finally:
        await CloseChatClientMessage(chat_id=_CHAT_ID).send(websocket)


def _get_tool_call_id(websocket: Any) -> str:
    iterations = 0
    tool_call_id = None
    while iterations < 1000:
        json = websocket.receive_json()
        if mutation := json.get("mutation"):
            mutation_type = mutation["type"]
            if mutation_type == "AppendToCodeToolCallMutation":
                tool_call_id = mutation["tool_call_id"]
            elif mutation_type == "LockReleasedMutation" and tool_call_id is not None:
                break
        iterations += 1

    assert tool_call_id is not None, "Tool call id for generated code not found in response"
    return tool_call_id


def _get_generated_code_output(websocket: Any) -> str:
    iterations = 0
    result = ""
    while iterations < 1000:
        json = websocket.receive_json()
        if mutation := json.get("mutation"):
            mutation_type = mutation["type"]
            if mutation_type == "AppendToContentMessageMutation":
                result += mutation["content_delta"]
            elif mutation_type == "LockReleasedMutation" and result:
                break
        iterations += 1

    if not result:
        raise Exception("Generated code output not found in response")
    return result


def _wait_for_websocket_response(response_type: str, websocket: Any) -> None:
    tries_count = 0
    while tries_count < 100:
        json = websocket.receive_json()
        if json["type"] == response_type:
            return
        tries_count += 1
        sleep(0.1)

    raise Exception(f"Response of type {response_type} not received")
