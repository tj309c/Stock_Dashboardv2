"""
True Stock Ticker Web Scraper - NO API KEYS REQUIRED
Scrapes data directly from websites using BeautifulSoup and requests.
Retrieves news articles, Reddit posts, and search results for stock tickers.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import time
import re
from urllib.parse import quote, urljoin
import json

# For sentiment analysis
try:
    from textblob import TextBlob
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    print("TextBlob not installed. Sentiment analysis disabled.")
    print("Install with: pip install textblob")


class TrueStockScraper:
    """
    Web scraper that works without any API keys.
    Scrapes directly from public websites.
    """
    
    def __init__(self, ticker: str):
        """
        Initialize the scraper.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        """
        self.ticker = ticker.upper()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        if not SENTIMENT_AVAILABLE or not text:
            return {'sentiment': 'neutral', 'polarity': 0.0, 'subjectivity': 0.0}
        
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
            print(f"Sentiment analysis error: {e}")
            return {'sentiment': 'neutral', 'polarity': 0.0, 'subjectivity': 0.0}
    
    def scrape_reddit_old(self, limit: int = 100) -> List[Dict]:
        """
        Scrape Reddit using old.reddit.com (no JavaScript required).
        
        Args:
            limit: Maximum posts to retrieve
            
        Returns:
            List of post dictionaries
        """
        results = []
        subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket', 'options']
        
        print(f"Scraping Reddit for ${self.ticker}...")
        
        for subreddit in subreddits:
            try:
                # Use old.reddit.com for easier scraping
                url = f"https://old.reddit.com/r/{subreddit}/search"
                params = {
                    'q': self.ticker,
                    'restrict_sr': 'on',
                    'sort': 'new',
                    't': 'month',
                    'limit': 100
                }
                
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all posts
                    posts = soup.find_all('div', class_='thing')
                    
                    for post in posts[:limit // len(subreddits)]:
                        try:
                            # Extract title
                            title_elem = post.find('a', class_='title')
                            if not title_elem:
                                continue
                            
                            title = title_elem.get_text(strip=True)
                            url_link = title_elem.get('href', '')
                            
                            # Make URL absolute if relative
                            if url_link.startswith('/r/'):
                                url_link = f"https://old.reddit.com{url_link}"
                            
                            # Extract score
                            score_elem = post.find('div', class_='score unvoted')
                            if not score_elem:
                                score_elem = post.find('div', class_='score')
                            score = score_elem.get_text(strip=True) if score_elem else '0'
                            
                            try:
                                score = int(score) if score.isdigit() else 0
                            except (ValueError, TypeError) as e:
                                print(f"Score parsing error: {e}")
                                score = 0
                            
                            # Extract number of comments
                            comments_elem = post.find('a', class_='comments')
                            num_comments = 0
                            if comments_elem:
                                comments_text = comments_elem.get_text(strip=True)
                                match = re.search(r'(\d+)', comments_text)
                                if match:
                                    num_comments = int(match.group(1))
                            
                            # Extract date
                            time_elem = post.find('time')
                            if time_elem and time_elem.get('datetime'):
                                date_str = time_elem.get('datetime')
                                try:
                                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                    date = date.replace(tzinfo=None)
                                except (ValueError, TypeError, AttributeError) as e:
                                    print(f"Reddit date parsing error: {e}")
                                    date = datetime.now()
                            else:
                                date = datetime.now()
                            
                            # Check if within last month
                            if date < datetime.now() - timedelta(days=30):
                                continue
                            
                            text = title
                            sentiment_data = self.analyze_sentiment(text)
                            
                            results.append({
                                'source': 'Reddit',
                                'subreddit': subreddit,
                                'title': title,
                                'text': text,
                                'url': url_link,
                                'date': date,
                                'score': score,
                                'num_comments': num_comments,
                                **sentiment_data
                            })
                            
                        except Exception as e:
                            print(f"Error parsing post: {e}")
                            continue
                
                time.sleep(2)  # Be polite with rate limiting
                
            except Exception as e:
                print(f"Error scraping r/{subreddit}: {e}")
                continue
        
        print(f"Found {len(results)} Reddit posts")
        return results
    
    def scrape_finviz_news(self) -> List[Dict]:
        """
        Scrape news from Finviz.com (no API key needed).
        
        Returns:
            List of news article dictionaries
        """
        results = []
        
        print(f"Scraping Finviz news for ${self.ticker}...")
        
        try:
            url = f"https://finviz.com/quote.ashx?t={self.ticker}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find news table
                news_table = soup.find('table', class_='fullview-news-outer')
                
                if news_table:
                    rows = news_table.find_all('tr')
                    
                    for row in rows:
                        try:
                            # Get date/time
                            date_cell = row.find('td', align='right')
                            news_cell = row.find('td', align='left')
                            
                            if not news_cell:
                                continue
                            
                            link = news_cell.find('a')
                            if not link:
                                continue
                            
                            title = link.get_text(strip=True)
                            url_link = link.get('href', '')
                            
                            # Parse date
                            if date_cell:
                                date_text = date_cell.get_text(strip=True)
                                date = self._parse_finviz_date(date_text)
                            else:
                                date = datetime.now()
                            
                            # Only include last month
                            if date < datetime.now() - timedelta(days=30):
                                continue
                            
                            sentiment_data = self.analyze_sentiment(title)
                            
                            results.append({
                                'source': 'Finviz',
                                'title': title,
                                'text': title,
                                'url': url_link,
                                'date': date,
                                **sentiment_data
                            })
                            
                        except Exception as e:
                            print(f"Error parsing Finviz row: {e}")
                            continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping Finviz: {e}")
        
        print(f"Found {len(results)} Finviz articles")
        return results
    
    def _parse_finviz_date(self, date_text: str) -> datetime:
        """Parse Finviz date format."""
        try:
            # Format: "Dec-02-24 09:30AM" or "09:30AM" (today)
            date_text = date_text.strip()
            
            if len(date_text.split()) == 1:
                # Just time, assume today
                time_str = date_text
                date = datetime.now().replace(
                    hour=int(time_str.split(':')[0]),
                    minute=int(time_str.split(':')[1][:2]),
                    second=0, microsecond=0
                )
            else:
                # Full date and time
                date = datetime.strptime(date_text, '%b-%d-%y %I:%M%p')
            
            return date
        except (ValueError, TypeError, AttributeError) as e:
            print(f"StockTwits date parsing error: {e}")
            return datetime.now()
    
    def scrape_yahoo_finance(self) -> List[Dict]:
        """
        Scrape Yahoo Finance news.
        
        Returns:
            List of news dictionaries
        """
        results = []
        
        print(f"Scraping Yahoo Finance for ${self.ticker}...")
        
        try:
            # Try RSS feed first
            url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={self.ticker}&region=US&lang=en-US"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                for item in items:
                    try:
                        title_elem = item.find('title')
                        link_elem = item.find('link')
                        pubdate_elem = item.find('pubDate')
                        description_elem = item.find('description')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        description = description_elem.get_text(strip=True) if description_elem else ''
                        text = f"{title}. {description}"
                        url_link = link_elem.get_text(strip=True) if link_elem else ''
                        
                        # Parse date
                        if pubdate_elem:
                            try:
                                date_str = pubdate_elem.get_text(strip=True)
                                date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                                date = date.replace(tzinfo=None)
                            except (ValueError, TypeError, AttributeError) as e:
                                print(f"Yahoo Finance date parsing error: {e}")
                                date = datetime.now()
                        else:
                            date = datetime.now()
                        
                        # Only last month
                        if date < datetime.now() - timedelta(days=30):
                            continue
                        
                        sentiment_data = self.analyze_sentiment(text)
                        
                        results.append({
                            'source': 'Yahoo Finance',
                            'title': title,
                            'text': text[:500],
                            'url': url_link,
                            'date': date,
                            **sentiment_data
                        })
                        
                    except Exception as e:
                        print(f"Error parsing Yahoo item: {e}")
                        continue
            
        except Exception as e:
            print(f"Error scraping Yahoo Finance: {e}")
        
        print(f"Found {len(results)} Yahoo Finance articles")
        return results
    
    def scrape_marketwatch(self) -> List[Dict]:
        """
        Scrape MarketWatch news.
        
        Returns:
            List of news dictionaries
        """
        results = []
        
        print(f"Scraping MarketWatch for ${self.ticker}...")
        
        try:
            url = f"https://www.marketwatch.com/investing/stock/{self.ticker.lower()}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find news articles
                articles = soup.find_all('div', class_='article__content')
                
                for article in articles[:20]:
                    try:
                        title_elem = article.find('a', class_='link')
                        if not title_elem:
                            title_elem = article.find('h3')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url_link = title_elem.get('href', '')
                        
                        if url_link and not url_link.startswith('http'):
                            url_link = urljoin('https://www.marketwatch.com', url_link)
                        
                        # Try to find timestamp
                        time_elem = article.find('span', class_='article__timestamp')
                        if time_elem:
                            date = self._parse_relative_date(time_elem.get_text(strip=True))
                        else:
                            date = datetime.now()
                        
                        # Only last month
                        if date < datetime.now() - timedelta(days=30):
                            continue
                        
                        sentiment_data = self.analyze_sentiment(title)
                        
                        results.append({
                            'source': 'MarketWatch',
                            'title': title,
                            'text': title,
                            'url': url_link,
                            'date': date,
                            **sentiment_data
                        })
                        
                    except Exception as e:
                        print(f"Error parsing MarketWatch article: {e}")
                        continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping MarketWatch: {e}")
        
        print(f"Found {len(results)} MarketWatch articles")
        return results
    
    def _parse_relative_date(self, date_text: str) -> datetime:
        """Parse relative dates like '2 hours ago', '3 days ago'."""
        try:
            date_text = date_text.lower().strip()
            now = datetime.now()
            
            if 'hour' in date_text:
                hours = int(re.search(r'(\d+)', date_text).group(1))
                return now - timedelta(hours=hours)
            elif 'day' in date_text:
                days = int(re.search(r'(\d+)', date_text).group(1))
                return now - timedelta(days=days)
            elif 'minute' in date_text:
                minutes = int(re.search(r'(\d+)', date_text).group(1))
                return now - timedelta(minutes=minutes)
            elif 'week' in date_text:
                weeks = int(re.search(r'(\d+)', date_text).group(1))
                return now - timedelta(weeks=weeks)
            else:
                return now
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Relative date parsing error: {e}")
            return datetime.now()
    
    def scrape_seeking_alpha(self) -> List[Dict]:
        """
        Scrape Seeking Alpha news (latest articles).
        Note: Seeking Alpha has anti-scraping measures, so this may not always work.
        
        Returns:
            List of news dictionaries
        """
        results = []
        
        print(f"Scraping Seeking Alpha for ${self.ticker}...")
        
        try:
            url = f"https://seekingalpha.com/symbol/{self.ticker}/news"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find articles (structure may change)
                articles = soup.find_all('article', limit=20)
                
                for article in articles:
                    try:
                        # Find title
                        title_elem = article.find('a', {'data-test-id': 'post-list-item-title'})
                        if not title_elem:
                            title_elem = article.find('h3')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url_link = title_elem.get('href', '')
                        
                        if url_link and not url_link.startswith('http'):
                            url_link = f"https://seekingalpha.com{url_link}"
                        
                        # Get date
                        time_elem = article.find('time')
                        if time_elem and time_elem.get('datetime'):
                            try:
                                date = datetime.fromisoformat(time_elem.get('datetime').replace('Z', '+00:00'))
                                date = date.replace(tzinfo=None)
                            except (ValueError, TypeError, AttributeError) as e:
                                print(f"Seeking Alpha date parsing error: {e}")
                                date = datetime.now()
                        else:
                            date = datetime.now()
                        
                        # Only last month
                        if date < datetime.now() - timedelta(days=30):
                            continue
                        
                        sentiment_data = self.analyze_sentiment(title)
                        
                        results.append({
                            'source': 'Seeking Alpha',
                            'title': title,
                            'text': title,
                            'url': url_link,
                            'date': date,
                            **sentiment_data
                        })
                        
                    except Exception as e:
                        print(f"Error parsing Seeking Alpha article: {e}")
                        continue
            
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping Seeking Alpha: {e}")
        
        print(f"Found {len(results)} Seeking Alpha articles")
        return results
    
    def scrape_all(self, sources: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Scrape all available sources.
        
        Args:
            sources: List of sources to scrape. Options:
                    'reddit', 'finviz', 'yahoo', 'marketwatch', 'seekingalpha'
                    If None, scrapes all sources
        
        Returns:
            Pandas DataFrame with all scraped data
        """
        if sources is None:
            sources = ['reddit', 'finviz', 'yahoo', 'marketwatch', 'seekingalpha']
        
        print(f"\n{'='*60}")
        print(f"TRUE WEB SCRAPER - NO API KEYS NEEDED")
        print(f"Scraping data for ${self.ticker}")
        print(f"Sources: {', '.join(sources)}")
        print(f"{'='*60}\n")
        
        all_data = []
        
        # Scrape each source
        if 'reddit' in sources:
            reddit_data = self.scrape_reddit_old()
            all_data.extend(reddit_data)
        
        if 'finviz' in sources:
            finviz_data = self.scrape_finviz_news()
            all_data.extend(finviz_data)
        
        if 'yahoo' in sources:
            yahoo_data = self.scrape_yahoo_finance()
            all_data.extend(yahoo_data)
        
        if 'marketwatch' in sources:
            marketwatch_data = self.scrape_marketwatch()
            all_data.extend(marketwatch_data)
        
        if 'seekingalpha' in sources:
            seeking_alpha_data = self.scrape_seeking_alpha()
            all_data.extend(seeking_alpha_data)
        
        # Create DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Remove duplicates based on title
            df = df.drop_duplicates(subset=['title'], keep='first')
            
            # Sort by date
            df = df.sort_values('date', ascending=False)
            df = df.reset_index(drop=True)
            
            print(f"\n{'='*60}")
            print(f"SCRAPE COMPLETE")
            print(f"{'='*60}")
            print(f"Total unique items: {len(df)}")
            print(f"\nBy source:")
            print(df['source'].value_counts())
            
            if SENTIMENT_AVAILABLE:
                print(f"\nSentiment breakdown:")
                print(df['sentiment'].value_counts())
                print(f"\nAverage sentiment polarity: {df['polarity'].mean():.3f}")
            
            return df
        else:
            print("\nNo data collected. This could mean:")
            print("- The ticker symbol is invalid")
            print("- There's no recent news/discussion about this stock")
            print("- Websites may be blocking scraping attempts")
            print("- Network connectivity issues")
            return pd.DataFrame()


