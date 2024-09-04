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
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine

from aiconsole.api.endpoints.projects.registry import project_directory
from aiconsole.api.endpoints.projects.services import ProjectDirectory
from aiconsole.core.assets.materials.db_model import Base

router = APIRouter()


class ProjectDirectoryParams(BaseModel):
    directory: str


@router.post("/choose_directory")
async def choose_directory(
    project_directory: ProjectDirectory = Depends(dependency=project_directory),
):
    initial_directory = await project_directory.choose_directory()
    return {"directory": None if initial_directory is None else str(initial_directory)}


@router.get("/is_in_directory")
async def is_project_in_directory(
    directory: str,
    project_directory: ProjectDirectory = Depends(dependency=project_directory),
):
    return {"is_project": project_directory.is_project_in_directory(directory)}


@router.post("/switch")
async def switch_project_endpoint(
    params: ProjectDirectoryParams,
    background_tasks: BackgroundTasks,
    project_directory: ProjectDirectory = Depends(dependency=project_directory),
):
    try:
        await project_directory.switch_or_save_project(params.directory, background_tasks)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"message": str(object=e), "display": False})


# This endpoint is accessed when user chooses to either:
# 1. open existing project
# 2. create a new one
# see: aiconsole\frontend\src\store\projects\useProjectFileManagerStore.ts
# it creates the database in project directory and initializes tables
@router.post("/init_database")
async def init_database(directory: str):
    # Ensure directory is provided
    if not directory:
        raise HTTPException(status_code=400, detail="Directory path is required.")
    
    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    db_path = os.path.join(directory, "materials.db")
    engine = create_engine(f"sqlite:///{db_path}")

    Base.metadata.create_all(bind=engine)

    return {"directory": directory}