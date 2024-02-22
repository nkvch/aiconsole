from fastapi import APIRouter
from fastapi.responses import JSONResponse

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project import project

router = APIRouter()

@router.get("/")
async def fetch_files():
    return JSONResponse(
        [
            {
                **files.model_dump(exclude_none=True),
                "status": project.get_project_agents().get_status(AssetType.FILE, files.id),
            }
            for files in project.get_project_files().all_assets()
        ]
    )
