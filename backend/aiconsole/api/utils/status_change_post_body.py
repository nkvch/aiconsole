from pydantic import BaseModel

from aiconsole.core.assets.types import AssetStatus


class StatusChangePostBody(BaseModel):
    status: AssetStatus
    to_global: bool
