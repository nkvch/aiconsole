import { BrowserWindow } from 'electron';
import settings from 'electron-settings';
import debounce from 'lodash.debounce';

type WindowState = {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  isMaximized?: boolean;
};

export const windowStateTracker = async (windowName: string) => {
  let localWindow: BrowserWindow;
  let windowState: WindowState = {};

  const initState = async () => {
    if (await settings.has(`windowState.${windowName}`)) {
      windowState = (await settings.get(`windowState.${windowName}`)) as WindowState;
      return;
    }

    windowState = {
      x: undefined,
      y: undefined,
      width: 1280,
      height: 720,
    };
  };

  const updateState = debounce(async () => {
    if (!windowState.isMaximized) {
      windowState = localWindow.getBounds();
    }

    windowState.isMaximized = localWindow.isMaximized();
    await settings.set(`windowState.${windowName}`, windowState);
  }, 100);

  const track = (win: BrowserWindow) => {
    localWindow = win;

    // TODO: Fix the event typing in the handler
    // @ts-ignore
    ['resize', 'move'].forEach((e: string) => win.on(e, updateState));
  };

  await initState();

  return {
    x: windowState.x,
    y: windowState.y,
    width: windowState.width,
    height: windowState.height,
    isMaximized: windowState.isMaximized,
    track,
  };
};
