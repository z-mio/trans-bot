from core.config import bs
from translator import BaseTranslator, GoogleTranslator, OpenAITranslator
from utils.singleton import singleton


@singleton
class Trans:
    def __init__(self) -> None:
        self.provider = bs.trans_provider
        # 翻译器无状态, 构造一次复用 (OpenAITranslator 会创建 pydantic-ai Agent)
        self._translator = self._build_translator()

    async def translate(self, text: str, to_lang: str) -> str:
        return await self._translator.translate(text, to_lang)

    def _build_translator(self) -> BaseTranslator:
        match self.provider:
            case "google":
                return GoogleTranslator()
            case "openai":
                return OpenAITranslator(model=bs.trans_model)
            case _:
                raise ValueError(f"环境变量 <TRANS_PROVIDER> 配置错误: {self.provider} 不支持的翻译平台")
