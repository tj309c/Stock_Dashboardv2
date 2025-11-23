import streamlit as st
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_fetcher import get_ticker, get_company_info, get_stock_price_data
from squeeze_analyzer import calculate_squeeze_score
from performance_optimizer import PerformanceMonitor, optimize_dataframe

# Import fast batch fetcher for significant speedup
try:
    from fast_data_fetcher import get_leaderboard_data_fast
    from app_logic import _add_technical_indicators
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False

def _process_single_ticker(ticker, include_reddit, is_leaderboard=True):
    """
    Helper function to process a single ticker.
    Returns a tuple of (ticker_data_dict, sentiment_data) or (None, None) on failure.
    """
    try:
        # 1. Fetch required data
        stock_obj = get_ticker(ticker)
        info = get_company_info(stock_obj)
        price_data = get_stock_price_data(stock_obj)

        if not info or price_data.empty:
            return None, None

        # 2. Calculate necessary technical indicators for the squeeze score
        price_data.ta.rsi(length=14, append=True)
        price_data.dropna(inplace=True)

        # 3. Calculate the squeeze score
        score, components = calculate_squeeze_score(info, price_data, include_reddit, is_leaderboard=is_leaderboard)

        # Extract sentiment data if it exists
        sentiment_data = None
        if include_reddit and 'Social Buzz' in components and components['Social Buzz'].get('raw_data'):
            sentiment_data = components['Social Buzz']['raw_data']

        # 4. Prepare result
        ticker_data = {
            "Ticker": ticker,
            "Dashboard Link": f"/?ticker={ticker}",
            "Company": info.get('shortName', 'N/A'),
            "Squeeze Score": score,
            "Short % Float": components.get('Short Interest', {}).get('value', 0),
            "Volume Z-Score": components.get('Volume Z-Score', {}).get('value', 0),
            "Social Mentions (7d)": components.get('Social Buzz', {}).get('value', 0) if include_reddit else 'N/A'
        }
        return ticker_data, sentiment_data
    except Exception:
        # If any ticker fails, return None
        return None, None

@st.cache_data(ttl=3600) # Cache leaderboard for 1 hour
def generate_squeeze_leaderboard(tickers, include_reddit=True, use_fast=True):
    """
    Scans a list of tickers and ranks them by their USSI score.
    OPTIMIZED with parallel execution and memory optimization.

    Args:
        tickers (list): A list of stock tickers to scan.
        include_reddit (bool): Flag to include Reddit sentiment in the score.
        use_fast (bool): If True, uses yahooquery batch fetching (10-20x faster).

    Returns:
        A pandas DataFrame containing the ranked leaderboard.
    """
    with PerformanceMonitor(f"leaderboard_generation_{len(tickers)}_tickers"):
        # Use fast batch method if available
        if use_fast and YAHOOQUERY_AVAILABLE:
            return _generate_squeeze_leaderboard_fast(tickers, include_reddit)

        # Fallback to original parallel method
        leaderboard_data = []
        sentiment_data_dict = {}
        progress_bar = st.progress(0, text="Initializing parallel scan...")

        completed_count = 0
        total_tickers = len(tickers)

    # Use ThreadPoolExecutor for parallel processing
    # max_workers=5 is a good balance between speed and not overwhelming APIs
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_ticker = {
            executor.submit(_process_single_ticker, ticker, include_reddit): ticker
            for ticker in tickers
        }

        # Process results as they complete
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            completed_count += 1
            progress_bar.progress(completed_count / total_tickers, text=f"Scanned {completed_count}/{total_tickers} stocks...")

            try:
                ticker_data, sentiment_data = future.result()
                if ticker_data is not None:
                    leaderboard_data.append(ticker_data)
                    if sentiment_data is not None:
                        sentiment_data_dict[ticker] = sentiment_data
            except Exception:
                # Skip failed tickers
                continue

        progress_bar.empty()

        if not leaderboard_data:
            return pd.DataFrame(), {}

        df = pd.DataFrame(leaderboard_data).sort_values(by="Squeeze Score", ascending=False).reset_index(drop=True)

        # Optimize DataFrame memory usage (60-80% reduction)
        df = optimize_dataframe(df)

        return df, sentiment_data_dict


def _generate_squeeze_leaderboard_fast(tickers, include_reddit=True):
    """
    Fast version using yahooquery batch fetching (10-20x faster than sequential).
    """
    leaderboard_data = []
    sentiment_data_dict = {}
    progress_bar = st.progress(0, text="Fetching data for all tickers in batch...")

    # Fetch ALL data in one batch (this is where the speed improvement comes from)
    all_ticker_data = get_leaderboard_data_fast(tickers)

    progress_bar.progress(0.5, text="Processing squeeze scores...")

    completed_count = 0
    total_tickers = len(tickers)

    for ticker in tickers:
        completed_count += 1
        progress_bar.progress(0.5 + (completed_count / total_tickers * 0.5),
                             text=f"Processing {completed_count}/{total_tickers} stocks...")

        try:
            if ticker not in all_ticker_data:
                continue

            ticker_data_dict = all_ticker_data[ticker]
            info = ticker_data_dict.get('info', {})
            price_data = ticker_data_dict.get('price_data', pd.DataFrame())

            if not info or price_data.empty:
                continue

            # Add technical indicators
            price_data = _add_technical_indicators(price_data)

            # Calculate the squeeze score
            score, components = calculate_squeeze_score(info, price_data, include_reddit, is_leaderboard=True)

            # Extract sentiment data if it exists
            sentiment_data = None
            if include_reddit and 'Social Buzz' in components and components['Social Buzz'].get('raw_data'):
                sentiment_data = components['Social Buzz']['raw_data']

            # Prepare result
            ticker_result = {
                "Ticker": ticker,
                "Dashboard Link": f"/?ticker={ticker}",
                "Company": info.get('shortName', info.get('longName', 'N/A')),
                "Squeeze Score": score,
                "Short % Float": components.get('Short Interest %', {}).get('value', 0),
                "Volume Z-Score": components.get('Volume Z-Score', {}).get('value', 0),
                "Social Mentions (7d)": components.get('Social Buzz', {}).get('value', 0) if include_reddit else 'N/A'
            }
            leaderboard_data.append(ticker_result)
            if sentiment_data is not None:
                sentiment_data_dict[ticker] = sentiment_data

        except Exception as e:
            # Skip failed tickers
            st.warning(f"Failed to process {ticker}: {e}")
            continue

    progress_bar.empty()

    if not leaderboard_data:
        return pd.DataFrame(), {}

    df = pd.DataFrame(leaderboard_data).sort_values(by="Squeeze Score", ascending=False).reset_index(drop=True)

    # Optimize DataFrame memory usage (60-80% reduction)
    df = optimize_dataframe(df)

    return df, sentiment_data_dict