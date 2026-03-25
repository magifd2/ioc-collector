"""Gemini クライアントのエラーハンドリングテスト。"""
import pytest
from unittest.mock import MagicMock, patch, call

from google.genai import errors as genai_errors

from ioc_collector.exceptions import GeminiAuthError, GeminiRateLimitError, GeminiResponseError
from ioc_collector.gemini_client import GeminiResearchClient


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """全テストで time.sleep をスキップする。"""
    monkeypatch.setattr("ioc_collector.gemini_client.time.sleep", lambda _: None)


def _make_client_error(code: int) -> genai_errors.ClientError:
    return genai_errors.ClientError(code, {"error": {"code": code, "message": "error", "status": "ERROR"}})


def _make_server_error(code: int) -> genai_errors.ServerError:
    return genai_errors.ServerError(code, {"error": {"code": code, "message": "error", "status": "ERROR"}})


@pytest.fixture
def client():
    with patch("ioc_collector.gemini_client.genai.Client"):
        return GeminiResearchClient(project="test", location="us-central1")


class TestResearchErrorHandling:
    def test_401_raises_gemini_auth_error(self, client):
        client._client.models.generate_content.side_effect = _make_client_error(401)
        with pytest.raises(GeminiAuthError):
            client.research("test")

    def test_403_raises_gemini_auth_error(self, client):
        client._client.models.generate_content.side_effect = _make_client_error(403)
        with pytest.raises(GeminiAuthError):
            client.research("test")

    def test_429_raises_gemini_rate_limit_error(self, client):
        client._client.models.generate_content.side_effect = _make_client_error(429)
        with pytest.raises(GeminiRateLimitError):
            client.research("test", max_retries=1)

    def test_429_retries_before_raising(self, client):
        """429 は指数バックオフでリトライし、上限に達したら GeminiRateLimitError を送出する。"""
        client._client.models.generate_content.side_effect = _make_client_error(429)
        with pytest.raises(GeminiRateLimitError):
            client.research("test", max_retries=3)
        assert client._client.models.generate_content.call_count == 3

    def test_429_succeeds_after_retry(self, client):
        """429 の後にリトライで成功する場合は正常値を返す。"""
        mock_response = MagicMock(text="success")
        client._client.models.generate_content.side_effect = [
            _make_client_error(429),
            mock_response,
        ]
        result = client.research("test", max_retries=3)
        assert result == "success"
        assert client._client.models.generate_content.call_count == 2

    def test_500_raises_generic_api_error(self, client):
        from ioc_collector.exceptions import GeminiAPIError
        client._client.models.generate_content.side_effect = _make_server_error(500)
        with pytest.raises(GeminiAPIError):
            client.research("test", max_retries=1)


class TestExtractReportErrorHandling:
    def test_invalid_json_raises_gemini_response_error(self, client):
        client._client.models.generate_content.return_value = MagicMock(text="not valid json {{")
        with pytest.raises(GeminiResponseError, match="extract"):
            client.extract_report("research text")

    def test_429_retries_in_extract_report(self, client):
        import json
        from ioc_collector.models import IncidentReport
        valid_json = json.dumps({
            "title": "T", "summary": "S", "affected_scope": "A",
            "timeline": [], "countermeasures": [], "iocs": [], "references": [],
        })
        client._client.models.generate_content.side_effect = [
            _make_client_error(429),
            MagicMock(text=valid_json),
        ]
        report = client.extract_report("research text", max_retries=3)
        assert isinstance(report, IncidentReport)
        assert client._client.models.generate_content.call_count == 2
