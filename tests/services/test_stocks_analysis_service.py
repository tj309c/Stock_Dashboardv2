"""
Unit Tests for StocksAnalysisService
Comprehensive tests with mock data - NO real API calls
Target: 80%+ code coverage
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from typing import Dict

from src.services.stocks_analysis_service import StocksAnalysisService
from src.core.types import (
    StockPrice, TechnicalIndicators, FundamentalMetrics,
    RiskMetrics, ValuationResult, TradeSignal, StockAnalysisResult,
    Signal, Trend, ValuationMethod
)
from src.core.errors import DataFetchError, AnalysisError, ValuationError


# ========== MOCK DATA FIXTURES ==========

@pytest.fixture
def mock_components():
    """Create mock components for service initialization"""
    components = {
        "fetcher": Mock(),
        "valuation": Mock(),
        "technical": Mock(),
        "goodbuy": Mock(),
        "sentiment": Mock()
    }
    return components


@pytest.fixture
def mock_stock_data():
    """Create mock stock data"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    df = pd.DataFrame({
        'Close': np.random.randn(100).cumsum() + 100,
        'Open': np.random.randn(100).cumsum() + 99,
        'High': np.random.randn(100).cumsum() + 102,
        'Low': np.random.randn(100).cumsum() + 98,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    return {
        "ticker": "AAPL",
        "timestamp": datetime.now().isoformat(),
        "stock_data": {
            "info": {
                "currentPrice": 175.50,
                "previousClose": 173.20,
                "regularMarketPrice": 175.50,
                "open": 174.00,
                "dayHigh": 176.80,
                "dayLow": 173.50,
                "volume": 50000000,
                "marketCap": 2800000000000,
                "fiftyTwoWeekHigh": 198.23,
                "fiftyTwoWeekLow": 124.17,
                "trailingPE": 28.5,
                "forwardPE": 25.2,
                "priceToBook": 45.3,
                "trailingEps": 6.15,
                "totalRevenue": 394000000000,
                "revenueGrowth": 0.08,
                "earningsGrowth": 0.12,
                "returnOnEquity": 1.47,
                "returnOnAssets": 0.22,
                "debtToEquity": 170.0,
                "currentRatio": 0.93,
                "profitMargins": 0.26,
                "operatingMargins": 0.30,
                "beta": 1.2,
                "sharesOutstanding": 16000000000,
                "symbol": "AAPL"
            },
            "history": df.to_dict()
        },
        "quote": {
            "price": 175.50,
            "change": 2.30,
            "change_pct": 1.33,
            "volume": 50000000,
            "open": 174.00,
            "high": 176.80,
            "low": 173.50
        },
        "fundamentals": {
            "cash_flow": pd.DataFrame({
                "Free Cash Flow": [90000000000, 92000000000, 95000000000, 99000000000]
            }).to_dict(),
            "balance_sheet": {},
            "income_statement": {}
        },
        "df": df,
        "sentiment": {
            "stocktwits": {"sentiment": "bullish", "score": 0.65},
            "news": {"sentiment": "positive", "score": 0.70}
        }
    }


@pytest.fixture
def mock_technical_analysis():
    """Mock technical analysis results"""
    return {
        "rsi": 65.5,
        "macd": 2.5,
        "macd_signal": 1.8,
        "macd_hist": 0.7,
        "bb_upper": 180.0,
        "bb_middle": 175.0,
        "bb_lower": 170.0,
        "sma_20": 174.50,
        "sma_50": 172.00,
        "sma_200": 168.50,
        "adx": 28.5,
        "obv": 5000000000,
        "atr": 3.5
    }


@pytest.fixture
def mock_valuation_result():
    """Mock valuation result"""
    return {
        "fair_value": 210.00,
        "current_price": 175.50,
        "upside": 19.66,
        "method": "DCF",
        "scenarios": {
            "conservative": 185.00,
            "base": 210.00,
            "optimistic": 235.00
        }
    }


