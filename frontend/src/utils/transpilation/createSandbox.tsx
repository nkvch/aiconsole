import React, { ReactElement } from 'react';

// APIs to be injected
const apis = {
  React,
};

export const createSandbox = (code: string): ReactElement | null => {
  const frame = document.createElement('iframe');
  document.body.appendChild(frame);
  const F = frame.contentWindow?.window.Function;

  if (!F) {
    return null;
  }

  const sandboxedCode = new F(...Object.keys(apis), code);

  //TODO: document.body.removeChild(frame);

  const R = sandboxedCode(...Object.values(apis));

  return <R />;
};
