from functools import lru_cache
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from aiconsole.api.endpoints.services import Agents, MaterialService
from aiconsole.database.db import get_db_session

@lru_cache
def agents() -> Agents:
    return Agents()


def materials(session: AsyncSession = Depends(get_db_session)) -> MaterialService:
    return MaterialService(session=session)
