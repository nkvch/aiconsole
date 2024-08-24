import { Icon } from '@/components/common/icons/Icon';
import { AICMessageGroup } from '@/types/editables/chatTypes';
import { cn } from '@/utils/common/cn';
import { XIcon } from 'lucide-react';
import { useEffect, useState } from 'react';

export const AnalysisClosed = ({ group, onClick }: { group: AICMessageGroup; onClick: () => void }) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  return group.analysis || group.task ? (
    <div className="rounded-[8px] w-full cursor-pointer mt-2" onClick={handleClick}>
      <img src={`favicon.svg`} className="h-[18px] w-[18px] filter mx-auto" />
    </div>
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
  const handleClick = (e: React.MouseEvent) => {
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
      className={cn(
        'flex flex-col text-grayPurple-300 rounded-[20px] w-full text-[14px] border border-grayPurple-600 analysis-gradient max-w-[700px] transition-all duration-300 px-[30px] py-0',
        {
          'opacity-100 max-h-max p-[30px] h-auto': isLoaded && isOpen,
          'opacity-0 max-h-[0] h-0 cursor-default': !isLoaded || !isOpen,
        },
      )}
    >
      <div
        className={cn('flex justify-between transition-opacity duration-150"', {
          'ease-in opacity-100 max-h-max': isLoaded && isOpen,
          'ease-out opacity-0 max-h-[0]': !isLoaded || !isOpen,
        })}
      >
        <div className="flex gap-[10px] items-center">
          <img src={`favicon.svg`} className="h-[18px] w-[18px] filter" />
          AI Analysis process
        </div>
        <Icon
          icon={XIcon}
          className={cn('text-gray-400 cursor-pointer', {
            'ease-in opacity-100 max-h-max': isLoaded && isOpen,
            'ease-out opacity-0 max-h-[0]': !isLoaded || !isOpen,
          })}
          onClick={handleClick}
        />
      </div>
      <div
        className={cn('transition-opacity duration-150', {
          'ease-in opacity-100 max-h-max mt-[20px]': isLoaded && isOpen,
          'ease-out opacity-0 max-h-[0] mt-[0px]': !isLoaded || !isOpen,
        })}
        hidden={!isLoaded || !isOpen}
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
