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

import { useChatStore } from '@/store/editables/chat/useChatStore';
import * as ReactCheckbox from '@radix-ui/react-checkbox';
import { Check } from 'lucide-react';
import { FC } from 'react';

type CheckboxProps = {
  checked: boolean;
  id: string;
  disabled?: boolean;
  onChange: (checked: boolean) => void;
};

const Checkbox: FC<CheckboxProps> = ({ checked, id, onChange }) => {
  const handleCheckedChange = (isChecked: ReactCheckbox.CheckedState) => onChange(isChecked === true);
  const isChatLoading = useChatStore((state) => state.isChatLoading);

  return (
    <ReactCheckbox.Root
      className="hover:bg-violet3 flex h-[24px] w-[24px] appearance-none items-center justify-center rounded-[4px] bg-transparent outline outline-1 outline-gray-500 m-[1px] text-white focus:outline-gray-400 hover:outline-gray-400 disabled:hover:outline-gray-500"
      checked={checked}
      id={id}
      onCheckedChange={handleCheckedChange}
      disabled={isChatLoading}
    >
      <ReactCheckbox.Indicator>
        <Check />
      </ReactCheckbox.Indicator>
    </ReactCheckbox.Root>
  );
};

export default Checkbox;
