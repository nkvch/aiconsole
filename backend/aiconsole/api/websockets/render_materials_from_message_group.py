from dataclasses import dataclass
from typing import cast

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import Material
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.types import AICMessageGroup, Chat
from aiconsole.core.project import project


@dataclass
class MaterialsAndRenderedMaterials:
    materials: list[Material]
    rendered_materials: list[RenderedMaterial]


async def render_materials_from_message_group(
    message_group: AICMessageGroup, chat: Chat, agent: AICAgent, init: bool = False
) -> MaterialsAndRenderedMaterials:
    relevant_materials_ids = message_group.materials_ids

    relevant_materials = [
        cast(Material, project.get_project_materials().get_asset(material_id))
        for material_id in relevant_materials_ids
    ]

    content_context = ContentEvaluationContext(
        chat=chat,
        agent=agent,
        gpt_mode=agent.gpt_mode,
        relevant_materials=relevant_materials,
    )

    # rendered_materials = await asyncio.gather(
    #     *[
    #         material.render(content_context)
    #         for material in relevant_materials
    #         if init or material.type == "rendered_material"
    #     ]
    # )
    rendered_materials = []
    for material in relevant_materials:
        rendered_material = await material.render(content_context)
        rendered_materials.append(rendered_material)

    return MaterialsAndRenderedMaterials(materials=relevant_materials, rendered_materials=rendered_materials)
