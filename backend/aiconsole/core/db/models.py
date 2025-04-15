from typing import Optional

from sqlalchemy import Boolean, Column, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from aiconsole.core.db.database import Base


class Material(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, default="0.0.1", nullable=True)
    usage = Column(String, nullable=True)
    usage_examples = Column(ARRAY(String), default=[])
    default_status = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    content_static_text = Column(Text, nullable=True)
    content_dynamic_text = Column(Text, nullable=True)
    content_api = Column(Text, nullable=True)
