// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { PartialSettingsData, SettingsData } from '@/types/settings/settingsTypes';
import ky from 'ky';
import { API_HOOKS, getBaseURL } from '../../store/useAPIStore';

const checkKey = (key: string) => {
  return ky.get(`${getBaseURL()}/api/key`, {
    searchParams: `key=${key}`,
    hooks: API_HOOKS,
  });
};

async function getUserAvatar(email?: string): Promise<Avatar> {
  const response = await ky
    .get(`${getBaseURL()}/profile`, { searchParams: email ? { email } : undefined })
    .json<Avatar>();

  return {
    avatar_url: `${getBaseURL()}/${response.avatar_url}`,
    username: response.username,
  };
}

// TODO: this is not working now - backend is not ready
async function setUserAvatar(avatar: FormData) {
  return ky.post(`${getBaseURL()}/profile_image`, { body: avatar, hooks: API_HOOKS });
}

async function saveSettings(params: { to_global: boolean } & PartialSettingsData) {
  console.log(params);
  return ky.patch(`${getBaseURL()}/api/settings`, { json: params, hooks: API_HOOKS });
}

async function getSettings(): Promise<SettingsData> {
  return ky.get(`${getBaseURL()}/api/settings`, { hooks: API_HOOKS, timeout: 60000 }).json();
}

export const SettingsAPI = {
  saveSettings,
  getSettings,
  setUserAvatar,
  getUserAvatar,
  checkKey,
};
