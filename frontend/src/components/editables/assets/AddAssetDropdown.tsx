import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import { MATERIAL_CONTENT_TYPE_ICONS, getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { DropdownMenu, Trigger, Item, Content } from '@radix-ui/react-dropdown-menu';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';

const ChatIcon = getEditableObjectIcon('chat');
const MaterialNoteIcon = MATERIAL_CONTENT_TYPE_ICONS['static_text'];
const MaterialDynamicNoteIcon = MATERIAL_CONTENT_TYPE_ICONS['dynamic_text'];
const MaterialPythonAPIIcon = MATERIAL_CONTENT_TYPE_ICONS['api'];
const AgentIcon = getEditableObjectIcon('agent');

export const AddAssetDropdown = () => {
  const [opened, setOpened] = useState(false);
  const navigate = useNavigate();

  const handleClick = (path?: string) => () => {
    if (path) {
      navigate(path);
    }
  };

  const uuid = uuidv4();

  const dropdownItems = useMemo(
    () => [
      {
        key: 'chat',
        icon: <Icon icon={ChatIcon} className="w-6 h-6 !text-chat" />,
        title: 'Chat',
        path: `/chats/${uuid}`,
      },
      {
        key: 'agent',
        icon: <Icon icon={AgentIcon} className="w-6 h-6 !text-agent" />,
        title: 'Agent',
        path: `/agents/new`,
      },
      {
        key: 'note',
        icon: <Icon icon={MaterialNoteIcon} className="w-6 h-6 !text-material" />,
        title: 'Note',
        path: `/materials/new?type=static_text`,
      },
      {
        key: 'dynamic_note',
        icon: <Icon icon={MaterialDynamicNoteIcon} className="w-6 h-6 !text-material" />,
        title: 'Dynamic Note',
        path: `/materials/new?type=dynamic_text`,
      },
      {
        key: 'python_api',
        icon: <Icon icon={MaterialPythonAPIIcon} className="w-6 h-6 !text-material" />,
        title: 'Python API',
        path: `/materials/new?type=api`,
      },
    ],
    [uuid],
  );

  return (
    <DropdownMenu modal={false} open={opened} onOpenChange={setOpened}>
      <Trigger asChild>
        <button
          className={cn(
            'group flex justify-center align-center gap-[12px] rounded-[8px] py-[6px] border border-gray-500  text-gray-300 text-[16px] font-semibold w-[180px] leading-[23px] hover:border-gray-300 transition duration-200 hover:text-gray-300',
            {
              'rounded-b-none text-gray-500': opened,
            },
          )}
        >
          Add new
        </button>
      </Trigger>

      <Content
        className={cn('bg-gray-700 border-t-0 border-gray-800 p-0 w-[180px]', {
          'rounded-t-none ': opened,
        })}
      >
        {dropdownItems.map(
          ({
            icon,
            title,
            path,
            key,
            disabled,
          }: {
            icon: JSX.Element;
            title: string;
            path: string;
            key: string;
            disabled?: boolean;
          }) => (
            <Item
              key={key}
              onClick={handleClick(path)}
              className={cn('group flex p-0 rounded-none hover:bg-gray-600 hover:outline-none w-full cursor-pointer', {
                'pointer-events-none': disabled,
              })}
            >
              <div
                className={cn(
                  'flex items-center gap-[12px] px-[16px] py-[10px] text-[14px] text-gray-300 group-hover:text-white w-full',
                  {
                    'text-gray-400 pb-0 ': disabled,
                  },
                )}
              >
                {icon}
                <p>{title}</p>
              </div>
            </Item>
          ),
        )}
      </Content>
    </DropdownMenu>
  );
};
