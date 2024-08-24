import React, { useCallback, useEffect, useState, useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import { Markdown } from 'tiptap-markdown';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { lowlight } from 'lowlight/lib/core';
import hljs from 'highlight.js';
import 'highlight.js/styles/vs2015.css';
import { Icon } from '@/components/common/icons/Icon';
import {
  Bold as BoldIcon,
  Italic as ItalicIcon,
  Code,
  List,
  ListOrdered,
  Minimize2,
  Maximize2,
  Heading1,
  Heading2,
  Heading3,
  Table as TableIcon,
  PlusSquare,
  MinusSquare,
  Rows,
  Merge,
  Scissors,
  Trash2,
  Undo,
  Redo,
} from 'lucide-react';
import { cn } from '@/utils/common/cn';
import Document from '@tiptap/extension-document';
import ListItem from '@tiptap/extension-list-item';
import Paragraph from '@tiptap/extension-paragraph';
import Text from '@tiptap/extension-text';
import BulletList from '@tiptap/extension-bullet-list';
import OrderedList from '@tiptap/extension-ordered-list';
import Heading from '@tiptap/extension-heading';
import Bold from '@tiptap/extension-bold';
import Italic from '@tiptap/extension-italic';
import Table from '@tiptap/extension-table';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import History from '@tiptap/extension-history';

interface RichTextEditorProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  disabled?: boolean;
  readOnly?: boolean;
  maxHeight?: string;
  minHeight?: string;
  withFullscreen?: boolean;
  fullHeight?: boolean;
  className?: string;
  codeLanguage?: string;
}
interface MenuBarProps {
  editor: ReturnType<typeof useEditor>;
}

const MenuBar = React.memo<MenuBarProps>(({ editor }) => {
  if (!editor) return null;
  const buttons = [
    {
      onClick: () => editor.chain().focus().toggleBold().run(),
      isActive: editor.isActive('bold'),
      icon: BoldIcon,
      title: 'Toggle bold',
    },
    {
      onClick: () => editor.chain().focus().toggleItalic().run(),
      isActive: editor.isActive('italic'),
      icon: ItalicIcon,
      title: 'Toggle italic',
    },
    {
      onClick: () => editor.chain().focus().toggleCodeBlock().run(),
      isActive: editor.isActive('codeBlock'),
      icon: Code,
      title: 'Toggle code block',
    },
    {
      onClick: () => editor.chain().focus().toggleBulletList().run(),
      isActive: editor.isActive('bulletList'),
      icon: List,
      title: 'Toggle bullet list',
    },
    {
      onClick: () => editor.chain().focus().toggleOrderedList().run(),
      isActive: editor.isActive('orderedList'),
      icon: ListOrdered,
      title: 'Toggle ordered list',
    },
    {
      onClick: () => editor.chain().focus().toggleHeading({ level: 1 }).run(),
      isActive: editor.isActive('heading', { level: 1 }),
      icon: Heading1,
      title: 'Toggle heading 1',
    },
    {
      onClick: () => editor.chain().focus().toggleHeading({ level: 2 }).run(),
      isActive: editor.isActive('heading', { level: 2 }),
      icon: Heading2,
      title: 'Toggle heading 2',
    },
    {
      onClick: () => editor.chain().focus().toggleHeading({ level: 3 }).run(),
      isActive: editor.isActive('heading', { level: 3 }),
      icon: Heading3,
      title: 'Toggle heading 3',
    },
    {
      onClick: () => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(),
      icon: TableIcon,
      title: 'Insert table',
    },
    { onClick: () => editor.chain().focus().addColumnBefore().run(), icon: PlusSquare, title: 'Add column before' },
    { onClick: () => editor.chain().focus().addColumnAfter().run(), icon: PlusSquare, title: 'Add column after' },
    { onClick: () => editor.chain().focus().deleteColumn().run(), icon: MinusSquare, title: 'Delete column' },
    { onClick: () => editor.chain().focus().addRowBefore().run(), icon: Rows, title: 'Add row before' },
    { onClick: () => editor.chain().focus().addRowAfter().run(), icon: Rows, title: 'Add row after' },
    { onClick: () => editor.chain().focus().deleteRow().run(), icon: MinusSquare, title: 'Delete row' },
    { onClick: () => editor.chain().focus().mergeCells().run(), icon: Merge, title: 'Merge cells' },
    { onClick: () => editor.chain().focus().splitCell().run(), icon: Scissors, title: 'Split cell' },
    { onClick: () => editor.chain().focus().deleteTable().run(), icon: Trash2, title: 'Delete table' },
    { onClick: () => editor.chain().focus().undo().run(), icon: Undo, title: 'Undo', disabled: !editor.can().undo() },
    { onClick: () => editor.chain().focus().redo().run(), icon: Redo, title: 'Redo', disabled: !editor.can().redo() },
  ];

  return (
    <div className="flex space-x-2 mb-2">
      {buttons.map((button, index) => (
        <button
          key={index}
          onClick={button.onClick}
          className={cn(button.isActive ? 'is-active' : '', button.disabled ? 'opacity-50 cursor-not-allowed' : '')}
          title={button.title}
          disabled={button.disabled}
        >
          <Icon icon={button.icon} />
        </button>
      ))}
    </div>
  );
});

