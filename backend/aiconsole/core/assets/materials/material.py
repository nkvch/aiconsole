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
import traceback
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.inspection import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from aiconsole.core.assets.materials.db_model import DbMaterial
from aiconsole.core.assets.materials.documentation_from_code import (
    documentation_from_code,
)
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.assets.types import Asset, AssetLocation, AssetStatus, AssetType
from aiconsole.utils.events import InternalEvent, internal_events

if TYPE_CHECKING:
    from aiconsole.core.assets.materials.content_evaluation_context import (
        ContentEvaluationContext,
    )


@dataclass(frozen=True, slots=True)
class MaterialRenderErrorEvent(InternalEvent):
    pass


class MaterialContentType(str, Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"


class Material(Asset):
    type: AssetType = AssetType.MATERIAL
    id: str
    name: str
    version: str = "0.0.1"
    usage: str
    defined_in: AssetLocation

    # Content, either static or dynamic
    content_type: MaterialContentType = MaterialContentType.STATIC_TEXT
    content: str = ""

    def __hash__(self):
        return hash(self.id + self.version + self.name + self.usage + self.content_type + self.content)

    @property
    def inlined_content(self):
        # if starts with file:// then load the file, take into account file://./relative paths
        if self.content.startswith("file://"):
            content_file = self.content[len("file://") :]

            from aiconsole.core.project.paths import (
                get_core_assets_directory,
                get_project_assets_directory,
            )

            project_dir_path = get_project_assets_directory(self.type)
            core_resource_path = get_core_assets_directory(self.type)
            # TODO: content_file path is relative. If material is default, only .toml file is copied to project
            #  directory, so content_file is not found. If material is in project, then content_file is found.
            # if self.defined_in == AssetLocation.PROJECT_DIR:
            #     base_search_path = project_dir_path
            # else:
            #     base_search_path = core_resource_path

            # This is a workaround for now, but it should be fixed in the future
            if (project_dir_path / content_file).exists():
                base_search_path = project_dir_path
            else:
                base_search_path = core_resource_path

            with open(base_search_path / content_file, "r", encoding="utf8", errors="replace") as file:
                return file.read()

        return self.content

    async def render(self, context: "ContentEvaluationContext"):
        header = f"# {self.name}\n\n"

        match self.content_type:
            case MaterialContentType.STATIC_TEXT:
                return RenderedMaterial(id=self.id, content=header + self.inlined_content, error="")
            case MaterialContentType.DYNAMIC_TEXT:
                return await self._handle_dynamic_text_content(context, header)
            case MaterialContentType.API:
                return await self._handle_api_content(context, header)
            case _:
                raise ValueError("Material has no content")

    async def _handle_dynamic_text_content(self, context, header):
        try:
            source_code = compile(self.inlined_content, "<string>", "exec")
            local_vars = {}
            exec(source_code, local_vars)
            content_func = local_vars.get("content")
            if callable(content_func):
                content = await content_func(context)
                return RenderedMaterial(id=self.id, content=header + content, error="")
            else:
                raise ValueError("No callable content function found!")
        except Exception:
            await internal_events().emit(MaterialRenderErrorEvent(), details=f"Error in DYNAMIC_TEXT material `{self.id}`")
            error_details = RenderedMaterial(id=self.id, content="", error=traceback.format_exc())
            raise ValueError("Error in Dynamic Note material", error_details)

    async def _handle_api_content(self, context, header):
        try:
            compile(self.inlined_content, "temp_module", "exec")
            content = documentation_from_code(self, self.inlined_content)(context)
            return RenderedMaterial(id=self.id, content=header + content, error="")
        except Exception:
            await internal_events().emit(MaterialRenderErrorEvent(), details=f"Error in API material `{self.id}`")
            error_details = RenderedMaterial(id=self.id, content="", error=traceback.format_exc())
            raise ValueError("Error in Python API material", error_details)
        
    @classmethod
    def from_orm_with_defaults(cls, db_material: DbMaterial):
        # Convert from SQLAlchemy model to Pydantic schema, filling in missing fields
        return cls(
            id=db_material.id,
            name=db_material.name,
            version=db_material.version,
            usage=db_material.usage,
            status=db_material.status,
            content_type=db_material.content_type,
            content=db_material.content,
            # Default values for fields not present in the SQLAlchemy model
            usage_examples=[], 
            type=AssetType.MATERIAL,
            default_status=AssetStatus.ENABLED,
            defined_in=AssetLocation.PROJECT_DIR,
            override = False # because it's retrieved from databae (?)always(?)
        )
    
    def model_dump_filtered(self, model_class: DeclarativeMeta) -> dict:
        """Dump the model to a dictionary, filtering to include only fields from sqlalchemy model."""
        allowed_fields = {c.key for c in inspect(model_class).mapper.column_attrs}
        model_dict = self.model_dump(by_alias=True)
        filtered_dict = {k: v for k, v in model_dict.items() if k in allowed_fields}
        return filtered_dict


class MaterialWithStatus(Material):
    status: AssetStatus = AssetStatus.ENABLED
