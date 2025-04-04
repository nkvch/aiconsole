import { create } from 'zustand';

type Section = 'chats' | 'materials' | 'agents';

interface SelectionState {
  selections: Record<Section, string[]>;
  toggleSelection: (section: Section, id: string) => void;
  clearSelection: (section?: Section) => void;
  getSelectedCount: (section: Section) => number;
}

export const useSelectionStore = create<SelectionState>((set, get) => ({
  selections: {
    chats: [],
    materials: [],
    agents: [],
  },
  toggleSelection: (section, id) =>
    set((state) => ({
      selections: {
        ...state.selections,
        [section]: state.selections[section].includes(id)
          ? state.selections[section].filter((item) => item !== id)
          : [...state.selections[section], id],
      },
    })),
  clearSelection: (section) =>
    set((state) => ({
      selections: section
        ? { ...state.selections, [section]: [] }
        : { chats: [], materials: [], agents: [] },
    })),
  getSelectedCount: (section) => {
    const selections = get().selections;
    return selections && selections[section] ? selections[section].length : 0;
  },
})); 