# Trans Bot

Telegram 群组自动翻译机器人:添加到群组后,自动把外语消息翻译成群组语言。

## 功能

- 群组自动翻译: 检测消息语言, 按回复/非回复场景智能决定目标语言
- `/enable <语言代码>` 启用翻译并设置群组语言 (如 `/enable en`、`/enable zh`)
- `/disable` 禁用翻译
- 翻译目标语言代码使用两位 ISO 639-1 格式 (`zh` / `en` / `ja` / `ru`)
- 翻译提供商: openai (pydantic-ai)

## 环境变量

| 名称              | 默认值                                 | 描述                       |
|-------------------|----------------------------------------|----------------------------|
| `API_ID`          |                                        | Telegram API ID (必填)     |
| `API_HASH`        |                                        | Telegram API Hash (必填)   |
| `BOT_TOKEN`       |                                        | Bot Token (必填)           |
| `BOT_PROXY`       |                                        | 代理 URL                   |
| `DEBUG`           | `false`                                | 调试模式                   |
| `DATABASE_URL`    | `sqlite+aiosqlite:///data/database.db` | 数据库连接 URL             |
| `TRANS_MODEL`     | `gpt-5-mini`                           | openai 使用的模型          |
| `OPENAI_API_KEY`  |                                        | openai API Key (必填)      |
| `OPENAI_BASE_URL` |                                        | openai API Base URL (必填) |

## 运行

```bash
uv sync
uv run bot.py
```

## 指令

群聊中由群管理员发送:

- `/enable <语言代码>` - 启用自动翻译并设置群组语言
- `/disable` - 禁用自动翻译

命令菜单按用户语言显示(zh / en / ja / ru)。

## 开发

```bash
uv sync                       # 安装依赖 (含 dev)
uv run pytest                 # 运行测试 (语言决策穷举 / 检测 / 数据库访问)
uv run ruff check .           # 代码检查
uv run mypy                   # 类型检查
uv run python i18n.py         # 重新生成 i18n 翻译 (需要 OPENAI_API_KEY)
```

## 部署 (Docker)

```bash
docker compose up -d
```

`start.sh` 提供容器管理:启动 / 停止 / 重启 / 查看日志。
