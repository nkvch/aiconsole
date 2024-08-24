import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useAPIStore } from '@/store/useAPIStore';
import { cn } from '@/utils/common/cn';

interface ActorAvatarProps {
  actorId?: string;
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
  actorType: 'agent' | 'user';
}

export function ActorAvatar({ actorId, title, type, className, actorType }: ActorAvatarProps) {
  const getBaseURL = useAPIStore((state) => state.getBaseURL);
  const agent = useAssetStore((state) => state.getAsset('agent', actorId || ''));
  const userAvatarUrl = useSettingsStore((state) => state.userAvatarUrl) || undefined;

  let src: string | undefined = '';

  if (actorType === 'agent') {
    src = `${getBaseURL()}/api/agents/${actorId}/image?version=${agent?.version}`;
    className = cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
      'w-20 h-20 ': type === 'large',
      'w-16 h-16': type === 'small',
      'w-6 h-6': type === 'extraSmall',
      'border-[2px] border-agent shadow-agent': agent?.status === 'forced',
      'shadow-md': agent?.status !== 'forced',
      hidden: !actorId,
    });
  } else if (actorType === 'user') {
    src = userAvatarUrl;
    className = cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
      'w-20 h-20 ': type === 'large',
      'w-16 h-16': type === 'small',
      'w-6 h-6': type === 'extraSmall',
    });
  }

  return <img title={title} src={src} className={className} />;
}
