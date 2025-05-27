from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.tables.base import Base

Path("data").mkdir(parents=True, exist_ok=True)
async_engine = create_async_engine(
    "sqlite+aiosqlite:///data/database.db",
    connect_args={"check_same_thread": False},
    echo=False,
)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)