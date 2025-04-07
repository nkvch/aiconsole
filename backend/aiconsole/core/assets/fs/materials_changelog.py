import os
from git import Repo
from git import NULL_TREE
from datetime import datetime


MATERIALS_PATH = os.path.abspath("materials")
CHANGELOG_REPO_PATH = os.path.abspath("materials-changelog")


def commit_to_changelog(message: str):
    """Stage and commit changes from the materials
    directory to the changelog repo"""

    repo = materials_changelog_repo_init(CHANGELOG_REPO_PATH)

    # Add relative path from the repo to materials
    rel_materials_path = os.path.relpath(MATERIALS_PATH,
                                         CHANGELOG_REPO_PATH)
    repo.index.add([rel_materials_path])
    repo.index.commit(message)


def materials_changelog_repo_init(repo_path) -> Repo:
    """GitPython repo init in materials-changelog"""

    if not os.path.exists(repo_path):
        os.makedirs(repo_path, exist_ok=True)

    git_dir = os.path.join(repo_path, ".git")
    
    if not os.path.exists(git_dir):
        repo = Repo.init(repo_path)
    else:
        repo = Repo(repo_path)

    return repo


def get_changelog(material_id: str):
    if not os.path.exists(CHANGELOG_REPO_PATH):
        return []
    repo = Repo(CHANGELOG_REPO_PATH)
    commits = list(repo.iter_commits("master"))
    commits = filter_out_wrong_ids(commits, material_id + ".toml")
    changelog = []
    for commit in commits:
        full_diff_text = create_full_diff_text(commit)

        changelog.append({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
            "message": commit.message,
            "diff" : full_diff_text
        })
    return changelog
    

def create_full_diff_text(commit):
    """Returns merged diff comments (+, - and other)"""

    if commit.parents:
        diff_index = commit.diff(commit.parents[0], create_patch=True)
    else:
        diff_index = commit.diff(NULL_TREE, create_patch=True)

    full_diff_text = ""
    for diff in diff_index:
        try:
            full_diff_text += diff.diff.decode("utf-8", errors="ignore")
            full_diff_text = strip_4th_sign(full_diff_text, '@')
        except Exception as e:
            full_diff_text += f"--- Diff could not be decoded: {e} ---\n"
    return full_diff_text


def strip_4th_sign(message, sign):
    count = 0
    for i, char in enumerate(message):
        if char == sign:
            count += 1
            if count == 4:
                return message[i+1:]
    return message[count+1:]


def filter_out_wrong_ids(commits, material_id: str):
    """Returns list of commits for only
    passed specific material_id"""

    commits = [commit for commit in commits
            if (
                material_id in (commit.message.decode('utf-8')
                if isinstance(commit.message, (bytes, bytearray))
                else commit.message)
                )
            ]
    return commits
