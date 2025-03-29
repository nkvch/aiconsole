import React from 'react';
import { Trash } from 'lucide-react';

interface BulkActionsProps {
  selectedCount: number;
  onDelete: () => void;
}

export const BulkActions: React.FC<BulkActionsProps> = ({ selectedCount, onDelete }) => {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 flex items-center gap-4 bg-white p-4 rounded-lg shadow-lg">
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600">
          {selectedCount} {selectedCount === 1 ? 'item' : 'items'} selected
        </span>
        <button
          onClick={onDelete}
          className="flex items-center gap-2 px-4 py-2 border-2 border-red-500 text-red-500 rounded hover:bg-red-50 transition-colors font-medium"
        >
          <Trash size={16} />
          Delete Selected
        </button>
      </div>
    </div>
  );
};
