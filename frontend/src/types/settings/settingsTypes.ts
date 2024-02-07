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

import { z } from 'zod';
import { AssetStatusSchema } from '../editables/assetTypes';

export type Settings = {
  code_autorun?: boolean;
  openai_api_key?: string;
  user_profile?: {
    username?: string;
    email?: string;
    avatar_url?: string;
  };
};

const GPTModeConfigSchema = z.object({
  max_tokens: z.number(),
  encoding: z.enum(['gpt-4', 'gpt-3.5-turbo']),
  model: z.string(),
  api_key: z.string(),
});

export type GPTModeConfig = z.infer<typeof GPTModeConfigSchema>;

// Define UserProfile schema
const UserProfileSchema = z.object({
  display_name: z.string(),
  profile_picture: z.string(), // Base64-encoded string
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

export const PartialSettingsDataSchema = z.object({
  user_id: z.string().optional(),
  code_autorun: z.boolean().optional(),
  openai_api_key: z.string().optional(),
  user_profile: UserProfileSchema.partial().optional(),
  materials: z.record(z.string(), AssetStatusSchema).optional(),
  materials_to_reset: z.array(z.string()).optional(),
  agents: z.record(z.string(), AssetStatusSchema).optional(),
  agents_to_reset: z.array(z.string()).optional(),
  gpt_modes: z.record(z.string(), GPTModeConfigSchema).optional(),
  extra: z.record(z.string(), z.any()).optional(),
});

export type PartialSettingsData = z.infer<typeof PartialSettingsDataSchema>;

export const SettingsDataSchema = z.object({
  user_id: z.string().optional(),
  code_autorun: z.boolean().default(false),
  openai_api_key: z.string().optional(),
  user_profile: UserProfileSchema,
  materials: z.record(z.string(), AssetStatusSchema).default({}),
  agents: z.record(z.string(), AssetStatusSchema).default({}),
  gpt_modes: z.record(z.string(), GPTModeConfigSchema).default({}),
  extra: z.record(z.string(), z.any()).default({}),
});

export type SettingsData = z.infer<typeof SettingsDataSchema>;
