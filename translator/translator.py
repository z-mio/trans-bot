"""
翻译器
"""

import os
from typing import cast

from googletrans import Translator as Gt
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from tenacity import retry, stop_after_attempt, wait_fixed

from translator.prompts import TRANSLATE_PROMPT

from .base import BaseTranslator
from .error import TranslationError


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
    """OpenAI 兼容接口翻译 (基于 pydantic-ai, Agent 内置重试)"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-4.1-nano",
        prompt: str = TRANSLATE_PROMPT,
    ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 未配置")
        self.model = model
        self.prompt = prompt
        self._agent = Agent(
            model=OpenAIChatModel(
                model,
                provider=OpenAIProvider(api_key=api_key, base_url=base_url or os.getenv("OPENAI_BASE_URL")),
            ),
            output_type=str,
            system_prompt=prompt,
            model_settings=ModelSettings(temperature=0),
            retries=3,
        )

    async def translate(self, text: str, target_lang: str) -> str:
        """
        gpt翻译
        """
        try:
            response = await self._agent.run(f"Translate the text to {target_lang}:\n{text}")
        except Exception as e:
            raise TranslationError(f"OpenAI翻译错误: {e}") from e
        else:
            content = response.output
            if not content:
                raise TranslationError("OpenAI 返回了空内容")
            return content
