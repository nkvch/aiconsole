# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .database import SessionLocal
from .models import Material
from .schemas import MaterialOut  # Ensure this schema includes all fields

router = APIRouter()

@router.get("/", response_model=List[MaterialOut])
async def fetch_materials():
    db: Session = SessionLocal()

    try:
        # Query all materials from the database
        materials = db.query(Material).all()

        # Convert SQLAlchemy model instances to Pydantic models
        materials_list = [MaterialOut.from_orm(material) for material in materials]

        return materials_list

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
