import streamlit as st
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Optional import for Google Trends
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

# --- NLTK Downloader ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    st.info("Downloading the VADER sentiment analysis model (one-time setup)...")
    nltk.download('vader_lexicon')

def _scrape_google_news(query):
    """
    Scrapes Google News for a given query and returns headlines.
    Uses a custom User-Agent to appear as a regular browser.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    url = f"https://news.google.com/rss/search?q={query}+when:7d&hl=en-US&gl=US&ceid=US:en"
    try:
        response = requests.get(url, headers=headers)
        time.sleep(0.5) # Be respectful of the server
        soup = BeautifulSoup(response.content, 'xml')
        return [item.title.text for item in soup.findAll('item')]
    except Exception as e:
        st.warning(f"Could not scrape Google News: {e}")
        return []

def _scrape_reddit(query):
    """
    Scrapes Reddit's public HTML for a given query and returns post titles.
    This avoids needing the Reddit API.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    # Search across popular finance subreddits
    url = f"https://www.reddit.com/search/?q={query}&type=link&c=1&sort=new&t=week"
    try:
        response = requests.get(url, headers=headers)
        time.sleep(0.5) # Be respectful of the server
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all post titles using a specific data attribute
        return [a.text for a in soup.find_all('a', {'data-testid': 'post-title'})]
    except Exception as e:
        st.warning(f"Could not scrape Reddit: {e}")
        return []

def _get_google_trends(query):
    """
    Gets the Google Trends interest over time for a query.
    Returns the DataFrame with daily trend data.
    """
    if not PYTRENDS_AVAILABLE:
        return pd.DataFrame()

    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        pytrends.build_payload([query], cat=0, timeframe='today 7-d', geo='', gprop='')
        df = pytrends.interest_over_time()
        if not df.empty:
            return df
    except Exception as e:
        st.warning(f"Could not get Google Trends data: {e}")
        return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_social_sentiment(ticker, company_name):
    """
    Aggregates sentiment and mention volume from Google News, Reddit, and Google Trends.
    """
    sia = SentimentIntensityAnalyzer()
    query = f'"{ticker}" OR "{company_name}"'

    # --- Scrape Data ---
    google_headlines = _scrape_google_news(query)
    reddit_titles = _scrape_reddit(ticker) # Reddit search works better with just the ticker
    google_trends_df = _get_google_trends(ticker)

    google_trends_score = 0
    # FIX: Check for ticker column existence before accessing it to prevent KeyError.
    # The .get(ticker) call safely returns None if the column is missing.
    if not google_trends_df.empty and ticker in google_trends_df.columns:
        google_trends_score = google_trends_df.get(ticker, pd.Series(dtype=float)).mean()

    all_mentions = google_headlines + reddit_titles

    # --- Analyze Data ---
    mention_volume = len(all_mentions)
    avg_sentiment = 0.0
    if mention_volume > 0:
        avg_sentiment = np.mean([sia.polarity_scores(text)['compound'] for text in all_mentions])

    # --- Normalize Scores (0-100) ---
    # Normalize mention volume: 0 for 0 mentions, 100 for 200+ mentions (capped)
    mention_volume_score = min((mention_volume / 200.0) * 100, 100)

    # --- Composite Score ---
    # Formula: (Sentiment * 0.6) + (Mention Volume * 0.2) + (Google Trends * 0.2)
    # Sentiment is from -1 to 1, so we scale it to 0-100 first
    sentiment_component = ((avg_sentiment + 1) / 2) * 100 
    buzz_index = (sentiment_component * 0.6) + (mention_volume_score * 0.2) + (google_trends_score * 0.2)

    return {
        "ticker": ticker,
        "mention_volume": mention_volume,
        "avg_sentiment": avg_sentiment,
        "google_trends_score": google_trends_score,
        "google_trends_df": google_trends_df, # NEW: Pass the full DataFrame
        "social_buzz_index": buzz_index,
        "top_mentions": all_mentions[:5] # Return the top 5 most recent mentions
    }