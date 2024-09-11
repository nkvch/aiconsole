import { useCallback, useState } from 'react';
import { Editor } from '@tiptap/react';
import { Bold, Italic, Strikethrough, ArrowLeft, ArrowRight, Link as LinkIcon } from 'lucide-react';
import * as Select from '@radix-ui/react-select';
import * as Popover from '@radix-ui/react-popover';

const BUTTON_OPTIONS = [
    { icon: ArrowLeft, action: 'undo' },
    { icon: ArrowRight, action: 'redo' },
    { icon: Bold, action: 'toggleBold', active: 'bold' },
    { icon: Italic, action: 'toggleItalic', active: 'italic' },
    { icon: Strikethrough, action: 'toggleStrike', active: 'strike' },
];

const HEADING_OPTIONS = [
    { value: 'normal', label: 'Normal' },
    { value: '1', label: 'Header' },
    { value: '2', label: 'Header 2' },
    { value: '3', label: 'Header 3' },
];

const RichTextEditorToolbar = ({ editor }: { editor: Editor | null }) => {
    const [url, setUrl] = useState('');

    const setLink = useCallback(() => {
        if (!editor) return;
        editor.chain().focus().extendMarkRange('link').setLink({ href: url || null }).run();
        setUrl('');
    }, [editor, url]);

    const handleHeadingChange = (value: string) => editor?.chain().focus()[value === 'normal' ? 'setParagraph' : 'toggleHeading']({ level: +value || 1 }).run();

    if (!editor) return null;

    return (
        <div className="mb-2 flex gap-2 text-gray-400">
            {BUTTON_OPTIONS.map(({ icon: Icon, action, active }, i) => (
                <button
                    key={i}
                    onClick={() => editor.chain().focus()[action]().run()}
                    className={`px-2 py-1 rounded hover:bg-gray-800 ${active && editor.isActive(active) ? 'bg-gray-800 text-white' : ''}`}
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
                        <Select.Viewport className="p-1 text-gray-300">
                            {HEADING_OPTIONS.map(({ value, label }) => (
                                <Select.Item key={value} value={value} className="flex items-center px-2 py-1 rounded hover:bg-gray-700">
                                    <Select.ItemText>{label}</Select.ItemText>
                                </Select.Item>
                            ))}
                        </Select.Viewport>
                    </Select.Content>
                </Select.Portal>
            </Select.Root>

            <Popover.Root>
                <Popover.Trigger asChild>
                    <button className={`px-2 py-1 rounded hover:bg-gray-800 ${editor.isActive('link') ? 'bg-gray-800 text-white' : ''}`}>
                        <LinkIcon className="w-4 h-4" />
                    </button>
                </Popover.Trigger>
                <Popover.Portal>
                    <Popover.Content align="center" sideOffset={5} className="p-2 bg-gray-800 border border-gray-700 rounded shadow-lg">
                        <input
                            type="text"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && setLink()}
                            placeholder="Enter URL"
                            className="px-2 py-1 bg-gray-700 text-white rounded w-full"
                        />
                        <button onClick={setLink} className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 ml-2">
                            Apply
                        </button>
                        <Popover.Arrow className="fill-gray-800" />
                    </Popover.Content>
                </Popover.Portal>
            </Popover.Root>
        </div>
    );
};

export default RichTextEditorToolbar;
