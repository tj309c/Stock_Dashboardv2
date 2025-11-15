"""
Enhanced Stock Ticker Data Scraper
Features:
- Reddit API integration (PRAW)
- Configurable sources
- Advanced sentiment analysis
- Export to multiple formats
"""

import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import time
import os
from urllib.parse import quote
import json
# Migrated to use centralized API configuration
from src.config.api_config import api_config

# For sentiment analysis
try:
    from textblob import TextBlob
except ImportError:
    print("TextBlob not installed. Install with: pip install textblob")

# For Reddit API (optional but recommended)
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("PRAW not installed. Using JSON API fallback for Reddit.")


class EnhancedStockDataScraper:
    """Enhanced scraper with more features and configuration options."""
    
    def __init__(self, ticker: str, config: Optional[Dict] = None):
        """
        Initialize the scraper with a stock ticker and configuration.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
            config: Configuration dictionary with API keys and settings
        """
        self.ticker = ticker.upper()
        self.config = config or {}
        self.data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Configuration
        self.reddit_client_id = self.config.get('reddit_client_id')
        self.reddit_client_secret = self.config.get('reddit_client_secret')
        self.reddit_user_agent = self.config.get('reddit_user_agent', 'StockScraper/1.0')
        self.news_api_key = self.config.get('news_api_key')
        
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment with detailed scores.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment label and scores
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'sentiment': label,
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3)
            }
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0
            }
    
    def scrape_reddit_with_praw(self, limit: int = 100) -> List[Dict]:
        """
        Scrape Reddit using PRAW (Reddit API).
        Requires Reddit API credentials.
        
        Args:
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of dictionaries containing post data
        """
        if not PRAW_AVAILABLE:
            print("PRAW not available. Use pip install praw")
            return []
        
        if not all([self.reddit_client_id, self.reddit_client_secret]):
            print("Reddit API credentials not provided. Using JSON API fallback.")
            return self.scrape_reddit_json(limit)
        
        # Check for placeholder credentials
        if 'your_reddit' in self.reddit_client_id.lower() or 'your_reddit' in self.reddit_client_secret.lower():
            print("⚠️ Reddit API has placeholder credentials. Please register at reddit.com/prefs/apps")
            print("Using JSON API fallback (no authentication)...")
            return self.scrape_reddit_json(limit)
        
        results = []
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket', 
                     'options', 'Daytrading', 'SecurityAnalysis']
        
        print(f"Scraping Reddit with PRAW for ${self.ticker}...")
        
        try:
            reddit = praw.Reddit(
                client_id=self.reddit_client_id,
                client_secret=self.reddit_client_secret,
                user_agent=self.reddit_user_agent
            )
            
            for subreddit_name in subreddits:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    
                    # Search for ticker
                    for submission in subreddit.search(self.ticker, 
                                                      sort='new', 
                                                      time_filter='month', 
                                                      limit=limit // len(subreddits)):
                        
                        created_date = datetime.fromtimestamp(submission.created_utc)
                        text = f"{submission.title}. {submission.selftext}"
                        sentiment_data = self.analyze_sentiment(text)
                        
                        results.append({
                            'source': 'Reddit',
                            'subreddit': subreddit_name,
                            'title': submission.title,
                            'text': text[:1000],
                            'url': f"https://reddit.com{submission.permalink}",
                            'date': created_date,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            **sentiment_data
                        })
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error scraping r/{subreddit_name}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error initializing Reddit API: {e}")
            return self.scrape_reddit_json(limit)
        
        print(f"Found {len(results)} Reddit posts")
        return results
    
    def scrape_reddit_json(self, limit: int = 100) -> List[Dict]:
        """
        Scrape Reddit using JSON API (no authentication).
        Fallback method when PRAW is not available.
        
        Args:
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of dictionaries containing post data
        """
        results = []
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
        
        print(f"Scraping Reddit (JSON API) for ${self.ticker}...")
        
        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': self.ticker,
                    'restrict_sr': 'on',
                    'sort': 'new',
                    'limit': limit // len(subreddits),
                    't': 'month'
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('children', [])
                    
                    for post in posts:
                        post_data = post.get('data', {})
                        created_utc = post_data.get('created_utc', 0)
                        created_date = datetime.fromtimestamp(created_utc)
                        
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        text = f"{title}. {selftext}"
                        sentiment_data = self.analyze_sentiment(text)
                        
                        results.append({
                            'source': 'Reddit',
                            'subreddit': subreddit,
                            'title': title,
                            'text': text[:1000],
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'date': created_date,
                            'score': post_data.get('score', 0),
                            'num_comments': post_data.get('num_comments', 0),
                            **sentiment_data
                        })
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"Error scraping r/{subreddit}: {e}")
                continue
        
        print(f"Found {len(results)} Reddit posts")
        return results
    
    def scrape_news_api(self) -> List[Dict]:
        """
        Scrape news articles using NewsAPI.
        
        Returns:
            List of dictionaries containing article data
        """
        results = []
        
        if not self.news_api_key:
            print("No NewsAPI key provided. Skipping news scraping.")
            return results
        
        print(f"Scraping news for ${self.ticker}...")
        
        try:
            url = "https://newsapi.org/v2/everything"
            
            # Try different search queries
            queries = [
                f"{self.ticker}",
                f"{self.ticker} stock",
                f"{self.ticker} shares"
            ]
            
            for query in queries:
                params = {
                    'q': query,
                    'from': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'apiKey': self.news_api_key,
                    'pageSize': 100
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        published_at = article.get('publishedAt', '')
                        try:
                            date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                        except (ValueError, TypeError) as e:
                            print(f"Date parsing error for NewsAPI: {e}")
                            date = datetime.now()
                        
                        title = article.get('title', '')
                        description = article.get('description', '') or ''
                        content = article.get('content', '') or ''
                        text = f"{title}. {description} {content}"
                        sentiment_data = self.analyze_sentiment(text)
                        
                        results.append({
                            'source': 'News',
                            'outlet': article.get('source', {}).get('name', 'Unknown'),
                            'title': title,
                            'text': text[:1000],
                            'url': article.get('url', ''),
                            'date': date,
                            'author': article.get('author', 'Unknown'),
                            **sentiment_data
                        })
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Error scraping news: {e}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for item in results:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                unique_results.append(item)
        
        print(f"Found {len(unique_results)} unique news articles")
        return unique_results
    
    def scrape_yahoo_finance(self) -> List[Dict]:
        """
        Scrape Yahoo Finance news.
        
        Returns:
            List of dictionaries containing Yahoo Finance news
        """
        results = []
        
        print(f"Scraping Yahoo Finance for ${self.ticker}...")
        
        try:
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.ticker}&region=US&lang=en-US"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item'):
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pubdate_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    
                    if title_elem is not None:
                        title = title_elem.text or ''
                        description = description_elem.text if description_elem is not None else ''
                        text = f"{title}. {description}"
                        
                        try:
                            date_str = pubdate_elem.text if pubdate_elem is not None else ''
                            date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                            date = date.replace(tzinfo=None)
                        except (ValueError, TypeError, AttributeError) as e:
                            print(f"Date parsing error for RSS feed: {e}")
                            date = datetime.now()
                        
                        if date > datetime.now() - timedelta(days=30):
                            sentiment_data = self.analyze_sentiment(text)
                            
                            results.append({
                                'source': 'Yahoo Finance',
                                'title': title,
                                'text': text[:1000],
                                'url': link_elem.text if link_elem is not None else '',
                                'date': date,
                                **sentiment_data
                            })
                            
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {e}")
        
        print(f"Found {len(results)} Yahoo Finance articles")
        return results
    
    def scrape_all(self, sources: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scrape specified sources and return a pandas DataFrame.
        
        Args:
            sources: List of sources to scrape. 
                    Options: 'reddit', 'news', 'yahoo'
                    If None, scrapes all available sources
            
        Returns:
            Pandas DataFrame with all scraped data
        """
        if sources is None:
            sources = ['reddit', 'news', 'yahoo']
        
        print(f"\n{'='*50}")
        print(f"Starting scrape for ${self.ticker}")
        print(f"Sources: {', '.join(sources)}")
        print(f"{'='*50}\n")
        
        all_data = []
        
        # Scrape Reddit
        if 'reddit' in sources:
            if PRAW_AVAILABLE and self.reddit_client_id:
                reddit_data = self.scrape_reddit_with_praw()
            else:
                reddit_data = self.scrape_reddit_json()
            all_data.extend(reddit_data)
        
        # Scrape Yahoo Finance
        if 'yahoo' in sources:
            yahoo_data = self.scrape_yahoo_finance()
            all_data.extend(yahoo_data)
        
        # Scrape News
        if 'news' in sources and self.news_api_key:
            news_data = self.scrape_news_api()
            all_data.extend(news_data)
        
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            df = df.sort_values('date', ascending=False)
            df = df.reset_index(drop=True)
            
            print(f"\n{'='*50}")
            print(f"Scrape complete for ${self.ticker}")
            print(f"{'='*50}")
            print(f"Total items: {len(df)}")
            print(f"\nBy source:")
            print(df['source'].value_counts())
            print(f"\nSentiment breakdown:")
            print(df['sentiment'].value_counts())
            
            return df
        else:
            print("No data collected")
            return pd.DataFrame()
    
    def export_to_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export DataFrame to CSV."""
        if filename is None:
            filename = f"{self.ticker}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        return filename
    
    def export_to_json(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export DataFrame to JSON."""
        if filename is None:
            filename = f"{self.ticker}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        df.to_json(filename, orient='records', date_format='iso', indent=2)
        return filename
    
    def export_to_excel(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export DataFrame to Excel with formatting."""
        if filename is None:
            filename = f"{self.ticker}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='All Data')
            
            # Create sentiment summary sheet
            sentiment_summary = df.groupby('source')['sentiment'].value_counts().unstack(fill_value=0)
            sentiment_summary.to_excel(writer, sheet_name='Sentiment Summary')
        
        return filename


def load_config_from_env() -> Dict:
    """Load configuration from centralized API config."""
    return {
        'reddit_client_id': api_config.reddit.client_id if api_config.reddit.is_configured else None,
        'reddit_client_secret': api_config.reddit.client_secret if api_config.reddit.is_configured else None,
        'reddit_user_agent': api_config.reddit.user_agent,
        'news_api_key': api_config.news.api_key if api_config.news.is_configured else None
    }


def main():
    """Example usage of the EnhancedStockDataScraper."""
    
    # Get ticker from user
    ticker = input("Enter stock ticker (e.g., AAPL, TSLA, GME): ").strip().upper()
    
    if not ticker:
        ticker = "AAPL"
        print(f"Using default ticker: {ticker}")
    
    # Load configuration
    config = load_config_from_env()
    
    # Or manually set configuration:
    # config = {
    #     'reddit_client_id': 'YOUR_CLIENT_ID',
    #     'reddit_client_secret': 'YOUR_CLIENT_SECRET',
    #     'reddit_user_agent': 'StockScraper/1.0',
    #     'news_api_key': 'YOUR_NEWS_API_KEY'
    # }
    
    # Initialize scraper
    scraper = EnhancedStockDataScraper(ticker, config)
    
    # Scrape data
    df = scraper.scrape_all()
    
    # Display and export results
    if not df.empty:
        print("\n" + "="*50)
        print("SAMPLE RESULTS")
        print("="*50)
        
        # Show sample with key columns
        display_columns = ['source', 'title', 'date', 'sentiment', 'polarity']
        available_columns = [col for col in display_columns if col in df.columns]
        print(df[available_columns].head(10).to_string())
        
        # Export to multiple formats
        csv_file = scraper.export_to_csv(df)
        print(f"\n✓ Data exported to CSV: {csv_file}")
        
        json_file = scraper.export_to_json(df)
        print(f"✓ Data exported to JSON: {json_file}")
        
        # Statistics
        print("\n" + "="*50)
        print("STATISTICS")
        print("="*50)
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"\nAverage sentiment polarity: {df['polarity'].mean():.3f}")
        print(f"\nTop sources:")
        print(df['source'].value_counts().head())
        
        if 'subreddit' in df.columns:
            print(f"\nTop subreddits:")
            print(df[df['source'] == 'Reddit']['subreddit'].value_counts().head())


if __name__ == "__main__":
    main()
