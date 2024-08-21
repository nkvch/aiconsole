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

import { create } from 'zustand';
import { TabsValues } from '@/types/editables/assetTypes';

export type ActiveTab = TabsValues | string;

export type SidebarSlice = {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
    isCollapsed: boolean;
   handlesCollapse: () => void;
};

export const useSidebarStore = create<SidebarSlice>((set) => ({
  activeTab: 'chat',
  setActiveTab: (tab: ActiveTab) => {
    set(() => ({
      activeTab: tab,
    }));
  },
  isCollapsed: false,
      handlesCollapse: () => {
    set((state) => ({
      isCollapsed: !state.isCollapsed,
    }));
  }
}));
