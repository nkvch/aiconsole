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
import { useClickOutside } from '@/utils/common/useClickOutside';
import { Maximize2, Minimize2 } from 'lucide-react';
import { ReactNode, useCallback, useEffect, useRef, useState } from 'react';
import { CodeInputFullScreen } from './CodeInputFullScreen';
import { RichTextEditor } from './RichTextEditor';

const DEFAULT_MAX_HEIGHT = 'calc(100% - 60px)';
const DEFAULT_MIN_HEIGHT = '180px';

interface CodeInputProps {
  label?: string;
  value: string | ReactNode;
  labelContent?: ReactNode;
  labelSize?: 'sm' | 'md';
  className?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  codeLanguage?: string;
  disabled?: boolean;
  readOnly?: boolean;
  transparent?: boolean;
  maxHeight?: string;
  minHeight?: string;
  focused?: boolean;
  withFullscreen?: boolean;
  fullHeight?: boolean;
}

export function CodeInput({
  label,
  value,
  className,
  onChange,
  onBlur,
  codeLanguage,
  disabled = false,
  readOnly = false,
  transparent = false,
  maxHeight = DEFAULT_MAX_HEIGHT,
  minHeight = DEFAULT_MIN_HEIGHT,
  labelContent,
  labelSize = 'sm',
  focused,
  withFullscreen,
  fullHeight = false,
}: CodeInputProps) {
  const [focus, setFocus] = useState(false);
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
  const editorBoxRef = useRef<HTMLDivElement | null>(null);

  const handleValueChange = (code: string) => {
    if (onChange) {
      onChange(code);
    }
  };

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (editorBoxRef.current?.contains(event.target as HTMLElement)) {
        return;
      }

      if (focus) {
        setFocus(false);
        onBlur?.();
      }
    },
    [focus, onBlur],
  );

  useClickOutside(editorBoxRef, handleClickOutside);

  useEffect(() => {
    if (focused) {
      setFocus(true);
    }
  }, [focused]);

  useEffect(() => {
    if (!isFullscreenOpen) {
      setFocus(false);
    }
  }, [focused, isFullscreenOpen]);

  const toggleFullscreen = () => {
    setIsFullscreenOpen((prev) => !prev);
  };

  const codeInputCore = (fullScreen: boolean) => (
    <div className={cn('relative', { 'h-full': fullHeight })}>
      {label && (fullScreen || !withFullscreen) && (
        <div className="mb-[10px] flex">
          <label
            htmlFor={label}
            className={cn('py-3 mb-[10px] flex', {
              'text-gray-300 text-sm': labelSize === 'sm',
              'text-white text-[15px]': labelSize === 'md',
            })}
          >
            {label}
          </label>
          {labelContent}
        </div>
      )}
      <div
        ref={editorBoxRef}
        style={{
          maxHeight,
          minHeight: isFullscreenOpen ? maxHeight : minHeight,
        }}
        className={cn(
          className,
          'border-gray-500 w-full !leading-relaxed font-mono text-sm overflow-y-auto bg-gray-800 border rounded-[8px] transition duration-100',
          {
            'bg-gray-600 border-gray-400': focus,
            'hover:bg-gray-600 hover:placeholder:text-gray-300': !disabled && !readOnly,
          },
        )}
      >
        {typeof value === 'string' ? (
          <RichTextEditor
            value={value}
            onChange={handleValueChange}
            onBlur={onBlur}
            disabled={disabled || readOnly}
            codeLanguage={codeLanguage}
            readOnly={readOnly}
            className={cn(
              'resize-none appearance-none border border-transparent w-full placeholder-gray-400 bottom-0 p-0 h-full  placeholder:text-gray-400 text-[15px] text-gray-300 focus:text-white rounded-[8px] focus:!outline-none focus:!shadow-none !px-[20px] !py-[12px]',
              {
                'cursor-not-allowed': disabled,
                'opacity-[0.7] ': disabled,
                'bg-transparent': transparent,
                'pointer-events-none': disabled || readOnly,
              },
            )}
          />
        ) : (
          value
        )}

        {withFullscreen && (
          <Icon
            icon={isFullscreenOpen ? Minimize2 : Maximize2}
            width={24}
            height={24}
            className={cn(`absolute right-[25px] bottom-[25px] cursor-pointer text-gray-300 hover:text-white`, {
              'right-[25px] bottom-[25px]': fullScreen,
            })}
            onClick={toggleFullscreen}
          />
        )}
      </div>
    </div>
  );

  if (withFullscreen) {
    return (
      <>
        {codeInputCore(withFullscreen)}
        <CodeInputFullScreen setOpen={setIsFullscreenOpen} open={isFullscreenOpen}>
          {codeInputCore(false)}
        </CodeInputFullScreen>
      </>
    );
  }

  return codeInputCore(false);
}
