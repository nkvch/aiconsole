from typing import cast

from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.types import AssetStatus
from aiconsole.core.project import project


def agents_to_choose_from(all: bool = False) -> list[AICAgent]:
    assets_to_choose_from = project.get_project_agents().assets_with_status(AssetStatus.ENABLED)
    if all:
        assets_to_choose_from = project.get_project_agents().all_assets()
    agents_to_choose_from = cast(list[AICAgent], assets_to_choose_from)
    return agents_to_choose_from
