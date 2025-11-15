"""
Application Constants
Centralized location for all magic numbers and configuration values
"""
from typing import Dict, List

# ==================== API Configuration ====================
YFINANCE_RATE_LIMIT = 2000  # requests per hour
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# ==================== Cache Configuration ====================
CACHE_DIR = "data/cache"
CACHE_DB_NAME = "market_data.db"
CACHE_TTL = 300  # 5 minutes in seconds (also aliased as DEFAULT_CACHE_TTL)
DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
LONG_CACHE_TTL = 3600  # 1 hour in seconds
SHORT_CACHE_TTL = 60  # 1 minute in seconds

# ==================== Data Fetching ====================
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"
MIN_DATA_POINTS = 20  # minimum for technical analysis

# ==================== Technical Analysis Thresholds ====================
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_NEUTRAL_LOW = 40
RSI_NEUTRAL_HIGH = 60

# ==================== Valuation Scoring ====================
SCORE_WEIGHTS = {
    "valuation": 0.35,
    "technical": 0.30,
    "sentiment": 0.20,
    "fundamentals": 0.15
}

CONFIDENCE_THRESHOLDS = {
    "strong_buy": 70,
    "buy": 50,
    "hold": 30,
    "sell": 0
}

# ==================== Display Configuration ====================
MAX_DISPLAY_ROWS = 100
DEFAULT_DECIMALS = 2
CURRENCY_DECIMALS = 2
PERCENTAGE_DECIMALS = 2

# ==================== Color Scheme ====================
COLORS = {
    # Primary colors
    "bullish_green": "#00FF88",
    "bearish_red": "#FF3860",
    "info_blue": "#00D4FF",
    "warning_gold": "#FFB700",
    "neutral_gray": "#999999",
    
    # Background colors
    "dark_bg": "#1C1F26",
    "light_bg": "#FFFFFF",
    "card_bg_dark": "rgba(28, 31, 38, 0.9)",
    "card_bg_light": "rgba(255, 255, 255, 0.9)",
    
    # Accent colors
    "success": "#00FF88",
    "error": "#FF3860",
    "warning": "#FFB700",
    "info": "#00D4FF",
}

# ==================== Chart Configuration ====================
CHART_HEIGHT = 600
CHART_HEIGHT_SMALL = 400
CHART_HEIGHT_LARGE = 800

PLOTLY_TEMPLATE = "plotly_dark"

# ==================== Options Analysis ====================
OPTIONS_MIN_VOLUME = 100
OPTIONS_MIN_OI = 50
OPTIONS_UNUSUAL_ACTIVITY_RATIO = 2.0  # volume/OI ratio

# ==================== Sentiment Thresholds ====================
SENTIMENT_BULLISH_THRESHOLD = 30
SENTIMENT_BEARISH_THRESHOLD = -30

# ==================== Dashboard Configuration ====================
DASHBOARD_TYPES = ["stocks", "options", "crypto"]

DEFAULT_TICKERS = {
    "stocks": "META",
    "options": "SPY",
    "crypto": "BTC-USD"
}

POPULAR_TICKERS = {
    "stocks": ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "META", "AMZN", "SPY", "QQQ"],
    "options": ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMZN"],
    "crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "ADA-USD", "XRP-USD"]
}

# ==================== Error Messages ====================
ERROR_MESSAGES = {
    "no_data": "Unable to fetch data. Please try again.",
    "invalid_ticker": "Invalid ticker symbol. Please check and try again.",
    "api_error": "API error occurred. Please try again later.",
    "cache_error": "Cache error. Data may be stale.",
    "analysis_error": "Error during analysis. Some metrics unavailable."
}

# ==================== Logging Configuration ====================
LOG_DIR = "logs"
LOG_FILE = "dashboard.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== Feature Flags ====================
FEATURES = {
    "debug_mode": False,
    "cache_enabled": True,
    "sentiment_analysis": True,
    "options_analysis": True,
    "crypto_analysis": True,
    "institutional_data": True,
}

# ==================== Performance Optimization ====================
BATCH_SIZE = 100
MAX_WORKERS = 4
LAZY_LOADING = True

# ==================== Mobile Breakpoints ====================
MOBILE_BREAKPOINT = "768px"
TABLET_BREAKPOINT = "1024px"

# ==================== Rate Limiting ====================
RATE_LIMIT_REQUESTS = 50
RATE_LIMIT_PERIOD = 60  # seconds

# ==================== Data Validation ====================
MAX_TICKER_LENGTH = 10
MIN_TICKER_LENGTH = 1
VALID_TICKER_PATTERN = r"^[A-Z0-9\-\.]+$"

# ==================== Export Configuration ====================
EXPORT_FORMATS = ["csv", "json", "excel"]
MAX_EXPORT_ROWS = 10000
