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

import { useState } from 'react';
import { Controller, useWatch } from 'react-hook-form';
import type { Control } from 'react-hook-form';
import { Pencil } from 'lucide-react';

import ImageUploader from '@/components/common/ImageUploader';
import { Icon } from '@/components/common/icons/Icon';
import { TextInput } from '@/components/editables/assets/TextInput';
import { GlobalSettingsFormData } from '@/forms/globalSettingsForm';

interface GlobalSettingsUserSectionProps {
  control: Control<GlobalSettingsFormData>;
  onImageSelected: (avatar: File) => void;
  avatarUrl?: string;
}

const GlobalSettingsUserSection = ({ onImageSelected, avatarUrl, control }: GlobalSettingsUserSectionProps) => {
  const [isEditMode, setIsEditMode] = useState(false);

  const watchName = useWatch({ control, name: 'user_profile.username' });

  const handleNameInputBlur = () => setIsEditMode(false);

  return (
    <div className="flex items-center w-full gap-[30px]">
      <ImageUploader currentImage={avatarUrl} onUpload={onImageSelected} />
      <div className="flex flex-col justify-between h-full">
        <div className="flex gap-2.5 text-[25px] font-black pt-[30px]">
          <h2 className="text-gray-400">Hello, </h2>
          {isEditMode ? (
            <Controller
              name="user_profile.username"
              control={control}
              render={({ field }) => (
                <input
                  type="text"
                  className="bg-transparent text-white rounded-[8px] outline-none focus:ring-1 focus:ring-gray-400 transition duration-100"
                  autoFocus
                  {...field}
                  onBlur={handleNameInputBlur}
                />
              )}
            />
          ) : (
            <div className="flex gap-5 items-center">
              <h2 className="text-white">{watchName}</h2>
              <button onClick={() => setIsEditMode(true)}>
                <Icon icon={Pencil} className="text-gray-400 h-6 w-6" />
              </button>
            </div>
          )}
          <div className="flex flex-col gap-2.5 w-[255px]">
            <p className="text-white text-[15px]">E-mail address</p>
            <Controller
              name="user_profile.email"
              control={control}
              render={({ field }) => <TextInput type="email" placeholder="Write e-mail here" {...field} />}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
export default GlobalSettingsUserSection;
