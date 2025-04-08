from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict

from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.types import AssetStatus, AssetType


class BulkStatusChangePostBody(BaseModel):
    status_changes: Dict[str, AssetStatus]


async def bulk_asset_status_change(asset_type: AssetType, body: BulkStatusChangePostBody):
    try:
        for asset_id, new_status in body.status_changes.items():
            Assets.set_status(asset_type, id=asset_id, status=new_status)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 