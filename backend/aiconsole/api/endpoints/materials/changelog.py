from fastapi import APIRouter, HTTPException
from pathlib import Path
from aiconsole.utils.git_materials_utils import GitMaterialRepo
router = APIRouter()


HOME_DIR = Path.home()
MATERIALS_DIR = HOME_DIR / "aiconsole" / "materials"
repo = GitMaterialRepo(MATERIALS_DIR)

@router.get("/materials/{filename}/changelog")
def get_material_changelog(filename: str):
    material_path = MATERIALS_DIR / filename

    if not material_path.exists():
        raise HTTPException(status_code=404, detail="Material file not found")

    try:
        changelog = repo.get_file_changelog(filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"filename": filename, "changelog": changelog}