from datetime import datetime
from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo


def get_or_init_repo(materials_path: Path) -> Repo:
    try:
        return Repo(materials_path)
    except InvalidGitRepositoryError:
        print(f"[Git] No repo found in {materials_path}, initializing new repo.")
        return Repo.init(materials_path)


def commit_material_change(materials_path: Path, file_path: Path, message: str = None):
    repo = get_or_init_repo(materials_path)
    relative_path = file_path.relative_to(materials_path)

    try:
        repo.index.add([str(relative_path)])
        commit_message = message or f"Auto-commit: updated {relative_path} at {datetime.now().isoformat()}"
        repo.index.commit(commit_message)
        print(f"[Git] ✅ Committed: {commit_message}")
    except GitCommandError as e:
        print(f"[Git] ⚠️ Skipped commit for {relative_path}: {e}")


def get_material_changelog(materials_path: Path, file_path: Path) -> list[dict]:
    try:
        repo = Repo(materials_path)
    except InvalidGitRepositoryError:
        print(f"[Git] ❌ No repo found in {materials_path}, cannot get changelog.")
        return []

    relative_path = file_path.relative_to(materials_path)

    try:
        commits = list(repo.iter_commits(paths=str(relative_path)))
    except GitCommandError:
        print(f"[Git] ❌ No commits found for {relative_path}.")
        return []

    return [
        {
            "timestamp": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
            "commit_id": commit.hexsha[:7],
        }
        for commit in commits
    ]


def find_existing_material_file(materials_path: Path, material_id: str) -> Path | None:
    for ext in [".toml", ".txt", ".py"]:
        candidate = materials_path / f"{material_id}{ext}"
        if candidate.exists():
            return candidate
    return None
