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

import {useEffect, useReducer} from "react";
import { Asset, AssetStatus, AssetType } from '@/types/editables/assetTypes';
import SideBarItem from './SideBarItem';
import {SideBarContentHeader} from "./SideBarContentHeader.tsx";
import {bulkSelectAssetReducer} from "@/store/editables/bulkSelectAssetReducer.ts";

const getTitle = (status: AssetStatus, isAgentChosen: boolean, assetType: AssetType) => {
  switch (status) {
    case 'forced':
      return 'User enforced';
    case 'enabled':
      return isAgentChosen && assetType === 'agent' ? 'Disabled' : 'Enabled';
    case 'disabled':
      return 'Disabled';
  }
};

function groupAssetsByStatus(assets: Asset[]) {
  const groupedAssets = new Map<AssetStatus, Asset[]>([
    ['forced', []],
    ['enabled', []],
    ['disabled', []],
  ]);

  assets.forEach((asset) => {
    const { status } = asset;
    const assets = groupedAssets.get(status) || [];
    const updatedAssets = [...assets, asset];
    groupedAssets.set(status, updatedAssets);
  });

  return [...groupedAssets.entries()];
}

export const AssetsSidebarTab = ({ assetType, assets }: { assetType: AssetType; assets: Asset[] }) => {
  const groupedAssets = groupAssetsByStatus(assets);
  const hasForcedAssets = Boolean(groupedAssets[0][1].length);

  const [selectState, selectDispatch] = useReducer(bulkSelectAssetReducer, {
    selectedItems: [],
    restrictedItems: [],
    collection: [],
  });

  useEffect(() => {
    selectDispatch({type: "setCollection", payload: {collection: assets}});
  }, [assets]);

  return (
    <div className="flex flex-col gap-[5px] overflow-y-auto h-full">
      <SideBarContentHeader
        assetType={assetType}
        allItemsChecked={selectState.selectedItems.length === selectState.collection.length && selectState.collection.length !== 0}
        checkedItems={selectState.selectedItems}
        restrictedItems={selectState.restrictedItems}
        onCheckAll={(isChecked) => isChecked ? selectDispatch({type: "selectAll"}) : selectDispatch({type: "selectNone"})}
      />
      {groupedAssets.map(([status, assets]) => {
        const title = getTitle(status, hasForcedAssets, assetType);

        return (
          assets.length > 0 && (
            <div key={status}>
              <h3 className="uppercase px-[9px] pb-[5px] text-gray-400 text-[12px] leading-[18px] border-b border-gray-400 mb-2">{title}</h3>
              {assets.map((asset) => (
                <SideBarItem
                  key={asset.id}
                  editableObject={asset}
                  editableObjectType={assetType}
                  isChecked={selectState.selectedItems.includes(asset.id)}
                  onCheck={(isChecked) => isChecked ?
                    selectDispatch({type: "selectItem", payload: {asset}}) :
                    selectDispatch({type: "deselectItem", payload: {asset}})}
                />
              ))}
            </div>
          )
        );
      })}
    </div>
  );
};
