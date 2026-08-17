"""pytest 全局配置: 测试环境变量 + 隔离数据库."""

import os
import tempfile

# BotSettings 的 OPENAI_API_KEY / OPENAI_BASE_URL 是必填字段,
# 测试环境不依赖真实凭据, 提供占位值即可 (测试不会发起真实请求).
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_BASE_URL", "https://test.local/v1")

# 数据库指向临时目录, 避免污染真实 data/database.db
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tempfile.mkdtemp(prefix='trans-bot-test-')}/test.db"
