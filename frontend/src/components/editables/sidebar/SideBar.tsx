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
  const [searchQuery,setSearchQuery] = useState('');
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
  const initMaterials = useEditablesStore((state) => state.initMaterials);
  const { activeTab, setActiveTab } = useSidebarStore();
  const [loading, setLoading] = useState(false);  
  const [hasMore, setHasMore] = useState(true);    
  const [offset, setOffset] = useState(0);     
  const limit = 18;        

  useEffect(() => {
    setActiveTab(initialTab);
    loadMoreMaterials();
  }, [initialTab, setActiveTab]);

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    setOffset(0);   //to search for search matches among all the materials    
    setHasMore(true);         
    setLoading(true);        

    try {
      useEditablesStore.setState({ materials: [] });
      console.log("Searching for:", query);
      await initMaterials(0, query);

    } catch (error) {
      console.error("Failed to search materials:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadMoreMaterials = async () => {
    if (loading) return;
    setLoading(true);
    
    setOffset(offset + limit);
    console.log("Offset value",offset)

    try {
      console.log("Fetching more materials with offset:", offset);
      await initMaterials(offset,searchQuery);
      
      const materials = useEditablesStore.getState().materials;

      if (materials.length < offset) {
        setHasMore(false);
      }

      
    } catch (error) {
      console.error("Failed to load materials:", error);
    } finally {
      setLoading(false);
    }
  };

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
                        <DoubleArrowRightIcon className="h-8 w-6 text-gray-400 hover:text-white transition-colors" style={{ marginTop: '-3px' }} />
                    ) : (
                        <DoubleArrowLeftIcon className="h-8 w-6 text-gray-400 hover:text-white transition-colors" style={{ marginTop: '-13px' }} />
                    )}
                </button>

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
                  <div className="px-5" style={{marginTop:"5px"}}>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={handleSearch}
                      placeholder="Search Materials"
                      className="w-full p-2 rounded-md bg-gray-800 text-white"
                    />
                  </div>
                    <AssetsSidebarTab assetType="material" assets={materials || []} loadMoreMaterials={loadMoreMaterials} hasMore={hasMore} loading={loading} />
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
