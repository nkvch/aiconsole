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

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Query
from aiconsole.core.assets.types import AssetType
from aiconsole.core.project import project

router = APIRouter()

@router.get("/")
async def fetch_materials(
    offset: int = Query(0),
    search: str = Query(None)
):
    materials = project.get_project_materials().all_assets()
    limit = 18  # Fixed limit

    # Apply search filter if search query is provided
    if search:
        search_lower = search.lower()
        materials = [material for material in materials if search_lower in material.name.lower()]

    # Check if the offset is beyond the available materials
    if offset >= len(materials):
        return JSONResponse([])  # Return an empty list, indicating no more materials

    # Slice the materials list based on the offset and limit
    paginated_materials = materials[offset:offset + limit]

    response_data = [
        {
            **material.model_dump(exclude_none=True),
            "status": project.get_project_agents().get_status(AssetType.MATERIAL, material.id),
        }
        for material in paginated_materials
    ]

    return JSONResponse(response_data)

