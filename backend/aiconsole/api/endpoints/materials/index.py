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

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project import project

from aiconsole.database import get_db
from aiconsole.models.material import Material
from aiconsole.schemas.material import MaterialResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[MaterialResponse])
async def fetch_materials(db: Session = Depends(get_db)):
    try:
        materials = db.query(Material).all()

        materials_list = [MaterialResponse.from_orm(material) for material in materials]

        return materials_list

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f'{e}')

    finally:
        db.close()
