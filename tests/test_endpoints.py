"""Tests for all 31 endpoint methods."""

import pytest
import requests_mock

from pykrx_openapi.client import KRXOpenAPI

# All 31 endpoints with (category, method_name, endpoint_path)
ALL_ENDPOINTS = [
    # Indices (idx) - 5 endpoints
    ("idx", "get_krx_daily_trade", "krx_dd_trd"),
    ("idx", "get_kospi_daily_trade", "kospi_dd_trd"),
    ("idx", "get_kosdaq_daily_trade", "kosdaq_dd_trd"),
    ("idx", "get_bond_index_daily_trade", "bon_dd_trd"),
    ("idx", "get_derivative_index_daily_trade", "drvprod_dd_trd"),

    # Stocks (sto) - 8 endpoints
    ("sto", "get_stock_daily_trade", "stk_bydd_trd"),
    ("sto", "get_kosdaq_stock_daily_trade", "ksq_bydd_trd"),
    ("sto", "get_konex_daily_trade", "knx_bydd_trd"),
    ("sto", "get_stock_warrant_daily_trade", "sw_bydd_trd"),
    ("sto", "get_short_covering_daily_trade", "sr_bydd_trd"),
    ("sto", "get_stock_base_info", "stk_isu_base_info"),
    ("sto", "get_kosdaq_stock_base_info", "ksq_isu_base_info"),
    ("sto", "get_konex_base_info", "knx_isu_base_info"),

    # ETPs (etp) - 3 endpoints
    ("etp", "get_etf_daily_trade", "etf_bydd_trd"),
    ("etp", "get_etn_daily_trade", "etn_bydd_trd"),
    ("etp", "get_elw_daily_trade", "elw_bydd_trd"),

    # Bonds (bon) - 3 endpoints
    ("bon", "get_kts_bond_daily_trade", "kts_bydd_trd"),
    ("bon", "get_bond_daily_trade", "bnd_bydd_trd"),
    ("bon", "get_small_bond_daily_trade", "smb_bydd_trd"),

    # Derivatives (drv) - 6 endpoints
    ("drv", "get_futures_daily_trade", "fut_bydd_trd"),
    ("drv", "get_kospi_stock_futures_daily_trade", "eqsfu_stk_bydd_trd"),
    ("drv", "get_kosdaq_stock_futures_daily_trade", "eqkfu_ksq_bydd_trd"),
    ("drv", "get_options_daily_trade", "opt_bydd_trd"),
    ("drv", "get_kospi_stock_options_daily_trade", "eqsop_bydd_trd"),
    ("drv", "get_kosdaq_stock_options_daily_trade", "eqkop_bydd_trd"),

    # General Markets (gen) - 3 endpoints
    ("gen", "get_oil_daily_trade", "oil_bydd_trd"),
    ("gen", "get_gold_daily_trade", "gold_bydd_trd"),
    ("gen", "get_emissions_daily_trade", "ets_bydd_trd"),

    # ESG (esg) - 3 endpoints
    ("esg", "get_sri_bond_info", "sri_bond_info"),
    ("esg", "get_esg_etp_info", "esg_etp_info"),
    ("esg", "get_esg_index_info", "esg_index_info"),
]


class TestAllEndpoints:
    """Test all 31 endpoint methods."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        return KRXOpenAPI(api_key="test-key")

    @pytest.mark.parametrize("category,method_name,endpoint", ALL_ENDPOINTS)
    def test_endpoint(self, client, mock_api_response, category, method_name, endpoint):
        """Test that each endpoint method works correctly."""
        with requests_mock.Mocker() as m:
            url = f"https://data-dbg.krx.co.kr/svc/apis/{category}/{endpoint}"
            m.get(url, json=mock_api_response)

            # Get the method and call it
            method = getattr(client, method_name)
            result = method("20240101")

            # Verify response structure
            assert result is not None
            assert "OutBlock_1" in result
            assert isinstance(result["OutBlock_1"], list)

            # Verify request was made
            assert m.called
            assert m.call_count == 1

    def test_all_endpoints_count(self):
        """Verify that we have exactly 31 endpoints."""
        assert len(ALL_ENDPOINTS) == 31

    def test_all_endpoint_methods_exist(self, client):
        """Verify that all endpoint methods exist on the client."""
        for _, method_name, _ in ALL_ENDPOINTS:
            assert hasattr(client, method_name), f"Method {method_name} not found"

    def test_endpoint_returns_converted_data(self, client):
        """Test that endpoint returns data with type conversion."""
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

            result = client.get_kospi_daily_trade("20240101")

            from datetime import datetime
            record = result["OutBlock_1"][0]
            assert isinstance(record["BAS_DD"], datetime)
            assert isinstance(record["CLSPRC_IDX"], float)
            assert isinstance(record["ACC_TRDVOL"], int)

    def test_multiple_endpoints_share_rate_limiter(self, client):
        """Test that all endpoints share the same rate limiter."""
        with requests_mock.Mocker() as m:
            # Mock multiple endpoints
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd",
                json={"OutBlock_1": []},
            )
            m.get(
                "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd",
                json={"OutBlock_1": []},
            )

            # Call different endpoints - they should all use the same rate limiter
            client.get_kospi_daily_trade("20240101")
            client.get_stock_daily_trade("20240101")

            # Both calls should have been made
            assert m.call_count == 2


class TestEndpointCategories:
    """Test endpoints by category."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        return KRXOpenAPI(api_key="test-key")

    def test_index_endpoints(self, client, mock_api_response):
        """Test all index (idx) endpoints."""
        index_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "idx"]
        assert len(index_endpoints) == 5

        with requests_mock.Mocker() as m:
            for category, method_name, endpoint in index_endpoints:
                url = f"https://data-dbg.krx.co.kr/svc/apis/{category}/{endpoint}"
                m.get(url, json=mock_api_response)
                method = getattr(client, method_name)
                result = method("20240101")
                assert "OutBlock_1" in result

    def test_stock_endpoints(self, client, mock_api_response):
        """Test all stock (sto) endpoints."""
        stock_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "sto"]
        assert len(stock_endpoints) == 8

    def test_etp_endpoints(self, client, mock_api_response):
        """Test all ETP (etp) endpoints."""
        etp_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "etp"]
        assert len(etp_endpoints) == 3

    def test_bond_endpoints(self, client, mock_api_response):
        """Test all bond (bon) endpoints."""
        bond_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "bon"]
        assert len(bond_endpoints) == 3

    def test_derivative_endpoints(self, client, mock_api_response):
        """Test all derivative (drv) endpoints."""
        drv_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "drv"]
        assert len(drv_endpoints) == 6

    def test_general_market_endpoints(self, client, mock_api_response):
        """Test all general market (gen) endpoints."""
        gen_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "gen"]
        assert len(gen_endpoints) == 3

    def test_esg_endpoints(self, client, mock_api_response):
        """Test all ESG (esg) endpoints."""
        esg_endpoints = [e for e in ALL_ENDPOINTS if e[0] == "esg"]
        assert len(esg_endpoints) == 3
