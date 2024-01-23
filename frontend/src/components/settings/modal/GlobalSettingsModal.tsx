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

import { useEffect } from 'react';
import { X } from 'lucide-react';
import { Content, Portal, Root } from '@radix-ui/react-dialog';
import { useForm } from 'react-hook-form';

import TopGradient from '@/components/common/TopGradient';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { Button } from '../../common/Button';
import { Icon } from '../../common/icons/Icon';
import GlobalSettingsApiSection from './sections/GlobalSettingsApiSection';
import GlobalSettingsCodeSection from './sections/GlobalSettingsCodeSection';
import GlobalSettingsUserSection from './sections/GlobalSettingsUserSection';
import { GlobalSettingsFormData } from '@/forms/globalSettingsForm';

// TODO: implement other features from figma like api for azure, user profile and tutorial
export const GlobalSettingsModal = () => {
  const isSettingsModalVisible = useSettingsStore((state) => state.isSettingsModalVisible);
  const setSettingsModalVisibility = useSettingsStore((state) => state.setSettingsModalVisibility);

  const username = useSettingsStore((state) => state.username);
  const email = useSettingsStore((state) => state.userEmail);
  const userAvatarUrl = useSettingsStore((state) => state.userAvatarUrl);
  const openAiApiKey = useSettingsStore((state) => state.openAiApiKey);

  const { reset, control, setValue } = useForm<GlobalSettingsFormData>();

  useEffect(() => {
    if (isSettingsModalVisible) {
      reset({
        user_profile: {
          username,
          email: email || '',
        },
        openai_api_key: openAiApiKey,
        avatarUrl: userAvatarUrl,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSettingsModalVisible]);

  // const [usernameFormValue, setUsernameFormValue] = useState<string | undefined>(undefined);
  //
  // useEffect(() => {
  //   setUsernameFormValue(username);
  // }, [username]);

  // const [emailFormValue, setEmailFormValue] = useState<string | undefined>(undefined);
  //
  // useEffect(() => {
  //   setEmailFormValue(email);
  // }, [email]);

  // const [apiKeyValue, setApiKeyValue] = useState<string | undefined>(openAiApiKey);

  // useEffect(() => {
  //   setApiKeyValue(openAiApiKey || '');
  // }, [openAiApiKey]);

  // const [isAutoRun, setIsAutoRun] = useState(false);
  // const alwaysExecuteCode = useSettingsStore((state) => state.alwaysExecuteCode);
  // useEffect(() => {
  //   setIsAutoRun(alwaysExecuteCode);
  // }, [alwaysExecuteCode]);

  // const [userAvatarData, setUserAvatarData] = useState<File>();
  // const [isAvatarOverwritten, setIsAvatarOverwritten] = useState(false);

  // const handleAutoRunChange = (autorun: boolean) => {
  //   setIsAutoRun(autorun);
  // };

  // const save = async () => {
  //   let avatarFormData: FormData | null = null;

  //   // check if avatar was overwritten to avoid sending unnecessary requests
  //   if (isAvatarOverwritten && userAvatarData) {
  //     avatarFormData = new FormData();
  //     avatarFormData.append('avatar', userAvatarData);
  //   }

  //   useSettingsStore.getState().saveSettings(
  //     {
  //       user_profile:
  //         usernameFormValue !== username || emailFormValue !== email
  //           ? {
  //               username: usernameFormValue !== username ? usernameFormValue : undefined,
  //               email: emailFormValue !== email ? emailFormValue : undefined,
  //             }
  //           : undefined,
  //       openai_api_key: apiKeyValue !== openAiApiKey ? apiKeyValue : undefined,
  //       code_autorun: isAutoRun !== alwaysExecuteCode ? isAutoRun : undefined,
  //     },
  //     true,
  //     avatarFormData,
  //   );
  //   setSettingsModalVisibility(false);
  // };

  const handleSetAvatarImage = (avatar: File) => setValue('avatar', avatar);

  // useEffect(() => {
  //   const resetState = () => {
  //     setUsernameFormValue(username);
  //     setEmailFormValue(email);
  //     setApiKeyValue(openAiApiKey);
  //     setIsAutoRun(alwaysExecuteCode);
  //     setUserAvatarData(undefined);
  //     setIsAvatarOverwritten(false);
  //   };

  //   if (isSettingsModalVisible) {
  //     resetState();
  //   }
  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  // }, [isSettingsModalVisible]); // reset state when modal is closed or opened

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
                control={control}
                avatarUrl={userAvatarUrl}
                onImageSelected={handleSetAvatarImage}
              />
              {/* <GlobalSettingsApiSection apiKey={apiKeyValue} setApiKey={setApiKeyValue} />
              <GlobalSettingsCodeSection isAutoRun={isAutoRun} setIsAutoRun={handleAutoRunChange} />
               */}
              <div className="flex items-center justify-end gap-[10px] py-[40px]">
                <Button variant="secondary" bold onClick={handleModalClose}>
                  Cancel
                </Button>
                <Button>{'Save'}</Button>
              </div>
            </div>
          </div>
        </Content>
      </Portal>
    </Root>
  );
};
