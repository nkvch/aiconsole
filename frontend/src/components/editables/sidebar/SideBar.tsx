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
import { useEffect, useState } from 'react';
import { AssetsSidebarTab } from './AssetsSidebarTab';
import { ChatsSidebarTab } from './ChatsSidebarTab';
import { Tab } from './Tab';
import * as Tabs from '@radix-ui/react-tabs';
import { useSidebarStore } from '@/store/common/useSidebarStore';
import {DoubleArrowLeftIcon, DoubleArrowRightIcon } from '@radix-ui/react-icons';



const TABS = [
  { label: 'Chats', key: 'chats' },
  { label: 'Materials', key: 'materials' },
  { label: 'Agents', key: 'agents' },
];

const SideBar = ({ initialTab }: { initialTab: string }) => {
  const [isCollapsed,setIsCollapsed] = useState(false);
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
  const { activeTab, setActiveTab } = useSidebarStore();

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab, setActiveTab]);

  const toggleCollapse = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <div
      className={`h-full bg-gray-900 pt-[20px] drop-shadow-md flex flex-col border-r border-gray-600 transition-all duration-300 ${
        isCollapsed ? 'w-[60px] min-w-[60px]' : 'w-[336px] min-w-[336px]'
      }`}
    >
      <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <Tabs.List className="flex items-center px-2 mb-[15px]">
          <button
            onClick={toggleCollapse}
            className="p-2 mr-2 transition-colors"
           
          >
            {isCollapsed ? (
              <DoubleArrowRightIcon className="h-8 w-6 text-gray-400 hover:text-white transition-colors" style={{marginTop:'-3px'}}/>
            ) : (
              <DoubleArrowLeftIcon className="h-8 w-6 text-gray-400 hover:text-white transition-colors"  style={{marginTop:'-13px'}} />
            )}
          </button>

          {/* Tabs will only show labels when not collapsed */}
          {!isCollapsed && (
            <div className="flex flex-1 justify-around">
              {TABS.map(({ label, key }) => (
                <Tab key={key} value={key} label={label} activeTab={activeTab} />
              ))}
            </div>
          )}
        </Tabs.List>

        {!isCollapsed && (
          <>
            <Tabs.Content value="chats" className="flex-1 overflow-hidden">
              <ChatsSidebarTab />
            </Tabs.Content>
            <Tabs.Content value="materials" className="flex-1 overflow-hidden px-5">
              <AssetsSidebarTab assetType="material" assets={materials || []} />
            </Tabs.Content>
            <Tabs.Content value="agents" className="flex-1 overflow-hidden px-5">
              <AssetsSidebarTab assetType="agent" assets={agents} />
            </Tabs.Content>
          </>
        )}
      </Tabs.Root>
    </div>
  );
};

export default SideBar;
