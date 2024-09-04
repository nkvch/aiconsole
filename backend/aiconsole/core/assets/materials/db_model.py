from pydantic import BaseModel
from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional

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
    
class DbMaterialUpdateSchema(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    usage: Optional[str] = None
    usage_examples: Optional[List[str]] = None
    defined_in: Optional[str] = None
    type: Optional[str] = None
    default_status: Optional[str] = None
    status: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    override: Optional[bool] = None

    class Config:
        from_attributes = True

