"""migrate_chat_to_chats

Revision ID: a1b2c3d4e5f7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-17 11:30:01.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 新旧表 type 列均存枚举 name (如 "SUPERGROUP"), 名称一致可直接直通;
# 旧表来自 pyrogram 枚举, 多了 BOT 等本项目不存在的类型, 回退为 GROUP
_LEGACY_TYPE_NAMES = {"PRIVATE", "GROUP", "SUPERGROUP", "CHANNEL"}


def _map_type(value: str | None) -> str:
    if value in _LEGACY_TYPE_NAMES:
        return value
    return "GROUP"


def upgrade() -> None:
    """将旧表 chat 的数据搬运到新表 chats 后删除旧表."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 新数据库没有旧表, 无需搬运数据.
    if not inspector.has_table("chat") or not inspector.has_table("chats"):
        return

    metadata = sa.MetaData()
    legacy_chat = sa.Table("chat", metadata, autoload_with=bind)
    chats = sa.Table("chats", metadata, autoload_with=bind)

    rows = bind.execute(sa.select(legacy_chat)).mappings().all()
    for row in rows:
        bind.execute(
            chats.insert().values(
                telegram_chat_id=row["id"],
                username=row.get("username"),
                title=row.get("title"),
                type=_map_type(row.get("type")),
                language_code=row.get("language_code") or "zh-hans",
                disable=bool(row.get("disable")),
                created_at=row.get("created_at") or sa.func.now(),
            )
        )

    op.drop_table("chat")


def downgrade() -> None:
    """回滚: 重建旧表 chat 并搬回数据."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 新数据库没有新表, 无需回滚.
    if not inspector.has_table("chats"):
        return
    if inspector.has_table("chat"):
        op.drop_table("chat")

    op.create_table(
        "chat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String()),
        sa.Column("title", sa.String()),
        sa.Column("type", sa.String(10)),
        sa.Column("language_code", sa.String()),
        sa.Column("disable", sa.Boolean()),
        sa.Column("created_at", sa.DateTime()),
    )

    metadata = sa.MetaData()
    legacy_chat = sa.Table("chat", metadata, autoload_with=bind)
    chats = sa.Table("chats", metadata, autoload_with=bind)

    rows = bind.execute(sa.select(chats)).mappings().all()
    for row in rows:
        bind.execute(
            legacy_chat.insert().values(
                id=row["telegram_chat_id"],
                username=row.get("username"),
                title=row.get("title"),
                type=_map_type(row.get("type")),
                language_code=row.get("language_code"),
                disable=row.get("disable"),
                created_at=row.get("created_at"),
            )
        )
