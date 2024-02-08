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

import { EditablesAPI } from '@/api/api/EditablesAPI';
import { Agent, Asset, AssetStatus, AssetType, Material } from '@/types/editables/assetTypes';
import { canThereBeOnlyOneForcedAsset } from '@/utils/editables/canThereBeOnlyOneForcedAsset';
import { create } from 'zustand';
import { useEditablesStore } from '../useEditablesStore';

export type AssetStore = {
  selectedAsset?: Asset;
  lastSavedSelectedAsset?: Asset;
  getAsset: (assetType: AssetType, id: string) => Asset | undefined;
  setSelectedAsset: (asset?: Asset) => void;
  setLastSavedSelectedAsset: (asset?: Asset) => void;
  setAssetStatus: (assetType: AssetType, id: string, status: AssetStatus) => Promise<void>;
};

export const useAssetStore = create<AssetStore>((set) => ({
  lastSavedSelectedAsset: undefined,
  selectedAsset: undefined,
  setLastSavedSelectedAsset: (asset?: Asset) => {
    set({
      lastSavedSelectedAsset: asset,
    });
  },
  getAsset: (assetType: AssetType, id: string): Asset | undefined => {
    if (assetType === 'agent') {
      if (id === 'user') {
        const agent: Agent = {
          type: 'agent',
          id: 'user',
          name: 'You',
          usage: '',
          usage_examples: [],
          system: '',
          defined_in: 'aiconsole',
          status: 'enabled',
          gpt_mode: 'quality',
          execution_mode: 'aiconsole.core.chat.execution_modes.normal:execution_mode',
          default_status: 'enabled',
          override: false,
        };

        return agent;
      }

      if (id === 'new') {
        //TODO: There should be only one place where this is defined, right now it's both in backend and frontend

        const agent: Agent = {
          type: 'agent',
          id: 'new_agent',
          name: 'New agent',
          usage: '',
          usage_examples: [],
          system: '',
          defined_in: 'project',
          status: 'enabled',
          gpt_mode: 'quality',
          execution_mode: 'aiconsole.core.chat.execution_modes.normal:execution_mode',
          default_status: 'enabled',
          override: false,
        };

        return agent;
      }

      //
      // I just realized that client needs to be able to send modification messages in the same way the server does to a client ... which warants a slightly different setup than what I already have ...
      //

      return useEditablesStore.getState().agents.find((agent) => agent.id === id);
    }

    if (assetType === 'material') {
      if (id === 'new') {
        const material: Material = {
          type: 'material',
          id: 'new_material',
          name: 'New material',
          usage: '',
          usage_examples: [],
          defined_in: 'project',
          status: 'enabled',
          content: '',
          content_type: 'static_text',
          default_status: 'enabled',
          override: false,
        };

        return material;
      }

      return useEditablesStore.getState().materials?.find((material) => material.id === id);
    }

    throw new Error(`Unknown asset type ${assetType}`);
  },
  setSelectedAsset: (asset?: Asset) => {
    set({
      selectedAsset: asset,
    });
  },
  setAssetStatus: async (assetType: AssetType, id: string, status: AssetStatus) => {
    const plural = (assetType + 's') as 'materials' | 'agents';

    useEditablesStore.setState((state) => ({
      [plural]: (state[plural] || []).map((asset) => {
        if (asset.id === id) {
          asset.status = status;
        } else {
          if (canThereBeOnlyOneForcedAsset(assetType)) {
            if (asset.status === 'forced') {
              asset.status = 'enabled';
            }
          }
        }
        return asset;
      }),
    }));

    await EditablesAPI.setAssetStatus(assetType, id, status);
  },
}));
