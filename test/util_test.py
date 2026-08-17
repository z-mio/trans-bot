"""to_iso639_1 语言码归一化测试."""

from utils.util import to_iso639_1


def test_normalize_bcp47() -> None:
    assert to_iso639_1("zh-hans") == "zh"
    assert to_iso639_1("zh-Hant") == "zh"
    assert to_iso639_1("zh-Hans") == "zh"
    assert to_iso639_1("en-US") == "en"
    assert to_iso639_1("ru_RU") == "ru"


def test_normalize_two_letter() -> None:
    assert to_iso639_1("ja") == "ja"
    assert to_iso639_1("en") == "en"
    assert to_iso639_1("ZH") == "zh"


def test_normalize_whitespace() -> None:
    assert to_iso639_1("  zh-Hans  ") == "zh"
    assert to_iso639_1(" en ") == "en"


def test_empty_inputs() -> None:
    assert to_iso639_1(None) is None
    assert to_iso639_1("") is None
    assert to_iso639_1(" ") is None
