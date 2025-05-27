from easy_ai18n import EasyAI18n
from easy_ai18n.translator import OpenAIBulkTranslator


i18n = EasyAI18n(i18n_function_names=["t_", "_", "_t"])
t_ = i18n.i18n()

if __name__ == "__main__":
    i18n.build(
        ["en", "ja", "zh-hant", "ru"],
        translator=OpenAIBulkTranslator(),
        include=["plugins"],
    )
    