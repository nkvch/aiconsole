import { SVGProps } from 'react';

export const SquareFill = (props: SVGProps<SVGSVGElement>): React.ReactElement => (
  <svg {...props} width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M18.25 1.75H1.75V18.25H18.25V1.75Z"
      fill="currentColor"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
