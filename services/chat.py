from sqlalchemy.ext.asyncio import AsyncSession

from db.models.chat import Chat, ChatType
from repo.chat import ChatRepo


class ChatNotFoundError(Exception):
    pass


class ChatService:
    def __init__(self, session: AsyncSession) -> None:
        self.chat = ChatRepo(session)

    async def add(
        self,
        telegram_chat_id: int,
        chat_type: ChatType,
        *,
        username: str | None = None,
        title: str | None = None,
        language_code: str | None = None,
    ) -> Chat:
        return await self.chat.add(
            telegram_chat_id,
            chat_type,
            username=username,
            title=title,
            language_code=language_code,
        )

    async def get(self, telegram_chat_id: int) -> Chat | None:
        return await self.chat.get_by_tg_chat_id(telegram_chat_id)

    async def get_or_raise(self, telegram_chat_id: int) -> Chat:
        if not (chat := await self.get(telegram_chat_id)):
            raise ChatNotFoundError(f"在数据库中找不到 Chat: {telegram_chat_id}")
        return chat

    async def ensure(
        self,
        telegram_chat_id: int,
        chat_type: ChatType,
        *,
        username: str | None = None,
        title: str | None = None,
        language_code: str | None = None,
    ) -> Chat:
        if not (chat := await self.get(telegram_chat_id)):
            return await self.add(
                telegram_chat_id,
                chat_type,
                username=username,
                title=title,
                language_code=language_code,
            )
        return chat

    async def get_lang(self, telegram_chat_id: int) -> str | None:
        if chat := await self.get(telegram_chat_id):
            return chat.language_code
        return None

    async def trans_is_disable(self, telegram_chat_id: int) -> bool:
        if chat := await self.get(telegram_chat_id):
            return chat.disable
        return True
