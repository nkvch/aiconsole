# aiconsole/api/schemas/material.py
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
class MaterialContentType(str, Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"

class AssetStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

class MaterialCreate(BaseModel):
    name: str
    version: str = "0.0.1"
    usage: str
    content_type: MaterialContentType
    content: str
    status: AssetStatus = AssetStatus.ENABLED
    
class Material(MaterialCreate):
    id: int

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    usage: Optional[str] = None
    content_type: Optional[MaterialContentType] = None
    content: Optional[str] = None
    status: Optional[AssetStatus] = None
