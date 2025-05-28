from pyrogram import Client, filters
from pyrogram.types import Message

from methods import Trans
from translator import Detecter


@Client.on_message(filters.private & filters.text)
async def trans(_, msg: Message):
    to_lang = msg.from_user.language_code
    text = msg.text
    from_lang = (await Detecter().detect(text)).lower()
    if from_lang == to_lang:
        return None
    translated = await Trans().translate(text, "en")
    return await msg.reply(translated)
