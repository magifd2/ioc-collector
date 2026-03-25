"""カスタム例外クラス。"""


class IoCCollectorError(Exception):
    """ioc-collector のベース例外。"""


class GeminiAPIError(IoCCollectorError):
    """Gemini API 呼び出しに関する例外。"""


class GeminiAuthError(GeminiAPIError):
    """認証・認可エラー（401/403、ADC 未設定等）。"""


class GeminiRateLimitError(GeminiAPIError):
    """レート制限エラー（HTTP 429）。

    Attributes:
        retry_after: 推奨待機秒数。
    """

    def __init__(self, message: str, retry_after: int = 60) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class GeminiResponseError(GeminiAPIError):
    """Gemini のレスポンスが不正で解析できなかった場合の例外。"""
