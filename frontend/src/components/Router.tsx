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

import { useEffect } from 'react';
import { v4 as uuid } from 'uuid';
import {
  createHashRouter,
  createRoutesFromElements,
  Navigate,
  Outlet,
  Route,
  RouterProvider,
  Routes,
} from 'react-router-dom';

import { TopBar } from '@/components/common/TopBar';
import { ProjectTopBarElements } from '@/components/projects/ProjectTopBarElements';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { AssetEditor } from './editables/assets/AssetEditor';
import { ChatPage } from './editables/chat/ChatPage';
import SideBar from './editables/sidebar/SideBar';
import { Home } from './projects/Home';
import { GlobalSettingsModal } from './settings/modal/GlobalSettingsModal';
import { useAPIStore } from '@/store/useAPIStore';
import { useToastsStore } from '@/store/common/useToastsStore';

function MustHaveProject() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  if (!isProjectOpen && !isProjectLoading) {
    return <Navigate to="/" />;
  }

  return <Outlet />;
}

function NoProject() {
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);

  if (isProjectOpen && !isProjectLoading) {
    return <Navigate to={`/chats/${uuid()}`} />;
  }

  return <Outlet />;
}

const HomeRoute = () => (
  <>
    <Home />
    <GlobalSettingsModal />
  </>
);

export function Router() {
  const port = useAPIStore((state) => state.port);

  const showToast = useToastsStore.getState().showToast;

  useEffect(() => {
    window.electron?.onBackendExit(() => {
      showToast({
        title: 'Application Error',
        message: 'Please restart the app.',
        variant: 'error',
      });
    });

    return () => {
      window.electron?.disposeBackendExitListener();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!port) {
    return null;
  }

  return (
    <RouterProvider
      router={createHashRouter(
        createRoutesFromElements(
          <>
            <Route path="/" element={<NoProject />}>
              <Route index element={<HomeRoute />} />
            </Route>
            <Route path="/" element={<MustHaveProject />}>
              <Route
                path="*"
                element={
                  <div className="App flex flex-col h-screen fixed top-0 left-0 bottom-0 right-0 bg-gray-900 text-stone-400">
                    <GlobalSettingsModal />
                    <TopBar>
                      <ProjectTopBarElements />
                    </TopBar>
                    <div className="flex flex-row h-full overflow-y-auto">
                      <Routes>
                        <Route path="/agents/*" element={<SideBar initialTab="agents" />} />
                        <Route path="/materials/*" element={<SideBar initialTab="materials" />} />
                        <Route path="/chats/*" element={<SideBar initialTab="chats" />} />
                      </Routes>
                      <Routes>
                        <Route path="/chats/:id" element={<ChatPage />} />
                        <Route path="/materials/:id" element={<AssetEditor assetType={'material'} />} />
                        <Route path="/agents/:id" element={<AssetEditor assetType={'agent'} />} />
                      </Routes>
                    </div>
                  </div>
                }
              />
            </Route>
          </>,
        ),
      )}
    />
  );
}
