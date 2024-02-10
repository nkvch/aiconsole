import { useChatStore } from '@/store/editables/chat/useChatStore';
import React, { ReactElement } from 'react';

// APIs to be injected

async function submitCommand(command: string): Promise<void> {
  const submitCommand = useChatStore.getState().submitCommand;
  return submitCommand(command);
}

async function fetchCommand(command: string, columns: string[]): Promise<object[]> {
  const rets = [];

  for (let i = 0; i < 10; i++) {
    const obj: { [key: string]: string } = {};

    columns.forEach((col) => {
      obj[col] = `${col}-${i}`;
    });

    rets.push(obj);
  }

  return rets;
}

export const createSandbox = (code: string): ReactElement | null => {
  const apis = {
    React,
    submitCommand,
    fetchCommand,
  };

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
