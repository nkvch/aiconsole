from http.client import OK
from typing import List, Optional, cast
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from aiconsole.api.endpoints.materials.material import get_default_content_for_type
from aiconsole.core.adapters.material import MaterialWithStatus
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import MaterialContentType
from aiconsole.core.assets.types import AssetLocation, AssetStatus
from aiconsole.core.project.paths import get_project_directory
from aiconsole.core.assets.materials.db_crud import (
    DbMaterialSchema,
    DbMaterialUpdateSchema,
    _create_material_db, 
    _delete_material_db, 
    _get_material_db, 
    _get_materials_db,
    _material_exists,
    _patch_material_db,
    _set_material_status, 
    _update_material_db
)

# fastAPI dependency uses current project directory path to initialize connection to the right database

router = APIRouter()

def get_db(project_directory: str = Depends(get_project_directory)):
    db_url = f"sqlite:///{project_directory}/materials.db"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# API Endpoints
@router.post("/{material_id}")
def create_material_db(amterial_id: str, material: DbMaterialSchema, db: Session = Depends(get_db)):
    db_material = _create_material_db(db, material)

# This method mimicks the previous method from material.py. It is accessed with name='new' when creating new material
@router.get("/{material_id}")
def read_material(material_id: str, location='', type = 'static_text', db: Session = Depends(get_db)):
    if material_id == "new":
        material = MaterialWithStatus(
            id="new_material",
            name="New " + get_material_content_name(type),
            content_type=type,
            usage="",
            usage_examples=[],
            status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override=False,
            content=get_default_content_for_type(type),
        )
        material = JSONResponse(material.model_dump(exclude_none=True))
    else:
        material = _get_material_db(db, material_id)
        if material is None:
            raise HTTPException(status_code=404, detail="Material not found")
        return material

@router.get("/", response_model=List[DbMaterialSchema])
def read_materials_db(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return _get_materials_db(db, skip=skip, limit=limit)

@router.put("/{name}", response_model=DbMaterialSchema)
def update_material_db(name: str, content: str, db: Session = Depends(get_db)):
    db_material = _update_material_db(db, name, content)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return db_material

@router.delete("/{material_id}", response_model=DbMaterialSchema)
def delete_material_db(material_id: str, db: Session = Depends(get_db)):
    db_material = _delete_material_db(db, material_id)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return JSONResponse({"status": "ok"})

@router.patch("/{name}")
def patch_material_db(name: str, material_update: DbMaterialUpdateSchema, db: Session = Depends(get_db)):
    rename = _patch_material_db(db, name, material_update)
    if rename is None:
        raise HTTPException(status_code=404, detail="Material not found")
        

@router.post("/materials/{id}/status-change")
async def change_material_status(id: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status field is required")

    db_material = _set_material_status(db, id, status)
    
    return {
        # "id": db_material.id,
        # "name": db_material.name,
        "status": db_material.status
    }

@router.get("/{material_id}/exists")
def material_exists(request: Request, material_id: str, db: Session = Depends(get_db)):
    location_param = request.query_params.get("location", None)
    location = AssetLocation(location_param) if location_param else None

    if not location:
        raise HTTPException(status_code=400, detail="Location not specified")
    
    exists = _material_exists(db, location, material_id)

    return JSONResponse({"exists": exists})