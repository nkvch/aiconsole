from typing import List
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel

from aiconsole.core.assets.materials.material import MaterialContentType
from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType


class MaterialBase(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    version: str = "0.0.1"
    usage: str
    defined_in: AssetLocation
    default_status: AssetStatus = AssetStatus.ENABLED
    status: AssetStatus = AssetStatus.ENABLED
    content_type: MaterialContentType = MaterialContentType.STATIC_TEXT
    content: str = ""
    override: bool = False
    type: AssetType = AssetType.MATERIAL


class UsageExample(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    material_id: str = Field(foreign_key="materialdb.id")
    example: str
    material: "MaterialDB" = Relationship(back_populates="usage_examples")


class MaterialDB(MaterialBase, table=True):
    usage_examples: List[UsageExample] = Relationship(back_populates="material")