@pytest.fixture
def mock_goodbuy_analysis():
    """Mock goodbuy analyzer results"""
    return {
        "total_score": 72.5,
        "confidence": "High confidence",
        "buy_range": {
            "low": 170.00,
            "high": 178.00
        },
        "target_price": 210.00,
        "signals": ["Undervalued", "Positive momentum", "Strong fundamentals"]
    }


# ========== SERVICE INITIALIZATION TESTS ==========

def test_service_initialization_success(mock_components):
    """Test successful service initialization"""
    service = StocksAnalysisService(mock_components)
    
    assert service.fetcher == mock_components["fetcher"]
    assert service.valuation_engine == mock_components["valuation"]
    assert service.technical_engine == mock_components["technical"]


def test_service_initialization_missing_components():
    """Test initialization fails with missing components"""
    with pytest.raises(ValueError, match="Missing required components"):
        StocksAnalysisService({})


def test_service_initialization_partial_components():
    """Test initialization with optional components"""
    components = {
        "fetcher": Mock(),
        "valuation": Mock(),
        "technical": Mock()
    }
    service = StocksAnalysisService(components)
    
    assert service.goodbuy_analyzer is None
    assert service.sentiment_analyzer is None


# ========== ANALYZE_STOCK TESTS ==========

def test_analyze_stock_success(
    mock_components, 
    mock_stock_data, 
    mock_technical_analysis,
    mock_valuation_result,
    mock_goodbuy_analysis
):
    """Test successful stock analysis"""
    # Setup mocks
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = mock_valuation_result
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = mock_goodbuy_analysis
    mock_components["sentiment"].get_stocktwits_sentiment.return_value = {"sentiment": "bullish"}
    mock_components["sentiment"].get_news_sentiment.return_value = {"sentiment": "positive"}
    
    service = StocksAnalysisService(mock_components)
    result = service.analyze_stock("AAPL")
    
    # Assertions
    assert isinstance(result, StockAnalysisResult)
    assert result.ticker == "AAPL"
    assert isinstance(result.price, StockPrice)
    assert isinstance(result.technical, TechnicalIndicators)
    assert isinstance(result.fundamentals, FundamentalMetrics)
    assert isinstance(result.risk, RiskMetrics)
    assert isinstance(result.valuation, ValuationResult)
    assert len(result.signals) > 0
    assert isinstance(result.signals[0], TradeSignal)


def test_analyze_stock_data_fetch_error(mock_components):
    """Test analysis handles data fetch errors"""
    mock_components["fetcher"].get_stock_data.return_value = {"error": "API error"}
    
    service = StocksAnalysisService(mock_components)
    
    with pytest.raises(DataFetchError):
        service.analyze_stock("INVALID")


def test_analyze_stock_without_sentiment(
    mock_components,
    mock_stock_data,
    mock_technical_analysis,
    mock_valuation_result,
    mock_goodbuy_analysis
):
    """Test analysis without sentiment data"""
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = mock_valuation_result
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = mock_goodbuy_analysis
    
    service = StocksAnalysisService(mock_components)
    result = service.analyze_stock("AAPL", include_sentiment=False)
    
    assert isinstance(result, StockAnalysisResult)
    assert result.ticker == "AAPL"


# ========== PRICE EXTRACTION TESTS ==========

def test_extract_stock_price(mock_components, mock_stock_data):
    """Test StockPrice extraction"""
    service = StocksAnalysisService(mock_components)
    
    info = mock_stock_data["stock_data"]["info"]
    quote = mock_stock_data["quote"]
    
    price = service._extract_stock_price(info, quote)
    
    assert isinstance(price, StockPrice)
    assert price.current == 175.50
    assert price.day_change_percent > 0
    assert price.week_52_high == 198.23
    assert price.week_52_low == 124.17
    assert price.volume == 50000000


# ========== TECHNICAL INDICATORS TESTS ==========

