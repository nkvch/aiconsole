type Action = {
  type: "selectItem" | "deselectItem" | "selectAll" | "selectNone" | "setCollection",
  payload?: {
    chatId?: string,
    collection?: string[],
  },
}

interface State {
  selectedItems: string[],
  collection: string[],
}

export const bulkSelectChatReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "selectItem":
      if (!action.payload?.chatId) return state;
      return {
        ...state,
        selectedItems: [...state.selectedItems, action.payload.chatId]
      };
    case "deselectItem":
      if (!action.payload?.chatId) return state;
      return {
        ...state,
        selectedItems: state.selectedItems.filter((id: string) => id !== action.payload?.chatId)
      };
    case "selectAll":
      return {
        ...state,
        selectedItems: state.collection
      };
    case "selectNone":
      return {
        ...state,
        selectedItems: []
      };
    case "setCollection":
      if (!action.payload?.collection) return state;
      return {
        ...state,
        selectedItems: [],
        collection: action.payload.collection
      }
    default:
      return state;
  }
};
