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

import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import { Trash, Pencil, Save, X, Copy,Check } from 'lucide-react';
import { useState } from 'react';
interface MessageControlsProps {
  isEditing?: boolean;
  hideControls?: boolean;
  onSaveClick?: () => void;
  onEditClick?: () => void;
  onRemoveClick?: () => void;
  onCancelClick?: () => void;
  onCopyText?:string
}

export function MessageControls({
  isEditing,
  hideControls,
  onSaveClick,
  onCancelClick,
  onEditClick,
  onRemoveClick,
   onCopyText
}: MessageControlsProps) {
  const [isCopied, setIsCopied] = useState(false);
 
  const handleCopyClick = async () => {
     if (!onCopyText) onCopyText = '';
    try {
      await navigator.clipboard.writeText(onCopyText);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2500); 
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  return (
    <div className="min-w-[48px]">
      {isEditing ? (
        <div className="flex justify-between">
          {onSaveClick ? (
            <button>
              <Icon icon={Save} width={20} height={20} onClick={onSaveClick} />
            </button>
          ) : (
            <div className="h-4 w-4"></div>
          )}
          <button>
            <Icon icon={X} width={20} height={20} onClick={onCancelClick} />{' '}
          </button>
        </div>
      ) : (
        <div
          className={cn('flex flex-none gap-4 justify-end', {
            'hidden group-hover:flex': hideControls,
          })}
        >
          {onSaveClick && onEditClick && onCancelClick ? (
            <button onClick={onEditClick}>
              <Icon icon={Pencil} className="pointer-events-none" />{' '}
            </button>
          ) : (
            <div className="h-4 w-4"></div>
          )}
               {handleCopyClick && (
            <button onClick={handleCopyClick}>
               {isCopied ? 
              <Icon icon={Check} />:<Icon icon={Copy} />  }
            </button>
          )}
          {onRemoveClick && (
            <button onClick={onRemoveClick}>
              <Icon icon={Trash} />{' '}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
