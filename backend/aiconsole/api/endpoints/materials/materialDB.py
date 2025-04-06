from aiconsole.db.initDB import get_db_connection, init_db
from fastapi import APIRouter, Depends, HTTPException, Request
from aiconsole.core.assets.materials.material import Material
from typing import List

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

@router.get("/materials/test", response_model=List[Material])
def list_materials(db=Depends(get_db)):
    return []  # zwracamy pustą listę typu List[Material], żeby przetestować