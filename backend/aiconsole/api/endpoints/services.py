from typing import Optional

from fastapi import UploadFile, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.assets import Assets
from aiconsole.core.assets.materials.material import Material, MaterialCreate, StatusChangePostResponse
from aiconsole.core.assets.types import Asset, AssetType
from aiconsole.core.project import project
from aiconsole.core.project.paths import get_project_assets_directory
from aiconsole.database.models import MaterialDB, material_to_db, db_to_material


class DomainError(Exception):
    """Base class for all domain-specific exceptions."""

    status_code: int = 400
    detail: str = "A domain error occurred."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class AssetWithGivenNameAlreadyExistError(DomainError):
    status_code = 409
    detail = "Resource already exists."


class NotFoundError(DomainError):
    status_code = 404
    detail = "Resource not found."


class _Assets:
    async def _create(self, assets: Assets, asset_id: str, asset: Asset) -> None:
        self._validate_existance(assets, asset_id)

        await assets.save_asset(asset, old_asset_id=asset_id, create=True)

    async def _partially_update(self, assets: Assets, old_asset_id: str, asset: Asset) -> None:
        # if asset.id != old_asset_id:
        #     self._validate_existance(assets, asset.id)

        await assets.save_asset(asset, old_asset_id=old_asset_id, create=True)

    def _validate_existance(self, assets: Assets, asset_id: str) -> None:
        existing_asset = assets.get_asset(asset_id)
        if existing_asset is not None:
            raise AssetWithGivenNameAlreadyExistError()


class Agents(_Assets):
    async def create_agent(self, agent_id: str, agent: AICAgent) -> None:
        agents = project.get_project_agents()
        await self._create(agents, agent_id, agent)

    async def partially_update_agent(self, agent_id: str, agent: AICAgent) -> None:
        agents = project.get_project_agents()
        await self._partially_update(agents, agent_id, agent)

    async def set_agent_avatar(self, agent_id: str, avatar: UploadFile) -> None:
        image_path = get_project_assets_directory(AssetType.AGENT) / f"{agent_id}.jpg"
        content = await avatar.read()
        with open(image_path, "wb+") as avatar_file:
            avatar_file.write(content)


class MaterialService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_material(self, material_id: str, material: MaterialCreate) -> str:
        existing = await self.session.get(MaterialDB, material_id)
        if existing:
            raise AssetWithGivenNameAlreadyExistError()

        material_data = material.model_dump()
        material_data["name"] = material_id

        db_material = MaterialDB(**material_data)
        self.session.add(db_material)
        await self.session.commit()
        return db_material.id

    async def partially_update_material(self, material_id: str, material: Material) -> MaterialDB:
        db_material = await self.session.get(MaterialDB, material_id)
        if not db_material:
            raise NotFoundError(material_id)

        updated = material_to_db(material)
        updated_data = updated.model_dump(exclude_unset=True)

        for field, value in updated_data.items():
            setattr(db_material, field, value)
        await self.session.commit()
        return updated

    async def delete_material(self, material_id: str) -> None:
        db_material = await self.session.get(MaterialDB, material_id)
        if not db_material:
            raise NotFoundError(material_id)
        await self.session.delete(db_material)
        await self.session.commit()

    async def get_material(self, material_id: str) -> Optional[Material]:
        statement = select(MaterialDB).where(MaterialDB.id == material_id)
        result = await self.session.exec(statement)
        db_material = result.first()
        if not db_material:
            raise HTTPException(status_code=404, detail=f"Material with ID '{material_id}' not found.")
        return db_to_material(db_material)

    async def material_exists(self, material_id: str) -> bool:
        return await self.session.get(MaterialDB, material_id) is not None

    async def update_material_status(self, material_id: str, status: str) -> StatusChangePostResponse:
        db_material = await self.session.get(MaterialDB, material_id)
        if not db_material:
            raise NotFoundError(material_id)
        db_material.status = status
        await self.session.commit()
        return StatusChangePostResponse(id=material_id, status=status)
