from enum import Enum
from typing import List

from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import relationship

from aiconsole.core.assets.types import AssetLocation, AssetStatus
from aiconsole.core.database.config import Base


class MaterialContentType(str, Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"


class MaterialDB(Base):
    __tablename__ = "materials"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False, default="0.0.1")
    usage = Column(String, nullable=False)
    defined_in = Column(SQLEnum(AssetLocation), nullable=False)
    content_type = Column(SQLEnum(MaterialContentType), nullable=False)
    content = Column(String, nullable=False)
    default_status = Column(SQLEnum(AssetStatus), nullable=False, default=AssetStatus.ENABLED)
    usage_examples = Column(JSON, nullable=True, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "usage": self.usage,
            "defined_in": self.defined_in,
            "content_type": self.content_type,
            "content": self.content,
            "default_status": self.default_status,
            "usage_examples": self.usage_examples or [],
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            version=data.get("version", "0.0.1"),
            usage=data["usage"],
            defined_in=data["defined_in"],
            content_type=data["content_type"],
            content=data["content"],
            default_status=data.get("default_status", AssetStatus.ENABLED),
            usage_examples=data.get("usage_examples", []),
        )
