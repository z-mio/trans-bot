import asyncio
from typing import Any

from pyrogram import Client
from pyrogram.handlers import ConnectHandler, DisconnectHandler
from pyrogram.types import BotCommand

from core.config import bs, ws
from core.watchdog import on_connect, on_disconnect
from db.engine import close_db
from db.init import init_db
from i18n import ISO639_MAP, t_
from log import logger, setup_logging
from utils.event_loop import setup_optimized_event_loop

setup_logging(debug=bs.debug)

setup_optimized_event_loop()
loop = asyncio.new_event_loop()

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
            loop=loop,
            workdir=bs.bot_workdir,
        )

    async def start(self, **kwargs: Any) -> None:
        self.init_watchdog()
        await init_db()
        await super().start()
        logger.info("Bot开始运行...")
        if not bs.debug:
            await self.set_menu()

    async def stop(self, *args: Any, **kwargs: Any) -> None:
        ws.exit_flag = True
        await super().stop(*args, **kwargs)
        await close_db()

    def init_watchdog(self) -> None:
        self.add_handler(ConnectHandler(on_connect))
        self.add_handler(DisconnectHandler(on_disconnect))

    async def set_menu(self) -> None:
        """按语言设置命令菜单 (Bot API 支持多语言命令)."""
        for iso639, bcp47 in ISO639_MAP.items():
            commands = [BotCommand(command=k, description=v[bcp47]) for k, v in COMMANDS.items()]
            await self.set_bot_commands(commands, language_code=iso639)
            logger.debug(f"{iso639} 菜单已设置: {commands}")
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    bot = Bot()
    bot.run()
