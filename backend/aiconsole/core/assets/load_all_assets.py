import os
from pathlib import Path

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
from aiconsole.core.assets.types import Asset, AssetLocation, AssetStatus, AssetType
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)
from aiconsole.utils.list_files_in_file_system import list_files_in_file_system
from aiconsole.core.assets.materials.save_materials_to_db import save_materials_to_db
from aiconsole.database.models import MaterialDB


async def load_all_assets(asset_type: AssetType) -> dict[str, list[Asset]]:
    _assets: dict[str, list[Asset]] = {}
    material_assets: list[MaterialDB] = []

    locations = [
        [AssetLocation.PROJECT_DIR, get_project_assets_directory(asset_type)],
        [AssetLocation.AICONSOLE_CORE, get_core_assets_directory(asset_type)],
    ]

    for [location, dir] in locations:
        ids = set(
            [
                os.path.splitext(os.path.basename(path))[0]
                for path in list_files_in_file_system(dir)
                if os.path.splitext(Path(path))[-1] == ".toml"
            ]
        )

        for id in ids:
            try:
                asset = await load_asset_from_fs(asset_type, id, location)

                if asset_type == AssetType.MATERIAL and location == AssetLocation.AICONSOLE_CORE:
                    material_db = MaterialDB(**asset.model_dump())
                    material_assets.append(material_db)

                # Legacy support (for v. prior to 0.2.11)
                if Assets.get_status(asset.type, asset.id) == AssetStatus.FORCED:
                    Assets.set_status(asset.type, asset.id, AssetStatus.ENABLED)

                if id not in _assets:
                    _assets[id] = []
                _assets[id].append(asset)
            except Exception as e:
                await connection_manager().send_to_all(
                    ErrorServerMessage(
                        error=f"Invalid {asset_type} {id} {e}",
                    )
                )
                continue
    if material_assets:
        await save_materials_to_db(material_assets)
    return _assets
