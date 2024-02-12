import React, { ReactNode } from 'react';

// APIs to be injected
const apis = {
  React,
};

export const createSandbox = (code: string): (() => ReactNode) | null => {
  const frame = document.createElement('iframe');
  document.body.appendChild(frame);
  const F = frame.contentWindow?.window.Function;

  if (!F) {
    return null;
  }

  const sandboxedCode = new F(...Object.keys(apis), code);

  document.body.removeChild(frame);

  return sandboxedCode(...Object.values(apis));
};
