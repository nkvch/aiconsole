import json
import uuid
from datetime import datetime
from pathlib import Path

import aiofiles
import aiofiles.os as async_os

from aiconsole.core.assets.types import AssetLocation
from aiconsole.core.chat.types import AICChatOptions
from aiconsole.core.project.paths import get_history_directory


async def load_chat_options(id: str, project_path: Path | None = None) -> AICChatOptions:
    if id == "new":
        raise ValueError("Cannot load chat options with id 'new'")

    history_directory = get_history_directory(project_path)
    file_path = history_directory / f"{id}.json"

    if await async_os.path.exists(file_path):
        async with aiofiles.open(file_path, mode="r", encoding="utf8", errors="replace") as f:
            data = json.loads(await f.read())

            if "chat_options" in data:
                return AICChatOptions(**data["chat_options"])
            
    return AICChatOptions()
