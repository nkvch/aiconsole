import os
from typing import AsyncGenerator, Protocol

from aiconsole.core.assets.materials.material import Material
from aiconsole_toolkit.env import (
    get_current_project_venv_bin_path,
    get_current_project_venv_path,
)


class BaseCodeInterpreter(Protocol):
    """
    .run is a generator that yields a dict with attributes: active_line, output
    """

    async def initialize(self):  # fmt: off
        ...

    def run(self, code: str, materials: list[Material]) -> AsyncGenerator[str, None]:  # fmt: off
        ...

    def terminate(self) -> None:  # fmt: off
        ...

    def get_environment_variables(self) -> dict[str, str]:
        path = os.environ.get("PATH") or ""

        # replace the first element in the PATH with the venv bin path
        # this is the one we've added to get the correct embedded interpreter when the app is starting
        sep = str(os.pathsep)
        _path = sep.join([str(get_current_project_venv_bin_path()), *path.split(sep)])
        r = {
            **os.environ,
            # just in case for correct questions about the venv locations and similar
            "VIRTUAL_ENV": str(get_current_project_venv_path()),
        }
        r["PATH"] = _path
        return r
