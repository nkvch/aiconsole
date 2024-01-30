import { Icon } from '@/components/common/icons/Icon';
import { AICMessageGroup } from '@/types/editables/chatTypes';
import { cn } from '@/utils/common/cn';
import { XIcon } from 'lucide-react';
import { useEffect, useState } from 'react';

export const AnalysisClosed = ({ group, onClick }: { group: AICMessageGroup; onClick: () => void }) => {
  const onClick2 = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  return group.analysis || group.task ? (
    <img onClick={onClick2} src={`favicon.svg`} className="h-[18px] w-[18px] filter cursor-pointer mt-2" />
  ) : (
    <></>
  );
};

export const AnalysisOpened = ({
  group,
  onClick,
  isOpen,
}: {
  group: AICMessageGroup;
  onClick: () => void;
  isOpen: boolean;
}) => {
  const onClick2 = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (group.analysis) {
      setIsLoaded(true);
    }
  }, [group.analysis]);

  return (
    <div
      onClick={onClick2}
      className={cn(
        'flex flex-col text-grayPurple-300 rounded-[20px] w-full text-[14px] border border-grayPurple-600 cursor-pointer analysis-gradient max-w-[700px] transition-all duration-300 px-[30px] py-0',
        {
          'opacity-100 max-h-max p-[30px]': isLoaded && isOpen,
          'opacity-0 max-h-[0]': !isLoaded || !isOpen,
        },
      )}
    >
      <div
        className={cn('flex justify-between transition-opacity duration-150"', {
          'ease-in opacity-100 ': isLoaded && isOpen,
          'ease-out opacity-0': !isLoaded || !isOpen,
        })}
      >
        <div className="flex gap-[10px] items-center">
          <img src={`favicon.svg`} className="h-[18px] w-[18px] filter" />
          AI Analysis process
        </div>
        <Icon icon={XIcon} className="text-gray-400" />
      </div>
      <div
        className={cn('mt-[20px] transition-opacity duration-150', {
          'ease-in opacity-100 ': isLoaded && isOpen,
          'ease-out opacity-0': !isLoaded || !isOpen,
        })}
      >
        {group.analysis}{' '}
        {group.task && (
          <span className="text-white inline-block">
            <br /> Next step: <span className="text-purple-400 leading-[24px]">{group.task}</span>
          </span>
        )}
      </div>
    </div>
  );
};
