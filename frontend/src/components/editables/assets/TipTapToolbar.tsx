import { Editor } from '@tiptap/react';
import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Quote,
  Code,
  Heading1,
  Heading2,
  Heading3,
  Undo,
  Redo,
  Maximize2,
  Minimize2,
} from 'lucide-react';

interface TipTapToolbarProps {
  editor: Editor;
  onToggleFullscreen?: () => void;
  isFullscreen?: boolean;
}

export function TipTapToolbar({ editor, onToggleFullscreen, isFullscreen }: TipTapToolbarProps) {
  if (!editor) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2 p-2 border-b border-gray-600 bg-gray-800 rounded-t-[8px]">
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleBold().run()}
        active={editor.isActive('bold')}
      >
        <Icon icon={Bold} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleItalic().run()}
        active={editor.isActive('italic')}
      >
        <Icon icon={Italic} />
      </Button>
      <div className="w-px h-6 bg-gray-600 mx-1" />
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        active={editor.isActive('heading', { level: 1 })}
      >
        <Icon icon={Heading1} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        active={editor.isActive('heading', { level: 2 })}
      >
        <Icon icon={Heading2} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        active={editor.isActive('heading', { level: 3 })}
      >
        <Icon icon={Heading3} />
      </Button>
      <div className="w-px h-6 bg-gray-600 mx-1" />
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        active={editor.isActive('bulletList')}
      >
        <Icon icon={List} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        active={editor.isActive('orderedList')}
      >
        <Icon icon={ListOrdered} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        active={editor.isActive('blockquote')}
      >
        <Icon icon={Quote} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        active={editor.isActive('codeBlock')}
      >
        <Icon icon={Code} />
      </Button>
      <div className="w-px h-6 bg-gray-600 mx-1" />
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().undo().run()}
        disabled={!editor.can().undo()}
      >
        <Icon icon={Undo} />
      </Button>
      <Button
        variant="tertiary"
        small
        onClick={() => editor.chain().focus().redo().run()}
        disabled={!editor.can().redo()}
      >
        <Icon icon={Redo} />
      </Button>
      {onToggleFullscreen && (
        <>
          <div className="w-px h-6 bg-gray-600 mx-1" />
          <Button variant="tertiary" small onClick={onToggleFullscreen}>
            <Icon icon={isFullscreen ? Minimize2 : Maximize2} />
          </Button>
        </>
      )}
    </div>
  );
}
