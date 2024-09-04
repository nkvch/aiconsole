from typing import List
from fastapi import HTTPException

from sqlalchemy.orm import Session
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.types import AssetLocation
from aiconsole.core.assets.materials.db_model import DbMaterial, DbMaterialUpdateSchema


# CRUD operations
def _create_material_db(db: Session, material: Material):
    db_material = DbMaterial(**material.model_dump_filtered(DbMaterial))
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def _get_material_db(db: Session, id: str):
    orm_material = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if orm_material is not None:
        return Material.from_orm_with_defaults(orm_material)
    else: 
        return orm_material

def _get_materials_db(db: Session, skip: int = 0, limit: int = 100):
    orm_materials: List[DbMaterial] = db.query(DbMaterial).offset(skip).limit(limit).all()
    return [
        Material.from_orm_with_defaults(material) 
        for material in orm_materials
        ]

def _delete_material_db(db: Session, id: str):
    db_material = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if db_material:
        db.delete(db_material)
        db.commit()
    return db_material

def _patch_material_db(db: Session, old_id: str, material_update: DbMaterialUpdateSchema):
    db_material = db.query(DbMaterial).filter(DbMaterial.id == old_id).first()

    if db_material is None:
        return None

    # Update only the fields provided in the request
    if material_update.id is not None:
        db_material.id = material_update.id
    if material_update.name is not None:
        db_material.name = material_update.name
    if material_update.content_type is not None:
        db_material.content_type = material_update.content_type
    if material_update.status is not None:
        db_material.status = material_update.status
    if material_update.usage is not None:
        db_material.usage = material_update.usage
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

def _material_exists(db: Session, location:AssetLocation, material_id: str) -> bool:
    if material_id == 'new':
        return False
    
    # FIXME this logic is simplified.
    # Focus was on database - here called PROJECT_DIR which is inaccurate
    if location == AssetLocation.AICONSOLE_CORE:
        return True
    elif location == AssetLocation.PROJECT_DIR:
        material = _get_material_db(db, material_id)

    return (material is not None)
