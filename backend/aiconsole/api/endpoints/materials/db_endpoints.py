from contextlib import contextmanager
from typing import Generator, List,  cast
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker, Session
from aiconsole.api.endpoints.materials.material import get_default_content_for_type
from aiconsole.api.utils.asset_get import asset_get
from aiconsole.api.endpoints.registry import materials
from aiconsole.api.endpoints.services import AssetWithGivenNameAlreadyExistError, Materials
from aiconsole.core.assets.assets import Assets
from aiconsole.core.project import project
from aiconsole.core.assets.materials.db_model import DbMaterialUpdateSchema
from aiconsole.core.adapters.material import MaterialWithStatus
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import Material, MaterialContentType
from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType
from aiconsole.core.project.paths import get_project_directory
from aiconsole.core.assets.materials.db_crud import (
    _create_material_db, 
    _delete_material_db, 
    _get_material_db, 
    _get_materials_db,
    _material_exists,
    _patch_material_db,
    _set_material_status
)

# fastAPI dependency uses current project directory path to initialize connection to the right database

router = APIRouter()

@contextmanager
def create_db_session(project_directory: str):
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

def get_db(project_directory: str = Depends(get_project_directory)):
    with create_db_session(project_directory) as db:
        yield db

def get_db_session(project_directory: str) -> Session:
    return create_db_session(project_directory)

# API Endpoints
@router.post("/{material_id}")
def create_material_db(material_id: str, material: Material, db: Session = Depends(get_db), materials_service: Materials = Depends(materials)):
    materials:Assets = project.get_project_materials()
    try:
        materials_service._validate_existance(materials, material_id)
    except AssetWithGivenNameAlreadyExistError:
        raise HTTPException(status_code=404, detail="Material with given name already exists")

    existing_material = _get_material_db(db, material_id)
    if existing_material:
        raise HTTPException(status_code=404, detail="Material with given name already exists")
     
    _create_material_db(db, material)

# This method mimicks the previous method from material.py. It is accessed with name='new' when creating new material
@router.get("/{material_id}")
async def read_material(material_id: str, request: Request, db: Session = Depends(get_db)):
    type = cast(MaterialContentType, request.query_params.get("type", ""))
    location_param = request.query_params.get("location", None)
    location = AssetLocation(location_param) if location_param else None

    if material_id == "new" or location == AssetLocation.AICONSOLE_CORE:
        return await asset_get(
        request, 
        AssetType.MATERIAL, 
        material_id, 
        lambda: MaterialWithStatus(
            id="new_" + get_material_content_name(type).lower(),
            name="New " + get_material_content_name(type),
            content_type=type,
            usage="",
            usage_examples=[],
            status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override=False,
            content=get_default_content_for_type(type),
            )
        )

    elif location == AssetLocation.PROJECT_DIR or location is None:  
        material = _get_material_db(db, material_id)
        if material is None:
            raise HTTPException(status_code=404, detail="Material not found in database")    
    
    return material

@router.get("/")
def read_all_materials(db: Session = Depends(get_db)):
    # effectively all materials except those in database
    preinstalled_materials = project.get_project_materials().all_assets()
    db_materials = _get_materials_db(db, limit=100)
    return JSONResponse(
        [
                material.model_dump(exclude_none=True) for material in preinstalled_materials + db_materials
        ]
    )

@router.delete("/{material_id}", response_model=Material)
def delete_material_db(material_id: str, db: Session = Depends(get_db)):
    db_material = _delete_material_db(db, material_id)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return JSONResponse({"status": "ok"})

@router.patch("/{material_id}")
def patch_material_db(material_id: str, material_update: DbMaterialUpdateSchema, db: Session = Depends(get_db)):
    rename = _patch_material_db(db, material_id, material_update)
    if rename is None:
        raise HTTPException(status_code=404, detail="Material not found")
        

@router.post("/{material_id}/status-change")
async def change_material_status(material_id: str, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status field is required")

    db_material = _set_material_status(db, material_id, status)
    
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