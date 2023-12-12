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
import { useProjectStore } from '@/store/projects/useProjectStore';
import { Agent, Asset, AssetType } from '@/types/editables/assetTypes';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { useProjectContextMenu } from '@/utils/projects/useProjectContextMenu';
import { AgentAvatar } from './AgentAvatar';
import { cn } from '@/utils/common/cn';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';

import { SliderArrowLeft } from '@/components/common/icons/SliderArrowLeft';
import { SliderArrowRight } from '@/components/common/icons/SliderArrowRight';
import { useNavigate } from 'react-router-dom';

function EmptyChatAgentAvatar({ agent }: { agent: Agent }) {
  const { showContextMenu } = useEditableObjectContextMenu({ editableObjectType: 'agent', editable: agent });
  const navigate = useNavigate();

  return (
    <div
      key={agent.id}
      onClick={() => navigate(`/agents/${agent.id}`)}
      className={cn(
        'flex flex-col justify-center items-center text-gray-500  hover:text-gray-300 cursor-pointer min-w-[110px]',
        {
          'text-agent': agent.status === 'forced',
        },
      )}
      onContextMenu={showContextMenu()}
    >
      <AgentAvatar agentId={agent.id} type="small" />
      <p className="text-[15px] text-center">{agent.name}</p>
    </div>
  );
}

function EmptyChatAssetLink({ assetType, asset }: { assetType: AssetType; asset: Asset }) {
  const { showContextMenu } = useEditableObjectContextMenu({ editableObjectType: assetType, editable: asset });
  const navigate = useNavigate();
  const Icon = getEditableObjectIcon(asset);

  return (
    <div
      className="inline-block cursor-pointer"
      onClick={() => navigate(`/materials/${asset.id}`)}
      onContextMenu={showContextMenu()}
    >
      <div className="group py-2 flex items-center gap-[12px] text-[14px] text-gray-300 hover:text-white">
        <Icon className="w-6 h-6 text-gray-500 group-hover:text-material" />
        <p className="max-w-[160px] truncate">{asset.name}</p>
      </div>
    </div>
  );
}

const MAX_ASSETS_TO_DISPLAY = 6;

export const EmptyChat = () => {
  const projectName = useProjectStore((state) => state.projectName);
  const agents = useEditablesStore((state) => state.agents);
  const materials = useEditablesStore((state) => state.materials || []);
  const { showContextMenu: showProjectContextMenu } = useProjectContextMenu();
  const forcedMaterials = materials.filter((m) => m.status === 'forced');
  const aiChoiceMaterials = materials.filter((m) => m.status === 'enabled');
  const activeSystemAgents = agents.filter((agent) => agent.status !== 'disabled' && agent.id !== 'user');
  const hasForcedMaterials = forcedMaterials.length > 0;
  const hasAiChoiceMaterials = aiChoiceMaterials.length > 0;

  return (
    <section className="flex flex-col items-center justify-center container mx-auto px-6 py-[80px] select-none">
      <img src="chat-page-glow.png" alt="glow" className="absolute top-[40px] -z-[1]" />
      <p className="text-[16px] text-gray-300 text-center mb-[15px]">Welcome to the project</p>
      <h2
        className="text-[36px] text-center font-black cursor-pointer uppercase text-white mb-[40px]"
        onContextMenu={showProjectContextMenu()}
        onClick={showProjectContextMenu()}
      >
        {projectName}
      </h2>
      <p className="mb-4 text-center text-[14px] text-gray-400">Agents in the project:</p>
      <div className="flex items-center justify-center mb-8 ">
        <SliderArrowLeft className="swiper-left text-gray-400 cursor-pointer" />
        <Swiper
          modules={[Navigation]}
          navigation={{ nextEl: '.swiper-right', prevEl: '.swiper-left' }}
          spaceBetween={0}
          slidesPerView={MAX_ASSETS_TO_DISPLAY}
          className="max-w-[700px]"
        >
          {activeSystemAgents.map((agent) => (
            <SwiperSlide className="width-[110px]" key={agent.id}>
              <EmptyChatAgentAvatar key={agent.id} agent={agent} />
            </SwiperSlide>
          ))}
        </Swiper>
        <SliderArrowRight className="swiper-right text-gray-400 cursor-pointer" />
      </div>
      <div className="max-w-[700px]">
        <p className="mb-4 text-center text-[14px] text-gray-400">Custom materials in the project:</p>
        {hasForcedMaterials && (
          <div
            className={cn('flex gap-[14px] py-[10px]', {
              'border-b border-gray-600': hasAiChoiceMaterials,
            })}
          >
            <p className="text-[14px] text-gray-400 py-2 min-w-[116px]">User enforced:</p>
            <div className="flex flex-wrap gap-[20px]">
              {forcedMaterials.map(
                (material, index) =>
                  index < MAX_ASSETS_TO_DISPLAY && (
                    <EmptyChatAssetLink assetType="material" asset={material} key={material.id} />
                  ),
              )}
            </div>
          </div>
        )}
        {hasAiChoiceMaterials && (
          <div className="flex gap-[14px] py-[10px]">
            <p className="text-[14px] py-2 text-gray-400 min-w-[116px]">AI choice:</p>
            <div className="flex flex-wrap gap-x-[20px]">
              {aiChoiceMaterials.map(
                (material, index) =>
                  index < MAX_ASSETS_TO_DISPLAY && (
                    <EmptyChatAssetLink assetType="material" asset={material} key={material.id} />
                  ),
              )}
            </div>
          </div>
        )}
        {hasAiChoiceMaterials || hasForcedMaterials ? (
          <p className=" text-gray-500 text-right text-[14px]">and X more...</p>
        ) : null}
      </div>
    </section>
  );
};
