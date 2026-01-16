"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_api_response():
    """Standard KRX API response structure."""
    return {
        "OutBlock_1": [
            {
                "BAS_DD": "20240101",
                "IDX_NM": "KOSPI",
                "CLSPRC_IDX": "2655.50",
            }
        ]
    }
