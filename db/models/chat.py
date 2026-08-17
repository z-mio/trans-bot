from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, String, false, func
from sqlalchemy.orm import Mapped, mapped_column

from core.config import bs
from db.base import Base


class ChatType(enum.Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"

    @classmethod
    def from_pyrogram(cls, chat_type: Any) -> ChatType:
        """从 pyrogram 的 ChatType 映射到本项目枚举, 未知类型回退为 GROUP"""
        return cls[chat_type.name] if chat_type.name in cls.__members__ else cls.GROUP


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[ChatType] = mapped_column(Enum(ChatType), nullable=False)
    language_code: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=bs.default_lang,
        server_default=bs.default_lang,
    )
    disable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
