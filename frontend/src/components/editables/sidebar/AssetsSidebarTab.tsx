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

import { Asset, AssetStatus, AssetType } from '@/types/editables/assetTypes';
import SideBarItem from './SideBarItem';


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

export const AssetsSidebarTab = ({ assetType, assets, loadMoreMaterials, hasMore, loading, scrollable = false }: { assetType: AssetType; assets: Asset[], loadMoreMaterials?: () => void, hasMore?: boolean, loading?: boolean, scrollable?: boolean }) => {
  const groupedAssets = groupAssetsByStatus(assets);
  const hasForcedAssets = Boolean(groupedAssets[0][1].length);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    console.log("Handle Scroll is triggered!")
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 1; // Allow for small rounding errors

    if (isAtBottom && hasMore && !loading && loadMoreMaterials) {
      loadMoreMaterials();
      console.log("Reached the bottom!");
    }
  };

  return (
    <div className="flex flex-col gap-[5px] pr-[20px] overflow-y-auto h-full" style={{marginTop:'8px'}} onScroll={handleScroll}>
      {groupedAssets.map(([status, assets]) => {
        const title = getTitle(status, hasForcedAssets, assetType);
        return (
          assets.length > 0 && (
            <div key={status}>
              <h3 className="uppercase px-[9px] py-[5px] text-gray-400 text-[12px] leading-[18px]">{title}</h3>
              {assets.map((asset) => (
                <SideBarItem key={asset.id} editableObject={asset} editableObjectType={assetType} />
              ))}
            </div>
          )
        );
      })}
      {loading && <div style={{marginTop:'20px'}}>Loading more materials...</div>}
      {!hasMore && scrollable && <div>No more materials to load</div>}
    </div>
  );
};
