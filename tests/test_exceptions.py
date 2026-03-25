"""カスタム例外クラスのテスト。"""
from ioc_collector.exceptions import (
    IoCCollectorError,
    GeminiAPIError,
    GeminiAuthError,
    GeminiRateLimitError,
    GeminiResponseError,
)


def test_exception_hierarchy():
    assert issubclass(GeminiAPIError, IoCCollectorError)
    assert issubclass(GeminiAuthError, GeminiAPIError)
    assert issubclass(GeminiRateLimitError, GeminiAPIError)
    assert issubclass(GeminiResponseError, GeminiAPIError)


def test_rate_limit_error_has_retry_after():
    err = GeminiRateLimitError("rate limited", retry_after=30)
    assert err.retry_after == 30
    assert "rate limited" in str(err)


def test_rate_limit_error_default_retry_after():
    err = GeminiRateLimitError("rate limited")
    assert err.retry_after == 60  # デフォルト60秒
