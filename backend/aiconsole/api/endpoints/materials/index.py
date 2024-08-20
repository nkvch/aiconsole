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
from http.client import HTTPException

from sqlalchemy.exc import SQLAlchemyError

from .database import *
from .material import *
from .models import *


from fastapi import APIRouter
from fastapi.responses import JSONResponse

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project import project

router = APIRouter()


@router.get("/")
async def fetch_materials():
    # Create a new database session
    db: Session = SessionLocal()

    try:
        # Query all materials from the database
        materials = db.query(Material).all()

        # Convert materials to list of dictionaries
        materials_list = [
            {
                "id": material.id,
                "name": material.name,
                "version": material.version,
                "usage": material.usage,
                "usage_examples": material.usage_examples,
                "content_type": material.content_type,
                "content": material.content,
                "content_static_text": material.content_static_text,
                "default_status": material.default_status,
                "status": get_material_status(material.id)  # Implement this function
            }
            for material in materials
        ]

        # Return the result as a JSON response
        return JSONResponse(content=materials_list)

    except SQLAlchemyError as e:
        # Handle SQLAlchemy exceptions
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the database session
        db.close()


def get_material_status(material_id: int):
    # Implement this function to return the status of the material
    # For example, it might look up the status based on the material ID
    # This is just a placeholder implementation
    return "status_placeholder"