"""
Core Package

Contains foundational components for the trading dashboard:
- Type definitions (types.py)
- Custom exceptions (errors.py)
- Data layer (data/)
- Business logic (business/)

Author: Refactoring Team
Date: 2024-11
Phase: 1 (Foundation)
"""

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
    PortfolioMetrics,
    OptimizationResult,
    AnalysisResult,
)

from core.errors import (
    TradingDashboardError,
    DataFetchError,
    InsufficientDataError,
    DataValidationError,
    CalculationError,
    InvalidParameterError,
    AnalysisError,
    ValuationError,
    ServiceError,
    CacheError,
    ConfigurationError,
    handle_error,
)

__version__ = "2.0.0-alpha"

__all__ = [
    # Types
    "StockData",
    "ValuationResult",
    "MonteCarloResult",
    "Signal",
    "TechnicalAnalysis",
    "SentimentResult",
    "RiskMetrics",
    "PortfolioPosition",
    "Portfolio",
    "PortfolioMetrics",
    "OptimizationResult",
    "AnalysisResult",
    
    # Errors
    "TradingDashboardError",
    "DataFetchError",
    "InsufficientDataError",
    "DataValidationError",
    "CalculationError",
    "InvalidParameterError",
    "AnalysisError",
    "ValuationError",
    "ServiceError",
    "CacheError",
    "ConfigurationError",
    "handle_error",
]
