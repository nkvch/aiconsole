import { create } from 'zustand';

interface SelectionState {
  selectedItems: string[];
  toggleSelection: (id: string) => void;
  clearSelection: () => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  selectedItems: [],
  toggleSelection: (id) =>
    set((state) => ({
      selectedItems: state.selectedItems.includes(id)
        ? state.selectedItems.filter((item) => item !== id)
        : [...state.selectedItems, id],
    })),
  clearSelection: () => set({ selectedItems: [] }),
})); 