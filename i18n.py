from dotenv import load_dotenv
from easy_ai18n import EasyAI18n
from easy_ai18n.translators import LLMBulkTranslator

load_dotenv()

i18n = EasyAI18n("zh", func_names=["t_", "_", "_t"])
t_ = i18n.i18n()

if __name__ == "__main__":
    i18n.build(
        ["en", "ja", "ru"],
        translator=LLMBulkTranslator(),
        include=["plugins"],
    )
