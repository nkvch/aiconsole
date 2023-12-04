// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import ReactDOM from 'react-dom/client';
import { ContextMenuProvider } from 'mantine-contextmenu';
import * as Sentry from '@sentry/react';

import '@mantine/core/styles.css';
import '@mantine/core/styles.layer.css';
import '@mantine/notifications/styles.css';
import 'mantine-contextmenu/styles.layer.css';
import './index.css';
import './layout.css';

import { initStore } from './store/initStore.ts';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { Router } from './components/Router.tsx';
import { createRoutesFromChildren, matchRoutes, useLocation, useNavigationType } from 'react-router-dom';

Sentry.init({
  dsn: 'https://370c52dd1eee4886a999803f8bf94c2f@sentry.10clouds.com/590',
  integrations: [
    new Sentry.BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes,
      ),
    }),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MantineProvider>
      <Notifications position="top-right" />
      <ContextMenuProvider>
        <Router />
      </ContextMenuProvider>
    </MantineProvider>
  </React.StrictMode>,
);

initStore();
