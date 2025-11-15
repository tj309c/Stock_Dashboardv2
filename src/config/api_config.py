"""
API Configuration
Centralized management of all API keys, endpoints, and configurations.
"""

import os
from typing import Dict, Optional
from pathlib import Path
import streamlit as st

# =============================================================================
# API Keys Loading
# =============================================================================

def get_api_key(key_name: str, required: bool = False) -> Optional[str]:
    """
    Get API key from environment or Streamlit secrets.
    
    Args:
        key_name: Name of the API key
        required: If True, raises error when key not found
        
    Returns:
        API key value or None
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    
    # Fall back to environment variables
    value = os.getenv(key_name)
    
    if required and not value:
        raise ValueError(f"Required API key '{key_name}' not found in environment or secrets")
    
    return value


# =============================================================================
# API Endpoints
# =============================================================================

class APIEndpoints:
    """API endpoint constants."""
    
    # Yahoo Finance (via yfinance)
    YAHOO_FINANCE = "https://query1.finance.yahoo.com"
    
    # Federal Reserve Economic Data
    FRED_BASE = "https://api.stlouisfed.org/fred"
    FRED_SERIES = f"{FRED_BASE}/series/observations"
    
    # Alpha Vantage
    ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
    
    # Finnhub
    FINNHUB_BASE = "https://finnhub.io/api/v1"
    FINNHUB_STOCK = f"{FINNHUB_BASE}/stock"
    FINNHUB_INSIDER = f"{FINNHUB_BASE}/stock/insider-transactions"
    
    # News API
    NEWS_API_BASE = "https://newsapi.org/v2"
    NEWS_API_EVERYTHING = f"{NEWS_API_BASE}/everything"
    NEWS_API_TOP_HEADLINES = f"{NEWS_API_BASE}/top-headlines"
    
    # Reddit (via PRAW)
    REDDIT_BASE = "https://www.reddit.com"
    
    # Anthropic Claude
    ANTHROPIC_BASE = "https://api.anthropic.com/v1"
    ANTHROPIC_MESSAGES = f"{ANTHROPIC_BASE}/messages"
    
    # QuiverQuant (Congressional Trades)
    QUIVER_BASE = "https://api.quiverquant.com/beta"
    QUIVER_CONGRESS = f"{QUIVER_BASE}/live/congresstrading"
    
    # CoinGecko (Crypto)
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    COINGECKO_PRICE = f"{COINGECKO_BASE}/simple/price"
    
    # Fear & Greed Index
    FEAR_GREED_INDEX = "https://api.alternative.me/fng/"
    
    # EIA (Energy Information Administration)
    EIA_BASE = "https://api.eia.gov"
    EIA_SERIES = f"{EIA_BASE}/series"


# =============================================================================
# API Configuration Classes
# =============================================================================

class FREDConfig:
    """Federal Reserve Economic Data API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("FRED_API_KEY")
        self.base_url = APIEndpoints.FRED_BASE
        self.timeout = 10
        self.max_retries = 3
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_params(self, series_id: str, **kwargs) -> Dict:
        """Get request parameters for FRED API."""
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
        }
        params.update(kwargs)
        return params


class AlphaVantageConfig:
    """Alpha Vantage API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("ALPHA_VANTAGE_API_KEY")
        self.base_url = APIEndpoints.ALPHA_VANTAGE_BASE
        self.timeout = 10
        self.max_retries = 3
        self.rate_limit = 5  # 5 requests per minute
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None


class FinnhubConfig:
    """Finnhub API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("FINNHUB_API_KEY")
        self.base_url = APIEndpoints.FINNHUB_BASE
        self.timeout = 10
        self.max_retries = 3
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_headers(self) -> Dict:
        """Get request headers for Finnhub API."""
        return {"X-Finnhub-Token": self.api_key}


class NewsAPIConfig:
    """News API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("NEWS_API_KEY")
        self.base_url = APIEndpoints.NEWS_API_BASE
        self.timeout = 10
        self.max_retries = 3
        self.page_size = 100
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_params(self, **kwargs) -> Dict:
        """Get request parameters for News API."""
        params = {"apiKey": self.api_key}
        params.update(kwargs)
        return params


class RedditConfig:
    """Reddit API (PRAW) configuration."""
    
    def __init__(self):
        self.client_id = get_api_key("REDDIT_CLIENT_ID")
        self.client_secret = get_api_key("REDDIT_CLIENT_SECRET")
        self.user_agent = get_api_key("REDDIT_USER_AGENT") or "AnalysisMaster/1.0"
        
    @property
    def is_configured(self) -> bool:
        return (self.client_id is not None and 
                self.client_secret is not None and
                "your_reddit" not in (self.client_id or ""))
    
    def get_praw_config(self) -> Dict:
        """Get configuration dict for PRAW initialization."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "user_agent": self.user_agent,
        }


