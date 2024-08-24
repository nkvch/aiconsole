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

import { useState } from 'react';

import { Button } from '../common/Button';
import { useApiKey } from '@/utils/settings/useApiKey';
import { useToastsStore } from '@/store/common/useToastsStore';
import { TextInput } from '../editables/assets/TextInput';

const OpenAiApiKeyForm = () => {
  const [inputText, setInputText] = useState('');
  const { validating, setApiKey, saveOpenAiApiKey } = useApiKey();

  const showToast = useToastsStore((state) => state.showToast);

  const onFormSubmit = async () => {
    const successfulySet = await setApiKey(inputText);

    if (successfulySet) {
      setInputText('');
      saveOpenAiApiKey(inputText);
      showToast({
        title: 'Success',
        message: 'Open AI API key was successfully set.',
        variant: 'success',
      });
    }
  };

  return (
    <div>
      <div className="p-10 border border-gray-600 rounded-[14px] my-[60px] flex flex-col gap-5 bg-top-elipse">
        <p className="text-lg text-center font-semibold text-white">
          To start, provide your OpenAI API key with GPT-4 access.
        </p>
        <div className="flex justify-center gap-5 w-full">
          <TextInput fullWidth value={inputText} onChange={setInputText} placeholder="OpenAI API key..." name="api" />
          <Button small onClick={onFormSubmit} disabled={!inputText}>
            {validating ? 'Validating...' : 'Add API key'}
          </Button>
        </div>
      </div>

      <div className="flex flex-col text-center h-[102px] justify-between">
        <p className="text-[15px] leading-6	text-gray-400">
          To get your own OpenAI API key you need to raise a $1 dollar payment by setting up your payment method in
          OpenAI settings pannel.
        </p>
        <a
          className="text-gray-300 underline"
          href="https://help.openai.com/en/articles/7102672-how-can-i-access-gpt-4"
          target="_blank"
        >
          How can I access GPT-4? | OpenAI Help Center
        </a>
      </div>
    </div>
  );
};

export default OpenAiApiKeyForm;
