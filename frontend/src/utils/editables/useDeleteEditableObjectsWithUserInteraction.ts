import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { EditableObjectType } from '@/types/editables/assetTypes';
import { useSelectedEditableObject } from './useSelectedEditableObject';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';

export function useDeleteEditableObjectsWithUserInteraction(editableObjectType: EditableObjectType) {
  const deleteEditableObjects = useEditablesStore((state) => state.deleteEditableObjects);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const [editable] = useSelectedEditableObject();

  async function handleDelete(ids: string[]) {
    await deleteEditableObjects(editableObjectType, ids);

    // if currently selected editable is among the deleted objects, remove selection and go back to init screen.
    // as pointed out in Discord thread, application doesn't have no-asset selected feature implemented.
    if (editable?.id && ids.includes(editable?.id)) {
      setSelectedAsset(undefined);
      setLastSavedSelectedAsset(undefined);
    }
  }

  return handleDelete;
}
