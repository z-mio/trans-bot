from lingua import LanguageDetectorBuilder
from tenacity import retry, stop_after_attempt, wait_fixed

from translator.error import DetectionError
from utils.singleton import singleton


@singleton
class Detecter:
    """语言检测器 (单例: 检测器构建需加载全部语言模型, 成本高)."""

    def __init__(self) -> None:
        self._detector = LanguageDetectorBuilder.from_all_languages().build()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1.5))
    async def detect(self, text: str) -> str:
        try:
            result = self._detector.detect_language_of(text)
        except Exception as e:
            raise DetectionError(f"检测语言错误: {e}") from e
        if result is None:
            raise DetectionError(f"无法检测语言: {text!r}")
        return result.iso_code_639_1.name.lower()
