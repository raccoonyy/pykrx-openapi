"""pykrx-openapi 로깅 설정."""

import logging
import sys


def setup_logger(name: str = "pykrx_openapi", level: int = logging.INFO) -> logging.Logger:
    """
    로거 인스턴스를 설정하고 반환합니다.

    Args:
        name: 로거 이름
        level: 로깅 레벨 (기본값: INFO)

    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 로거에 핸들러가 없는 경우에만 추가
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
