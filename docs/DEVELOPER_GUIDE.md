# RetailAnalyst - Developer Guide

**Version:** 1.0
**Last Updated:** November 23, 2025
**Target Audience:** Developers, Contributors, Technical Team

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Key Components](#key-components)
5. [Data Fetching Strategy](#data-fetching-strategy)
6. [AI Integration](#ai-integration)
7. [Performance Optimization](#performance-optimization)
8. [Testing Strategy](#testing-strategy)
9. [Deployment](#deployment)
10. [Contributing Guidelines](#contributing-guidelines)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

### Technology Stack

**Core Framework:**
- **Streamlit 1.28+** - Web application framework
- **Python 3.11** - Primary programming language

**Data Sources:**
- **yfinance** - Primary market data (prices, fundamentals)
- **yahooquery** - Advanced queries, faster performance
- **Alpha Vantage** - Backup/fallback data provider
- **FRED API** - Economic indicators (Fed Funds rate, GDP, etc.)
- **Finnhub** - News, earnings calendar
- **Polygon.io** - Professional-grade market data (optional)
- **Financial Modeling Prep (FMP)** - Alternative fundamental data

**AI/ML:**
- **OpenAI (GPT-4)** - Text generation, analysis
- **Anthropic (Claude)** - Alternative LLM provider
- **Google Gemini** - Cost-effective LLM option
- **xAI (Grok)** - Additional LLM provider
- **Prophet** - Time series forecasting (Facebook)
- **VADER** - Sentiment analysis (rule-based)
- **FinBERT** - Financial sentiment (transformer-based)

**Data Processing:**
- **Pandas 2.0+** - Data manipulation
- **NumPy** - Numerical computing
- **TA-Lib / pandas_ta** - Technical indicators

**Visualization:**
- **Plotly 5.17+** - Interactive charts
- **Matplotlib** - Static visualizations

**Database:**
- **SQLite** - Local caching (MVP)
- **PostgreSQL** - Future scaling option

---

## Architecture

### Project Structure

```
Stocks/
├── Home.py                      # Landing page (entry point)
├── pages/                       # Multi-page Streamlit app
│   ├── 01_📊_Market_Overview_&_Economy.py
│   ├── 02_📈_Individual_Charts_&_Visuals.py
│   ├── 03_🔬_Fundamental_Analysis.py
│   ├── 04_🤝_Competitive_&_Market.py
│   ├── 05_🎲_Risk_&_Forecasting.py
│   ├── 06_💼_Portfolio_&_Strategy.py
│   ├── 07_🔧_Debug_Dashboard.py
│   ├── 08_📰_News_&_Sentiment.py
│   └── 09_📅_Earnings_&_Estimates.py
├── data_fetcher.py              # Core data fetching logic
├── advanced_charting.py         # Technical analysis, charting
├── valuation_models.py          # DCF, DDM, valuation
├── backtester.py                # Strategy backtesting
├── ai_services.py               # AI integration utilities
├── ai_model_config.py           # Multi-provider AI configuration
├── news_fetcher.py              # News aggregation, sentiment
├── correlation_factors.py       # Economic correlations
├── fear_greed_history.py        # Market sentiment indicators
├── visual_analysis_presets.py   # Pre-built visualizations
├── market_overview_advanced_visuals.py  # Advanced market visuals
├── performance_optimizer.py     # Caching, batch fetching
├── ticker_utils.py              # Ticker validation, utilities
├── app_utils.py                 # Shared UI components
├── global_sidebar.py            # Sidebar configuration
├── mode_config.py               # Trader/Investor mode system
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml             # API keys (DO NOT COMMIT)
├── docs/                        # Documentation
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
└── README.md                    # Project README
```

### Design Patterns

#### 1. **Modular Data Connectors**
**Pattern:** Strategy Pattern for data fetching

```python
# data_fetcher.py
def get_stock_price_data(ticker: str, period: str = "2y"):
    """Fetch stock price data with automatic fallback"""
    try:
        # Primary: yfinance
        return fetch_with_yfinance(ticker, period)
    except Exception as e:
        logger.warning(f"yfinance failed: {e}")
        try:
            # Fallback: yahooquery
            return fetch_with_yahooquery(ticker, period)
        except Exception as e2:
            logger.error(f"All providers failed")
            raise
```

**Benefits:**
- Resilient to API failures
- Easy to add new data providers
- Consistent interface across app

#### 2. **Aggressive Caching**
**Pattern:** Decorator pattern with Streamlit's `@st.cache_data`

```python
from mode_config import get_cache_ttl

@st.cache_data(ttl=get_cache_ttl("fast"))  # 60s (Trader) or 300s (Investor)
def get_stock_price_data(ticker: str, period: str = "2y"):
    # Expensive API call
    return data
```

**Cache Tiers:**
- **Fast (price data, news):** 60s (Trader) / 300s (Investor)
- **Medium (indicators, company info):** 300s (Trader) / 1800s (Investor)
- **Slow (fundamentals):** 900s (Trader) / 3600s (Investor)

**Benefits:**
- Reduces API calls by 50-70%
- Faster page loads
- Lower API costs

#### 3. **Hybrid Trading Mode**
**Pattern:** Configuration-based personalization

```python
# mode_config.py
TRADER_MODE = ModeConfig(
    cache_ttl_fast=60,      # 1 minute
    cache_ttl_medium=300,   # 5 minutes
    cache_ttl_slow=900,     # 15 minutes
    default_period="5d",
    default_interval="15m",
    features_enabled=["intraday_charts", "realtime_news"]
)

INVESTOR_MODE = ModeConfig(
    cache_ttl_fast=300,     # 5 minutes
    cache_ttl_medium=1800,  # 30 minutes
    cache_ttl_slow=3600,    # 1 hour
    default_period="1y",
    default_interval="1d",
    features_enabled=["fundamental_analysis", "long_term_forecasts"]
)
```

**Benefits:**
- Optimized UX for different user types
- Reduced API costs for long-term investors
- Faster updates for traders

#### 4. **Multi-Provider AI Integration**
**Pattern:** Factory pattern for LLM providers

```python
# ai_model_config.py
def call_ai_model(prompt, provider='auto', temperature=0.7):
    """Call AI model with automatic provider selection"""
    if provider == 'auto':
        provider = get_configured_provider()

    if provider == AIProvider.OPENAI:
        return call_openai(prompt, temperature)
    elif provider == AIProvider.ANTHROPIC:
        return call_anthropic(prompt, temperature)
    elif provider == AIProvider.GEMINI:
        return call_gemini(prompt, temperature)
    # ... etc
```

**Benefits:**
- Cost optimization (choose cheapest provider)
- Reliability (fallback if one provider fails)
- Flexibility (users can choose preferred model)

---

## Development Setup

### Prerequisites

- **Python 3.11+** (tested on 3.11, may work on 3.10+)
- **Git** for version control
- **Virtual environment** (venv, conda, or virtualenv)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd Stocks
```

#### 2. Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.28
yahooquery>=2.3.0
plotly>=5.17.0
requests>=2.31.0
openai>=1.0.0
anthropic>=0.5.0
google-generativeai>=0.3.0
```

#### 4. Configure API Keys

Copy the example secrets file:

```bash
cp .env.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your API keys:

```toml
# === Financial Data APIs ===
FINNHUB_API_KEY = "your_finnhub_key_here"
FRED_API_KEY = "your_fred_key_here"
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key_here"
POLYGON_API_KEY = "your_polygon_key_here"  # Optional
FMP_API_KEY = "your_fmp_key_here"  # Optional

# === News APIs ===
NEWS_API_KEY = "your_newsapi_key_here"

# === LLM APIs ===
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
GEMINI_API_KEY = "AIza..."
GOOGLE_API_KEY = "AIza..."  # Alias for GEMINI_API_KEY
XAI_API_KEY = "xai-..."  # Optional
```

**Free API Keys:**
- **FRED:** https://fred.stlouisfed.org/docs/api/api_key.html
- **Finnhub:** https://finnhub.io/register
- **Alpha Vantage:** https://www.alphavantage.co/support/#api-key
- **NewsAPI:** https://newsapi.org/register
- **Google Gemini:** https://aistudio.google.com/app/apikey

**Paid API Keys (optional):**
- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/
- **Polygon.io:** https://polygon.io/

#### 5. Run the Application

```bash
streamlit run Home.py
```

The app will open at `http://localhost:8501`

---

## Key Components

### 1. Data Fetcher (`data_fetcher.py`)

**Purpose:** Centralized data fetching with error handling and fallbacks

**Key Functions:**

```python
# Stock price data
get_stock_price_data(ticker, period="2y") -> pd.DataFrame

# Company information
get_company_info(stock: yf.Ticker) -> dict

# Financial statements
get_income_statement(stock: yf.Ticker) -> pd.DataFrame
get_balance_sheet(stock: yf.Ticker) -> pd.DataFrame
get_cash_flow(stock: yf.Ticker) -> pd.DataFrame

# News & sentiment
get_stock_news(stock: yf.Ticker) -> list

# Dividends
get_dividend_values(ticker: str) -> pd.DataFrame

# Competitor data
get_competitor_data(competitor_tickers: list) -> pd.DataFrame
```

**Design Principles:**
- ✅ All functions are cached using `@st.cache_data`
- ✅ Mode-aware TTLs (Trader vs Investor)
- ✅ Robust error handling with try/except
- ✅ Fallback to alternative data sources
- ✅ Logging for debugging

### 2. Advanced Charting (`advanced_charting.py`)

**Purpose:** Technical analysis and interactive charting

**Key Functions:**

```python
# Calculate 50+ technical indicators
calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame

# Detect chart patterns
detect_chart_patterns(df: pd.DataFrame) -> list

# Create candlestick charts with indicators
create_advanced_chart(
    df: pd.DataFrame,
    indicators: list,
    show_patterns: bool = True
) -> plotly.graph_objects.Figure
```

**Supported Indicators:**
- **Trend:** SMA, EMA, MACD, ADX
- **Momentum:** RSI, Stochastic, CCI, ROC
- **Volatility:** Bollinger Bands, ATR, Keltner Channels
- **Volume:** OBV, MFI, VWAP, Volume Profile

**Supported Patterns:**
- Head & Shoulders
- Double Top / Double Bottom
- Triangle patterns (Ascending, Descending, Symmetrical)
- Wedges (Rising, Falling)

### 3. Valuation Models (`valuation_models.py`)

**Purpose:** Fundamental valuation using DCF and DDM

**Key Functions:**

```python
# Discounted Cash Flow model
calculate_dcf(
    ticker: str,
    growth_rate: float = 0.05,
    terminal_growth: float = 0.025,
    discount_rate: float = 0.10,
    projection_years: int = 5
) -> dict

# Dividend Discount Model
calculate_ddm(
    ticker: str,
    growth_rate: float = 0.03,
    discount_rate: float = 0.08
) -> dict

# Scenario analysis
run_scenario_analysis(ticker: str) -> dict  # Bear, Base, Bull
```

**DCF Methodology:**
1. Fetch historical financials (Income Statement, Cash Flow)
2. Calculate Free Cash Flow (FCF = Operating CF - CapEx)
3. Project FCF for next 5-10 years using growth rate
4. Calculate Terminal Value using Gordon Growth Model
5. Discount all cash flows to present value using WACC
6. Compare fair value to current price (margin of safety)

**Features:**
- ✅ User-adjustable assumptions (growth, discount rate)
- ✅ Sensitivity analysis (what-if scenarios)
- ✅ Monte Carlo simulation (1,000+ iterations)
- ✅ Industry-specific adjustments (ROIC fade, margin compression)

### 4. Backtester (`backtester.py`)

**Purpose:** Test investment strategies against historical data

**Current Strategies:**
- ✅ DCF Valuation Backtest (buy when undervalued)
- ✅ Relative Valuation Backtest (P/E ratio-based)

**Missing Strategies (TO BE BUILT):**
- ❌ RSI Mean Reversion (buy RSI < 30, sell RSI > 70)
- ❌ Moving Average Crossover (50/200 SMA)
- ❌ Bollinger Band Breakouts

**Performance Metrics:**
- ✅ Mean Absolute Percentage Error (MAPE)
- ❌ Sharpe Ratio (TO BE BUILT)
- ❌ Maximum Drawdown (TO BE BUILT)
- ❌ Win Rate (TO BE BUILT)

### 5. AI Services (`ai_services.py`)

**Purpose:** AI-powered insights and analysis

**Key Functions:**

```python
# Multi-provider AI call
call_ai_model(
    prompt: str,
    provider: str = 'auto',
    temperature: float = 0.7
) -> str

# Chart pattern analysis
get_ai_chart_analysis(
    df: pd.DataFrame,
    ticker: str
) -> str

# Competitor discovery
get_ai_comparables(
    ticker: str,
    company_info: dict
) -> list

# News summarization
summarize_news(
    articles: list,
    ticker: str
) -> str
```

**AI Model Configuration:**

See [`ai_model_config.py`] for multi-provider setup. Supports:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude Opus, Claude Sonnet)
- Google Gemini (Gemini Pro, Gemini Flash)
- xAI (Grok)

**Cost Optimization:**
- Use cheaper models (Gemini Flash) for simple tasks
- Use expensive models (GPT-4, Claude Opus) for complex analysis
- Cache all AI responses for 24 hours

### 6. Mode Configuration (`mode_config.py`)

**Purpose:** Trader/Investor mode personalization

**Key Functions:**

```python
# Get current mode
get_current_mode() -> ModeType  # 'trader' or 'investor'

# Set mode
set_mode(mode: str) -> None

# Get cache TTL for current mode
get_cache_ttl(tier: str) -> int  # 'fast', 'medium', or 'slow'

# Check if feature should be shown
should_show_feature(feature: str) -> bool

# Render mode info banner
render_mode_info() -> None
```

**Usage Example:**

```python
from mode_config import get_cache_ttl, render_mode_info, should_show_feature

# Display mode banner
render_mode_info()

# Mode-aware caching
@st.cache_data(ttl=get_cache_ttl("fast"))
def fetch_prices(ticker):
    return data

# Conditional features
if should_show_feature("intraday_charts"):
    render_intraday_chart()

if should_show_feature("fundamental_analysis"):
    render_dcf_model()
```

---

## Data Fetching Strategy

### Multi-Provider Architecture

**Philosophy:** Never depend on a single data source

**Provider Hierarchy:**

1. **Primary:** yfinance (free, comprehensive, widely used)
2. **Secondary:** yahooquery (faster, more reliable for some queries)
3. **Tertiary:** Alpha Vantage (backup for price data)
4. **Specialized:** Finnhub (news), FRED (economic data), Polygon (professional-grade)

**Fallback Logic:**

```python
def get_stock_price_data(ticker: str, period: str = "2y"):
    """Fetch with automatic fallback"""
    providers = [
        ('yfinance', fetch_with_yfinance),
        ('yahooquery', fetch_with_yahooquery),
        ('alpha_vantage', fetch_with_alpha_vantage)
    ]

    for provider_name, fetch_func in providers:
        try:
            logger.info(f"Trying {provider_name}...")
            data = fetch_func(ticker, period)
            if data is not None and len(data) > 0:
                logger.info(f"✓ Success with {provider_name}")
                return data
        except Exception as e:
            logger.warning(f"✗ {provider_name} failed: {e}")
            continue

    raise ValueError("All data providers failed")
```

### Caching Strategy

**Cache Levels:**

| Data Type | Trader Mode TTL | Investor Mode TTL | Rationale |
|-----------|-----------------|-------------------|-----------|
| **Price data** | 60s | 300s | Traders need fresh prices, investors less sensitive |
| **News** | 60s | 300s | Time-sensitive for traders |
| **Technical indicators** | 300s | 1800s | Derived from prices, can lag slightly |
| **Company info** | 300s | 1800s | Changes infrequently (sector, industry) |
| **Fundamentals** | 900s | 3600s | Updated quarterly, no need for frequent refresh |
| **AI responses** | 3600s | 3600s | Expensive, cache aggressively |

**Cache Invalidation:**

Streamlit's `@st.cache_data` automatically handles TTL-based invalidation. Manual invalidation:

```python
# Clear specific cache
get_stock_price_data.clear()

# Clear all caches
st.cache_data.clear()
```

**Cache Monitoring:**

Use Debug Dashboard (`pages/07_🔧_Debug_Dashboard.py`) to view:
- Cache hit/miss rates
- API call counts
- Cache sizes

---

## AI Integration

### Multi-Provider Setup

**Configuration:** `ai_model_config.py`

**Provider Selection Logic:**

```python
def get_configured_provider() -> AIProvider:
    """Auto-detect which AI provider is configured"""
    if 'ANTHROPIC_API_KEY' in st.secrets:
        return AIProvider.ANTHROPIC  # Prefer Claude
    elif 'OPENAI_API_KEY' in st.secrets:
        return AIProvider.OPENAI
    elif 'GEMINI_API_KEY' in st.secrets or 'GOOGLE_API_KEY' in st.secrets:
        return AIProvider.GEMINI
    elif 'XAI_API_KEY' in st.secrets:
        return AIProvider.XAI
    else:
        raise ValueError("No AI provider configured")
```

**Cost Comparison:**

| Provider | Model | Cost (per 1M tokens) | Speed | Quality |
|----------|-------|----------------------|-------|---------|
| **OpenAI** | GPT-4 | $30 input / $60 output | Medium | Excellent |
| **OpenAI** | GPT-3.5 | $0.50 input / $1.50 output | Fast | Good |
| **Anthropic** | Claude Opus | $15 input / $75 output | Slow | Excellent |
| **Anthropic** | Claude Sonnet | $3 input / $15 output | Medium | Very Good |
| **Google** | Gemini Pro | $0.50 input / $1.50 output | Fast | Good |
| **Google** | Gemini Flash | $0.075 input / $0.30 output | Very Fast | Fair |
| **xAI** | Grok | $5 input / $15 output | Medium | Good |

**Recommendation:**
- **Development:** Use Gemini Flash (cheapest)
- **Production (free tier):** Use Gemini Pro (good quality, low cost)
- **Production (paid tier):** Use Claude Sonnet or GPT-4 (best quality)

### AI Use Cases

1. **Chart Analysis**
   - Input: OHLCV data + indicators
   - Output: "The stock shows bullish momentum with RSI at 65..."

2. **News Summarization**
   - Input: List of news articles
   - Output: "Key developments: 1) Earnings beat expectations, 2) New product launch..."

3. **Competitor Discovery**
   - Input: Company name, sector, industry
   - Output: List of competitor tickers

4. **Sentiment Analysis**
   - Input: News articles, social media posts
   - Output: Sentiment score (-1 to 1)

5. **Earnings Analysis**
   - Input: Earnings report, analyst estimates
   - Output: "Beat on EPS ($1.25 vs $1.20 est), missed on revenue..."

---

## Performance Optimization

### Strategies

#### 1. **Batch Fetching**

Instead of:
```python
# BAD: 10 API calls
for ticker in tickers:
    data = fetch_stock_data(ticker)
```

Do:
```python
# GOOD: 1 API call
data = batch_fetch_tickers(tickers)  # Uses performance_optimizer.py
```

#### 2. **Lazy Loading**

```python
# Load expensive data only when tab is selected
tab1, tab2, tab3 = st.tabs(["Overview", "Advanced", "AI"])

with tab1:
    render_overview()  # Fast, always loaded

with tab2:
    if st.session_state.get('show_advanced', False):
        render_advanced_charts()  # Expensive, lazy-loaded
```

#### 3. **Pagination**

```python
# Don't load all 500 news articles at once
articles = get_news(ticker, limit=20)  # Paginate
```

#### 4. **Compression**

For large datasets (e.g., 10 years of minute-level data), use compression:

```python
# performance_optimizer.py
def cache_with_compression(key: str, data: Any):
    """Cache large data with gzip compression"""
    import gzip, pickle
    compressed = gzip.compress(pickle.dumps(data))
    return compressed
```

### Monitoring Performance

Use the Debug Dashboard to track:
- Page load times
- API call counts
- Cache hit rates
- Memory usage

**Target Metrics:**
- Page load time: < 3 seconds (95th percentile)
- Cache hit rate: > 80%
- API calls: < 100/min (stay under rate limits)

---

## Testing Strategy

### Test Categories

#### 1. **Unit Tests**
Test individual functions in isolation

Example: `tests/test_data_fetcher.py`

```python
def test_get_stock_price_data():
    """Test fetching stock price data"""
    data = get_stock_price_data("AAPL", period="1mo")
    assert data is not None
    assert len(data) > 0
    assert 'Close' in data.columns
```

#### 2. **Integration Tests**
Test interactions between components

Example: `tests/test_advanced_charting.py`

```python
def test_create_chart_with_indicators():
    """Test creating chart with multiple indicators"""
    df = get_stock_price_data("AAPL", period="3mo")
    df = calculate_all_indicators(df)
    fig = create_advanced_chart(df, indicators=['SMA', 'RSI'])
    assert fig is not None
```

#### 3. **Validation Tests**
Test data accuracy against known benchmarks

Example: `tests/test_valuation_accuracy.py`

```python
def test_dcf_accuracy():
    """Validate DCF model against manual calculation"""
    # Known: AAPL fair value ~$150 (as of test date)
    result = calculate_dcf("AAPL", growth_rate=0.05)
    assert 140 <= result['fair_value'] <= 160
```

#### 4. **Mode-Aware Tests**
Test Trader/Investor mode functionality

Example: `test_mode_switching_comprehensive.py`

```python
def test_cache_ttl_differences():
    """Verify cache TTLs differ between modes"""
    set_mode('trader')
    trader_ttl = get_cache_ttl('fast')

    set_mode('investor')
    investor_ttl = get_cache_ttl('fast')

    assert trader_ttl < investor_ttl  # Trader mode refreshes faster
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_data_fetcher.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run recent bug fix tests
python test_recent_fixes.py
```

### Test Coverage Goals

- **Core modules:** >80% coverage
- **UI pages:** >50% coverage (harder to test Streamlit UI)
- **Critical paths:** 100% coverage (data fetching, valuation, backtesting)

---

## Deployment

### Option 1: Streamlit Community Cloud (Free)

**Pros:**
- ✅ Free hosting for public apps
- ✅ Easy deployment (connect GitHub repo)
- ✅ Automatic HTTPS
- ✅ Auto-deploy on git push

**Cons:**
- ❌ Limited resources (1 GB RAM, 1 CPU)
- ❌ Public apps only (unless on paid plan)
- ❌ Shared infrastructure (performance can vary)

**Steps:**
1. Push code to GitHub (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to https://share.streamlit.io
3. Connect GitHub account
4. Select repository and branch
5. Add secrets via Streamlit Cloud UI
6. Deploy!

**Secrets Management:**
In Streamlit Cloud dashboard, go to "Advanced settings" > "Secrets" and paste your `secrets.toml` content.

### Option 2: AWS EC2 (Paid, ~$10-50/month)

**Pros:**
- ✅ Full control over infrastructure
- ✅ Private apps
- ✅ Scalable (upgrade instance as needed)
- ✅ Custom domain

**Cons:**
- ❌ Requires DevOps knowledge
- ❌ Manual setup and maintenance
- ❌ Costs money

**Steps:**
1. Launch EC2 instance (t2.micro or t3.small)
2. Install Python, dependencies
3. Clone repository
4. Set up systemd service to run `streamlit run Home.py`
5. Configure Nginx reverse proxy
6. Set up SSL with Let's Encrypt
7. Point domain to EC2 instance

**Estimated Costs:**
- EC2 t2.micro (1 vCPU, 1 GB RAM): $8-10/month
- EC2 t3.small (2 vCPU, 2 GB RAM): $15-20/month
- Domain: $12/year

### Option 3: Docker + Cloud Run / Heroku

**Pros:**
- ✅ Containerized (consistent across environments)
- ✅ Auto-scaling (Cloud Run)
- ✅ Pay-per-use pricing (Cloud Run)

**Cons:**
- ❌ Requires Docker knowledge
- ❌ More complex setup

**Dockerfile Example:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## Contributing Guidelines

### Code Style

- **Formatter:** Use `black` for Python code formatting
- **Linter:** Use `ruff` or `flake8`
- **Type Hints:** Encouraged but not required
- **Docstrings:** Use Google-style docstrings for all public functions

**Example:**

```python
def calculate_dcf(
    ticker: str,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10
) -> dict:
    """
    Calculate Discounted Cash Flow valuation.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        growth_rate: Expected annual revenue growth rate (default: 5%)
        discount_rate: Discount rate / WACC (default: 10%)

    Returns:
        dict: {
            'fair_value': float,
            'current_price': float,
            'margin_of_safety': float,
            'recommendation': str
        }

    Raises:
        ValueError: If ticker is invalid or data unavailable
    """
    # Implementation
    pass
```

### Git Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/rsi-backtesting
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: implement RSI backtesting strategy"
   ```

3. **Push to remote:**
   ```bash
   git push origin feature/rsi-backtesting
   ```

4. **Create pull request** on GitHub

5. **Code review** (if working with team)

6. **Merge to main** after approval

### Commit Message Format

Use conventional commits:

- `feat: add new feature` (new functionality)
- `fix: fix bug` (bug fix)
- `docs: update documentation` (documentation only)
- `style: format code` (formatting, no code change)
- `refactor: refactor code` (restructuring, no behavior change)
- `test: add tests` (adding tests)
- `chore: update dependencies` (maintenance tasks)

---

## Troubleshooting

### Common Issues

#### 1. **"Module not found" error**

**Cause:** Missing dependency

**Fix:**
```bash
pip install -r requirements.txt
```

#### 2. **"API key not found" error**

**Cause:** Missing API key in `secrets.toml`

**Fix:**
- Check `.streamlit/secrets.toml` exists
- Verify key name matches what's in code (e.g., `FINNHUB_API_KEY`)
- Restart Streamlit app

#### 3. **"Rate limit exceeded" error**

**Cause:** Too many API calls

**Fix:**
- Increase cache TTLs in `mode_config.py`
- Reduce number of tickers analyzed simultaneously
- Wait a few minutes for rate limit to reset

#### 4. **Slow page loads (>10 seconds)**

**Cause:** Inefficient data fetching

**Fix:**
- Check cache hit rates in Debug Dashboard
- Use batch fetching (`performance_optimizer.py`)
- Reduce number of indicators calculated
- Enable lazy loading for expensive components

#### 5. **"Streamlit app freezing" error**

**Cause:** Blocking operations in main thread

**Fix:**
- Use `@st.cache_data` for expensive operations
- Move long-running tasks to background (future: use Streamlit's async support)
- Show spinner while loading: `with st.spinner("Loading..."):`

#### 6. **"Google API key error" (recent fix)**

**Cause:** Code looks for `GOOGLE_API_KEY` but secrets has `GEMINI_API_KEY`

**Fix:** ✅ Already fixed - both keys are now supported (see `test_recent_fixes.py`)

#### 7. **"Plotly annotation bgcolor error" (recent fix)**

**Cause:** Invalid `bgcolor` in `annotation_font` dict

**Fix:** ✅ Already fixed - removed invalid property from `visual_analysis_presets.py:1549`

### Debug Tools

#### 1. **Streamlit Debug Mode**

Add to `.streamlit/config.toml`:

```toml
[runner]
fastReruns = true

[logger]
level = "debug"
```

#### 2. **Python Debugger**

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

#### 3. **Streamlit Session State Inspection**

```python
st.write("Session State:", st.session_state)
```

#### 4. **Cache Inspection**

```python
# See what's cached
st.write("Cache info:", get_stock_price_data.cache_info())
```

---

## Appendix

### Useful Resources

**Streamlit:**
- Official Docs: https://docs.streamlit.io
- Gallery: https://streamlit.io/gallery
- Forum: https://discuss.streamlit.io

**Data APIs:**
- yfinance: https://github.com/ranaroussi/yfinance
- FRED: https://fred.stlouisfed.org/docs/api/
- Finnhub: https://finnhub.io/docs/api

**AI APIs:**
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com
- Google Gemini: https://ai.google.dev/docs

**Technical Analysis:**
- TA-Lib: https://mrjbq7.github.io/ta-lib/
- pandas_ta: https://github.com/twopirllc/pandas-ta

### Performance Benchmarks

**Target Metrics (95th percentile):**
- Home page: < 2 seconds
- Market Overview: < 3 seconds
- Individual Charts: < 4 seconds (with indicators)
- Fundamental Analysis: < 3 seconds
- AI-powered features: < 8 seconds

**Actual Performance (to be measured):**
- TBD after production deployment

---

**Document Version:** 1.0
**Classification:** Internal / Developer Use
**Maintainer:** Development Team
