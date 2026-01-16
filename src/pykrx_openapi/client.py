"""KRX OpenAPI 클라이언트 구현."""

import json
import logging
import os
import re

import requests

from .constants import BASE_URL
from .converters import convert_response
from .exceptions import (
    KRXAPIError,
    KRXAuthenticationError,
    KRXInvalidDateError,
    KRXNetworkError,
    KRXRateLimitError,
    KRXServerError,
)
from .logger import setup_logger
from .rate_limiter import RateLimiter


class KRXOpenAPI:
    """
    KRX OpenAPI 메인 클라이언트.

    31개의 KRX OpenAPI 엔드포인트에 대한 접근을 제공하며,
    요청 속도 제한, 데이터 타입 변환, 로깅 기능이 내장되어 있습니다.
    """

    def __init__(
        self,
        api_key: str | None = None,
        rate_limit: int = 10,
        per_seconds: int = 1,
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        KRX OpenAPI 클라이언트를 초기화합니다.

        Args:
            api_key: 인증용 API 키. 제공하지 않으면 KRX_OPENAPI_KEY 환경 변수에서 읽음.
            rate_limit: 기간당 최대 요청 수 (기본값: 10)
            per_seconds: 요청 속도 제한 기간 (초) (기본값: 1)
            timeout: 요청 타임아웃 (초) (기본값: 30)
            debug: 디버그 로깅 활성화 (기본값: False)

        Raises:
            ValueError: API 키가 제공되지 않고 환경 변수에서도 찾을 수 없는 경우
        """
        # 파라미터 또는 환경 변수에서 API 키 가져오기
        self.api_key = api_key or os.getenv("KRX_OPENAPI_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required: pass as parameter or set KRX_OPENAPI_KEY environment variable"
            )

        # 연결 풀링을 위한 HTTP 세션 초기화
        self.session = requests.Session()
        self.timeout = timeout

        # 요청 속도 제한기 초기화
        self.rate_limiter = RateLimiter(max_calls=rate_limit, period=per_seconds)

        # 로거 설정
        log_level = logging.DEBUG if debug else logging.INFO
        self.logger = setup_logger(level=log_level)

        self.logger.info(
            f"Initialized KRX OpenAPI client (rate_limit={rate_limit}/{per_seconds}s)"
        )

    def _make_request(self, category: str, endpoint: str, bas_dd: str) -> dict:
        """
        KRX API에 HTTP 요청을 보냅니다.

        Args:
            category: API 카테고리 (예: "idx", "sto")
            endpoint: 엔드포인트 경로 (예: "kospi_dd_trd")
            bas_dd: 기준일자 (YYYYMMDD 형식)

        Returns:
            "OutBlock_1"에 레코드 리스트를 포함한 딕셔너리

        Raises:
            KRXInvalidDateError: 날짜 형식이 유효하지 않은 경우
            KRXAuthenticationError: API 키가 유효하지 않은 경우
            KRXRateLimitError: 서버 요청 제한 초과 시
            KRXServerError: 서버가 5xx 오류를 반환한 경우
            KRXNetworkError: 네트워크/연결 오류 발생 시
            KRXAPIError: 기타 API 오류
        """
        # 날짜 형식 검증
        if not re.match(r"^\d{8}$", bas_dd):
            raise KRXInvalidDateError(
                f"Invalid date format: {bas_dd}. Expected YYYYMMDD (e.g., 20240101)"
            )

        # 요청 속도 제한 적용
        self.rate_limiter.wait_if_needed()

        # URL 및 파라미터 구성
        url = f"{BASE_URL}/{category}/{endpoint}"
        params = {
            "AUTH_KEY": self.api_key,
            "basDd": bas_dd,
        }

        self.logger.debug(f"Request: {category}/{endpoint} - basDd={bas_dd}")

        try:
            # HTTP 요청 실행
            response = self.session.get(url, params=params, timeout=self.timeout)

            # HTTP 오류 처리
            if response.status_code == 401:
                raise KRXAuthenticationError("Invalid API key (401 Unauthorized)")
            elif response.status_code == 429:
                raise KRXRateLimitError("Rate limit exceeded (429 Too Many Requests)")
            elif 500 <= response.status_code < 600:
                raise KRXServerError(
                    f"Server error: {response.status_code} - {response.text[:200]}"
                )

            response.raise_for_status()

            # JSON 응답 파싱
            data = response.json()

            # 응답에서 OutBlock_1 확인
            if "OutBlock_1" not in data:
                self.logger.warning(
                    f"Unexpected response structure (no OutBlock_1): {list(data.keys())}"
                )
                return {"OutBlock_1": []}

            # 데이터 타입 변환
            data["OutBlock_1"] = convert_response(data["OutBlock_1"])

            self.logger.debug(f"Response: {len(data['OutBlock_1'])} records")

            return data

        except json.JSONDecodeError as e:
            raise KRXAPIError(f"Invalid JSON response: {e}") from e
        except requests.exceptions.Timeout as e:
            raise KRXNetworkError(f"Request timeout after {self.timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            raise KRXNetworkError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise KRXNetworkError(f"Network error: {e}") from e

    # ==================== 지수 엔드포인트 (idx) ====================

    def get_krx_daily_trade(self, bas_dd: str) -> dict:
        """
        KRX 시리즈 일별시세정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format, e.g., "20240101")

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("idx", "krx_dd_trd", bas_dd)

    def get_kospi_daily_trade(self, bas_dd: str) -> dict:
        """
        KOSPI 시리즈 일별시세정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("idx", "kospi_dd_trd", bas_dd)

    def get_kosdaq_daily_trade(self, bas_dd: str) -> dict:
        """
        KOSDAQ 시리즈 일별시세정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("idx", "kosdaq_dd_trd", bas_dd)

    def get_bond_index_daily_trade(self, bas_dd: str) -> dict:
        """
        채권지수 시세정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("idx", "bon_dd_trd", bas_dd)

    def get_derivative_index_daily_trade(self, bas_dd: str) -> dict:
        """
        파생상품지수 시세정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("idx", "drvprod_dd_trd", bas_dd)

    # ==================== 주식 엔드포인트 (sto) ====================

    def get_stock_daily_trade(self, bas_dd: str) -> dict:
        """
        유가증권 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "stk_bydd_trd", bas_dd)

    def get_kosdaq_stock_daily_trade(self, bas_dd: str) -> dict:
        """
        코스닥 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "ksq_bydd_trd", bas_dd)

    def get_konex_daily_trade(self, bas_dd: str) -> dict:
        """
        코넥스 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "knx_bydd_trd", bas_dd)

    def get_stock_warrant_daily_trade(self, bas_dd: str) -> dict:
        """
        신주인수권증권 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "sw_bydd_trd", bas_dd)

    def get_short_covering_daily_trade(self, bas_dd: str) -> dict:
        """
        신주인수권증서 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "sr_bydd_trd", bas_dd)

    def get_stock_base_info(self, bas_dd: str) -> dict:
        """
        유가증권 종목기본정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "stk_isu_base_info", bas_dd)

    def get_kosdaq_stock_base_info(self, bas_dd: str) -> dict:
        """
        코스닥 종목기본정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "ksq_isu_base_info", bas_dd)

    def get_konex_base_info(self, bas_dd: str) -> dict:
        """
        코넥스 종목기본정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("sto", "knx_isu_base_info", bas_dd)

    # ==================== ETP 엔드포인트 (etp) ====================

    def get_etf_daily_trade(self, bas_dd: str) -> dict:
        """
        ETF 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("etp", "etf_bydd_trd", bas_dd)

    def get_etn_daily_trade(self, bas_dd: str) -> dict:
        """
        ETN 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("etp", "etn_bydd_trd", bas_dd)

    def get_elw_daily_trade(self, bas_dd: str) -> dict:
        """
        ELW 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("etp", "elw_bydd_trd", bas_dd)

    # ==================== 채권 엔드포인트 (bon) ====================

    def get_kts_bond_daily_trade(self, bas_dd: str) -> dict:
        """
        국채전문유통시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("bon", "kts_bydd_trd", bas_dd)

    def get_bond_daily_trade(self, bas_dd: str) -> dict:
        """
        일반채권시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("bon", "bnd_bydd_trd", bas_dd)

    def get_small_bond_daily_trade(self, bas_dd: str) -> dict:
        """
        소액채권시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("bon", "smb_bydd_trd", bas_dd)

    # ==================== 파생상품 엔드포인트 (drv) ====================

    def get_futures_daily_trade(self, bas_dd: str) -> dict:
        """
        선물 일별매매정보 (주식선물外).

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "fut_bydd_trd", bas_dd)

    def get_kospi_stock_futures_daily_trade(self, bas_dd: str) -> dict:
        """
        주식선물(유가) 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "eqsfu_stk_bydd_trd", bas_dd)

    def get_kosdaq_stock_futures_daily_trade(self, bas_dd: str) -> dict:
        """
        주식선물(코스닥) 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "eqkfu_ksq_bydd_trd", bas_dd)

    def get_options_daily_trade(self, bas_dd: str) -> dict:
        """
        옵션 일별매매정보 (주식옵션外).

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "opt_bydd_trd", bas_dd)

    def get_kospi_stock_options_daily_trade(self, bas_dd: str) -> dict:
        """
        주식옵션(유가) 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "eqsop_bydd_trd", bas_dd)

    def get_kosdaq_stock_options_daily_trade(self, bas_dd: str) -> dict:
        """
        주식옵션(코스닥) 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("drv", "eqkop_bydd_trd", bas_dd)

    # ==================== 일반시장 엔드포인트 (gen) ====================

    def get_oil_daily_trade(self, bas_dd: str) -> dict:
        """
        석유시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("gen", "oil_bydd_trd", bas_dd)

    def get_gold_daily_trade(self, bas_dd: str) -> dict:
        """
        금시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("gen", "gold_bydd_trd", bas_dd)

    def get_emissions_daily_trade(self, bas_dd: str) -> dict:
        """
        배출권 시장 일별매매정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("gen", "ets_bydd_trd", bas_dd)

    # ==================== ESG 엔드포인트 (esg) ====================

    def get_sri_bond_info(self, bas_dd: str) -> dict:
        """
        사회책임투자채권 정보.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("esg", "sri_bond_info", bas_dd)

    def get_esg_etp_info(self, bas_dd: str) -> dict:
        """
        ESG 증권상품.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("esg", "esg_etp_info", bas_dd)

    def get_esg_index_info(self, bas_dd: str) -> dict:
        """
        ESG 지수.

        Args:
            bas_dd: 기준일자 (YYYYMMDD format)

        Returns:
            dict: OutBlock_1에 레코드 리스트를 포함한 응답
        """
        return self._make_request("esg", "esg_index_info", bas_dd)
