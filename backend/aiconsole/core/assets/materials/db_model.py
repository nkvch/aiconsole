from pydantic import BaseModel
from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional

from aiconsole.core.assets.types import AssetType

# sqlalchemy model is created based on json model already existing in the project
Base = declarative_base()

class DbMaterial(Base):
    __tablename__ = 'materials'

    id = Column(Text, primary_key=True, index=True)
    name = Column(Integer, unique=True, index=True)
    version = Column(String)
    usage = Column(String)
    status = Column(Text)
    content_type = Column(Text)
    content = Column(Text)

    __table_args__ = (
        CheckConstraint(
            "content_type IN ('static_text', 'dynamic_text', 'api')", 
            name='type_check'
        ),
    )

