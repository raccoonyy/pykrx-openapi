"""KRX OpenAPI 커스텀 예외 클래스."""


class KRXAPIError(Exception):
    """KRX API 오류의 기본 예외 클래스."""
    pass


class KRXAuthenticationError(KRXAPIError):
    """인증 실패 (API 키 누락 또는 유효하지 않음)."""
    pass


class KRXRateLimitError(KRXAPIError):
    """서버 측 요청 제한 초과."""
    pass


class KRXInvalidDateError(KRXAPIError):
    """잘못된 날짜 형식 (YYYYMMDD 형식이어야 함)."""
    pass


class KRXNetworkError(KRXAPIError):
    """네트워크 또는 연결 오류."""
    pass


class KRXServerError(KRXAPIError):
    """서버 오류 (5xx 상태 코드)."""
    pass
