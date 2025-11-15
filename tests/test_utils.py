"""
Unit Tests for Utility Functions
"""
import pytest
import pandas as pd
from datetime import datetime

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from old location (backward compatible)
from utils import (
    format_currency,
    format_percentage,
    format_large_number,
    safe_divide,
    validate_ticker,
    sanitize_dict_for_cache
)


class TestFormatters:
    """Test formatting functions"""
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert "$1.23K" in format_currency(1234.56)
        assert "$" in format_currency(100)
        assert format_currency(None) == "N/A"
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        result = format_percentage(12.345)
        assert "%" in result
        assert "12.35" in result or "12.3" in result
    
    def test_format_large_number(self):
        """Test large number formatting"""
        result = format_large_number(1234567890)
        assert "B" in result or "M" in result
        assert format_large_number(None) == "N/A"


class TestMathUtils:
    """Test mathematical utilities"""
    
    def test_safe_divide(self):
        """Test safe division"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=999) == 999
    
    def test_safe_divide_edge_cases(self):
        """Test edge cases"""
        assert safe_divide(0, 5) == 0.0
        assert safe_divide(None, 5) == 0.0
        assert safe_divide(10, None) == 0.0


class TestValidators:
    """Test validation functions"""
    
    def test_validate_ticker(self):
        """Test ticker validation"""
        assert validate_ticker("AAPL") == True
        assert validate_ticker("BTC-USD") == True
        assert validate_ticker("") == False
        assert validate_ticker("A" * 20) == False
    
    def test_validate_ticker_invalid(self):
        """Test invalid tickers"""
        assert validate_ticker("invalid!") == False
        assert validate_ticker("123") == False  # May vary by implementation


class TestDataSanitization:
    """Test data sanitization for caching"""
    
    def test_sanitize_timestamps(self):
        """Test Timestamp conversion"""
        data = {
            "timestamp": pd.Timestamp("2025-01-01"),
            "value": 123.45
        }
        result = sanitize_dict_for_cache(data)
        assert isinstance(result["timestamp"], str)
        assert result["value"] == 123.45
    
    def test_sanitize_nested(self):
        """Test nested dictionary sanitization"""
        data = {
            "outer": {
                "inner": {
                    "timestamp": pd.Timestamp("2025-01-01")
                }
            }
        }
        result = sanitize_dict_for_cache(data)
        assert isinstance(result["outer"]["inner"]["timestamp"], str)
    
    def test_sanitize_list_of_dicts(self):
        """Test list of dictionaries"""
        data = {
            "items": [
                {"ts": pd.Timestamp("2025-01-01")},
                {"ts": pd.Timestamp("2025-01-02")}
            ]
        }
        result = sanitize_dict_for_cache(data)
        assert isinstance(result["items"][0]["ts"], str)
        assert isinstance(result["items"][1]["ts"], str)


# Run tests with: pytest tests/test_utils.py -v
