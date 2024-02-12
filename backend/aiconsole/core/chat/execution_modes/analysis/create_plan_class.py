# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random

from pydantic import Field

from aiconsole.core.gpt.function_calls import OpenAISchema


def create_plan_class(available_agents, available_materials):
    class Plan(OpenAISchema):
        """
        Plan what should happen next.
        """

        thinking_process: str = Field(
            description="Short description (up to two short sentences) of the thinking process that led to the next step.",
            json_schema_extra={"type": "string"},
        )

        next_step: str = Field(
            description="A short actionable description of the next single atomic task to move this conversation "
            "forward.",
            json_schema_extra={"type": "string"},
        )

        is_final_step: bool = Field(
            ...,
            description="Whether this is the final step to be done by the agents, and after it, it will be the user's turn.",
            json_schema_extra={"type": "boolean"},
        )

        is_users_turn: bool = Field(
            ...,
            description="Whether the initiative is on the user side or on assistant side.",
            json_schema_extra={"type": "boolean"},
        )

        agent_id: str = Field(
            description="Chosen agent to perform the next step.",
            json_schema_extra={"enum": [s.id for s in random.sample(available_agents, len(available_agents))]},
        )

        relevant_material_ids: list[str] = Field(
            ...,
            description="Chosen material ids relevant for the task",
            json_schema_extra={
                "items": {
                    "enum": [k.id for k in random.sample(available_materials, len(available_materials))],
                    "type": "string",
                }
            },
        )

    return Plan
