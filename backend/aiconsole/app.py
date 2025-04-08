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

import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from aiconsole.api.routers import app_router
from aiconsole.core.project.paths import get_project_directory_safe
from aiconsole.core.settings.fs.settings_file_storage import SettingsFileStorage
from aiconsole.core.settings.settings import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from aiconsole.core.settings.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if "BE_SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.environ.get("BE_SENTRY_DSN", ""),
        enable_tracing=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings().configure(SettingsFileStorage(project_path=get_project_directory_safe()))
    yield


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        protected_paths = ["/api/project", "/api/projects", "/api/chats", "/api/agents", "/api/materials"]
        logger.info(f"Request path: {request.url.path}, Method: {request.method}, Cookies: {request.cookies}")

        if request.method == "OPTIONS":
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in protected_paths):
            if not request.cookies.get("user"):
                logger.warning("No 'user' cookie found, raising 401")
                raise HTTPException(status_code=401, detail="Unauthorized")

        response = await call_next(request)
        return response


def app():
    origin = os.getenv("CORS_ORIGIN", None)

    if origin is None:
        raise Exception("CORS_ORIGIN environment variable not set")

    app = FastAPI(title="AI Console", lifespan=lifespan)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings().session_secret_key,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        AuthMiddleware,
    )

    app.include_router(app_router)

    return app
