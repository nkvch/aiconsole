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

import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Asset, AssetStatus, AssetType, EditableObject, EditableObjectType } from '@/types/editables/assetTypes';
import { Circle, Copy, Edit, File, FolderOpenIcon, Trash, Undo2 } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import { useDeleteEditableObjectWithUserInteraction } from './useDeleteEditableObjectWithUserInteraction';
import { useMemo } from 'react';
import { RadioCheckedIcon } from '@/components/common/icons/RadioCheckedIcon';
import { noop } from '../common/noop';
import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { ContextMenuItem, ContextMenuItems } from '@/types/common/contextMenu';

export const DISABLED_CSS_CLASSES = 'max-w-[400px] truncate !text-gray-400 pointer-events-none !cursor-default ';

const statusHelper = (
  status: AssetStatus,
  editableObject: Asset,
  editableObjectType: AssetType,
): Omit<ContextMenuItem, 'type' | 'title'> => {
  const handleClick = (status: AssetStatus) => () => {
    useAssetStore.getState().setAssetStatus(editableObjectType, editableObject.id, status);
  };

  const assetStatusIcon = (itemStatus: AssetStatus) => {
    if ((editableObject as Asset)?.status === itemStatus) {
      return RadioCheckedIcon;
    }

    return Circle;
  };

  const activeItemClass = editableObject.status === status ? 'text-white' : 'text-gray-400';

  return {
    className: activeItemClass,
    iconClassName: activeItemClass,
    disabled: editableObject.status === status,
    icon: assetStatusIcon(status),
    hidden: !editableObject,
    action: editableObject.status === status ? noop : handleClick(status),
  };
};

const assetItems = (editableObjectType: EditableObjectType, editableObject: EditableObject): ContextMenuItems => {
  if (editableObjectType === 'chat') return [];
  const asset = editableObject as Asset;

  return [
    { type: 'separator', key: 'usage-separator' },
    {
      type: 'label',
      title: 'Usage',
    },

    {
      type: 'item',
      title: 'Enabled',
      ...statusHelper('enabled', asset, editableObjectType),
    },

    {
      type: 'item',
      title: 'Disabled',
      ...statusHelper('disabled', asset, editableObjectType),
    },
  ];
};

export function useEditableObjectContextMenu({
  editableObjectType,
  editable: editableObject,
  setIsEditing,
}: {
  editableObjectType: EditableObjectType;
  editable?: EditableObject;
  setIsEditing?: (isEditing: boolean) => void;
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const handleDelete = useDeleteEditableObjectWithUserInteraction(editableObjectType);
  const canOpenFinderForEditable = useEditablesStore((state) => state.canOpenFinderForEditable);
  const openFinderForEditable = useEditablesStore((state) => state.openFinderForEditable);

  const hasDelete = useMemo(
    () => (editableObjectType === 'chat' ? true : (editableObject as Asset)?.defined_in === 'project'),
    [editableObject, editableObjectType],
  );
  const isDeleteRevert = useMemo(
    () => (editableObjectType === 'chat' ? false : (editableObject as Asset)?.override),
    [editableObject, editableObjectType],
  );

  function getMenuItems() {
    if (!editableObject) {
      return [];
    }

    const content: ContextMenuItems = [
      {
        type: 'item',
        icon: Edit,
        title: 'Rename',
        hidden: !setIsEditing || (editableObject as Asset)?.defined_in === 'aiconsole',
        action: () => {
          if (!setIsEditing) {
            return;
          }
          setIsEditing(true);
        },
      },
      {
        type: 'item',
        icon: Copy,
        title: 'Duplicate',
        action: () => {
          navigate(
            `/${editableObjectType}s/${editableObjectType === 'chat' ? uuidv4() : 'new'}?copy=${editableObject.id}`,
          );
        },
      },
      {
        type: 'item',
        icon: File,
        title: 'Open',
        hidden: location.pathname === `/${editableObjectType}s/${editableObject.id}`,
        action: () => {
          navigate(`/${editableObjectType}s/${editableObject.id}`);
        },
      },
      {
        type: 'item',
        icon: FolderOpenIcon,
        title: `Reveal in ${window.window?.electron?.getFileManagerName()}`,
        hidden: !canOpenFinderForEditable(editableObject),
        action: () => {
          openFinderForEditable(editableObject);
        },
      },

      ...assetItems(editableObjectType, editableObject),
      { type: 'separator', key: 'delete-separator', hidden: !hasDelete },
      {
        type: 'item',
        icon: isDeleteRevert ? Undo2 : Trash,
        title: isDeleteRevert ? 'Revert' : 'Delete',
        hidden: !hasDelete,
        action: () => handleDelete(editableObject.id),
      },
    ];

    return content;
  }

  const menuItems = getMenuItems();

  return menuItems;
}
