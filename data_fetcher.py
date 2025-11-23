import yfinance as yf
import requests
import streamlit as st
import pandas as pd
from datetime import timedelta
from alpha_vantage.fundamentaldata import FundamentalData
from error_logger import log_error, log_warning

# Import fast batch fetcher for multi-ticker operations
try:
    from fast_data_fetcher import get_competitor_data_fast
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False

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
            log_warning(
                "Invalid or incomplete company info data",
                "data_fetcher.get_company_info",
                {"symbol": getattr(_stock, 'ticker', 'Unknown')}
            )
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
    except Exception as e:
        # Catch any other potential errors during info retrieval (e.g., network issues)
        log_error(
            e,
            "data_fetcher.get_company_info",
            {"symbol": getattr(_stock, 'ticker', 'Unknown')}
        )
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
def get_competitor_data(competitor_tickers, use_fast=True):
    """
    Fetches company information for a list of competitor tickers.

    Args:
        competitor_tickers: List of ticker symbols
        use_fast: If True, uses yahooquery for batch fetching (5-10x faster)
                  If False, uses yfinance sequential fetching (more reliable)

    Returns:
        List of competitor info dictionaries
    """
    # Use fast batch fetching if available and requested
    if use_fast and YAHOOQUERY_AVAILABLE:
        return get_competitor_data_fast(competitor_tickers)

    # Fallback to original yfinance sequential method
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
def get_eps_estimates_list(ticker: str) -> list:
    """
    Aggregate analyst EPS estimates from available providers.

    Sources (in order):
      - Alpha Vantage earnings calendar (if API key configured in st.secrets['alpha_vantage']['api_key'])
      - yfinance Ticker.earnings_dates / calendar fields (if available)

    Returns:
        list of floats (may be empty). Values are deduplicated and sorted.
    """
    estimates = []

    # 1) Alpha Vantage calendar (global earnings calendar) -> filter by ticker
    try:
        if 'alpha_vantage' in st.secrets and 'api_key' in st.secrets['alpha_vantage']:
            api_key = st.secrets['alpha_vantage']['api_key']
            df = get_earnings_calendar(api_key)

            if not df.empty and 'Ticker' in df.columns and 'Analyst EPS' in df.columns:
                # match ticker case-insensitively
                rows = df[df['Ticker'].str.upper() == ticker.upper()]
                for v in rows['Analyst EPS'].tolist():
                    try:
                        # Accept numeric types or numeric strings
                        val = float(v)
                        estimates.append(val)
                    except Exception:
                        continue
    except Exception:
        # non-fatal — continue to next source
        pass

    # 2) yfinance earnings_dates / calendar
    try:
        stock = get_stock_object(ticker)

        # earnings_dates may be a dataframe with an 'EPS Estimate' column or similar
        if hasattr(stock, 'earnings_dates'):
            ed = stock.earnings_dates
            if ed is not None and hasattr(ed, 'columns'):
                # find any column with 'eps' or 'estimate' in the name
                for col in ed.columns:
                    col_lower = col.lower()
                    if 'eps' in col_lower or 'estimate' in col_lower:
                        # attempt to extract numeric entries
                        for v in ed[col].dropna().tolist():
                            try:
                                estimates.append(float(v))
                            except Exception:
                                continue
                        break

        # Another common place: stock.calendar may have 'Earnings Average/Low/High' accessible
        if hasattr(stock, 'calendar'):
            cal = stock.calendar
            if cal and isinstance(cal, dict):
                # check keys like 'Earnings Average', 'Earnings Low', 'Earnings High'
                keys = ['Earnings Average', 'Earnings Low', 'Earnings High']
                for k in keys:
                    if k in cal and pd.notna(cal.get(k)):
                        try:
                            estimates.append(float(cal.get(k)))
                        except Exception:
                            continue
    except Exception:
        pass

    # 3) Additional provider fallbacks: Finnhub, FMP (FMP Cloud), Polygon
    def _extract_numbers_from_json(obj):
        """Recursively find numeric values in dict/list where key names look like 'eps' or 'estimate'"""
        found = []

        if isinstance(obj, dict):
            for k, v in obj.items():
                k_lower = str(k).lower()
                if isinstance(v, (int, float)) and ('eps' in k_lower or 'estimate' in k_lower or 'est' in k_lower):
                    try:
                        found.append(float(v))
                    except Exception:
                        pass
                elif isinstance(v, (list, dict)):
                    found.extend(_extract_numbers_from_json(v))
                else:
                    # If value is a string that can be cast to float and key contains 'estimate' or 'eps'
                    if isinstance(v, str) and ('eps' in k_lower or 'estimate' in k_lower or 'est' in k_lower):
                        try:
                            found.append(float(v))
                        except Exception:
                            pass

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    found.extend(_extract_numbers_from_json(item))
                elif isinstance(item, (int, float)):
                    found.append(float(item))
                elif isinstance(item, str):
                    try:
                        found.append(float(item))
                    except Exception:
                        pass

        return found

    try:
        # Finnhub
        if 'FINNHUB_API_KEY' in st.secrets:
            key = st.secrets['FINNHUB_API_KEY']
            url = f"https://finnhub.io/api/v1/stock/earnings?symbol={ticker}&token={key}"
            r = requests.get(url, timeout=6)
            if r.ok:
                data = r.json()
                estimates.extend([float(x) for x in _extract_numbers_from_json(data)])
    except Exception:
        pass

    try:
        # FinancialModelingPrep (FMP)
        if 'FMP_API_KEY' in st.secrets:
            key = st.secrets['FMP_API_KEY']
            url = f"https://financialmodelingprep.com/api/v3/earnings-estimates/{ticker}?apikey={key}"
            r = requests.get(url, timeout=6)
            if r.ok:
                data = r.json()
                # the API might return list or dict
                estimates.extend([float(x) for x in _extract_numbers_from_json(data)])
    except Exception:
        pass

    try:
        # Polygon (earnings reference)
        if 'POLYGON_API_KEY' in st.secrets:
            key = st.secrets['POLYGON_API_KEY']
            url = f"https://api.polygon.io/v3/reference/earnings?ticker={ticker}&apiKey={key}"
            r = requests.get(url, timeout=6)
            if r.ok:
                data = r.json()
                estimates.extend([float(x) for x in _extract_numbers_from_json(data)])
    except Exception:
        pass

    # Deduplicate, filter NaN, sort
    cleaned = sorted({float(x) for x in estimates if x is not None and not (isinstance(x, float) and pd.isna(x))})
    return cleaned


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