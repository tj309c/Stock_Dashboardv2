"""
Fast data fetcher using yahooquery for batch operations.
Use this for fetching multiple tickers at once (competitors, leaderboards, portfolios).
For single ticker operations, continue using yfinance via data_fetcher.py
"""
import streamlit as st
import pandas as pd
from yahooquery import Ticker
from typing import List, Dict, Any


@st.cache_data(ttl=900)
def get_multiple_tickers_info(ticker_list: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch company info for multiple tickers in one batch request.
    Much faster than calling yfinance sequentially.

    Args:
        ticker_list: List of ticker symbols (e.g., ['AAPL', 'MSFT', 'GOOGL'])

    Returns:
        Dictionary mapping ticker symbols to their info dicts
    """
    if not ticker_list:
        return {}

    try:
        tickers = Ticker(ticker_list, asynchronous=True)

        # Get summary detail (similar to yfinance .info)
        summary_detail = tickers.summary_detail

        # Get quote type for additional metadata
        quote_type = tickers.quote_type

        # Get key stats
        key_stats = tickers.key_stats

        # Combine the data
        result = {}
        for ticker_symbol in ticker_list:
            try:
                ticker_info = {}

                # Add summary detail data
                if isinstance(summary_detail, dict) and ticker_symbol in summary_detail:
                    ticker_data = summary_detail[ticker_symbol]
                    if not isinstance(ticker_data, str):  # Check it's not an error message
                        ticker_info.update(ticker_data)

                # Add quote type data
                if isinstance(quote_type, dict) and ticker_symbol in quote_type:
                    ticker_data = quote_type[ticker_symbol]
                    if not isinstance(ticker_data, str):
                        ticker_info.update(ticker_data)

                # Add key stats
                if isinstance(key_stats, dict) and ticker_symbol in key_stats:
                    ticker_data = key_stats[ticker_symbol]
                    if not isinstance(ticker_data, str):
                        ticker_info.update(ticker_data)

                # Only add if we got valid data
                if ticker_info:
                    result[ticker_symbol] = ticker_info

            except Exception as e:
                st.warning(f"Could not fetch data for {ticker_symbol}: {e}")
                continue

        return result

    except Exception as e:
        st.error(f"Error fetching batch ticker data: {e}")
        return {}


@st.cache_data(ttl=3600)
def get_multiple_tickers_price_data(ticker_list: List[str], period: str = '1y') -> Dict[str, pd.DataFrame]:
    """
    Fetch price history for multiple tickers efficiently.

    Args:
        ticker_list: List of ticker symbols
        period: Time period (e.g., '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

    Returns:
        Dictionary mapping ticker symbols to their price DataFrames
    """
    if not ticker_list:
        return {}

    try:
        tickers = Ticker(ticker_list, asynchronous=True)

        # Get historical data
        history = tickers.history(period=period)

        # yahooquery returns a multi-index DataFrame
        # Convert to dict of DataFrames (one per ticker)
        result = {}

        if isinstance(history, pd.DataFrame) and not history.empty:
            # Group by ticker symbol (first level of multi-index)
            for ticker_symbol in ticker_list:
                try:
                    if ticker_symbol in history.index.get_level_values(0):
                        ticker_df = history.xs(ticker_symbol, level=0)
                        result[ticker_symbol] = ticker_df
                except Exception:
                    continue

        return result

    except Exception as e:
        st.error(f"Error fetching batch price data: {e}")
        return {}


@st.cache_data(ttl=3600)
def get_competitor_data_fast(competitor_tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Fast version of get_competitor_data using yahooquery batch requests.
    Replaces the sequential yfinance approach in data_fetcher.py

    Args:
        competitor_tickers: List of competitor ticker symbols

    Returns:
        List of dictionaries containing competitor info
    """
    if not competitor_tickers:
        return []

    # Get all data in one batch
    all_info = get_multiple_tickers_info(competitor_tickers)

    # Format the results
    result = []
    for ticker_symbol in competitor_tickers:
        if ticker_symbol in all_info:
            info = all_info[ticker_symbol]

            # Check for essential fields to confirm validity
            if info.get('longName') or info.get('shortName'):
                # Extract relevant fields in the format expected by the app
                formatted_info = {
                    'symbol': ticker_symbol,
                    'longName': info.get('longName', info.get('shortName', ticker_symbol)),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                    'marketCap': info.get('marketCap'),
                    'country': info.get('country'),
                    'financialCurrency': info.get('financialCurrency'),
                    'logo_url': info.get('logo_url'),
                    'website': info.get('website'),
                    'fullTimeEmployees': info.get('fullTimeEmployees'),
                }
                result.append(formatted_info)
            else:
                st.warning(f"Could not retrieve full company data for competitor: {ticker_symbol}. It might be an invalid ticker or data is unavailable.")

    return result


@st.cache_data(ttl=1800)
def get_leaderboard_data_fast(ticker_list: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fast data fetching for squeeze leaderboard.
    Gets both info and price data for multiple tickers in batch.

    Args:
        ticker_list: List of ticker symbols to analyze

    Returns:
        Dictionary with 'info' and 'price_data' for each ticker
    """
    if not ticker_list:
        return {}

    # Fetch both info and price data in parallel
    all_info = get_multiple_tickers_info(ticker_list)
    all_prices = get_multiple_tickers_price_data(ticker_list, period='6mo')  # 6 months for technical analysis

    # Combine results
    result = {}
    for ticker_symbol in ticker_list:
        ticker_data = {}

        if ticker_symbol in all_info:
            ticker_data['info'] = all_info[ticker_symbol]
        else:
            ticker_data['info'] = {}

        if ticker_symbol in all_prices:
            ticker_data['price_data'] = all_prices[ticker_symbol]
        else:
            ticker_data['price_data'] = pd.DataFrame()

        # Only include if we have at least some data
        if ticker_data['info'] or not ticker_data['price_data'].empty:
            result[ticker_symbol] = ticker_data

    return result
