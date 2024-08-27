# aiconsole/schemas/material.py

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class DefinedInEnum(str, Enum):
    AICONSOLE = "aiconsole"
    PROJECT = "project"


class TypeEnum(str, Enum):
    AGENT = "agent"
    MATERIAL = "material"


class StatusEnum(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    FORCED = "forced"


class ContentTypeEnum(str, Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"


class MaterialCreate(BaseModel):
    name: str
    version: Optional[str] = "0.0.1"
    usage: str
    usage_examples: Optional[List[str]] = []
    defined_in: DefinedInEnum
    type: Optional[TypeEnum] = TypeEnum.MATERIAL
    default_status: Optional[StatusEnum] = StatusEnum.ENABLED
    status: Optional[StatusEnum] = StatusEnum.ENABLED
    override: bool
    content_type: Optional[ContentTypeEnum] = ContentTypeEnum.STATIC_TEXT
    content: Optional[str] = ""

    class Config:
        from_attributes = True


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    usage: Optional[str] = None
    usage_examples: Optional[List[str]] = None
    defined_in: Optional[DefinedInEnum] = None
    type: Optional[TypeEnum] = None
    default_status: Optional[StatusEnum] = None
    status: Optional[StatusEnum] = None
    override: Optional[bool] = None
    content_type: Optional[ContentTypeEnum] = None
    content: Optional[str] = None

    class Config:
        from_attributes = True


class MaterialResponse(MaterialCreate):
    id: int
