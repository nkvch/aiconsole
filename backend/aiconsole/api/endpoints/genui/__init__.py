from fastapi import APIRouter

from . import index

router = APIRouter()

router.include_router(index.router, prefix="/genui")
