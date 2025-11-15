"""
Unit Tests for Core Types

Tests all dataclasses in core/types.py to ensure:
- Proper initialization
- Validation logic
- Property methods
- Edge cases

Author: Refactoring Team
Date: 2024-11
Phase: 1 (Foundation)
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from core.types import (
    StockData,
    ValuationResult,
    MonteCarloResult,
    Signal,
    TechnicalAnalysis,
    SentimentResult,
    RiskMetrics,
    PortfolioPosition,
    Portfolio,
    AnalysisResult,
)


class TestStockData:
    """Test StockData dataclass"""
    
    def test_valid_stock_data(self):
        """Test creating valid StockData"""
        data = StockData(
            ticker="AAPL",
            price=150.0,
            volume=50_000_000,
            market_cap=2_500_000_000_000,
            beta=1.2,
            pe_ratio=25.0,
            dividend_yield=0.005
        )
        
        assert data.ticker == "AAPL"
        assert data.price == 150.0
        assert data.volume == 50_000_000
    
    def test_negative_price_raises_error(self):
        """Test that negative price raises ValueError"""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            StockData(
                ticker="AAPL",
                price=-10.0,
                volume=1000,
                market_cap=1_000_000,
                beta=1.0
            )
    
    def test_negative_volume_raises_error(self):
        """Test that negative volume raises ValueError"""
        with pytest.raises(ValueError, match="Volume cannot be negative"):
            StockData(
                ticker="AAPL",
                price=100.0,
                volume=-1000,
                market_cap=1_000_000,
                beta=1.0
            )
    
    def test_optional_fields(self):
        """Test that optional fields can be None"""
        data = StockData(
            ticker="AAPL",
            price=150.0,
            volume=50_000_000,
            market_cap=2_500_000_000_000,
            beta=1.2
        )
        
        assert data.pe_ratio is None
        assert data.dividend_yield is None
    
    def test_default_timestamp(self):
        """Test that timestamp is set automatically"""
        data = StockData(
            ticker="AAPL",
            price=150.0,
            volume=50_000_000,
            market_cap=2_500_000_000_000,
            beta=1.2
        )
        
        assert isinstance(data.timestamp, datetime)
        assert (datetime.now() - data.timestamp).seconds < 1


class TestValuationResult:
    """Test ValuationResult dataclass"""
    
    def test_valid_valuation_result(self):
        """Test creating valid ValuationResult"""
        result = ValuationResult(
            method="DCF",
            fair_value=180.0,
            current_price=150.0,
            upside_percent=20.0,
            confidence=85.0,
            assumptions={"growth_rate": 0.10, "wacc": 0.08},
            breakdown={"pv_cash_flows": 100.0, "terminal_value": 80.0}
        )
        
        assert result.method == "DCF"
        assert result.fair_value == 180.0
        assert result.upside_percent == 20.0
    
    def test_is_undervalued_property(self):
        """Test is_undervalued property"""
        # Undervalued
        result1 = ValuationResult(
            method="DCF",
            fair_value=180.0,
            current_price=150.0,
            upside_percent=20.0,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result1.is_undervalued is True
        
        # Overvalued
        result2 = ValuationResult(
            method="DCF",
            fair_value=150.0,
            current_price=180.0,
            upside_percent=-16.7,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result2.is_undervalued is False
    
    def test_recommendation_property(self):
        """Test recommendation property"""
        # Strong Buy (>20% upside)
        result1 = ValuationResult(
            method="DCF",
            fair_value=180.0,
            current_price=150.0,
            upside_percent=25.0,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result1.recommendation == "Strong Buy"
        
        # Buy (10-20% upside)
        result2 = ValuationResult(
            method="DCF",
            fair_value=165.0,
            current_price=150.0,
            upside_percent=15.0,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result2.recommendation == "Buy"
        
        # Hold (-10 to +10%)
        result3 = ValuationResult(
            method="DCF",
            fair_value=155.0,
            current_price=150.0,
            upside_percent=5.0,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result3.recommendation == "Hold"
        
        # Strong Sell (< -20%)
        result4 = ValuationResult(
            method="DCF",
            fair_value=100.0,
            current_price=150.0,
            upside_percent=-33.3,
            confidence=85.0,
            assumptions={},
            breakdown={}
        )
        assert result4.recommendation == "Strong Sell"


class TestSignal:
    """Test Signal dataclass"""
    
    def test_valid_signal(self):
        """Test creating valid Signal"""
        signal = Signal(
            type="buy",
            strength=85.0,
            reason="RSI oversold + MACD bullish crossover"
        )
        
        assert signal.type == "buy"
        assert signal.strength == 85.0
        assert "RSI" in signal.reason
    
    def test_invalid_signal_type(self):
        """Test that invalid signal type raises ValueError"""
        with pytest.raises(ValueError, match="Invalid signal type"):
            Signal(
                type="invalid",
                strength=50.0,
                reason="Test"
            )
    
    def test_invalid_strength_raises_error(self):
        """Test that strength outside 0-100 raises ValueError"""
        with pytest.raises(ValueError, match="Strength must be 0-100"):
            Signal(
                type="buy",
                strength=150.0,
                reason="Test"
            )
        
        with pytest.raises(ValueError, match="Strength must be 0-100"):
            Signal(
                type="buy",
                strength=-10.0,
                reason="Test"
            )


class TestTechnicalAnalysis:
    """Test TechnicalAnalysis dataclass"""
    
    def test_valid_technical_analysis(self):
        """Test creating valid TechnicalAnalysis"""
        signals = [
            Signal(type="buy", strength=70.0, reason="RSI oversold"),
            Signal(type="hold", strength=50.0, reason="MACD neutral")
        ]
        
        analysis = TechnicalAnalysis(
            indicators={"RSI": 28.5, "MACD": -1.2, "ADX": 35.0},
            signals=signals,
            support_levels=[145.0, 142.0, 138.0],
            resistance_levels=[155.0, 158.0, 162.0],
            trend="bullish"
        )
        
        assert analysis.trend == "bullish"
        assert len(analysis.signals) == 2
        assert analysis.rsi == 28.5
    
    def test_rsi_property(self):
        """Test RSI property"""
        analysis = TechnicalAnalysis(
            indicators={"RSI": 65.5},
            signals=[],
            support_levels=[],
            resistance_levels=[],
            trend="neutral"
        )
        
        assert analysis.rsi == 65.5
    
    def test_is_oversold_property(self):
        """Test is_oversold property"""
        # Oversold (RSI < 30)
        analysis1 = TechnicalAnalysis(
            indicators={"RSI": 25.0},
            signals=[],
            support_levels=[],
            resistance_levels=[],
            trend="neutral"
        )
        assert analysis1.is_oversold is True
        
        # Not oversold
        analysis2 = TechnicalAnalysis(
            indicators={"RSI": 45.0},
            signals=[],
            support_levels=[],
            resistance_levels=[],
            trend="neutral"
        )
        assert analysis2.is_oversold is False
    
    def test_is_overbought_property(self):
        """Test is_overbought property"""
        # Overbought (RSI > 70)
        analysis1 = TechnicalAnalysis(
            indicators={"RSI": 75.0},
            signals=[],
            support_levels=[],
            resistance_levels=[],
            trend="neutral"
        )
        assert analysis1.is_overbought is True
        
        # Not overbought
        analysis2 = TechnicalAnalysis(
            indicators={"RSI": 55.0},
            signals=[],
            support_levels=[],
            resistance_levels=[],
            trend="neutral"
        )
        assert analysis2.is_overbought is False


class TestSentimentResult:
    """Test SentimentResult dataclass"""
    
    def test_valid_sentiment_result(self):
        """Test creating valid SentimentResult"""
        sentiment = SentimentResult(
            overall_score=0.65,
            news_score=0.70,
            social_score=0.60,
            analyst_score=0.65,
            num_sources=15,
            top_keywords=["bullish", "growth", "innovation"]
        )
        
        assert sentiment.overall_score == 0.65
        assert sentiment.num_sources == 15
    
    def test_sentiment_label_property(self):
        """Test sentiment_label property"""
        # Very Positive
        s1 = SentimentResult(0.8, 0.8, 0.8, 0.8, 10, [])
        assert s1.sentiment_label == "Very Positive"
        
        # Positive
        s2 = SentimentResult(0.3, 0.3, 0.3, 0.3, 10, [])
        assert s2.sentiment_label == "Positive"
        
        # Neutral
        s3 = SentimentResult(0.0, 0.0, 0.0, 0.0, 10, [])
        assert s3.sentiment_label == "Neutral"
        
        # Negative
        s4 = SentimentResult(-0.3, -0.3, -0.3, -0.3, 10, [])
        assert s4.sentiment_label == "Negative"
        
        # Very Negative
        s5 = SentimentResult(-0.8, -0.8, -0.8, -0.8, 10, [])
        assert s5.sentiment_label == "Very Negative"


class TestRiskMetrics:
    """Test RiskMetrics dataclass"""
    
    def test_valid_risk_metrics(self):
        """Test creating valid RiskMetrics"""
        metrics = RiskMetrics(
            beta=1.2,
            sharpe_ratio=1.5,
            sortino_ratio=1.8,
            volatility=0.25,
            max_drawdown=-15.5,
            var_95=-8.5,
            cvar_95=-12.0
        )
        
        assert metrics.beta == 1.2
        assert metrics.sharpe_ratio == 1.5
        assert metrics.volatility == 0.25
    
    def test_risk_level_property(self):
        """Test risk_level property"""
        # Low risk
        m1 = RiskMetrics(1.0, 1.5, 1.8, 0.10, -5.0, -3.0, -4.0)
        assert m1.risk_level == "Low"
        
        # Medium risk
        m2 = RiskMetrics(1.0, 1.5, 1.8, 0.20, -10.0, -6.0, -8.0)
        assert m2.risk_level == "Medium"
        
        # High risk
        m3 = RiskMetrics(1.5, 1.0, 1.2, 0.40, -20.0, -12.0, -16.0)
        assert m3.risk_level == "High"
        
        # Very High risk
        m4 = RiskMetrics(2.0, 0.5, 0.8, 0.60, -30.0, -18.0, -24.0)
        assert m4.risk_level == "Very High"


class TestPortfolio:
    """Test Portfolio dataclass"""
    
    def test_valid_portfolio(self):
        """Test creating valid Portfolio"""
        positions = [
            PortfolioPosition("AAPL", 100, 150, 155, 15500, 500, 3.33, 0.4),
            PortfolioPosition("MSFT", 50, 300, 310, 15500, 500, 3.33, 0.4),
            PortfolioPosition("GOOGL", 20, 120, 125, 2500, 100, 4.17, 0.2),
        ]
        
        portfolio = Portfolio(
            positions=positions,
            total_value=33500,
            total_cost=32400,
            total_pnl=1100,
            total_pnl_percent=3.40
        )
        
        assert portfolio.num_positions == 3
        assert portfolio.total_value == 33500
    
    def test_largest_position_property(self):
        """Test largest_position property"""
        positions = [
            PortfolioPosition("AAPL", 100, 150, 155, 15500, 500, 3.33, 0.4),
            PortfolioPosition("MSFT", 50, 300, 310, 15500, 500, 3.33, 0.5),  # Largest
            PortfolioPosition("GOOGL", 20, 120, 125, 2500, 100, 4.17, 0.1),
        ]
        
        portfolio = Portfolio(
            positions=positions,
            total_value=33500,
            total_cost=32400,
            total_pnl=1100,
            total_pnl_percent=3.40
        )
        
        largest = portfolio.largest_position
        assert largest is not None
        assert largest.ticker == "MSFT"
        assert largest.weight == 0.5
    
    def test_empty_portfolio(self):
        """Test portfolio with no positions"""
        portfolio = Portfolio(
            positions=[],
            total_value=0,
            total_cost=0,
            total_pnl=0,
            total_pnl_percent=0
        )
        
        assert portfolio.num_positions == 0
        assert portfolio.largest_position is None


class TestMonteCarloResult:
    """Test MonteCarloResult dataclass"""
    
    def test_valid_monte_carlo_result(self):
        """Test creating valid MonteCarloResult"""
        np.random.seed(42)
        values = np.random.normal(180, 20, 1000)
        
        result = MonteCarloResult(
            mean_fair_value=180.0,
            median_fair_value=179.5,
            std_dev=20.0,
            num_simulations=1000,
            confidence_intervals={
                0.50: (170.0, 190.0),
                0.80: (160.0, 200.0),
                0.90: (150.0, 210.0)
            },
            percentiles={
                5: 147.0,
                25: 166.0,
                50: 179.5,
                75: 193.0,
                95: 213.0
            },
            all_values=values
        )
        
        assert result.mean_fair_value == 180.0
        assert result.num_simulations == 1000
        assert len(result.all_values) == 1000
    
    def test_get_probability_above(self):
        """Test get_probability_above method"""
        np.random.seed(42)
        values = np.random.normal(180, 20, 1000)
        
        result = MonteCarloResult(
            mean_fair_value=180.0,
            median_fair_value=179.5,
            std_dev=20.0,
            num_simulations=1000,
            confidence_intervals={},
            percentiles={},
            all_values=values
        )
        
        # Should be ~50% at mean
        prob_above_mean = result.get_probability_above(180.0)
        assert 0.40 < prob_above_mean < 0.60
        
        # Should be high probability above low value
        prob_above_low = result.get_probability_above(140.0)
        assert prob_above_low > 0.90
        
        # Should be low probability above high value
        prob_above_high = result.get_probability_above(220.0)
        assert prob_above_high < 0.10


class TestAnalysisResult:
    """Test AnalysisResult dataclass"""
    
    def test_overall_recommendation(self):
        """Test overall_recommendation property"""
        # Create mock components
        stock_data = StockData("AAPL", 150.0, 50000000, 2500000000000, 1.2)
        
        valuation = ValuationResult(
            "DCF", 180.0, 150.0, 20.0, 85.0, {}, {}
        )
        
        technical = TechnicalAnalysis(
            {"RSI": 65.0}, [], [], [], "bullish"
        )
        
        sentiment = SentimentResult(0.6, 0.6, 0.6, 0.6, 10, [])
        
        risk = RiskMetrics(1.2, 1.5, 1.8, 0.25, -15.0, -8.0, -12.0)
        
        # All positive signals
        result = AnalysisResult(
            stock_data=stock_data,
            valuation=valuation,
            technical=technical,
            sentiment=sentiment,
            risk=risk
        )
        
        assert result.overall_recommendation in ["Strong Buy", "Buy"]
    
    def test_confidence_score(self):
        """Test confidence_score property"""
        stock_data = StockData("AAPL", 150.0, 50000000, 2500000000000, 1.2)
        risk = RiskMetrics(1.2, 1.5, 1.8, 0.25, -15.0, -8.0, -12.0)
        sentiment = SentimentResult(0.6, 0.6, 0.6, 0.6, 10, [])
        
        # Agreeing signals (positive valuation + bullish technical)
        valuation1 = ValuationResult("DCF", 180.0, 150.0, 20.0, 80.0, {}, {})
        technical1 = TechnicalAnalysis({}, [], [], [], "bullish")
        
        result1 = AnalysisResult(
            stock_data, valuation1, technical1, sentiment, risk
        )
        
        # Confidence should increase when signals agree
        assert result1.confidence_score > 80.0
        
        # Disagreeing signals (positive valuation + bearish technical)
        valuation2 = ValuationResult("DCF", 180.0, 150.0, 20.0, 80.0, {}, {})
        technical2 = TechnicalAnalysis({}, [], [], [], "bearish")
        
        result2 = AnalysisResult(
            stock_data, valuation2, technical2, sentiment, risk
        )
        
        # Confidence should decrease when signals disagree
        assert result2.confidence_score < 80.0
