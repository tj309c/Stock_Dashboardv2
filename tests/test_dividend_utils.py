import pytest

from app_utils import normalize_dividend_yield


def test_computed_from_rate_and_price():
    info = {'dividendRate': 1.0}
    pct, source = normalize_dividend_yield(info, current_price=100.0)
    assert pytest.approx(pct, rel=1e-6) == 1.0
    assert source == 'computed_from_rate_and_price'


def test_dividend_yield_fraction():
    info = {'dividendYield': 0.038}
    pct, source = normalize_dividend_yield(info)
    assert pytest.approx(pct, rel=1e-6) == 3.8
    assert source == 'dividendYield_fraction'


def test_dividend_yield_raw_percent():
    info = {'dividendYield': 3.8}
    pct, source = normalize_dividend_yield(info)
    assert pytest.approx(pct, rel=1e-6) == 3.8
    assert source == 'dividendYield_raw_percent'


def test_suspicious_computed_value():
    info = {'dividendRate': 1000}
    pct, source = normalize_dividend_yield(info, current_price=1.0)
    assert pct is None
    assert source == 'suspicious_computed_value'


def test_not_available():
    info = {}
    pct, source = normalize_dividend_yield(info)
    assert pct is None
    assert source == 'not_available'
