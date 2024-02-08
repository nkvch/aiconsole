"""

Example usage:

chat_link = "https://chat.openai.com/share/5fa0b36f-ac97-4660-a648-e9c1ce935744"
import_chat_data(extract_and_format_chat_data(chat_link))

Try to avoid calling writing the entire chat data as a literal parameter for import_chat_data, prefer to extract and pass the parameter as a variable.


"""

import json
import re
import uuid
from datetime import datetime, timezone

import requests

from aiconsole.core.chat.types import Chat


def import_chat_gpt_link(chat_link: str) -> str:
    """
    Imports the chat into AIConsole from a given chat gpt link, returns the chat id.
    The user can access the chat in the following url: /#/chats/{chat_id}. Present it to the user after importing.
    """

    chat_data = extract_and_format_chat_data(chat_link)

    chat = Chat(**chat_data)

    with open(f"./chats/{chat.id}.json", "w") as f:
        json.dump(chat.model_dump(mode="json"), f, indent=4)

    return chat.id


def extract_and_format_chat_data(chat_link: str) -> dict:
    """
    Function to extract and format chat data from a given chat gpt link
    """

    # Send a GET request to the URL
    response = requests.get(chat_link)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch chat data. Status code: {response.status_code}")

    # Parse the HTML content
    chat_content = response.text

    # Extract the JSON data from the script tag
    chat_data_match = re.search(
        r'"linear_conversation":(\[.*?\]),"has_user_editable_context"', chat_content, re.DOTALL
    )

    if not chat_data_match:
        raise Exception("Failed to extract chat data from the HTML content")

    chat_data_json = chat_data_match.group(1)
    chat_data = json.loads(chat_data_json)

    # Format the chat data
    formatted_chat_data = {
        "id": str(uuid.uuid4()),
        "lock_id": None,
        "title_edited": False,
        "name": "Imported Chat",
        "last_modified": datetime.now(timezone.utc).isoformat(),
        "chat_options": {"agent_id": "", "materials_ids": []},
        "message_groups": [],
        "is_analysis_in_progress": False,
    }

    for message in chat_data:
        # Skip system messages
        if "system" in message.get("message", {}).get("author", {}).get("role", ""):
            continue

        # Extract message details
        message_id = message.get("id")
        message_content = "".join(message.get("message", {}).get("content", {}).get("parts", []))

        if not message_content:
            continue

        message_timestamp = datetime.fromtimestamp(
            message.get("message", {}).get("create_time") or 0, tz=timezone.utc
        ).isoformat()
        message_role = message.get("message", {}).get("author", {}).get("role")

        # Create message group
        message_group = {
            "id": str(uuid.uuid4()),
            "actor_id": {"type": "agent" if message_role == "assistant" else "user", "id": str(uuid.uuid4())},
            "role": "assistant" if message_role == "assistant" else "user",
            "task": "",
            "materials_ids": [],
            "messages": [
                {
                    "id": message_id,
                    "timestamp": message_timestamp,
                    "content": message_content,
                    "tool_calls": [],
                    "is_streaming": False,
                }
            ],
            "analysis": "",
        }
        formatted_chat_data["message_groups"].append(message_group)

    return formatted_chat_data
