from typing import List, Optional

from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import validator
import uuid
from aiconsole.core.assets.materials.material import Material, MaterialBase

class MaterialDB(SQLModel, MaterialBase, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(unique=True)
    usage_examples: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    @validator("id", pre=True, always=True)
    def validate_id(cls, v):
        if v is None:
            return str(uuid.uuid4())
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("The ID must be a valid UUID")

def material_to_db(material: Material) -> MaterialDB:
    return MaterialDB(
        name=material.name,
        id=material.id,
        version=material.version,
        usage=material.usage,
        defined_in=material.defined_in,
        type=material.type,
        default_status=material.default_status,
        status=material.status,
        override=material.override,
        usage_examples=material.usage_examples,
        content_type=material.content_type,
        content=material.content,
    )


def db_to_material(db: MaterialDB) -> Material:
    return Material(
        name=db.name,
        id=db.id,
        version=db.version,
        usage=db.usage,
        defined_in=db.defined_in,
        type=db.type,
        default_status=db.default_status,
        status=db.status,
        override=db.override,
        usage_examples=db.usage_examples,
        content_type=db.content_type,
        content=db.content,
    )
