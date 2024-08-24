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

import React from 'react';
import * as ReactTooltip from '@radix-ui/react-tooltip';

interface TooltipProps {
  label?: string;
  align?: ReactTooltip.TooltipContentProps['align'];
  disableAnimation?: boolean;
  position?: ReactTooltip.TooltipContentProps['side'];
  sideOffset?: ReactTooltip.TooltipContentProps['sideOffset'];
  withArrow?: boolean;
  children: React.ReactNode;
}

const Tooltip: React.FC<TooltipProps> = ({
  label = '',
  disableAnimation = false,
  align = 'center',
  position = 'top',
  sideOffset = 5,
  withArrow,
  children,
}) => {
  return (
    <ReactTooltip.Provider skipDelayDuration={0}>
      <ReactTooltip.Root delayDuration={0}>
        <ReactTooltip.Trigger asChild>{children}</ReactTooltip.Trigger>
        <ReactTooltip.Portal>
          <ReactTooltip.Content
            className="data-[state=instant-open]:animate-fadeIn data-[state=delayed-open]:data-[side=top]:animate-slideDownAndFade data-[state=delayed-open]:data-[side=right]:animate-slideLeftAndFade data-[state=delayed-open]:data-[side=left]:animate-slideRightAndFade data-[state=delayed-open]:data-[side=bottom]:animate-slideUpAndFade select-none rounded-[8px] bg-gray-600 border border-gray-700 text-gray-200 text-[12px] px-5 py-3 text-sm leading-none shadow-[hsl(206_22%_7%_/_35%)_0px_10px_38px_-10px,_hsl(206_22%_7%_/_20%)_0px_10px_20px_-15px] will-change-[transform,opacity]"
            sideOffset={sideOffset}
            side={position}
            align={align}
            data-state={disableAnimation ? 'instant-open' : 'delayed-open'}
          >
            {label}
            {withArrow && <ReactTooltip.Arrow width={12} height={8} className="fill-gray-600" />}
          </ReactTooltip.Content>
        </ReactTooltip.Portal>
      </ReactTooltip.Root>
    </ReactTooltip.Provider>
  );
};

export default Tooltip;
