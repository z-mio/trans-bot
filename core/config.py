import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url


class WatchdogSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
        env_prefix="WD_",
    )
    is_running: bool = Field(default=False)
    """运行中"""
    restart_count: int = Field(default=0)
    """重启次数"""
    disconnect_count: int = Field(default=0)
    """断开连接次数"""
    max_disconnect_count: int = Field(default=3)
    """最大断开连接次数, 超过后重启"""
    remove_session_after_restart: int = Field(default=3)
    """重启失败几次后删除会话文件"""
    max_restart_count: int = Field(default=6)
    """意外断开连接时，最大重启次数"""
    exit_flag: bool = Field(default=False)
    """退出标志"""

    def update_bot_restart_count(self) -> None:
        self.restart_count += 1
        os.environ["WD_RESTART_COUNT"] = str(self.restart_count)

    def reset_bot_restart_count(self) -> None:
        self.restart_count = 0
        os.environ["WD_RESTART_COUNT"] = "0"

    def update_bot_disconnect_count(self) -> None:
        self.disconnect_count += 1
        os.environ["WD_DISCONNECT_COUNT"] = str(self.disconnect_count)

    def reset_bot_disconnect_count(self) -> None:
        self.disconnect_count = 0
        os.environ["WD_DISCONNECT_COUNT"] = "0"


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    api_id: str
    api_hash: str
    bot_proxy: dict | None = Field(default=None)
    bot_workdir: Path = Field(default=Path("sessions"))
    debug: bool = Field(default=False)
    admins: list[int] = Field(default_factory=list)
    """管理员用户 ID 列表, 逗号分隔"""

    # trans-bot 特有配置
    default_lang: str = Field(default="zh-hans")
    """默认语言"""
    trans_provider: str = Field(default="google")
    """翻译提供商: google / openai"""
    trans_model: str = Field(default="gpt-4o-mini")
    """OpenAI 翻译模型"""

    database_url: str = Field(default="sqlite+aiosqlite:///data/database.db")
    """数据库连接 URL"""

    def model_post_init(self, __context: Any) -> None:
        """模型初始化后的操作"""
        self.bot_workdir.mkdir(parents=True, exist_ok=True)

        url = make_url(self.database_url)
        if url.get_backend_name() == "sqlite" and url.database:
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)

    @field_validator("admins", mode="before")
    @classmethod
    def admins_config(cls, v: Any) -> list[int]:
        if v is None or v == "":
            return []
        if isinstance(v, str):
            v = [x.strip() for x in v.split(",") if x.strip()]
        return [int(x) for x in v]

    @field_validator("bot_proxy", mode="before")
    @classmethod
    def proxy_config(cls, v: str | None = None) -> dict | None:
        url = urlparse(v) if v else None
        if not url:
            return None
        return {
            "scheme": url.scheme,
            "hostname": url.hostname,
            "port": url.port,
            "username": url.username,
            "password": url.password,
        }

    @property
    def bot_session_name(self) -> str:
        return f"bot_{self.bot_token.split(':')[0]}"


bs = BotSettings()  # type: ignore
ws = WatchdogSettings()
