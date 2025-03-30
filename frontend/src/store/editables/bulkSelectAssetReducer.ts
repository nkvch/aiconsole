import {Asset} from "@/types/editables/assetTypes.ts";

type Action = {
  type: "selectItem" | "deselectItem" | "selectAll" | "selectNone" | "setCollection",
  payload?: {
    asset?: Asset,
    collection?: Asset[],
  },
}

interface State {
  selectedItems: string[],
  restrictedItems: string[],
  collection: Asset[],
}

export const bulkSelectAssetReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "selectItem":
      if (!action.payload?.asset) return state;
      return {
        ...state,
        restrictedItems: action.payload.asset.defined_in === "aiconsole" ?
          [...state.restrictedItems, action.payload.asset.id] : state.restrictedItems
        ,
        selectedItems: [...state.selectedItems, action.payload.asset.id]
      };
    case "deselectItem":
      if (!action.payload?.asset) return state;
      return {
        ...state,
        restrictedItems: action.payload.asset.defined_in === "aiconsole" ?
          state.restrictedItems.filter(id => id !== action.payload?.asset?.id) : state.restrictedItems
        ,
        selectedItems: state.selectedItems.filter(id => id !== action.payload?.asset?.id)
      };
    case "selectAll":
      return {
        ...state,
        restrictedItems: state.collection.filter(asset => asset.defined_in === "aiconsole").map(
          restrictedAsset => restrictedAsset.id
        ),
        selectedItems: state.collection.map(asset => asset.id),
      };
    case "selectNone":
      return {
        ...state,
        restrictedItems: [],
        selectedItems: []
      };
    case "setCollection":
      if (!action.payload?.collection) return state;
      return {
        ...state,
        restrictedItems: [],
        selectedItems: [],
        collection: action.payload.collection
      }
    default:
      return state;
  }
};
