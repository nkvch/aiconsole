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

import { TopBar } from '@/components/common/TopBar';
import { HomeTopBarElements } from '@/components/projects/HomeTopBarElements';
import { useRecentProjectsStore } from '@/store/projects/useRecentProjectsStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useProjectStore } from '../../store/projects/useProjectStore';
import { ProjectCard } from './ProjectCard';
import { RecentProjectsEmpty } from './RecentProjectsEmpty';
import AlertDialog from '../common/AlertDialog';
import { useCallback, useState } from 'react';
import { useProjectFileManager } from '@/utils/projects/useProjectFileManager';

export type ModalProjectTitle = 'Locate' | 'Delete';
export interface ModalProjectProps {
  name: string;
  title: ModalProjectTitle;
  path: string;
}

export function Home() {
  const openAiApiKey = useSettingsStore((state) => state.openAiApiKey);
  const isApiKeyValid = useSettingsStore((state) => state.isApiKeyValid);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);
  const recentProjects = useRecentProjectsStore((state) => state.recentProjects);
  const removeRecentProject = useRecentProjectsStore((state) => state.removeRecentProject);
  const { initProject } = useProjectFileManager();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentProject, setCurrentProject] = useState<ModalProjectProps>({ name: '', title: 'Locate', path: '' });
  const isLocateType = currentProject.title === 'Locate';

  const openModalProject = (project: ModalProjectProps) => {
    setCurrentProject(project);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentProject({ name: '', title: 'Locate', path: '' });
  };

  const deleteProject = useCallback(
    (path: string) => async () => {
      await removeRecentProject(path);
      closeModal();
    },
    [removeRecentProject],
  );

  return (
    <div className="min-h-[100vh] bg-recent-bg bg-cover bg-top">
      <div>
        {openAiApiKey === undefined || isProjectLoading ? (
          <>{/* the request is in progress - don't render anything to avoid flickering */}</>
        ) : (
          <div className="h-screen max-h-screen overflow-hidden flex flex-col">
            {recentProjects.length > 0 && openAiApiKey && isApiKeyValid ? (
              <>
                <TopBar>
                  <HomeTopBarElements />
                </TopBar>
                <div className="px-5 pb-10 pt-[40px] flex-1 flex flex-col grow overflow-hidden">
                  <div className="px-[60px] text-white ">
                    <img src="favicon.png" className="shadows-lg w-[60px] h-[60px] mx-auto m-4" alt="Logo" />
                    <h1 className="text-[32px] md:text-[38px] xl:text-[42px] 2xl:text-[56px] mb-[50px] font-black text-center">
                      Welcome to <span className=" text-primary">AIConsole!</span>
                    </h1>
                    <div className="px-4 pb-[30px] text-center opacity-75 text-gray-400">Recent projects:</div>
                  </div>
                  <div className="w-full flex flex-wrap justify-center gap-[20px] mx-auto overflow-auto pr-5">
                    {recentProjects.map(({ name, path, recent_chats, stats, incorrect_path }) => (
                      <div
                        key={path}
                        className="w-full md:w-[calc(50%-10px)] xl:w-[calc(33.333%-13.33px)] 2xl:w-[calc(25%-15px)]"
                      >
                        <ProjectCard
                          name={name}
                          path={path}
                          recentChats={recent_chats}
                          incorrectPath={incorrect_path}
                          stats={stats}
                          openModalProject={openModalProject}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : null}

            {!recentProjects.length || !openAiApiKey || !isApiKeyValid ? (
              <RecentProjectsEmpty openAiApiKey={openAiApiKey} isApiKeyValid={isApiKeyValid} />
            ) : null}
          </div>
        )}
      </div>
      <AlertDialog
        title={isLocateType ? "Can't find the project" : 'Delete file'}
        isOpen={isModalOpen}
        onClose={closeModal}
        onConfirm={isLocateType ? () => initProject('existing') : deleteProject(currentProject.path)}
        confirmationButtonText={isLocateType ? 'Locate project' : 'Yes, delete'}
        cancelButtonText={isLocateType ? 'Close' : 'No, cancel'}
      >
        {isLocateType
          ? `The "${currentProject.name}" project has been deleted or its location has been changed.`
          : 'Are you sure you want to delete the file?'}
      </AlertDialog>
    </div>
  );
}
