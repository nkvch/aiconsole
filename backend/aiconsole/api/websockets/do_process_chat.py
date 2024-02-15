from uuid import uuid4

from aiconsole.api.websockets.render_materials_from_message_group import (
    render_materials_from_message_group,
)
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.types import AssetLocation
from aiconsole.core.chat.actor_id import ActorId
from aiconsole.core.chat.chat_mutations import CreateMessageGroupMutation
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.execution_modes.analysis.agents_to_choose_from import (
    agents_to_choose_from,
)
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.gpt.consts import ANALYSIS_GPT_MODE
from aiconsole.core.gpt.types import GPTRole
from aiconsole.core.project import project

# TODO: Move this to a file
_director_agent = AICAgent(
    id="director",
    name="Director",
    gpt_mode=ANALYSIS_GPT_MODE,
    execution_mode="aiconsole.core.chat.execution_modes.director:execution_mode",
    usage="",
    usage_examples=[],
    defined_in=AssetLocation.AICONSOLE_CORE,
    override=False,
    system="",
)


async def do_process_chat(chat_mutator: ChatMutator):
    agent = _director_agent

    role: GPTRole
    if chat_mutator.chat.chat_options.agent_id and not chat_mutator.chat.chat_options.let_ai_add_extra_materials:
        for _agent in agents_to_choose_from(all=True):
            if _agent.id == chat_mutator.chat.chat_options.agent_id:
                agent = _agent

        role = "assistant"
    else:
        role = "system"

    # Create a new message group for analysis
    message_group_id = str(uuid4())

    if chat_mutator.chat.chat_options.materials_ids:
        materials_ids = chat_mutator.chat.chat_options.materials_ids
    else:
        materials_ids = []

    await chat_mutator.mutate(
        CreateMessageGroupMutation(
            message_group_id=message_group_id,
            actor_id=ActorId(type="agent", id=agent.id),
            role=role,
            materials_ids=materials_ids,
            analysis="",
            task="",
        )
    )

    if materials_ids:
        materials = [_m for _m in project.get_project_materials().all_assets() if _m.id in materials_ids]
        materials_and_rmats = await render_materials_from_message_group(
            chat_mutator.chat.message_groups[-1], chat_mutator.chat, agent, init=True
        )
        render_materials = materials_and_rmats.rendered_materials
    else:
        materials = []
        render_materials = []

    execution_mode = await import_and_validate_execution_mode(agent)
    await execution_mode.process_chat(
        chat_mutator=chat_mutator,
        agent=agent,
        materials=materials,  # type: ignore
        rendered_materials=render_materials,
    )
