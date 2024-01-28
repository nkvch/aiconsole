import { create } from 'zustand';
import { ProjectsAPI } from '@/api/api/ProjectsAPI';
import { useProjectStore } from '@/store/projects/useProjectStore';

export enum ProjectModalMode {
  OPEN_NEW,
  OPEN_EXISTING,
  LOCATE,
  DELETE,
  CLOSED,
}

export type FileManagerStore = {
  projectModalMode: ProjectModalMode;
  tempPath: string;
  isProjectDirectory?: boolean;
  projectName: string;

  setProjectModalMode: (mode: ProjectModalMode) => void;
  setTempPath: (path: string) => void;
  setIsProjectDirectory: (isProject: boolean) => void;
  initProject: (mode: ProjectModalMode) => Promise<void>;
  openModal: (mode: ProjectModalMode, path: string, name: string) => void;
  resetIsProjectFlag: () => void;
  openProjectConfirmation: () => void;
  resetProjectOpening: () => void;
};

export const useProjectFileManagerStore = create<FileManagerStore>((set, get) => ({
  projectModalMode: ProjectModalMode.CLOSED,
  tempPath: '',
  isProjectDirectory: undefined,
  projectName: '',

  setProjectModalMode: (mode) => set({ projectModalMode: mode }),
  setTempPath: (path) => set({ tempPath: path }),
  setIsProjectDirectory: (isProject) => set({ isProjectDirectory: isProject }),

  initProject: async (mode) => {
    let pathFromElectron;
    if (window?.electron?.openDirectoryPicker) {
      pathFromElectron = await window?.electron?.openDirectoryPicker();
      if (!pathFromElectron) return;
    }

    const path = pathFromElectron || (await ProjectsAPI.getInitialPath()).directory;
    const { is_project: isProject } = await ProjectsAPI.isProjectDirectory(path);
    get().setIsProjectDirectory(isProject);
    get().setTempPath(path);
    if (isProject === undefined && !path) {
      await ProjectsAPI.chooseProject(path);
    }

    set({ projectModalMode: mode });
  },

  openModal: (mode, path, name) => {
    set({ projectModalMode: mode, tempPath: path, projectName: name });
  },

  resetIsProjectFlag: () => {
    set({ isProjectDirectory: undefined, tempPath: '' });
  },

  openProjectConfirmation: () => {
    const { tempPath } = get();
    const chooseProject = useProjectStore.getState().chooseProject;
    chooseProject(tempPath);
    get().resetIsProjectFlag();
    set({ projectModalMode: ProjectModalMode.CLOSED });
  },

  resetProjectOpening: () => {
    get().resetIsProjectFlag();
    set({ projectModalMode: ProjectModalMode.CLOSED });
  },
}));
