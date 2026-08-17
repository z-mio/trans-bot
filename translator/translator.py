"""
翻译器
"""

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from core.config import bs
from translator.prompts import TRANSLATE_PROMPT

from .error import TranslationError


class OpenAITranslator:
    """OpenAI 兼容接口翻译 (基于 pydantic-ai, Agent 内置重试).

    api_key / base_url 统一从 BotSettings (OPENAI_API_KEY / OPENAI_BASE_URL) 读取.
    """

    def __init__(
        self,
        model: str = "gpt-5-mini",
        prompt: str = TRANSLATE_PROMPT,
    ) -> None:
        self.model = model
        self.prompt = prompt
        self._agent = Agent(
            model=OpenAIChatModel(
                model,
                provider=OpenAIProvider(api_key=bs.openai_api_key, base_url=bs.openai_base_url),
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
