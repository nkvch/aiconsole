from typing import Literal

from pydantic import BaseModel


class ActorId(BaseModel):
    type: Literal["user", "agent"]
    id: str

    def __hash__(self):
        return hash((self.type, self.id))
