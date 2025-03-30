from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from send2trash import send2trash

from aiconsole.core.assets.types import AssetType
from aiconsole.core.project.paths import get_project_assets_directory

router = APIRouter()


class BulkDeleteRequest(BaseModel):
    """
    BulkDelete model for data validation and documentation.
    """
    ids: list[str]

@router.delete("/bulk/delete")
async def delete_bulk_agents(request: BulkDeleteRequest):
    """
    Deletes multiple Agents at once.
    request: {
        ids: list[str] - list of IDs to delete.
    }
    """
    dir_path = get_project_assets_directory(AssetType.AGENT)
    for agent_id in request.ids:
        file_path = dir_path / f'{agent_id}.toml'
        try:
            send2trash(file_path)
        except FileNotFoundError:
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=f'Agent with id:{agent_id} not found.'
            )

    return Response(
        status_code=status.HTTP_200_OK,
        content=f'Successfully deleted {len(request.ids)} agents.'
    )
