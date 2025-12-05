from typing import overload

from googletrans import Translator as Gt
from langcodes import standardize_tag
from lingua import LanguageDetectorBuilder
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
    async def detect(self, text: str) -> str:
        try:
            # result = await self.gt.detect(text)
            detector = LanguageDetectorBuilder.from_all_languages().build()
            result = detector.detect_language_of(text)
        except Exception as e:
            raise DetectionError(f"检测语言错误: {e}")
        else:
            return LangMap.get(result.iso_code_639_1.name.lower())


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
