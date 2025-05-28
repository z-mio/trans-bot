import emoji
import unicodedata
import re

from collections import Counter
from pyrogram import Client
from pyrogram.types import Message
from translator import Detecter


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
    """
    使用emoji库检查文本是否只包含emoji

    Args:
        text (str): 要检查的文本

    Returns:
        bool: 如果文本只包含emoji，返回True；否则返回False
    """

    text = text.strip()
    if not text:
        return False

    # 移除所有可能的emoji
    text_without_emoji = emoji.replace_emoji(text, "")
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


def is_only_mentions(text):
    """
    判断文本是否只包含@用户名

    Args:
        text (str): 要检查的文本

    Returns:
        bool: 如果文本只包含@用户名，返回 True；否则返回 False
    """
    text = text.strip()
    if not text:
        return False

    pattern = re.compile(r"^(@[a-zA-Z0-9_]{1,32})(\s+@[a-zA-Z0-9_]{5,32})*$")

    return bool(pattern.match(text))
