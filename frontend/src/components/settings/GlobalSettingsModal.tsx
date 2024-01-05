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

import { useApiKey } from '@/utils/settings/useApiKey';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { Ban, Check, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Button } from '../common/Button';
import { useLocation, useNavigate } from 'react-router-dom';
import { Icon } from '../common/icons/Icon';
import { Root, Portal, Content } from '@radix-ui/react-dialog';
import { useDisclosure } from '@mantine/hooks';
import { TextInput } from '../editables/assets/TextInput';

// TODO: implement other features from figma like api for azure, user profile and tutorial
export const GlobalSettingsModal = () => {
  const openAiApiKey = useSettingsStore((state) => state.openAiApiKey);

  const alwaysExecuteCode = useSettingsStore((state) => state.alwaysExecuteCode);
  const [inputText, setInputText] = useState(openAiApiKey || '');
  const [isAutoRun, setIsAutoRun] = useState(alwaysExecuteCode);

  const { validating, setApiKey, saveOpenAiApiKey } = useApiKey();
  const location = useLocation();
  const isSettingsModalVisible = useMemo(
    () => location.state?.isSettingsModalVisible,
    [location.state?.isSettingsModalVisible],
  );
  const navigate = useNavigate();

  const handleOpen = () => {
    if (openAiApiKey) {
      setInputText(openAiApiKey);
    }
  };

  const onClose = () => {
    navigate(location.pathname, {
      state: { ...location.state, isSettingsModalVisible: false },
    });
  };

  const [opened, { close, open }] = useDisclosure(isSettingsModalVisible, { onClose, onOpen: handleOpen });

  useEffect(() => {
    if (isSettingsModalVisible) {
      open();
    } else {
      close();
    }
  }, [close, isSettingsModalVisible, open]);

  const setAutoCodeExecution = useSettingsStore((state) => state.setAutoCodeExecution);

  const save = async () => {
    if (isAutoRun !== alwaysExecuteCode) {
      setAutoCodeExecution(isAutoRun);
    }
    if (inputText !== openAiApiKey) {
      await setApiKey(inputText);

      saveOpenAiApiKey(inputText);
    }

    close();
  };

  return (
    <Root open={opened} onOpenChange={close}>
      <Portal>
        <Content asChild className="fixed">
          <div className="w-full h-[100vh] z-[99] top-0 left-0 right-0 bg-gray-900">
            <div className="flex justify-between items-center px-[30px] py-[26px]">
              <img src={`favicon.svg`} className="h-[48px] w-[48px] cursor-pointer filter" />
              <Button variant="secondary" onClick={close} small>
                <Icon icon={X} />
                Close
              </Button>
            </div>

            <div className="h-[calc(100%-100px)] max-w-[720px] mx-auto">
              <h3 className="uppercase p-[30px] text-gray-400 text-[14px] leading-[21px] text-center mb-[40px]">
                Settings
              </h3>
              <div className="flex flex-col gap-[40px]">
                <h3 className="text-gray-400 text-[14px] leading-5">System settings</h3>
                <div className="flex items-center gap-[30px]">
                  <h4 className="text-gray-300 font-semibold text-[16px] leading-[19px]">Always run code</h4>
                  <div className="flex items-center gap-[10px]">
                    <Button
                      statusColor={isAutoRun ? 'green' : 'base'}
                      variant="status"
                      onClick={() => setIsAutoRun(true)}
                    >
                      <Icon icon={Check} /> YES
                    </Button>
                    <Button
                      statusColor={isAutoRun == false ? 'red' : 'base'}
                      variant="status"
                      onClick={() => setIsAutoRun(false)}
                    >
                      <Icon icon={Ban} /> NO
                    </Button>
                  </div>
                </div>
                <div className="border border-gray-600 rounded-[8px] p-[20px]">
                  <TextInput
                    value={inputText}
                    onChange={setInputText}
                    horizontal
                    placeholder="OpenAI API key..."
                    label="API"
                    name="api"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end gap-[10px] py-[60px] mt-[40px]">
                <Button variant="secondary" bold onClick={close}>
                  Cancel
                </Button>
                <Button onClick={save}>{validating ? 'Validating...' : 'Save'}</Button>
              </div>
            </div>
          </div>
        </Content>
      </Portal>
    </Root>
  );
};
