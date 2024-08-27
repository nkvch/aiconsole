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

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from aiconsole.api.endpoints.registry import materials
from aiconsole.api.endpoints.services import (
    AssetWithGivenNameAlreadyExistError,
    Materials,
)
from aiconsole.api.utils.asset_exists import asset_exists, asset_path
from aiconsole.api.utils.asset_get import asset_get
from aiconsole.api.utils.asset_status_change import asset_status_change
from aiconsole.api.utils.status_change_post_body import StatusChangePostBody
from aiconsole.core.assets.get_material_content_name import get_material_content_name
from aiconsole.core.assets.materials.material import (
    Material as MaterialModel,
    MaterialContentType,
    MaterialWithStatus,
)
from aiconsole.core.assets.types import AssetLocation, AssetStatus, AssetType
from aiconsole.core.project import project

from sqlalchemy.orm import Session
from aiconsole.database import get_db
from aiconsole.models.material import Material
from aiconsole.schemas.material import MaterialCreate, MaterialResponse, MaterialUpdate
from aiconsole.api.services.repository import (
    create_material,
    get_material,
    update_material,
    delete_material
)


router = APIRouter()


def get_default_content_for_type(type: MaterialContentType):
    if type == MaterialContentType.STATIC_TEXT:
        return """

content, content content

## Sub header

Bullets in sub header:
* Bullet 1
* Bullet 2
* Bullet 3

""".strip()
    elif type == MaterialContentType.DYNAMIC_TEXT:
        return """

import random

async def content(context):
    samples = ['sample 1' , 'sample 2', 'sample 3', 'sample 4']
    return f'''
# Examples of great content
{random.sample(samples, 2)}

'''.strip()

""".strip()
    elif type == MaterialContentType.API:
        return """

'''
Add here general API description
'''

def create():
    '''
    Add comment when to use this function, and add example of usage:
    ```python
        create()
    ```
    '''
    print("Created")


def print_list():
    '''
    Use this function to print 'List'.
    Sample of use:
    ```python
        print_list()
    ```

    '''
    print("List")



def fibonacci(n):
    '''
    Use it to calculate and return the nth term of the Fibonacci sequence.
    Sample of use:
    ```python
      fibonacci(10)
    ```
    '''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
""".strip()
    else:
        raise ValueError("Invalid material content type")


@router.post("/", response_model=MaterialResponse)
async def create_material_endpoint(material: MaterialCreate,
                                   db: Session = Depends(get_db)
                                   ):
    existing_material = db.query(Material).filter(Material.name == material.name).first()
    if existing_material:
        raise HTTPException(status_code=400, detail="Material with the given name already exists.")

    material_data = material.dict()
    return create_material(db, material_data)


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material_endpoint(material_id: int,
                                db: Session = Depends(get_db)
                                ):
    material = get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.patch("/{material_id}", response_model=MaterialResponse)
async def update_material_endpoint(material_id: int,
                                    material: MaterialUpdate,
                                    db: Session = Depends(get_db)
                                    ):
    material_data = material.dict(exclude_unset=True)
    updated_material = update_material(db, material_id, material_data)
    if not updated_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return updated_material


@router.delete("/{material_id}", response_model=dict)
async def delete_material_endpoint(material_id: int,
                                   db: Session = Depends(get_db)
                                   ):
    deleted_material = delete_material(db, material_id)
    if not deleted_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": "ok"}


@router.post("/{material_id}/status-change", response_model=MaterialResponse)
async def material_status_change_endpoint(material_id: int,
                                          body: StatusChangePostBody,
                                          db: Session = Depends(get_db)
                                          ):
    material = get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    material.status = body.status
    db.commit()
    db.refresh(material)
    return material


@router.get("/{material_id}/exists", response_model=dict)
async def material_exists_endpoint(material_id: int,
                                   db: Session = Depends(get_db)
                                   ):
    material = get_material(db, material_id)
    return {"exists": bool(material)}