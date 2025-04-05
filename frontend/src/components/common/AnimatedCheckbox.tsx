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

import { cn } from '@/utils/common/cn';
import { EditableObjectType } from '@/types/editables/assetTypes';

interface CheckboxProps {
  checked: boolean;
  onChange: () => void;
  type: EditableObjectType;
}

export const Checkbox = ({ checked, onChange, type }: CheckboxProps) => {
  return (
    <div 
      className={cn(
        "relative flex items-center",
        type === 'chat' && 'text-chat',
        type === 'material' && 'text-material',
        type === 'agent' && 'text-agent'
      )}  
    >
      <input
        type="checkbox"
        id="cbx"
        checked={checked}
        onChange={() => {}}
        className="absolute w-[18px] h-[18px] hidden"
      />
      <label 
        htmlFor="cbx" 
        onClick={onChange} 
        className="check absolute m-auto w-[18px] h-[18px] cursor-pointer touch-manipulation transform-gpu
                  before:content-[''] before:absolute before:-top-[15px] before:-left-[15px]
                  before:w-[48px] before:h-[48px] before:rounded-full before:bg-[#22325408]
                  before:opacity-0 before:transition-opacity hover:before:opacity-100"
      >
        <svg 
          className="svg relative z-[1] w-full h-full stroke-[#C8CCD4] transform-gpu transition-all duration-200" 
          width="18px" 
          height="18px" 
          viewBox="0 0 18 18"
        >
          <path d="M1,9 L1,3.5 C1,2 2,1 3.5,1 L14.5,1 C16,1 17,2 17,3.5 L17,14.5 C17,16 16,17 14.5,17 L3.5,17 C2,17 1,16 1,14.5 L1,9 Z"></path>
          <polyline points="1 9 7 14 15 4"></polyline>
        </svg>
      </label>
    </div>
  );
}; 