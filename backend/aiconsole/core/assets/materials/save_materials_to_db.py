from aiconsole.database.models import MaterialDB
from aiconsole.database.db import get_db_instance
from sqlalchemy.exc import IntegrityError


async def save_materials_to_db(materials: list[MaterialDB]):
    db = get_db_instance()
    async with db.session() as session:
        added_materials = []

        for material in materials:

            existing = await session.get(MaterialDB, material.id)
            if existing:
                added_materials.append(existing)
                continue

            session.add(material)
            added_materials.append(material)

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise ValueError("Error while saving materials to DB.") from e
        return added_materials
