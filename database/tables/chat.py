from datetime import datetime
from typing import Optional

from sqlalchemy import INTEGER
from sqlalchemy.orm import Mapped, mapped_column
from pyrogram.enums import ChatType

from config.config import cfg
from database.tables.base import Base


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)  # chat_id
    username: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    type: Mapped[ChatType]
    language_code: Mapped[str] = mapped_column(default=cfg.default_lang)
    disable: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
