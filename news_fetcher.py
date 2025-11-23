"""
News Fetcher - Real-time news and sentiment analysis
Integrates Finnhub, News API, X/Twitter (via Grok), and AI-powered sentiment analysis
"""
import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
import pandas as pd
from typing import List, Dict, Optional
from error_logger import log_error, log_warning, with_error_logging
import json
from ai_model_config import get_selected_model, create_model_client, AIProvider, get_model_info


# ========================================
# FINNHUB NEWS FETCHER
# ========================================

@st.cache_data(ttl=900)  # Cache for 15 minutes
@with_error_logging("news_fetcher.get_finnhub_news")
def get_finnhub_news(ticker: str, days_back: int = 7) -> List[Dict]:
    """
    Fetch company news from Finnhub API

    Args:
        ticker: Stock ticker symbol
        days_back: Number of days to look back for news

    Returns:
        List of news articles with metadata
    """
    if 'FINNHUB_API_KEY' not in st.secrets:
        log_warning("Finnhub API key not configured", "news_fetcher.get_finnhub_news")
        return []

    api_key = st.secrets['FINNHUB_API_KEY']

    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    # Format dates for API
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    url = f"https://finnhub.io/api/v1/company-news"
    params = {
        'symbol': ticker,
        'from': start_str,
        'to': end_str,
        'token': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        news_data = response.json()

        if not news_data:
            return []

        # Process and enrich news data
        processed_news = []
        for article in news_data[:20]:  # Limit to 20 most recent
            # Convert timestamp to timezone-aware datetime (UTC)
            timestamp = article.get('datetime', 0)
            published_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc) if timestamp else datetime.now(timezone.utc)

            processed_news.append({
                'title': article.get('headline', 'No title'),
                'summary': article.get('summary', ''),
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'published': published_dt,
                'category': article.get('category', 'General'),
                'image': article.get('image', ''),
                'related': article.get('related', ticker),
                'api_source': 'finnhub'
            })

        return processed_news

    except requests.exceptions.RequestException as e:
        log_error(e, "news_fetcher.get_finnhub_news", {"ticker": ticker})
        return []


# ========================================
# NEWS API FETCHER
# ========================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
@with_error_logging("news_fetcher.get_news_api_articles")
def get_news_api_articles(company_name: str, days_back: int = 7) -> List[Dict]:
    """
    Fetch news from News API

    Args:
        company_name: Company name to search for
        days_back: Number of days to look back

    Returns:
        List of news articles
    """
    if 'NEWS_API_KEY' not in st.secrets:
        log_warning("News API key not configured", "news_fetcher.get_news_api_articles")
        return []

    api_key = st.secrets['NEWS_API_KEY']

    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_back)

    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d'),
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': api_key,
        'pageSize': 20
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') != 'ok':
            return []

        articles = data.get('articles', [])

        # Process articles
        processed_news = []
        for article in articles:
            # Parse published date and ensure it's timezone-aware
            published_at = article.get('publishedAt', '')
            if published_at:
                try:
                    published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_dt = datetime.now(timezone.utc)
            else:
                published_dt = datetime.now(timezone.utc)

            processed_news.append({
                'title': article.get('title', 'No title'),
                'summary': article.get('description', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'published': published_dt,
                'category': 'General',
                'image': article.get('urlToImage', ''),
                'related': company_name,
                'api_source': 'newsapi'
            })

        return processed_news

    except requests.exceptions.RequestException as e:
        log_error(e, "news_fetcher.get_news_api_articles", {"company": company_name})
        return []
    except Exception as e:
        log_error(e, "news_fetcher.get_news_api_articles", {"company": company_name})
        return []


# ========================================
# SENTIMENT ANALYSIS
# ========================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_sentiment_simple(text: str) -> Dict:
    """
    Simple sentiment analysis using NLTK VADER

    Args:
        text: Text to analyze

    Returns:
        Sentiment scores and classification
    """
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        import nltk

        # Ensure VADER lexicon is downloaded
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)

        sia = SentimentIntensityAnalyzer()
        scores = sia.polarity_scores(text)

        # Classify sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
            emoji = '📈'
        elif compound <= -0.05:
            sentiment = 'negative'
            emoji = '📉'
        else:
            sentiment = 'neutral'
            emoji = '➖'

        return {
            'sentiment': sentiment,
            'emoji': emoji,
            'compound': compound,
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }

    except Exception as e:
        log_error(e, "news_fetcher.analyze_sentiment_simple", {"text_length": len(text)})
        return {
            'sentiment': 'neutral',
            'emoji': '➖',
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0
        }


