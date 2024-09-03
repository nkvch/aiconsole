from sqlalchemy import Boolean, CheckConstraint, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel, Field, validator
from typing import List, Optional

from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType

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


# Pydantic schemas were required by the environment 
# Also Pydantic Models make endpoints developement more managable and scalable
# ChatGPT advised me to create separate schema for patch method. 
# All fields are optional there and only non-None are used to update

class DbMaterialSchema(BaseModel):
    id: Optional[str] = Field(None, description="Primary key")
    name: str = Field(..., description="Unique name of the material")
    version: str
    usage: Optional[str] = None
    usage_examples: Optional[List[str]] = None
    defined_in: Optional[str] = None
    type: Optional[str] = 'material'
    default_status: str
    status: str
    content_type: str = Field(..., description="Type of the material")
    content: str
    override: Optional[bool]

    class Config:
        from_attributes = True
# tables are created in project initialization

    @classmethod
    def from_orm_with_defaults(cls, db_material: DbMaterial):
        # Convert from SQLAlchemy model to Pydantic schema, filling in missing fields
        return cls(
            id=db_material.id,
            name=db_material.name,
            version=db_material.version,
            usage=db_material.usage,
            status=db_material.status,
            content_type=db_material.content_type,
            content=db_material.content,
            # Default values for fields not present in the SQLAlchemy model
            usage_examples=[], 
            type=AssetType.MATERIAL,
            default_status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override = False # because it's retrieved from databae (?)always(?)
        )

    def model_dump_filtered(self, model_class: DeclarativeMeta) -> dict:
        """Dump the model to a dictionary, filtering to include only fields from sqlalchemy model."""
        allowed_fields = {c.key for c in inspect(model_class).mapper.column_attrs}
        model_dict = self.model_dump(by_alias=True)
        filtered_dict = {k: v for k, v in model_dict.items() if k in allowed_fields}
        return filtered_dict


    @validator('content_type')
    def validate_content_type(cls, value):
        allowed_types = ['static_text', 'dynamic_text', 'api']
        if value not in allowed_types:
            raise ValueError(f"Invalid content_type: '{value}'. Must be one of {allowed_types}.")
        return value

    @validator('id', always=True)
    def validate_id(cls, value):
        if value is None:
            raise ValueError("id must be provided.")
        return value

    @validator('name')
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("name must not be empty.")
        return value
    
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

    class Config:
        from_attributes = True

