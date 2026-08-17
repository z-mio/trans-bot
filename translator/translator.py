"""
翻译器
"""

import os
from typing import cast

from googletrans import Translator as Gt
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from translator.prompts import TRANSLATE_PROMPT

from .base import BaseTranslator
from .error import TranslationError
from .utils import build_messages


class GoogleTranslator(BaseTranslator):
    """谷歌翻译"""

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
    async def translate(self, text: str, target_lang: str) -> str:
        try:
            result = await Gt().translate(text, dest=target_lang)
        except Exception as e:
            raise TranslationError(f"谷歌翻译错误: {e}") from e
        else:
            return cast(str, result.text)


class OpenAITranslator(BaseTranslator):
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4.1-nano",
        prompt: str = TRANSLATE_PROMPT,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未配置")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model
        self.prompt = prompt
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
    async def translate(self, text: str, target_lang: str) -> str:
        """
        gpt翻译
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=build_messages(self.prompt, f"Translate the text to {target_lang}:\n{text}"),
                temperature=0,
            )
        except Exception as e:
            raise TranslationError(f"OpenAI翻译错误: {e}") from e
        else:
            content = response.choices[0].message.content
            if content is None:
                raise TranslationError("OpenAI 返回了空内容")
            return content
