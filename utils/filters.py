from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.filters import Filter
from pyrogram.types import Message

from core.config import bs
from db import get_session
from db.models import ChatType as DbChatType
from log import logger
from services import ChatService
from utils.telegram import chat_id
from utils.util import is_emoji_only, is_only_mentions, is_only_url, is_symbols_only


async def _is_admin(flt: Filter, _: Client, msg: Message) -> bool:
    user = msg.from_user
    if user is None:
        return False
    return user.id in bs.admins


is_admin = filters.create(_is_admin)


async def _add_chat(flt: Filter, _: Client, msg: Message) -> bool:
    chat = msg.chat
    if chat is None or chat.type != ChatType.PRIVATE:
        return True
    user = msg.from_user
    if user is None:
        return True
    async with get_session() as session:
        await ChatService(session).ensure(
            chat_id(msg),
            DbChatType.from_pyrogram(chat.type),
            username=chat.username,
            title=chat.title,
            language_code=user.language_code,
        )
    return True


add_chat = filters.create(_add_chat)


async def _is_group_admin(flt: Filter, cli: Client, msg: Message) -> bool:
    user = msg.from_user
    if user is None:
        return False
    try:
        u = await cli.get_chat_member(chat_id(msg), user.id)
    except Exception:
        return False
    status = u.status
    return status == ChatMemberStatus.OWNER or status == ChatMemberStatus.ADMINISTRATOR


is_group_admin = filters.create(_is_group_admin)


async def _is_enable_trans(flt: Filter, _: Client, msg: Message) -> bool:
    async with get_session() as session:
        return not await ChatService(session).trans_is_disable(chat_id(msg))


is_enable_trans = filters.create(_is_enable_trans)


async def _trans_filter(flt: Filter, _: Client, msg: Message) -> bool:
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
