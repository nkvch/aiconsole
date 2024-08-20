import React from 'react';
import collapseIcon from '../../../public/collapse.png';
import expandIcon from '../../../public/expand.png';

interface CollapseButtonProps {
  isCollapsed: boolean;
  onClick: () => void;
}

const CollapseButton: React.FC<CollapseButtonProps> = ({ isCollapsed, onClick }) => {
  return (
    <button
      onClick={onClick}
    >
      {isCollapsed ? (
        <img src={expandIcon} alt="Expand" width={30} />
      ) : (
        <img src={collapseIcon} alt="Collapse" width={30} />
      )}
    </button>
  );
};

export default CollapseButton;
