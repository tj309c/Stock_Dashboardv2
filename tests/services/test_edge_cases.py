"""
Edge Case Tests for Services Layer
Tests boundary conditions, error scenarios, and unusual inputs
"""
import pytest
from unittest.mock import Mock
from datetime import datetime
import numpy as np

from src.services import StocksAnalysisService, OptionsAnalysisService
from src.core.types import *
from src.core.errors import *


# ========== STOCK SERVICE EDGE CASES ==========

def test_stock_with_zero_price():
    """Test handling of zero stock price"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {"regularMarketPrice": 0}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    service = StocksAnalysisService(components)
    
    with pytest.raises(Exception):
        service.analyze_stock("INVALID")


def test_stock_with_negative_values():
    """Test handling of negative financial metrics"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {
        "regularMarketPrice": 100,
        "trailingPE": -5,  # Negative P/E (company losing money)
        "profitMargins": -0.1,  # Negative margin
        "returnOnEquity": -0.2  # Negative ROE
    }
    fetcher.get_historical_data.return_value = {"Close": [100, 95, 90]}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    components["analyzer"].analyze.return_value = {"rsi": {"value": 50}}
    components["valuation"].calculate_fair_value.return_value = {"fair_value": 80}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("LOSS")
    
    # Should handle negative values gracefully
    assert result is not None
    if result.fundamentals:
        assert result.fundamentals.pe_ratio == -5


def test_stock_with_missing_data():
    """Test handling of incomplete stock data"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {
        "regularMarketPrice": 100
        # Missing most fields
    }
    fetcher.get_historical_data.return_value = {"Close": [100]}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    components["analyzer"].analyze.return_value = {}
    components["valuation"].calculate_fair_value.return_value = {}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("INCOMPLETE")
    
    # Should use default values
    assert result is not None
    assert result.price.current == 100


def test_stock_with_extreme_rsi():
    """Test handling of RSI at boundaries"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {"regularMarketPrice": 100}
    fetcher.get_historical_data.return_value = {"Close": [100, 100, 100]}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    # Test RSI = 0
    components["analyzer"].analyze.return_value = {"rsi": {"value": 0}}
    components["valuation"].calculate_fair_value.return_value = {"fair_value": 100}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("OVERSOLD")
    
    assert result.technical.rsi == 0
    
    # Test RSI = 100
    components["analyzer"].analyze.return_value = {"rsi": {"value": 100}}
    result = service.analyze_stock("OVERBOUGHT")
    
    assert result.technical.rsi == 100


def test_stock_with_infinite_values():
    """Test handling of infinite volatility or metrics"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {
        "regularMarketPrice": 100,
        "beta": float('inf')  # Infinite beta
    }
    fetcher.get_historical_data.return_value = {
        "Close": [100, 200, 50, 300, 10]  # Extreme volatility
    }
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    components["analyzer"].analyze.return_value = {"rsi": {"value": 50}}
    components["valuation"].calculate_fair_value.return_value = {"fair_value": 100}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("VOLATILE")
    
    # Should handle gracefully
    assert result is not None


# ========== OPTIONS SERVICE EDGE CASES ==========

def test_options_with_zero_volatility():
    """Test Greeks with zero volatility"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=100,
        strike=100,
        time_to_expiry=0.25,
        volatility=0.0,  # Zero volatility
        option_type="call"
    )
    
    # Should handle gracefully (may use small epsilon internally)
    assert greeks is not None


def test_options_with_very_high_volatility():
    """Test Greeks with extreme volatility"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=100,
        strike=100,
        time_to_expiry=0.25,
        volatility=5.0,  # 500% volatility
        option_type="call"
    )
    
    assert greeks is not None
    assert greeks.vega > 0


def test_options_at_expiration():
    """Test options with zero time to expiry"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=100,
        strike=100,
        time_to_expiry=0.0,  # Expired
        volatility=0.25,
        option_type="call"
    )
    
    # Should use minimum time (1 day)
    assert greeks is not None


def test_options_far_in_future():
    """Test long-dated options"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=100,
        strike=100,
        time_to_expiry=10.0,  # 10 years
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks is not None
    assert greeks.theta != 0


def test_deep_itm_call():
    """Test very deep ITM call option"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=200,  # Very deep ITM
        strike=100,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    # Delta should be near 1.0
    assert 0.95 < greeks.delta <= 1.0
    # Gamma should be near 0
    assert greeks.gamma < 0.01


def test_deep_otm_call():
    """Test very deep OTM call option"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    greeks = service.calculate_greeks(
        spot_price=50,  # Very deep OTM
        strike=100,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    # Delta should be near 0
    assert 0 <= greeks.delta < 0.05
    # Gamma should be near 0
    assert greeks.gamma < 0.01


def test_negative_strike_price():
    """Test handling of invalid negative strike"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    # Should handle gracefully (may return zero Greeks)
    greeks = service.calculate_greeks(
        spot_price=100,
        strike=-50,  # Invalid negative strike
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks is not None


def test_covered_call_with_zero_premium():
    """Test covered call with zero premium"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    result = service.calculate_covered_call(
        stock_price=100,
        strike=105,
        premium=0.0,  # Zero premium
        shares=100
    )
    
    assert result["premium_income"] == 0
    assert result["breakeven"] == 100


def test_vertical_spread_zero_width():
    """Test spread with same strike prices"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    result = service.calculate_vertical_spread(
        long_strike=100,
        short_strike=100,  # Same strike
        long_premium=5.0,
        short_premium=3.0,
        spread_type="bull_call"
    )
    
    assert result["max_profit"] == -200  # Net debit only


