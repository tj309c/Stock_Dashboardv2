"""
Integration Tests for Services Layer
Tests interactions between StocksAnalysisService and OptionsAnalysisService
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
import time

from src.services import StocksAnalysisService, OptionsAnalysisService
from src.core.types import StockAnalysisResult, OptionsChain, OptionContract
from src.core.errors import DataFetchError, AnalysisError


# ========== FIXTURES ==========

@pytest.fixture
def mock_fetcher():
    """Mock MarketDataFetcher with data for both stocks and options"""
    fetcher = Mock()
    
    # Stock data
    fetcher.get_stock_info.return_value = {
        "symbol": "AAPL",
        "shortName": "Apple Inc.",
        "regularMarketPrice": 175.00,
        "regularMarketOpen": 174.50,
        "regularMarketDayHigh": 176.00,
        "regularMarketDayLow": 173.50,
        "regularMarketVolume": 50000000,
        "marketCap": 2800000000000,
        "fiftyTwoWeekHigh": 200.00,
        "fiftyTwoWeekLow": 150.00
    }
    
    fetcher.get_historical_data.return_value = {
        "Close": [170, 172, 171, 173, 175],
        "Volume": [48000000, 49000000, 47000000, 51000000, 50000000]
    }
    
    # Options data
    fetcher.get_options_chain.return_value = {
        "chains": {
            "2024-03-15": {
                "calls": [
                    {
                        "strike": 175.0,
                        "lastPrice": 5.00,
                        "bid": 4.90,
                        "ask": 5.10,
                        "volume": 500,
                        "openInterest": 200,
                        "impliedVolatility": 0.25
                    }
                ],
                "puts": [
                    {
                        "strike": 175.0,
                        "lastPrice": 4.50,
                        "bid": 4.40,
                        "ask": 4.60,
                        "volume": 300,
                        "openInterest": 150,
                        "impliedVolatility": 0.27
                    }
                ]
            }
        }
    }
    
    fetcher.get_realtime_quote.return_value = {
        "price": 175.00,
        "change": 0.50,
        "changePercent": 0.29
    }
    
    return fetcher


@pytest.fixture
def mock_components(mock_fetcher):
    """Complete components dict"""
    return {
        "fetcher": mock_fetcher,
        "analyzer": Mock(),
        "valuation": Mock(),
        "signals": Mock(),
        "options": Mock()
    }


@pytest.fixture
def stocks_service(mock_components):
    """StocksAnalysisService instance"""
    # Setup mock returns for analyzer components
    mock_components["analyzer"].analyze.return_value = {
        "rsi": {"value": 55.0},
        "macd": {"macd": 2.5, "signal": 2.0, "histogram": 0.5},
        "bollinger": {"upper": 180, "middle": 175, "lower": 170},
        "price_action": {"sma_20": 174, "sma_50": 172, "sma_200": 168, "ema_12": 175.5, "ema_26": 174.0},
        "volume_analysis": {"adx": 25, "obv": 1000000, "atr": 3.5}
    }
    
    mock_components["valuation"].calculate_fair_value.return_value = {
        "fair_value": 180.0,
        "method": "DCF",
        "confidence": 0.75,
        "scenarios": {"bull": 200, "base": 180, "bear": 160}
    }
    
    mock_components["signals"].generate_signals.return_value = [
        {"signal": "BUY", "confidence": 0.8, "reasoning": "Strong momentum"}
    ]
    
    return StocksAnalysisService(mock_components)


@pytest.fixture
def options_service(mock_components):
    """OptionsAnalysisService instance"""
    return OptionsAnalysisService(mock_components)


# ========== INTEGRATION TESTS ==========

def test_both_services_initialize_with_same_components(mock_components):
    """Test both services can share components"""
    stocks = StocksAnalysisService(mock_components)
    options = OptionsAnalysisService(mock_components)
    
    assert stocks.fetcher is options.fetcher
    assert stocks.fetcher is not None


def test_analyze_stock_and_options_for_same_ticker(stocks_service, options_service):
    """Test analyzing both stock and options for same ticker"""
    ticker = "AAPL"
    
    # Analyze stock
    stock_result = stocks_service.analyze_stock(ticker)
    assert stock_result.ticker == ticker
    assert stock_result.price.current > 0
    
    # Analyze options
    options_chain = options_service.analyze_options_chain(ticker)
    assert options_chain.ticker == ticker
    assert options_chain.spot_price > 0
    
    # Verify prices match
    assert stock_result.price.current == options_chain.spot_price


def test_options_strategies_based_on_stock_analysis(stocks_service, options_service):
    """Test options strategies informed by stock analysis"""
    ticker = "AAPL"
    
    # Get stock analysis first
    stock_result = stocks_service.analyze_stock(ticker)
    
    # Determine outlook from stock analysis
    if stock_result.technical.rsi > 60:
        outlook = "bullish"
    elif stock_result.technical.rsi < 40:
        outlook = "bearish"
    else:
        outlook = "neutral"
    
    # Get options strategies based on outlook
    strategies = options_service.get_strategy_recommendations(
        ticker,
        stock_result.price.current,
        outlook
    )
    
    assert isinstance(strategies, list)


def test_greeks_at_current_stock_price(stocks_service, options_service):
    """Test Greeks calculation using current stock price from stock analysis"""
    ticker = "AAPL"
    
    # Get current price from stock service
    stock_result = stocks_service.analyze_stock(ticker)
    current_price = stock_result.price.current
    
    # Get options contracts
    contracts = options_service.get_contracts_by_expiration(ticker, "2024-03-15")
    
    if contracts:
        contract = contracts[0]
        
        # Calculate Greeks using stock price
        greeks = options_service.calculate_greeks(
            spot_price=current_price,
            strike=contract.strike,
            time_to_expiry=0.25,
            volatility=contract.implied_volatility,
            option_type=contract.contract_type
        )
        
        assert greeks.delta != 0
        assert greeks.gamma >= 0
        assert greeks.vega >= 0


def test_volatility_comparison(stocks_service, options_service):
    """Test comparing historical volatility (stock) with IV (options)"""
    ticker = "AAPL"
    
    # Get historical volatility from stock analysis
    stock_result = stocks_service.analyze_stock(ticker)
    historical_vol = stock_result.risk.volatility if stock_result.risk else 0
    
    # Get IV from options
    iv_metrics = options_service.calculate_iv_metrics(ticker, "2024-03-15", 175.0)
    
    if "error" not in iv_metrics:
        implied_vol = iv_metrics["average_iv"]
        
        # Both should be positive
        assert historical_vol >= 0
        assert implied_vol >= 0


def test_covered_call_with_stock_position(stocks_service, options_service):
    """Test covered call strategy using stock analysis"""
    ticker = "AAPL"
    
    # Analyze stock
    stock_result = stocks_service.analyze_stock(ticker)
    stock_price = stock_result.price.current
    
    # Get ATM call for covered call
    contracts = options_service.get_contracts_by_expiration(ticker, "2024-03-15", "calls")
    
    if contracts:
        atm_call = min(contracts, key=lambda c: abs(c.strike - stock_price))
        
        # Calculate covered call
        cc_metrics = options_service.calculate_covered_call(
            stock_price=stock_price,
            strike=atm_call.strike,
            premium=atm_call.last_price
        )
        
        assert cc_metrics["strategy"] == "Covered Call"
        assert cc_metrics["premium_income"] > 0
        assert cc_metrics["breakeven"] < stock_price


def test_service_error_handling(mock_components):
    """Test both services handle errors consistently"""
    # Make fetcher raise error
    mock_components["fetcher"].get_stock_info.side_effect = Exception("Network error")
    mock_components["fetcher"].get_options_chain.side_effect = Exception("Network error")
    
    stocks = StocksAnalysisService(mock_components)
    options = OptionsAnalysisService(mock_components)
    
    # Both should raise appropriate errors
    with pytest.raises(Exception):
        stocks.analyze_stock("AAPL")
    
    with pytest.raises(Exception):
        options.analyze_options_chain("AAPL")


# ========== PERFORMANCE TESTS ==========

def test_stock_analysis_performance(stocks_service):
    """Test stock analysis completes in reasonable time"""
    start = time.time()
    
    result = stocks_service.analyze_stock("AAPL")
    
    elapsed = time.time() - start
    
    assert elapsed < 2.0  # Should complete in under 2 seconds with mocks
    assert result is not None


def test_options_analysis_performance(options_service):
    """Test options analysis completes in reasonable time"""
    start = time.time()
    
    chain = options_service.analyze_options_chain("SPY")
    
    elapsed = time.time() - start
    
    assert elapsed < 2.0  # Should complete in under 2 seconds with mocks
    assert chain is not None


def test_greeks_calculation_performance(options_service):
    """Test Greeks calculation is fast"""
    start = time.time()
    
    for _ in range(100):
        greeks = options_service.calculate_greeks(
            spot_price=100.0,
            strike=100.0,
            time_to_expiry=0.25,
            volatility=0.25,
            option_type="call"
        )
    
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # 100 calculations in under 1 second
    assert greeks is not None


def test_batch_analysis_performance(stocks_service):
    """Test analyzing multiple stocks"""
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    start = time.time()
    
    results = []
    for ticker in tickers:
        result = stocks_service.analyze_stock(ticker)
        results.append(result)
    
    elapsed = time.time() - start
    
    assert len(results) == 5
    assert elapsed < 10.0  # 5 stocks in under 10 seconds with mocks


# ========== EDGE CASES ==========

def test_missing_optional_components(mock_fetcher):
    """Test services work with minimal components"""
    minimal_components = {"fetcher": mock_fetcher}
    
    # Stocks service requires more components
    with pytest.raises(ValueError):
        StocksAnalysisService(minimal_components)
    
    # Options service should work
    options = OptionsAnalysisService(minimal_components)
    assert options is not None


def test_unusual_activity_with_stock_context(stocks_service, options_service):
    """Test unusual activity detection with stock context"""
    ticker = "AAPL"
    
    # Get stock analysis
    stock_result = stocks_service.analyze_stock(ticker)
    
    # Detect unusual options activity
    unusual = options_service.detect_unusual_activity(ticker, volume_threshold=1.5)
    
    # Should return list (may be empty with mock data)
    assert isinstance(unusual, list)


def test_multiple_expirations_analysis(options_service):
    """Test analyzing options across multiple expirations"""
    ticker = "SPY"
    
    chain = options_service.analyze_options_chain(ticker)
    
    # Test getting contracts for first expiration
    if chain.expiration_dates:
        exp_str = chain.expiration_dates[0].strftime("%Y-%m-%d")
        contracts = options_service.get_contracts_by_expiration(ticker, exp_str)
        
        assert isinstance(contracts, list)


def test_service_state_isolation(mock_components):
    """Test services don't share mutable state"""
    stocks1 = StocksAnalysisService(mock_components)
    stocks2 = StocksAnalysisService(mock_components)
    
    # Each should have independent state
    result1 = stocks1.analyze_stock("AAPL")
    result2 = stocks2.analyze_stock("AAPL")
    
    # Results should be equal but not same object
    assert result1.ticker == result2.ticker
    assert result1 is not result2