@st.cache_data(ttl=3600)  # Cache for 1 hour
@with_error_logging("news_fetcher.analyze_sentiment_ai", show_error=False)
def analyze_sentiment_ai(text: str, title: str, model_id: Optional[str] = None) -> Dict:
    """
    AI-powered sentiment analysis using selected AI model
    Supports Google Gemini, OpenAI, Claude, and Grok
    Falls back to simple sentiment if AI fails

    Args:
        text: Article text
        title: Article title
        model_id: Specific model to use (if None, uses selected model)

    Returns:
        Enhanced sentiment analysis
    """
    # Fallback to simple sentiment
    simple_result = analyze_sentiment_simple(title + " " + text)

    try:
        # Get selected model
        if model_id is None:
            model_id = get_selected_model("selected_ai_model")

        model_info = get_model_info(model_id)

        if not model_info:
            return simple_result

        # Create prompt
        prompt = f"""Analyze the sentiment of this financial news article and its potential impact on the stock:

Title: {title}
Content: {text[:500]}

Respond with JSON only:
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "impact": "high/medium/low",
    "reasoning": "brief explanation"
}}"""

        # Generate response based on provider
        ai_result = None

        if model_info.provider == AIProvider.GEMINI:
            model = create_model_client(model_id)
            response = model.generate_content(prompt)

            if response and response.text:
                text_response = response.text.strip()
                # Extract JSON
                if '```json' in text_response:
                    text_response = text_response.split('```json')[1].split('```')[0]
                elif '```' in text_response:
                    text_response = text_response.split('```')[1].split('```')[0]
                ai_result = json.loads(text_response)

        elif model_info.provider == AIProvider.OPENAI:
            client = create_model_client(model_id)
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            ai_result = json.loads(response.choices[0].message.content)

        elif model_info.provider == AIProvider.CLAUDE:
            client = create_model_client(model_id)
            response = client.messages.create(
                model=model_id,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            text_response = response.content[0].text
            # Extract JSON
            if '```json' in text_response:
                text_response = text_response.split('```json')[1].split('```')[0]
            elif '```' in text_response:
                text_response = text_response.split('```')[1].split('```')[0]
            ai_result = json.loads(text_response)

        elif model_info.provider == AIProvider.GROK:
            client = create_model_client(model_id)
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            text_response = response.choices[0].message.content
            # Extract JSON
            if '```json' in text_response:
                text_response = text_response.split('```json')[1].split('```')[0]
            elif '```' in text_response:
                text_response = text_response.split('```')[1].split('```')[0]
            ai_result = json.loads(text_response)

        # Combine AI and simple analysis
        if ai_result:
            return {
                'sentiment': ai_result.get('sentiment', simple_result['sentiment']),
                'emoji': simple_result['emoji'],
                'compound': simple_result['compound'],
                'confidence': ai_result.get('confidence', 0.5),
                'impact': ai_result.get('impact', 'medium'),
                'reasoning': ai_result.get('reasoning', ''),
                'ai_powered': True,
                'model_used': model_info.display_name
            }

    except Exception as e:
        log_error(e, "news_fetcher.analyze_sentiment_ai",
                 {"title_length": len(title), "text_length": len(text), "model_id": model_id})

    return simple_result


# ========================================
# COMBINED NEWS FETCHER
# ========================================

@st.cache_data(ttl=900)  # Cache for 15 minutes
def get_all_news(ticker: str, company_name: str, days_back: int = 7,
                 use_ai_sentiment: bool = False) -> pd.DataFrame:
    """
    Fetch news from all available sources and combine

    Args:
        ticker: Stock ticker symbol
        company_name: Company name
        days_back: Number of days to look back
        use_ai_sentiment: Whether to use AI-powered sentiment (slower)

    Returns:
        DataFrame with all news articles and sentiment
    """
    all_news = []

    # Fetch from Finnhub
    finnhub_news = get_finnhub_news(ticker, days_back)
    all_news.extend(finnhub_news)

    # Fetch from News API
    newsapi_articles = get_news_api_articles(company_name, days_back)
    all_news.extend(newsapi_articles)

    if not all_news:
        return pd.DataFrame()

    # Remove duplicates based on title similarity
    unique_news = []
    seen_titles = set()

    for article in all_news:
        title_lower = article['title'].lower()[:50]  # First 50 chars
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(article)

    # Sort by date (most recent first)
    unique_news.sort(key=lambda x: x['published'], reverse=True)

    # Add sentiment analysis
    for article in unique_news:
        text = f"{article['title']} {article['summary']}"

        if use_ai_sentiment:
            sentiment = analyze_sentiment_ai(article['summary'], article['title'])
        else:
            sentiment = analyze_sentiment_simple(text)

        article.update(sentiment)

    # Convert to DataFrame
    df = pd.DataFrame(unique_news)

    return df


# ========================================
# NEWS SUMMARY STATISTICS
# ========================================

def get_news_sentiment_summary(news_df: pd.DataFrame) -> Dict:
    """
    Calculate aggregate sentiment statistics from news

    Args:
        news_df: DataFrame with news and sentiment

    Returns:
        Summary statistics
    """
    if news_df.empty:
        return {
            'total_articles': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'avg_sentiment': 0.0,
            'sentiment_trend': 'neutral'
        }

    total = len(news_df)
    positive = len(news_df[news_df['sentiment'] == 'positive'])
    negative = len(news_df[news_df['sentiment'] == 'negative'])
    neutral = len(news_df[news_df['sentiment'] == 'neutral'])

    avg_compound = news_df['compound'].mean() if 'compound' in news_df else 0.0

    # Determine overall trend
    if avg_compound >= 0.1:
        trend = 'bullish'
        trend_emoji = '🟢'
    elif avg_compound <= -0.1:
        trend = 'bearish'
        trend_emoji = '🔴'
    else:
        trend = 'neutral'
        trend_emoji = '🟡'

    return {
        'total_articles': total,
        'positive_count': positive,
        'negative_count': negative,
        'neutral_count': neutral,
        'positive_pct': (positive / total * 100) if total > 0 else 0,
        'negative_pct': (negative / total * 100) if total > 0 else 0,
        'neutral_pct': (neutral / total * 100) if total > 0 else 0,
        'avg_sentiment': avg_compound,
        'sentiment_trend': trend,
        'trend_emoji': trend_emoji
    }


# ========================================
# HELPER FUNCTIONS
# ========================================

def format_time_ago(published_date: datetime) -> str:
    """Format datetime as human-readable time ago"""
    now = datetime.now(published_date.tzinfo) if published_date.tzinfo else datetime.now(timezone.utc)
    diff = now - published_date

    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"


def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'


# ========================================
# X/TWITTER SENTIMENT (via Grok AI)
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes - social sentiment changes fast
@with_error_logging("news_fetcher.get_twitter_sentiment_grok")
def get_twitter_sentiment_grok(ticker: str, company_name: str) -> Dict:
    """
    Get Twitter/X sentiment analysis using Grok AI

    Uses Grok to analyze current Twitter sentiment about a stock/company

    Args:
        ticker: Stock ticker symbol
        company_name: Full company name

    Returns:
        Dict with sentiment analysis, trending topics, and key tweets summary
    """
    if 'XAI_API_KEY' not in st.secrets:
        log_warning("XAI (Grok) API key not configured", "news_fetcher.get_twitter_sentiment_grok")
        return {
            'available': False,
            'sentiment': 'neutral',
            'confidence': 0.0,
            'trending_score': 0,
            'volume': 'N/A',
            'key_topics': [],
            'summary': 'Twitter sentiment unavailable - XAI API key not configured'
        }

    api_key = st.secrets['XAI_API_KEY']

    # Grok API endpoint (OpenAI-compatible)
    url = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Craft prompt for Grok to analyze Twitter sentiment
    prompt = f"""Analyze the current Twitter/X sentiment for ${ticker} ({company_name}).

Provide a comprehensive sentiment analysis including:
1. Overall sentiment (positive/negative/neutral) and confidence level (0-1)
2. Trending score (0-10) - how much people are talking about it
3. Tweet volume estimate (low/medium/high/viral)
4. Top 3-5 trending topics/themes in tweets
5. Key sentiment drivers (why positive or negative)
6. Notable influencer sentiment (if any)

Respond ONLY in valid JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "trending_score": 0-10,
    "volume": "low|medium|high|viral",
    "key_topics": ["topic1", "topic2", "topic3"],
    "sentiment_drivers": ["driver1", "driver2"],
    "influencer_sentiment": "description or null",
    "summary": "2-3 sentence summary of Twitter sentiment",
    "bullish_signals": ["signal1", "signal2"],
    "bearish_signals": ["signal1", "signal2"]
}}

Focus on recent tweets (last 24-48 hours). Be objective and data-driven."""

    payload = {
        "model": "grok-beta",  # Grok's model name
        "messages": [
            {
                "role": "system",
                "content": "You are Grok, an AI with real-time access to X (Twitter) data. Analyze social media sentiment for stocks with accuracy and wit."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,  # Lower temperature for more consistent analysis
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'choices' not in data or not data['choices']:
            log_warning("Empty response from Grok API", "news_fetcher.get_twitter_sentiment_grok")
            return _get_fallback_twitter_sentiment()

        content = data['choices'][0]['message']['content']

        # Parse JSON response
        # Remove markdown code blocks if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]

        sentiment_data = json.loads(content.strip())

        # Add metadata
        sentiment_data['available'] = True
        sentiment_data['source'] = 'X/Twitter via Grok'
        sentiment_data['timestamp'] = datetime.now(timezone.utc).isoformat()
        sentiment_data['ticker'] = ticker

        return sentiment_data

    except requests.exceptions.RequestException as e:
        log_error(e, "news_fetcher.get_twitter_sentiment_grok",
                 {"ticker": ticker, "company": company_name})
        return _get_fallback_twitter_sentiment()
    except json.JSONDecodeError as e:
        log_error(e, "news_fetcher.get_twitter_sentiment_grok",
                 {"ticker": ticker, "response_content": content[:200] if 'content' in locals() else 'N/A'})
        return _get_fallback_twitter_sentiment()
    except Exception as e:
        log_error(e, "news_fetcher.get_twitter_sentiment_grok",
                 {"ticker": ticker})
        return _get_fallback_twitter_sentiment()


def _get_fallback_twitter_sentiment() -> Dict:
    """Fallback Twitter sentiment when API fails"""
    return {
        'available': False,
        'sentiment': 'neutral',
        'confidence': 0.0,
        'trending_score': 0,
        'volume': 'N/A',
        'key_topics': [],
        'sentiment_drivers': [],
        'influencer_sentiment': None,
        'summary': 'Twitter sentiment analysis unavailable at this time',
        'bullish_signals': [],
        'bearish_signals': []
    }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_social_sentiment_summary(ticker: str, company_name: str) -> Dict:
    """
    Get comprehensive social media sentiment summary

    Combines Twitter/X sentiment with other indicators

    Args:
        ticker: Stock ticker
        company_name: Company name

    Returns:
        Comprehensive social sentiment data
    """
    twitter_sentiment = get_twitter_sentiment_grok(ticker, company_name)

    # Calculate overall social sentiment score
    if twitter_sentiment['available']:
        sentiment = twitter_sentiment['sentiment']
        confidence = twitter_sentiment['confidence']
        trending = twitter_sentiment['trending_score'] / 10.0  # Normalize to 0-1

        # Weighted social score
        if sentiment == 'positive':
            base_score = 0.7 + (confidence * 0.3)
        elif sentiment == 'negative':
            base_score = 0.3 - (confidence * 0.3)
        else:
            base_score = 0.5

        # Adjust for trending/volume
        social_score = base_score * (0.7 + trending * 0.3)

        # Determine emoji
        if social_score >= 0.65:
            emoji = '🔥'
            label = 'Very Bullish'
        elif social_score >= 0.55:
            emoji = '📈'
            label = 'Bullish'
        elif social_score >= 0.45:
            emoji = '➖'
            label = 'Neutral'
        elif social_score >= 0.35:
            emoji = '📉'
            label = 'Bearish'
        else:
            emoji = '❄️'
            label = 'Very Bearish'
    else:
        social_score = 0.5
        emoji = '❓'
        label = 'Unknown'

    return {
        'twitter': twitter_sentiment,
        'overall_score': social_score,
        'overall_sentiment': label,
        'overall_emoji': emoji,
        'data_sources': ['X/Twitter'] if twitter_sentiment['available'] else []
    }


# ========================================
# GOOGLE TRENDS INTEGRATION
# ========================================

@st.cache_data(ttl=600)  # Cache for 10 minutes - trends change throughout the day
@with_error_logging("news_fetcher.get_google_trends_data")
def get_google_trends_data(ticker: str, company_name: str, timeframe: str = 'now 1-d') -> Dict:
    """
    Get Google Trends search interest data

    Args:
        ticker: Stock ticker
        company_name: Company name
        timeframe: Timeframe for trends ('now 1-d', 'now 7-d', 'today 1-m', 'today 3-m')

    Returns:
        Google Trends data with interest over time and related queries
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl='en-US', tz=360)

        # Build search keywords
        keywords = [ticker, company_name]

        # Get interest over time
        pytrends.build_payload(keywords, timeframe=timeframe)
        interest_df = pytrends.interest_over_time()

        if interest_df.empty:
            return {
                'available': False,
                'trend': 'neutral',
                'current_interest': 0,
                'trend_direction': 'flat',
                'related_queries': []
            }

        # Calculate trend metrics
        ticker_interest = interest_df[ticker] if ticker in interest_df else pd.Series()
        company_interest = interest_df[company_name] if company_name in interest_df else pd.Series()

        # Use whichever has more data
        if len(ticker_interest) > len(company_interest):
            interest_series = ticker_interest
        else:
            interest_series = company_interest if len(company_interest) > 0 else ticker_interest

        if len(interest_series) == 0:
            return {
                'available': False,
                'trend': 'neutral',
                'current_interest': 0,
                'trend_direction': 'flat',
                'related_queries': []
            }

        current_interest = interest_series.iloc[-1] if len(interest_series) > 0 else 0
        avg_interest = interest_series.mean()

        # Calculate trend direction
        if len(interest_series) >= 2:
            recent_avg = interest_series.iloc[-3:].mean() if len(interest_series) >= 3 else interest_series.iloc[-1]
            older_avg = interest_series.iloc[:len(interest_series)//2].mean()

            if recent_avg > older_avg * 1.2:
                trend_direction = 'rising'
                trend_emoji = '📈'
            elif recent_avg < older_avg * 0.8:
                trend_direction = 'falling'
                trend_emoji = '📉'
            else:
                trend_direction = 'stable'
                trend_emoji = '➖'
        else:
            trend_direction = 'stable'
            trend_emoji = '➖'

        # Get related queries
        try:
            related_queries = pytrends.related_queries()
            top_queries = []

            if ticker in related_queries and related_queries[ticker]['top'] is not None:
                top_df = related_queries[ticker]['top']
                if not top_df.empty:
                    top_queries = top_df.head(5)['query'].tolist()
        except:
            top_queries = []

        # Determine overall trend sentiment
        if current_interest >= 75:
            trend = 'very high'
        elif current_interest >= 50:
            trend = 'high'
        elif current_interest >= 25:
            trend = 'moderate'
        else:
            trend = 'low'

        return {
            'available': True,
            'trend': trend,
            'current_interest': int(current_interest),
            'avg_interest': float(avg_interest),
            'trend_direction': trend_direction,
            'trend_emoji': trend_emoji,
            'related_queries': top_queries[:5],
            'timeframe': timeframe,
            'data_points': len(interest_series),
            'peak_interest': int(interest_series.max()),
            'interest_series': interest_series.tolist()  # For charting
        }

    except ImportError:
        log_warning("pytrends not installed", "news_fetcher.get_google_trends_data")
        return {'available': False, 'trend': 'neutral', 'current_interest': 0}
    except Exception as e:
        log_error(e, "news_fetcher.get_google_trends_data",
                 {"ticker": ticker, "company": company_name})
        return {'available': False, 'trend': 'neutral', 'current_interest': 0}


@st.cache_data(ttl=300)  # Cache for 5 minutes - keep social sentiment fresh
def get_comprehensive_social_sentiment(ticker: str, company_name: str) -> Dict:
    """
    Get comprehensive social sentiment combining X/Twitter, Google Trends, and news

    Args:
        ticker: Stock ticker
        company_name: Company name

    Returns:
        Complete social sentiment analysis
    """
    # Get Twitter sentiment
    twitter_data = get_twitter_sentiment_grok(ticker, company_name)

    # Get Google Trends
    trends_data = get_google_trends_data(ticker, company_name)

    # Calculate combined sentiment score
    scores = []
    weights = []

    # Twitter sentiment (weight: 40%)
    if twitter_data['available']:
        twitter_score = 0.5  # Default neutral

        if twitter_data['sentiment'] == 'positive':
            twitter_score = 0.65 + (twitter_data['confidence'] * 0.25)
        elif twitter_data['sentiment'] == 'negative':
            twitter_score = 0.35 - (twitter_data['confidence'] * 0.25)

        # Adjust for trending
        trending_boost = twitter_data['trending_score'] / 100  # 0-0.1 boost
        twitter_score = min(1.0, twitter_score + trending_boost)

        scores.append(twitter_score)
        weights.append(0.4)

    # Google Trends (weight: 30%)
    if trends_data['available']:
        # Higher search interest = more attention (can be bullish or bearish)
        # Rising trend = positive signal, falling = negative
        interest_score = trends_data['current_interest'] / 100

        if trends_data['trend_direction'] == 'rising':
            trends_score = 0.5 + (interest_score * 0.3)
        elif trends_data['trend_direction'] == 'falling':
            trends_score = 0.5 - (interest_score * 0.2)
        else:
            trends_score = 0.5

        scores.append(trends_score)
        weights.append(0.3)

    # Calculate weighted average
    if scores:
        combined_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
    else:
        combined_score = 0.5

    # Determine overall sentiment label
    if combined_score >= 0.7:
        label = 'Very Bullish'
        emoji = '🔥'
        color = '#00CC96'
    elif combined_score >= 0.6:
        label = 'Bullish'
        emoji = '📈'
        color = '#26C281'
    elif combined_score >= 0.4:
        label = 'Neutral'
        emoji = '➖'
        color = '#95A5A6'
    elif combined_score >= 0.3:
        label = 'Bearish'
        emoji = '📉'
        color = '#F39C12'
    else:
        label = 'Very Bearish'
        emoji = '❄️'
        color = '#E74C3C'

    return {
        'combined_score': combined_score,
        'sentiment_label': label,
        'sentiment_emoji': emoji,
        'sentiment_color': color,
        'twitter': twitter_data,
        'google_trends': trends_data,
        'data_sources_count': sum([
            twitter_data.get('available', False),
            trends_data.get('available', False)
        ]),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
