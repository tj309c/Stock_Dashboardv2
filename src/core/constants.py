"""
Core Constants
Single source of truth for all application constants.
"""

# =============================================================================
# Financial Constants
# =============================================================================

# Risk and Returns
RISK_FREE_RATE = 0.04  # 4% risk-free rate
MARKET_RISK_PREMIUM = 0.08  # 8% market risk premium
TERMINAL_GROWTH_RATE = 0.025  # 2.5% perpetual growth

# Valuation Defaults
DEFAULT_WACC = 0.10  # 10% Weighted Average Cost of Capital
DEFAULT_GROWTH_RATE = 0.10  # 10% growth rate
DEFAULT_PROJECTION_YEARS = 5  # 5-year DCF projection
DEFAULT_PE_RATIO = 20  # Industry average P/E
MAX_PE_RATIO = 25  # Cap P/E at 25x
DEFAULT_PB_TARGET = 1.5  # Target Price-to-Book ratio
PEG_UNDERVALUED_THRESHOLD = 1.0  # PEG < 1 is undervalued
PEG_MAX_THRESHOLD = 2.0  # Ignore PEG > 2

# Technical Analysis
RSI_OVERSOLD = 30  # RSI oversold threshold
RSI_OVERBOUGHT = 70  # RSI overbought threshold
MACD_SIGNAL_PERIOD = 9  # MACD signal line period
BOLLINGER_STD_DEV = 2  # Bollinger Bands standard deviations

# =============================================================================
# Data & Caching
# =============================================================================

# Cache TTL (seconds)
CACHE_TTL_SHORT = 60  # 1 minute
CACHE_TTL_MEDIUM = 300  # 5 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_DAY = 86400  # 24 hours

# Data Periods
PERIOD_1D = "1d"
PERIOD_5D = "5d"
PERIOD_1MO = "1mo"
PERIOD_3MO = "3mo"
PERIOD_6MO = "6mo"
PERIOD_1Y = "1y"
PERIOD_2Y = "2y"
PERIOD_5Y = "5y"
PERIOD_10Y = "10y"
PERIOD_YTD = "ytd"
PERIOD_MAX = "max"

# Data Intervals
INTERVAL_1M = "1m"
INTERVAL_5M = "5m"
INTERVAL_15M = "15m"
INTERVAL_1H = "1h"
INTERVAL_1D = "1d"
INTERVAL_1WK = "1wk"
INTERVAL_1MO = "1mo"

# =============================================================================
# Performance Modes
# =============================================================================

PERFORMANCE_MODES = {
    "fast": {
        "name": "Fast Mode",
        "emoji": "⚡",
        "historical_period": "1mo",
        "cache_ttl_multiplier": 0.5,
        "fetch_institutional": False,
        "fetch_sentiment": False,
        "max_indicators": 5,
    },
    "balanced": {
        "name": "Balanced Mode",
        "emoji": "⚖️",
        "historical_period": "3mo",
        "cache_ttl_multiplier": 1.0,
        "fetch_institutional": True,
        "fetch_sentiment": True,
        "max_indicators": 10,
    },
    "deep": {
        "name": "Deep Mode",
        "emoji": "🔬",
        "historical_period": "1y",
        "cache_ttl_multiplier": 2.0,
        "fetch_institutional": True,
        "fetch_sentiment": True,
        "max_indicators": None,  # No limit
    },
}

DEFAULT_PERFORMANCE_MODE = "balanced"

# =============================================================================
# UI Constants - High Contrast WCAG AA Compliant Color Scheme
# =============================================================================

# Text Colors - Maximum Readability
COLOR_TEXT_PRIMARY = "#FFFFFF"  # Pure white for highest contrast
COLOR_TEXT_SECONDARY = "#E0E0E0"  # Light gray for secondary text (7:1 contrast)
COLOR_TEXT_TERTIARY = "#C0C0C0"  # Medium gray for disabled/tertiary text

# Background Colors - Dark Mode Optimized
COLOR_BG_PRIMARY = "#1A1A1A"  # Main background (very dark gray)
COLOR_BG_SECONDARY = "#2D2D2D"  # Card/container background (slightly lighter)
COLOR_BG_TERTIARY = "#3A3A3A"  # Hover/active states

# Semantic Colors - WCAG AA Compliant (4.5:1 minimum contrast on dark bg)
COLOR_SUCCESS = "#22C55E"  # Bright green (7.2:1 contrast)
COLOR_ERROR = "#EF4444"  # Red (4.7:1 contrast)
COLOR_WARNING = "#F59E0B"  # Orange (5.1:1 contrast)
COLOR_INFO = "#3B82F6"  # Blue (5.4:1 contrast)
COLOR_NEUTRAL = "#9CA3AF"  # Gray (4.5:1 contrast)

# Chart Colors - Vibrant but readable
CHART_COLOR_PRIMARY = "#3B82F6"  # Blue
CHART_COLOR_SECONDARY = "#8B5CF6"  # Purple
CHART_COLOR_TERTIARY = "#EC4899"  # Pink
CHART_COLOR_BULLISH = "#22C55E"  # Bright green
CHART_COLOR_BEARISH = "#EF4444"  # Red

# Legacy Dark Mode Colors (deprecated - use main colors above)
COLOR_SUCCESS_DARK = "#22C55E"
COLOR_ERROR_DARK = "#EF4444"
COLOR_WARNING_DARK = "#F59E0B"
COLOR_INFO_DARK = "#3B82F6"
COLOR_NEUTRAL_DARK = "#9CA3AF"

