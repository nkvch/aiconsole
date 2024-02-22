import { StateCreator } from 'zustand';

import { Asset } from '@/types/editables/assetTypes';
import { EditablesAPI } from '../../api/api/EditablesAPI';
import { EditablesStore } from './useEditablesStore';
import { useProjectStore } from '@/store/projects/useProjectStore';

export type FileSlice = {
  files?: Asset[];
  initFiles: () => Promise<void>;
};

export const createFileSlice: StateCreator<EditablesStore, [], [], FileSlice> = (set) => ({
  files: undefined,
  initFiles: async () => {
    if (useProjectStore.getState().isProjectOpen) {
      const files = await EditablesAPI.fetchEditableObjects<Asset>('file');

      //sort alphabetically
      files.sort((a, b) => a.name.localeCompare(b.name));

      //sort by defined_in
      files.sort((a, b) => {
        const aDefinedIn = a.defined_in === 'project' ? 0 : 1;
        const bDefinedIn = b.defined_in === 'project' ? 0 : 1;
        return aDefinedIn - bDefinedIn;
      });

      //sort by status (forced first, disabled last, enabled in the middle)
      files.sort((a, b) => {
        const aStatus = a.status === 'forced' ? 0 : a.status === 'enabled' ? 1 : 2;
        const bStatus = b.status === 'forced' ? 0 : b.status === 'enabled' ? 1 : 2;
        return aStatus - bStatus;
      });
      set({
        files: files,
      });
    } else {
      set({ files: [] });
    }
  },
});
