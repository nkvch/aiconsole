import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import { Code2, Fullscreen } from 'lucide-react';

interface CodeEditorLabelContentProps {
  showPreview: boolean;
  onClick: () => void;
}

export const CodeEditorLabelContent = ({ showPreview, onClick }: CodeEditorLabelContentProps) => (
  <Button
    classNames={cn(
      'ml-auto text-[15px] leading-[24px] justify-start px-[10px] w-[120px] hover:border-gray-300 hover:text-gray-300 hover:bg-transparent focus:border-gray-300 focus:text-gray-300 focus:bg-transparent',
      {
        'flex-row-reverse': showPreview,
      },
    )}
    small
    transparent
    variant="secondary"
    onClick={onClick}
  >
    <div className="bg-gray-600 h-[34px] w-[34px] flex items-center justify-center rounded-[20px]">
      <Icon icon={showPreview ? Fullscreen : Code2} className="!w-[24px] !h-[24px]" />
    </div>
    {showPreview ? 'Preview' : 'Code'}
  </Button>
);
