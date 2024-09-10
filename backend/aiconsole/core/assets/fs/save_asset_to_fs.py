# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import shutil

import tomlkit

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.fs.db.database import MaterialNotFoundError, MaterialsService
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.fs.load_asset_from_fs import (
    load_asset_from_fs,
    load_material_for_project,
)
from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import Asset
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)

_USER_AGENT_ID = "user"


async def save_asset_to_fs(asset: Asset, old_asset_id: str) -> Asset:
    if isinstance(asset, AICAgent):
        if asset.id == _USER_AGENT_ID:
            raise UserIsAnInvalidAgentIdError()

    path = get_project_assets_directory(asset.type)

    try:
        current_version = (await load_asset_from_fs(asset.type, asset.id)).version
    except KeyError:
        current_version = "0.0.1"

    # Parse version number
    current_version_parts = current_version.split(".")

    # Increment version number
    current_version_parts[-1] = str(int(current_version_parts[-1]) + 1)

    # Join version number
    asset.version = ".".join(current_version_parts)

    # Save to .toml file
    with (path / f"{asset.id}.toml").open("w", encoding="utf8", errors="replace") as file:
        # FIXME: preserve formatting and comments in the file using tomlkit

        model_dump = asset.model_dump(exclude_none=True)

        doc = prepare_doc(asset)

        file.write(doc.as_string())

    extensions = [".jpeg", ".jpg", ".png", ".gif", ".SVG"]
    for extension in extensions:
        old_file_path = get_core_assets_directory(asset.type) / f"{old_asset_id}{extension}"
        new_file_path = path / f"{asset.id}{extension}"
        if old_file_path.exists():
            shutil.copy(old_file_path, new_file_path)

    return asset


async def save_material(asset: Asset, project_id: str, old_file_name: str, service: MaterialsService) -> Asset:
    try:
        old_asset = await load_material_for_project(service, project_id, old_file_name)
    except MaterialNotFoundError:
        old_asset = None

    if old_asset is not None:
        current_version = old_asset.version
    else:
        current_version = "0.0.1"

    # Parse version number
    current_version_parts = current_version.split(".")

    # Increment version number
    current_version_parts[-1] = str(int(current_version_parts[-1]) + 1)

    # Join version number
    asset.version = ".".join(current_version_parts)

    doc = prepare_doc(asset)

    if old_asset is None:
        service.add_file(project_id, asset.id, doc.as_string())
    else:
        service.edit_file(project_id, old_file_name, doc.as_string(), asset.id)

    return asset


def prepare_doc(asset: Asset):
    def make_sure_starts_and_ends_with_newline(s: str):
        if not s.startswith("\n"):
            s = "\n" + s

        if not s.endswith("\n"):
            s = s + "\n"

        return s

    doc = tomlkit.document()
    doc.append("name", tomlkit.string(asset.name))
    doc.append("version", tomlkit.string(asset.version))
    doc.append("usage", tomlkit.string(asset.usage))
    doc.append("usage_examples", tomlkit.item(asset.usage_examples))
    doc.append("default_status", tomlkit.string(asset.default_status))

    if isinstance(asset, Material):
        material: Material = asset

        doc.append("content_type", tomlkit.string(asset.content_type))

        {
            MaterialContentType.STATIC_TEXT: lambda: doc.append(
                "content_static_text",
                tomlkit.string(
                    make_sure_starts_and_ends_with_newline(material.content),
                    multiline=True,
                ),
            ),
            MaterialContentType.DYNAMIC_TEXT: lambda: doc.append(
                "content_dynamic_text",
                tomlkit.string(
                    make_sure_starts_and_ends_with_newline(material.content),
                    multiline=True,
                ),
            ),
            MaterialContentType.API: lambda: doc.append(
                "content_api",
                tomlkit.string(
                    make_sure_starts_and_ends_with_newline(material.content),
                    multiline=True,
                ),
            ),
        }[asset.content_type]()

    if isinstance(asset, AICAgent):
        doc.append("system", tomlkit.string(asset.system))
        doc.append("gpt_mode", tomlkit.string(asset.gpt_mode))
        doc.append("execution_mode", tomlkit.string(asset.execution_mode))

    return doc
