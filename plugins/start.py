from pyrogram import Client, filters
from pyrogram.types import Message

from utils.filters import add_chat


@Client.on_message(filters.command(["start", "help"]) & add_chat)
async def start(_: Client, msg: Message) -> None:
    await msg.reply_text("呀哈喽!")