def main():
    """Example usage of the TrueStockScraper."""
    
    print("="*60)
    print("TRUE STOCK SCRAPER - NO API KEYS REQUIRED")
    print("="*60)
    print("\nThis scraper works by directly scraping public websites.")
    print("No API keys or paid services needed!\n")
    
    # Get ticker from user
    ticker = input("Enter stock ticker (e.g., AAPL, TSLA, GME): ").strip().upper()
    
    if not ticker:
        ticker = "AAPL"
        print(f"Using default ticker: {ticker}\n")
    
    # Initialize scraper
    scraper = TrueStockScraper(ticker)
    
    # Scrape all sources
    df = scraper.scrape_all()
    
    # Display and save results
    if not df.empty:
        print("\n" + "="*60)
        print("SAMPLE RESULTS")
        print("="*60)
        
        # Display top results
        display_cols = ['source', 'title', 'date', 'sentiment']
        available_cols = [col for col in display_cols if col in df.columns]
        print(df[available_cols].head(15).to_string(index=False))
        
        # Save to CSV
        filename = f"{ticker}_scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\n✓ Data saved to: {filename}")
        
        # Additional analysis
        print("\n" + "="*60)
        print("ANALYSIS")
        print("="*60)
        
        print(f"\nDate range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"Total sources: {df['source'].nunique()}")
        
        if 'score' in df.columns:
            reddit_df = df[df['source'] == 'Reddit']
            if not reddit_df.empty:
                print(f"\nTop Reddit post by score:")
                top_post = reddit_df.loc[reddit_df['score'].idxmax()]
                print(f"  Score: {top_post['score']}")
                print(f"  Title: {top_post['title'][:80]}...")
                print(f"  r/{top_post['subreddit']}")
        
        if SENTIMENT_AVAILABLE and 'sentiment' in df.columns:
            print(f"\nSentiment distribution:")
            sentiment_pct = df['sentiment'].value_counts(normalize=True) * 100
            for sentiment, pct in sentiment_pct.items():
                print(f"  {sentiment.capitalize()}: {pct:.1f}%")
    else:
        print("\n⚠ No data was collected. Please try:")
        print("  1. A more popular stock ticker (e.g., AAPL, TSLA, MSFT)")
        print("  2. Checking your internet connection")
        print("  3. Trying again later (some sites may temporarily block requests)")


if __name__ == "__main__":
    main()
