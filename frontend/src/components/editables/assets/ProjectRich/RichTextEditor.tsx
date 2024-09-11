import React, { ReactNode } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import { cn } from '@/utils/common/cn';
import RichTextEditorToolbar from './RichTextToolbar';
import { HelperLabel } from '../HelperLabel';

interface RichTextEditorProps {
    label?: string;
    value: string;
    name?: string;
    placeholder?: string;
    className?: string;
    onChange: (value: string) => void;
    helperText?: string;
    horizontal?: boolean;
    fullWidth?: boolean;
    labelChildren?: ReactNode;
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
                                                           label,
                                                           value,
                                                           name,
                                                           placeholder,
                                                           className,
                                                           onChange,
                                                           helperText,
                                                           fullWidth,
                                                           horizontal,
                                                           labelChildren,
                                                       }) => {
    const editor = useEditor({
        extensions: [
            StarterKit,
            Placeholder.configure({
                placeholder,
                emptyNodeClass: 'first:before:text-gray-300 first:before:content-[attr(data-placeholder)]',
            }),
            Link.configure({
                openOnClick: false,
                autolink: true,
                HTMLAttributes: { class: 'text-blue-500 underline' },
            }),
        ],
        content: value,
        onUpdate: ({ editor }) => onChange(editor.getHTML()),
        editorProps: {
            attributes: {
                class: cn(
                    className,
                    'min-h-[90px] w-full border border-gray-500 placeholder:text-gray-400 bg-gray-800 text-gray-300 ' +
                    'focus:text-white flex-grow resize-none rounded-[8px] px-[20px] py-[12px] hover:bg-gray-600 ' +
                    'focus:bg-gray-600 focus:border-gray-400 transition duration-100',
                ),
            },
        },
    });

    return (
        <div className={cn('flex flex-col relative', { 'flex-row items-center': horizontal, 'w-full': fullWidth })}>
            {label && (
                <div className="text-white text-[15px] flex items-center gap-[30px] mb-[20px]">
                    <label htmlFor={name}>{label}</label>
                    {labelChildren}
                    {helperText && <HelperLabel helperText={helperText} />}
                </div>
            )}
            <RichTextEditorToolbar editor={editor} />
            <div className="w-full">
                <EditorContent editor={editor} />
            </div>
        </div>
    );
};

export default RichTextEditor;
