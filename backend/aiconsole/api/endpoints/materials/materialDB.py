from aiconsole.db.initDB import get_db_connection, init_db
from fastapi import APIRouter, Depends, HTTPException, Request
from aiconsole.core.assets.materials.materialDB import Material,MaterialCreate,MaterialContentType, AssetStatus
from typing import List
from sqlite3 import IntegrityError

router = APIRouter()

@router.on_event("startup")
def startup_event():
    init_db() 
    
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

    
    
@router.get("/materials/{material_id}", response_model=Material)
def get_material(material_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return Material(
        id=row["id"],
        name=row["name"],
        version=row["version"],
        usage=row["usage"],
        content_type=MaterialContentType(row["content_type"]),
        content=row["content"],
        status=AssetStatus(row["status"])
    )
    
@router.post("/materials/", response_model=Material)
def create_material(material: MaterialCreate, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM materials WHERE name = ?", (material.name,))
    if cursor.fetchone():
        raise HTTPException(status_code=409, detail="Material with this name already exists")

    cursor.execute("""
        INSERT INTO materials (name, version, usage, content_type, content, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        material.name,
        material.version,
        material.usage,
        material.content_type.value,
        material.content,
        material.status.value
    ))
    db.commit()
    new_id = cursor.lastrowid
    return Material(id=new_id, **material.dict())