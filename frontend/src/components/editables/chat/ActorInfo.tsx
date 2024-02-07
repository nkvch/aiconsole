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

import { MouseEvent, useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import { ContextMenu, ContextMenuRef } from '@/components/common/ContextMenu';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { cn } from '@/utils/common/cn';
import { useUserContextMenu } from '@/utils/common/useUserContextMenu';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { ActorAvatar } from './ActorAvatar';

function AgentInfoMaterialLink({
  materialId,
  isLoaded,
  isRunning,
}: {
  materialId: string;
  isLoaded: boolean;
  isRunning: boolean;
}) {
  const materials = useEditablesStore((state) => state.materials) || [];
  const material = materials.find((m) => m.id === materialId);
  const menuItems = useEditableObjectContextMenu({ editableObjectType: 'material', editable: material });

  return (
    <ContextMenu options={menuItems}>
      <Link to={`/materials/${materialId}`}>
        <div
          className={cn(
            'text-[12px] text-center text-gray-400 whitespace-nowrap pb-1 max-w-[120px] px-[10px] truncate opacity-0',
            {
              'transition-opacity duration-500 opacity-40': isLoaded,
              'opacity-40': isRunning,
            },
          )}
          title={materialId}
        >
          {materialId}
        </div>
      </Link>
    </ContextMenu>
  );
}

export function ActorInfo({
  actorId,
  materialsIds,
  task,
}: {
  actorId: string;
  materialsIds: string[];
  task?: string;
}) {
  const [isLoaded, setIsLoaded] = useState(false);
  const isAnalysisRunning = useChatStore((state) => state.chat?.is_analysis_in_progress);
  const isExecutionRunning = useChatStore((state) => state.isExecutionRunning());
  const agents = useEditablesStore((state) => state.agents) || [];
  const agent = agents.find((m) => m.id === actorId);

  const editableMenuItems = useEditableObjectContextMenu({
    editableObjectType: 'agent',
    editable: agent || {
      id: actorId,
      name: actorId,
    },
  });

  const triggerRef = useRef<ContextMenuRef>(null);

  const openContext = (event: MouseEvent) => {
    if (triggerRef.current && actorId === 'user') {
      triggerRef?.current.handleTriggerClick(event);
    }
  };

  const userMenuItems = useUserContextMenu();

  const menuItems = actorId !== 'user' ? editableMenuItems : userMenuItems;

  useEffect(() => {
    if (agent) {
      setIsLoaded(true);
    }
  }, [agent]);

  return (
    <>
      <ContextMenu options={menuItems} ref={triggerRef}>
        <Link
          to={actorId != 'user' ? `/agents/${actorId}` : ''}
          onClick={openContext}
          className="flex-none items-center flex flex-col"
        >
          <ActorAvatar
            actorType="agent"
            actorId={actorId}
            title={`${agent?.name || actorId}${task ? ` tasked with:\n${task}` : ``}`}
            type="small"
          />
          <div
            className={cn(
              'text-[15px] w-32 text-center text-gray-300 max-w-[120px] truncate overflow-ellipsis overflow-hidden whitespace-nowrap  opacity-0',
              {
                'transition-opacity duration-500 opacity-100': isLoaded,
                'opacity-100': !isAnalysisRunning && !isExecutionRunning,
              },
            )}
            title={`${agent?.id} - ${agent?.usage}`}
          >
            {agent?.name || agent?.id}
          </div>
        </Link>
      </ContextMenu>
      {materialsIds.length > 0 && (
        <div
          className={cn('text-xs text-center opacity-0', {
            'transition-opacity duration-500 opacity-40': isLoaded,
            'opacity-40': !isAnalysisRunning && !isExecutionRunning,
          })}
        >
          +
        </div>
      )}
      {materialsIds.map((material_id) => (
        <AgentInfoMaterialLink
          key={material_id}
          materialId={material_id}
          isLoaded={isLoaded}
          isRunning={!isAnalysisRunning && !isExecutionRunning}
        />
      ))}
    </>
  );
}
