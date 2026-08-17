from easy_ai18n import EasyAI18n
from easy_ai18n.translators import LLMBulkTranslator

from core.config import bs

i18n = EasyAI18n("zh", func_names=["t_"])
t_ = i18n.i18n()

# 命令菜单支持的语言 (ISO 639-1, 与 i18n 文案语言一致)
SUPPORTED_LANGS = ["zh", "en", "ja", "ru"]

if __name__ == "__main__":
    i18n.build(
        ["en", "ja", "ru"],
        translator=LLMBulkTranslator(api_key=bs.openai_api_key, base_url=bs.openai_base_url),
        include=["plugins"],
    )
