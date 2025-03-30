import {Button} from "@/components/common/Button.tsx";
import Checkbox from "@/components/common/Checkbox.tsx";
import {EditableObjectType} from "@/types/editables/assetTypes.ts";
import {
  useDeleteEditableObjectsWithUserInteraction
} from "@/utils/editables/useDeleteEditableObjectsWithUserInteraction.ts";


export const SideBarContentHeader = (
  { assetType, allItemsChecked, checkedItems, restrictedItems, onCheckAll }:
  {
    assetType: EditableObjectType;
    allItemsChecked: boolean;
    checkedItems: string[];
    restrictedItems: string[];
    onCheckAll: (checked: boolean) => void;
  })=> {
  // Possible handlers:
  // Didn't manage to implement other bulk operations (enable and disable) for material and agent assets.
  // This handleBulkDelete pointer would be eventually moved outside of this Component and passed through props.
  const handleBulkDelete = useDeleteEditableObjectsWithUserInteraction(assetType);

  return (
    <>
      <div className={'flex flex-row justify-between mb-2'} onContextMenu={() => {}}>
        <Checkbox checked={allItemsChecked} id={'header'} onChange={(isChecked) => {onCheckAll(isChecked)}} />
          <Button
            variant={'tertiary'}
            smallNoPadding
            transparent
            borderless
            classNames={'whitespace-nowrap hover:text-danger'}
            disabled={checkedItems.length === 0 || restrictedItems.length !== 0}
            onClick={() => handleBulkDelete(checkedItems)}
          >
            Delete ({checkedItems.length})
          </Button>
      </div>
      {restrictedItems.length !== 0 && (
        <span className={"text-sm text-gray-400 text-center mb-4"}>You have selected {restrictedItems.length} builtin assets!<br/> Some functions will be disabled.</span>
      )}
    </>
  );
};
