import logging

import rtoml
from sqlalchemy.orm import Session

from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType
from aiconsole.core.database.config import DatabaseConfig
from aiconsole.core.database.models import MaterialContentType, MaterialDB
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_project_assets_directory,
)

_log = logging.getLogger(__name__)


def migrate_from_filesystem(db: Session):
    """Migrate materials from filesystem to database."""

    core_materials_dir = get_core_assets_directory(AssetType.MATERIAL)
    project_materials_dir = get_project_assets_directory(AssetType.MATERIAL)

    for materials_dir in [core_materials_dir, project_materials_dir]:
        if not materials_dir.exists():
            continue

        is_core = materials_dir == core_materials_dir

        for toml_file in materials_dir.glob("*.toml"):
            try:

                with open(toml_file, "r", encoding="utf-8") as f:
                    data = rtoml.load(f)

                material_data = {
                    "id": toml_file.stem,
                    "name": data["name"],
                    "version": data.get("version", "0.0.1"),
                    "usage": data["usage"],
                    "defined_in": AssetLocation.AICONSOLE_CORE if is_core else AssetLocation.PROJECT_DIR,
                    "content_type": MaterialContentType(data["content_type"]),
                    "content": data.get("content", ""),
                    "default_status": AssetStatus(data.get("default_status", "enabled")),
                    "usage_examples": data.get("usage_examples", []),
                }

                material = MaterialDB.from_dict(material_data)
                db.merge(material)

                _log.info(f"Migrated material: {material.id}")

            except Exception as e:
                _log.error(f"Error migrating material from {toml_file}: {str(e)}")
                continue

    db.commit()


def run_migrations():
    """Run all database migrations."""
    db_config = DatabaseConfig()

    db_config.create_tables()

    db = db_config.SessionLocal()

    try:
        migrate_from_filesystem(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_migrations()
