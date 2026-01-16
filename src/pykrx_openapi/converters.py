"""KRX API 응답 데이터 타입 변환 유틸리티."""

from datetime import datetime

from .constants import DATE_FIELD_PATTERNS, NUMERIC_FIELD_PATTERNS


def convert_field(field_name: str, value: str) -> int | float | datetime | str | None:
    """
    필드명 패턴에 따라 필드 값을 변환합니다.

    Args:
        field_name: 필드명 (예: "BAS_DD", "CLSPRC_IDX")
        value: 변환할 문자열 값

    Returns:
        변환된 값 (int, float, datetime, str, 또는 None)
    """
    # 빈 값 또는 null 값 처리
    if not value or value.strip() == "" or value.strip() == "-":
        return None

    # 날짜 변환 시도
    for pattern in DATE_FIELD_PATTERNS:
        if field_name.endswith(pattern):
            try:
                # YYYYMMDD 형식 시도
                if len(value) == 8 and value.isdigit():
                    return datetime.strptime(value, "%Y%m%d")
            except ValueError:
                pass
            break

    # 필드 패턴에 따라 숫자 변환 시도
    field_upper = field_name.upper()

    # 각 숫자 패턴 확인
    for pattern_type, patterns in NUMERIC_FIELD_PATTERNS.items():
        for pattern in patterns:
            if pattern in field_upper:
                # 쉼표 및 기타 서식 제거
                clean_value = value.replace(",", "").strip()

                try:
                    # 거래량과 개수 필드는 정수여야 함
                    if pattern_type in ("volume", "count"):
                        return int(float(clean_value))
                    else:
                        # 가격, 금액, 지수, 비율 필드는 실수여야 함
                        return float(clean_value)
                except (ValueError, AttributeError):
                    # 변환 실패 시 원본 문자열 반환
                    return value

    # 변환이 적용되지 않은 경우 원본 문자열 반환
    return value


def convert_record(record: dict) -> dict:
    """
    단일 레코드의 모든 필드를 변환합니다.

    Args:
        record: 필드명-값 쌍을 포함한 딕셔너리

    Returns:
        변환된 값을 포함한 딕셔너리
    """
    return {
        field: convert_field(field, value)
        for field, value in record.items()
    }


def convert_response(data: list[dict]) -> list[dict]:
    """
    응답의 모든 레코드를 변환합니다.

    Args:
        data: 레코드 딕셔너리 리스트

    Returns:
        변환된 값을 포함한 딕셔너리 리스트
    """
    return [convert_record(record) for record in data]
