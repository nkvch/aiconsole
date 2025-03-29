import { Editor } from '@monaco-editor/react';
import { cn } from '@/utils/common/cn';
import { FocusEvent, ReactNode, useCallback, useEffect, useRef, useState } from 'react';
import { Icon } from '@/components/common/icons/Icon';
import { Maximize2, Minimize2 } from 'lucide-react';
import { CodeInputFullScreen } from './CodeInputFullScreen';

const DEFAULT_MAX_HEIGHT = 'calc(100% - 60px)';
const DEFAULT_MIN_HEIGHT = '180px';

interface MonacoEditorProps {
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

export function MonacoEditor({
  label,
  value,
  className,
  onChange,
  onBlur,
  codeLanguage = 'javascript',
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
}: MonacoEditorProps) {
  const [focus, setFocus] = useState(false);
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
  const editorRef = useRef<HTMLDivElement | null>(null);

  const handleEditorDidMount = useCallback((editor: any) => {
    editorRef.current = editor;
  }, []);

  const handleValueChange = useCallback(
    (value: string | undefined) => {
      if (onChange && value !== undefined) {
        onChange(value);
      }
    },
    [onChange],
  );

  const handleFocus = useCallback(() => {
    setFocus(true);
  }, []);

  const handleBlur = useCallback(() => {
    setFocus(false);
    onBlur?.();
  }, [onBlur]);

  useEffect(() => {
    if (focused) {
      setFocus(true);
      editorRef.current?.focus();
    }
  }, [focused]);

  useEffect(() => {
    if (!isFullscreenOpen) {
      setFocus(false);
      editorRef.current?.blur();
    }
  }, [focused, isFullscreenOpen]);

  const toggleFullscreen = () => {
    setIsFullscreenOpen((prev) => !prev);
  };

  const editorCore = (fullScreen: boolean) => (
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
          </label>{' '}
          {labelContent}
        </div>
      )}
      <div
        style={{
          maxHeight,
          minHeight: isFullscreenOpen ? maxHeight : minHeight,
        }}
        className={cn(
          className,
          'border-gray-500 w-full overflow-y-auto bg-gray-800 border rounded-[8px] transition duration-100',
          {
            'bg-gray-600 border-gray-400': focus,
            'hover:bg-gray-600': !disabled && !readOnly,
          },
        )}
      >
        {typeof value === 'string' ? (
          <Editor
            height="100%"
            defaultLanguage={codeLanguage}
            defaultValue={value}
            value={value}
            onChange={handleValueChange}
            onMount={handleEditorDidMount}
            onFocus={handleFocus}
            onBlur={handleBlur}
            options={{
              readOnly: disabled || readOnly,
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              theme: 'vs-dark',
            }}
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
        {editorCore(withFullscreen)}
        <CodeInputFullScreen setOpen={setIsFullscreenOpen} open={isFullscreenOpen}>
          {editorCore(false)}
        </CodeInputFullScreen>
      </>
    );
  }

  return editorCore(false);
}
