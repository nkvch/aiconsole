import os
from pathlib import Path

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.fs.load_asset_from_fs import load_asset_from_fs
from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import Asset, AssetLocation, AssetStatus, AssetType
from aiconsole.core.db.database import db_provider
from aiconsole.core.db.models import Material as material_model_db
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)


async def load_all_assets(asset_type: AssetType) -> dict[str, list[Asset]]:
    _assets: dict[str, list[Asset]] = {}

    session = db_provider.SessionLocal()
    
    try:
        materials = session.query(material_model_db).all()

        for material in materials:

            params = {
                "id": material.id,
                "name": material.name,
                "version": material.version or "0.0.1",
                "defined_in": AssetLocation.PROJECT_DIR,
                "usage": material.usage or "",
                "usage_examples": material.usage_examples or [],
                "default_status": AssetStatus(material.default_status if material.default_status else "enabled"),
                "override": False,
            }

            mat = Material(
                **params,
                content_type=MaterialContentType(material.content_type),
            )

            if material.content:
                mat.content = material.content

            if material.content_static_text and material.content_type == MaterialContentType.STATIC_TEXT:
                mat.content = material.content_static_text

            if material.content_dynamic_text and material.content_type == MaterialContentType.DYNAMIC_TEXT:
                mat.content = material.content_dynamic_text

            if material.content_api and material.content_type == MaterialContentType.API:
                mat.content = material.content_api

            # Legacy support (for v. prior to 0.2.11)
            if Assets.get_status(AssetType.MATERIAL, str(mat.id)) == AssetStatus.FORCED:
                Assets.set_status(AssetType.MATERIAL, str(mat.id), AssetStatus.ENABLED)

            if mat not in _assets:
                _assets[str(mat.id)] = []
            _assets[str(mat.id)].append(mat)
    finally:
        session.close()
        
    return _assets
