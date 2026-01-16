"""KRX OpenAPI 클라이언트 테스트."""


import pytest
import requests
import requests_mock

from pykrx_openapi.client import KRXOpenAPI
from pykrx_openapi.exceptions import (
    KRXAPIError,
    KRXAuthenticationError,
    KRXInvalidDateError,
    KRXNetworkError,
    KRXRateLimitError,
    KRXServerError,
)


class TestKRXOpenAPIInitialization:
    """클라이언트 초기화 테스트."""

    def test_init_with_api_key_parameter(self):
        """파라미터로 API 키를 전달하여 초기화하는 테스트."""
        client = KRXOpenAPI(api_key="test-key")
        assert client.api_key == "test-key"

    def test_init_with_environment_variable(self, monkeypatch):
        """환경 변수에서 API 키를 가져와 초기화하는 테스트."""
        monkeypatch.setenv("KRX_OPENAPI_KEY", "env-key")
        client = KRXOpenAPI()
        assert client.api_key == "env-key"

    def test_init_without_api_key_raises_error(self, monkeypatch):
        """API 키 없이 초기화하면 ValueError가 발생하는지 테스트."""
        monkeypatch.delenv("KRX_OPENAPI_KEY", raising=False)
        with pytest.raises(ValueError, match="API key required"):
            KRXOpenAPI()

    def test_init_sets_default_values(self):
        """초기화 시 기본값이 올바르게 설정되는지 테스트."""
        client = KRXOpenAPI(api_key="test-key")
        assert client.timeout == 30
        assert client.session is not None
        assert client.rate_limiter is not None
        assert client.logger is not None

    def test_init_with_custom_rate_limit(self):
        """사용자 정의 요청 속도 제한으로 초기화하는 테스트."""
        client = KRXOpenAPI(api_key="test-key", rate_limit=5, per_seconds=2)
        assert client.rate_limiter.max_calls == 5
        assert client.rate_limiter.period == 2

    def test_init_with_custom_timeout(self):
        """사용자 정의 타임아웃으로 초기화하는 테스트."""
        client = KRXOpenAPI(api_key="test-key", timeout=60)
        assert client.timeout == 60

    def test_init_with_debug_mode(self):
        """디버그 모드로 초기화하는 테스트."""
        client = KRXOpenAPI(api_key="test-key", debug=True)
        import logging
        assert client.logger.level == logging.DEBUG


class TestMakeRequest:
    """_make_request 메서드 테스트."""

    @pytest.fixture
    def client(self):
        """테스트용 클라이언트 인스턴스 생성."""
        return KRXOpenAPI(api_key="test-key")

    @pytest.fixture
    def mock_response(self):
        """표준 모의 응답."""
        return {
            "OutBlock_1": [
                {
                    "BAS_DD": "20240101",
                    "IDX_NM": "KOSPI",
                    "CLSPRC_IDX": "2655.50",
                }
            ]
        }

    def test_make_request_success(self, client, mock_response):
        """API 요청 성공 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                json=mock_response,
            )

            result = client._make_request("idx", "kospi_dd_trd", "20240101")

            assert "OutBlock_1" in result
            assert len(result["OutBlock_1"]) == 1
            assert result["OutBlock_1"][0]["IDX_NM"] == "KOSPI"

    def test_make_request_invalid_date_format(self, client):
        """잘못된 날짜 형식에서 오류가 발생하는지 테스트."""
        with pytest.raises(KRXInvalidDateError, match="Invalid date format"):
            client._make_request("idx", "kospi_dd_trd", "2024-01-01")

        with pytest.raises(KRXInvalidDateError):
            client._make_request("idx", "kospi_dd_trd", "20241")

        with pytest.raises(KRXInvalidDateError):
            client._make_request("idx", "kospi_dd_trd", "invalid")

    def test_make_request_401_raises_authentication_error(self, client):
        """401 상태 코드에서 인증 오류가 발생하는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                status_code=401,
            )

            with pytest.raises(KRXAuthenticationError, match="Invalid API key"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_429_raises_rate_limit_error(self, client):
        """429 상태 코드에서 요청 제한 오류가 발생하는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                status_code=429,
            )

            with pytest.raises(KRXRateLimitError, match="Rate limit exceeded"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_500_raises_server_error(self, client):
        """5xx 상태 코드에서 서버 오류가 발생하는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                status_code=500,
                text="Internal Server Error",
            )

            with pytest.raises(KRXServerError, match="Server error"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_connection_error(self, client):
        """연결 오류가 처리되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                exc=requests.exceptions.ConnectionError("Connection failed"),
            )

            with pytest.raises(KRXNetworkError, match="Connection error"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_timeout_error(self, client):
        """타임아웃 오류가 처리되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                exc=requests.exceptions.Timeout("Request timed out"),
            )

            with pytest.raises(KRXNetworkError, match="Request timeout"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_invalid_json(self, client):
        """잘못된 JSON 응답이 처리되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                text="Not valid JSON",
            )

            with pytest.raises(KRXAPIError, match="Invalid JSON response"):
                client._make_request("idx", "kospi_dd_trd", "20240101")

    def test_make_request_missing_outblock(self, client):
        """OutBlock_1이 없는 응답에서 빈 리스트가 반환되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                json={"some_other_key": "value"},
            )

            result = client._make_request("idx", "kospi_dd_trd", "20240101")
            assert result == {"OutBlock_1": []}

    def test_make_request_converts_data_types(self, client):
        """응답 데이터 타입이 변환되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                json={
                    "OutBlock_1": [
                        {
                            "BAS_DD": "20240101",
                            "CLSPRC_IDX": "2655.50",
                            "ACC_TRDVOL": "123456",
                        }
                    ]
                },
            )

            result = client._make_request("idx", "kospi_dd_trd", "20240101")

            from datetime import datetime
            record = result["OutBlock_1"][0]
            assert isinstance(record["BAS_DD"], datetime)
            assert isinstance(record["CLSPRC_IDX"], float)
            assert isinstance(record["ACC_TRDVOL"], int)

    def test_make_request_url_construction(self, client):
        """URL과 파라미터가 올바르게 구성되는지 테스트."""
        with requests_mock.Mocker() as m:
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd",
                json={"OutBlock_1": []},
            )

            client._make_request("sto", "stk_bydd_trd", "20240115")

            # 요청이 전송되었는지 확인
            assert m.called
            assert m.call_count == 1

            # URL과 파라미터 확인
            request = m.request_history[0]
            assert request.url.startswith("https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd")
            assert "basDd" in request.url

            # AUTH_KEY가 파라미터(URL 쿼리 문자열)에 있는지 확인
            assert "AUTH_KEY=test-key" in request.url
