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
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import Asset
from aiconsole.core.db.database import db_provider
from aiconsole.core.db.models import Material as db_model_material
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

    if isinstance(asset, AICAgent):
        # Save to .toml file
        with (path / f"{asset.id}.toml").open("w", encoding="utf8", errors="replace") as file:
            # FIXME: preserve formatting and comments in the file using tomlkit

            model_dump = asset.model_dump(exclude_none=True)

            doc = tomlkit.document()
            doc.append("name", tomlkit.string(asset.name))
            doc.append("version", tomlkit.string(asset.version))
            doc.append("usage", tomlkit.string(asset.usage))
            doc.append("usage_examples", tomlkit.item(asset.usage_examples))
            doc.append("default_status", tomlkit.string(asset.default_status))
            doc.append("system", tomlkit.string(asset.system))
            doc.append("gpt_mode", tomlkit.string(asset.gpt_mode))
            doc.append("execution_mode", tomlkit.string(asset.execution_mode))
            
            file.write(doc.as_string())

        extensions = [".jpeg", ".jpg", ".png", ".gif", ".SVG"]
        for extension in extensions:
            old_file_path = get_core_assets_directory(asset.type) / f"{old_asset_id}{extension}"
            new_file_path = path / f"{asset.id}{extension}"
            if old_file_path.exists():
                shutil.copy(old_file_path, new_file_path)

    if isinstance(asset, Material):
        material: Material = asset

        session = db_provider.SessionLocal()
        try:
            model = db_model_material(
                id=material.id,
                name=material.name,
                version=material.version,
                usage=material.usage,
                usage_examples=material.usage_examples,
                default_status=material.default_status,
                content_type=material.content_type
            )

            {
                MaterialContentType.STATIC_TEXT: lambda: setattr(model, "content_static_text", material.content),
                MaterialContentType.DYNAMIC_TEXT: lambda: setattr(model, "content_api", material.content),
                MaterialContentType.API: lambda: setattr(model, "content_api", material.content),
            }[material.content_type]()

            session.add(model)
            session.commit()
        finally:
            session.close()
            
    return asset
