"""
Unit Tests for OptionsAnalysisService
Tests all methods with mock data
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
import numpy as np

from src.services.options_analysis_service import OptionsAnalysisService
from src.core.types import (
    OptionsChain,
    OptionContract,
    GreeksData,
    UnusualActivity
)
from src.core.errors import DataFetchError, AnalysisError


# ========== FIXTURES ==========

@pytest.fixture
def mock_fetcher():
    """Mock MarketDataFetcher"""
    fetcher = Mock()
    
    # Mock get_realtime_quote
    fetcher.get_realtime_quote.return_value = {
        "price": 450.0,
        "change": 2.5,
        "changePercent": 0.56
    }
    
    # Mock get_options_chain
    fetcher.get_options_chain.return_value = {
        "chains": {
            "2024-03-15": {
                "calls": [
                    {
                        "strike": 445.0,
                        "lastPrice": 8.50,
                        "bid": 8.40,
                        "ask": 8.60,
                        "volume": 250,
                        "openInterest": 100,
                        "impliedVolatility": 0.25
                    },
                    {
                        "strike": 450.0,
                        "lastPrice": 6.00,
                        "bid": 5.90,
                        "ask": 6.10,
                        "volume": 500,
                        "openInterest": 200,
                        "impliedVolatility": 0.24
                    },
                    {
                        "strike": 455.0,
                        "lastPrice": 4.00,
                        "bid": 3.90,
                        "ask": 4.10,
                        "volume": 150,
                        "openInterest": 300,
                        "impliedVolatility": 0.26
                    }
                ],
                "puts": [
                    {
                        "strike": 445.0,
                        "lastPrice": 3.00,
                        "bid": 2.90,
                        "ask": 3.10,
                        "volume": 200,
                        "openInterest": 150,
                        "impliedVolatility": 0.27
                    },
                    {
                        "strike": 450.0,
                        "lastPrice": 5.50,
                        "bid": 5.40,
                        "ask": 5.60,
                        "volume": 300,
                        "openInterest": 100,
                        "impliedVolatility": 0.28
                    },
                    {
                        "strike": 455.0,
                        "lastPrice": 8.00,
                        "bid": 7.90,
                        "ask": 8.10,
                        "volume": 400,
                        "openInterest": 80,
                        "impliedVolatility": 0.30
                    }
                ]
            },
            "2024-04-19": {
                "calls": [
                    {
                        "strike": 450.0,
                        "lastPrice": 12.00,
                        "bid": 11.80,
                        "ask": 12.20,
                        "volume": 100,
                        "openInterest": 50,
                        "impliedVolatility": 0.23
                    }
                ],
                "puts": [
                    {
                        "strike": 450.0,
                        "lastPrice": 10.00,
                        "bid": 9.80,
                        "ask": 10.20,
                        "volume": 80,
                        "openInterest": 40,
                        "impliedVolatility": 0.29
                    }
                ]
            }
        }
    }
    
    return fetcher


@pytest.fixture
def components(mock_fetcher):
    """Components dict for service"""
    return {
        "fetcher": mock_fetcher,
        "options": Mock()
    }


@pytest.fixture
def service(components):
    """OptionsAnalysisService instance"""
    return OptionsAnalysisService(components)


@pytest.fixture
def sample_chain():
    """Sample OptionsChain"""
    return OptionsChain(
        ticker="SPY",
        current_price=450.0,
        expirations=["2024-03-15", "2024-04-19"],
        chains={
            "2024-03-15": {
                "calls": [
                    {
                        "strike": 445.0,
                        "lastPrice": 8.50,
                        "bid": 8.40,
                        "ask": 8.60,
                        "volume": 250,
                        "openInterest": 100,
                        "impliedVolatility": 0.25
                    },
                    {
                        "strike": 450.0,
                        "lastPrice": 6.00,
                        "bid": 5.90,
                        "ask": 6.10,
                        "volume": 500,
                        "openInterest": 200,
                        "impliedVolatility": 0.24
                    }
                ],
                "puts": [
                    {
                        "strike": 445.0,
                        "lastPrice": 3.00,
                        "bid": 2.90,
                        "ask": 3.10,
                        "volume": 200,
                        "openInterest": 150,
                        "impliedVolatility": 0.27
                    }
                ]
            }
        },
        timestamp=datetime.now()
    )


@pytest.fixture
def sample_contracts():
    """Sample OptionContract list"""
    return [
        OptionContract(
            contract_type="call",
            strike=450.0,
            expiration="2024-03-15",
            last_price=6.00,
            bid=5.90,
            ask=6.10,
            volume=500,
            open_interest=200,
            implied_volatility=0.24
        ),
        OptionContract(
            contract_type="put",
            strike=450.0,
            expiration="2024-03-15",
            last_price=5.50,
            bid=5.40,
            ask=5.60,
            volume=300,
            open_interest=100,
            implied_volatility=0.28
        )
    ]


# ========== SERVICE INITIALIZATION ==========

def test_service_initialization_success(components):
    """Test successful service initialization"""
    service = OptionsAnalysisService(components)
    assert service.fetcher is not None
    assert service.options_analyzer is not None


def test_service_initialization_missing_fetcher():
    """Test initialization fails without fetcher"""
    with pytest.raises(ValueError, match="Missing required component: fetcher"):
        OptionsAnalysisService({})


# ========== ANALYZE OPTIONS CHAIN ==========

def test_analyze_options_chain_success(service):
    """Test successful options chain analysis"""
    chain = service.analyze_options_chain("SPY")
    
    assert isinstance(chain, OptionsChain)
    assert chain.ticker == "SPY"
    assert chain.current_price == 450.0
    assert len(chain.expirations) == 2
    assert "2024-03-15" in chain.expirations
    assert "2024-04-19" in chain.expirations


def test_analyze_options_chain_no_data(service, mock_fetcher):
    """Test chain analysis with no data"""
    mock_fetcher.get_options_chain.return_value = {"error": "No data"}
    
    with pytest.raises(DataFetchError, match="Cannot fetch options"):
        service.analyze_options_chain("INVALID")


def test_analyze_options_chain_no_price(service, mock_fetcher):
    """Test chain analysis with no price"""
    mock_fetcher.get_realtime_quote.return_value = {"price": 0}
    
    with pytest.raises(DataFetchError, match="Cannot get current price"):
        service.analyze_options_chain("SPY")


# ========== GET CONTRACTS BY EXPIRATION ==========

def test_get_contracts_by_expiration_both(service, sample_chain):
    """Test getting both calls and puts"""
    contracts = service.get_contracts_by_expiration(sample_chain, "2024-03-15", "both")
    
    assert len(contracts) == 3  # 2 calls + 1 put
    assert sum(1 for c in contracts if c.contract_type == "call") == 2
    assert sum(1 for c in contracts if c.contract_type == "put") == 1


def test_get_contracts_by_expiration_calls_only(service, sample_chain):
    """Test getting only calls"""
    contracts = service.get_contracts_by_expiration(sample_chain, "2024-03-15", "calls")
    
    assert len(contracts) == 2
    assert all(c.contract_type == "call" for c in contracts)


def test_get_contracts_by_expiration_puts_only(service, sample_chain):
    """Test getting only puts"""
    contracts = service.get_contracts_by_expiration(sample_chain, "2024-03-15", "puts")
    
    assert len(contracts) == 1
    assert all(c.contract_type == "put" for c in contracts)


def test_get_contracts_invalid_expiration(service, sample_chain):
    """Test with invalid expiration"""
    contracts = service.get_contracts_by_expiration(sample_chain, "2099-12-31", "both")
    assert len(contracts) == 0


# ========== GREEKS CALCULATION ==========

def test_calculate_greeks_call(service):
    """Test Greeks calculation for call option"""
    greeks = service.calculate_greeks(
        spot_price=100.0,
        strike=100.0,
        time_to_expiry=0.25,  # 3 months
        volatility=0.25,
        risk_free_rate=0.045,
        option_type="call"
    )
    
    assert isinstance(greeks, GreeksData)
    assert 0 < greeks.delta <= 1  # Call delta: 0 to 1
    assert greeks.gamma > 0  # Always positive
    assert greeks.theta < 0  # Time decay negative
    assert greeks.vega > 0  # Always positive
    assert greeks.rho > 0  # Call rho positive


def test_calculate_greeks_put(service):
    """Test Greeks calculation for put option"""
    greeks = service.calculate_greeks(
        spot_price=100.0,
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.25,
        risk_free_rate=0.045,
        option_type="put"
    )
    
    assert isinstance(greeks, GreeksData)
    assert -1 <= greeks.delta < 0  # Put delta: -1 to 0
    assert greeks.gamma > 0  # Always positive
    assert greeks.theta < 0  # Time decay negative
    assert greeks.vega > 0  # Always positive
    assert greeks.rho < 0  # Put rho negative


def test_calculate_greeks_itm_call(service):
    """Test ITM call has higher delta"""
    greeks = service.calculate_greeks(
        spot_price=110.0,  # ITM
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks.delta > 0.7  # ITM call should have high delta


def test_calculate_greeks_otm_call(service):
    """Test OTM call has lower delta"""
    greeks = service.calculate_greeks(
        spot_price=90.0,  # OTM
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks.delta < 0.3  # OTM call should have low delta


def test_calculate_greeks_zero_time(service):
    """Test Greeks with zero time to expiry"""
    greeks = service.calculate_greeks(
        spot_price=100.0,
        strike=100.0,
        time_to_expiry=0,  # Expired
        volatility=0.25,
        option_type="call"
    )
    
    # Should still return valid Greeks (uses 1 day minimum)
    assert isinstance(greeks, GreeksData)


# ========== UNUSUAL ACTIVITY DETECTION ==========

def test_detect_unusual_activity_found(service, sample_chain):
    """Test detecting unusual activity"""
    unusual = service.detect_unusual_activity(sample_chain, volume_threshold=2.0, min_volume=100)
    
    # Should find 450 call (500 vol / 200 OI = 2.5) and 450 put (300 vol / 100 OI = 3.0)
    # and 455 put (400 vol / 80 OI = 5.0)
    assert len(unusual) >= 2
    assert all(isinstance(u, UnusualActivity) for u in unusual)
    assert all(u.volume_oi_ratio >= 2.0 for u in unusual)


def test_detect_unusual_activity_sorted(service, sample_chain):
    """Test unusual activity sorted by ratio"""
    unusual = service.detect_unusual_activity(sample_chain)
    
    if len(unusual) > 1:
        # Check descending order
        for i in range(len(unusual) - 1):
            assert unusual[i].volume_oi_ratio >= unusual[i + 1].volume_oi_ratio


def test_detect_unusual_activity_min_volume(service, sample_chain):
    """Test minimum volume filter"""
    unusual = service.detect_unusual_activity(sample_chain, min_volume=1000)
    
    # No contracts have volume >= 1000 in sample data
    assert len(unusual) == 0


# ========== STRATEGY RECOMMENDATIONS ==========

def test_get_strategy_recommendations_bullish(service, sample_chain):
    """Test bullish strategy recommendations"""
    strategies = service.get_strategy_recommendations(sample_chain, 450.0, "bullish")
    
    assert len(strategies) > 0
    assert any(s["name"] == "Long Call" for s in strategies)
    assert all(s["type"] == "bullish" for s in strategies)


def test_get_strategy_recommendations_bearish(service, sample_chain):
    """Test bearish strategy recommendations"""
    strategies = service.get_strategy_recommendations(sample_chain, 450.0, "bearish")
    
    assert len(strategies) > 0
    assert any(s["name"] == "Long Put" for s in strategies)
    assert all(s["type"] == "bearish" for s in strategies)


def test_get_strategy_recommendations_neutral(service, sample_chain):
    """Test neutral strategy recommendations"""
    strategies = service.get_strategy_recommendations(sample_chain, 450.0, "neutral")
    
    assert len(strategies) > 0
    assert any(s["name"] == "Covered Call" for s in strategies)
    assert all(s["type"] == "neutral" for s in strategies)


def test_get_strategy_recommendations_no_expirations(service):
    """Test with empty chain"""
    empty_chain = OptionsChain(
        ticker="SPY",
        current_price=450.0,
        expirations=[],
        chains={},
        timestamp=datetime.now()
    )
    
    strategies = service.get_strategy_recommendations(empty_chain, 450.0, "bullish")
    assert len(strategies) == 0


# ========== COVERED CALL ==========

def test_calculate_covered_call(service):
    """Test covered call calculation"""
    result = service.calculate_covered_call(
        stock_price=100.0,
        strike=105.0,
        premium=2.50,
        shares=100
    )
    
    assert result["strategy"] == "Covered Call"
    assert result["max_profit"] == 750.0  # (105-100)*100 + 2.50*100
    assert result["max_loss"] == float('inf')
    assert result["breakeven"] == 97.50  # 100 - 2.50
    assert result["premium_income"] == 250.0  # 2.50 * 100
    assert result["return_on_capital"] > 0


# ========== VERTICAL SPREAD ==========

def test_calculate_vertical_spread_bull_call(service):
    """Test bull call spread calculation"""
    result = service.calculate_vertical_spread(
        long_strike=100.0,
        short_strike=105.0,
        long_premium=3.00,
        short_premium=1.00,
        spread_type="bull_call"
    )
    
    assert result["strategy"] == "Bull Call"
    assert result["net_debit"] == 200.0  # (3.00 - 1.00) * 100
    assert result["max_profit"] == 300.0  # (105-100)*100 - 200
    assert result["max_loss"] == 200.0
    assert result["breakeven"] == 102.0  # 100 + 2.00
    assert result["risk_reward_ratio"] == 1.5  # 300/200


def test_calculate_vertical_spread_bear_put(service):
    """Test bear put spread calculation"""
    result = service.calculate_vertical_spread(
        long_strike=105.0,
        short_strike=100.0,
        long_premium=4.00,
        short_premium=2.00,
        spread_type="bear_put"
    )
    
    assert result["strategy"] == "Bear Put"
    assert result["net_debit"] == 200.0  # (4.00 - 2.00) * 100
    assert result["max_profit"] == 300.0  # (105-100)*100 - 200
    assert result["max_loss"] == 200.0


# ========== IRON CONDOR ==========

def test_calculate_iron_condor(service):
    """Test iron condor calculation"""
    result = service.calculate_iron_condor(
        put_buy_strike=95.0,
        put_sell_strike=97.5,
        call_sell_strike=102.5,
        call_buy_strike=105.0,
        put_buy_premium=0.50,
        put_sell_premium=1.00,
        call_sell_premium=1.00,
        call_buy_premium=0.50
    )
    
    assert result["strategy"] == "Iron Condor"
    assert result["net_credit"] == 100.0  # ((1.00-0.50) + (1.00-0.50)) * 100
    assert result["max_profit"] == 100.0
    assert result["max_loss"] == 150.0  # Max spread width (250) - credit (100)
    assert result["lower_breakeven"] == 96.50  # 97.5 - 1.00
    assert result["upper_breakeven"] == 103.50  # 102.5 + 1.00
    assert "probability_of_profit" in result


# ========== IV METRICS ==========

def test_calculate_iv_metrics(service, sample_chain):
    """Test IV metrics calculation"""
    metrics = service.calculate_iv_metrics(sample_chain, "2024-03-15")
    
    assert "average_iv" in metrics
    assert "min_iv" in metrics
    assert "max_iv" in metrics
    assert "iv_rank" in metrics
    assert "iv_percentile" in metrics
    assert "volatility_skew" in metrics
    
    assert 0 <= metrics["iv_rank"] <= 100
    assert metrics["min_iv"] <= metrics["average_iv"] <= metrics["max_iv"]


def test_calculate_iv_metrics_no_contracts(service, sample_chain):
    """Test IV metrics with invalid expiration"""
    metrics = service.calculate_iv_metrics(sample_chain, "2099-12-31")
    assert "error" in metrics


# ========== EDGE CASES ==========

def test_greeks_high_volatility(service):
    """Test Greeks with very high volatility"""
    greeks = service.calculate_greeks(
        spot_price=100.0,
        strike=100.0,
        time_to_expiry=0.25,
        volatility=1.0,  # 100% volatility
        option_type="call"
    )
    
    assert isinstance(greeks, GreeksData)
    assert greeks.vega > 0


def test_greeks_low_volatility(service):
    """Test Greeks with very low volatility"""
    greeks = service.calculate_greeks(
        spot_price=100.0,
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.01,  # 1% volatility
        option_type="call"
    )
    
    assert isinstance(greeks, GreeksData)
    assert greeks.vega > 0


def test_greeks_deep_itm(service):
    """Test Greeks for deep ITM option"""
    greeks = service.calculate_greeks(
        spot_price=150.0,
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks.delta > 0.95  # Deep ITM should be near 1.0


def test_greeks_deep_otm(service):
    """Test Greeks for deep OTM option"""
    greeks = service.calculate_greeks(
        spot_price=50.0,
        strike=100.0,
        time_to_expiry=0.25,
        volatility=0.25,
        option_type="call"
    )
    
    assert greeks.delta < 0.05  # Deep OTM should be near 0


# ========== INTEGRATION TESTS ==========

def test_full_analysis_workflow(service):
    """Test complete analysis workflow"""
    # 1. Fetch chain
    chain = service.analyze_options_chain("SPY")
    assert isinstance(chain, OptionsChain)
    
    # 2. Get contracts
    contracts = service.get_contracts_by_expiration(chain, chain.expirations[0])
    assert len(contracts) > 0
    
    # 3. Calculate Greeks for first contract
    contract = contracts[0]
    greeks = service.calculate_greeks(
        spot_price=chain.current_price,
        strike=contract.strike,
        time_to_expiry=0.25,
        volatility=contract.implied_volatility,
        option_type=contract.contract_type
    )
    assert isinstance(greeks, GreeksData)
    
    # 4. Detect unusual activity
    unusual = service.detect_unusual_activity(chain)
    assert isinstance(unusual, list)
    
    # 5. Get strategies
    strategies = service.get_strategy_recommendations(chain, chain.current_price, "neutral")
    assert isinstance(strategies, list)
    
    # 6. Calculate IV metrics
    iv_metrics = service.calculate_iv_metrics(chain, chain.expirations[0])
    assert "average_iv" in iv_metrics


def test_analyze_multiple_tickers(service):
    """Test analyzing multiple tickers"""
    tickers = ["SPY", "QQQ", "IWM"]
    
    for ticker in tickers:
        chain = service.analyze_options_chain(ticker)
        assert chain.ticker == ticker
        assert chain.current_price > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
