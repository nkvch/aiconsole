import subprocess
import sys
from pathlib import Path


def get_current_project_venv_path() -> Path:
    return Path.cwd() / ".aic" / "venv"


def get_current_project_venv_bin_path() -> Path:
    if sys.platform == "win32":
        return get_current_project_venv_path() / "Scripts"
    else:
        return get_current_project_venv_path() / "bin"


def get_current_project_venv_python_path() -> Path:
    return get_current_project_venv_bin_path() / "python"


def get_current_project_venv_available_packages() -> str:
    try:
        output = subprocess.check_output([str(get_current_project_venv_bin_path() / "pip"), "list"]).decode("utf-8")
        package_lines = output.split("\\n")
        package_names = [line.split("==")[0] for line in package_lines]
        return " ".join(package_names)
    except subprocess.CalledProcessError:
        return ""
