import { useEditablesStore } from '@/store/editables/useEditablesStore';
import { Asset, EditableObjectType } from '@/types/editables/assetTypes';
import { useSelectedEditableObject } from './useSelectedEditableObject';
import { isAsset } from './isAsset';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { EditablesAPI } from '@/api/api/EditablesAPI';

export function useDeleteEditableObjectWithUserInteraction(editableObjectType: EditableObjectType) {
  const deleteEditableObject = useEditablesStore((state) => state.deleteEditableObject);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const setLastSavedSelectedAsset = useAssetStore((state) => state.setLastSavedSelectedAsset);
  const [editable] = useSelectedEditableObject();

  async function handleDelete(id: string) {
    await deleteEditableObject(editableObjectType, id);

    if (editable?.id === id) {
      if (isAsset(editableObjectType) && (editable as Asset).override) {
        //Force reload of the current asset
        const newAsset = await EditablesAPI.fetchEditableObject<Asset>({ editableObjectType, id });
        setSelectedAsset(newAsset);
        setLastSavedSelectedAsset(newAsset);
      } else {
        //const navigate = useNavigate();
        //This causes the asset list to be fully reloaded, and is probably not really needed:
        //navigate(`/${editableObjectType}s`);
      }
    }
  }

  return handleDelete;
}
