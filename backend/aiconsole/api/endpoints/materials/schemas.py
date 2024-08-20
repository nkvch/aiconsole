from pydantic import BaseModel
from typing import List, Optional
import enum

class MaterialContentType(str, enum.Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"

class MaterialBase(BaseModel):
    name: str
    version: Optional[str] = None
    usage: Optional[str] = None
    usage_examples: Optional[List[str]] = []
    content_type: MaterialContentType
    content: Optional[str] = None
    content_static_text: Optional[str] = None
    default_status: Optional[str] = "enabled"

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(MaterialBase):
    pass

class MaterialOut(MaterialBase):
    id: int

    class Config:
        from_attributes = True
