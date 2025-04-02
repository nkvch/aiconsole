import os

from git import Repo

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project.paths import (
    get_project_assets_directory,
)


def is_git_dir(path: str) -> bool:
    return os.path.isdir(os.path.join(path, ".git"))


def get_repo():
    materials_path = get_project_assets_directory(AssetType.MATERIAL)

    if is_git_dir(materials_path):
        repo = Repo(materials_path)
    else:
        repo = Repo.init(materials_path)
        repo.index.commit("Init commit")
    return repo


def get_material_path(material_id: str):
    return f"{material_id}.toml"


def get_changelog_of_material(material_id: str):
    repo = get_repo()
    path = get_material_path(material_id)
    changelog = []

    last_commit = list(repo.iter_commits(all=True))[-1]
    commits_for_file = list(repo.iter_commits(all=True, paths=path))

    for commit in commits_for_file[::-1]:
        diff_summary = repo.git.diff(last_commit, commit, path).split("\n")[5:]
        changelog.append(
            {
                "date": commit.committed_datetime,
                "message": commit.message.strip(),
                "diff": [diff for diff in diff_summary if diff[0] == "+" or diff[0] == "-"],
            }
        )
        last_commit = commit

    return changelog


def update_material(material_id: str):
    repo = get_repo()

    repo.index.add([get_material_path(material_id)])
    repo.index.commit(f"Update material {material_id}")


def rename_material(old_material_id: str, new_material_id: str):
    repo = get_repo()

    repo.index.remove([get_material_path(old_material_id)])
    repo.index.add([get_material_path(new_material_id)])
    repo.index.commit(f"Rename material from {old_material_id} to {new_material_id}")


def create_material(material_id: str):
    repo = get_repo()

    repo.index.add([get_material_path(material_id)])
    repo.index.commit(f"Create material {material_id}")


def delete_material(material_id: str):
    repo = get_repo()

    repo.index.remove([get_material_path(material_id)])
    repo.index.commit(f"Delete material {material_id}")
