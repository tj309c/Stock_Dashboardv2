"""
Formatters Utility
Centralized formatting functions for currency, numbers, dates, etc.
Consolidates all format_* functions from utils.py into one module.
"""

import pandas as pd
from typing import Union, Optional
from datetime import datetime, date

# =============================================================================
# Number Formatting
# =============================================================================

def format_number(
    value: Union[int, float, None],
    decimals: int = 2,
    prefix: str = "",
    suffix: str = ""
) -> str:
    """
    Format number with abbreviations (K, M, B, T) and optional prefix/suffix.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
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
    """Format as currency with $ and commas."""
    return format_number(value, decimals, prefix="$")


def format_percentage(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format as percentage with % and commas."""
    return format_number(value, decimals, suffix="%")


def format_large_number(value: Union[int, float, None]) -> str:
    """Format large numbers with K, M, B, T suffixes."""
    return format_number(value, decimals=2)


def format_price(value: Union[int, float, None]) -> str:
    """
    Format price with appropriate decimal places.
    More decimals for prices < $1.
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value < 1:
            return f"${value:,.4f}"
        elif value < 10:
            return f"${value:,.3f}"
        else:
            return f"${value:,.2f}"
    except (ValueError, TypeError):
        return "N/A"


def format_integer(value: Union[int, float, None]) -> str:
    """Format as integer with comma separators."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "N/A"


