from typing import cast

from aiconsole.core.assets.agents.agent import Agent
from aiconsole.core.assets.models import AssetStatus
from aiconsole.core.project import project


def agents_to_choose_from(all: bool = False) -> list[Agent]:
    assets_to_choose_from = project.get_project_agents().assets_with_status(AssetStatus.ENABLED)
    if all:
        assets_to_choose_from = project.get_project_agents().all_assets()
    agents_to_choose_from = cast(list[Agent], assets_to_choose_from)
    return agents_to_choose_from
