from config.config import cfg
from translator import GoogleTranslator, OpenAITranslator
from utils.singleton import singleton


@singleton
class Trans:
    def __init__(self):
        self.provider = cfg.trans_provider

    async def translate(self, text: str, to_lang: str):
        return await self.selsct_trans_provider().translate(text, to_lang)

    def selsct_trans_provider(self):
        match self.provider:
            case "google":
                return GoogleTranslator()
            case "openai":
                return OpenAITranslator(model=cfg.trans_model)
            case _:
                raise ValueError(
                    f"环境变量 <TRANS_PROVIDER> 配置错误: {self.provider} 不支持的翻译平台"
                )
            