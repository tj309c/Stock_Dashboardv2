"""
Utility Functions for Formatting and Data Processing
Clean, reusable functions for the dashboard
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional, Union


# ==================== NUMBER FORMATTING ====================

def format_number(value: Union[int, float, None], decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
    """
    Format numbers with commas for aesthetics
    
    Args:
        value: Number to format
        decimals: Decimal places
        prefix: String before number (e.g., "$")
        suffix: String after number (e.g., "%")
    
    Returns:
        Formatted string
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if abs(value) >= 1e12:  # Trillions
            formatted = f"{value/1e12:,.{decimals}f}T"
        elif abs(value) >= 1e9:  # Billions
            formatted = f"{value/1e9:,.{decimals}f}B"
        elif abs(value) >= 1e6:  # Millions
            formatted = f"{value/1e6:,.{decimals}f}M"
        elif abs(value) >= 1e3:  # Thousands
            formatted = f"{value/1e3:,.{decimals}f}K"
        else:
            formatted = f"{value:,.{decimals}f}"
        
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format as currency with $ and commas"""
    return format_number(value, decimals, prefix="$")


def format_percentage(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format as percentage with % and commas"""
    return format_number(value, decimals, suffix="%")


def format_large_number(value: Union[int, float, None]) -> str:
    """Format large numbers with K, M, B, T suffixes"""
    return format_number(value, decimals=2)


def format_price(value: Union[int, float, None]) -> str:
    """Format price with appropriate decimal places"""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value < 1:
            return f"${value:,.4f}"
        elif value < 100:
            return f"${value:,.2f}"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "N/A"


# ==================== DATA SANITIZATION ====================

def sanitize_dict_for_cache(data: Dict) -> Dict:
    """
    Convert Timestamp and other non-serializable objects to strings
    For Streamlit caching compatibility
    
    Args:
        data: Dictionary that may contain Timestamps
    
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        # Convert Timestamp keys to strings
        if hasattr(key, 'isoformat'):
            key = key.isoformat()
        elif isinstance(key, pd.Timestamp):
            key = str(key)
        
        # Convert Timestamp values
        if isinstance(value, pd.Timestamp):
            sanitized[key] = str(value)
        elif hasattr(value, 'isoformat'):
            sanitized[key] = value.isoformat()
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict_for_cache(value)
        elif isinstance(value, (list, tuple)):
            sanitized[key] = [
                sanitize_dict_for_cache(item) if isinstance(item, dict) else
                str(item) if isinstance(item, pd.Timestamp) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


# ==================== SAFE DATA EXTRACTION ====================

def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary
    
    Args:
        dictionary: Dict to extract from
        key: Key to look for
        default: Default value if not found
    
    Returns:
        Value or default
    """
    if not isinstance(dictionary, dict):
        return default
    
    return dictionary.get(key, default)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, avoiding division by zero
    
    Args:
        numerator: Top number
        denominator: Bottom number
        default: Value to return if division fails
    
    Returns:
        Result or default
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        result = numerator / denominator
        return result if not pd.isna(result) else default
    except (TypeError, ZeroDivisionError):
        return default


# ==================== DATA VALIDATION ====================

def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format
    
    Args:
        ticker: Ticker string
    
    Returns:
        True if valid format
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    ticker = ticker.strip().upper()
    
    # Basic validation: 1-5 characters, alphanumeric and hyphens
    if len(ticker) < 1 or len(ticker) > 10:
        return False
    
    # Allow letters, numbers, hyphens (for crypto like BTC-USD)
    return all(c.isalnum() or c == '-' or c == '.' for c in ticker)


def is_valid_number(value: Any) -> bool:
    """Check if value is a valid number"""
    try:
        float(value)
        return not pd.isna(value)
    except (ValueError, TypeError):
        return False


# ==================== TIME FORMATTING ====================

# ==================== COLOR HELPERS ====================

def get_color_for_value(value: float, positive_color: str = "#00FF88", 
                        negative_color: str = "#FF3860", 
                        neutral_color: str = "#FFB700") -> str:
    """
    Get color based on value (positive/negative)
    
    Args:
        value: Number to evaluate
        positive_color: Color for positive values
        negative_color: Color for negative values
        neutral_color: Color for zero
    
    Returns:
        Hex color string
    """
    if not is_valid_number(value):
        return neutral_color
    
    value = float(value)
    
    if value > 0:
        return positive_color
    elif value < 0:
        return negative_color
    else:
        return neutral_color


def get_confidence_color(score: float) -> str:
    """
    Get color based on confidence score
    
    Args:
        score: Confidence score 0-100
    
    Returns:
        Hex color string
    """
    if score >= 70:
        return "#00FF88"  # Green
    elif score >= 50:
        return "#FFB700"  # Orange
    else:
        return "#FF3860"  # Red


# ==================== TEXT FORMATTING ====================

# ==================== DATAFRAME HELPERS ====================

# ==================== ERROR HANDLING ====================

class DashboardError(Exception):
    """Custom exception for dashboard errors"""
    pass


# ==================== PERFORMANCE HELPERS ====================