def test_concurrent_service_usage(mock_components):
    """Test both services can be used simultaneously"""
    stocks = StocksAnalysisService(mock_components)
    options = OptionsAnalysisService(mock_components)
    
    # Use both at same time
    stock_result = stocks.analyze_stock("AAPL")
    options_chain = options.analyze_options_chain("AAPL")
    
    # Both should complete successfully
    assert stock_result is not None
    assert options_chain is not None
    
    # Can still use each service afterward
    score = stocks.get_overall_score()
    strategies = options.get_strategy_recommendations("AAPL", 175.0, "neutral")
    
    assert isinstance(score, (int, float))
    assert isinstance(strategies, list)


# ========== DATA CONSISTENCY TESTS ==========

def test_price_consistency_across_services(stocks_service, options_service):
    """Test price data is consistent between services"""
    ticker = "AAPL"
    
    stock_result = stocks_service.analyze_stock(ticker)
    options_chain = options_service.analyze_options_chain(ticker)
    
    # Prices should match (within small tolerance for timing)
    assert abs(stock_result.price.current - options_chain.spot_price) < 0.01


def test_valuation_informed_options_strategies(stocks_service, options_service):
    """Test options strategies can use valuation data"""
    ticker = "AAPL"
    
    # Get stock valuation
    stock_result = stocks_service.analyze_stock(ticker)
    
    if stock_result.valuation:
        fair_value = stock_result.valuation.fair_value
        current_price = stock_result.price.current
        
        # Determine if stock is overvalued or undervalued
        if fair_value > current_price * 1.1:
            # Undervalued - bullish strategies
            outlook = "bullish"
        elif fair_value < current_price * 0.9:
            # Overvalued - bearish strategies
            outlook = "bearish"
        else:
            outlook = "neutral"
        
        strategies = options_service.get_strategy_recommendations(
            ticker, current_price, outlook
        )
        
        assert isinstance(strategies, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
