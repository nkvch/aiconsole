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
    # Get both core and project materials directories
    core_materials_dir = get_core_assets_directory(AssetType.MATERIAL)
    project_materials_dir = get_project_assets_directory(AssetType.MATERIAL)

    # Process both directories
    for materials_dir in [core_materials_dir, project_materials_dir]:
        if not materials_dir.exists():
            continue

        # Determine if this is core or project materials
        is_core = materials_dir == core_materials_dir

        # Process all .toml files
        for toml_file in materials_dir.glob("*.toml"):
            try:
                # Read TOML file
                with open(toml_file, "r", encoding="utf-8") as f:
                    data = rtoml.load(f)

                # Convert to database model
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

                # Create or update material in database
                material = MaterialDB.from_dict(material_data)
                db.merge(material)

                _log.info(f"Migrated material: {material.id}")

            except Exception as e:
                _log.error(f"Error migrating material from {toml_file}: {str(e)}")
                continue

    # Commit all changes
    db.commit()


def run_migrations():
    """Run all database migrations."""
    db_config = DatabaseConfig()

    # Create tables if they don't exist
    db_config.create_tables()

    # Get database session
    db = db_config.SessionLocal()

    try:
        # Run filesystem to database migration
        migrate_from_filesystem(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_migrations()
