import logging
import subprocess
from pathlib import Path

_log = logging.getLogger(__name__)


def install_dependencies(python_path: Path, dependency_path: Path, develop_mode: bool = True):
    """
    Installs dependencies using pip.

    :param python_path: Path to the Python executable.
    :param dependency_path: Path to the dependency or requirements file.
    :param develop_mode: If True, install in editable mode.
    """
    if not python_path.exists() or not dependency_path.exists():
        _log.error("Invalid path provided for Python or dependency.")
        return

    install_command: list[str] = [
        str(python_path),
        "-m",
        "pip",
        "install",
        str(dependency_path),
    ]

    if develop_mode:
        install_command.insert(4, "-e")

    command_str = " ".join(filter(None, install_command))
    _log.info(f"Installing dependencies using: {command_str}")

    try:
        result = subprocess.run(
            [str(elem) for elem in install_command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _log.info(f"Installation successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        _log.error(f"Installation failed: {e.stderr}")
