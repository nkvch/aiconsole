// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { useEditablesStore } from '@/store/editables/useEditablesStore';
<<<<<<< HEAD
import { useEffect } from 'react';
=======
import { useEffect,useState } from 'react';
>>>>>>> 5f371ad1 (end)
import { AssetsSidebarTab } from './AssetsSidebarTab';
import { ChatsSidebarTab } from './ChatsSidebarTab';
import { Tab } from './Tab';
import * as Tabs from '@radix-ui/react-tabs';
import { useSidebarStore } from '@/store/common/useSidebarStore';
<<<<<<< HEAD
=======
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
>>>>>>> 5f371ad1 (end)

const TABS = [
  { label: 'Chats', key: 'chats' },
  { label: 'Materials', key: 'materials' },
  { label: 'Agents', key: 'agents' },
];

const SideBar = ({ initialTab }: { initialTab: string }) => {
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
<<<<<<< HEAD
  const { activeTab, setActiveTab } = useSidebarStore();
=======
  const { activeTab, setActiveTab, isCollapsed, handlesCollapse } = useSidebarStore();

  const [openTab, setOpenTab] = useState(false);
>>>>>>> 5f371ad1 (end)

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab, setActiveTab]);

  return (
    <div
<<<<<<< HEAD
      className={`min-w-[336px] w-[336px] h-full  bg-gray-900 pt-[20px] drop-shadow-md flex flex-col border-r  border-gray-600`}
    >
      <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <Tabs.List className="mb-[15px] px-5">
          {TABS.map(({ label, key }) => (
            <Tab key={key} value={key} label={label} activeTab={activeTab} />
=======
      className={`${
        isCollapsed ? 'w-[100px]' : 'min-w-[336px] w-[336px]'
      } h-full  bg-gray-900 pt-[20px] drop-shadow-md flex flex-col border-r  border-gray-600`}
    >
      <Tabs.Root
        value={activeTab}
        onValueChange={(value) => {
          setActiveTab(value);
          if (isCollapsed && openTab) {
            setOpenTab(false);
          }
        }}
        className="h-full flex flex-col"
      >
        {isCollapsed && (
          <div className="flex flex-col  items-center">
            <Button
              classNames=" bg-blue-500 hover:bg-blue-600 rounded-full p-2"
              small
              iconOnly
              onClick={() => setOpenTab(!openTab)}
            >
              <Icon icon={Plus} className="text-white" />
            </Button>
          </div>
        )}
        {isCollapsed && openTab && (
          <div className="w-30 ">
            <Tabs.List className="flex flex-col">
              {TABS.map(({ label, key }) => (
                <Tab key={key} value={key} label={label} activeTab={activeTab} openTab={openTab} />
              ))}
            </Tabs.List>
          </div>
        )}

        <Tabs.List className={`${isCollapsed ? 'hidden' : 'flex flex-row '}  mb-[15px] px-5 `}>
          {TABS.map(({ label, key }) => (
            <Tab key={key} value={key} label={label} activeTab={activeTab} openTab={openTab} />
>>>>>>> 5f371ad1 (end)
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
<<<<<<< HEAD
=======
        <button onClick={() => handlesCollapse()} className="mr-10 mb-4 flex justify-end hover:text-white z-50">
          {isCollapsed ? <ChevronRight /> : <ChevronLeft />}
        </button>
>>>>>>> 5f371ad1 (end)
      </Tabs.Root>
    </div>
  );
};

export default SideBar;
