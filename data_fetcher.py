"""
Data Fetcher Module - Using yfinance for all market data
Always fetches comprehensive data: options, institutional holdings, sentiment
Optimized for speed and reliability
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
import logging
from pathlib import Path
from utils import sanitize_dict_for_cache
import streamlit as st
from src.config.performance_config import (
    get_adjusted_ttl,
    get_historical_period,
    should_fetch_options,
    should_fetch_institutional,
    APIUsageTracker
)

logger = logging.getLogger(__name__)
api_tracker = APIUsageTracker()

class MarketDataFetcher:
    """Fetches all market data using yfinance API"""
    
    def __init__(self, cache_dir: Path = Path("data/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    # ========== PRICE DATA ==========
    def get_stock_data(self, ticker: str, period: str = None) -> Dict:
        """Get comprehensive stock data from yfinance (mode-aware)"""
        # Initialize api_usage if not exists
        if 'api_usage' not in st.session_state:
            st.session_state.api_usage = {}
        
        # Use mode-specific period if not provided
        if period is None:
            period = get_historical_period()
        
        # Use dynamic TTL based on performance mode
        ttl = get_adjusted_ttl(300)  # Base 5 minutes
        
        return self._get_stock_data_cached(ticker, period, ttl)
    
    @st.cache_data(ttl=300)  # Base TTL, will be overridden
    def _get_stock_data_cached(_self, ticker: str, period: str, ttl: int) -> Dict:
        """Internal cached method"""
        try:
            api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            
            # Get all data in one go
            data = {
                "info": stock.info,
                "history": stock.history(period=period).to_dict(),
                "actions": stock.actions.to_dict() if not stock.actions.empty else {},
                "dividends": stock.dividends.to_dict() if not stock.dividends.empty else {},
                "splits": stock.splits.to_dict() if not stock.splits.empty else {},
            }
            
            # Sanitize for caching (fix Timestamp issues)
            data = sanitize_dict_for_cache(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            return {}
    
    def get_realtime_quote(self, ticker: str) -> Dict:
        """Get real-time quote (mode-aware)"""
        ttl = get_adjusted_ttl(30)  # Base 30 seconds
        return self._get_realtime_quote_cached(ticker, ttl)
    
    @st.cache_data(ttl=30)
    def _get_realtime_quote_cached(_self, ticker: str, ttl: int) -> Dict:
        """Internal cached method"""
        try:
            api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            quote = {
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "change": info.get("regularMarketChange", 0),
                "change_pct": info.get("regularMarketChangePercent", 0),
                "volume": info.get("volume", 0),
                "bid": info.get("bid", 0),
                "ask": info.get("ask", 0),
                "bid_size": info.get("bidSize", 0),
                "ask_size": info.get("askSize", 0),
                "high": info.get("dayHigh", 0),
                "low": info.get("dayLow", 0),
                "open": info.get("open", 0),
                "prev_close": info.get("previousClose", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            return quote
            
        except Exception as e:
            logger.error(f"Error fetching quote for {ticker}: {e}")
            return {}
    
    # ========== OPTIONS DATA ==========
    def get_options_chain(self, ticker: str) -> Dict:
        """Get options chain with Greeks - always enabled"""
        ttl = get_adjusted_ttl(300)  # Base 5 minutes
        return self._get_options_chain_cached(ticker, ttl)
    
    @st.cache_data(ttl=300)
    def _get_options_chain_cached(_self, ticker: str, ttl: int) -> Dict:
        """Internal cached method"""
        try:
            api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            expirations = stock.options[:6]  # Get first 6 expirations
            
            options_data = {
                "expirations": expirations,
                "chains": {}
            }
            
            for exp in expirations:
                chain = stock.option_chain(exp)
                options_data["chains"][exp] = {
                    "calls": chain.calls.to_dict() if not chain.calls.empty else {},
                    "puts": chain.puts.to_dict() if not chain.puts.empty else {}
                }
            
            return options_data
            
        except Exception as e:
            logger.error(f"Error fetching options for {ticker}: {e}")
            return {}
    
    # ========== FUNDAMENTALS ==========
    def get_fundamentals(self, ticker: str) -> Dict:
        """Get fundamental data (mode-aware)"""
        ttl = get_adjusted_ttl(3600)  # Base 1 hour
        return self._get_fundamentals_cached(ticker, ttl)
    
    @st.cache_data(ttl=3600)
    def _get_fundamentals_cached(_self, ticker: str, ttl: int) -> Dict:
        """Internal cached method"""
        try:
            api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            
            fundamentals = {
                "financials": stock.financials.to_dict() if hasattr(stock, 'financials') and stock.financials is not None else {},
                "balance_sheet": stock.balance_sheet.to_dict() if hasattr(stock, 'balance_sheet') and stock.balance_sheet is not None else {},
                "cash_flow": stock.cashflow.to_dict() if hasattr(stock, 'cashflow') and stock.cashflow is not None else {},
                "earnings": stock.earnings.to_dict() if hasattr(stock, 'earnings') and stock.earnings is not None else {},
                "recommendations": stock.recommendations.to_dict() if hasattr(stock, 'recommendations') and stock.recommendations is not None else {},
            }
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {ticker}: {e}")
            return {}
    
    # ========== INSTITUTIONAL ==========
    def get_institutional_data(self, ticker: str) -> Dict:
        """Get institutional and insider data - always enabled"""
        ttl = get_adjusted_ttl(86400)  # Base 24 hours
        return self._get_institutional_data_cached(ticker, ttl)
    
    @st.cache_data(ttl=86400)
    def _get_institutional_data_cached(_self, ticker: str, ttl: int) -> Dict:
        """Internal cached method"""
        try:
            api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            
            data = {
                "major_holders": stock.major_holders.to_dict() if hasattr(stock, 'major_holders') and stock.major_holders is not None else {},
                "institutional_holders": stock.institutional_holders.to_dict() if hasattr(stock, 'institutional_holders') and stock.institutional_holders is not None else {},
                "insider_transactions": stock.insider_transactions.to_dict() if hasattr(stock, 'insider_transactions') and stock.insider_transactions is not None else {},
                "insider_purchases": stock.insider_purchases.to_dict() if hasattr(stock, 'insider_purchases') and stock.insider_purchases is not None else {},
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching institutional data for {ticker}: {e}")
            return {}


class SentimentScraper:
    """Scrapes sentiment data from web sources (mode-aware)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.api_tracker = APIUsageTracker()
    
    def get_stocktwits_sentiment(self, ticker: str) -> Dict:
        """Get StockTwits sentiment - always enabled"""
        from src.config.performance_config import should_fetch_sentiment, get_adjusted_ttl
        
        try:
            # Check rate limit
            if not self.api_tracker.check_limit("stocktwits"):
                return {"error": "Rate limit reached for StockTwits API"}
            
            self.api_tracker.record_request("stocktwits")
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            response = self.session.get(url)
            
            if response.status_code != 200:
                return {"error": "Unable to fetch StockTwits data"}
            
            data = response.json()
            messages = data.get("messages", [])
            
            if not messages:
                return {"error": "No messages found"}
            
            # Analyze sentiment
            bullish = bearish = neutral = 0
            for msg in messages:
                sentiment = msg.get("entities", {}).get("sentiment", {}).get("basic")
                if sentiment == "Bullish":
                    bullish += 1
                elif sentiment == "Bearish":
                    bearish += 1
                else:
                    neutral += 1
            
            total = len(messages)
            return {
                "total_messages": total,
                "bullish": bullish,
                "bearish": bearish,
                "neutral": neutral,
                "bullish_pct": (bullish/total)*100 if total > 0 else 0,
                "bearish_pct": (bearish/total)*100 if total > 0 else 0,
                "sentiment_score": ((bullish-bearish)/total)*100 if total > 0 else 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching StockTwits sentiment: {e}")
            return {"error": str(e)}
    
    def get_reddit_mentions(self, ticker: str) -> Dict:
        """Get Reddit mentions (requires PRAW setup)"""
        # Simplified version without API key
        # Would need Reddit API credentials for full implementation
        return {
            "mentions": 0,
            "sentiment": "neutral",
            "top_posts": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def get_news_sentiment(self, ticker: str) -> List[Dict]:
        """Get news from yfinance - always enabled"""
        from src.config.performance_config import should_fetch_sentiment
        
        try:
            self.api_tracker.record_request("yfinance")
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            # Format news items
            formatted = []
            for item in news[:10]:  # Limit to 10 items
                formatted.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "timestamp": datetime.fromtimestamp(item.get("providerPublishTime", 0)).isoformat(),
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
