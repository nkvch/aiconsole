# Versioning of “Materials” by integrating Git

Under path "/backend/aiconsole/core/assets/materials/materials_changelog.py" there are functions to implement tracking materials.

Function "commit_to_changelog" stages and commits changes from materials directory into git repo under path "/backend/materials-changelog".

Changelogs can be retrieved from the backend site by endpoint "/materials/{material_id}/changelog"

As in the endpoint, material_id is passed as we retrieve the changelogs only of some specific material.

Changelogs contain commit hash, author name, date, message, diff.

"diff" represents what changed in the specific file.
