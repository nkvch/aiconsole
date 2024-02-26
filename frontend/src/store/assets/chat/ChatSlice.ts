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

import { StateCreator } from 'zustand';

import { AssetsAPI } from '@/api/api/AssetsAPI';
import { AICChat } from '@/types/assets/chatTypes';
import { useAssetStore } from '../useAssetStore';
import { ChatStore, useChatStore } from './useChatStore';
import { ChatAPI } from '@/api/api/ChatAPI';

export type ChatSlice = {
  chat?: AICChat;
  chatOptions?: {
    agentId: string;
    materialsIds: string[];
    aiCanAddExtraMaterials: boolean;
    draft_command: string;
  };
  lastUsedChat?: AICChat;
  isChatLoading: boolean;
  isChatOptionsExpanded: boolean;
  setLastUsedChat: (chat?: AICChat) => void;
  setChat: (chat: AICChat) => void;
  renameChat: (newChat: AICChat) => Promise<void>;
  setIsChatLoading: (isLoading: boolean) => void;
  setIsChatOptionsExpanded: (isExpanded: boolean) => void;

  setSelectedAgentId: (id: string) => void;
  setSelectedMaterialsIds: (ids: string[]) => void;
  setAICanAddExtraMaterials: (aiCanAddExtraMaterials: boolean) => void;
  setDraftCommand: (draftCommand: string) => void;

  chatOptionsSaveDebounceTimer: NodeJS.Timeout | null;
};

export const createChatSlice: StateCreator<ChatStore, [], [], ChatSlice> = (set, get) => ({
  isChatLoading: false,
  chat: undefined,
  chatOptions: undefined,
  agent: undefined,
  lastUsedChat: undefined,
  isChatOptionsExpanded: true,
  materials: [],
  chatOptionsSaveDebounceTimer: null,
  setLastUsedChat: (chat?: AICChat) => {
    set({ lastUsedChat: chat });
  },
  setChat: (chat: AICChat) => {
    set({
      chat,
      chatOptions: {
        agentId: chat.chat_options.agent_id,
        materialsIds: chat.chat_options.materials_ids,
        aiCanAddExtraMaterials: chat.chat_options.ai_can_add_extra_materials,
        draft_command: chat.chat_options.draft_command,
      },
    });
  },
  renameChat: async (newChat: AICChat) => {
    await AssetsAPI.updateAsset(newChat, newChat.id);
    get().setChat(newChat);

    //If it's chat we need to reload chat history because there is no autoreload on change for chats
    useAssetStore.getState().initAssets();
  },
  setIsChatLoading: (isLoading: boolean) => {
    set({ isChatLoading: isLoading });
  },
  setIsChatOptionsExpanded: (isExpanded: boolean) => {
    set({ isChatOptionsExpanded: isExpanded });
  },
  setSelectedAgentId: (id: string) => {
    set((state) => {
      const newState = {
        chatOptions: {
          agentId: id,
          materialsIds: state.chatOptions?.materialsIds ?? [],
          aiCanAddExtraMaterials: state.chatOptions?.aiCanAddExtraMaterials ?? true,
          draft_command: state.chatOptions?.draft_command ?? '',
        },
      };
      debounceChatOptionsUpdate(state.chat?.id, newState.chatOptions);
      return newState;
    });
  },
  setSelectedMaterialsIds: (ids: string[]) => {
    set((state) => {
      const newState = {
        chatOptions: {
          agentId: state.chatOptions?.agentId ?? '',
          materialsIds: ids,
          aiCanAddExtraMaterials: state.chatOptions?.aiCanAddExtraMaterials ?? true,
          draft_command: state.chatOptions?.draft_command ?? '',
        },
      };
      debounceChatOptionsUpdate(state.chat?.id, newState.chatOptions);
      return newState;
    });
  },
  setAICanAddExtraMaterials: (aiCanAddExtraMaterials: boolean) => {
    set((state) => {
      const newState = {
        chatOptions: {
          agentId: state.chatOptions?.agentId ?? '',
          materialsIds: state.chatOptions?.materialsIds ?? [],
          aiCanAddExtraMaterials,
          draft_command: state.chatOptions?.draft_command ?? '',
        },
      };
      debounceChatOptionsUpdate(state.chat?.id, newState.chatOptions);
      return newState;
    });
  },
  setDraftCommand: (draftCommand: string) => {
    set((state) => {
      const newState = {
        chatOptions: {
          agentId: state.chatOptions?.agentId ?? '',
          materialsIds: state.chatOptions?.materialsIds ?? [],
          aiCanAddExtraMaterials: state.chatOptions?.aiCanAddExtraMaterials ?? true,
          draft_command: draftCommand,
        },
      };
      debounceChatOptionsUpdate(state.chat?.id, newState.chatOptions);
      return newState;
    });
  },
});

const debounceChatOptionsUpdate = (
  chatId: string | undefined,
  chatOptions: { agentId: string; materialsIds: string[]; aiCanAddExtraMaterials: boolean; draft_command: string },
) => {
  const debounceDelay = 500; // milliseconds

  const timer = useChatStore.getState().chatOptionsSaveDebounceTimer;
  if (timer) {
    clearTimeout(timer);
    useChatStore.setState({ chatOptionsSaveDebounceTimer: null });
  }

  useChatStore.setState({
    chatOptionsSaveDebounceTimer: setTimeout(async () => {
      if (chatId) {
        // Assuming there's a method in ChatAPI to update chat options
        await ChatAPI.saveChatOptions(chatId, {
          agent_id: chatOptions.agentId,
          materials_ids: chatOptions.materialsIds,
          ai_can_add_extra_materials: chatOptions.aiCanAddExtraMaterials,
          draft_command: chatOptions.draft_command,
        });
        console.debug(`Chat options updated for chatId: ${chatId} with options: ${JSON.stringify(chatOptions)}`);
      }
      useChatStore.setState({ chatOptionsSaveDebounceTimer: null });
    }, debounceDelay),
  });
};
