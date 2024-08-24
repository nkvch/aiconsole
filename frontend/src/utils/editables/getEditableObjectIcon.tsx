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

import { EditableObject, EditableObjectType, Material, MaterialContentType } from '@/types/editables/assetTypes';
import { Blocks, Bot, FileQuestion, MessageSquare, ScanText, StickyNote } from 'lucide-react';
import { getEditableObjectType } from './getEditableObjectType';

export const MATERIAL_CONTENT_TYPE_ICONS = {
  static_text: StickyNote,
  dynamic_text: ScanText,
  api: Blocks,
};

export function getEditableObjectIcon(editableObject?: EditableObject | EditableObjectType) {
  let assetType;
  let contentType: MaterialContentType = 'static_text';

  if (typeof editableObject === 'string') {
    assetType = editableObject;
  } else {
    assetType = getEditableObjectType(editableObject);
    if (assetType === 'material') {
      contentType = (editableObject as Material).content_type;
    }
  }

  switch (assetType) {
    case 'material': {
      const icon = MATERIAL_CONTENT_TYPE_ICONS[contentType];
      if (!icon) {
        return FileQuestion;
      }
      return icon;
    }
    case 'agent':
      return Bot;
    case 'chat':
      return MessageSquare;
    default:
      return FileQuestion;
  }
}
