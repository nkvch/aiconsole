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
import { useSelectionStore } from '@/store/useSelectionStore';
import { Button } from '@/components/common/Button';
import { Trash, CheckSquare, Square, ToggleLeft, ToggleRight } from 'lucide-react';
import { useToastsStore } from '@/store/common/useToastsStore';
import { motion, AnimatePresence } from 'framer-motion';
import { EditablesAPI } from '@/api/api/EditablesAPI';

const TABS = [
  { label: 'Chats', key: 'chats' },
  { label: 'Materials', key: 'materials' },
  { label: 'Agents', key: 'agents' },
];

const SideBar = ({ initialTab }: { initialTab: string }) => {
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials);
  const { activeTab, setActiveTab } = useSidebarStore();
  const { selections, clearSelection, getSelectedCount, isSelectionMode, setSelectionMode } = useSelectionStore(state => ({ 
    selections: state.selections as Record<'chats' | 'materials' | 'agents', string[]>,
    clearSelection: state.clearSelection,
    getSelectedCount: state.getSelectedCount,
    isSelectionMode: state.isSelectionMode,
    setSelectionMode: state.setSelectionMode
  }));
  const bulkDeleteEditableObjects = useEditablesStore((state) => state.bulkDeleteEditableObjects);
  const showToast = useToastsStore((state) => state.showToast);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isChangingStatus, setIsChangingStatus] = useState(false);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab, setActiveTab]);

  const handleDeleteSelected = async () => {
    setIsDeleting(true);
    setTimeout(async () => {
      const activeTabKey = activeTab as 'chats' | 'materials' | 'agents';
      const selectedIds = selections[activeTabKey];
      const editableType = activeTab === 'chats' ? 'chat' : activeTab === 'agents' ? 'agent' : 'material';
      
      if (selectedIds.length === 0) return;
      
      const deletableIds = selectedIds.filter(id => {
        if (editableType === 'chat') return true;
        const asset = editableType === 'agent' 
          ? agents.find(a => a.id === id)
          : materials?.find(m => m.id === id);
        return asset?.defined_in === 'project';
      });

      if (deletableIds.length === 0) {
        setIsDeleting(false);
        showToast({
          title: 'Cannot delete',
          message: 'Selected items cannot be deleted',
          variant: 'error',
        });
        return;
      }
      
      try {
        await bulkDeleteEditableObjects(editableType, deletableIds);
        clearSelection(activeTabKey);
        setIsDeleting(false);
        
        showToast({
          title: 'Items deleted',
          message: `Successfully deleted ${deletableIds.length} ${
            activeTab === 'chats' ? 'chats' : activeTab === 'agents' ? 'agents' : 'materials'
          }`,
          variant: 'success',
        });
      } catch (error) {
        console.error('Error while deleting items:', error);
        setIsDeleting(false);
        showToast({
          title: 'Error',
          message: 'There was a problem deleting the items',
          variant: 'error',
        });
      }
    }, 300);
  };

  const handleChangeStatus = async () => {
    if (isChangingStatus) return;
    setIsChangingStatus(true);
    
    try {
      const activeTabKey = activeTab as 'chats' | 'materials' | 'agents';
      const selectedIds = selections[activeTabKey];
      const editableType = activeTab === 'chats' ? 'chat' : activeTab === 'agents' ? 'agent' : 'material';
      
      if (selectedIds.length === 0) {
        setIsChangingStatus(false);
        showToast({
          title: 'Cannot change status',
          message: 'No items selected',
          variant: 'error',
        });
        return;
      }

      const status_changes: Record<string, 'enabled' | 'disabled'> = {};
      let newStatus: 'enabled' | 'disabled' = 'disabled';
      
      for (const id of selectedIds) {
        const asset = editableType === 'agent' 
          ? agents.find(a => a.id === id)
          : materials?.find(m => m.id === id);
        
        if (asset) {
          newStatus = asset.status === 'enabled' ? 'disabled' : 'enabled';
          status_changes[id] = newStatus;
        }
      }

      if (Object.keys(status_changes).length === 0) {
        setIsChangingStatus(false);
        showToast({
          title: 'Cannot change status',
          message: 'No valid items found to change status',
          variant: 'error',
        });
        return;
      }

      console.log('Sending status changes:', {
        type: editableType,
        status: newStatus,
        to_global: false,
        status_changes
      });
      
      await EditablesAPI.bulkChangeStatus(
        editableType as 'agent' | 'material', 
        status_changes,
        newStatus,
        false
      );
      
      clearSelection(activeTabKey);
      setIsChangingStatus(false);
      
      showToast({
        title: 'Status changed',
        message: `Successfully changed status of ${selectedIds.length} ${
          activeTab === 'agents' ? 'agents' : 'materials'
        }`,
        variant: 'success',
      });
    } catch (error) {
      console.error('Error while changing status:', error);
      setIsChangingStatus(false);
      showToast({
        title: 'Error',
        message: 'There was a problem changing the status',
        variant: 'error',
      });
    }
  };

  const selectedCount = getSelectedCount(activeTab as keyof typeof selections);
  
  const canDeleteSelected = () => {
    const activeTabKey = activeTab as 'chats' | 'materials' | 'agents';
    const selectedIds = selections[activeTabKey];
    const editableType = activeTab === 'chats' ? 'chat' : activeTab === 'agents' ? 'agent' : 'material';
    
    if (selectedIds.length === 0) return false;
    
    if (editableType === 'chat') return true;
    
    return selectedIds.every(id => {
      const asset = editableType === 'agent' 
        ? agents.find(a => a.id === id)
        : materials?.find(m => m.id === id);
      return asset?.defined_in === 'project';
    });
  };

  return (
    <div
      className={`min-w-[336px] w-[336px] h-full bg-gray-900 pt-[20px] drop-shadow-md flex flex-col border-r border-gray-600`}
    >
      <Tabs.Root value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
        <Tabs.List className="mb-[15px] px-5">
          {TABS.map(({ label, key }) => (
            <Tab key={key} value={key} label={label} activeTab={activeTab} />
          ))}
        </Tabs.List>
        <div className="px-5 mb-4">
          <Button
            variant="status"
            small
            onClick={() => {
              if (isSelectionMode) {
                clearSelection();
              }
              setSelectionMode(!isSelectionMode);
            }}
            classNames="w-full"
          >
            <motion.div
              animate={{ 
                x: isSelectionMode ? 5 : 0
              }}
              transition={{ 
                type: "spring",
                stiffness: 400,
                damping: 25
              }}
            >
              {isSelectionMode ? (
                  <Square className="w-3 h-3 mr-2" />
              ) : (
                <CheckSquare className="w-3 h-3 mr-2" />
              )}
            </motion.div>
            <AnimatePresence mode="wait">
              <motion.span
                key={isSelectionMode ? 'exit' : 'enter'}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2 }}
              >
                {isSelectionMode ? 'Exit Selection Mode' : 'Enter Selection Mode'}
              </motion.span>
            </AnimatePresence>
          </Button>
        </div>
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <Tabs.Content value="chats" className="h-full">
              <ChatsSidebarTab />
            </Tabs.Content>
            <Tabs.Content value="materials" className="h-full px-5">
              <AssetsSidebarTab assetType="material" assets={materials || []} />
            </Tabs.Content>
            <Tabs.Content value="agents" className="h-full px-5">
              <AssetsSidebarTab assetType="agent" assets={agents} />
            </Tabs.Content>
          </div>
          <AnimatePresence>
            {selectedCount > 0 && !isDeleting && !isChangingStatus && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="w-full bg-gray-900/95 backdrop-blur-sm border-t border-gray-700"
              >
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <motion.span 
                      key={selectedCount}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      transition={{ type: "spring", stiffness: 300, damping: 30 }}
                      className="text-sm text-gray-400"
                    >
                      {selectedCount} {selectedCount === 1 ? 'item' : 'items'} selected
                    </motion.span>
                    <div className="flex gap-2">
                      <Button 
                        variant="status" 
                        small 
                        onClick={handleChangeStatus}
                        classNames="flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
                      >
                        <ToggleRight size={16} />
                        Status
                      </Button>
                      <Button 
                        variant="status" 
                        small 
                        onClick={() => {
                          if (canDeleteSelected()) {
                            handleDeleteSelected();
                          } else {
                            showToast({
                              title: 'Cannot delete',
                              message: 'Selected items cannot be deleted',
                              variant: 'error',
                            });
                          }
                        }}
                        classNames="flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105 active:scale-95"
                      >
                        <Trash size={16} />
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Tabs.Root>
    </div>
  );
};

export default SideBar;
