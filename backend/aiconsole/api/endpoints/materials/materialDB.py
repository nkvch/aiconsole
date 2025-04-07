from aiconsole.db.initDB import get_db_connection, init_db
from fastapi import APIRouter, Depends, HTTPException, Request
from aiconsole.core.assets.materials.materialDB import Material,MaterialCreate,MaterialContentType, AssetStatus, MaterialUpdate
from typing import List
from sqlite3 import IntegrityError
from enum import Enum
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

@router.get("/materials", response_model=List[Material])
def list_materials(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM materials")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
    materials = []
    for row in rows:
        try:
            material = Material(
                id=row["id"],
                name=row["name"],
                version=row["version"],
                usage=row["usage"],
                content_type=MaterialContentType(row["content_type"]),
                content=row["content"],
                status=AssetStatus(row["status"])
            )
            materials.append(material)
        except Exception as e:
            print(f"Skipped invalid row: {e}")
            continue

    return materials
    
@router.get("/materials/{material_id}", response_model=Material)
def get_material(material_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    if not row:
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
    data = material.dict()
    data["id"] = new_id
    return Material(**data)



@router.patch("/materials/{material_id}", response_model=Material)
def update_material(material_id: int, update: MaterialUpdate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Material not found")

    update_data = update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    set_clause = ", ".join([f"{field} = ?" for field in update_data.keys()])
    values = [
        (v.value if isinstance(v, Enum) else v)
        for v in update_data.values()
    ]
    values.append(material_id)

    cursor.execute(f"""
        UPDATE materials SET {set_clause} WHERE id = ?
    """, values)
    db.commit()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    updated = cursor.fetchone()
    return Material(
        id=updated["id"],
        name=updated["name"],
        version=updated["version"],
        usage=updated["usage"],
        content_type=MaterialContentType(updated["content_type"]),
        content=updated["content"],
        status=AssetStatus(updated["status"])
    )
    

@router.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    db.commit()
    return None

@router.delete("/materials/", status_code=204)
def delete_all_materials( db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM materials ")
    db.commit()
    return []
