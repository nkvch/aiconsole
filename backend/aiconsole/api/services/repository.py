from sqlalchemy.orm import Session
from aiconsole.models.material import Material


def create_material(db: Session, material_data: dict):
    db_material = Material(**material_data)
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material


def get_material(db: Session, material_id: int):
    return db.query(Material).filter(Material.id == material_id).first()


def update_material(db: Session, material_id: int, material_data: dict):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if db_material:
        for key, value in material_data.items():
            setattr(db_material, key, value)
        db.commit()
        db.refresh(db_material)
    return db_material


def delete_material(db: Session, material_id: int):
    db_material = db.query(Material).filter(Material.id == material_id).first()
    if db_material:
        db.delete(db_material)
        db.commit()
    return db_material