def test_calculate_technical_indicators(
    mock_components,
    mock_stock_data,
    mock_technical_analysis
):
    """Test TechnicalIndicators calculation"""
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    
    service = StocksAnalysisService(mock_components)
    df = mock_stock_data["df"]
    info = mock_stock_data["stock_data"]["info"]
    
    technical = service._calculate_technical_indicators(df, info)
    
    assert isinstance(technical, TechnicalIndicators)
    assert technical.rsi == 65.5
    assert technical.macd == 2.5
    assert technical.sma_20 == 174.50
    assert technical.adx == 28.5


def test_calculate_technical_indicators_empty_df(mock_components):
    """Test technical indicators with empty DataFrame"""
    service = StocksAnalysisService(mock_components)
    
    from src.core.errors import InsufficientDataError
    with pytest.raises(InsufficientDataError):
        service._calculate_technical_indicators(pd.DataFrame(), {})


def test_calculate_technical_indicators_fallback(mock_components, mock_stock_data):
    """Test technical indicators fallback on error"""
    mock_components["technical"].analyze.side_effect = Exception("Calculation error")
    
    service = StocksAnalysisService(mock_components)
    df = mock_stock_data["df"]
    
    technical = service._calculate_technical_indicators(df, {})
    
    # Should return neutral indicators
    assert isinstance(technical, TechnicalIndicators)
    assert technical.rsi == 50.0  # Neutral
    assert technical.macd == 0.0


# ========== FUNDAMENTALS TESTS ==========

def test_extract_fundamentals(mock_components, mock_stock_data):
    """Test FundamentalMetrics extraction"""
    service = StocksAnalysisService(mock_components)
    
    info = mock_stock_data["stock_data"]["info"]
    fundamentals = mock_stock_data["fundamentals"]
    
    fund = service._extract_fundamentals(info, fundamentals)
    
    assert isinstance(fund, FundamentalMetrics)
    assert fund.pe_ratio == 28.5
    assert fund.eps == 6.15
    assert fund.revenue_growth == 0.08
    assert fund.roe == 1.47
    assert fund.debt_to_equity == 170.0


# ========== RISK METRICS TESTS ==========

def test_calculate_risk_metrics(mock_components, mock_stock_data):
    """Test RiskMetrics calculation"""
    service = StocksAnalysisService(mock_components)
    
    df = mock_stock_data["df"]
    info = mock_stock_data["stock_data"]["info"]
    fundamentals = FundamentalMetrics(pe_ratio=28.5)
    
    risk = service._calculate_risk_metrics(df, info, fundamentals)
    
    assert isinstance(risk, RiskMetrics)
    assert risk.beta == 1.2
    assert risk.volatility > 0
    assert risk.max_drawdown < 0
    assert risk.sharpe_ratio is not None


def test_calculate_risk_metrics_empty_df(mock_components, mock_stock_data):
    """Test risk metrics with empty DataFrame (uses estimates)"""
    service = StocksAnalysisService(mock_components)
    
    info = mock_stock_data["stock_data"]["info"]
    fundamentals = FundamentalMetrics()
    
    risk = service._calculate_risk_metrics(pd.DataFrame(), info, fundamentals)
    
    assert isinstance(risk, RiskMetrics)
    assert risk.beta == 1.2  # From info


# ========== VALUATION TESTS ==========

def test_calculate_valuation(mock_components, mock_stock_data, mock_valuation_result):
    """Test ValuationResult calculation"""
    mock_components["valuation"].calculate_valuation.return_value = mock_valuation_result
    
    service = StocksAnalysisService(mock_components)
    
    fundamentals = mock_stock_data["fundamentals"]
    info = mock_stock_data["stock_data"]["info"]
    
    valuation = service._calculate_valuation(fundamentals, info)
    
    assert isinstance(valuation, ValuationResult)
    assert valuation.fair_value == 210.00
    assert valuation.upside_percent > 0
    assert valuation.method == ValuationMethod.DCF
    assert valuation.confidence > 0


def test_calculate_valuation_error(mock_components, mock_stock_data):
    """Test valuation handles errors"""
    mock_components["valuation"].calculate_valuation.return_value = {
        "error": "Insufficient data"
    }
    
    service = StocksAnalysisService(mock_components)
    
    with pytest.raises(ValuationError):
        service._calculate_valuation(mock_stock_data["fundamentals"], {})


