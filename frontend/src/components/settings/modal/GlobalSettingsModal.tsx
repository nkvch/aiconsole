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

import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { Content, Portal, Root } from '@radix-ui/react-dialog';

import TopGradient from '@/components/common/TopGradient';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { Button } from '../../common/Button';
import { Icon } from '../../common/icons/Icon';
import GlobalSettingsApiSection from './sections/GlobalSettingsApiSection';
import GlobalSettingsCodeSection from './sections/GlobalSettingsCodeSection';
import GlobalSettingsUserSection from './sections/GlobalSettingsUserSection';

// TODO: implement other features from figma like api for azure, user profile and tutorial
export const GlobalSettingsModal = () => {
  const isSettingsModalVisible = useSettingsStore((state) => state.isSettingsModalVisible);
  const setSettingsModalVisibility = useSettingsStore((state) => state.setSettingsModalVisibility);

  const [usernameFormValue, setUsernameFormValue] = useState<string | undefined>(undefined);
  const display_name = useSettingsStore((state) => state.settings.user_profile?.display_name);
  useEffect(() => {
    setUsernameFormValue(display_name);
  }, [display_name]);

  const [profilePictureFormValue, setProfilePictureFormValue] = useState<string | undefined>(undefined);
  const profile_picture = useSettingsStore((state) => state.settings.user_profile?.profile_picture);
  useEffect(() => {
    setProfilePictureFormValue(profile_picture);
  }, [profile_picture]);

  const [apiKeyValue, setApiKeyValue] = useState<string | undefined>(undefined);
  const openai_api_key = useSettingsStore((state) => state.settings.openai_api_key);
  useEffect(() => {
    setApiKeyValue(openai_api_key || '');
  }, [openai_api_key]);

  const [isAutoRun, setIsAutoRun] = useState(false);
  const code_autorun = useSettingsStore((state) => !!state.settings.code_autorun);
  useEffect(() => {
    setIsAutoRun(code_autorun);
  }, [code_autorun]);

  const [userAvatarData, setUserAvatarData] = useState<File>();
  const [isAvatarOverwritten, setIsAvatarOverwritten] = useState(false);

  const handleAutoRunChange = (autorun: boolean) => {
    setIsAutoRun(autorun);
  };

  const save = async () => {
    let avatarFormData: FormData | null = null;

    // check if avatar was overwritten to avoid sending unnecessary requests
    if (isAvatarOverwritten && userAvatarData) {
      avatarFormData = new FormData();
      avatarFormData.append('avatar', userAvatarData);
    }

    useSettingsStore.getState().saveSettings(
      {
        user_profile:
          usernameFormValue !== display_name || profilePictureFormValue !== profile_picture
            ? {
                display_name: usernameFormValue !== display_name ? usernameFormValue : undefined,
                profile_picture: profilePictureFormValue !== profile_picture ? profilePictureFormValue : undefined,
              }
            : undefined,
        openai_api_key: apiKeyValue !== openai_api_key ? apiKeyValue : undefined,
        code_autorun: isAutoRun !== code_autorun ? isAutoRun : undefined,
      },
      true,
      avatarFormData,
    );
    setSettingsModalVisibility(false);
  };

  const handleSetAvatarImage = (avatar: File) => {
    setUserAvatarData(avatar);
    setIsAvatarOverwritten(true);
  };

  useEffect(() => {
    const resetState = () => {
      setUsernameFormValue(display_name);
      setApiKeyValue(openai_api_key);
      setIsAutoRun(code_autorun);
      setUserAvatarData(undefined);
      setIsAvatarOverwritten(false);
    };

    if (isSettingsModalVisible) {
      resetState();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSettingsModalVisible]); // reset state when modal is closed or opened

  const handleModalClose = () => {
    setSettingsModalVisibility(false);
  };

  return (
    <Root open={isSettingsModalVisible}>
      <Portal>
        <Content asChild className="fixed" onEscapeKeyDown={handleModalClose}>
          <div className="w-full h-[100vh] z-[99] top-0 left-0 right-0 bg-gray-900">
            <TopGradient />
            <div className="flex justify-between items-center px-[30px] py-[26px] relative z-10">
              <img src={`favicon.svg`} className="h-[48px] w-[48px] cursor-pointer filter" />
              <h3 className="text-gray-400 text-[14px] leading-[21px]">AIConsole settings</h3>
              <Button variant="secondary" onClick={handleModalClose} small>
                <Icon icon={X} />
                Close
              </Button>
            </div>

            <div className="h-[calc(100%-100px)] max-w-[720px] mx-auto relative flex flex-col justify-center gap-5">
              <GlobalSettingsUserSection
                username={usernameFormValue}
                setUsername={setUsernameFormValue}
                setImage={handleSetAvatarImage}
              />

              <GlobalSettingsApiSection apiKey={openai_api_key} setApiKey={setApiKeyValue} />
              <GlobalSettingsCodeSection isAutoRun={isAutoRun} setIsAutoRun={handleAutoRunChange} />
              <div className="flex items-center justify-end gap-[10px] py-[40px]">
                <Button variant="secondary" bold onClick={handleModalClose}>
                  Cancel
                </Button>
                <Button onClick={save}>{'Save'}</Button>
              </div>
            </div>
          </div>
        </Content>
      </Portal>
    </Root>
  );
};
