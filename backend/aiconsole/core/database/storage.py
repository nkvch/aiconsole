from sqlalchemy import select

from aiconsole.core.adapters.material import Adapter, EditableObjectType
from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import AssetLocation, AssetStatus, EditableObject
from aiconsole.core.database.config import DatabaseConfig
from aiconsole.core.database.models import MaterialDB


class DatabaseStorageAdapter(Adapter):
    def __init__(self):
        super().__init__(id="database", name="Database Storage", defined_in=AssetLocation.PROJECT_DIR)
        self._db_config = DatabaseConfig()

    async def fetch_objects(self, type: EditableObjectType) -> list[EditableObject]:
        if type != "material":
            return []

        db = self._db_config.SessionLocal()
        try:
            # Query all materials
            stmt = select(MaterialDB)
            result = db.execute(stmt)
            materials = result.scalars().all()

            # Convert to domain objects
            return [self._db_to_domain(material) for material in materials]
        finally:
            db.close()

    async def fetch_object(self, type: EditableObjectType, id: str) -> EditableObject:
        if type != "material":
            raise ValueError(f"Unsupported object type: {type}")

        db = self._db_config.SessionLocal()
        try:
            # Query specific material
            stmt = select(MaterialDB).where(MaterialDB.id == id)
            result = db.execute(stmt)
            material = result.scalar_one_or_none()

            if material is None:
                raise KeyError(f"Material with id {id} not found")

            return self._db_to_domain(material)
        finally:
            db.close()

    async def save_obj(self, obj: EditableObject):
        if not isinstance(obj, Material):
            raise ValueError(f"Unsupported object type: {type(obj)}")

        db = self._db_config.SessionLocal()
        try:
            # Convert domain object to database model
            db_material = self._domain_to_db(obj)

            # Merge will update if exists, insert if not
            db.merge(db_material)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def delete_obj(self, obj: EditableObject):
        if not isinstance(obj, Material):
            raise ValueError(f"Unsupported object type: {type(obj)}")

        db = self._db_config.SessionLocal()
        try:
            # Find and delete the material
            stmt = select(MaterialDB).where(MaterialDB.id == obj.id)
            result = db.execute(stmt)
            material = result.scalar_one_or_none()

            if material is None:
                raise KeyError(f"Material with id {obj.id} not found")

            db.delete(material)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def _db_to_domain(self, db_material: MaterialDB) -> Material:
        """Convert database model to domain object."""
        # Convert to dict to handle JSON fields properly
        data = db_material.to_dict()

        # Ensure usage_examples is a list of strings
        usage_examples = data["usage_examples"]
        if not isinstance(usage_examples, list):
            usage_examples = []
        usage_examples = [str(example) for example in usage_examples]

        return Material(
            id=str(data["id"]),
            name=str(data["name"]),
            version=str(data["version"]),
            usage=str(data["usage"]),
            defined_in=AssetLocation(data["defined_in"]),
            content_type=MaterialContentType(data["content_type"]),
            content=str(data["content"]),
            default_status=AssetStatus(data["default_status"]),
            usage_examples=usage_examples,
            override=False,  # Default to False for database-stored materials
        )

    def _domain_to_db(self, material: Material) -> MaterialDB:
        """Convert domain object to database model."""
        return MaterialDB(
            id=material.id,
            name=material.name,
            version=material.version,
            usage=material.usage,
            defined_in=material.defined_in,
            content_type=material.content_type,
            content=material.content,
            default_status=material.default_status,
            usage_examples=material.usage_examples,
        )