export function RichTextEditor({
  label,
  value,
  onChange,
  onBlur,
  disabled = false,
  readOnly = false,
  maxHeight = 'calc(100% - 60px)',
  minHeight = '180px',
  withFullscreen = false,
  fullHeight = false,
  className,
  codeLanguage,
}: RichTextEditorProps) {
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);
  const previousValueRef = useRef(value);

  const onHighlight = useCallback(
    (code: string, language: string) => {
      if (!code) return '';
      language = language || codeLanguage || 'python';
      try {
        return hljs.highlight(code, { language }).value;
      } catch (e) {
        return hljs.highlightAuto(code).value;
      }
    },
    [codeLanguage],
  );

  const editor = useEditor({
    extensions: [
      Document,
      Paragraph,
      Text,
      Bold,
      Italic,
      Markdown,
      BulletList,
      OrderedList,
      ListItem,
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Heading.configure({ levels: [1, 2, 3] }),
      CodeBlockLowlight.configure({
        lowlight,
        defaultLanguage: codeLanguage || 'python',
        HTMLAttributes: { class: 'hljs' },
      }),
      History,
    ],
    parseOptions: { preserveWhitespace: 'full' },
    content: value,
    editable: !disabled && !readOnly,
    onUpdate: ({ editor }) => {
      const markdown = editor.storage.markdown.getMarkdown();
      if (markdown !== previousValueRef.current) {
        previousValueRef.current = markdown;
        onChange(markdown);
      }
    },
    onBlur: onBlur,
  });

  useEffect(() => {
    if (editor && value !== previousValueRef.current) {
      previousValueRef.current = value;
      editor.commands.setContent(value, false);
    }
  }, [editor, value]);

  useEffect(() => {
    if (editor) {
      editor.view.dom.querySelectorAll('pre code').forEach((block) => {
        if (block instanceof HTMLElement) {
          const language = block.getAttribute('class')?.replace('language-', '') || codeLanguage || 'python';
          block.innerHTML = onHighlight(block.textContent || '', language);
        }
      });
    }
  }, [editor, onHighlight, codeLanguage]);

  const toggleFullscreen = useCallback(() => {
    setIsFullscreenOpen((prev) => !prev);
  }, []);

  return (
    <div className={cn('relative', { 'h-full': fullHeight })}>
      {label && <label className="block mb-2 text-sm font-medium text-gray-300">{label}</label>}
      <div
        style={{
          maxHeight: isFullscreenOpen ? '100%' : maxHeight,
          minHeight: isFullscreenOpen ? '100%' : minHeight,
        }}
        className={cn(
          'border-gray-500 w-full overflow-y-auto bg-gray-800 border rounded-[8px] transition duration-100',
          {
            'hover:bg-gray-600 hover:border-gray-400': !disabled && !readOnly,
          },
        )}
      >
        <MenuBar editor={editor} />
        <EditorContent editor={editor} className={className} />
        {withFullscreen && (
          <Icon
            icon={isFullscreenOpen ? Minimize2 : Maximize2}
            width={24}
            height={24}
            className="absolute right-[25px] bottom-[25px] cursor-pointer text-gray-300 hover:text-white"
            onClick={toggleFullscreen}
          />
        )}
      </div>
    </div>
  );
}
