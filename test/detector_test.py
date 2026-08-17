"""语言检测器测试."""

import pytest

from translator import Detector
from translator.error import DetectionError


async def test_detect_chinese() -> None:
    assert await Detector().detect("这是一段中文测试文本") == "zh"


async def test_detect_english() -> None:
    assert await Detector().detect("this is an english sentence") == "en"


async def test_detect_japanese() -> None:
    assert await Detector().detect("これは日本語の文章です") == "ja"


async def test_detect_empty_raises() -> None:
    with pytest.raises(DetectionError):
        await Detector().detect("")


async def test_detect_singleton() -> None:
    assert Detector() is Detector()
