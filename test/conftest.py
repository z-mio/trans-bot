"""pytest 全局配置: 测试环境变量 + 隔离数据库."""

import os
import tempfile

# BotSettings 的必填字段没有默认值, CI 环境不存在 .env,
# 测试不依赖真实凭据, 提供占位值即可 (测试不会发起真实请求).
os.environ.setdefault("BOT_TOKEN", "123456:test-token")
os.environ.setdefault("API_ID", "12345")
os.environ.setdefault("API_HASH", "test-hash")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://test.local/v1")

# 数据库指向临时目录, 避免污染真实 data/database.db
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mkdtemp(prefix='trans-bot-test-')}/test.db"
