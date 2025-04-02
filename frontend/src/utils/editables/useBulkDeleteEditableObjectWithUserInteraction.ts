import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { Asset, EditableObjectType } from '@/types/editables/assetTypes';
import { useSelectedEditableObject } from './useSelectedEditableObject';
import { isAsset } from './isAsset';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { EditablesAPI } from '@/api/api/EditablesAPI';

export function useBulkDeleteEditableObjectWithUserInteraction(editableObjectType: EditableObjectType) {
  const deleteEditableObject = useEditablesStore((state) => state.bulkDeleteEditableObjects);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const [editable] = useSelectedEditableObject();

  async function handleDelete(ids: string[]) {
    await deleteEditableObject(editableObjectType, ids);

    ids.forEach(async (id) => {
      if (editable?.id === id) {
        if (isAsset(editableObjectType) && (editable as Asset).override) {
          //Force reload of the current asset
          const newAsset = await EditablesAPI.fetchEditableObject<Asset>({ editableObjectType, id });
          setSelectedAsset(newAsset);
          setLastSavedSelectedAsset(newAsset);
        }
      }
    })
  }

  return handleDelete;
}