# ========== TRADE SIGNALS TESTS ==========

def test_generate_trade_signals_with_goodbuy(
    mock_components,
    mock_stock_data,
    mock_goodbuy_analysis
):
    """Test trade signal generation with goodbuy analyzer"""
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = mock_goodbuy_analysis
    
    service = StocksAnalysisService(mock_components)
    
    price = StockPrice(current=175.50, day_change_percent=1.33)
    technical = TechnicalIndicators(rsi=65.5)
    fundamental = FundamentalMetrics(pe_ratio=28.5)
    valuation = ValuationResult(fair_value=210.00, upside_percent=19.66)
    
    signals = service._generate_trade_signals(
        price, technical, fundamental, valuation,
        mock_stock_data["stock_data"]["info"],
        mock_stock_data["df"]
    )
    
    assert len(signals) > 0
    assert isinstance(signals[0], TradeSignal)
    assert signals[0].confidence > 0
    assert signals[0].entry_price > 0


def test_generate_trade_signals_without_goodbuy(mock_components):
    """Test trade signal generation without goodbuy analyzer (fallback)"""
    mock_components["goodbuy"] = None
    
    service = StocksAnalysisService(mock_components)
    
    price = StockPrice(current=175.50, day_change_percent=1.33)
    technical = TechnicalIndicators(rsi=65.5, macd=2.5, macd_signal=1.8)
    fundamental = FundamentalMetrics(pe_ratio=28.5)
    valuation = ValuationResult(fair_value=210.00, upside_percent=19.66)
    
    signals = service._generate_trade_signals(
        price, technical, fundamental, valuation,
        {"symbol": "AAPL"},
        pd.DataFrame()
    )
    
    assert len(signals) > 0
    signal = signals[0]
    assert isinstance(signal, TradeSignal)
    assert signal.signal in [Signal.BUY, Signal.SELL, Signal.HOLD]


def test_determine_primary_signal_strong_buy(mock_components, mock_goodbuy_analysis):
    """Test strong buy signal determination"""
    service = StocksAnalysisService(mock_components)
    
    buy_analysis = {"total_score": 75}
    valuation = ValuationResult(fair_value=210.00, upside_percent=20.0)
    technical = TechnicalIndicators(rsi=55.0)
    fundamental = FundamentalMetrics()
    
    signal = service._determine_primary_signal(buy_analysis, valuation, technical, fundamental)
    
    assert signal == Signal.STRONG_BUY


def test_determine_primary_signal_sell(mock_components):
    """Test sell signal determination"""
    service = StocksAnalysisService(mock_components)
    
    buy_analysis = {"total_score": 35}
    valuation = ValuationResult(fair_value=150.00, upside_percent=-15.0)
    technical = TechnicalIndicators(rsi=75.0)  # Overbought
    fundamental = FundamentalMetrics()
    
    signal = service._determine_primary_signal(buy_analysis, valuation, technical, fundamental)
    
    assert signal == Signal.SELL


# ========== SUMMARY METHODS TESTS ==========

def test_get_technical_summary(mock_components, mock_stock_data, mock_technical_analysis):
    """Test technical summary generation"""
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = {
        "fair_value": 210.00, "method": "DCF"
    }
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = {
        "total_score": 70, "buy_range": {"low": 170}, "target_price": 210
    }
    
    service = StocksAnalysisService(mock_components)
    analysis = service.analyze_stock("AAPL")
    
    summary = service.get_technical_summary(analysis)
    
    assert "trend" in summary
    assert "momentum_score" in summary
    assert "is_overbought" in summary
    assert "rsi" in summary
    assert summary["rsi"] == 65.5


