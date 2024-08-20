import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { useEffect, useState } from 'react';
import { AssetsSidebarTab } from './AssetsSidebarTab';
import { ChatsSidebarTab } from './ChatsSidebarTab';
import { Tab } from './Tab';
import * as Tabs from '@radix-ui/react-tabs';
import { useSidebarStore } from '@/store/common/useSidebarStore';
import CollapseButton from './CollapseButton'; // Import the CollapseButton component

const TABS = [
  { label: 'Chats', key: 'chats' },
  { label: 'Materials', key: 'materials' },
  { label: 'Agents', key: 'agents' },
];

const SideBar = ({ initialTab }: { initialTab: string }) => {
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
  const { activeTab, setActiveTab } = useSidebarStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab, setActiveTab]);

  const toggleCollapse = () => setIsCollapsed(!isCollapsed);

  return (
    <>
      <div className="relative h-full flex flex-col">
        {/* Collapse button in its own block */}
        <div className="p-4 bg-gray-900 border-b border-gray-600">
          <CollapseButton isCollapsed={isCollapsed} onClick={toggleCollapse} />
        </div>

        {/* Rest of the content */}
        {!isCollapsed && (
          <div className="min-w-[336px] w-[336px] h-full bg-gray-900 drop-shadow-md flex flex-col border-r border-gray-600">
            <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
              <Tabs.List className="mb-[15px] px-5">
                {TABS.map(({ label, key }) => (
                  <Tab key={key} value={key} label={label} activeTab={activeTab} />
                ))}
              </Tabs.List>

              <Tabs.Content value="chats" className="flex-1 overflow-hidden">
                <ChatsSidebarTab />
              </Tabs.Content>
              <Tabs.Content value="materials" className="flex-1 overflow-hidden px-5">
                <AssetsSidebarTab assetType="material" assets={materials || []} />
              </Tabs.Content>
              <Tabs.Content value="agents" className="flex-1 overflow-hidden px-5">
                <AssetsSidebarTab assetType="agent" assets={agents} />
              </Tabs.Content>
            </Tabs.Root>
          </div>
        )}
      </div>
    </>
  );
};

export default SideBar;
