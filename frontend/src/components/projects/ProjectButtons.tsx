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
import { useMemo } from 'react';
import { Plus } from 'lucide-react';

import { useProjectFileManager } from '@/utils/projects/useProjectFileManager';
import { Button } from '../common/Button';
import { cn } from '@/utils/common/cn';
import { Icon } from '../common/icons/Icon';
import AlertDialog from '../common/AlertDialog';
import { useRecentProjectsStore } from '@/store/projects/useRecentProjectsStore';

interface ProjectButtonsProps {
  className?: string;
}

export function ProjectButtons({ className }: ProjectButtonsProps): JSX.Element {
  const {
    isProjectDirectory,
    isNewProjectModalOpen,
    isOpenProjectModalOpen,
    openProject,
    newProject,
    handleReset,
    openProjectConfirmation,
    tempPath,
  } = useProjectFileManager();

  const recentProjects = useRecentProjectsStore((state) => state.recentProjects);

  const addButtonLabel = useMemo(
    () => (recentProjects.length ? 'New Project' : 'Create your first project'),
    [recentProjects.length],
  );

  return (
    <div className={cn(className)}>
      <AlertDialog
        title="This folder already contains an AIConsole project"
        isOpen={isProjectDirectory === true && isNewProjectModalOpen && Boolean(tempPath)}
        onClose={handleReset}
        onConfirm={openProjectConfirmation}
      >
        Do you want to open it instead?
      </AlertDialog>
      <AlertDialog
        title="There is no project in this directory"
        isOpen={isProjectDirectory === false && isOpenProjectModalOpen && Boolean(tempPath)}
        onClose={handleReset}
        onConfirm={openProjectConfirmation}
      >
        Do you want to create one there instead?
      </AlertDialog>

      <Button small onClick={newProject}>
        {addButtonLabel} <Icon icon={Plus} />
      </Button>

      <Button small variant="secondary" onClick={openProject}>
        Open an Existing Project
      </Button>
    </div>
  );
}
