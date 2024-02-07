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

import { ChangeEvent, useEffect, useRef, useState } from 'react';
import { cn } from '@/utils/common/cn';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { Icon } from '@/components/common/icons/Icon';
import { useClickOutside } from '@/utils/common/useClickOutside';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { Agent, Material } from '@/types/editables/assetTypes';
import { ActorAvatar } from '../chat/ActorAvatar';

type ChatOptionsProps = {
  onSelectAgentId: (id: string) => void;
  handleMaterialSelect: (material: Material) => void;
  materialsOptions: Material[];
};

const ChatOption = ({ option, selectOption }: { option: Material; selectOption: (option: Material) => void }) => {
  const OptionIcon = getEditableObjectIcon(option);

  return (
    <button
      className="flex justify-between items-center max-w-full w-max gap-3 hover:bg-gray-600 px-2 py-1 rounded-[8px] max-h-[32px] group"
      onClick={() => selectOption(option)}
    >
      <Icon icon={OptionIcon} className="w-6 h-6 min-h-6 min-w-6 text-material" />
      <p className="flex-1 truncate font-normal text-sm text-gray-400 group-hover:text-white">{option.name}</p>
    </button>
  );
};

const ChatOptions = ({ onSelectAgentId, handleMaterialSelect, materialsOptions }: ChatOptionsProps) => {
  const chat = useChatStore((state) => state.chat);
  const agents = useEditablesStore((state) => state.agents);
  const [inputValue, setInputValue] = useState('');
  const [filteredMaterialOptions, setFilteredMaterialOptions] = useState<Material[]>([]);
  const [filteredAgentsOptions, setFilteredAgentsOptions] = useState<Agent[]>(agents);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const isChatLoading = useChatStore((state) => state.isChatLoading);

  useEffect(() => {
    setFilteredMaterialOptions(materialsOptions);
  }, [materialsOptions]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setInputValue(inputValue);

    const regex = new RegExp(`^${inputValue}`, 'i');
    const filteredMaterialOptions = materialsOptions.filter((item) => regex.test(item.name));
    const filteredAgentOptions = agents.filter((item) => regex.test(item.name));
    setFilteredAgentsOptions(filteredAgentOptions);
    setFilteredMaterialOptions(filteredMaterialOptions);
  };

  const handleClickOutside = () => {
    setInputValue('');
  };

  useClickOutside(wrapperRef, handleClickOutside);

  if (!chat && !isChatLoading) {
    return;
  }

  return (
    <div
      style={{ width: 'calc(100% - 60px)', bottom: 'calc(100% + 8px)' }}
      className="flex flex-col py-3 px-2 w-full bg-gray-800 rounded-[8px] min-h-[164px] absolute w-full border border-gray-600"
    >
      <div className="relative flex flex-col gap-2" ref={wrapperRef}>
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Search for an agent or material"
          className="bg-transparent p-2 focus:outline-none border-gray-400 text-white w-full placeholder:text-gray-400 placeholder:text-[15px]"
          disabled={isChatLoading}
        />
        <ul className="max-h-[134px] overflow-y-auto">
          {filteredAgentsOptions.length === 0 ? (
            <p className="text-sm p-2 text-gray-400">There is no agent with this name.</p>
          ) : (
            filteredAgentsOptions.map((option) => {
              return (
                <li
                  key={option.id}
                  className={cn(
                    'w-full overflow-hidden px-2 py-2.5 flex items-center cursor-pointer hover:bg-gray-600 rounded-[8px] max-h-[44px] gap-2 group',
                  )}
                  onClick={() => onSelectAgentId(option.id)}
                >
                  <ActorAvatar
                    actorType="agent"
                    actorId={option.id}
                    title={option.name}
                    type="extraSmall"
                    className="!mb-0 !mt-0"
                  />
                  <h4 className="text-white ml-[4px] text-[15px]">{option.name}</h4>
                  <span className="text-sm truncate text-gray-400">{option.usage}</span>
                </li>
              );
            })
          )}
        </ul>
        <div className="h-1 border-b border-gray-600" />
        <div className="max-h-[76px] overflow-y-auto flex gap-2 w-full flex-wrap">
          {materialsOptions.length === 0 && <p className="text-sm p-2 text-gray-400">There is no more materials.</p>}
          {filteredMaterialOptions.length === 0 && materialsOptions.length !== 0 && (
            <p className="text-sm p-2 text-gray-400">There is no material with this name.</p>
          )}
          {filteredMaterialOptions.length !== 0 &&
            materialsOptions.length !== 0 &&
            filteredMaterialOptions.map((option) => (
              <ChatOption option={option} selectOption={handleMaterialSelect} key={option.id} />
            ))}
        </div>
      </div>
    </div>
  );
};

export default ChatOptions;
