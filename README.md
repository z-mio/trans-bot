# Telegram Translate Bot

Telegram 翻译Bot, 可添加到群组中, 自动翻译其他语言消息为本地语言  
Telegram Translation Bot, can be added to groups, automatically translating other languages into local languages.

## 环境变量

| 名称                | 默认值           | 描述                            |
|-------------------|---------------|-------------------------------|
| `TRANS_PROVIDER`  | `google`      | 翻译服务提供商,可选: `google`,`openai` |
| `TRANS_MODEL`     | `gpt-4o-mini` | openai使用的模型                   |
| `OPENAI_API_KEY`  |               | openai API_KEY                |
| `OPENAI_BASE_URL` |               | openai API_URL                |

## 运行

```bash
uv sync
uv run bot.py
```

## 指令

群聊中发送

- `/enable` - 启用自动翻译
- `/disable` - 禁用自动翻译