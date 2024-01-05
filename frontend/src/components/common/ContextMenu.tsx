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

import { MouseEvent as ReactMouseEvent, ReactNode, forwardRef, useCallback, useImperativeHandle, useRef } from 'react';
import { Icon } from '@/components/common/icons/Icon';
import { ContextMenuItem, ContextMenuItems } from '@/types/common/contextMenu';
import { cn } from '@/utils/common/cn';
import {
  Trigger,
  Content,
  Item,
  Separator,
  Label,
  Portal,
  Root,
  ContextMenuProps as RadixContextMenuProps,
} from '@radix-ui/react-context-menu';

export type ContextMenuRef = {
  handleTriggerClick: (event: ReactMouseEvent) => void;
};

interface ContextMenuProps {
  children: ReactNode;
  options: ContextMenuItems;
  triggerClassName?: string;
  onOpenChange?: RadixContextMenuProps['onOpenChange'];
}

export const ContextMenu = forwardRef<ContextMenuRef | undefined, ContextMenuProps>(
  ({ children, options, onOpenChange, triggerClassName }, ref) => {
    const triggerRef = useRef<HTMLDivElement>(null);

    // RadixUI ContextMenu does not provide any option to open/control this component than by using onContextMenu event,
    // soo, to be able to display context menu onClick we need to dispatch this event manually
    // https://www.radix-ui.com/primitives/docs/components/context-menu#api-reference
    const handleTriggerClick = useCallback(
      (event: ReactMouseEvent) => {
        if (!ref) return;

        if (triggerRef.current) {
          const contextMenuEvent = new MouseEvent('contextmenu', {
            bubbles: true,
            cancelable: true,
            clientX: event.pageX,
            clientY: event.pageY,
          });

          triggerRef.current.dispatchEvent(contextMenuEvent);
        }
      },
      [ref],
    );

    useImperativeHandle(
      ref,
      () => {
        if (ref) {
          return {
            handleTriggerClick,
          };
        }

        return;
      },
      [handleTriggerClick, ref],
    );

    const renderDropdownElement = (props: ContextMenuItem) => {
      const { type, title = '', disabled, action, icon, iconClassName, className } = props;

      switch (type) {
        case 'item':
          return (
            <Item
              onClick={action}
              disabled={disabled}
              className={cn(
                'group text-white bg-gray-700 py-[7px] px-[15px] rounded-none my-[3px] hover:text-white text-[16px] context-menu-icon flex  gap-[15px] hover:outline-none hover:bg-gray-600 cursor-pointer',
                className,
              )}
            >
              {icon ? (
                <Icon icon={icon} className={cn('mt-1 text-gray-400 group-hover:text-white', iconClassName)} />
              ) : null}{' '}
              {title}
            </Item>
          );
        case 'separator':
          return <Separator className="bg-gray-800 my-[3px] h-[1px]" />;
        case 'label':
          return (
            <Label className="truncate text-gray-400 pointer-events-none cursor-default py-[5px] px-[15px] my-[3px]">
              {title}
            </Label>
          );
      }
    };

    return (
      <Root modal={false} onOpenChange={onOpenChange}>
        <Trigger ref={triggerRef} className={triggerClassName}>
          {children}
        </Trigger>

        <Portal>
          <Content className="w-full z-5 !bg-gray-700 border border-gray-800 px-0 py-[6px] rounded-[4px] text-gray-400 min-w-[137px] max-w-[300px] z-[98]">
            <div>
              {options.map(
                ({ key, hidden, ...props }) =>
                  !hidden && <div key={key || props.title}>{renderDropdownElement(props)}</div>,
              )}
            </div>
          </Content>
        </Portal>
      </Root>
    );
  },
);
