import abc


class BaseTranslator(abc.ABC):
    @abc.abstractmethod
    async def translate(self, text: str, target_lang: str) -> str:
        """
        翻译
        :param text: 要翻译的文本
        :param target_lang: 目标语言
        :return: 翻译结果
        """
        raise NotImplementedError()