class AnthropicConfig:
    """Anthropic Claude API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("ANTHROPIC_API_KEY")
        self.base_url = APIEndpoints.ANTHROPIC_BASE
        self.model = "claude-3-sonnet-20240229"
        self.max_tokens = 1024
        self.timeout = 30
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_headers(self) -> Dict:
        """Get request headers for Anthropic API."""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }


class QuiverConfig:
    """QuiverQuant API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("QUIVER_API_KEY")
        self.base_url = APIEndpoints.QUIVER_BASE
        self.timeout = 10
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_headers(self) -> Dict:
        """Get request headers for QuiverQuant API."""
        return {"Authorization": f"Bearer {self.api_key}"}


class EIAConfig:
    """EIA (Energy Information Administration) API configuration."""
    
    def __init__(self):
        self.api_key = get_api_key("EIA_API_KEY")
        self.base_url = APIEndpoints.EIA_BASE
        self.timeout = 10
        
    @property
    def is_configured(self) -> bool:
        return self.api_key is not None


# =============================================================================
# Master API Configuration
# =============================================================================

class APIConfig:
    """
    Master API configuration manager.
    Provides centralized access to all API configurations.
    """
    
    def __init__(self):
        self.fred = FREDConfig()
        self.alpha_vantage = AlphaVantageConfig()
        self.finnhub = FinnhubConfig()
        self.news = NewsAPIConfig()
        self.reddit = RedditConfig()
        self.anthropic = AnthropicConfig()
        self.quiver = QuiverConfig()
        self.eia = EIAConfig()
        
    def get_configured_apis(self) -> Dict[str, bool]:
        """Get dictionary of all APIs and their configuration status."""
        return {
            "FRED": self.fred.is_configured,
            "Alpha Vantage": self.alpha_vantage.is_configured,
            "Finnhub": self.finnhub.is_configured,
            "News API": self.news.is_configured,
            "Reddit": self.reddit.is_configured,
            "Anthropic Claude": self.anthropic.is_configured,
            "QuiverQuant": self.quiver.is_configured,
            "EIA": self.eia.is_configured,
        }
    
    def get_missing_apis(self) -> list[str]:
        """Get list of APIs that are not configured."""
        return [name for name, configured in self.get_configured_apis().items() 
                if not configured]
    
    def validate_all(self) -> tuple[bool, list[str]]:
        """
        Validate all API configurations.
        
        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        missing = self.get_missing_apis()
        all_valid = len(missing) == 0
        return all_valid, missing


# =============================================================================
# Singleton Instance
# =============================================================================

# Global API configuration instance
api_config = APIConfig()


# =============================================================================
# Utility Functions
# =============================================================================

def check_api_health(api_name: str) -> Dict[str, any]:
    """
    Check health status of a specific API.
    
    Args:
        api_name: Name of the API to check
        
    Returns:
        Dictionary with status, message, and additional info
    """
    config_map = {
        "fred": api_config.fred,
        "alpha_vantage": api_config.alpha_vantage,
        "finnhub": api_config.finnhub,
        "news": api_config.news,
        "reddit": api_config.reddit,
        "anthropic": api_config.anthropic,
        "quiver": api_config.quiver,
        "eia": api_config.eia,
    }
    
    api_cfg = config_map.get(api_name.lower())
    if not api_cfg:
        return {"status": "error", "message": f"Unknown API: {api_name}"}
    
    if not api_cfg.is_configured:
        return {"status": "not_configured", "message": "API key not configured"}
    
    return {"status": "configured", "message": "API key configured"}


def get_api_summary() -> Dict:
    """Get summary of all API configurations."""
    configured = api_config.get_configured_apis()
    total = len(configured)
    active = sum(configured.values())
    
    return {
        "total": total,
        "configured": active,
        "missing": total - active,
        "percentage": (active / total * 100) if total > 0 else 0,
        "apis": configured,
    }
