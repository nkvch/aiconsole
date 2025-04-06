import os
import subprocess
from pathlib import Path
from typing import List, Dict

DEFAULT_MATERIALS_PATH = Path(__file__).parent.parent / "materials/"


def init_git_repo():
    if not (DEFAULT_MATERIALS_PATH / ".git").exists():
        DEFAULT_MATERIALS_PATH.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init'], cwd=DEFAULT_MATERIALS_PATH, check=True)


def get_changelog() -> List[Dict[str, str]]:
    repo_path = find_git_root()
    rel_path = os.path.relpath(DEFAULT_MATERIALS_PATH, repo_path)
    result = subprocess.run(
        [
            'git', 'log', '--pretty=format:%H%x09%an%x09%ad%x09%s', '--date=iso', '--', rel_path
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )
    changelog = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) == 4:
            commit_hash, author, date, message = parts
            changelog.append({
                'commit': commit_hash,
                'author': author,
                'date': date,
                'message': message
            })
    return changelog



def find_git_root() -> str:
    path = os.path.abspath(DEFAULT_MATERIALS_PATH)
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, '.git')):
            return path
        path = os.path.dirname(path)
    raise FileNotFoundError("No git repository found in hierarchy.")
