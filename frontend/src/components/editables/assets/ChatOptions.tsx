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
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { Icon } from '@/components/common/icons/Icon';
import { useClickOutside } from '@/utils/common/useClickOutside';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { Agent, Material } from '@/types/editables/assetTypes';
import { ActorAvatar } from '../chat/ActorAvatar';
import clsx from 'clsx';

type ChatOptionsProps = {
  onSelectAgentId: (id: string) => void;
  handleMaterialSelect: (material: Material) => void;
  materialsOptions: Material[];
  setShowChatOptions: React.Dispatch<React.SetStateAction<boolean>>;
  inputRef: React.RefObject<HTMLInputElement>;
  textAreaRef: React.RefObject<HTMLTextAreaElement>;
};

const MaterialIcon = ({ option }: { option: Material }) => {
  const OptionIcon = getEditableObjectIcon(option);

  return <Icon icon={OptionIcon} className="w-6 h-6 min-h-6 min-w-6 text-material flex-shrink-0" />;
};

const ChatOptions = ({
  onSelectAgentId,
  handleMaterialSelect,
  materialsOptions,
  setShowChatOptions,
  inputRef,
  textAreaRef,
}: ChatOptionsProps) => {
  const chat = useChatStore((state) => state.chat);
  const agents = useEditablesStore((state) => state.agents);
  const [inputValue, setInputValue] = useState('');
  const [filteredMaterialsOptions, setFilteredMaterialsOptions] = useState<Material[]>([]);
  const [filteredAgentsOptions, setFilteredAgentsOptions] = useState<Agent[]>(agents);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const isChatLoading = useChatStore((state) => state.isChatLoading);
  const [focusedIndex, setFocusedIndex] = useState(0);

  useEffect(() => {
    setFilteredMaterialsOptions(materialsOptions);
  }, [materialsOptions]);

  useEffect(() => {
    const filtredAgents = agents.filter((item) => item.status === 'enabled');
    setFilteredAgentsOptions(filtredAgents);
  }, [agents]);

  useEffect(() => {
    if (focusedIndex >= 0) {
      const buttons = wrapperRef.current?.querySelectorAll('.options-list button') as NodeListOf<HTMLButtonElement>;
      const buttonToFocus = buttons?.[focusedIndex];
      buttonToFocus?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [focusedIndex]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setInputValue(inputValue);

    const regex = new RegExp(`^${inputValue}`, 'i');
    const filteredMaterialOptions = materialsOptions.filter((item) => regex.test(item.name));
    const filteredAgentOptions = agents
      .filter((item) => regex.test(item.name))
      .filter((item) => item.status === 'enabled');
    setFilteredAgentsOptions(filteredAgentOptions);
    setFilteredMaterialsOptions(filteredMaterialOptions);
  };

  const handleKeydown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    const itemCount = filteredAgentsOptions.length + filteredMaterialsOptions.length;
    if ((e.nativeEvent.key === 'Backspace' && inputValue === '') || e.nativeEvent.key === 'Escape') {
      setShowChatOptions(false);
      setFocusedIndex(0);
      textAreaRef?.current?.focus();
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocusedIndex((prevIndex) => {
        const nextIndex = prevIndex - 1;
        if (nextIndex < 0) {
          return prevIndex;
        }
        return nextIndex;
      });
    }
    if (e.nativeEvent.key === 'ArrowDown') {
      e.preventDefault();
      setFocusedIndex((prevIndex) => {
        const nextIndex = prevIndex + 1;
        if (nextIndex >= itemCount) {
          return prevIndex;
        }
        return nextIndex;
      });
    }
    if (e.key === 'Escape') {
      e.preventDefault();
      setFocusedIndex(0);
      setShowChatOptions(false);
      textAreaRef?.current?.focus();
    }

    if (e.key === 'Enter') {
      e.preventDefault();
      e.stopPropagation();
      const currentOption = options[focusedIndex];
      if (currentOption) {
        currentOption.type === 'agent'
          ? onSelectAgentId(currentOption.id)
          : handleMaterialSelect(currentOption as Material);
        setInputValue('');
        setShowChatOptions(false);
        textAreaRef?.current?.focus();
      }
    }
  };

  const handleClickOutside = () => {
    setInputValue('');
    setShowChatOptions(false);
  };

  useClickOutside(wrapperRef, handleClickOutside);

  const handleListKeyDown = (e: React.KeyboardEvent<HTMLUListElement>) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
    }
  };

  if (!chat && !isChatLoading) {
    return;
  }

  const options = [...filteredAgentsOptions, ...filteredMaterialsOptions];

  return (
    <div
      style={{ width: 'calc(100% - 60px)', bottom: 'calc(100% + 8px)' }}
      className="flex flex-col py-3 px-2 w-full bg-gray-800 rounded-[8px] min-h-[104px] absolute w-full border border-gray-600"
    >
      <div className="relative flex flex-col gap-2" ref={wrapperRef}>
        <input
          autoComplete="off"
          autoCorrect="off"
          spellCheck="false"
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeydown}
          placeholder="Search for an agent or material"
          className="bg-transparent p-2 focus:outline-none border-gray-400 text-white w-full placeholder:text-gray-400 placeholder:text-[15px]"
          disabled={isChatLoading}
          ref={inputRef}
        />
        <ul className="options-list max-h-[266px] overflow-y-auto" onKeyDown={handleListKeyDown} tabIndex={0}>
          {options.length === 0 ? (
            <p className="text-sm p-2 text-gray-400">There is no agent or material with this name.</p>
          ) : (
            options
              .sort((a, b) => a.name.localeCompare(b.name))
              .map((option) => {
                return (
                  <li key={option.id}>
                    <button
                      className={clsx(
                        'w-full overflow-hidden px-2 py-2.5 flex items-center cursor-pointer hover:bg-gray-600 rounded-[8px] max-h-[44px] gap-2 group focus:outline-none',
                        focusedIndex === options.indexOf(option) && 'bg-gray-600',
                      )}
                      onClick={() =>
                        option.type === 'agent' ? onSelectAgentId(option.id) : handleMaterialSelect(option as Material)
                      }
                    >
                      <div className="w-6 h-6 flex-shrink-0">
                        {option.type === 'agent' ? (
                          <ActorAvatar
                            actorType="agent"
                            actorId={option.id}
                            title={option.name}
                            type="extraSmall"
                            className="!mb-0 !mt-0"
                          />
                        ) : (
                          <MaterialIcon option={option as Material} />
                        )}
                      </div>
                      <h4 className="text-white ml-[4px] text-[15px] flex-shrink-0">{option.name}</h4>
                      <span className="text-sm truncate text-gray-400">{option.usage}</span>
                    </button>
                  </li>
                );
              })
          )}
        </ul>
      </div>
    </div>
  );
};

export default ChatOptions;
