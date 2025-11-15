"""
Core Type Definitions

This module defines all core data structures using dataclasses for type safety.
Replaces magic dictionaries with typed, validated data structures.

Author: Refactoring Team
Date: 2024-11
Phase: 1 (Foundation)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np


# ==================== Stock Data ====================

@dataclass
class StockData:
    """
    Comprehensive stock data container.
    
    Replaces magic dictionaries with typed structure.
    Provides IDE autocomplete and type checking.
    """
    ticker: str
    price: float
    volume: int
    market_cap: float
    beta: float
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    history: pd.DataFrame = field(default_factory=pd.DataFrame)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate data after initialization"""
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")
        if self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")
        if self.market_cap < 0:
            raise ValueError(f"Market cap cannot be negative: {self.market_cap}")


# ==================== Valuation ====================

@dataclass
class ValuationResult:
    """
    Valuation calculation result.
    
    Contains all valuation outputs including fair value,
    upside potential, confidence, and detailed breakdown.
    """
    method: str  # "DCF", "Multiples", "DDM", "Zero-FCF"
    fair_value: float
    current_price: float
    upside_percent: float
    confidence: float  # 0-100
    assumptions: Dict[str, Any]
    breakdown: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_undervalued(self) -> bool:
        """Check if stock is undervalued"""
        return self.upside_percent > 0
    
    @property
    def recommendation(self) -> str:
        """Generate recommendation based on upside"""
        if self.upside_percent > 20:
            return "Strong Buy"
        elif self.upside_percent > 10:
            return "Buy"
        elif self.upside_percent > -10:
            return "Hold"
        elif self.upside_percent > -20:
            return "Sell"
        else:
            return "Strong Sell"


@dataclass
class MonteCarloResult:
    """
    Monte Carlo simulation result.
    
    Contains probability distribution of fair values
    with confidence intervals and percentile analysis.
    """
    mean_fair_value: float
    median_fair_value: float
    std_dev: float
    num_simulations: int
    confidence_intervals: Dict[float, Tuple[float, float]]  # {0.50: (low, high), ...}
    percentiles: Dict[int, float]  # {5: value, 10: value, ..., 95: value}
    all_values: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_probability_above(self, price: float) -> float:
        """Calculate probability that fair value is above given price"""
        return (self.all_values > price).mean()


# ==================== Technical Analysis ====================

@dataclass
class Signal:
    """
    Buy/sell/hold signal.
    
    Generated from technical analysis, fundamental analysis,
    or combination of factors.
    """
    type: str  # "buy", "sell", "hold"
    strength: float  # 0-100
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate signal"""
        if self.type not in ["buy", "sell", "hold"]:
            raise ValueError(f"Invalid signal type: {self.type}")
        if not 0 <= self.strength <= 100:
            raise ValueError(f"Strength must be 0-100: {self.strength}")


@dataclass
class TechnicalAnalysis:
    """
    Technical analysis results.
    
    Contains all technical indicators, signals,
    support/resistance levels, and overall trend.
    """
    indicators: Dict[str, float]  # {"RSI": 65.3, "MACD": 2.1, ...}
    signals: List[Signal]
    support_levels: List[float]
    resistance_levels: List[float]
    trend: str  # "bullish", "bearish", "neutral"
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def rsi(self) -> Optional[float]:
        """Get RSI value"""
        return self.indicators.get("RSI")
    
    @property
    def macd(self) -> Optional[float]:
        """Get MACD value"""
        return self.indicators.get("MACD")
    
    @property
    def is_oversold(self) -> bool:
        """Check if RSI indicates oversold condition"""
        rsi = self.rsi
        return rsi is not None and rsi < 30
    
    @property
    def is_overbought(self) -> bool:
        """Check if RSI indicates overbought condition"""
        rsi = self.rsi
        return rsi is not None and rsi > 70


# ==================== Sentiment Analysis ====================

@dataclass
class SentimentResult:
    """
    Sentiment analysis result.
    
    Aggregates sentiment from news, social media,
    and other sources into overall sentiment score.
    """
    overall_score: float  # -1.0 (very negative) to 1.0 (very positive)
    news_score: float
    social_score: float
    analyst_score: float
    num_sources: int
    top_keywords: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def sentiment_label(self) -> str:
        """Get human-readable sentiment label"""
        if self.overall_score > 0.5:
            return "Very Positive"
        elif self.overall_score > 0.2:
            return "Positive"
        elif self.overall_score > -0.2:
            return "Neutral"
        elif self.overall_score > -0.5:
            return "Negative"
        else:
            return "Very Negative"


# ==================== Risk Metrics ====================

@dataclass
class RiskMetrics:
    """
    Risk and volatility metrics.
    
    Contains beta, Sharpe ratio, volatility,
    max drawdown, and other risk measures.
    """
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    volatility: float  # Annualized
    max_drawdown: float  # As percentage
    var_95: float  # Value at Risk (95% confidence)
    cvar_95: float  # Conditional VaR
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def risk_level(self) -> str:
        """Categorize risk level"""
        if self.volatility < 0.15:
            return "Low"
        elif self.volatility < 0.30:
            return "Medium"
        elif self.volatility < 0.50:
            return "High"
        else:
            return "Very High"


# ==================== Portfolio ====================

@dataclass
class PortfolioPosition:
    """
    Single portfolio position.
    
    Represents one stock holding in a portfolio
    with cost basis, current value, and P&L.
    """
    ticker: str
    shares: float
    avg_cost: float
    current_price: float
    market_value: float
    pnl: float
    pnl_percent: float
    weight: float  # Portfolio weight (0-1)
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost basis"""
        return self.shares * self.avg_cost