def test_iron_condor_inverted_strikes():
    """Test iron condor with inverted strikes"""
    components = {"fetcher": Mock()}
    service = OptionsAnalysisService(components)
    
    result = service.calculate_iron_condor(
        put_buy_strike=95,
        put_sell_strike=100,
        call_sell_strike=110,
        call_buy_strike=115,
        put_buy_premium=1.0,
        put_sell_premium=2.0,
        call_sell_premium=2.0,
        call_buy_premium=1.0
    )
    
    # Should have positive net credit
    assert result["net_credit"] > 0


# ========== BOUNDARY VALUE TESTS ==========

def test_rsi_boundary_values():
    """Test RSI at exact boundaries"""
    for rsi_value in [0, 30, 50, 70, 100]:
        fetcher = Mock()
        fetcher.get_stock_info.return_value = {"regularMarketPrice": 100}
        fetcher.get_historical_data.return_value = {"Close": [100]}
        
        components = {
            "fetcher": fetcher,
            "analyzer": Mock(),
            "valuation": Mock(),
            "signals": Mock()
        }
        
        components["analyzer"].analyze.return_value = {"rsi": {"value": rsi_value}}
        components["valuation"].calculate_fair_value.return_value = {"fair_value": 100}
        components["signals"].generate_signals.return_value = []
        
        service = StocksAnalysisService(components)
        result = service.analyze_stock("TEST")
        
        assert result.technical.rsi == rsi_value


def test_pe_ratio_boundary_values():
    """Test P/E ratio edge cases"""
    test_cases = [
        (0, "zero P/E"),
        (5, "low P/E"),
        (50, "high P/E"),
        (1000, "extreme P/E"),
        (-10, "negative P/E")
    ]
    
    for pe_value, description in test_cases:
        fetcher = Mock()
        fetcher.get_stock_info.return_value = {
            "regularMarketPrice": 100,
            "trailingPE": pe_value
        }
        fetcher.get_historical_data.return_value = {"Close": [100]}
        
        components = {
            "fetcher": fetcher,
            "analyzer": Mock(),
            "valuation": Mock(),
            "signals": Mock()
        }
        
        components["analyzer"].analyze.return_value = {"rsi": {"value": 50}}
        components["valuation"].calculate_fair_value.return_value = {"fair_value": 100}
        components["signals"].generate_signals.return_value = []
        
        service = StocksAnalysisService(components)
        result = service.analyze_stock("TEST")
        
        if result.fundamentals:
            assert result.fundamentals.pe_ratio == pe_value, f"Failed for {description}"


def test_empty_unusual_activity():
    """Test unusual activity with no data"""
    fetcher = Mock()
    fetcher.get_options_chain.return_value = {"chains": {}}
    
    components = {"fetcher": fetcher}
    service = OptionsAnalysisService(components)
    
    unusual = service.detect_unusual_activity("NONE", volume_threshold=2.0)
    
    assert unusual == []


def test_all_contracts_have_zero_volume():
    """Test unusual activity when all volume is zero"""
    fetcher = Mock()
    fetcher.get_options_chain.return_value = {
        "chains": {
            "2024-03-15": {
                "calls": [
                    {
                        "strike": 100,
                        "lastPrice": 5.0,
                        "bid": 4.90,
                        "ask": 5.10,
                        "volume": 0,  # Zero volume
                        "openInterest": 100,
                        "impliedVolatility": 0.25
                    }
                ]
            }
        }
    }
    
    components = {"fetcher": fetcher}
    service = OptionsAnalysisService(components)
    
    unusual = service.detect_unusual_activity("LOW", volume_threshold=2.0)
    
    assert unusual == []


# ========== STRESS TESTS ==========

def test_very_large_market_cap():
    """Test handling of extremely large market cap"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {
        "regularMarketPrice": 1000,
        "marketCap": 10_000_000_000_000  # 10 trillion
    }
    fetcher.get_historical_data.return_value = {"Close": [1000]}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    components["analyzer"].analyze.return_value = {"rsi": {"value": 50}}
    components["valuation"].calculate_fair_value.return_value = {"fair_value": 1000}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("MEGA")
    
    assert result.price.market_cap == 10_000_000_000_000


def test_penny_stock():
    """Test handling of very low priced stock"""
    fetcher = Mock()
    fetcher.get_stock_info.return_value = {
        "regularMarketPrice": 0.01,  # $0.01
        "marketCap": 1_000_000
    }
    fetcher.get_historical_data.return_value = {"Close": [0.01, 0.01, 0.01]}
    
    components = {
        "fetcher": fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock()
    }
    
    components["analyzer"].analyze.return_value = {"rsi": {"value": 50}}
    components["valuation"].calculate_fair_value.return_value = {"fair_value": 0.01}
    components["signals"].generate_signals.return_value = []
    
    service = StocksAnalysisService(components)
    result = service.analyze_stock("PENNY")
    
    assert result.price.current == 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
