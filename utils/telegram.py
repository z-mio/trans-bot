"""消息字段窄化助手.

kurigram 把 Message.chat / Message.from_user 等字段标为 Optional,
而多数业务路径上这些字段必存在(如 filters.group 保证消息必有所属会话).
这里集中收敛 Optional, 避免各处重复守卫.
"""

from pyrogram.types import Message


def chat_id(msg: Message) -> int:
    """消息所属会话 ID; 消息缺少 chat 上下文时抛出 ValueError."""
    chat = msg.chat
    if chat is None or chat.id is None:
        raise ValueError("消息缺少 chat 上下文")
    return chat.id
