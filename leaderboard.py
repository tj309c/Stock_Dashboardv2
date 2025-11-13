import streamlit as st
import pandas as pd
from data_fetcher import get_ticker, get_company_info, get_stock_price_data
from squeeze_analyzer import calculate_squeeze_score

@st.cache_data(ttl=1800) # Cache leaderboard for 30 minutes
def generate_squeeze_leaderboard(tickers, include_reddit=True):
    """
    Scans a list of tickers and ranks them by their USSI score.

    Args:
        tickers (list): A list of stock tickers to scan.
        include_reddit (bool): Flag to include Reddit sentiment in the score.

    Returns:
        A pandas DataFrame containing the ranked leaderboard.
    """
    leaderboard_data = []
    # FIX: Store sentiment data separately to pass back to the UI
    sentiment_data_dict = {}
    progress_bar = st.progress(0, text="Initializing scan...")
    
    for i, ticker in enumerate(tickers):
        try:
            progress_bar.progress((i + 1) / len(tickers), text=f"Scanning {ticker}...")

            # 1. Fetch required data
            stock_obj = get_ticker(ticker)
            info = get_company_info(stock_obj)
            price_data = get_stock_price_data(stock_obj)

            if not info or price_data.empty:
                continue

            # 2. Calculate necessary technical indicators for the squeeze score
            price_data.ta.rsi(length=14, append=True)
            price_data.dropna(inplace=True)

            # 3. Calculate the squeeze score
            score, components = calculate_squeeze_score(info, price_data, include_reddit, is_leaderboard=True)

            # FIX: Store the raw sentiment data if it exists
            if include_reddit and 'Social Buzz' in components and components['Social Buzz'].get('raw_data'):
                sentiment_data_dict[ticker] = components['Social Buzz']['raw_data']

            # 4. Append results
            leaderboard_data.append({
                "Ticker": ticker,
                "Dashboard Link": f"/?ticker={ticker}", # Add a relative link with a query parameter
                "Company": info.get('shortName', 'N/A'),
                "Squeeze Score": score,
                "Short % Float": components.get('Short Interest', {}).get('value', 0),
                "Volume Z-Score": components.get('Volume Z-Score', {}).get('value', 0),
                "Social Mentions (7d)": components.get('Social Buzz', {}).get('value', 0) if include_reddit else 'N/A'
            })
        except Exception:
            # If any ticker fails, just skip it and continue the scan
            continue
    
    progress_bar.empty()
    
    if not leaderboard_data:
        return pd.DataFrame(), {}
    
    df = pd.DataFrame(leaderboard_data).sort_values(by="Squeeze Score", ascending=False).reset_index(drop=True)
    return df, sentiment_data_dict