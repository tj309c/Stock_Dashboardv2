"""
Performance Configuration Module
Full-featured mode with all capabilities enabled.
No restrictions on data fetching - comprehensive analysis for all operations.
"""
import streamlit as st
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMode:
    """Performance mode configuration"""
    name: str
    historical_period: str  # yfinance period
    cache_ttl_multiplier: float  # Multiply base TTLs by this
    enable_sentiment_scraping: bool
    enable_options_chain: bool
    enable_institutional: bool
    enable_economic_data: bool
    enable_political_data: bool
    max_sentiment_sources: int  # Number of sentiment sources (Reddit, News, etc.)
    parallel_fetch: bool
    show_eta: bool
    description: str


# ============================================================================
# FULL MODE DEFINITION (ALWAYS ENABLED)
# ============================================================================

FULL_MODE = PerformanceMode(
    name="Full Analysis Mode",
    historical_period="5y",  # 5 years of data
    cache_ttl_multiplier=1.0,  # Standard cache TTL
    enable_sentiment_scraping=True,  # Full sentiment analysis
    enable_options_chain=True,  # Full options chain with Greeks
    enable_institutional=True,  # Institutional holdings
    enable_economic_data=True,  # All economic indicators
    enable_political_data=True,  # Congressional trades
    max_sentiment_sources=3,  # Reddit, News, StockTwits
    parallel_fetch=True,
    show_eta=False,  # No need for mode indicator
    description="Comprehensive analysis with all data sources enabled. Full capabilities unlocked."
)

# Default and only mode
DEFAULT_MODE = FULL_MODE


# ============================================================================
# API RATE LIMITERS
# ============================================================================

# Rate limits based on free tier documentation
API_RATE_LIMITS = {
    # yfinance: No official limit, but recommended 2000 req/hour (GitHub issues)
    "yfinance": {
        "requests_per_hour": 2000,
        "requests_per_minute": 33,
        "burst_limit": 10  # Max concurrent requests
    },
    
    # Reddit API: 60 requests per minute (free tier)
    "reddit": {
        "requests_per_hour": 3600,
        "requests_per_minute": 60,
        "burst_limit": 5
    },
    
    # NewsAPI: 100 requests per day (free tier)
    "newsapi": {
        "requests_per_day": 100,
        "requests_per_hour": 4,  # Conservative to not hit daily limit
        "requests_per_minute": 1
    },
    
    # FRED: Unlimited (but be respectful)
    "fred": {
        "requests_per_hour": 1000,
        "requests_per_minute": 16,
        "burst_limit": 5
    },
    
    # BLS: 500 series per query, 500 daily requests
    "bls": {
        "requests_per_day": 500,
        "requests_per_hour": 20,
        "requests_per_minute": 2
    },
    
    # EIA: 5000 requests per day
    "eia": {
        "requests_per_day": 5000,
        "requests_per_hour": 200,
        "requests_per_minute": 10
    }
}


# ============================================================================
# ESTIMATED LOAD TIMES (seconds) - Full Analysis Mode
# ============================================================================

COMPONENT_ETA = {
    "stock_data": 5,  # 5 years of data
    "quote": 1,
    "fundamentals": 3,
    "options_chain": 15,  # Greeks calculation for 6 expirations
    "institutional": 8,  # Institutional holdings
    "sentiment_scraping": 30,  # Reddit + News + StockTwits scraping
    "economic_data": 5,  # Fresh economic data
    "political_data": 10,  # Congressional trades
    "technical_analysis": 2,
    "total": 79  # Total estimate (~1.3 minutes)
}


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_performance_mode():
    """Initialize performance mode in session state"""
    if "performance_mode" not in st.session_state:
        st.session_state.performance_mode = DEFAULT_MODE
        # Use ASCII-safe logging (emoji can cause UnicodeEncodeError on Windows)
        mode_name_ascii = DEFAULT_MODE.name.encode('ascii', 'ignore').decode('ascii').strip()
        logger.info(f"Initialized performance mode: {mode_name_ascii or DEFAULT_MODE.name.split()[0]}")


def get_current_mode() -> PerformanceMode:
    """Get the current performance mode"""
    initialize_performance_mode()
    return st.session_state.performance_mode


def set_performance_mode(mode: PerformanceMode):
    """Set the performance mode globally"""
    st.session_state.performance_mode = mode
    # Use ASCII-safe logging
    mode_name_ascii = mode.name.encode('ascii', 'ignore').decode('ascii').strip()
    logger.info(f"Performance mode changed to: {mode_name_ascii or mode.name.split()[0]}")


def toggle_performance_mode():
    """Toggle performance mode - deprecated, always uses full mode"""
    pass  # No-op since we only have one mode


def is_fast_mode() -> bool:
    """Check if currently in fast mode - always False (full mode enabled)"""
    return False


def is_deep_mode() -> bool:
    """Check if currently in deep mode - always True (full mode enabled)"""
    return True


# ============================================================================
# CACHE TTL CALCULATOR
# ============================================================================

def get_adjusted_ttl(base_ttl: int) -> int:
    """
    Get cache TTL adjusted for current performance mode.
    
    Args:
        base_ttl: Base TTL in seconds
        
    Returns:
        Adjusted TTL in seconds
    """
    mode = get_current_mode()
    adjusted = int(base_ttl * mode.cache_ttl_multiplier)
    return adjusted


