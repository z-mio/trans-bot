"""ChatService 数据库访问测试 (使用隔离的临时 SQLite)."""

from collections.abc import AsyncGenerator

import pytest

from db import get_session
from db.init import init_db
from db.models import ChatType
from services import ChatService


@pytest.fixture
async def db() -> AsyncGenerator[None]:
    await init_db()
    yield


async def test_ensure_creates_with_default_lang(db: None) -> None:
    async with get_session() as session:
        chat = await ChatService(session).ensure(111, ChatType.GROUP)
        assert chat.telegram_chat_id == 111
        assert chat.language_code == "zh"
        assert chat.disable is False


async def test_ensure_reuses_existing(db: None) -> None:
    async with get_session() as session:
        svc = ChatService(session)
        first = await svc.ensure(222, ChatType.GROUP, language_code="en")
        second = await svc.ensure(222, ChatType.GROUP, language_code="ja")
        assert first.id == second.id
        assert first.language_code == "en"  # 已存在则不覆盖


async def test_get_lang_and_disable_state(db: None) -> None:
    async with get_session() as session:
        svc = ChatService(session)
        # 不存在的 chat: 语言 None, 视为禁用
        assert await svc.get_lang(333) is None
        assert await svc.trans_is_disable(333) is True

        await svc.ensure(333, ChatType.GROUP, language_code="en")
        assert await svc.get_lang(333) == "en"
        assert await svc.trans_is_disable(333) is False


async def test_update_fields_persist(db: None) -> None:
    """读改写模式: 修改字段后在同一 session 提交."""
    async with get_session() as session:
        svc = ChatService(session)
        chat = await svc.ensure(444, ChatType.GROUP, language_code="en")
        chat.language_code = "ja"
        chat.disable = True
    # 新 session 验证持久化
    async with get_session() as session:
        svc = ChatService(session)
        persisted = await svc.get(444)
        assert persisted is not None
        assert persisted.language_code == "ja"
        assert persisted.disable is True
