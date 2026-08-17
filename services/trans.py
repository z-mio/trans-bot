from core.config import bs
from translator import OpenAITranslator
from utils.singleton import singleton


@singleton
class Trans:
    def __init__(self) -> None:
        # 翻译器无状态, 构造一次复用 (pydantic-ai Agent)
        self._translator = OpenAITranslator(model=bs.trans_model)

    async def translate(self, text: str, to_lang: str) -> str:
        return await self._translator.translate(text, to_lang)
