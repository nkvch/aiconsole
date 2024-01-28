import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useAPIStore } from '@/store/useAPIStore';
import { cn } from '@/utils/common/cn';
import { useState } from 'react';

interface ActorAvatarProps {
  agentId: string;
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
}

export function ActorAvatar({ agentId, title, type, className }: ActorAvatarProps) {
  const agent = useAssetStore((state) => state.getAsset('agent', agentId));
  const getBaseURL = useAPIStore((state) => state.getBaseURL);

  return (
    <img
      title={title}
      src={`${getBaseURL()}/api/agents/${agentId}/image`}
      className={cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
        'w-20 h-20 ': type === 'large',
        'w-16 h-16': type === 'small',
        'w-6 h-6': type === 'extraSmall',
        'border-[2px] border-agent shadow-agent': agent?.status === 'forced',
        'shadow-md': agent?.status !== 'forced',
      })}
    />
  );
}

interface UserAvatarProps {
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
}

export function UserAvatar({ title, type, className }: UserAvatarProps) {
  const userAvatarUrl = useSettingsStore((state) => state.userAvatarUrl) || undefined;
  const [avatarURL, setAvatarURL] = useState('');
  const getBaseURL = useAPIStore((state) => state.getBaseURL);

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
