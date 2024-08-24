import logging
import platform
import subprocess
from pathlib import Path

_log = logging.getLogger(__name__)


def install_and_update_pip(venv_path):
    venv_path = Path(venv_path)

    if platform.system() == "Windows":
        venv_python_path = venv_path / "Scripts" / "python.exe"
    else:
        venv_python_path = venv_path / "bin" / "python"

    def run_subprocess(*args):
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            _log.error(f"Command {' '.join(args)} failed with error: {stderr.decode().strip()}")
            raise RuntimeError(stderr.decode().strip())

        return stdout.decode().strip()

    if not venv_python_path.exists():
        _log.info("Installing pip in the virtual environment.")
        run_subprocess(str(venv_python_path), "-m", "ensurepip")

    _log.info("Upgrading pip in the virtual environment.")
    run_subprocess(str(venv_python_path), "-m", "pip", "install", "--upgrade", "pip")
    return True
