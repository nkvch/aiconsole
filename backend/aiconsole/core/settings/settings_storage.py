from pathlib import Path
from typing import Optional, Protocol

from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData


class SettingsStorage(Protocol):
    @property
    def global_settings(self) -> PartialSettingsData:  # fmt: off
        ...

    @property
    def project_settings(self) -> PartialSettingsData:  # fmt: off
        ...

    def change_project(self, project_path: Optional[Path] = None):  # fmt: off
        ...

    def save(self, settings_data: PartialSettingsData, to_global: bool):  # fmt: off
        ...
