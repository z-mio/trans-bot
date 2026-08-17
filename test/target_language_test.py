"""翻译目标语言决策逻辑穷举测试.

参考实现独立于被测代码, 用原始语义描述 (用户/群组/消息语言三元关系),
穷举所有组合, 锁定当前业务行为, 防止重构回归.
"""

from itertools import product

from plugins.group_trans import _get_normal_target_language, _get_reply_target_language

# 用户/群组语言可能缺失 (None), 消息语言是检测结果, 必有值
USER_GROUP_VALS: list[str | None] = [None, "en", "zh"]
MSG_VALS: list[str] = ["en", "zh"]


def reference_normal(user_lang: str | None, group_lang: str | None, msg_lang: str) -> str | None:
    """参考实现: 用户/消息/群组三者相同则不翻译, 否则翻成群组语言."""
    if user_lang == group_lang:
        if msg_lang == group_lang:
            return None
        return group_lang
    return group_lang


def reference_reply(user_lang: str | None, group_lang: str | None, msg_lang: str, reply_lang: str) -> str | None:
    """参考实现: 回复场景的 4 分支语义."""
    if msg_lang == user_lang and reply_lang != user_lang:
        return reply_lang
    if msg_lang != user_lang and reply_lang == user_lang:
        return user_lang
    if msg_lang == user_lang == reply_lang == group_lang:
        return None
    return group_lang


def test_normal_target_language_exhaustive() -> None:
    for user, group, msg in product(USER_GROUP_VALS, USER_GROUP_VALS, MSG_VALS):
        expected = reference_normal(user, group, msg)
        actual = _get_normal_target_language(user, group, msg)
        assert actual == expected, f"normal({user}, {group}, {msg}) -> {actual}, 期望 {expected}"


def test_reply_target_language_exhaustive() -> None:
    for user, group, msg, reply in product(USER_GROUP_VALS, USER_GROUP_VALS, MSG_VALS, MSG_VALS):
        expected = reference_reply(user, group, msg, reply)
        actual = _get_reply_target_language(user, group, msg, reply)
        assert actual == expected, f"reply({user}, {group}, {msg}, {reply}) -> {actual}, 期望 {expected}"


def test_known_normal_scenarios() -> None:
    """关键业务场景抽样."""
    # 群组 en, 用户 zh, 发中文 -> 翻成 en
    assert _get_normal_target_language("zh", "en", "zh") == "en"
    # 群组 en, 用户 en, 发中文 -> 翻成 en
    assert _get_normal_target_language("en", "en", "zh") == "en"
    # 群组 en, 用户 en, 发英文 -> 不翻
    assert _get_normal_target_language("en", "en", "en") is None


def test_known_reply_scenarios() -> None:
    """回复场景抽样: 群组 en, 用户母语 zh."""
    user, group = "zh", "en"
    # 看到英文消息, 回复中文 -> 翻成英文(被回复消息语言)
    assert _get_reply_target_language(user, group, "zh", "en") == "en"
    # 看到中文消息, 回复英文 -> 翻成中文(用户母语)
    assert _get_reply_target_language(user, group, "en", "zh") == "zh"
    # 看到英文消息, 回复英文 -> 翻成群组语言 en
    assert _get_reply_target_language(user, group, "en", "en") == "en"
    # 中文群里的中文回复 -> 不翻
    assert _get_reply_target_language("zh", "zh", "zh", "zh") is None


def test_all_none_falls_back_to_group() -> None:
    """用户语言缺失时退化为翻成群组语言."""
    assert _get_normal_target_language(None, "en", "zh") == "en"
    assert _get_reply_target_language(None, "en", "zh", "en") == "en"
