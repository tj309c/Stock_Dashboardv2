# True Stock Ticker Web Scraper - NO API KEYS REQUIRED! 🚀

A powerful Python web scraper that collects stock market data **without requiring any API keys or paid services**. Scrapes news articles, Reddit posts, and financial data directly from public websites.

## ✨ Key Features

- **🆓 100% FREE** - No API keys, no paid services, no limits
- **📰 Multiple Sources** - Reddit, Finviz, Yahoo Finance, MarketWatch, Seeking Alpha
- **😊 Sentiment Analysis** - Automatically analyzes positive/negative/neutral sentiment
- **📊 Structured Output** - Exports to CSV, Excel, or JSON with Pandas
- **⏰ Time Filtered** - Only retrieves data from the past month
- **🎯 No JavaScript Required** - Works with simple HTTP requests

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install requests pandas beautifulsoup4 lxml textblob
python -m textblob.download_corpora
```

### 2. Run the Scraper

```python
python true_web_scraper.py
```

That's it! No API keys, no configuration needed.

## 📖 Usage Examples

### Basic Usage

```python
from true_web_scraper import TrueStockScraper

# Create scraper for any stock
scraper = TrueStockScraper("AAPL")

# Scrape all sources
df = scraper.scrape_all()

# Save results
df.to_csv("apple_data.csv", index=False)
```

### Scrape Specific Sources

```python
# Only scrape Reddit and Yahoo Finance
df = scraper.scrape_all(sources=['reddit', 'yahoo'])

# Only scrape news sources (no Reddit)
df = scraper.scrape_all(sources=['finviz', 'yahoo', 'marketwatch'])
```

### Analyze Results

```python
# View sentiment breakdown
print(df['sentiment'].value_counts())

# Get most positive news
positive = df[df['sentiment'] == 'positive'].head(10)

# Filter by source
reddit_posts = df[df['source'] == 'Reddit']
news_articles = df[df['source'] != 'Reddit']

# Sort by Reddit score
top_reddit = df[df['source'] == 'Reddit'].sort_values('score', ascending=False)
```

## 📊 Data Sources

| Source | Type | What It Scrapes |
|--------|------|-----------------|
| **Reddit** | Social | Posts from r/wallstreetbets, r/stocks, r/investing, r/StockMarket, r/options |
| **Finviz** | Financial | Latest news headlines and links |
| **Yahoo Finance** | Financial | RSS news feed for the ticker |
| **MarketWatch** | Financial | News articles and updates |
| **Seeking Alpha** | Financial | Analysis and news articles |

## 📋 Output Format

The scraper returns a Pandas DataFrame with these columns:

| Column | Description |
|--------|-------------|
| `source` | Where the data came from (Reddit, Finviz, etc.) |
| `title` | Headline or post title |
| `text` | Full text content |
| `url` | Link to original source |
| `date` | Publication date |
| `sentiment` | Positive, negative, or neutral |
| `polarity` | Sentiment score from -1 to 1 |
| `subjectivity` | How subjective the text is (0-1) |

**Reddit-specific columns:**
- `subreddit` - Which subreddit the post is from
- `score` - Reddit upvotes minus downvotes
- `num_comments` - Number of comments on the post

## 🎯 Example Output

```
============================================================
TRUE WEB SCRAPER - NO API KEYS NEEDED
Scraping data for $TSLA
Sources: reddit, finviz, yahoo, marketwatch, seekingalpha
============================================================

Scraping Reddit for $TSLA...
Found 67 Reddit posts

Scraping Finviz news for $TSLA...
Found 15 Finviz articles

Scraping Yahoo Finance for $TSLA...
Found 28 Yahoo Finance articles

Scraping MarketWatch for $TSLA...
Found 12 MarketWatch articles

Scraping Seeking Alpha for $TSLA...
Found 8 Seeking Alpha articles

============================================================
SCRAPE COMPLETE
============================================================
Total unique items: 130

By source:
Reddit            67
Yahoo Finance     28
Finviz            15
MarketWatch       12
Seeking Alpha      8

Sentiment breakdown:
positive    58
neutral     45
negative    27

Average sentiment polarity: 0.142
```

## ⚙️ Advanced Features

### Custom Date Range

Modify the time filter in the code:

```python
# Change from 30 days to 7 days
if date > datetime.now() - timedelta(days=7):
    # include this data
```

### Adjust Sentiment Thresholds

```python
# In analyze_sentiment() method
if polarity > 0.2:  # More strict for positive
    label = 'positive'
elif polarity < -0.2:  # More strict for negative
    label = 'negative'
