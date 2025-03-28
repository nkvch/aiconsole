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



def commit_to_dict(commit):
    """serializes commit data"""
    return {
        "commit": commit.hexsha[:7],
        "author": commit.author.name,
        "email": commit.author.email,
        "date": commit.committed_datetime.isoformat(),
        "message": commit.message.strip()
    }


def get_changelog_sync(directory: Path) -> list[dict]:
    """
    Synchronously retrieves the changelog for a material from a Git repository.
    """
    try:
        repo = Repo(directory)
        return [commit_to_dict(commit) for commit in repo.iter_commits()]

    except GitCommandError as e:
        raise RuntimeError(f"Git error: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve changelog: {e}")


async def get_changelog_async(directory: Path) -> str:
    """Asynchronous wrapper for get_changelog_sync"""
    return await asyncio.to_thread(get_changelog_sync, directory)
