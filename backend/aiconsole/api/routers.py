from fastapi import APIRouter

from aiconsole.api.auth import router as auth_router
from aiconsole.api.endpoints import (
    agents,
    chats,
    check_key,
    commands_history,
    genui,
    image,
    materials,
    ping,
    profile,
    projects,
    settings,
    ws,
)

app_router = APIRouter()

app_router.include_router(ping.router)
app_router.include_router(genui.router)
app_router.include_router(image.router)
app_router.include_router(check_key.router)
app_router.include_router(profile.router, tags=["Profile"])
app_router.include_router(chats.router, prefix="/api/chats", tags=["Chats"])
app_router.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app_router.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app_router.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app_router.include_router(settings.router, prefix="/api/settings", tags=["Project Settings"])
app_router.include_router(commands_history.router)
app_router.include_router(ws.router)
app_router.include_router(auth_router)
