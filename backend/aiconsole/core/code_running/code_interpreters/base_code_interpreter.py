import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncGenerator, Protocol

from aiconsole.core.assets.materials.material import Material
from aiconsole.core.code_running.virtual_env.create_dedicated_venv import WaitForEnvEvent
from aiconsole.utils.events import internal_events
from aiconsole_toolkit.env import (
    get_current_project_venv_bin_path,
    get_current_project_venv_path,
)

_log = logging.getLogger(__name__)


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

    async def wait_for_path(self, timeout: int = 100, check_interval: int = 5):
        """
        Waits for a virtual environment path to exist, with a timeout and check interval.

        :param timeout: Total time to wait for the path in seconds.
        :param check_interval: Time interval between checks in seconds.
        :raises RuntimeError: If the path does not exist after the timeout period.
        """
        venv_path: Path = get_current_project_venv_path() / "aic_version"

        if not venv_path.exists():
            await internal_events().emit(WaitForEnvEvent())

        end_time = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < end_time:
            if venv_path.exists():
                _log.info(f"Path {venv_path} exists now.")
                return
            _log.info(f"Waiting for path {venv_path} to exist...")
            await asyncio.sleep(check_interval)

        raise RuntimeError(f"No venv located at {venv_path} after {timeout} seconds")
