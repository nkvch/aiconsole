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

import { ReactNode, useCallback, useState } from 'react';

import { Icon } from '@/components/common/icons/Icon';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { AICMessageGroup, AICToolCall } from '@/types/editables/chatTypes';
import { cn } from '@/utils/common/cn';
import { upperFirst } from '@mantine/hooks';
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  ChevronDown,
  ChevronUp,
  CircleDashedIcon,
  Infinity,
  Play,
} from 'lucide-react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { duotoneDark as vs2015 } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { Button } from '../../../common/Button';
import { Spinner } from '../Spinner';
import { EditableContentMessage } from './EditableContentMessage';
import { ToolOutput } from './ToolOutput';
import { transpileCode } from '@/utils/transpilation/transpileCode';
import { createSandbox } from '@/utils/transpilation/createSandbox';
import { MessageControls } from './MessageControls';

interface MessageProps {
  group: AICMessageGroup;
  toolCall: AICToolCall;
}

export function ToolCall({ group, toolCall: tool_call }: MessageProps) {
  const userMutateChat = useChatStore((state) => state.userMutateChat);
  const saveCommandAndMessagesToHistory = useChatStore((state) => state.saveCommandAndMessagesToHistory);
  const chat = useChatStore((state) => state.chat);

  const alwaysExecuteCode = useSettingsStore((state) => state.alwaysExecuteCode);

  const [folded, setFolded] = useState(alwaysExecuteCode);
  const doAcceptCode = useChatStore((state) => state.doAcceptCode);
  const enableAutoCodeExecution = useSettingsStore((state) => state.setAutoCodeExecution);
  const isViableForRunningCode = useChatStore((state) => state.isViableForRunningCode);

  const [uiResult, setUIResult] = useState<ReactNode | null>(null);

  const handleAcceptedContent = useCallback(
    (content: string) => {
      userMutateChat({
        type: 'SetCodeToolCallMutation',
        tool_call_id: tool_call.id,
        code: content,
      });
      saveCommandAndMessagesToHistory(content, group.role === 'user');
    },
    [tool_call.id, userMutateChat, saveCommandAndMessagesToHistory, group.role],
  );

  const handleRemoveClick = useCallback(() => {
    userMutateChat({
      type: 'DeleteToolCallMutation',
      tool_call_id: tool_call.id,
    });
  }, [tool_call.id, userMutateChat]);

  const renderUIResult = async () => {
    const finalCode = await transpileCode(tool_call.code);
    const sandbox = createSandbox(finalCode);
    setUIResult(sandbox);
  };

  const handleRunClick = async () => {
    if (tool_call.type === 'function') {
      doAcceptCode(tool_call.id);
      tool_call.output = '';
    } else {
      await renderUIResult();
    }
  };

  const handleAlwaysRunClick = () => {
    enableAutoCodeExecution(true);
    handleRunClick();
  };

  //Either executing or streaming while there are still no output messages
  const shouldDisplaySpinner = tool_call.is_executing || tool_call.is_streaming;

  const isError =
    tool_call.output?.toLowerCase().includes('traceback') ||
    tool_call.output?.toLowerCase().includes('syntax error:') ||
    tool_call.output?.toLowerCase().includes('execution error:') ||
    tool_call.output?.toLowerCase().includes('an error occurred on line') ||
    tool_call.output?.toLowerCase().match(/file\s*".*",\s*line/g);

  const customVs2015 = {
    ...vs2015,
    'pre[class*="language-"]': {
      ...vs2015['pre[class*="language-"]'],
      background: '#1A1A1A', // Change this to your desired text color
    },
    'code[class*="language-"]': {
      ...vs2015['code[class*="language-"]'],
      background: '#1A1A1A', // Change this to your desired text color
    },
  };

  return (
    <div className="rounded-md flex flex-col bg-gray-700 flex-grow overflow-auto ">
      <div
        className={cn(
          'cursor-pointer rounded-md  rounded-b-md px-[30px] py-[15px] border-2 border-gray-600 hover:text-gray-300 hover:border-gray-500 hover:bg-gray-600 transition-ease duration-100',
          {
            'border-b-2 border-gray-600 rounded-b-none': !folded,
          },
        )}
        onClick={async () => {
          if (folded && alwaysExecuteCode && isViableForRunningCode(tool_call.id)) {
            await renderUIResult();
          } else {
            setUIResult(null);
          }
          setFolded((folded) => !folded);
        }}
      >
        <div className="flex flex-row gap-2 items-center ">
          <div className="flex-grow flex flex-row gap-3 items-center">
            {shouldDisplaySpinner && <Spinner width={20} height={20} />}
            {!shouldDisplaySpinner && !isError && !(tool_call.output != undefined || tool_call.type == 'ui') && (
              <Icon icon={CircleDashedIcon} width={20} height={20} className="text-success flex-shrink-0" />
            )}
            {!shouldDisplaySpinner && !isError && (tool_call.output != undefined || tool_call.type == 'ui') && (
              <Icon icon={CheckCircle2Icon} width={20} height={20} className="text-success flex-shrink-0" />
            )}
            {!shouldDisplaySpinner && isError && (
              <Icon icon={AlertCircleIcon} width={20} height={20} className="text-danger flex-shrink-0" />
            )}

            <span className="font-semibold"> {tool_call.headline ? tool_call.headline : 'Task'}</span>
          </div>

          {!folded && <Icon icon={ChevronUp} width={20} height={20} className="flex-shrink-0" />}
          {folded && <Icon icon={ChevronDown} width={20} height={20} className="flex-shrink-0" />}
        </div>
      </div>
      {!folded && (
        <div className="px-[30px] pr-[14px] py-[15px] border-2 border-gray-600 border-t-0 min-h-[196px]">
          <div className="flex flex-row w-full">
            {uiResult ? (
              <div className="flex-grow overflow-auto">
                <div className={cn('flex flex-row items-start overflow-auto', 'mt-2')}>
                  <div className="flex-grow overflow-auto ">{uiResult}</div>

                  <div
                    className={cn('flex flex-none gap-4 px-4 self-start', {
                      'min-w-[100px] ml-[92px]': false,
                    })}
                  >
                    <MessageControls
                      isEditing={true}
                      hideControls={false}
                      onCancelClick={() => {
                        setUIResult(null);
                      }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-grow overflow-auto">
                <span className="text-[15px] w-20 flex-none">{upperFirst(tool_call.language || '')}: </span>
                <EditableContentMessage
                  initialContent={tool_call.code}
                  language={tool_call.language}
                  handleAcceptedContent={handleAcceptedContent}
                  handleRemoveClick={handleRemoveClick}
                  className="mt-2"
                >
                  <SyntaxHighlighter
                    style={customVs2015}
                    children={tool_call.code}
                    language={tool_call.language}
                    className="overflow-scroll flex-grow rounded-md !m-0"
                  />
                </EditableContentMessage>
                {isViableForRunningCode(tool_call.id) && !tool_call.is_streaming && !chat?.lock_id && (
                  <div className="flex gap-4 pt-2 mt-2">
                    <Button variant="status" statusColor="green" small onClick={handleRunClick}>
                      <Icon icon={Play} />
                      Run
                    </Button>

                    {!alwaysExecuteCode && (
                      <Button onClick={handleAlwaysRunClick} variant="status" statusColor="purple" small>
                        <Icon icon={Infinity} />
                        Always Run
                      </Button>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          <div>
            {tool_call.output != undefined && (
              <ToolOutput syntaxHighlighterCustomStyles={customVs2015} tool_call={tool_call} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
