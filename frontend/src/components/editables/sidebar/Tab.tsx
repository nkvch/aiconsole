import { ActiveTab } from '@/store/common/useSidebarStore';
import { cn } from '@/utils/common/cn';
import * as Tabs from '@radix-ui/react-tabs';

interface TabProps extends Tabs.TabsTriggerProps {
  value: string;
  activeTab: ActiveTab;
  label: string;
  openTab:boolean;
}

export const Tab = ({ value, activeTab, label,openTab }: TabProps) => (
  <Tabs.Trigger
    value={value}
    className={cn(
      `pt-[10px] px-5 relative pb-[25px] [&:first-letter:] tab-hover font-medium text-[14px] ${ openTab?"w-full":" w-1/3" }hover:bg-transparent overflow-hidden border-b border-gray-500 after:content-[""] after:opacity-20 after:left-[50%] after:translate-x-[-50%] after:w-[35px] after:h-[30px] after:absolute after:bottom-[-8px] after:z-[99]  after:bg-yellow after:hidden`,
      {
        'text-white after:blur-[15px] border-yellow after:block': activeTab === value,
      },
    )}
  >
    {label}
  </Tabs.Trigger>
);
