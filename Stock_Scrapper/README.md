# Stock Ticker Data Scraper

A comprehensive Python scraper that retrieves news articles, Reddit posts, and search results for any stock ticker, with built-in sentiment analysis.

## Features

- **Multiple Data Sources**:
  - Reddit posts from investing-related subreddits
  - News articles via NewsAPI
  - Yahoo Finance news feed
  - Google search results (requires API)

- **Sentiment Analysis**: Automatically analyzes sentiment (positive, negative, neutral) for all collected text
- **Structured Output**: Exports data to CSV, JSON, or Excel with pandas DataFrames
- **Date Filtering**: Only retrieves data from the past month
- **Rate Limiting**: Built-in delays to respect API limits

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download NLTK Data (for TextBlob)

```python
python -m textblob.download_corpora
```

### 3. Get API Keys (Optional but Recommended)

#### NewsAPI (Free tier available)
- Visit: https://newsapi.org/
- Sign up for a free API key
- Free tier: 100 requests/day, 1 request/second

#### Reddit API (Free)
- Visit: https://www.reddit.com/prefs/apps
- Click "Create App" or "Create Another App"
- Choose "script" as the app type
- Note your `client_id` and `client_secret`

## Usage

### Basic Usage (No API Keys Required)

```python
from stock_scraper import StockDataScraper

# Initialize scraper
scraper = StockDataScraper("AAPL")

# Scrape all available sources
df = scraper.scrape_all()

# Save results
df.to_csv("AAPL_data.csv", index=False)
```

### Enhanced Usage (With API Keys)

```python
from stock_scraper_enhanced import EnhancedStockDataScraper

# Configuration with API keys
config = {
    'reddit_client_id': 'YOUR_REDDIT_CLIENT_ID',
    'reddit_client_secret': 'YOUR_REDDIT_CLIENT_SECRET',
    'reddit_user_agent': 'StockScraper/1.0',
    'news_api_key': 'YOUR_NEWS_API_KEY'
}

# Initialize scraper
scraper = EnhancedStockDataScraper("TSLA", config)

# Scrape specific sources
df = scraper.scrape_all(sources=['reddit', 'news', 'yahoo'])

# Export to multiple formats
scraper.export_to_csv(df, "TSLA_data.csv")
scraper.export_to_json(df, "TSLA_data.json")
scraper.export_to_excel(df, "TSLA_data.xlsx")
```

### Using Environment Variables

Create a `.env` file:

```bash
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=StockScraper/1.0
NEWS_API_KEY=your_news_api_key_here
```

Then run:

```python
from stock_scraper_enhanced import EnhancedStockDataScraper, load_config_from_env

config = load_config_from_env()
scraper = EnhancedStockDataScraper("GME", config)
df = scraper.scrape_all()
```

### Command Line Usage

Run the basic scraper:
```bash
python stock_scraper.py
```

Run the enhanced scraper:
```bash
python stock_scraper_enhanced.py
```

## Output Format

The scraper returns a pandas DataFrame with the following columns:

- `source`: Data source (Reddit, News, Yahoo Finance)
- `title`: Article/post title
- `text`: Full text content (truncated to 1000 chars)
- `url`: Link to original content
- `date`: Publication date
- `sentiment`: Sentiment classification (positive/negative/neutral)
- `polarity`: Sentiment score (-1 to 1)
- `subjectivity`: Subjectivity score (0 to 1)

### Additional columns by source:

**Reddit:**
- `subreddit`: Name of subreddit
- `score`: Reddit post score (upvotes - downvotes)
- `num_comments`: Number of comments

**News:**
- `outlet`: News outlet name
- `author`: Article author

## Customization

### Change Target Subreddits

Edit the `subreddits` list in the scraping methods:

```python
subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket', 
              'options', 'Daytrading', 'SecurityAnalysis']
```

### Adjust Time Range

Change the `timedelta` parameter:

```python
# For 2 weeks instead of 1 month
if date > datetime.now() - timedelta(days=14):
    # process data
```

### Modify Sentiment Thresholds

Adjust the polarity thresholds in `analyze_sentiment()`:

```python
if polarity > 0.15:  # More strict for positive
    return 'positive'
elif polarity < -0.15:  # More strict for negative
    return 'negative'
```

### Add Custom Sources

Add your own scraping methods following this pattern:

```python
def scrape_custom_source(self) -> List[Dict]:
    results = []
    # Your scraping logic here
    # Each result should be a dictionary with:
    # - source, title, text, url, date
    # - sentiment analysis added automatically
    return results
```

## Rate Limits and Best Practices

- **Reddit JSON API**: ~60 requests per minute (no auth)
- **Reddit PRAW**: ~60 requests per minute (with auth)
- **NewsAPI**: 100 requests/day on free tier
- **Yahoo Finance RSS**: No official limit, but add delays

Built-in delays:
- 1-2 seconds between requests to same source
- Respects HTTP 429 (Too Many Requests) responses

## Troubleshooting

### "TextBlob not installed"
```bash
pip install textblob
python -m textblob.download_corpora
```

### "PRAW not available"
```bash
pip install praw
```

### Reddit API returns 429 (Rate Limited)
- Increase sleep delays between requests
- Use Reddit API authentication (PRAW) instead of JSON API
- Reduce the number of subreddits or posts requested

### NewsAPI returns 429
- You've exceeded free tier limits (100/day)
- Wait 24 hours or upgrade to paid tier

### No data collected
- Check your internet connection
- Verify ticker symbol is correct
- Some tickers may have little social media discussion
- Try a more popular stock (e.g., AAPL, TSLA, GME)

## Legal and Ethical Considerations

- **Respect robots.txt**: This scraper respects rate limits and includes delays
- **Terms of Service**: Review TOS for each platform you scrape
- **Personal Use**: This tool is for personal research and education
- **No Redistribution**: Don't redistribute scraped data commercially
- **API Keys**: Keep your API keys private and secure

## Example Output

```
=== Starting scrape for $AAPL ===

Scraping Reddit for $AAPL...
Found 45 Reddit posts

Scraping Yahoo Finance for $AAPL...
Found 23 Yahoo Finance articles

Scraping news for $AAPL...
Found 67 news articles

=== Scrape complete ===
Total items collected: 135

Sentiment breakdown:
positive     67
neutral      45
negative     23
Name: sentiment, dtype: int64
```

## Contributing

Feel free to submit issues or pull requests for:
- Additional data sources
- Improved sentiment analysis
- Better error handling
- New features

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with all applicable terms of service and laws.

## Disclaimer

This tool is for informational and educational purposes only. It should not be used as the sole basis for investment decisions. Always conduct thorough research and consult with financial professionals before making investment decisions.
