"""
Sentiment Scraper Wrapper
Integrates Stock_Scrapper tool for real-time sentiment analysis from Reddit and news sources.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Add Stock_Scrapper to path
STOCK_SCRAPPER_PATH = Path(__file__).parent.parent.parent / "Stock_Scrapper"
sys.path.insert(0, str(STOCK_SCRAPPER_PATH))

try:
    from stock_scraper_enhanced import EnhancedStockDataScraper as EnhancedScraper
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    
try:
    from stock_scraper import StockDataScraper as BasicScraper
    BASIC_AVAILABLE = True
except ImportError:
    BASIC_AVAILABLE = False


class SentimentScraper:
    """
    Wrapper for Stock_Scrapper tools to integrate sentiment data into dashboards.
    Automatically uses enhanced scraper if API keys available, falls back to basic scraper.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize sentiment scraper with optional API configuration.
        
        Args:
            config: Dictionary with API keys:
                - reddit_client_id: Reddit API client ID
                - reddit_client_secret: Reddit API client secret
                - reddit_user_agent: Reddit API user agent
                - news_api_key: NewsAPI key (optional)
        """
        self.config = config or {}
        self.use_enhanced = ENHANCED_AVAILABLE and self._has_reddit_credentials()
        
    def _has_reddit_credentials(self) -> bool:
        """Check if Reddit API credentials are configured."""
        return all([
            self.config.get('reddit_client_id'),
            self.config.get('reddit_client_secret'),
            self.config.get('reddit_user_agent')
        ])
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_sentiment_data(_self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Fetch sentiment data for a ticker from Reddit and news sources.
        Cached for 1 hour to avoid rate limiting.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with columns: source, title, text, url, date, sentiment, polarity, subjectivity
        """
        if not (ENHANCED_AVAILABLE or BASIC_AVAILABLE):
            st.warning("⚠️ Stock_Scrapper module not available. Please check installation.")
            return None
        
        try:
            if _self.use_enhanced:
                scraper = EnhancedScraper(ticker, config=_self.config)
                # EnhancedScraper doesn't take news_api_key as parameter, uses config
                df = scraper.scrape_all()
            else:
                scraper = BasicScraper(ticker)
                # BasicScraper takes news_api_key as parameter
                news_api_key = _self.config.get('news_api_key')
                df = scraper.scrape_all(news_api_key=news_api_key)
            
            if df is not None and not df.empty:
                # Add polarity and subjectivity if not present (for basic scraper)
                if 'polarity' not in df.columns:
                    df['polarity'] = df['sentiment'].map({
                        'positive': 0.5,
                        'negative': -0.5,
                        'neutral': 0.0
                    })
                if 'subjectivity' not in df.columns:
                    df['subjectivity'] = 0.5
                
                return df
            
            return None
            
        except Exception as e:
            st.error(f"❌ Error fetching sentiment data: {str(e)}")
            return None
    
    def get_sentiment_summary(self, ticker: str) -> Dict:
        """
        Get summarized sentiment metrics for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with sentiment summary metrics
        """
        df = self.get_sentiment_data(ticker)
        
        if df is None or df.empty:
            return {
                'total_mentions': 0,
                'positive_pct': 0.0,
                'negative_pct': 0.0,
                'neutral_pct': 0.0,
                'avg_polarity': 0.0,
                'avg_subjectivity': 0.0,
                'recent_posts': [],
                'trending_sources': [],
                'data_available': False
            }
        
        # Calculate sentiment percentages
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        positive_pct = (sentiment_counts.get('positive', 0) / total) * 100
        negative_pct = (sentiment_counts.get('negative', 0) / total) * 100
        neutral_pct = (sentiment_counts.get('neutral', 0) / total) * 100
        
        # Calculate average polarity and subjectivity
        avg_polarity = df['polarity'].mean()
        avg_subjectivity = df['subjectivity'].mean()
        
        # Get recent posts (last 24 hours)
        recent_df = df[df['date'] > datetime.now() - timedelta(days=1)]
        recent_posts = recent_df[['source', 'title', 'sentiment', 'date', 'url']].head(10).to_dict('records')
        
        # Get trending sources
        source_counts = df['source'].value_counts().head(5).to_dict()
        
        return {
            'total_mentions': total,
            'positive_pct': positive_pct,
            'negative_pct': negative_pct,
            'neutral_pct': neutral_pct,
            'avg_polarity': avg_polarity,
            'avg_subjectivity': avg_subjectivity,
            'recent_posts': recent_posts,
            'trending_sources': source_counts,
            'data_available': True,
            'scraper_type': 'enhanced' if self.use_enhanced else 'basic'
        }
    
    def get_sentiment_over_time(self, ticker: str, days: int = 7) -> pd.DataFrame:
        """
        Get sentiment trends over time.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to analyze
            
        Returns:
            DataFrame with daily sentiment aggregations
        """
        df = self.get_sentiment_data(ticker)
        
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Filter to requested time period
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['date'] > cutoff_date].copy()
        
        # Extract date only
        df['date_only'] = df['date'].dt.date
        
        # Group by date and sentiment
        daily_sentiment = df.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
        
        # Calculate daily polarity
        daily_polarity = df.groupby('date_only')['polarity'].mean()
        
        # Combine
        result = daily_sentiment.copy()
        result['avg_polarity'] = daily_polarity
        result['total_mentions'] = daily_sentiment.sum(axis=1)
        
        return result.reset_index()


