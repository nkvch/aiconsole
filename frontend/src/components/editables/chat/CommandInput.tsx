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

import { Button } from '@/components/common/Button';
import Tooltip from '@/components/common/Tooltip';
import { Icon } from '@/components/common/icons/Icon';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { cn } from '@/utils/common/cn';
import { LucideIcon, X } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import ChatOptions from '../assets/ChatOptions';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { ActorAvatar } from './ActorAvatar';
import { useDebounceCallback } from '@mantine/hooks';
import { ChatAPI } from '@/api/api/ChatAPI';
import { Material } from '@/types/editables/assetTypes';

interface MessageInputProps {
  actionIcon: LucideIcon | ((props: React.SVGProps<SVGSVGElement>) => JSX.Element);
  className?: string;
  actionLabel: string;
  onSubmit?: (command: string) => void;
}

export const CommandInput = ({ className, onSubmit, actionIcon, actionLabel }: MessageInputProps) => {
  const ActionIcon = actionIcon;
  const [showChatOptions, setShowChatOptions] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const command = useChatStore((state) => state.commandHistory[state.commandIndex]);

  const setCommand = useChatStore((state) => state.editCommand);
  const promptUp = useChatStore((state) => state.historyUp);
  const promptDown = useChatStore((state) => state.historyDown);
  const chat = useChatStore((state) => state.chat);
  const agents = useEditablesStore((state) => state.agents);
  const setChat = useChatStore((state) => state.setChat);
  const materials = useEditablesStore((state) => state.materials);
  const [materialsOptions, setMaterialsOptions] = useState<Material[]>([]);
  const [chosenMaterials, setChosenMaterials] = useState<Material[]>([]);
  const materialsIds = chosenMaterials.map((material) => material.id);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const chatOptionsInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = useCallback(
    async (e?: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
      if (onSubmit) onSubmit(command);

      if (e) e.currentTarget.blur();
    },
    [command, onSubmit],
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setCommand(e.target.value);
      const mentionMatch = e.target.value.match(/@(\s*)$/);
      setShowChatOptions(!!mentionMatch);

      setTimeout(() => {
        chatOptionsInputRef?.current?.focus();
      }, 0);
    },
    [setCommand],
  );

  const handleKeyDown = useCallback(
    async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();

        await handleSendMessage();
      }

      if (textAreaRef.current) {
        const caretAtStart = textAreaRef.current.selectionStart === 0 && textAreaRef.current.selectionEnd === 0;
        const caretAtEnd =
          textAreaRef.current.selectionStart === textAreaRef.current.value.length &&
          textAreaRef.current.selectionEnd === textAreaRef.current.value.length;

        if (e.key === 'ArrowUp' && caretAtStart) {
          promptUp();
        } else if (e.key === 'ArrowDown' && caretAtEnd) {
          promptDown();
        }

        if (e.key === 'Backspace' && caretAtStart) {
          if (chosenMaterials.length > 0) {
            const newChosenMaterials = [...chosenMaterials];
            newChosenMaterials.pop();
            setChosenMaterials(newChosenMaterials);
          } else {
            setSelectedAgentId('');
          }
        }
      }
    },
    [handleSendMessage, promptDown, promptUp, chosenMaterials, setSelectedAgentId, setChosenMaterials],
  );

  // auto focus this text area on changes to chatId
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, [chat?.id]);

  useEffect(() => {
    setSelectedAgentId('');
    setChosenMaterials([]);
  }, [chat?.id]);

  useEffect(() => {
    if (chat?.chat_options.agent_id) {
      setSelectedAgentId(chat?.chat_options.agent_id);
    }
  }, [chat?.chat_options.agent_id, chat?.id]);

  useEffect(() => {
    const filteredMaterials = materials?.filter(({ id }) => (chat?.chat_options.materials_ids || []).includes(id));
    if (filteredMaterials) {
      setChosenMaterials(filteredMaterials);
    }
  }, [chat?.chat_options.materials_ids, materials, chat?.id]);

  useEffect(() => {
    setMaterialsOptions(
      materials
        ?.filter((material) => !chosenMaterials.includes(material))
        .filter((item) => item.status === 'enabled') as Material[],
    );
  }, [chat?.id, materials, chosenMaterials]);

  const getAgent = (agentId: string) => agents.find((agent) => agent.id === agentId);

  const debounceChatUpdate = useDebounceCallback(async () => {
    try {
      if (chat) {
        ChatAPI.patchChatOptions(chat?.id, {
          agent_id: selectedAgentId,
          materials_ids: materialsIds,
        });

        setChat({
          ...chat,
          chat_options: {
            agent_id: selectedAgentId,
            materials_ids: materialsIds,
          },
        });
      }
    } catch (error) {
      console.error('An error occurred while updating chat options:', error);
    }
  }, 500);

  const removeLastAt = () => {
    if (command.endsWith('@')) {
      const newCommand = command.slice(0, -1);
      setCommand(newCommand);
    }
  };

  const onSelectAgentId = (id: string) => {
    setSelectedAgentId(id);
    debounceChatUpdate();
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const removeAgentId = () => {
    setSelectedAgentId('');
    debounceChatUpdate();
  };

  const handleMaterialSelect = (material: Material) => {
    setChosenMaterials((prev) => [...prev, material]);
    const filteredOptions = materialsOptions
      .filter(({ id }) => id !== material.id)
      .filter((item) => item.status === 'enabled');
    setMaterialsOptions(filteredOptions);
    debounceChatUpdate();
    setShowChatOptions(false);
    removeLastAt();
    setTimeout(() => {
      textAreaRef?.current?.focus();
    }, 0);
  };

  const removeSelectedMaterial = (id: string) => () => {
    const material = chosenMaterials.find((material) => material.id === id) as Material;
    setChosenMaterials((prev) => prev.filter(({ id }) => id !== material.id));
    setMaterialsOptions((prev) => [...prev, material].sort((a, b) => a.name.localeCompare(b.name)));
    debounceChatUpdate();
  };

  const handleFocus = useCallback(() => {
    setShowChatOptions(false);
  }, []);

  return (
    <div className={cn(className, 'flex w-full flex-col px-4 py-[20px]  bg-gray-900 z-50 ')}>
      <div className="flex items-end gap-[10px] max-w-[700px] w-full mx-auto relative">
        {showChatOptions && (
          <ChatOptions
            onSelectAgentId={onSelectAgentId}
            handleMaterialSelect={handleMaterialSelect}
            setShowChatOptions={setShowChatOptions}
            materialsOptions={materialsOptions}
            inputRef={chatOptionsInputRef}
            textAreaRef={textAreaRef}
          />
        )}
        <div className="w-full max-h-[200px] overflow-y-auto border border-gray-500 bg-gray-800 hover:bg-gray-600 focus-within:bg-gray-600 focus-within:border-gray-400 transition duration-100 rounded-[8px] flex flex-col flex-grow resize-none">
          {(selectedAgentId || chosenMaterials.length > 0) && (
            <div className="px-[20px] py-[12px] w-full flex flex-col gap-2">
              {selectedAgentId && (
                <div className="w-full flex jusify-between items-center">
                  <div className="flex items-center gap-3 w-full">
                    <ActorAvatar
                      actorType="agent"
                      actorId={selectedAgentId}
                      title="test"
                      type="extraSmall"
                      className="!mb-0 !mt-0"
                    />
                    <p className="text-[15px]">
                      Talking to <span className="text-white">{getAgent(selectedAgentId)?.name}</span>
                    </p>
                  </div>
                  <Icon
                    icon={X}
                    className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer')}
                    onClick={removeAgentId}
                  />
                </div>
              )}
              {chosenMaterials.length > 0 && (
                <div className="flex gap-2">
                  <span className="text-gray-400 text-[14px]">Using:</span>
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-1 overflow-y-auto max-h-[52px]">
                    {chosenMaterials.map((material) => (
                      <div key={material.id} className="flex gap-1 items-center">
                        <span className="text-gray-300 text-[14px]">{material.name}</span>
                        <Icon
                          icon={X}
                          className={cn('w-4 h-4 min-h-4 min-w-4 flex-shrink-0 cursor-pointer text-gray-400')}
                          onClick={removeSelectedMaterial(material.id)}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <TextareaAutosize
            ref={textAreaRef}
            className="w-full bg-transparent text-[15px] text-white resize-none overflow-y-auto px-[20px] py-[12px] placeholder:text-gray-400 hover:placeholder:text-gray-300 focus:outline-none"
            value={command}
            onChange={handleChange}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
            placeholder={`Type "@" to select a specific agent or materials`}
            rows={1}
          />
        </div>

        <Tooltip label={actionLabel} position="top" align="center" sideOffset={10} disableAnimation withArrow>
          <div>
            <Button variant="primary" iconOnly={true} onClick={handleSendMessage} classNames={cn('p-[12px]', {})}>
              <Icon icon={ActionIcon} width={24} height={24} className="w-6 h-6" />
            </Button>
          </div>
        </Tooltip>
      </div>
    </div>
  );
};
