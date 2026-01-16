# pykrx-openapi

KRX(한국거래소) OpenAPI를 위한 Python 래퍼

## 주요 기능

- KRX OpenAPI 지원
- 자동 데이터 타입 변환 (문자열을 int/float/datetime으로)
- 속도 제한 (기본값: , 설정 가능)

## 설치

```bash
pip install pykrx-openapi
```

또는 uv 사용:

```bash
uv pip install pykrx-openapi
```

## 빠른 시작

```python
from pykrx_openapi import KRXOpenAPI

# API 키로 초기화
client = KRXOpenAPI(api_key="your-api-key")

# 또는 환경 변수 사용: KRX_OPENAPI_KEY
import os
os.environ["KRX_OPENAPI_KEY"] = "your-api-key"
client = KRXOpenAPI()

# KOSPI 일별 거래 데이터 조회
data = client.get_kospi_daily_trade(bas_dd="20260101")
print(data)
```

## API 목록

### 지수 (idx) - 5개 엔드포인트
- `get_krx_daily_trade()` - KRX 시리즈 일별시세정보
- `get_kospi_daily_trade()` - KOSPI 시리즈 일별시세정보
- `get_kosdaq_daily_trade()` - KOSDAQ 시리즈 일별시세정보
- `get_bond_index_daily_trade()` - 채권지수 시세정보
- `get_derivative_index_daily_trade()` - 파생상품지수 시세정보

### 주식 (sto) - 8개 엔드포인트
- `get_stock_daily_trade()` - 유가증권 일별매매정보
- `get_kosdaq_stock_daily_trade()` - 코스닥 일별매매정보
- `get_konex_daily_trade()` - 코넥스 일별매매정보
- `get_stock_warrant_daily_trade()` - 신주인수권증권 일별매매정보
- `get_short_covering_daily_trade()` - 신주인수권증서 일별매매정보
- `get_stock_base_info()` - 유가증권 종목기본정보
- `get_kosdaq_stock_base_info()` - 코스닥 종목기본정보
- `get_konex_base_info()` - 코넥스 종목기본정보

### ETP (etp) - 3개 엔드포인트
- `get_etf_daily_trade()` - ETF 일별매매정보
- `get_etn_daily_trade()` - ETN 일별매매정보
- `get_elw_daily_trade()` - ELW 일별매매정보

### 채권 (bon) - 3개 엔드포인트
- `get_kts_bond_daily_trade()` - 국채전문유통시장 일별매매정보
- `get_bond_daily_trade()` - 일반채권시장 일별매매정보
- `get_small_bond_daily_trade()` - 소액채권시장 일별매매정보

### 파생상품 (drv) - 6개 엔드포인트
- `get_futures_daily_trade()` - 선물 일별매매정보 (주식선물外)
- `get_kospi_stock_futures_daily_trade()` - 주식선물(유가) 일별매매정보
- `get_kosdaq_stock_futures_daily_trade()` - 주식선물(코스닥) 일별매매정보
- `get_options_daily_trade()` - 옵션 일별매매정보 (주식옵션外)
- `get_kospi_stock_options_daily_trade()` - 주식옵션(유가) 일별매매정보
- `get_kosdaq_stock_options_daily_trade()` - 주식옵션(코스닥) 일별매매정보

### 일반시장 (gen) - 3개 엔드포인트
- `get_oil_daily_trade()` - 석유시장 일별매매정보
- `get_gold_daily_trade()` - 금시장 일별매매정보
- `get_emissions_daily_trade()` - 배출권 시장 일별매매정보

### ESG (esg) - 3개 엔드포인트
- `get_sri_bond_info()` - 사회책임투자채권 정보
- `get_esg_etp_info()` - ESG 증권상품
- `get_esg_index_info()` - ESG 지수

## 설정

```python
client = KRXOpenAPI(
    api_key="your-key",      # API 키 (또는 KRX_OPENAPI_KEY 환경 변수 사용)
    rate_limit=10,            # 기간당 최대 요청 수 (기본값: 10)
    per_seconds=1,            # 시간 기간(초) (기본값: 1)
    timeout=30,               # 요청 타임아웃(초) (기본값: 30)
    debug=False               # 디버그 로깅 활성화 (기본값: False)
)
```

## 에러 처리

```python
from pykrx_openapi import (
    KRXOpenAPI,
    KRXAuthenticationError,
    KRXInvalidDateError,
    KRXNetworkError
)

try:
    client = KRXOpenAPI()
    data = client.get_kospi_daily_trade("20240101")
except KRXAuthenticationError:
    print("유효하지 않은 API 키입니다")
except KRXInvalidDateError:
    print("날짜는 YYYYMMDD 형식이어야 합니다")
except KRXNetworkError as e:
    print(f"네트워크 오류: {e}")
```

## 개발

```bash
# 저장소 클론
git clone https://github.com/raccoonyy/pykrx-openapi.git
cd pykrx-openapi

# uv로 의존성 설치
uv sync --dev

# 테스트 실행
uv run pytest

# 커버리지와 함께 테스트 실행
uv run pytest --cov

# 린터 실행
uv run ruff check src/ tests/
```

## 라이선스

MIT 라이선스 - 자세한 내용은 LICENSE 파일을 참조하세요

## 기여

기여를 환영합니다! Pull Request를 자유롭게 제출해 주세요.