def get_scraper(config: Optional[Dict] = None) -> SentimentScraper:
    """
    Factory function to get a configured sentiment scraper.
    Retrieves API keys from streamlit secrets or config.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured SentimentScraper instance
    """
    if config is None:
        # Try to get from streamlit secrets
        config = {}
        try:
            if hasattr(st, 'secrets'):
                config = {
                    'reddit_client_id': st.secrets.get('REDDIT_CLIENT_ID'),
                    'reddit_client_secret': st.secrets.get('REDDIT_CLIENT_SECRET'),
                    'reddit_user_agent': st.secrets.get('REDDIT_USER_AGENT', 'StocksV2App/1.0'),
                    'news_api_key': st.secrets.get('NEWS_API_KEY')
                }
        except Exception as e:
            logger.warning(f"Could not load secrets for sentiment scraper: {e}")
            config = {}  # Fallback to empty config
    
    return SentimentScraper(config)


def display_sentiment_metrics(summary: Dict):
    """
    Display sentiment metrics in Streamlit columns.
    
    Args:
        summary: Sentiment summary dictionary from get_sentiment_summary()
    """
    if not summary['data_available']:
        st.info("📊 No sentiment data available. Configure API keys for real-time data.")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Mentions",
            f"{summary['total_mentions']:,}",
            help="Total social media and news mentions"
        )
    
    with col2:
        st.metric(
            "Positive",
            f"{summary['positive_pct']:.1f}%",
            help="Percentage of positive sentiment"
        )
    
    with col3:
        st.metric(
            "Negative",
            f"{summary['negative_pct']:.1f}%",
            help="Percentage of negative sentiment"
        )
    
    with col4:
        st.metric(
            "Avg Polarity",
            f"{summary['avg_polarity']:.2f}",
            help="Average sentiment polarity (-1 to 1)"
        )
    
    # Scraper info
    scraper_type = summary.get('scraper_type', 'unknown')
    if scraper_type == 'enhanced':
        st.success("✅ Using enhanced scraper with Reddit API authentication")
    else:
        st.info("ℹ️ Using basic scraper (no API keys). Configure Reddit API for better data quality.")


def display_recent_posts(recent_posts: List[Dict], max_posts: int = 10):
    """
    Display recent social media posts in an expander.
    
    Args:
        recent_posts: List of post dictionaries
        max_posts: Maximum number of posts to display
    """
    if not recent_posts:
        st.info("No recent posts available")
        return
    
    with st.expander(f"📰 Recent Posts ({len(recent_posts)} items)", expanded=False):
        for post in recent_posts[:max_posts]:
            sentiment_emoji = {
                'positive': '🟢',
                'negative': '🔴',
                'neutral': '⚪'
            }.get(post['sentiment'], '⚪')
            
            date_str = post['date'].strftime('%Y-%m-%d %H:%M') if isinstance(post['date'], datetime) else str(post['date'])
            
            st.markdown(f"""
            **{sentiment_emoji} {post['title']}**  
            *Source: {post['source']} | {date_str}*  
            [View Source]({post['url']})
            """)
            st.divider()
