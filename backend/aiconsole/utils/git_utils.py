import logging

import git
import git.exc
from git import Actor
from datetime import datetime
import uuid
from pathlib import Path
from typing import Optional
from aiconsole.core.assets.types import AssetType
from watchdog.events import FileSystemEvent
import pytz


_log = logging.getLogger(__name__)


def is_in_git_repo(file_path: Path) -> bool:
    return (file_path / ".git").exists()

def is_in_materials_folder(file_path: Path) -> bool:
    return file_path.name == 'materials'

def generate_commit_message(event: FileSystemEvent) -> str:
    """
    Generates a message to the commit depending on the type of file event.
    """
    event_type = event.event_type
    file_path = event.src_path

    match event_type:
        case "created":
            return f"📄 Created file: {file_path}"
        case "modified":
            return f"✏️ Modified file: {file_path}"
        case "deleted":
            return f"🗑️ Deleted file: {file_path}"
        case "moved":
            return f"📦 Moved file: {event.src_path} → {getattr(event, 'dest_path', 'UNKNOWN')}"
        case _:
            return f"🔧 Changed file: {file_path}"


def advanced_commit(repo, message: str, file_path: Path, event_type: str) -> str:
    """
    An advanced feature for committing changes to a Git repository, with additional information, including a unique ID for the commit.
    """
    commit_date = datetime.now(pytz.utc)
    commit_id = str(uuid.uuid4())
    
    author = Actor(name="AutoVersioner", email="")
    if event_type == "deleted" and not file_path.exists():
        repo.index.remove([file_path])
    elif file_path.is_file():
        repo.index.add([file_path])
    
    commit_message = f"{message} (Commit ID: {commit_id})"
    
    repo.index.commit(
        commit_message,
        author=author,
        committer=author,
        author_date=commit_date,
        commit_date=commit_date,
        skip_hooks=True
    )
    return commit_id


def commit_changes_to_git(event: FileSystemEvent) -> None:
    """
    Commits changes to the Git repository if event is for the materials folder.
    """

    file_path = Path(event.src_path)
    materials_path = file_path.parent

    if not is_in_materials_folder(materials_path) or not is_in_git_repo(materials_path):
        return

    try:
        repo = git.Repo(materials_path)
        message = generate_commit_message(event)
        commit_id = advanced_commit(repo, message, file_path, event_type=event.event_type)

        _log.info(f"Commit ({commit_id}) has been created.")

    except ValueError as e:
        raise ValueError(f"Error: {e}")
    except git.exc.GitCommandError as e:
        raise RuntimeError(f"Git error: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during Git commit: {e}")


def initialize_git(path: Path) -> None:
    """Initialize git in the materials folder."""
    try:
        if not Path(path / ".git").exists():
            git.Repo.init(path)
    except git.exc.GitCommandError as e:
        raise RuntimeError(f"Error initializing Git: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during Git init: {e}")