def format_decimal(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format decimal number with comma separators."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_ratio(value: Union[int, float, None], decimals: int = 2) -> str:
    """Format ratio (e.g., P/E ratio)."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value < 0:
            return "N/A"  # Negative ratios don't make sense
        return f"{value:.{decimals}f}x"
    except (ValueError, TypeError):
        return "N/A"


def format_multiplier(value: Union[int, float, None], decimals: int = 1) -> str:
    """Format multiplier (e.g., 2.5x)."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        return f"{float(value):.{decimals}f}x"
    except (ValueError, TypeError):
        return "N/A"


def format_change(value: Union[int, float, None], decimals: int = 2, show_sign: bool = True) -> str:
    """
    Format change value with + or - sign.
    
    Args:
        value: Change value
        decimals: Number of decimal places
        show_sign: Show + sign for positive values
    
    Returns:
        Formatted string with sign
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 and show_sign else ""
        return f"{sign}{value:.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percent_change(value: Union[int, float, None], decimals: int = 2, show_sign: bool = True) -> str:
    """Format percentage change with + or - sign."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 and show_sign else ""
        return f"{sign}{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


# =============================================================================
# Date & Time Formatting
# =============================================================================

def format_date(dt: Union[datetime, date, pd.Timestamp, str, None], fmt: str = "%Y-%m-%d") -> str:
    """
    Format date to string.
    
    Args:
        dt: Date/datetime to format
        fmt: Format string
    
    Returns:
        Formatted date string
    """
    if dt is None or pd.isna(dt):
        return "N/A"
    
    try:
        if isinstance(dt, str):
            dt = pd.to_datetime(dt)
        elif isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        
        if isinstance(dt, (datetime, date)):
            return dt.strftime(fmt)
        
        return str(dt)
    except:
        return "N/A"


def format_datetime(dt: Union[datetime, pd.Timestamp, str, None], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return format_date(dt, fmt)


def format_time_ago(dt: Union[datetime, pd.Timestamp, str, None]) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").
    
    Args:
        dt: Datetime to format
    
    Returns:
        Relative time string
    """
    if dt is None or pd.isna(dt):
        return "N/A"
    
    try:
        if isinstance(dt, str):
            dt = pd.to_datetime(dt)
        elif isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()
        
        now = datetime.now()
        if dt.tzinfo:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds/3600)} hours ago"
        elif seconds < 604800:
            return f"{int(seconds/86400)} days ago"
        elif seconds < 2592000:
            return f"{int(seconds/604800)} weeks ago"
        elif seconds < 31536000:
            return f"{int(seconds/2592000)} months ago"
        else:
            return f"{int(seconds/31536000)} years ago"
    except:
        return "N/A"


# =============================================================================
# Special Formatters
# =============================================================================

def format_market_cap(value: Union[int, float, None]) -> str:
    """Format market capitalization."""
    return format_currency(value, decimals=2)


def format_volume(value: Union[int, float, None]) -> str:
    """Format trading volume."""
    return format_large_number(value)


def format_shares(value: Union[int, float, None]) -> str:
    """Format share count."""
    return format_large_number(value)


def format_dividend_yield(value: Union[int, float, None]) -> str:
    """Format dividend yield as percentage."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        # Convert to percentage if needed
        value = float(value)
        if value < 1:
            value *= 100
        return f"{value:.2f}%"
    except:
        return "N/A"


def format_beta(value: Union[int, float, None]) -> str:
    """Format beta coefficient."""
    return format_decimal(value, decimals=2)


def format_rsi(value: Union[int, float, None]) -> str:
    """Format RSI (0-100 scale)."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value < 30:
            emoji = "🟢"  # Oversold
        elif value > 70:
            emoji = "🔴"  # Overbought
        else:
            emoji = "🟡"  # Neutral
        
        return f"{emoji} {value:.1f}"
    except:
        return "N/A"


def format_sentiment_score(value: Union[int, float, None]) -> str:
    """
    Format sentiment score (-1 to 1 scale).
    
    Args:
        value: Sentiment score
    
    Returns:
        Formatted string with emoji
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value > 0.3:
            emoji = "😊"  # Positive
            label = "Bullish"
        elif value < -0.3:
            emoji = "😟"  # Negative
            label = "Bearish"
        else:
            emoji = "😐"  # Neutral
            label = "Neutral"
        
        return f"{emoji} {label} ({value:+.2f})"
    except:
        return "N/A"


def format_confidence(value: Union[int, float, None]) -> str:
    """Format confidence level as percentage."""
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        value = float(value)
        if value <= 1:
            value *= 100  # Convert to percentage
        
        if value >= 80:
            emoji = "🟢"
        elif value >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        return f"{emoji} {value:.0f}%"
    except:
        return "N/A"


# =============================================================================
# Table/DataFrame Formatting
# =============================================================================

def format_dataframe_currency(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Format specified DataFrame columns as currency.
    
    Args:
        df: DataFrame to format
        columns: List of column names to format
    
    Returns:
        DataFrame with formatted columns
    """
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(format_currency)
    return df_copy


def format_dataframe_percentage(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Format specified DataFrame columns as percentages."""
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(format_percentage)
    return df_copy


def format_dataframe_dates(df: pd.DataFrame, columns: list[str], fmt: str = "%Y-%m-%d") -> pd.DataFrame:
    """Format specified DataFrame columns as dates."""
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: format_date(x, fmt))
    return df_copy


# =============================================================================
# Color Formatting for UI
# =============================================================================

def get_color_for_value(value: Union[int, float, None], reverse: bool = False) -> str:
    """
    Get color code based on value (positive=green, negative=red).
    
    Args:
        value: Value to evaluate
        reverse: Reverse color logic (positive=red, negative=green)
    
    Returns:
        Color code
    """
    from src.core.constants import COLOR_SUCCESS, COLOR_ERROR, COLOR_NEUTRAL
    
    if value is None or pd.isna(value):
        return COLOR_NEUTRAL
    
    try:
        value = float(value)
        if value > 0:
            return COLOR_ERROR if reverse else COLOR_SUCCESS
        elif value < 0:
            return COLOR_SUCCESS if reverse else COLOR_ERROR
        else:
            return COLOR_NEUTRAL
    except:
        return COLOR_NEUTRAL


def get_emoji_for_change(value: Union[int, float, None]) -> str:
    """Get emoji based on positive/negative change."""
    if value is None or pd.isna(value):
        return "➖"
    
    try:
        value = float(value)
        if value > 0:
            return "📈"
        elif value < 0:
            return "📉"
        else:
            return "➖"
    except:
        return "➖"


def get_trend_emoji(value: Union[int, float, None], threshold: float = 0) -> str:
    """Get trend emoji (up/down arrow)."""
    if value is None or pd.isna(value):
        return "→"
    
    try:
        value = float(value)
        if value > threshold:
            return "↗"
        elif value < -threshold:
            return "↘"
        else:
            return "→"
    except:
        return "→"
