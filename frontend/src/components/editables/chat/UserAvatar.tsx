import { cn } from '@/utils/common/cn';
import { useSettingsStore } from '@/store/settings/useSettingsStore';

interface UserAvatarProps {
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
}

export function UserAvatar({ title, type, className }: UserAvatarProps) {
  const userAvatarUrl = useSettingsStore((state) => state.userAvatarUrl) || undefined;

  return (
    <img
      title={title}
      src={userAvatarUrl}
      className={cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
        'w-20 h-20 ': type === 'large',
        'w-16 h-16': type === 'small',
        'w-6 h-6': type === 'extraSmall',
      })}
    />
  );
}
