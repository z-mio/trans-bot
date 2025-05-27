from config.config import cfg
from database.db import async_session
from database.tables.chat import Chat
from utils.db import DB
from utils.singleton import singleton


@singleton
class ChatMgmt:
    def __init__(self):
        self.db = DB(async_session)

    async def add_chat(self, chat: Chat):
        if await self.get_chat(chat.id):
            return False
        return await self.db.add(chat)

    async def get_chat(self, chat_id: int):
        return await self.db.get_one(Chat, Chat.id == chat_id)

    async def get_lang(self, chat_id: int):
        if chat := await self.get_chat(chat_id):
            return chat.language_code or cfg.default_lang
        return False

    async def set_lang(self, chat_id: int, lang: str):
        if await self.get_chat(chat_id):
            await self.db.update(Chat, Chat.id == chat_id, language_code=lang)
            return True
        return False

    async def trans_is_disable(self, chat_id: int):
        if chat := await self.get_chat(chat_id):
            return chat.disable
        return True

    async def set_trans_status(self, chat_id: int, status: bool):
        if await self.get_chat(chat_id):
            await self.db.update(Chat, Chat.id == chat_id, disable=not status)
            return True
        return False
