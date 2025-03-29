import asyncio
import logging
import os
from pathlib import Path
from typing import AsyncGenerator, Protocol, Optional

from aiconsole.core.assets.materials.material import Material
from aiconsole.core.code_running.virtual_env.create_dedicated_venv import WaitForEnvEvent
from aiconsole.utils.events import internal_events
from aiconsole_toolkit.env import (
    get_current_project_venv_bin_path,
    get_current_project_venv_path,
)

_log = logging.getLogger(__name__)


class BaseCodeInterpreter(Protocol):
    async def initialize(self, use_mcp: bool = False) -> None:
        """Initialize the interpreter, optionally with MCP support"""
        ...

    async def run(self, code: str, materials: list[Material]) -> AsyncGenerator[str, None]:
        """Run code and yield output"""
        yield ""

    def terminate(self) -> None:
        """Terminate the interpreter"""
        ...

    def preprocess_code(self, code: str, materials: list[Material]) -> str:
        """Preprocess code before execution"""
        return code

    def get_environment_variables(self) -> dict[str, str]:
        path = os.environ.get("PATH") or ""
        sep = str(os.pathsep)
        _path = sep.join([str(get_current_project_venv_bin_path()), *path.split(sep)])
        return {
            **os.environ,
            "VIRTUAL_ENV": str(get_current_project_venv_path()),
            "PATH": _path
        }

    async def wait_for_path(self, timeout: int = 100, check_interval: int = 5):
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