from pyrogram import filters, Client
from pyrogram.types import Message
from config.config import cfg
from database.tables import Chat
from log import logger
from methods.chat_mgmt import ChatMgmt
from pyrogram.enums import ChatType, ChatMemberStatus

from utils.util import is_emoji_only, is_only_url, is_symbols_only, is_only_mentions


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


async def _trans_filter(_, __, msg: Message):
    t = msg.text or msg.caption
    logger.debug(f"检测消息: {t}")
    if not t:
        return False
    if t.startswith("/"):
        logger.debug("是命令, 跳过")
        return False
    if t.isdigit():
        logger.debug("是数字, 跳过")
        return False
    if is_emoji_only(t):
        logger.debug("是emoji, 跳过")
        return False
    if is_only_url(t):
        logger.debug("是链接, 跳过")
        return False
    if is_symbols_only(t):
        logger.debug("是符号, 跳过")
        return False
    if is_only_mentions(t):
        logger.debug("是@, 跳过")
        return False
    return True

trans_filter = filters.create(_trans_filter)
