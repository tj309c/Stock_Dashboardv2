"""
Market Data Pipeline
Consolidated wrapper for stock, crypto, and options data fetching.

Data Sources:
- yfinance: Stock prices, fundamentals, options chains
- ccxt: Cryptocurrency exchange data (200+ exchanges)
- Alpha Vantage: Fundamental data, news, technical indicators

Use Cases:
- Centralized data fetching with caching
- Multi-exchange crypto data for arbitrage detection
- Historical and real-time price data
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

try:
    from alpha_vantage.timeseries import TimeSeries
    from alpha_vantage.fundamentaldata import FundamentalData
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False

logger = logging.getLogger(__name__)


class MarketDataPipeline:
    """
    Unified interface for fetching market data from multiple sources.
    """
    
    def __init__(self):
        """Initialize with API keys from Streamlit secrets or environment."""
        self.alpha_vantage_key = None
        
        try:
            if hasattr(st, 'secrets'):
                self.alpha_vantage_key = st.secrets.get('ALPHA_VANTAGE_API_KEY')
            else:
                import os
                self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            
            if self.alpha_vantage_key and ALPHA_VANTAGE_AVAILABLE:
                self.ts_client = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
                self.fd_client = FundamentalData(key=self.alpha_vantage_key, output_format='pandas')
                logger.info("Alpha Vantage API initialized")
            else:
                logger.warning("Alpha Vantage API key not found")
                
        except Exception as e:
            logger.error(f"Error initializing Alpha Vantage: {e}")
    
    # =========================================================================
    # Stock Data (yfinance)
    # =========================================================================
    
    @st.cache_data(ttl=300, show_spinner=False)  # 5-minute cache for real-time data
    def get_stock_data(_self, ticker: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """
        Fetch historical stock price data.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with OHLCV data
        """
        if not YFINANCE_AVAILABLE:
            st.warning("⚠️ yfinance not installed. Run: pip install yfinance")
            return None
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if len(df) == 0:
                logger.warning(f"No data found for {ticker}")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)  # 1-hour cache
    def get_stock_info(_self, ticker: str) -> Optional[Dict]:
        """
        Fetch stock fundamentals and company info.
        
        Returns:
            Dictionary with company info, metrics, fundamentals
        """
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_options_chain(_self, ticker: str) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Fetch options chain data.
        
        Returns:
            Tuple of (calls_df, puts_df)
        """
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            
            if len(expirations) == 0:
                return None
            
            # Get nearest expiration
            nearest_exp = expirations[0]
            opt_chain = stock.option_chain(nearest_exp)
            
            return (opt_chain.calls, opt_chain.puts)
            
        except Exception as e:
            logger.error(f"Error fetching options for {ticker}: {e}")
            return None
    
    # =========================================================================
    # Crypto Data (ccxt)
    # =========================================================================
    
    @st.cache_data(ttl=60, show_spinner=False)  # 1-minute cache for crypto
    def get_crypto_ticker(_self, symbol: str, exchange_name: str = 'binance') -> Optional[Dict]:
        """
        Fetch current crypto ticker data from exchange.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            exchange_name: Exchange name (binance, coinbase, kraken, etc.)
            
        Returns:
            Dictionary with price, volume, bid/ask
        """
        if not CCXT_AVAILABLE:
            st.warning("⚠️ ccxt not installed. Run: pip install ccxt")
            return None
        
        try:
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class()
            ticker = exchange.fetch_ticker(symbol)
            
            return {
                'symbol': ticker['symbol'],
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['quoteVolume'],
                'change_24h': ticker.get('percentage', 0),
                'exchange': exchange_name
            }
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} from {exchange_name}: {e}")
            return None
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_multi_exchange_prices(_self, symbol: str, exchanges: List[str] = None) -> Dict[str, Dict]:
        """
        Fetch prices for same trading pair across multiple exchanges.
        Used for arbitrage detection.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            exchanges: List of exchange names (default: ['binance', 'coinbase', 'kraken'])
            
        Returns:
            Dictionary mapping exchange_name -> ticker_data
        """
        if not CCXT_AVAILABLE:
            return {}
        
        if exchanges is None:
            exchanges = ['binance', 'coinbase', 'kraken', 'bybit', 'okx']
        
        results = {}
        
        for exchange_name in exchanges:
            ticker = _self.get_crypto_ticker(symbol, exchange_name)
            if ticker:
                results[exchange_name] = ticker
        
        return results
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_crypto_ohlcv(_self, symbol: str, exchange_name: str = 'binance', 
                         timeframe: str = '1d', limit: int = 365) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for cryptocurrency.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            exchange_name: Exchange name
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        if not CCXT_AVAILABLE:
            return None
        
        try:
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class()
            
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} from {exchange_name}: {e}")
            return None
    
    # =========================================================================
    # Alpha Vantage (Fundamental Data)
    # =========================================================================
    
    @st.cache_data(ttl=86400, show_spinner=False)  # 24-hour cache
    def get_company_overview(_self, ticker: str) -> Optional[Dict]:
        """
        Fetch company fundamental overview from Alpha Vantage.
        Includes PE ratio, EPS, market cap, sector, industry.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with fundamental metrics
        """
        if not _self.alpha_vantage_key or not ALPHA_VANTAGE_AVAILABLE:
            st.warning("⚠️ Alpha Vantage API key not configured")
            return None
        
        try:
            data, _ = _self.fd_client.get_company_overview(ticker)
            return data.to_dict()
            
        except Exception as e:
            logger.error(f"Error fetching company overview for {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def get_earnings_history(_self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch historical earnings reports.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with earnings dates, EPS estimates, actuals
        """
        if not _self.alpha_vantage_key or not ALPHA_VANTAGE_AVAILABLE:
            return None
        
        try:
            data, _ = _self.fd_client.get_earnings(ticker)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching earnings for {ticker}: {e}")
            return None
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    def get_comprehensive_ticker_data(self, ticker: str, is_crypto: bool = False) -> Dict:
        """
        Fetch all available data for a ticker in one call.
        
        Args:
            ticker: Ticker symbol or crypto pair
            is_crypto: If True, fetch crypto data; if False, fetch stock data
            
        Returns:
            Dictionary with all available data
        """
        result = {}
        
        if is_crypto:
            result['current_price'] = self.get_crypto_ticker(ticker)
            result['historical_data'] = self.get_crypto_ohlcv(ticker)
            result['multi_exchange'] = self.get_multi_exchange_prices(ticker)
        else:
            result['historical_data'] = self.get_stock_data(ticker)
            result['info'] = self.get_stock_info(ticker)
            result['options'] = self.get_options_chain(ticker)
            result['fundamentals'] = self.get_company_overview(ticker)
            result['earnings'] = self.get_earnings_history(ticker)
        
        return result


# Convenience function
def get_market_data_pipeline() -> MarketDataPipeline:
    """Factory function to get configured pipeline instance."""
    return MarketDataPipeline()
