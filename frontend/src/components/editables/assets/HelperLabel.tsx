import { cn } from '@/utils/common/cn';

interface HelperLabel {
  helperText: string;
  learnMoreLink?: string;
  className?: string;
}

export const HelperLabel = ({ helperText, learnMoreLink, className }: HelperLabel) => (
  <p className={cn('ml-auto text-[14px] text-gray-400 font-normal', className)}>
    {helperText}&nbsp;
    {learnMoreLink ? (
      <a
        className="text-gray-300 underline cursor-pointer"
        href={learnMoreLink}
        target="_blank"
        rel="noreferrer noopener"
      >
        Learn more
      </a>
    ) : null}
  </p>
);
