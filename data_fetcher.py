import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import timedelta
from alpha_vantage.fundamentaldata import FundamentalData

# This function (get_stock_object) is generally useful for creating and caching
# yfinance Ticker objects, which are then passed to other data fetching functions.
# It's assumed to be part of the full data_fetcher.py file.
@st.cache_data(ttl=3600)
def get_stock_object(ticker: str) -> yf.Ticker:
    """Creates and caches a yfinance Ticker object."""
    return yf.Ticker(ticker)

# Alias for compatibility
def get_ticker(ticker: str) -> yf.Ticker:
    """Alias for get_stock_object - creates and caches a yfinance Ticker object."""
    return get_stock_object(ticker)

# This function (get_company_info) is being modified/added to handle
# invalid tickers by returning None, preventing redundant calls.
@st.cache_data(ttl=3600)
def get_company_info(_stock: yf.Ticker):
    """
    Fetches general company information using yfinance.
    Returns a dictionary of company info or None if the ticker is invalid or data is not found.
    This function is crucial for competitor data retrieval, handling validation internally.
    """
    try:
        info_data = _stock.info
        # yfinance.Ticker.info returns an empty dict or a dict with 'quoteType': 'NONE'
        # if the ticker is invalid or data is not available.
        # Check for essential fields to confirm validity.
        if not info_data or 'longName' not in info_data or 'marketCap' not in info_data:
            return None

        # Extract relevant fields
        info = {
            'symbol': info_data.get('symbol'),
            'longName': info_data.get('longName'),
            'sector': info_data.get('sector'),
            'industry': info_data.get('industry'),
            'marketCap': info_data.get('marketCap'),
            'country': info_data.get('country'),
            'financialCurrency': info_data.get('financialCurrency'),
            'logo_url': info_data.get('logo_url'),
            'website': info_data.get('website'),
            'fullTimeEmployees': info_data.get('fullTimeEmployees'),
        }
        return info
    except Exception:
        # Catch any other potential errors during info retrieval (e.g., network issues)
        return None

@st.cache_data(ttl=3600)
def get_cash_flow(_stock: yf.Ticker):
    return _stock.quarterly_cash_flow

@st.cache_data(ttl=1800)
def get_stock_news(_stock: yf.Ticker):
    return _stock.news

@st.cache_data(ttl=86400)
def get_analyst_recommendations(_stock: yf.Ticker):
    """Fetches analyst recommendations."""
    try:
        # Try the newer property name first
        if hasattr(_stock, 'recommendations'):
            return _stock.recommendations
        # Fall back to old property name
        elif hasattr(_stock, 'get_recommendations'):
            return _stock.get_recommendations()
        else:
            # Return empty DataFrame if neither exists
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_earnings_calendar(api_key):
    """Fetches the earnings calendar from Alpha Vantage."""
    try:
        fd = FundamentalData(key=api_key, output_format='pandas')
        df, _ = fd.get_earnings_calendar(horizon='3month')
        # FIX: The API returns dates as strings. Coerce errors to NaT (Not a Time)
        # which will be dropped by the subsequent filter.
        df['reportDate'] = pd.to_datetime(df['reportDate'], errors='coerce')
        # Line 64 was an empty line in the original snippet.

        # Log how many dates failed to parse
        failed_dates = df['reportDate'].isna().sum()
        if failed_dates > 0:
            st.warning(f"Earnings calendar: {failed_dates} entries had invalid dates and were removed.")

        today = pd.to_datetime('today').normalize()
        thirty_days_from_now = today + timedelta(days=30)

        df = df[(df['reportDate'] >= today) & (df['reportDate'] <= thirty_days_from_now)]
        df = df[['symbol', 'name', 'reportDate', 'estimate']]
        df.columns = ['Ticker', 'Company Name', 'Report Date', 'Analyst EPS']

        return df.sort_values(by="Report Date")
    except Exception as e:
        st.error(f"Failed to retrieve earnings calendar from Alpha Vantage: {e}")
        st.info("Please ensure your `alpha_vantage` API key is in .streamlit/secrets.toml")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_competitor_data(competitor_tickers):
    """
    Fetches company information for a list of competitor tickers.
    Optimized to call get_company_info only once per ticker.
    """
    all_info = []
    for ticker_symbol in competitor_tickers:
        try:
            # Use the cached get_stock_object to get the yf.Ticker object
            stock_obj = get_stock_object(ticker_symbol)
            
            # Call get_company_info ONLY ONCE per ticker.
            # get_company_info now handles internal validation and returns None for invalid tickers.
            info = get_company_info(stock_obj)

            # Validate using the already fetched 'info'. If 'info' is None, the ticker was invalid.
            if info:
                all_info.append(info)
            else:
                # Log or display a warning for invalid/unavailable competitor data
                st.warning(f"Could not retrieve full company data for competitor: {ticker_symbol}. It might be an invalid ticker or data is unavailable.")
        except Exception as e:
            # Catch any unexpected errors during processing a specific ticker
            st.error(f"An unexpected error occurred while processing competitor {ticker_symbol}: {e}")
            # Do not append partial or invalid data for this ticker
    return all_info


@st.cache_data(ttl=3600)
def get_stock_price_data(ticker: str, period: str = "2y"):
    """
    Fetches historical price data for a stock.

    Args:
        ticker: Stock ticker symbol
        period: Time period (e.g., '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

    Returns:
        DataFrame with historical price data including OHLCV
    """
    try:
        stock = get_stock_object(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"Failed to fetch price data for {ticker}: {e}")
        return pd.DataFrame()