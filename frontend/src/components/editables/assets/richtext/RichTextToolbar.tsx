import { useCallback, useState } from 'react';
import { Editor } from '@tiptap/react';
import { Bold, Italic, Strikethrough, ArrowLeft, ArrowRight, Link as LinkIcon } from 'lucide-react';
import * as Select from '@radix-ui/react-select';
import * as Popover from '@radix-ui/react-popover';

type HeadingLevel = 'normal' | '1' | '2' | '3';

type Level = 1 | 2 | 3;

type RichTextEditorToolbarProps = {
  editor: Editor | null;
};

const HEADING_OPTIONS = [
  { value: 'normal', label: 'Normal' },
  { value: '1', label: 'Header' },
  { value: '2', label: 'Header 2' },
  { value: '3', label: 'Header 3' },
];

const BUTTON_OPTIONS = [
  {
    icon: ArrowLeft,
    action: (editor: Editor) => editor.chain().focus().undo().run(),
  },
  {
    icon: ArrowRight,
    action: (editor: Editor) => editor.chain().focus().redo().run(),
  },
  {
    icon: Bold,
    action: (editor: Editor) => editor.chain().focus().toggleBold().run(),
    isActive: (editor: Editor) => editor.isActive('bold'),
  },
  {
    icon: Italic,
    action: (editor: Editor) => editor.chain().focus().toggleItalic().run(),
    isActive: (editor: Editor) => editor.isActive('italic'),
  },
  {
    icon: Strikethrough,
    action: (editor: Editor) => editor.chain().focus().toggleStrike().run(),
    isActive: (editor: Editor) => editor.isActive('strike'),
  },
];

const RichTextEditorToolbar: React.FC<RichTextEditorToolbarProps> = ({ editor }) => {
  const [url, setUrl] = useState('');

  const setLink = useCallback(() => {
    if (!editor) return;

    if (url === '') return editor.chain().focus().extendMarkRange('link').unsetLink().run();

    editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
    setUrl('');
  }, [editor, url]);

  const handlePopoverOpen = useCallback(() => {
    if (editor) {
      const previousUrl = editor.getAttributes('link').href;
      setUrl(previousUrl || '');
    }
  }, [editor]);

  const handleHeadingChange = useCallback(
    (value: HeadingLevel) => {
      if (!editor) return;
      if (value === 'normal') return editor.chain().focus().setParagraph().run();

      const level = parseInt(value) as Level;
      editor.chain().focus().toggleHeading({ level }).run();
    },
    [editor],
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        setLink();
      }
    },
    [setLink],
  );

  if (!editor) return;

  return (
    <div className="mb-2 flex gap-2 text-gray-400">
      {BUTTON_OPTIONS.map(({ icon: Icon, action, isActive }, index) => (
        <button
          key={index}
          onClick={() => action(editor)}
          className={`px-2 py-1 rounded hover:bg-gray-800 ${
            isActive && isActive(editor) ? 'bg-gray-800 text-white' : ''
          }`}
        >
          <Icon className="w-4 h-4" />
        </button>
      ))}

      <Select.Root onValueChange={handleHeadingChange}>
        <Select.Trigger className="inline-flex items-center justify-between gap-2 px-2 py-1 rounded hover:bg-gray-800 text-gray-400">
          <Select.Value placeholder="Normal" />
        </Select.Trigger>

        <Select.Portal>
          <Select.Content className="bg-gray-800 border border-gray-700 rounded shadow-lg">
            <Select.ScrollUpButton />
            <Select.Viewport className="p-1 text-gray-300">
              {HEADING_OPTIONS.map(({ value, label }) => (
                <Select.Item
                  key={value}
                  value={value}
                  className="flex items-center px-2 py-1 rounded hover:bg-gray-700 text-gray-300 hover:cursor-pointer"
                >
                  <Select.ItemText>{label}</Select.ItemText>
                </Select.Item>
              ))}
            </Select.Viewport>
            <Select.ScrollDownButton />
          </Select.Content>
        </Select.Portal>
      </Select.Root>

      <Popover.Root onOpenChange={handlePopoverOpen}>
        <Popover.Trigger asChild>
          <button
            className={`px-2 py-1 rounded hover:bg-gray-800 ${
              editor.isActive('link') ? 'bg-gray-800 text-white' : ''
            }`}
          >
            <LinkIcon className="w-4 h-4" />
          </button>
        </Popover.Trigger>
        <Popover.Portal>
          <Popover.Content
            className="p-2 bg-gray-800 border border-gray-700 rounded shadow-lg"
            align="center"
            sideOffset={5}
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter URL"
                className="px-2 py-1 bg-gray-700 text-white rounded outline-none w-full"
              />
              <button onClick={setLink} className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                Apply
              </button>
            </div>
            <Popover.Arrow className="fill-gray-800" />
          </Popover.Content>
        </Popover.Portal>
      </Popover.Root>
    </div>
  );
};

export default RichTextEditorToolbar;
