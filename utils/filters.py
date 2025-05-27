from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import cfg
from database.tables import Chat
from methods.chat_mgmt import ChatMgmt
from pyrogram.enums import ChatType, ChatMemberStatus

from translator import Detecter


async def _is_admin(_, __, msg: Message):
    return msg.from_user.id in cfg.admins


is_admin = filters.create(_is_admin)


async def _add_chat(_, __, msg: Message):
    if msg.chat.type != ChatType.PRIVATE:
        return True
    language_code = msg.from_user.language_code
    await ChatMgmt().add_chat(
        Chat(
            id=msg.chat.id,
            username=msg.chat.username,
            title=msg.chat.title,
            type=msg.chat.type,
            language_code=language_code,
        )
    )
    return True


add_chat = filters.create(_add_chat)


async def _is_group_admin(_, cli: Client, msg: Message):
    try:
        u = await cli.get_chat_member(msg.chat.id, msg.from_user.id)
    except Exception:
        return False
    if u and u.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return True
    return False


is_group_admin = filters.create(_is_group_admin)


async def _is_enable_trans(_, __, msg: Message):
    return not await ChatMgmt().trans_is_disable(msg.chat.id)


is_enable_trans = filters.create(_is_enable_trans)
