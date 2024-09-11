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

import { StateCreator } from 'zustand';

import { Material } from '@/types/editables/assetTypes';
import { EditablesAPI } from '../../api/api/EditablesAPI';
import { EditablesStore } from './useEditablesStore';
import { useProjectStore } from '@/store/projects/useProjectStore';


export type MaterialSlice = {
  materials: Material[];
  initMaterials: (offset: number,search: string) => Promise<void>; //matching parameters to what the endpoint needs
};


export const createMaterialSlice: StateCreator<EditablesStore, [], [], MaterialSlice> = (set, get) => ({
  materials: [],
  initMaterials: async (offset = 0,search ='') => {
    if (useProjectStore.getState().isProjectOpen) {
      const fetchedMaterials = await EditablesAPI.fetchMaterials<Material>('material', offset,search);

      console.log("Fetched materials:", fetchedMaterials);

      // Filter out duplicate materials
      const existingMaterials = get().materials;
      const uniqueNewMaterials = fetchedMaterials.filter(
        fetchedMaterial => !existingMaterials.some(existingMaterial => existingMaterial.id === fetchedMaterial.id)
      );

      if (fetchedMaterials.length === 0) return;

      // Sort the new materials in the desired order
      uniqueNewMaterials.sort((a, b) => a.name.localeCompare(b.name));
      uniqueNewMaterials.sort((a, b) => (a.defined_in === 'project' ? 0 : 1) - (b.defined_in === 'project' ? 0 : 1));
      uniqueNewMaterials.sort((a, b) => {
        const aStatus = a.status === 'forced' ? 0 : a.status === 'enabled' ? 1 : 2;
        const bStatus = b.status === 'forced' ? 0 : b.status === 'enabled' ? 1 : 2;
        return aStatus - bStatus;
      });

      set((state) => ({
        materials: [...state.materials, ...uniqueNewMaterials], 
      }));
    } else {
      set({ materials: [] });
    }
  },
});