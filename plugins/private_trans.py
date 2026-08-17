from pyrogram import Client, filters
from pyrogram.types import Message

from methods import Trans
from translator import Detecter
from utils.filters import trans_filter


@Client.on_message(filters.private & (filters.text | filters.caption) & ~filters.via_bot & trans_filter)
async def trans(_: Client, msg: Message) -> Message | None:
    user = msg.from_user
    text = msg.text
    if user is None or not text:
        return None
    to_lang = user.language_code
    from_lang = (await Detecter().detect(text)).lower()
    if from_lang == to_lang:
        return None
    translated = await Trans().translate(text, "en")
    return await msg.reply(translated)


# TODO: 私聊翻译功能
