import logging
from pathlib import Path

from aiconsole.core.project.paths import (
    get_core_assets_directory,
)

_log = logging.getLogger(__name__)


def copy_file_content(content):
    try:
        content_file_path = Path(content[len("file://") :])

        if content_file_path.is_absolute():
            if not content_file_path.exists():
                raise FileNotFoundError(f"File {content_file_path} does not exist.")
        else:
            #  Content_file path is relative. If material is default, only .toml file is copied to project
            #  directory, so content_file is not found. If material is in project, then content_file is found.
            core_resource_path = get_core_assets_directory()
            
            if (core_resource_path / content_file_path).exists():
                content_file_path = core_resource_path / content_file_path
            else:
                raise FileNotFoundError(f"File {content_file_path} does not exist in project and in core.")

        with open(content_file_path, "r", encoding="utf8", errors="replace") as file:
            return file.read()

    except Exception as e:
        _log.error(f"Error while reading file content: {e}")
        return content