# Metrics
METRIC_LABEL_COLOR_POSITIVE = "normal"
METRIC_LABEL_COLOR_NEGATIVE = "inverse"

# Font Sizes
FONT_SIZE_SMALL = "0.875rem"
FONT_SIZE_NORMAL = "1rem"
FONT_SIZE_LARGE = "1.125rem"
FONT_SIZE_XLARGE = "1.25rem"

# =============================================================================
# API Constants
# =============================================================================

# API Rate Limits (requests per minute)
RATE_LIMIT_YFINANCE = 2000
RATE_LIMIT_FRED = 120
RATE_LIMIT_ALPHAVANTAGE = 5
RATE_LIMIT_FINNHUB = 60
RATE_LIMIT_NEWS_API = 100
RATE_LIMIT_REDDIT = 60

# API Timeouts (seconds)
API_TIMEOUT_SHORT = 5
API_TIMEOUT_MEDIUM = 10
API_TIMEOUT_LONG = 30

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1s, 2s, 4s

# =============================================================================
# Validation Constants
# =============================================================================

# Stock Ticker Validation
MIN_TICKER_LENGTH = 1
MAX_TICKER_LENGTH = 5
VALID_TICKER_PATTERN = r'^[A-Z\-\.]{1,5}$'

# Price Validation
MIN_STOCK_PRICE = 0.01
MAX_STOCK_PRICE = 1000000
MIN_CRYPTO_PRICE = 0.00000001
MAX_CRYPTO_PRICE = 10000000

# Data Quality Thresholds
MIN_DATA_POINTS = 10  # Minimum data points for analysis
MIN_VOLUME = 1000  # Minimum daily volume
DATA_COMPLETENESS_THRESHOLD = 0.8  # 80% data completeness required

# =============================================================================
# File Paths
# =============================================================================

# Data Directories
DATA_DIR = "data"
CACHE_DIR = "data/cache"
LOGS_DIR = "logs"
EXPORTS_DIR = "data/exports"

# Log Files
LOG_FILE = "logs/app.log"
ERROR_LOG_FILE = "logs/errors.log"
DEBUG_LOG_FILE = "logs/debug.log"

# =============================================================================
# Logging Constants
# =============================================================================

# Log Levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Log Format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# Business Logic Constants
# =============================================================================

# Portfolio Optimization
MIN_PORTFOLIO_ASSETS = 2
MAX_PORTFOLIO_ASSETS = 20
DEFAULT_RISK_TOLERANCE = 0.5  # 0-1 scale
REBALANCE_THRESHOLD = 0.05  # 5% drift triggers rebalance

# Monte Carlo Simulation
DEFAULT_SIMULATIONS = 1000
MIN_SIMULATIONS = 100
MAX_SIMULATIONS = 10000

# Options Analysis
DEFAULT_RISK_FREE_RATE_OPTIONS = 0.04
MIN_IMPLIED_VOLATILITY = 0.01
MAX_IMPLIED_VOLATILITY = 3.0
MIN_TIME_TO_EXPIRY = 1/365  # 1 day
MAX_TIME_TO_EXPIRY = 2  # 2 years

# Crypto Constants
CRYPTO_FEAR_GREED_THRESHOLD_FEAR = 30
CRYPTO_FEAR_GREED_THRESHOLD_GREED = 70
DEFAULT_CRYPTO_ALLOCATION = 0.05  # 5% of portfolio

# =============================================================================
# Error Messages
# =============================================================================

ERROR_NO_DATA = "No data available for the selected ticker"
ERROR_INVALID_TICKER = "Invalid ticker symbol"
ERROR_API_FAILED = "API request failed"
ERROR_INSUFFICIENT_DATA = "Insufficient data for analysis"
ERROR_CALCULATION_FAILED = "Calculation failed"
ERROR_NETWORK = "Network error - check your connection"

# =============================================================================
# Success Messages
# =============================================================================

SUCCESS_DATA_LOADED = "Data loaded successfully"
SUCCESS_CALCULATION = "Calculation completed successfully"
SUCCESS_EXPORT = "Data exported successfully"

# =============================================================================
# Feature Flags
# =============================================================================

FEATURE_SENTIMENT_ANALYSIS = True
FEATURE_OPTIONS_FLOW = True
FEATURE_CRYPTO_ARBITRAGE = True
FEATURE_AI_PREDICTIONS = True
FEATURE_PORTFOLIO_OPTIMIZATION = True
FEATURE_CONGRESSIONAL_TRADES = True
FEATURE_INSIDER_TRADES = True
FEATURE_ZERO_FCF_VALUATION = True

# =============================================================================
# Misc Constants
# =============================================================================

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Export Formats
EXPORT_FORMAT_CSV = "csv"
EXPORT_FORMAT_EXCEL = "xlsx"
EXPORT_FORMAT_JSON = "json"

# Date Formats
DATE_FORMAT_DISPLAY = "%Y-%m-%d"
DATE_FORMAT_FILE = "%Y%m%d"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"

# App Metadata
APP_NAME = "Analysis Master"
APP_VERSION = "3.0.0"
APP_AUTHOR = "Your Name"
APP_DESCRIPTION = "Comprehensive Stock Market Analysis Platform"
