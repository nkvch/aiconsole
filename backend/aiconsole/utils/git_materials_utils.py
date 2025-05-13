from git import Repo, GitCommandError
from pathlib import Path
from typing import Optional, List

class GitMaterialRepo:
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.repo = self._load_or_init_repo()

    def _load_or_init_repo(self) -> Repo:
        if not (self.repo_path / ".git").exists():
            return Repo.init(self.repo_path)
        return Repo(self.repo_path)

    def get_active_branch(self) -> str:
        return self.repo.active_branch.name

    def checkout_or_create_branch(self, branch_name: str):
        if branch_name in self.repo.heads:
            self.repo.git.checkout(branch_name)
        else:
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()

    def commit_file(self, relative_path: str, message: str = "Updated material"):
        file_path = self.repo_path / relative_path
        if file_path.exists():
            self.repo.index.add([str(file_path)])
            self.repo.index.commit(message)
        else:
            raise FileNotFoundError(f"{file_path} does not exist")

    def get_file_changelog(self, relative_path: str) -> List[dict]:
        commits = list(self.repo.iter_commits(paths=relative_path))
        return [
            {
                "hash": commit.hexsha,
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": commit.committed_datetime.isoformat()
            }
            for commit in commits
        ]

    def is_git_repo(self) -> bool:
        return (self.repo_path / ".git").exists()

    def status(self) -> str:
        return self.repo.git.status()

    def has_uncommitted_changes(self) -> bool:
        return self.repo.is_dirty()