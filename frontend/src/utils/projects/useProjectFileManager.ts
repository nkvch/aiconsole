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

import { ProjectsAPI } from '@/api/api/ProjectsAPI';
import { useCallback, useEffect, useState } from 'react';
import { useProjectStore } from '../../store/projects/useProjectStore';

export enum ProjectModalMode {
  OPEN_NEW,
  OPEN_EXISTING,
  CLOSED,
}

export const useProjectFileManager = () => {
  const [projectModalMode, setProjectModalMode] = useState<ProjectModalMode>(ProjectModalMode.CLOSED);
  const [tempPath, setTempPath] = useState('');
  const [isProjectDirectory, setIsProjectDirectory] = useState<boolean>();

  const chooseProject = useProjectStore((state) => state.chooseProject);

  const checkPath = async (pathToCheck?: string) => {
    let pathFromElectron;

    if (!pathToCheck && window?.electron?.openDirectoryPicker) {
      pathFromElectron = await window?.electron?.openDirectoryPicker();

      if (!pathFromElectron) {
        return;
      }
    }

    const path = pathToCheck || pathFromElectron || (await ProjectsAPI.getInitialPath()).directory;
    const { is_project: isProject } = await ProjectsAPI.isProjectDirectory(path);
    setIsProjectDirectory(isProject);
    setTempPath(path);
    if (isProject === undefined && !path) {
      await ProjectsAPI.chooseProject(path);
    }
  };

  const resetIsProjectFlag = () => {
    setIsProjectDirectory(undefined);
    setTempPath('');
  };

  const openProjectConfirmation = useCallback(() => {
    chooseProject(tempPath);
    resetIsProjectFlag();
    setProjectModalMode(ProjectModalMode.CLOSED);
  }, [chooseProject, tempPath]);

  useEffect(() => {
    if (isProjectDirectory === false && projectModalMode === ProjectModalMode.OPEN_NEW) {
      openProjectConfirmation();
      return;
    }
    if (isProjectDirectory === true && projectModalMode === ProjectModalMode.OPEN_EXISTING) {
      openProjectConfirmation();
      return;
    }
  }, [openProjectConfirmation, projectModalMode, isProjectDirectory]);

  const initProject = (mode: 'new' | 'existing') => {
    checkPath();
    setProjectModalMode(mode === 'new' ? ProjectModalMode.OPEN_NEW : ProjectModalMode.OPEN_EXISTING);
  };

  const resetProjectOpening = () => {
    resetIsProjectFlag();
    setProjectModalMode(ProjectModalMode.CLOSED);
  };

  return {
    initProject,
    isProjectDirectory,
    projectModalMode,
    resetProjectOpening,
    openProjectConfirmation,
    tempPath,
  };
};
