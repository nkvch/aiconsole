from pathlib import Path
from aiconsole.core.assets.types import AssetType
from aiconsole.core.assets.assets import get_project_assets_directory


def get_asset_path(asset_type: AssetType, asset_id: str) -> Path:
    if asset_type == AssetType.MATERIAL:
        directory = get_project_assets_directory(asset_type)
        return directory / f"{asset_id}.toml"
    raise ValueError(f"Unsupported asset type: {asset_type}")


def asset_exists_bool(asset_type: AssetType, asset_id: str) -> bool:
    return get_asset_path(asset_type, asset_id).exists()