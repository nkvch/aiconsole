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

import OpenAiApiKeyForm from '@/components/settings/OpenAiApiKeyForm';
import { ProjectButtons } from './ProjectButtons';
import { GithubLogin } from '../auth/GithubLogin';
import { useUser } from '@/store/users/useUser';

interface RecentProjectsEmptyProps {
  openAiApiKey: string | null | undefined;
  isApiKeyValid: boolean | undefined;
}

export function RecentProjectsEmpty({ openAiApiKey, isApiKeyValid }: RecentProjectsEmptyProps) {
  const { user, isLoading, error, loginWithGithub } = useUser();
  const isApiKeySet = openAiApiKey && isApiKeyValid;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[100vh]">
        <p className="text-white">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[100vh]">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }
  if (!user) {
    return (
      <div className="flex justify-center items-center flex-col min-h-[100vh] px-[60px] relative">
        <div className="my-[180px]">
          <img src="favicon.png" className="shadows-lg w-[60px] h-[60px] mx-auto" alt="Logo" />
          <h1 className="text-center font-black text-white">
            Welcome to <span className="text-primary">AIConsole</span>
          </h1>
          <GithubLogin onLogin={loginWithGithub} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center flex-col min-h-[100vh] px-[60px] relative">
      <div className="my-[180px]">
        <img src="favicon.png" className="shadows-lg w-[60px] h-[60px] mx-auto" alt="Logo" />
        <h1 className="text-center font-black text-white">
          Welcome to <span className="text-primary">AIConsole</span>
        </h1>

        {isApiKeySet ? (
          <ProjectButtons className="relative flex justify-center gap-[20px] mt-5 py-[10px] z-10" />
        ) : (
          <div className="mb-[-40px] max-w-[714px] relative z-10">
            <OpenAiApiKeyForm />
          </div>
        )}
      </div>
      {isApiKeySet && (
        <img
          src="recent-projects-empty-image.png"
          className="relative z-0 mx-auto mt-[-200px] sm:mt-[-250px] lg:mt-[-300px] 2xl:mt-[-400px]"
          alt="aiconsole chat image"
        />
      )}
    </div>
  );
}