@dataclass
class Portfolio:
    """
    Complete portfolio container.
    
    Contains all positions, portfolio-level metrics,
    and optimization results.
    """
    positions: List[PortfolioPosition]
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_percent: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def num_positions(self) -> int:
        """Number of positions in portfolio"""
        return len(self.positions)
    
    @property
    def largest_position(self) -> Optional[PortfolioPosition]:
        """Get largest position by weight"""
        if not self.positions:
            return None
        return max(self.positions, key=lambda p: p.weight)


@dataclass
class PortfolioMetrics:
    """
    Portfolio-level performance metrics.
    
    Contains risk-adjusted returns, diversification
    metrics, and performance attribution.
    """
    total_value: float
    total_cost: float
    total_pnl: float
    sharpe_ratio: float
    beta: float
    volatility: float
    max_drawdown: float
    correlation_matrix: pd.DataFrame = field(default_factory=pd.DataFrame)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """
    Portfolio optimization result.
    
    Contains optimal weights, expected return,
    risk, and efficient frontier data.
    """
    optimal_weights: Dict[str, float]  # {ticker: weight}
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    efficient_frontier: pd.DataFrame = field(default_factory=pd.DataFrame)
    timestamp: datetime = field(default_factory=datetime.now)


# ==================== Analysis Result ====================

@dataclass
class AnalysisResult:
    """
    Complete stock analysis result.
    
    Combines all analysis types into single container.
    Returned by AnalysisService.analyze_stock()
    """
    stock_data: StockData
    valuation: ValuationResult
    technical: TechnicalAnalysis
    sentiment: SentimentResult
    risk: RiskMetrics
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_recommendation(self) -> str:
        """
        Generate overall recommendation combining all factors.
        
        Considers valuation, technical trend, and sentiment.
        """
        # Simple weighted scoring
        val_score = self.valuation.upside_percent / 10  # -10 to +10
        tech_score = {"bullish": 1.0, "neutral": 0.0, "bearish": -1.0}[self.technical.trend]
        sent_score = self.sentiment.overall_score  # -1 to +1
        
        # Weighted average
        overall = 0.5 * val_score + 0.3 * tech_score + 0.2 * sent_score
        
        if overall > 0.5:
            return "Strong Buy"
        elif overall > 0.2:
            return "Buy"
        elif overall > -0.2:
            return "Hold"
        elif overall > -0.5:
            return "Sell"
        else:
            return "Strong Sell"
    
    @property
    def confidence_score(self) -> float:
        """
        Calculate overall confidence in analysis.
        
        Higher when multiple indicators agree.
        """
        # Check agreement between signals
        signals_agree = (
            (self.valuation.upside_percent > 0 and self.technical.trend == "bullish") or
            (self.valuation.upside_percent < 0 and self.technical.trend == "bearish")
        )
        
        base_confidence = self.valuation.confidence
        
        if signals_agree:
            return min(100, base_confidence + 10)
        else:
            return max(0, base_confidence - 10)


# ==================== Exports ====================

__all__ = [
    # Stock data
    "StockData",
    
    # Valuation
    "ValuationResult",
    "MonteCarloResult",
    
    # Technical
    "Signal",
    "TechnicalAnalysis",
    
    # Sentiment
    "SentimentResult",
    
    # Risk
    "RiskMetrics",
    
    # Portfolio
    "PortfolioPosition",
    "Portfolio",
    "PortfolioMetrics",
    "OptimizationResult",
    
    # Analysis
    "AnalysisResult",
]
