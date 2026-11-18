from pathlib import Path
from typing import Any

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    api_id: str
    api_hash: str
    # 兼容历史键名: 旧 .env 用 PROXY / BOT_DEBUG, 新键名 BOT_PROXY / DEBUG 优先
    bot_proxy: str | None = Field(default=None, validation_alias=AliasChoices("BOT_PROXY", "PROXY"))
    bot_workdir: Path = Field(default=Path("sessions"))
    debug: bool = Field(default=False, validation_alias=AliasChoices("DEBUG", "BOT_DEBUG"))

    trans_model: str = Field(default="gpt-5-mini")
    """OpenAI 翻译模型"""
    openai_api_key: str = Field(min_length=1)
    """OpenAI API Key (必填)"""
    openai_base_url: str = Field(min_length=1)
    """OpenAI API Base URL (必填)"""

    database_url: str = Field(default="sqlite+aiosqlite:///data/database.db")
    """数据库连接 URL"""

    def model_post_init(self, __context: Any) -> None:
        """模型初始化后的操作"""
        self.bot_workdir.mkdir(parents=True, exist_ok=True)

        url = make_url(self.database_url)
        if url.get_backend_name() == "sqlite" and url.database:
            Path(url.database).parent.mkdir(parents=True, exist_ok=True)

    @field_validator("bot_proxy", mode="before")
    @classmethod
    def empty_proxy_to_none(cls, v: str | None = None) -> str | None:
        return v or None

    @property
    def bot_session_name(self) -> str:
        return f"bot_{self.bot_token.split(':')[0]}"


bs = BotSettings()  # type: ignore
