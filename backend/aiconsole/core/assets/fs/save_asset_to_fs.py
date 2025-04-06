
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
import sqlite3

import tomlkit

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.fs.exceptions import UserIsAnInvalidAgentIdError
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
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

    if isinstance(asset, Material):
        material: Material = asset

        # Connect to SQLite database
        conn = sqlite3.connect('local_db_AIConsole.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS asset_info (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        version TEXT,
                        usage TEXT,
                        usage_examples TEXT,
                        default_status TEXT,
                        content TEXT,
                        content_type TEXT,
                        path TEXT
                    )
                ''')

            cursor.execute('SELECT id FROM asset_info where id = ?', (asset.id,))
            table = cursor.fetchall()

            if table:
                cursor.execute('''
                           UPDATE asset_info
                           SET name = ?,
                               version = ?,
                               usage = ?,
                               usage_examples = ?,
                               default_status = ?,
                               content = ?,
                               path = ?
                           WHERE id = ?
                ''', (
                    asset.name,
                    asset.version,
                    asset.usage,
                    str(asset.usage_examples),
                    asset.default_status,
                    material.content,
                    str(path),
                    asset.id
                ))
                conn.commit()
            else:
                cursor.execute('''
                    INSERT INTO asset_info (id, name, version, usage, usage_examples, default_status, content, content_type, path) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                asset.id,
                asset.name,
                asset.version,
                asset.usage,
                str(asset.usage_examples),
                asset.default_status,
                material.content,
                material.content_type,
                str(path)
            ))

            conn.commit()
            cursor.execute('''
                    Select * from asset_info
                ''')
            text = cursor.fetchall()
            print(text)

        except sqlite3.Error as e:
            print(f"An error occurred while saving asset information: {e}")

        finally:
            conn.close()

    elif isinstance(asset, AICAgent):
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

    return asset
