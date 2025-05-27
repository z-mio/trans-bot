from typing import overload

from googletrans import Translator as Gt
from langcodes import standardize_tag
from tenacity import retry, stop_after_attempt, wait_fixed

from translator.error import DetectionError


class Detecter:
    def __init__(self):
        self.gt = Gt()

    @overload
    async def detect(self, text: str) -> str: ...
    @overload
    async def detect(self, text: list[str]) -> list[str]: ...

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
    async def detect(self, text: str | list[str]) -> str | list[str]:
        try:
            result = await self.gt.detect(text)
        except Exception as e:
            raise DetectionError(f"检测语言错误: {e}")
        else:
            if isinstance(result, list):
                return [LangMap.get(r.lang) for r in result]
            else:
                return LangMap.get(result.lang)


class LangMap:
    map = {
        "zh-CN": "zh-Hans",
        "zh-TW": "zh-Hant",
        "zh-HK": "zh-Hant",
        "zh-MO": "zh-Hant",
        "zh-SG": "zh-Hans",
    }

    @staticmethod
    def get(lang: str) -> str:
        return LangMap.map.get(standardize_tag(lang), lang)

    @staticmethod
    def get_reverse(lang: str) -> str:
        for k, v in LangMap.map.items():
            if v.lower() == lang.lower():
                return k
        return lang
