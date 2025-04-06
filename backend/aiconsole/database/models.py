from sqlmodel import SQLModel, Field
from typing import Optional, TypeAlias
from datetime import datetime
from uuid import UUID, uuid4


from aiconsole.core.assets.types import AssetType, AssetLocation, AssetStatus
from aiconsole.core.assets.materials.material import MaterialContentType
MaterialId: TypeAlias = UUID


class MaterialBase(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    version: str = "0.0.1"
    usage: str
    usage_examples: list[str] = Field(default_factory=list)
    defined_in: AssetLocation
    default_status: AssetStatus = AssetStatus.ENABLED
    status: AssetStatus = AssetStatus.ENABLED
    content_type: MaterialContentType = MaterialContentType.STATIC_TEXT
    content: str = ""
    override: bool = False
    type: AssetType = AssetType.MATERIAL


class MaterialDB(MaterialBase, table=True):
    ...
