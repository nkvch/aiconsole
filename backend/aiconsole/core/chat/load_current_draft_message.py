import json
from pathlib import Path
from aiconsole.core.project.paths import get_history_directory


async def load_current_draft_message(id: str, project_path: Path | None = None) -> str | None:
    history_directory = get_history_directory(project_path)
    file_path = history_directory / f"{id}.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf8", errors="replace") as f:
            data = json.load(f)

            if "draft_message" in data:
                return data["draft_message"]
            else:
                return None
    else:
        return None
