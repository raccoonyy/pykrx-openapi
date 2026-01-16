"""KRX OpenAPI 상수 및 엔드포인트 매핑."""

BASE_URL = "https://data-dbg.krx.co.kr/svc/apis"

# API 카테고리
CATEGORY_IDX = "idx"
CATEGORY_STO = "sto"
CATEGORY_ETP = "etp"
CATEGORY_BON = "bon"
CATEGORY_DRV = "drv"
CATEGORY_GEN = "gen"
CATEGORY_ESG = "esg"

# 엔드포인트 매핑: endpoint_path -> (category, korean_name)
ENDPOINTS = {
    # 지수 (idx) - 5개 엔드포인트
    "krx_dd_trd": ("idx", "KRX 시리즈 일별시세정보"),
    "kospi_dd_trd": ("idx", "KOSPI 시리즈 일별시세정보"),
    "kosdaq_dd_trd": ("idx", "KOSDAQ 시리즈 일별시세정보"),
    "bon_dd_trd": ("idx", "채권지수 시세정보"),
    "drvprod_dd_trd": ("idx", "파생상품지수 시세정보"),

    # 주식 (sto) - 8개 엔드포인트
    "stk_bydd_trd": ("sto", "유가증권 일별매매정보"),
    "ksq_bydd_trd": ("sto", "코스닥 일별매매정보"),
    "knx_bydd_trd": ("sto", "코넥스 일별매매정보"),
    "sw_bydd_trd": ("sto", "신주인수권증권 일별매매정보"),
    "sr_bydd_trd": ("sto", "신주인수권증서 일별매매정보"),
    "stk_isu_base_info": ("sto", "유가증권 종목기본정보"),
    "ksq_isu_base_info": ("sto", "코스닥 종목기본정보"),
    "knx_isu_base_info": ("sto", "코넥스 종목기본정보"),

    # ETP (etp) - 3개 엔드포인트
    "etf_bydd_trd": ("etp", "ETF 일별매매정보"),
    "etn_bydd_trd": ("etp", "ETN 일별매매정보"),
    "elw_bydd_trd": ("etp", "ELW 일별매매정보"),

    # 채권 (bon) - 3개 엔드포인트
    "kts_bydd_trd": ("bon", "국채전문유통시장 일별매매정보"),
    "bnd_bydd_trd": ("bon", "일반채권시장 일별매매정보"),
    "smb_bydd_trd": ("bon", "소액채권시장 일별매매정보"),

    # 파생상품 (drv) - 6개 엔드포인트
    "fut_bydd_trd": ("drv", "선물 일별매매정보 (주식선물外)"),
    "eqsfu_stk_bydd_trd": ("drv", "주식선물(유가) 일별매매정보"),
    "eqkfu_ksq_bydd_trd": ("drv", "주식선물(코스닥) 일별매매정보"),
    "opt_bydd_trd": ("drv", "옵션 일별매매정보 (주식옵션外)"),
    "eqsop_bydd_trd": ("drv", "주식옵션(유가) 일별매매정보"),
    "eqkop_bydd_trd": ("drv", "주식옵션(코스닥) 일별매매정보"),

    # 일반시장 (gen) - 3개 엔드포인트
    "oil_bydd_trd": ("gen", "석유시장 일별매매정보"),
    "gold_bydd_trd": ("gen", "금시장 일별매매정보"),
    "ets_bydd_trd": ("gen", "배출권 시장 일별매매정보"),

    # ESG (esg) - 3개 엔드포인트
    "sri_bond_info": ("esg", "사회책임투자채권 정보"),
    "esg_etp_info": ("esg", "ESG 증권상품"),
    "esg_index_info": ("esg", "ESG 지수"),
}

# 숫자 변환을 위한 필드명 패턴
NUMERIC_FIELD_PATTERNS = {
    "price": ["PRC", "PRICE", "CLSPRC", "OPNPRC", "HGPRC", "LWPRC", "PARVAL", "SETL_PRC"],
    "volume": ["VOL", "TRDVOL", "QTY", "OPNINT_QTY", "SHRS"],
    "amount": ["AMT", "VAL", "TRDVAL", "CAP"],
    "index": ["IDX", "INDEX"],
    "rate": ["RT", "RATE", "FLUC_RT"],
    "ratio": ["RATIO"],
    "count": ["CNT", "COUNT"],
}

# 날짜 변환을 위한 필드명 패턴
DATE_FIELD_PATTERNS = ["DD", "DT", "DATE"]
