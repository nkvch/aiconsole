from fastapi import APIRouter, HTTPException
from pathlib import Path
from aiconsole.utils.git_materials_utils import GitMaterialRepo
from aiconsole.consts import MATERIALS_DIR
router = APIRouter()



repo = GitMaterialRepo(MATERIALS_DIR)

@router.get("/{material_id}/changelog")
def get_material_changelog(material_id: str):
    filename = f"{material_id}.toml"
    material_path = MATERIALS_DIR / filename

    if not material_path.exists():
        raise HTTPException(status_code=404, detail="Material file not found")

    try:
        changelog = repo.get_file_changelog(filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"material_id": material_id, "changelog": changelog}