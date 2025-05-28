from collections import Counter

import unicodedata
from pyrogram import Client
from pyrogram.types import Message

from translator import Detecter
import re


async def get_group_lang(cli: Client, msg: Message) -> str | None:
    msgs = await cli.get_messages(msg.chat.id, range(msg.id - 100, msg.id - 1))
    text_list = [m.text for m in msgs if m.text]
    lang_list = await Detecter().detect(text_list[:30])
    if not lang_list:
        return None
    counter = Counter(lang_list).most_common(1)
    group_lang = counter[0][0]
    return group_lang


def is_emoji_only(text: str) -> bool:
    """检查文本是否只包含emoji"""

    # emoji正则表达式模式
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # 表情符号
        "\U0001f300-\U0001f5ff"  # 符号和象形文字
        "\U0001f680-\U0001f6ff"  # 交通和地图符号
        "\U0001f700-\U0001f77f"  # 闹钟符号
        "\U0001f780-\U0001f7ff"  # 几何符号
        "\U0001f800-\U0001f8ff"  # 箭头符号
        "\U0001f900-\U0001f9ff"  # 补充符号和象形文字
        "\U0001fa00-\U0001fa6f"  # 棋盘符号
        "\U0001fa70-\U0001faff"  # 符号和象形文字扩展
        "\U00002702-\U000027b0"  # 杂项符号
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )

    # 移除所有emoji
    text_without_emoji = emoji_pattern.sub(r"", text)
    # 移除空白字符
    text_without_emoji = text_without_emoji.strip()

    # 如果移除emoji后文本为空，则原文本只包含emoji
    return len(text_without_emoji) == 0


# URL匹配的正则表达式
# 匹配常见的URL格式，包括http, https, ftp协议以及没有协议的www开头域名
URL_PATTERN = re.compile(
    r"(https?://|www\.|ftp://)"  # 协议或www开头
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # 域名
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IP地址
    r"\[?[A-F0-9]*:[A-F0-9:]+]?)"  # IPv6
    r"(?::\d+)?"  # 可选的端口
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)  # 路径和查询字符串


def is_only_url(text):
    text = text.strip()
    return bool(URL_PATTERN.fullmatch(text))


def is_symbols_only(text):
    """
    判断文本是否只包含符号（标点符号、特殊字符等）

    Args:
        text (str): 要检查的文本

    Returns:
        bool: 如果文本只包含符号，返回 True；否则返回 False
    """
    text = text.strip()
    if not text:
        return False

    # 使用 Unicode 类别判断
    for char in text:
        category = unicodedata.category(char)
        # 如果不是标点符号 (P)、符号 (S) 或空白 (Z)，则不是纯符号
        if not (
            category.startswith("P")
            or category.startswith("S")
            or category.startswith("Z")
        ):
            return False

    return True
