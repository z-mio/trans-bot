import asyncio

from pyrogram import Client
from pyrogram.types import BotCommand

from core.config import bs
from db.engine import close_db
from db.init import init_db
from i18n import SUPPORTED_LANGS, t_
from log import logger, setup_logging

setup_logging(debug=bs.debug)

COMMANDS = {
    "start": t_("开始"),
    "help": t_("帮助"),
    "enable": t_("启用群内翻译"),
    "disable": t_("禁用群内翻译"),
}


class Bot(Client):
    def __init__(self) -> None:
        super().__init__(
            bs.bot_session_name,
            api_id=bs.api_id,
            api_hash=bs.api_hash,
            bot_token=bs.bot_token,
            plugins={"root": "plugins"},
            proxy=bs.bot_proxy,
            workdir=bs.bot_workdir,
        )

    async def start(self, *, use_qr: bool = False, except_ids: list[int] | None = None) -> Client:
        await init_db()
        await super().start(use_qr=use_qr, except_ids=except_ids)
        logger.info("Bot开始运行...")
        if not bs.debug:
            await self.set_menu()
        return self

    async def stop(self, block: bool = True, clear_handlers: bool = True) -> Client:
        await super().stop(block=block, clear_handlers=clear_handlers)
        await close_db()
        return self

    async def set_menu(self) -> None:
        """按语言设置命令菜单 (Bot API 支持多语言命令)."""
        for lang in SUPPORTED_LANGS:
            commands = [BotCommand(command=k, description=v[lang]) for k, v in COMMANDS.items()]
            await self.set_bot_commands(commands, language_code=lang)
            logger.debug(f"{lang} 菜单已设置: {commands}")
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    bot = Bot()
    bot.run()
