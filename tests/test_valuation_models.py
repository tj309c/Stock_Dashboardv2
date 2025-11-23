"""
Tests for valuation_models.py
"""
import pytest
import pandas as pd
import numpy as np
from valuation_models import calculate_dcf, calculate_ddm, calculate_nav, DCFInputs


def test_calculate_dcf_basic():
    """Test basic DCF calculation with valid inputs"""
    inputs = DCFInputs(
        revenue_growth_rates=[0.10, 0.08, 0.06],
        ebit_margin=0.20,
        tax_rate=0.21,
        depreciation_as_pct_revenue=0.03,
        capex_as_pct_revenue=0.05,
        nwc_as_pct_revenue=0.10,
        terminal_growth_rate=0.02,
        wacc=0.10,
        cash=50_000_000,
        total_debt=20_000_000,
        shares_outstanding=10_000_000,
        current_revenue=100_000_000
    )

    result, intermediates = calculate_dcf(inputs)

    assert result is not None
    assert isinstance(result, float)
    assert result >= 0
    assert isinstance(intermediates, dict)


def test_calculate_dcf_zero_shares():
    """Test DCF with zero shares outstanding"""
    inputs = DCFInputs(
        revenue_growth_rates=[0.10],
        ebit_margin=0.20,
        tax_rate=0.21,
        depreciation_as_pct_revenue=0.03,
        capex_as_pct_revenue=0.05,
        nwc_as_pct_revenue=0.10,
        terminal_growth_rate=0.02,
        wacc=0.10,
        cash=50_000_000,
        total_debt=20_000_000,
        shares_outstanding=0,
        current_revenue=100_000_000
    )

    result, intermediates = calculate_dcf(inputs)
    assert result == 0


def test_calculate_dcf_high_wacc():
    """Test DCF with WACC higher than terminal growth"""
    inputs = DCFInputs(
        revenue_growth_rates=[0.10, 0.08],
        ebit_margin=0.20,
        tax_rate=0.21,
        depreciation_as_pct_revenue=0.03,
        capex_as_pct_revenue=0.05,
        nwc_as_pct_revenue=0.10,
        terminal_growth_rate=0.02,
        wacc=0.15,
        cash=50_000_000,
        total_debt=20_000_000,
        shares_outstanding=10_000_000,
        current_revenue=100_000_000
    )

    result, intermediates = calculate_dcf(inputs)
    assert result >= 0


def test_calculate_ddm_basic():
    """Test basic DDM calculation"""
    dividend = 2.50
    wacc = 0.10
    growth_rate = 0.05

    result = calculate_ddm(dividend, wacc, growth_rate)

    assert result is not None
    assert isinstance(result, (int, float))
    assert result > 0
    expected = dividend * (1 + growth_rate) / (wacc - growth_rate)
    assert abs(result - expected) < 0.01


def test_calculate_ddm_zero_dividend():
    """Test DDM with zero dividend"""
    result = calculate_ddm(0, 0.10, 0.05)
    assert result == 0.0


def test_calculate_ddm_invalid_inputs():
    """Test DDM with invalid inputs (growth >= wacc)"""
    result = calculate_ddm(2.50, 0.10, 0.10)
    assert result == 0.0

    result = calculate_ddm(2.50, 0.10, 0.15)
    assert result == 0.0


def test_calculate_nav_basic():
    """Test basic NAV calculation"""
    info = {
        'totalAssets': 100_000_000,
        'totalLiab': 40_000_000,
        'sharesOutstanding': 10_000_000
    }

    result = calculate_nav(info)

    assert result is not None
    assert isinstance(result, (int, float))
    expected = (100_000_000 - 40_000_000) / 10_000_000
    assert abs(result - expected) < 0.01


def test_calculate_nav_zero_shares():
    """Test NAV with zero shares"""
    info = {
        'totalAssets': 100_000_000,
        'totalLiab': 40_000_000,
        'sharesOutstanding': 0
    }

    result = calculate_nav(info)
    assert result == 0.0


def test_calculate_nav_zero_assets():
    """Test NAV with zero assets"""
    info = {
        'totalAssets': 0,
        'totalLiab': 40_000_000,
        'sharesOutstanding': 10_000_000
    }

    result = calculate_nav(info)
    assert result == 0.0


def test_calculate_nav_missing_data():
    """Test NAV with missing data"""
    info = {}

    result = calculate_nav(info)
    assert result == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
