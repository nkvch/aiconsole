import os
from typing import Optional

from git import Repo

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project.paths import get_project_assets_directory


def _get_repo() -> Optional[Repo]:
    materials_path = get_project_assets_directory(AssetType.MATERIAL)

    if not os.path.exists(materials_path):
        return None

    if os.path.isdir(os.path.join(materials_path, ".git")):
        return Repo(materials_path)

    return Repo.init(materials_path)


def _get_material_filename(material_id: str) -> str:
    return material_id + ".toml"


def update_material_changelog(material_id: str, message: str) -> None:
    repo = _get_repo()
    if repo is None:
        raise RuntimeError("Repository was not initialized.")

    materials_path = get_project_assets_directory(AssetType.MATERIAL)
    material_filename = _get_material_filename(material_id)
    material_path = os.path.join(materials_path, material_filename)

    if os.path.isfile(material_path):
        repo.index.add([material_filename])
    else:
        repo.index.remove([material_filename], working_tree=True)

    repo.index.commit(message)


def get_material_changelog(material_id: str) -> list[dict]:
    repo = _get_repo()
    material_filename = _get_material_filename(material_id)

    commits = list(repo.iter_commits(paths=material_filename))

    changelog = []
    for commit in commits:
        changelog.append(
            {
                "date": commit.committed_datetime.isoformat(),
                "action": commit.message.strip(),
            }
        )

    return changelog
