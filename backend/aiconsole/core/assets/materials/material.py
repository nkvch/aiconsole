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
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import AnyUrl, FileUrl

from aiconsole.core.assets.materials.documentation_from_code import (
    documentation_from_code,
)
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.assets.types import Asset, AssetLocation, AssetStatus
from aiconsole.core.assets.utils.copy_file_content import copy_file_content

if TYPE_CHECKING:
    from aiconsole.core.assets.materials.content_evaluation_context import (
        ContentEvaluationContext,
    )


class MaterialContentType(str, Enum):
    STATIC_TEXT = "static_text"
    DYNAMIC_TEXT = "dynamic_text"
    API = "api"


class Material(Asset):
    id: str
    name: str
    version: str = "0.0.1"
    usage: str
    defined_in: AssetLocation

    # Content, either static or dynamic
    content_type: MaterialContentType = MaterialContentType.STATIC_TEXT
    content: str | AnyUrl = ""

    def __hash__(self):
        return hash(self.id + self.version + self.name + self.usage + self.content_type + str(self.content))

    @property
    def inlined_content(self):
        # if starts with file:// then load the file, takes into account file://./relative paths for core and project
        if isinstance(self.content, FileUrl):
            copy_file_content(self.content)
        return str(self.content)

    async def render(self, context: "ContentEvaluationContext"):
        header = f"# {self.name}\n\n"

        inline_content = self.inlined_content

        try:
            match self.content_type:
                case MaterialContentType.DYNAMIC_TEXT:
                    # Try compiling the python code and run it
                    source_code = compile(inline_content, "<string>", "exec")
                    local_vars: dict[str, Any] = {}
                    exec(source_code, local_vars)
                    # currently, getting the python object from another interpreter is quite limited, and
                    # using the dedicated local_vars is the easiest way (otherwise we would need to pickle
                    # the object and send it to the other interpreter or use stdin/stdout)
                    content_func = local_vars.get("content")
                    if callable(content_func):
                        return RenderedMaterial(
                            id=self.id,
                            content=header + await content_func(context),
                            error="",
                        )
                    return RenderedMaterial(id=self.id, content="", error="No callable content function found!")
                case MaterialContentType.STATIC_TEXT:
                    return RenderedMaterial(id=self.id, content=header + inline_content, error="")
                case MaterialContentType.API:
                    return RenderedMaterial(
                        id=self.id,
                        content=header + documentation_from_code(self, inline_content)(context),
                        error="",
                    )
                case _:
                    return RenderedMaterial(
                        id=self.id, content="", error="Unmatched content type!"
                    )
        except Exception:
            return RenderedMaterial(id=self.id, content="", error=traceback.format_exc())


class MaterialWithStatus(Material):
    status: AssetStatus = AssetStatus.ENABLED
