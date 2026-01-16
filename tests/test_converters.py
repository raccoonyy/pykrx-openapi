"""Tests for data type converters."""

from datetime import datetime

from pykrx_openapi.converters import convert_field, convert_record, convert_response


class TestConvertField:
    """Tests for convert_field function."""

    def test_convert_date_field(self):
        """Test date string conversion to datetime."""
        result = convert_field("BAS_DD", "20240101")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_convert_date_field_list_dd(self):
        """Test LIST_DD date field conversion."""
        result = convert_field("LIST_DD", "20231215")
        assert isinstance(result, datetime)
        assert result == datetime(2023, 12, 15)

    def test_convert_price_field(self):
        """Test price field conversion to float."""
        result = convert_field("CLSPRC_IDX", "2655.50")
        assert isinstance(result, float)
        assert result == 2655.50

    def test_convert_price_with_comma(self):
        """Test price field with comma separator."""
        result = convert_field("TDD_CLSPRC", "1,234,567.89")
        assert isinstance(result, float)
        assert result == 1234567.89

    def test_convert_volume_field(self):
        """Test volume field conversion to int."""
        result = convert_field("ACC_TRDVOL", "123456")
        assert isinstance(result, int)
        assert result == 123456

    def test_convert_volume_with_comma(self):
        """Test volume field with comma separator."""
        result = convert_field("ACC_TRDVOL", "1,234,567")
        assert isinstance(result, int)
        assert result == 1234567

    def test_convert_index_field(self):
        """Test index field conversion to float."""
        result = convert_field("CLSPRC_IDX", "2655.50")
        assert isinstance(result, float)
        assert result == 2655.50

    def test_convert_rate_field(self):
        """Test rate field conversion to float."""
        result = convert_field("FLUC_RT", "0.59")
        assert isinstance(result, float)
        assert result == 0.59

    def test_convert_amount_field(self):
        """Test amount field conversion to float."""
        result = convert_field("ACC_TRDVAL", "123456.78")
        assert isinstance(result, float)
        assert result == 123456.78

    def test_convert_shares_field(self):
        """Test shares field conversion to int."""
        result = convert_field("LIST_SHRS", "1000000")
        assert isinstance(result, int)
        assert result == 1000000

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        assert convert_field("BAS_DD", "") is None
        assert convert_field("CLSPRC_IDX", "  ") is None

    def test_dash_returns_none(self):
        """Test that dash returns None."""
        assert convert_field("CLSPRC_IDX", "-") is None

    def test_invalid_date_returns_string(self):
        """Test that invalid date format returns original string."""
        result = convert_field("BAS_DD", "invalid")
        assert result == "invalid"

    def test_invalid_number_returns_string(self):
        """Test that invalid number returns original string."""
        result = convert_field("CLSPRC_IDX", "not_a_number")
        assert result == "not_a_number"

    def test_string_field_unchanged(self):
        """Test that non-numeric, non-date fields remain strings."""
        result = convert_field("IDX_NM", "KOSPI")
        assert result == "KOSPI"

    def test_parval_field(self):
        """Test PARVAL (액면가) field conversion."""
        result = convert_field("PARVAL", "5000")
        assert isinstance(result, float)
        assert result == 5000.0


class TestConvertRecord:
    """Tests for convert_record function."""

    def test_convert_record_mixed_types(self):
        """Test converting a record with mixed field types."""
        record = {
            "BAS_DD": "20240101",
            "IDX_NM": "KOSPI",
            "CLSPRC_IDX": "2655.50",
            "ACC_TRDVOL": "123456",
            "FLUC_RT": "0.59",
        }

        result = convert_record(record)

        assert isinstance(result["BAS_DD"], datetime)
        assert result["IDX_NM"] == "KOSPI"
        assert isinstance(result["CLSPRC_IDX"], float)
        assert isinstance(result["ACC_TRDVOL"], int)
        assert isinstance(result["FLUC_RT"], float)

    def test_convert_record_with_empty_values(self):
        """Test converting a record with empty values."""
        record = {
            "BAS_DD": "20240101",
            "CLSPRC_IDX": "-",
            "ACC_TRDVOL": "",
        }

        result = convert_record(record)

        assert isinstance(result["BAS_DD"], datetime)
        assert result["CLSPRC_IDX"] is None
        assert result["ACC_TRDVOL"] is None

    def test_convert_empty_record(self):
        """Test converting an empty record."""
        result = convert_record({})
        assert result == {}


class TestConvertResponse:
    """Tests for convert_response function."""

    def test_convert_response_multiple_records(self):
        """Test converting a response with multiple records."""
        data = [
            {
                "BAS_DD": "20240101",
                "IDX_NM": "KOSPI",
                "CLSPRC_IDX": "2655.50",
            },
            {
                "BAS_DD": "20240102",
                "IDX_NM": "KOSDAQ",
                "CLSPRC_IDX": "850.25",
            },
        ]

        result = convert_response(data)

        assert len(result) == 2
        assert isinstance(result[0]["BAS_DD"], datetime)
        assert isinstance(result[0]["CLSPRC_IDX"], float)
        assert isinstance(result[1]["BAS_DD"], datetime)
        assert isinstance(result[1]["CLSPRC_IDX"], float)

    def test_convert_empty_response(self):
        """Test converting an empty response."""
        result = convert_response([])
        assert result == []

    def test_convert_response_preserves_order(self):
        """Test that response conversion preserves record order."""
        data = [{"ID": str(i)} for i in range(5)]
        result = convert_response(data)

        assert len(result) == 5
        for i, record in enumerate(result):
            assert record["ID"] == str(i)
