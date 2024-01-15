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

import logging
from functools import lru_cache
from uuid import uuid4

from aiconsole.core import project
from aiconsole.core.project.paths import (
    get_core_assets_directory,
    get_core_preinstalled_assets_directory,
)
from aiconsole.core.settings.fs.settings_file_storage import SettingsUpdatedEvent
from aiconsole.core.settings.settings_notifications import SettingsNotifications
from aiconsole.core.settings.settings_storage import SettingsStorage
from aiconsole.core.settings.utils.merge_settings_data import merge_settings_data
from aiconsole.core.users.types import UserProfile
from aiconsole.utils.events import internal_events
from aiconsole_toolkit.settings.partial_settings_data import PartialSettingsData
from aiconsole_toolkit.settings.settings_data import SettingsData

_log = logging.getLogger(__name__)


class Settings:
    _storage: SettingsStorage | None = None
    _settings_notifications: SettingsNotifications | None = None

    def configure(self, storage: SettingsStorage):
        self.destroy()

        self._storage = storage
        self._settings_notifications = SettingsNotifications()

        self._default_settings = SettingsData(
            user_profile=UserProfile(
                display_name="User",
                profile_picture=open(get_core_preinstalled_assets_directory() / "avatars" / "user.jpg", "rb").read(),
            ),
        )

        internal_events().subscribe(
            SettingsUpdatedEvent,
            self._when_reloaded,
        )

        # Assign system user installation / user_id
        if self.unified_settings.user_id is None:
            self.save(PartialSettingsData(user_id=str(uuid4())), to_global=True)

        _log.info("Settings configured")

    def destroy(self):
        self._storage = None
        self._settings_notifications = None

        internal_events().unsubscribe(
            SettingsUpdatedEvent,
            self._when_reloaded,
        )

    async def _when_reloaded(self, SettingsUpdatedEvent):
        if not self._storage or not self._settings_notifications:
            raise ValueError("Settings not configured")

        await self._settings_notifications.notify()

    @property
    def unified_settings(self) -> SettingsData:
        if not self._storage or not self._settings_notifications:
            raise ValueError("Settings not configured")

        return merge_settings_data(
            self._default_settings, self._storage.global_settings, self._storage.project_settings
        )

    def save(self, settings_data: PartialSettingsData, to_global: bool):
        if not self._storage or not self._settings_notifications:
            raise ValueError("Settings not configured")

        self._settings_notifications.suppress_next_notification()
        self._storage.save(settings_data, to_global=to_global)


@lru_cache
def settings() -> Settings:
    return Settings()
