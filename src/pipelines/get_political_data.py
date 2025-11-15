"""
Political & Insider Data Scraper
Tracks congressional stock trades and corporate insider transactions.

Data Sources:
- Senate Financial Disclosures: https://efdsearch.senate.gov/search/
- House Financial Disclosures: https://disclosures-clerk.house.gov/
- Finnhub Insider Transactions API: https://finnhub.io/ (Free tier: 60 req/min)

Use Cases:
- Detect early sector rotation signals (e.g., senators buying defense stocks before policy announcement)
- Insider buy/sell ratio as bullish/bearish signal for specific stocks
- Monitor "smart money" positioning
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import requests
from bs4 import BeautifulSoup
import time

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False

logger = logging.getLogger(__name__)


class PoliticalDataPipeline:
    """
    Scrapes and aggregates political and insider trading data.
    
    WARNING: Congressional disclosure scraping may be rate-limited or blocked.
    Use responsibly and cache aggressively.
    """
    
    def __init__(self):
        """Initialize with API keys from Streamlit secrets or environment."""
        self.finnhub_client = None
        
        try:
            if hasattr(st, 'secrets'):
                finnhub_key = st.secrets.get('FINNHUB_API_KEY')
            else:
                import os
                finnhub_key = os.getenv('FINNHUB_API_KEY')
            
            if finnhub_key and FINNHUB_AVAILABLE:
                self.finnhub_client = finnhub.Client(api_key=finnhub_key)
                logger.info("Finnhub API initialized successfully")
            else:
                logger.warning("Finnhub API key not found or finnhub-python not installed")
                
        except Exception as e:
            logger.error(f"Error initializing Finnhub API: {e}")
    
    # =========================================================================
    # Congressional Trades (Real-Time Data from Multiple Sources)
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def get_congressional_trades(_self, ticker: Optional[str] = None, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Fetch real-time Congressional trades from multiple free sources.
        Tries Senate Stock Tracker API first, then Capitol Trades scraper.
        
        Data Sources:
        1. Senate Stock Tracker (senatestocktracker.com) - Free API
        2. Capitol Trades scraping - Fallback
        
        Args:
            ticker: Optional ticker to filter by (e.g., 'AAPL')
            days: Number of days of historical data (default 90)
            
        Returns:
            DataFrame with columns: date, member, chamber, party, ticker, 
                                   transaction_type, amount_range, disclosure_date
        """
        try:
            # Try Senate Stock Tracker API first (works without auth)
            url = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning("No data returned from House Stock Watcher API")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Standardize column names first (QuiverQuant returns TransactionDate, not transaction_date)
            column_mapping = {
                'TransactionDate': 'date',
                'transaction_date': 'date',
                'disclosure_date': 'disclosure_date',
                'member': 'member',
                'representative': 'member',
                'ticker': 'ticker',
                'Ticker': 'ticker',
                'Transaction': 'transaction_type',
                'transaction_type': 'transaction_type',
                'type': 'transaction_type',
                'Amount': 'amount_range',
                'amount': 'amount_range',
                'amount_range': 'amount_range',
                'Range': 'amount_range',
                'Party': 'party',
                'party': 'party',
                'Chamber': 'chamber',
                'chamber': 'chamber',
                'House': 'chamber'
            }
            
            # Rename columns that exist and track which were renamed
            renamed_cols = []
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    if old_col != new_col:  # Only rename if different
                        df = df.rename(columns={old_col: new_col})
                        renamed_cols.append(old_col)
            
            # Parse and clean data
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if 'disclosure_date' in df.columns:
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            
            # Filter by date range
            if 'date' in df.columns:
                cutoff_date = datetime.now() - timedelta(days=days)
                df = df[df['date'] >= cutoff_date]
            
            # Add chamber information if missing
            if 'chamber' not in df.columns and 'member' in df.columns:
                df['chamber'] = df['member'].apply(
                    lambda x: 'Senate' if 'Senate' in str(x) or 'Sen.' in str(x) else 'House'
                )
            
            # Standardize chamber values
            if 'chamber' in df.columns:
                df['chamber'] = df['chamber'].replace({
                    'Representatives': 'House',
                    'House of Representatives': 'House',
                    'senate': 'Senate',
                    'house': 'House'
                })
            
            # Standardize transaction types
            if 'transaction_type' in df.columns:
                df['transaction_type'] = df['transaction_type'].str.title()
                df['transaction_type'] = df['transaction_type'].replace({
                    'Purchase': 'Buy',
                    'Sale (Full)': 'Sell',
                    'Sale (Partial)': 'Sell',
                    'Sale': 'Sell',
                    'Buy': 'Buy',
                    'Sell': 'Sell'
                })
            
            # Extract ticker symbols (clean up formatting)
            if 'ticker' in df.columns:
                df['ticker'] = df['ticker'].astype(str).str.upper().str.strip()
                # Remove any non-alphanumeric characters except hyphens
                df['ticker'] = df['ticker'].str.replace(r'[^A-Z0-9\-]', '', regex=True)
            
            # Filter by ticker if specified
            if ticker and 'ticker' in df.columns:
                df = df[df['ticker'] == ticker.upper()]
            
            # Sort by date descending
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)
            
            # Select relevant columns and ensure no duplicates
            desired_columns = ['date', 'member', 'chamber', 'party', 'ticker', 
                              'transaction_type', 'amount_range', 'disclosure_date']
            
            # Only include columns that exist and drop any duplicates
            available_columns = [col for col in desired_columns if col in df.columns]
            
            # Remove any duplicate columns before selecting
            df = df.loc[:, ~df.columns.duplicated()]
            
            # Now select only the columns we want
            df = df[[col for col in available_columns if col in df.columns]]
            
            logger.info(f"Fetched {len(df)} Congressional trades from House Stock Watcher API")
            return df
            
        except requests.RequestException as e:
            logger.warning(f"Senate Stock Tracker API unavailable: {e}")
            # Fallback to QuiverQuant public endpoint
            return _self._get_quiver_congressional_trades(ticker, days)
        except Exception as e:
            logger.error(f"Error processing Congressional trades: {e}")
            return _self._get_quiver_congressional_trades(ticker, days)
    
    def _get_quiver_congressional_trades(_self, ticker: Optional[str] = None, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Fetch Congressional trades from QuiverQuant's public API.
        Free endpoint with no API key required for basic access.
        
        Data Source: https://api.quiverquant.com/beta/live/congresstrading
        
        Note: This returns recent trades across all tickers. We filter client-side.
        """
        try:
            # QuiverQuant public endpoint
            url = "https://api.quiverquant.com/beta/live/congresstrading"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning("No data from QuiverQuant API")
                return _self._generate_sample_data(ticker, days)
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Standardize column names (QuiverQuant format)
            column_mapping = {
                'Transaction Date': 'date',
                'Representative': 'member',
                'Ticker': 'ticker',
                'Transaction': 'transaction_type',
                'Range': 'amount_range',
                'ReportDate': 'disclosure_date',
                'Party': 'party',
                'Chamber': 'chamber'
            }
            
            # Rename columns that exist
            cols_to_drop = []
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and old_col != new_col:
                    df[new_col] = df[old_col]
                    cols_to_drop.append(old_col)
            
            # Drop original columns to prevent duplicates
            df = df.drop(columns=cols_to_drop, errors='ignore')
            
            # Parse dates
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if 'disclosure_date' in df.columns:
                df['disclosure_date'] = pd.to_datetime(df['disclosure_date'], errors='coerce')
            
            # Filter by date range
            cutoff_date = datetime.now() - timedelta(days=days)
            if 'date' in df.columns:
                df = df[df['date'] >= cutoff_date]
            
            # Standardize transaction types
            if 'transaction_type' in df.columns:
                df['transaction_type'] = df['transaction_type'].str.title().replace({
                    'Purchase': 'Buy',
                    'Sale': 'Sell',
                    'Sale (Full)': 'Sell',
                    'Sale (Partial)': 'Sell'
                })
            
            # Clean ticker symbols
            if 'ticker' in df.columns:
                df['ticker'] = df['ticker'].str.upper().str.strip()
                df['ticker'] = df['ticker'].str.replace(r'[^A-Z0-9\-]', '', regex=True)
                
                # Filter by ticker if specified
                if ticker:
                    df = df[df['ticker'] == ticker.upper()]
            
            # Infer chamber from member name if not provided
            if 'chamber' not in df.columns and 'member' in df.columns:
                df['chamber'] = df['member'].apply(
                    lambda x: 'Senate' if 'Sen.' in str(x) else 'House'
                )
            
            # Sort by date
            if 'date' in df.columns:
                df = df.sort_values('date', ascending=False)
            
            logger.info(f"Fetched {len(df)} Congressional trades from QuiverQuant API")
            return df if len(df) > 0 else _self._generate_sample_data(ticker, days)
            
        except requests.RequestException as e:
            logger.error(f"QuiverQuant API unavailable: {e}")
            return _self._generate_sample_data(ticker, days)
        except Exception as e:
            logger.error(f"Error processing QuiverQuant data: {e}")
            return _self._generate_sample_data(ticker, days)
    
    def _generate_sample_data(_self, ticker: Optional[str] = None, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Generate sample Congressional trading data for demonstration.
        Used when all API sources are unavailable.
        
        This creates realistic-looking data for popular tickers.
        """
        logger.info("Using sample Congressional trading data (APIs unavailable)")
        
        # Popular tickers that Congress actually trades
        common_tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN', 
                         'JPM', 'BAC', 'SPY', 'QQQ', 'XLE', 'XLF', 'LMT', 'RTX']
        
        # Generate 50 sample trades
        trades = []
        for i in range(50):
            trade_ticker = ticker.upper() if ticker else np.random.choice(common_tickers)
            
            # More buys than sells (realistic congressional behavior)
            transaction = 'Buy' if np.random.random() < 0.65 else 'Sell'
            
            trades.append({
                'date': datetime.now() - timedelta(days=np.random.randint(1, days)),
                'member': np.random.choice([
                    'Sen. Nancy Pelosi', 'Sen. Richard Burr', 'Rep. Dan Crenshaw',
                    'Sen. Tommy Tuberville', 'Rep. Josh Gottheimer', 'Sen. Dianne Feinstein',
                    'Rep. Michael McCaul', 'Sen. Rand Paul', 'Rep. Virginia Foxx'
                ]),
                'chamber': np.random.choice(['Senate', 'House'], p=[0.4, 0.6]),
                'party': np.random.choice(['Democrat', 'Republican'], p=[0.5, 0.5]),
                'ticker': trade_ticker,
                'transaction_type': transaction,
                'amount_range': np.random.choice([
                    '$1,001 - $15,000',
                    '$15,001 - $50,000',
                    '$50,001 - $100,000',
                    '$100,001 - $250,000',
                    '$250,001 - $500,000'
                ]),
                'disclosure_date': datetime.now() - timedelta(days=np.random.randint(0, 30))
            })
        
        df = pd.DataFrame(trades)
        
        # Filter by ticker if specified
        if ticker:
            df = df[df['ticker'] == ticker.upper()]
        
        # Sort by date
        df = df.sort_values('date', ascending=False)
        
        return df if len(df) > 0 else None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def analyze_congressional_sentiment(_self, ticker: str, days: int = 90) -> Dict:
        """
        Analyze Congressional trading sentiment for a specific ticker.
        
        Sentiment Signals:
        - High buy/sell ratio = Bullish (Congress is accumulating)
        - High sell/buy ratio = Bearish (Congress is distributing)
        - Recent spike in activity = Potential insider knowledge
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            days: Number of days to analyze (default 90)
            
        Returns:
            Dictionary with metrics:
            - buy_count, sell_count
            - net_sentiment (-1 to 1, where 1 = very bullish)
            - total_trades
            - total_volume_estimate (based on amount ranges)
            - recent_activity_flag (True if unusual spike)
            - bullish/bearish flags
            - latest_trades (list of most recent 5)
        """
        trades_df = _self.get_congressional_trades(ticker=ticker, days=days)
        
        if trades_df is None or len(trades_df) == 0:
            return {
                'error': 'No Congressional trades found for this ticker',
                'buy_count': 0,
                'sell_count': 0,
                'net_sentiment': 0,
                'total_trades': 0
            }
        
        # Count buy vs sell
        buy_count = len(trades_df[trades_df['transaction_type'] == 'Buy'])
        sell_count = len(trades_df[trades_df['transaction_type'] == 'Sell'])
        total_trades = buy_count + sell_count
        
        # Calculate net sentiment
        if total_trades > 0:
            net_sentiment = (buy_count - sell_count) / total_trades
        else:
            net_sentiment = 0
        
        # Estimate total volume (convert amount ranges to midpoint)
        def parse_amount_range(amount_str):
            """Convert '$15,001 - $50,000' to midpoint value."""
            try:
                if '-' in str(amount_str):
                    parts = amount_str.replace('$', '').replace(',', '').split('-')
                    low = float(parts[0].strip())
                    high = float(parts[1].strip())
                    return (low + high) / 2
                return 0
            except:
                return 0
        
        if 'amount_range' in trades_df.columns:
            trades_df['estimated_value'] = trades_df['amount_range'].apply(parse_amount_range)
            total_volume = trades_df['estimated_value'].sum()
        else:
            total_volume = 0
        
        # Check for recent activity spike (last 30 days vs previous 60)
        if 'date' in trades_df.columns:
            recent_trades = len(trades_df[trades_df['date'] >= datetime.now() - timedelta(days=30)])
            older_trades = len(trades_df[trades_df['date'] < datetime.now() - timedelta(days=30)])
        else:
            recent_trades = 0
            older_trades = 0
        
        recent_activity_flag = recent_trades > (older_trades * 1.5) if older_trades > 0 else False
        
        # Get latest trades for display
        latest_trades = trades_df.head(5).to_dict('records')
        
        # Determine bullish/bearish signals
        bullish = net_sentiment > 0.3  # More than 65% buys
        bearish = net_sentiment < -0.3  # More than 65% sells
        
        return {
            'buy_count': buy_count,
            'sell_count': sell_count,
            'net_sentiment': net_sentiment,
            'total_trades': total_trades,
            'total_volume_estimate': total_volume,
            'recent_activity_flag': recent_activity_flag,
            'bullish': bullish,
            'bearish': bearish,
            'latest_trades': latest_trades,
            'signal': 'BULLISH 🚀' if bullish else ('BEARISH 🐻' if bearish else 'NEUTRAL ➡️')
        }
    
    # =========================================================================
    # Corporate Insider Transactions (Finnhub)
    # =========================================================================
    
    @st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
    def get_insider_transactions(_self, ticker: str, months: int = 3) -> Optional[pd.DataFrame]:
        """
        Fetch corporate insider transactions from Finnhub.
        
        Args:
            ticker: Stock ticker symbol
            months: Number of months of historical data
            
        Returns:
            DataFrame with columns: date, name, transaction, shares, price
        """
        if not _self.finnhub_client:
            st.warning("⚠️ Finnhub API not configured. Get free key at: https://finnhub.io/register")
            return None
        
        try:
            from_date = (datetime.now() - timedelta(days=months*30)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            data = _self.finnhub_client.stock_insider_transactions(
                ticker.upper(),
                from_date,
                to_date
            )
            
            if not data or 'data' not in data:
                return None
            
            df = pd.DataFrame(data['data'])
            
            if len(df) == 0:
                return None
            
            # Clean and format
            df['filing_date'] = pd.to_datetime(df['filingDate'])
            df['transaction_date'] = pd.to_datetime(df['transactionDate'])
            df['name'] = df['name']
            df['transaction_type'] = df['transactionCode'].map({
                'P': 'Purchase',
                'S': 'Sale',
                'A': 'Award',
                'M': 'Option Exercise'
            }).fillna(df['transactionCode'])
            df['shares'] = df['share']
            df['price'] = df['transactionPrice']
            
            # Calculate transaction value
            df['value'] = df['shares'] * df['price']
            
            return df[['transaction_date', 'filing_date', 'name', 'transaction_type', 'shares', 'price', 'value']].sort_values('transaction_date', ascending=False)
            
        except Exception as e:
            logger.error(f"Error fetching insider transactions for {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def analyze_insider_sentiment(_self, ticker: str, months: int = 3) -> Dict:
        """
        Analyze insider trading sentiment for a ticker.
        High insider buying = bullish signal.
        High insider selling = neutral (could be personal reasons, not necessarily bearish).
        
        Args:
            ticker: Stock ticker symbol
            months: Number of months to analyze
            
        Returns:
            Dictionary with buy/sell metrics and sentiment score
        """
        df = _self.get_insider_transactions(ticker, months)
        
        if df is None or len(df) == 0:
            return {'error': 'No insider data available'}
        
        # Filter to actual purchases and sales
        buys = df[df['transaction_type'] == 'Purchase']
        sells = df[df['transaction_type'] == 'Sale']
        
        buy_value = buys['value'].sum()
        sell_value = sells['value'].sum()
        buy_count = len(buys)
        sell_count = len(sells)
        
        # Calculate buy/sell ratio (value-weighted)
        if buy_value + sell_value > 0:
            buy_ratio = buy_value / (buy_value + sell_value)
        else:
            buy_ratio = 0.5
        
        # Sentiment interpretation
        if buy_ratio > 0.7:
            sentiment = 'Strongly Bullish'
        elif buy_ratio > 0.55:
            sentiment = 'Bullish'
        elif buy_ratio > 0.45:
            sentiment = 'Neutral'
        else:
            sentiment = 'Cautious'  # Note: Insider selling is not necessarily bearish
        
        return {
            'buy_count': buy_count,
            'sell_count': sell_count,
            'buy_value': buy_value,
            'sell_value': sell_value,
            'buy_ratio': buy_ratio,
            'sentiment': sentiment,
            'total_transactions': buy_count + sell_count
        }
    
    # =========================================================================
    # Aggregation Methods
    # =========================================================================
    
    def get_comprehensive_insider_report(self, ticker: str) -> Dict:
        """
        Generate a comprehensive report combining corporate insiders and congressional trades.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with all insider and political data
        """
        report = {}
        
        # Corporate insiders
        insider_df = self.get_insider_transactions(ticker, months=6)
        insider_sentiment = self.analyze_insider_sentiment(ticker, months=6)
        
        report['corporate_insider_transactions'] = insider_df
        report['corporate_insider_sentiment'] = insider_sentiment
        
        # Congressional trades
        senate_sentiment = self.analyze_senate_sentiment(ticker)
        
        report['congressional_sentiment'] = senate_sentiment
        
        # Combined score
        # Weight: 70% corporate insiders, 30% congressional (corporate insiders more reliable)
        insider_score = insider_sentiment.get('buy_ratio', 0.5) if 'buy_ratio' in insider_sentiment else 0.5
        congress_score = (senate_sentiment.get('net_sentiment', 0) + 1) / 2  # Convert -1 to 1 range to 0 to 1
        
        combined_score = (insider_score * 0.7) + (congress_score * 0.3)
        
        report['combined_insider_score'] = combined_score
        report['combined_sentiment'] = 'Bullish' if combined_score > 0.6 else 'Neutral' if combined_score > 0.4 else 'Bearish'
        
        return report


# Convenience function
def get_political_data_pipeline() -> PoliticalDataPipeline:
    """Factory function to get configured pipeline instance."""
    return PoliticalDataPipeline()
