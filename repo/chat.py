from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.chat import Chat, ChatType


class ChatRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_tg_chat_id(self, telegram_chat_id: int) -> Chat | None:
        stmt = select(Chat).where(Chat.telegram_chat_id == telegram_chat_id)
        return cast(Chat | None, await self._session.scalar(stmt))

    async def add(
        self,
        telegram_chat_id: int,
        chat_type: ChatType,
        *,
        username: str | None = None,
        title: str | None = None,
        language_code: str | None = None,
    ) -> Chat:
        chat = Chat(telegram_chat_id=telegram_chat_id, type=chat_type, username=username, title=title)
        if language_code is not None:
            chat.language_code = language_code
        self._session.add(chat)
        await self._session.flush()
        return chat
