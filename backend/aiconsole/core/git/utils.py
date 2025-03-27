import asyncio
import logging
from pathlib import Path

from git import GitCommandError, Repo

_log = logging.getLogger(__name__)


def init_git_repo(directory: Path) -> None:
    """Initialize a git repository in the given directory if it doesn't exist."""
    if not (directory / ".git").exists():
        try:
            Repo.init(directory)
            _log.info(f"Initialized git repository in {directory}")
        except GitCommandError as e:
            _log.warning(f"Warning: Failed to initialize git repository in {directory}: {e}")
        except Exception as e:
            _log.error(f"Error: {e}")

def commit_sync(directory: Path, message: str) -> None:
    try:
        repo = Repo(directory)
        if repo.is_dirty(untracked_files=True):
            repo.git.add(all=True)
            repo.index.commit(message)
            _log.info(f"Committed changes in {directory} with message: '{message}'")
        else:
            _log.info("No changes to commit.")
    except GitCommandError as e:
        _log.warning(f"Warning: Failed to commit changes in {directory}: {e}")
    except Exception as e:
        _log.error(f"Error: {e}")

async def commit_async(directory: Path, message: str) -> None:
    """Commit changes in the given git repository asynchronously."""
    await asyncio.to_thread(commit_sync, directory, message)