# ============================================================================
# ETA CALCULATOR
# ============================================================================

def calculate_eta(components: List[str]) -> Dict:
    """
    Calculate estimated time to load based on components.
    
    Args:
        components: List of components to load (e.g., ['stock_data', 'sentiment_scraping'])
        
    Returns:
        Dict with eta_seconds, eta_formatted, breakdown
    """
    eta_seconds = 0
    breakdown = {}
    
    for component in components:
        if component in COMPONENT_ETA:
            time = COMPONENT_ETA[component]
            eta_seconds += time
            breakdown[component] = time
    
    # Format ETA
    if eta_seconds < 60:
        eta_formatted = f"{eta_seconds}s"
    else:
        minutes = eta_seconds // 60
        seconds = eta_seconds % 60
        eta_formatted = f"{minutes}m {seconds}s"
    
    return {
        "eta_seconds": eta_seconds,
        "eta_formatted": eta_formatted,
        "breakdown": breakdown,
        "mode": "Full Analysis Mode"
    }


def get_dashboard_eta(dashboard_name: str) -> str:
    """Get estimated load time for a specific dashboard - always full analysis"""
    
    if dashboard_name == "stocks":
        components = ["stock_data", "quote", "fundamentals", "options_chain", 
                     "institutional", "sentiment_scraping", "technical_analysis"]
    
    elif dashboard_name == "options":
        components = ["stock_data", "options_chain", "technical_analysis"]
    
    elif dashboard_name == "crypto":
        components = ["stock_data", "quote", "sentiment_scraping", "technical_analysis"]
    
    elif dashboard_name == "advanced":
        components = ["stock_data", "fundamentals", "economic_data", 
                     "political_data", "sentiment_scraping", "technical_analysis"]
    
    else:
        return "N/A"
    
    eta = calculate_eta(components)
    return eta["eta_formatted"]


# ============================================================================
# MODE DISPLAY HELPERS
# ============================================================================

def show_performance_mode_indicator():
    """Display performance mode info in sidebar - always full mode"""
    st.sidebar.markdown("### 🚀 Full Analysis Mode")
    st.sidebar.caption("All features and data sources enabled. Comprehensive analysis with options chains, institutional holdings, and real-time sentiment.")
    st.sidebar.markdown("---")


def show_eta_indicator(dashboard_name: str):
    """Show estimated load time for current dashboard"""
    mode = get_current_mode()
    
    if mode.show_eta:
        eta = get_dashboard_eta(dashboard_name)
        st.info(f"⏱️ Estimated load time: **{eta}** ({mode.name})")


# ============================================================================
# FEATURE FLAGS
# ============================================================================

def should_fetch_sentiment() -> bool:
    """Check if sentiment scraping should be enabled - always True"""
    return True


def should_fetch_options() -> bool:
    """Check if options chain should be fetched - always True"""
    return True


def should_fetch_institutional() -> bool:
    """Check if institutional data should be fetched - always True"""
    return True


def should_fetch_economic() -> bool:
    """Check if economic data should be fetched - always True"""
    return True


def should_fetch_political() -> bool:
    """Check if political data should be fetched - always True"""
    return True


def get_historical_period() -> str:
    """Get the historical period for data fetching - always 5 years"""
    return "5y"


def get_max_sentiment_sources() -> int:
    """Get max number of sentiment sources to query - always 3"""
    return 3


# ============================================================================
# USAGE TRACKING
# ============================================================================

class APIUsageTracker:
    """Track API usage to prevent hitting rate limits"""
    
    def __init__(self):
        if "api_usage" not in st.session_state:
            st.session_state.api_usage = {}
    
    def record_request(self, api_name: str):
        """Record an API request"""
        if api_name not in st.session_state.api_usage:
            st.session_state.api_usage[api_name] = {
                "count": 0,
                "last_reset": datetime.now()
            }
        
        st.session_state.api_usage[api_name]["count"] += 1
    
    def check_limit(self, api_name: str) -> bool:
        """Check if we can make another request without hitting limits"""
        if api_name not in API_RATE_LIMITS:
            return True  # No limit defined
        
        usage = st.session_state.api_usage.get(api_name, {"count": 0})
        limit = API_RATE_LIMITS[api_name].get("requests_per_minute", float('inf'))
        
        return usage["count"] < limit
    
    def get_usage_stats(self) -> Dict:
        """Get current API usage statistics"""
        return st.session_state.api_usage.copy()


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "PerformanceMode",
    "FULL_MODE",
    "initialize_performance_mode",
    "get_current_mode",
    "set_performance_mode",
    "get_adjusted_ttl",
    "calculate_eta",
    "get_dashboard_eta",
    "show_performance_mode_indicator",
    "show_eta_indicator",
    "should_fetch_sentiment",
    "should_fetch_options",
    "should_fetch_institutional",
    "should_fetch_economic",
    "should_fetch_political",
    "get_historical_period",
    "get_max_sentiment_sources",
    "APIUsageTracker",
    "API_RATE_LIMITS"
]
