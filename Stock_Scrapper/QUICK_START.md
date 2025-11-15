# 🚀 QUICK START GUIDE - Stock Scraper

## Which scraper should I use?

### ⭐ **true_web_scraper.py** (RECOMMENDED - NO API KEYS!)
Use this if you want:
- ✅ No API keys or registration
- ✅ Completely free
- ✅ Multiple sources (Reddit, Finviz, Yahoo, MarketWatch, Seeking Alpha)
- ✅ Simple and fast setup

### 📦 **stock_scraper.py** (Basic)
Use this if you want:
- Simple code to learn from
- Fewer sources but faster
- Yahoo Finance + Reddit only

### 🔧 **stock_scraper_enhanced.py** (Advanced)
Use this if you have:
- Reddit API credentials
- NewsAPI key
- Need maximum data volume

---

## 🎯 Installation (2 minutes)

### Step 1: Install Python packages
```bash
pip install requests pandas beautifulsoup4 lxml textblob
```

### Step 2: Download sentiment data
```bash
python -m textblob.download_corpora
```

### Step 3: Run the scraper!
```bash
python true_web_scraper.py
```

That's it! No configuration needed.

---

## 💻 Example Session

```bash
$ python true_web_scraper.py

============================================================
TRUE STOCK SCRAPER - NO API KEYS REQUIRED
============================================================

This scraper works by directly scraping public websites.
No API keys or paid services needed!

Enter stock ticker (e.g., AAPL, TSLA, GME): TSLA

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

✓ Data saved to: TSLA_scraped_data_20241112_231530.csv
```

---

## 📝 Simple Python Script

Create a file called `my_scraper.py`:

```python
from true_web_scraper import TrueStockScraper

# Scrape Apple stock data
scraper = TrueStockScraper("AAPL")
df = scraper.scrape_all()

# Show results
print(f"Collected {len(df)} items")
print(df[['source', 'title', 'sentiment']].head(10))

# Save to CSV
df.to_csv("apple_data.csv", index=False)
print("Saved to apple_data.csv")
```

Run it:
```bash
python my_scraper.py
```

---

## 🎨 Analyze Multiple Stocks

```python
from true_web_scraper import TrueStockScraper
import pandas as pd

# List of tickers to analyze
tickers = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']

all_data = []

for ticker in tickers:
    print(f"\nScraping {ticker}...")
    scraper = TrueStockScraper(ticker)
    df = scraper.scrape_all()
    df['ticker'] = ticker  # Add ticker column
    all_data.append(df)
    
    # Small delay between tickers
    import time
    time.sleep(5)

# Combine all data
combined = pd.concat(all_data, ignore_index=True)

# Save
combined.to_csv("multi_stock_analysis.csv", index=False)

# Analyze
print("\nSentiment by Ticker:")
print(combined.groupby(['ticker', 'sentiment']).size())
```

---

## 📊 What Can You Do With The Data?

### 1. Sentiment Analysis
```python
# Find most positive news
positive = df[df['sentiment'] == 'positive']
print(positive[['title', 'source']].head())

# Calculate sentiment score
sentiment_score = df['polarity'].mean()
print(f"Overall sentiment: {sentiment_score:.2f}")
```

### 2. Reddit Analysis
```python
# Top Reddit posts
reddit = df[df['source'] == 'Reddit']
top_posts = reddit.nlargest(10, 'score')
print(top_posts[['title', 'score', 'subreddit']])
```

### 3. News Sources
```python
# Count articles by source
print(df['source'].value_counts())

# Recent news only
import pandas as pd
recent = df[df['date'] > pd.Timestamp.now() - pd.Timedelta(days=7)]
```

### 4. Export to Excel
```python
# Save with multiple sheets
with pd.ExcelWriter('analysis.xlsx') as writer:
    df.to_excel(writer, sheet_name='All Data', index=False)
    
    positive = df[df['sentiment'] == 'positive']
    positive.to_excel(writer, sheet_name='Positive', index=False)
    
    reddit = df[df['source'] == 'Reddit']
    reddit.to_excel(writer, sheet_name='Reddit', index=False)
```

---

## 🔥 Popular Tickers to Try

**Tech Giants:**
- AAPL (Apple) - Lots of discussion
- MSFT (Microsoft) - Steady news flow
- GOOGL (Google) - Regular updates
- NVDA (Nvidia) - Hot topic
- TSLA (Tesla) - High sentiment volatility

**Meme Stocks:**
- GME (GameStop) - Very active Reddit
- AMC (AMC Entertainment) - High social volume
- BB (BlackBerry) - Frequent mentions

**Finance:**
- SPY (S&P 500 ETF) - Market sentiment
- QQQ (Nasdaq ETF) - Tech sector sentiment

---

## ⚠️ Troubleshooting

### Problem: "No data collected"
**Solution:** 
1. Try a more popular ticker (AAPL, TSLA)
2. Check your internet connection
3. Wait a few minutes and try again

### Problem: "Module not found"
**Solution:**
```bash
pip install requests pandas beautifulsoup4 lxml textblob
```

### Problem: "Sentiment not working"
**Solution:**
```bash
pip install textblob
python -m textblob.download_corpora
```

### Problem: "403 Forbidden"
**Solution:**
- Wait a few minutes between runs
- Some sites may temporarily block requests
- Try using a VPN

---

## 📖 Next Steps

1. **Read the full README** - See `README_NO_API.md` for detailed docs
2. **Customize sources** - Edit which websites to scrape
3. **Adjust date ranges** - Change from 30 days to any timeframe
4. **Build a dashboard** - Use Plotly or Streamlit to visualize
5. **Automate** - Run on a schedule with cron or Task Scheduler

---

## 🎓 Learning Resources

- **Web Scraping**: BeautifulSoup documentation
- **Pandas**: Data manipulation tutorials
- **Sentiment Analysis**: TextBlob guide
- **Stock Analysis**: Investopedia basics

---

## 💡 Pro Tips

1. **Run once per hour** - Don't scrape too frequently
2. **Save your data** - Build a historical database
3. **Compare tickers** - Scrape multiple stocks for insights
4. **Check sentiment trends** - Track how sentiment changes over time
5. **Combine with price data** - Use yfinance for stock prices

---

## 📞 Need Help?

- Check `README_NO_API.md` for full documentation
- Review the code comments for detailed explanations
- Try with a simple ticker like AAPL first
- Make sure all dependencies are installed

---

**Happy Scraping! 🚀📈**