```

### Add More Subreddits

```python
# In scrape_reddit_old() method
subreddits = [
    'wallstreetbets', 'stocks', 'investing', 
    'StockMarket', 'options', 'Daytrading',
    'SecurityAnalysis', 'ValueInvesting'
]
```

### Export to Excel with Formatting

```python
df.to_excel('tesla_data.xlsx', index=False)
```

## 🛡️ Rate Limiting & Ethics

The scraper includes built-in delays to be respectful:
- 2 seconds between Reddit requests
- 1-2 seconds between news site requests
- Uses proper User-Agent headers
- Doesn't overwhelm servers

**Please use responsibly:**
- Don't run too frequently (once per hour is reasonable)
- Don't scrape excessively large amounts of data
- Respect robots.txt files
- Use data for personal research only

## ❗ Troubleshooting

### "No data collected"

**Possible causes:**
1. **Invalid ticker** - Make sure you're using the correct stock symbol
2. **Low discussion** - Some stocks aren't discussed much online
3. **Anti-scraping measures** - Some sites may temporarily block requests
4. **Network issues** - Check your internet connection

**Solutions:**
- Try a more popular stock (AAPL, TSLA, GME, NVDA)
- Wait a few minutes and try again
- Use a VPN if you're blocked
- Try scraping fewer sources at once

### "TextBlob not installed"

```bash
pip install textblob
python -m textblob.download_corpora
```

### "BeautifulSoup can't parse"

```bash
pip install lxml
# or
pip install html5lib
```

### Reddit returns no results

- Use `old.reddit.com` URLs (already done in the code)
- Check if Reddit is accessible in your region
- Try the JSON API fallback (in the old scraper versions)

### "403 Forbidden" or "429 Too Many Requests"

- **Wait longer between requests** - Increase sleep times
- **Use different User-Agent** - Change the header string
- **Try at different times** - Some sites have stricter limits during peak hours

## 🔧 How It Works

The scraper uses these techniques:

1. **HTTP Requests** - Uses Python `requests` library to fetch web pages
2. **HTML Parsing** - BeautifulSoup extracts data from HTML
3. **RSS Feeds** - Reads XML feeds (Yahoo Finance)
4. **Old Reddit** - Uses old.reddit.com which doesn't require JavaScript
5. **Sentiment Analysis** - TextBlob analyzes text sentiment
6. **Data Cleaning** - Removes duplicates and formats dates

## 📦 Complete File Structure

```
stock-scraper/
├── true_web_scraper.py      # Main scraper (NO API keys needed)
├── stock_scraper.py          # Basic version
├── stock_scraper_enhanced.py # Version with optional API support
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── .env.example             # Environment variables template
```

## 🆚 Comparison: Free Scraper vs API Version

| Feature | True Web Scraper | API Version |
|---------|------------------|-------------|
| Cost | 100% Free | Free tier limits |
| API Keys | None needed | Required |
| Setup | Install & run | Get keys, configure |
| Rate Limits | Respectful delays | API limits (100/day) |
| Data Sources | 5+ sources | 2-3 sources |
| Reliability | May break if sites change | More stable |
| Data Volume | Moderate | Higher with paid tiers |

**Recommendation:** Start with the true web scraper! It's free and works great for most use cases.

## 📝 Legal & Ethical Considerations

- ✅ **Public Data** - Only scrapes publicly available information
- ✅ **Personal Use** - Intended for research and education
- ✅ **Respectful** - Includes rate limiting and delays
- ✅ **No Login** - Doesn't bypass authentication
- ⚠️ **Check ToS** - Review each site's Terms of Service
- ⚠️ **No Redistribution** - Don't sell or redistribute scraped data
- ⚠️ **Be Responsible** - Don't abuse or overwhelm servers

## 🎓 Educational Use

This scraper is perfect for:
- Learning web scraping techniques
- Sentiment analysis projects
- Stock market research
- Data science portfolios
- Academic research
- Personal investment analysis

## 🤝 Contributing

Want to improve the scraper? Consider:
- Adding more data sources
- Improving sentiment analysis
- Better error handling
- More export formats
- Chart generation
- Real-time monitoring

## ⭐ Popular Tickers to Try

Test the scraper with these highly-discussed stocks:

**Tech:**
- AAPL (Apple)
- TSLA (Tesla)
- NVDA (Nvidia)
- MSFT (Microsoft)
- GOOGL (Google)

**Meme Stocks:**
- GME (GameStop)
- AMC (AMC Entertainment)
- BB (BlackBerry)

**Finance:**
- JPM (JPMorgan)
- BAC (Bank of America)
- GS (Goldman Sachs)

## 🔮 Future Enhancements

Potential features to add:
- [ ] Twitter/X integration
- [ ] StockTwits scraping
- [ ] Chart generation
- [ ] Real-time monitoring
- [ ] Email alerts
- [ ] Historical data collection
- [ ] Price correlation analysis
- [ ] Multi-ticker comparison

## 📄 License

This project is for educational purposes. Use responsibly and in accordance with all applicable laws and terms of service.

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It should not be used as the sole basis for investment decisions. Always:
- Do your own research
- Consult financial professionals
- Understand the risks
- Never invest more than you can afford to lose

**The scraped data may not be complete or accurate. Always verify information from official sources.**

---

Made with ❤️ for the Python community. Happy scraping! 🐍
