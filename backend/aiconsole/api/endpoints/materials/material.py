from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .crud import create_material, get_material, update_material, delete_material
from .database import SessionLocal
from .schemas import MaterialCreate, MaterialUpdate, MaterialOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{asset_id}", response_model=MaterialOut)
async def create_material_endpoint(asset_id: str, material: MaterialCreate, db: Session = Depends(get_db)):
    material_data = material.dict()
    material_data['id'] = asset_id
    return create_material(db, material_data)

@router.get("/{asset_id}", response_model=MaterialOut)
async def get_material_endpoint(asset_id: str, db: Session = Depends(get_db)):
    material = get_material(db, asset_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.patch("/{asset_id}", response_model=MaterialOut)
async def update_material_endpoint(asset_id: str, material: MaterialUpdate, db: Session = Depends(get_db)):
    material_data = material.dict()
    updated_material = update_material(db, asset_id, material_data)
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return updated_material

@router.delete("/{asset_id}", response_model=dict)
async def delete_material_endpoint(asset_id: str, db: Session = Depends(get_db)):
    deleted_material = delete_material(db, asset_id)
    if not deleted_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": "ok"}
