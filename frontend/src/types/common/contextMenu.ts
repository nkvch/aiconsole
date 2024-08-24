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

import { IconElement } from '@/components/common/icons/Icon';

export type ContextItemType = 'label' | 'separator' | 'item';

export interface ContextMenuItem {
  type: ContextItemType;
  key?: string;
  title?: string;
  icon?: IconElement;
  disabled?: boolean;
  action?: () => void;
  hidden?: boolean;
  className?: string;
  iconClassName?: string;
}

export type ContextMenuItems = ContextMenuItem[];
