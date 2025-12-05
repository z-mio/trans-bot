from langcodes import Language
from pyrogram import Client, filters
from pyrogram.types import Message

from database.tables import Chat
from log import logger
from methods.chat_mgmt import ChatMgmt
from methods import Trans
from translator import Detecter
from i18n import t_
from translator.detecter import LangMap
from utils.filters import is_group_admin, is_enable_trans, trans_filter
from utils.util import get_group_lang


@Client.on_message(filters.group & filters.command("enable") & is_group_admin)
async def enable_group_trans(cli: Client, msg: Message):
    cm = ChatMgmt()
    _t = t_[await cm.get_lang(msg.chat.id)]
    if msg.command[1:]:
        lang = msg.command[1]
        if not Language.get(lang).is_valid():
            return await msg.reply(_t(f"语言代码 `{lang}` 无效"))
    else:
        await msg.reply(_t("自动获取群组语言中..."))
        lang = await get_group_lang(cli, msg)
        if not lang:
            return await msg.reply(
                _t("自动获取群组语言失败, 请手动设置语言, `/enable <语言代码>`")
            )
    lang = lang.lower()
    chat = await cm.add_chat(
        Chat(
            id=msg.chat.id,
            username=msg.chat.username,
            title=msg.chat.title,
            type=msg.chat.type,
            language_code=lang,
        )
    )
    if not chat:
        await cm.set_trans_status(msg.chat.id, True)
        await cm.set_lang(msg.chat.id, lang)
        return await msg.reply(_t(f"已修改群组语言为: `{lang}`"))
    return await msg.reply(
        _t(
            f"已启用翻译, 群组语言设置为: `{lang}`\n如需手动设置语言, 请使用 `/enable <语言代码>`"
        )
    )


@Client.on_message(filters.group & filters.command("disable") & is_group_admin)
async def disable_group_trans(_, msg: Message):
    cm = ChatMgmt()
    _t = t_[await cm.get_lang(msg.chat.id)]

    if await cm.set_trans_status(msg.chat.id, False):
        return await msg.reply(_t("已禁用翻译"))
    return await msg.reply(_t("翻译未启用"))


@Client.on_message(
    filters.group
    & (filters.text | filters.caption)
    & ~filters.via_bot
    & trans_filter
    & is_enable_trans
)
async def trans_group(_, msg: Message):
    raw_text = msg.text or msg.caption
    if not raw_text:
        return None

    cm = ChatMgmt()
    group_lang = await cm.get_lang(msg.chat.id)
    user_lang = msg.from_user.language_code
    logger.debug(f"群组语言: {group_lang}, 用户语言: {user_lang}, 消息: {raw_text}")
    # 检测消息语言
    msg_lang = (await Detecter().detect(raw_text)).lower()

    # 确定目标翻译语言
    target_lang = await _determine_target_language(msg, user_lang, group_lang, msg_lang)
    # 如果不需要翻译，直接返回
    if not target_lang or target_lang == msg_lang:
        logger.debug(f"消息语言: {msg_lang} 与目标语言: {target_lang} 相同，不翻译")
        return None
    # 简繁不互相翻译
    if "zh" in msg_lang and "zh" in target_lang:
        logger.debug(f"消息语言: {msg_lang} 与目标语言: {target_lang} 均为中文，不翻译")
        return None

    # 执行翻译
    logger.debug(f"翻译到目标语言: {target_lang}")
    translated = await Trans().translate(raw_text, LangMap.get_reverse(target_lang))
    text = (
        f"<blockquote expandable>{translated}</blockquote>"
        if len(translated) > 60 or translated.count("\n") > 3
        else translated
    )
    if text == raw_text:
        return None
    return await msg.reply(text)


async def _determine_target_language(
    msg: Message, user_lang: str, group_lang: str, msg_lang: str
) -> str | None:
    """
    确定翻译目标语言

    Args:
        msg: 消息对象
        user_lang: 用户语言
        group_lang: 群组语言
        msg_lang: 消息语言

    Returns:
        目标语言代码，如果不需要翻译则返回 None
    """
    # 处理回复消息
    if msg.reply_to_message and msg.reply_to_message.text:
        raw_text = msg.reply_to_message.text or msg.reply_to_message.caption
        reply_lang = (await Detecter().detect(raw_text)).lower()
        return _get_reply_target_language(user_lang, group_lang, msg_lang, reply_lang)

    # 处理非回复消息
    return _get_normal_target_language(user_lang, group_lang, msg_lang)


def _get_reply_target_language(
    user_lang: str, group_lang: str, msg_lang: str, reply_lang: str
) -> str | None:
    """
    处理回复消息的目标语言逻辑
    """
    # 用户使用母语回复外语消息 → 翻译为被回复消息的语言
    if msg_lang == user_lang and reply_lang != user_lang:
        return reply_lang

    # 用户使用外语回复母语消息 → 翻译为用户母语
    if msg_lang != user_lang and reply_lang == user_lang:
        return user_lang

    # 用户使用母语回复母语消息（且都是群组语言） → 不翻译
    if msg_lang == user_lang == reply_lang == group_lang:
        return None

    # 其他情况 → 翻译为群组语言
    return group_lang


def _get_normal_target_language(
    user_lang: str, group_lang: str, msg_lang: str
) -> str | None:
    """
    处理普通消息的目标语言逻辑
    """
    # 用户语言与群组语言相同
    if user_lang == group_lang:
        # 如果消息语言也是群组语言，不翻译
        if msg_lang == group_lang:
            return None
        # 如果消息语言不是群组语言，翻译为群组语言
        return group_lang

    # 用户语言与群组语言不同，翻译为群组语言
    return group_lang