def test_get_valuation_summary(mock_components, mock_stock_data, mock_technical_analysis):
    """Test valuation summary generation"""
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = {
        "fair_value": 210.00, "method": "DCF"
    }
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = {
        "total_score": 70, "buy_range": {"low": 170}, "target_price": 210
    }
    
    service = StocksAnalysisService(mock_components)
    analysis = service.analyze_stock("AAPL")
    
    summary = service.get_valuation_summary(analysis)
    
    assert "recommendation" in summary
    assert "is_undervalued" in summary
    assert "fair_value" in summary
    assert "upside_percent" in summary
    assert summary["fair_value"] == 210.00


def test_get_overall_score(mock_components, mock_stock_data, mock_technical_analysis):
    """Test overall score calculation"""
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = {
        "fair_value": 210.00, "method": "DCF"
    }
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = {
        "total_score": 70, "buy_range": {"low": 170}, "target_price": 210
    }
    
    service = StocksAnalysisService(mock_components)
    analysis = service.analyze_stock("AAPL")
    
    score = service.get_overall_score(analysis)
    
    assert isinstance(score, float)
    assert 0 <= score <= 100


# ========== HELPER METHODS TESTS ==========

def test_get_sma_alignment_bullish(mock_components):
    """Test SMA alignment detection - bullish"""
    service = StocksAnalysisService(mock_components)
    
    technical = TechnicalIndicators(
        sma_20=180.0,
        sma_50=175.0,
        sma_200=170.0
    )
    
    alignment = service._get_sma_alignment(technical)
    assert alignment == "BULLISH_ALIGNED"


def test_get_sma_alignment_bearish(mock_components):
    """Test SMA alignment detection - bearish"""
    service = StocksAnalysisService(mock_components)
    
    technical = TechnicalIndicators(
        sma_20=170.0,
        sma_50=175.0,
        sma_200=180.0
    )
    
    alignment = service._get_sma_alignment(technical)
    assert alignment == "BEARISH_ALIGNED"


def test_get_sma_alignment_mixed(mock_components):
    """Test SMA alignment detection - mixed"""
    service = StocksAnalysisService(mock_components)
    
    technical = TechnicalIndicators(
        sma_20=175.0,
        sma_50=180.0,
        sma_200=170.0
    )
    
    alignment = service._get_sma_alignment(technical)
    assert alignment == "MIXED"


# ========== INTEGRATION TESTS ==========

def test_full_analysis_pipeline(
    mock_components,
    mock_stock_data,
    mock_technical_analysis,
    mock_valuation_result,
    mock_goodbuy_analysis
):
    """Test complete analysis pipeline end-to-end"""
    # Setup all mocks
    mock_components["fetcher"].get_stock_data.return_value = mock_stock_data["stock_data"]
    mock_components["fetcher"].get_realtime_quote.return_value = mock_stock_data["quote"]
    mock_components["fetcher"].get_fundamentals.return_value = mock_stock_data["fundamentals"]
    mock_components["technical"].analyze.return_value = mock_technical_analysis
    mock_components["valuation"].calculate_valuation.return_value = mock_valuation_result
    mock_components["goodbuy"].analyze_buy_opportunity.return_value = mock_goodbuy_analysis
    mock_components["sentiment"].get_stocktwits_sentiment.return_value = {"sentiment": "bullish"}
    mock_components["sentiment"].get_news_sentiment.return_value = {"sentiment": "positive"}
    
    service = StocksAnalysisService(mock_components)
    
    # Run full analysis
    analysis = service.analyze_stock("AAPL")
    
    # Get all summaries
    signals = service.calculate_buy_signals(analysis)
    tech_summary = service.get_technical_summary(analysis)
    val_summary = service.get_valuation_summary(analysis)
    overall_score = service.get_overall_score(analysis)
    
    # Assertions
    assert isinstance(analysis, StockAnalysisResult)
    assert len(signals) > 0
    assert isinstance(tech_summary, dict)
    assert isinstance(val_summary, dict)
    assert isinstance(overall_score, float)
    assert 0 <= overall_score <= 100


# ========== RUN DEMO ==========

if __name__ == "__main__":
    print("🧪 StocksAnalysisService Unit Tests")
    print("=" * 60)
    print()
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
