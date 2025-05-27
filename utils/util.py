from collections import Counter

from pyrogram import Client
from pyrogram.types import Message

from translator import Detecter


async def get_group_lang(cli: Client, msg: Message) -> str | None:
    msgs = await cli.get_messages(msg.chat.id, range(msg.id - 100, msg.id - 1))
    text_list = [m.text for m in msgs if m.text]
    lang_list = await Detecter().detect(text_list[:30])
    if not lang_list:
        return None
    counter = Counter(lang_list).most_common(1)
    group_lang = counter[0][0]
    return group_lang
