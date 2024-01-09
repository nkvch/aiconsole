import { cn } from '@/utils/common/cn';

import { MarkdownLogoIcon } from '../common/icons/MarkdownLogo';

interface MarkdownSupportedProps {
  className?: string;
}

export const MarkdownSupported = ({ className }: MarkdownSupportedProps) => (
  <div
    className={cn(
      'group-hover:text-yellow text-sm pointer-events-none flex items-center absolute bottom-[20px] right-[20px]',
      className,
    )}
  >
    <MarkdownLogoIcon className="mr-1" /> Markdown is supported
  </div>
);
