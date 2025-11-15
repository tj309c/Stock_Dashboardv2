"""
Custom Exception Hierarchy

Defines application-specific exceptions for better error handling
and more informative error messages.

Author: Refactoring Team
Date: 2024-11
Phase: 1 (Foundation)
"""

from typing import Any, Optional, Dict


# ==================== Base Exception ====================

class TradingDashboardError(Exception):
    """
    Base exception for all dashboard errors.
    
    All custom exceptions inherit from this class,
    making it easy to catch all dashboard-specific errors.
    """
    pass


# ==================== Data Errors ====================

class DataFetchError(TradingDashboardError):
    """
    Error fetching data from external source.
    
    Raised when API calls fail, timeouts occur,
    or data source is unavailable.
    """
    def __init__(self, ticker: str, source: str, message: str):
        self.ticker = ticker
        self.source = source
        self.message = message
        super().__init__(f"Error fetching {ticker} from {source}: {message}")


class InsufficientDataError(TradingDashboardError):
    """
    Insufficient data for analysis.
    
    Raised when data exists but is incomplete
    for the requested analysis type.
    """
    def __init__(self, required: str, available: str, ticker: Optional[str] = None):
        self.required = required
        self.available = available
        self.ticker = ticker
        
        msg = f"Need {required}, but only have {available}"
        if ticker:
            msg = f"{ticker}: {msg}"
        
        super().__init__(msg)


class DataValidationError(TradingDashboardError):
    """
    Data validation error.
    
    Raised when data is present but doesn't meet
    quality or consistency requirements.
    """
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for {field}={value}: {reason}")


# ==================== Calculation Errors ====================

class CalculationError(TradingDashboardError):
    """
    Error during calculation.
    
    Raised when mathematical calculations fail,
    produce invalid results, or encounter edge cases.
    """
    def __init__(self, calculation: str, message: str, details: Optional[Dict] = None):
        self.calculation = calculation
        self.message = message
        self.details = details or {}
        
        detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
        if detail_str:
            super().__init__(f"Error in {calculation}: {message} ({detail_str})")
        else:
            super().__init__(f"Error in {calculation}: {message}")


class InvalidParameterError(TradingDashboardError):
    """
    Invalid parameter provided to function.
    
    Raised when function parameters are outside
    valid ranges or incompatible with each other.
    """
    def __init__(self, parameter: str, value: Any, reason: str):
        self.parameter = parameter
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {parameter}={value}: {reason}")


# ==================== Analysis Errors ====================

class AnalysisError(TradingDashboardError):
    """
    Error during stock analysis.
    
    Raised when analysis pipeline fails at any stage
    (data fetching, valuation, technical, etc.)
    """
    def __init__(self, ticker: str, message: str, stage: Optional[str] = None):
        self.ticker = ticker
        self.message = message
        self.stage = stage
        
        if stage:
            super().__init__(f"Analysis failed for {ticker} at {stage}: {message}")
        else:
            super().__init__(f"Analysis failed for {ticker}: {message}")


class ValuationError(TradingDashboardError):
    """
    Error during valuation calculation.
    
    Raised when DCF, multiples, or other valuation
    methods cannot produce valid results.
    """
    def __init__(self, method: str, ticker: str, reason: str):
        self.method = method
        self.ticker = ticker
        self.reason = reason
        super().__init__(f"{method} valuation failed for {ticker}: {reason}")


# ==================== Service Errors ====================

class ServiceError(TradingDashboardError):
    """
    Error in service layer.
    
    Raised when service orchestration fails,
    dependencies are missing, or configuration is invalid.
    """
    def __init__(self, service: str, operation: str, message: str):
        self.service = service
        self.operation = operation
        self.message = message
        super().__init__(f"{service}.{operation} failed: {message}")


class CacheError(TradingDashboardError):
    """
    Error in caching layer.
    
    Raised when cache operations fail (read, write, invalidate).
    """
    def __init__(self, operation: str, key: str, message: str):
        self.operation = operation
        self.key = key
        self.message = message
        super().__init__(f"Cache {operation} failed for key '{key}': {message}")


# ==================== Configuration Errors ====================

class ConfigurationError(TradingDashboardError):
    """
    Configuration error.
    
    Raised when configuration is missing, invalid,
    or incompatible with current environment.
    """
    def __init__(self, key: str, reason: str):
        self.key = key
        self.reason = reason
        super().__init__(f"Configuration error for '{key}': {reason}")


# ==================== Helper Functions ====================

def handle_error(error: Exception, context: dict) -> TradingDashboardError:
    """
    Convert generic exceptions to dashboard-specific exceptions.
    
    Args:
        error: Original exception
        context: Context information (ticker, operation, etc.)
    
    Returns:
        TradingDashboardError subclass with more context
    
    Example:
        try:
            stock = yf.Ticker(ticker)
        except Exception as e:
            raise handle_error(e, {"ticker": ticker, "source": "yfinance"})
    """
    ticker = context.get("ticker", "unknown")
    source = context.get("source", "unknown")
    operation = context.get("operation", "unknown")
    
    # Convert common exceptions
    if isinstance(error, KeyError):
        return InsufficientDataError(
            required=str(error),
            available="partial data",
            ticker=ticker
        )
    
    elif isinstance(error, ValueError):
        return DataValidationError(
            field="data",
            value="invalid",
            reason=str(error)
        )
    
    elif isinstance(error, ZeroDivisionError):
        return CalculationError(
            calculation=operation,
            message="Division by zero"
        )
    
    elif isinstance(error, (ConnectionError, TimeoutError)):
        return DataFetchError(
            ticker=ticker,
            source=source,
            message=str(error)
        )
    
    # Default: wrap in generic TradingDashboardError
    else:
        return TradingDashboardError(f"{operation} failed: {str(error)}")


# ==================== Exports ====================

__all__ = [
    # Base
    "TradingDashboardError",
    
    # Data errors
    "DataFetchError",
    "InsufficientDataError",
    "DataValidationError",
    
    # Calculation errors
    "CalculationError",
    "InvalidParameterError",
    
    # Analysis errors
    "AnalysisError",
    "ValuationError",
    
    # Service errors
    "ServiceError",
    "CacheError",
    
    # Configuration errors
    "ConfigurationError",
    
    # Helper
    "handle_error",
]
