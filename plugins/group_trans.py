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
    return await msg.reply(_t(f"已启用翻译, 群组语言设置为: `{lang}`"))


@Client.on_message(filters.group & filters.command("disable") & is_group_admin)
async def disable_group_trans(_, msg: Message):
    cm = ChatMgmt()
    _t = t_[await cm.get_lang(msg.chat.id)]

    if await cm.set_trans_status(msg.chat.id, False):
        return await msg.reply(_t("已禁用翻译"))
    return await msg.reply(_t("翻译未启用"))


@Client.on_message(
    filters.group & filters.text & ~filters.via_bot & trans_filter & is_enable_trans
)
async def trans_group(_, msg: Message):
    if not msg.text:
        return None

    cm = ChatMgmt()
    group_lang = await cm.get_lang(msg.chat.id)
    user_lang = msg.from_user.language_code
    logger.debug(f"群组语言: {group_lang}, 用户语言: {user_lang}, 消息: {msg.text}")
    # 如果用户语言与群组语言相同，可能不需要翻译
    if user_lang == group_lang:
        # 但是我们仍然需要检测消息语言，以处理用户使用非母语的情况
        if msg.text.isdigit():
            return None
        msg_lang = (await Detecter().detect(msg.text)).lower()
        # 如果用户使用的是群组语言（即他的母语），则不翻译
        if msg_lang == group_lang:
            return None

        # 如果用户使用的不是群组语言，虽然他的母语是群组语言，我们仍然需要翻译
        target_lang = group_lang
    else:
        # 用户母语与群组语言不同的情况
        msg_lang = (await Detecter().detect(msg.text)).lower()

        # 如果是回复消息，需要特殊处理
        if msg.reply_to_message and msg.reply_to_message.text:
            reply_lang = (await Detecter().detect(msg.reply_to_message.text)).lower()

            # 情况1：用户使用母语回复外语消息 → 翻译为外语
            if msg_lang == user_lang and reply_lang != user_lang:
                target_lang = reply_lang
            # 情况2：用户使用外语回复母语消息 → 翻译为母语
            elif msg_lang != user_lang and reply_lang == user_lang:
                target_lang = user_lang
            # 其他情况：翻译为群组语言
            else:
                target_lang = group_lang
        else:
            # 非回复消息：翻译为群组语言
            target_lang = group_lang

    # 如果目标语言与消息语言相同，不翻译
    if target_lang == msg_lang:
        return None

    # 执行翻译
    logger.debug(f"翻译目标语言: {target_lang}")
    translated = await Trans().translate(
        msg.text, LangMap.get_reverse(target_lang)
    )
    return await msg.reply(translated)
