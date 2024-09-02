from fastapi import HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional

from sqlalchemy.orm import sessionmaker, Session
from aiconsole.core.assets.materials.db_model import DbMaterial

# Pydantic schemas were required by the environment 
# Also Pydantic Models make endpoints developement more managable and scalable
# ChatGPT advised me to create separate schema for patch method. 
# All fields are optional there and only non-None are used to update

class DbMaterialSchema(BaseModel):
    id: Optional[str] = Field(None, description="Primary key")
    name: str = Field(..., description="Unique name of the material")
    version: str
    usage: Optional[str] = None
    usage_examples: str
    defined_in: Optional[str] = None
    type: Optional[str] = 'material'
    default_status: str
    status: str
    content_type: str = Field(..., description="Type of the material")
    content: str

    class Config:
        from_attributes = True

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
    usage_examples: Optional[str] = None
    defined_in: Optional[str] = None
    type: Optional[str] = None
    default_status: Optional[str] = None
    status: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None

    class Config:
        from_attributes = True

# CRUD operations
def _create_material_db(db: Session, material: DbMaterialSchema):
    db_material = DbMaterial(**material.model_dump())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def _get_material_db(db: Session, name: str):
    return db.query(DbMaterial).filter(DbMaterial.name == name).first()

def _get_materials_db(db: Session, skip: int = 0, limit: int = 10):
    return db.query(DbMaterial).offset(skip).limit(limit).all()

def _update_material_db(db: Session, name: str, content: str):
    db_material = db.query(DbMaterial).filter(DbMaterial.name == name).first()
    if db_material:
        db_material.content = content
        db.commit()
        db.refresh(db_material)
    return db_material

def _delete_material_db(db: Session, name: str):
    db_material = db.query(DbMaterial).filter(DbMaterial.name == name).first()
    if db_material:
        db.delete(db_material)
        db.commit()
    return db_material

def _patch_material_db(db: Session, name: str, material_update: DbMaterialUpdateSchema):
    db_material = db.query(DbMaterial).filter(DbMaterial.name == name).first()

    if db_material is None:
        return None

    # Update only the fields provided in the request
    if material_update.name is not None:
        db_material.name = material_update.name
    if material_update.material_type is not None:
        db_material.material_type = material_update.material_type
    if material_update.enabled is not None:
        db_material.enabled = material_update.enabled
    if material_update.content is not None:
        db_material.content = material_update.content

    db.commit()
    db.refresh(db_material)

    return db_material

def _set_material_status(db: Session, material_id: str, status: str):
    db_material = db.query(DbMaterial).filter(DbMaterial.id == material_id).first()
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    
    db_material.status = status
    db.commit()
    db.refresh(db_material)
    return db_material