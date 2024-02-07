import logging

from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData

_log = logging.getLogger(__name__)


def merge_settings_data(settings: SettingsData, *new_settings: PartialSettingsData):
    settings_data = settings.model_dump()

    for new_setting in new_settings:
        new_setting_data = new_setting.model_dump(exclude_none=True)

        for key, value in new_setting_data.items():
            if key in settings_data:
                if isinstance(settings_data[key], list) and isinstance(value, list):
                    settings_data[key].extend(value)
                elif isinstance(settings_data[key], dict) and isinstance(value, dict):
                    settings_data[key].update(value)
                else:
                    settings_data[key] = value
            else:
                settings_data[key] = value

    return SettingsData(**settings_data)
