import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { createLowlight } from 'lowlight';
import { cn } from '@/utils/common/cn';
import { useEffect, useRef, useState } from 'react';
import { TipTapToolbar } from './TipTapToolbar';

const lowlight = createLowlight();

interface TipTapEditorProps {
  value: string;
  onChange?: (value: string) => void;
  codeLanguage?: string;
  disabled?: boolean;
  readOnly?: boolean;
  transparent?: boolean;
  maxHeight?: string;
  minHeight?: string;
  focused?: boolean;
  className?: string;
  label?: string;
  labelContent?: React.ReactNode;
  labelSize?: 'sm' | 'md';
  onBlur?: () => void;
  withFullscreen?: boolean;
}

export function TipTapEditor({
  value,
  onChange,
  codeLanguage,
  disabled = false,
  readOnly = false,
  transparent = false,
  maxHeight = 'calc(100% - 60px)',
  minHeight = '180px',
  focused = false,
  className,
  label,
  labelContent,
  labelSize = 'sm',
  onBlur,
  withFullscreen = false,
}: TipTapEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
        bulletList: {
          keepMarks: true,
          keepAttributes: false,
        },
        orderedList: {
          keepMarks: true,
          keepAttributes: false,
        },
      }),
      Placeholder.configure({
        placeholder: 'Write some text...',
      }),
      CodeBlockLowlight.configure({
        lowlight,
        defaultLanguage: codeLanguage || 'text',
      }),
    ],
    content: value,
    editable: !disabled && !readOnly,
    onUpdate: ({ editor }) => {
      // Получаем Markdown разметку
      const markdown = editor.storage.markdown?.getMarkdown() || editor.getText();
      onChange?.(markdown);
    },
    onBlur: () => {
      onBlur?.();
    },
    editorProps: {
      attributes: {
        class: 'prose prose-invert max-w-none focus:outline-none',
      },
    },
  });

  useEffect(() => {
    if (focused && editor) {
      editor.commands.focus();
    }
  }, [focused, editor]);

  useEffect(() => {
    if (editor && value !== editor.getText()) {
      editor.commands.setContent(value);
    }
  }, [value, editor]);

  const toggleFullscreen = () => {
    setIsFullscreen((prev) => !prev);
  };

  const editorContent = (
    <div className={cn('relative', className)}>
      {label && (
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
        ref={editorRef}
        style={{
          maxHeight: isFullscreen ? '100vh' : maxHeight,
          minHeight: isFullscreen ? '100vh' : minHeight,
        }}
        className={cn(
          'border-gray-500 w-full !leading-relaxed font-mono text-sm overflow-y-auto bg-gray-800 border rounded-[8px] transition duration-100',
          {
            'bg-gray-600 border-gray-400': focused,
            'hover:bg-gray-600 hover:placeholder:text-gray-300': !disabled && !readOnly,
            'opacity-[0.7]': disabled,
            'bg-transparent': transparent,
            'fixed inset-0 z-50': isFullscreen,
          },
        )}
      >
        {editor && (
          <TipTapToolbar
            editor={editor}
            onToggleFullscreen={withFullscreen ? toggleFullscreen : undefined}
            isFullscreen={isFullscreen}
          />
        )}
        <EditorContent editor={editor} />
      </div>
    </div>
  );

  if (isFullscreen) {
    return <div className="fixed inset-0 bg-gray-900 z-50">{editorContent}</div>;
  }

  return editorContent;
}
