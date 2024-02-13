from typing import Protocol

from aiconsole.core.chat.chat_mutations import ChatMutation
from aiconsole.core.chat.types import Chat


class ChatMutator(Protocol):
    # readonly chat: Chat
    @property
    def chat(self) -> Chat:  # fmt: off
        ...

    async def mutate(self, mutation: ChatMutation) -> None:  # fmt: off
        ...
