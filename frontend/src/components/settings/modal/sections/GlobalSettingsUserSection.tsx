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

import ImageUploader from '@/components/common/ImageUploader';
import { Icon } from '@/components/common/icons/Icon';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { Pencil } from 'lucide-react';
import { useEffect, useState } from 'react';

interface GlobalSettingsUserSectionProps {
  username?: string;
  setUsername: (value: string) => void;
  setImage: (avatar: File) => void;
}

const GlobalSettingsUserSection = ({ username, setUsername, setImage }: GlobalSettingsUserSectionProps) => {
  const currentUsername = useSettingsStore((state) => state.settings.user_profile.display_name) || '';
  const userAvatar = useSettingsStore((state) => state.settings.user_profile.profile_picture) || undefined;

  const [isEditMode, setIsEditMode] = useState(false);
  const [usernameFormValue, setUsernameFormValue] = useState(username);

  useEffect(() => {
    if (typeof username === 'string') {
      setUsernameFormValue(username);
    } else {
      setUsernameFormValue(currentUsername);
    }
  }, [username, currentUsername]);

  const handleNameInputBlur = () => {
    if (!username) {
      setUsername(currentUsername);
    }
    setIsEditMode(false);
  };

  return (
    <div className="flex items-center w-full gap-[30px]">
      <ImageUploader currentImage={userAvatar} onUpload={setImage} />
      <div className="flex flex-col justify-between h-full">
        <div className="flex gap-2.5 text-[25px] font-black pt-[30px]">
          <h2 className="text-gray-400">Hello, </h2>
          {isEditMode ? (
            <input
              type="text"
              value={usernameFormValue}
              onChange={(e) => setUsername(e.target.value)}
              className="bg-transparent text-white rounded-[8px] outline-none focus:ring-1 focus:ring-gray-400 transition duration-100"
              onBlur={handleNameInputBlur}
              autoFocus
            />
          ) : (
            <div className="flex gap-5 items-center">
              <h2 className="text-white">{username || currentUsername}</h2>
              <button onClick={() => setIsEditMode(true)}>
                <Icon icon={Pencil} className="text-gray-400 h-6 w-6" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default GlobalSettingsUserSection;
