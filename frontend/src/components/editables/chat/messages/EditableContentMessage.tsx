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

import { useCallback, useState } from 'react';
import { MessageControls } from './MessageControls';
import { TipTapEditor } from '../../assets/TipTapEditor';
import { cn } from '@/utils/common/cn';
import { useChatStore } from '@/store/editables/chat/useChatStore';

interface EditableContentMessageProps {
  initialContent: string;
  language?: string;
  children?: React.ReactNode;
  handleRemoveClick?: () => void;
  handleAcceptedContent: (content: string) => Promise<void>;
  className?: string;
  hideControls?: boolean;
  isEditing: boolean;
  setIsEditing: React.Dispatch<React.SetStateAction<boolean>>;
}

export function EditableContentMessage({
  initialContent,
  language,
  children,
  handleRemoveClick,
  handleAcceptedContent,
  className,
  hideControls,
  isEditing,
  setIsEditing,
}: EditableContentMessageProps) {
  const [content, setContent] = useState(initialContent);
  const [isBeingProcessed, setIsBeingProcessed] = useState(false);
  const lastUsedChat = useChatStore((state) => state.lastUsedChat);

  const handleOnChange = useCallback((value: string) => {
    setContent(value);
  }, []);

  const handleSaveClick = useCallback(async () => {
    setIsBeingProcessed(true);
    try {
      await handleAcceptedContent(content);
      setIsEditing(false);
    } finally {
      setIsBeingProcessed(false);
    }
  }, [content, handleAcceptedContent, setIsEditing]);

  const handleCancelEditClick = useCallback(() => {
    setContent(initialContent);
    setIsEditing(false);
  }, [initialContent, setIsEditing]);

  const handleEditClick = useCallback(() => {
    setIsEditing(true);
  }, [setIsEditing]);

  return (
    <div className={cn('flex flex-row items-start overflow-auto', className)}>
      {isEditing ? (
        <div className="rounded-md flex-grow ">
          <TipTapEditor
            className="resize-none border-0 bg-transparent w-full outline-none"
            value={content}
            onChange={handleOnChange}
            codeLanguage={language ? language : 'text'}
            transparent
            focused={isEditing}
            maxHeight="400px"
            minHeight="400px"
            onBlur={handleSaveClick}
          />
        </div>
      ) : (
        <div className="flex-grow overflow-auto ">{children}</div>
      )}

      <div
        className={cn('flex flex-none gap-4 px-4 self-start', {
          'min-w-[100px] ml-[92px]': hideControls,
        })}
      >
        {!isBeingProcessed && (
          <MessageControls
            isEditing={isEditing}
            hideControls={hideControls}
            onCancelClick={handleCancelEditClick}
            onEditClick={handleEditClick}
            onSaveClick={handleSaveClick}
            onRemoveClick={handleRemoveClick}
          />
        )}
      </div>
    </div>
  );
}
