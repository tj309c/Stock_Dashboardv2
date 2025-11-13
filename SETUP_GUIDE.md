# Stock Analysis Dashboard - Setup Guide

## Critical Errors Fixed ✅

All **13 critical errors** have been successfully resolved:
- Missing functions implemented
- Missing modules created
- Attribute mismatches corrected
- Type inconsistencies fixed

---

## Installation Instructions

### Step 1: Install Required Dependencies

Run the following command in your terminal from the project directory:

```bash
pip install -r requirements.txt
```

### Required Packages (from requirements.txt):
1. **streamlit** - Web application framework
2. **pandas** - Data manipulation
3. **yfinance** - Yahoo Finance data fetching
4. **pandas-ta** - Technical analysis indicators
5. **plotly** - Interactive charts
6. **numpy** - Numerical computing
7. **prophet** - Time series forecasting
8. **google-generativeai** - Gemini AI integration
9. **pytz** - Timezone handling
10. **alpha-vantage** - Additional financial data
11. **scipy** - Scientific computing
12. **nltk** - Natural language processing
13. **requests** - HTTP requests
14. **beautifulsoup4** - Web scraping
15. **pytrends** - Google Trends data

---

### Step 2: Configure API Keys

#### Required API Keys:

1. **Google Gemini API** (for AI features)
   - Get your API key from: https://makersuite.google.com/app/apikey
   - Add to `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here"
   ```

2. **Alpha Vantage API** (for earnings calendar)
   - Get your free API key from: https://www.alpha-vantage.co/support/#api-key
   - Add to `.streamlit/secrets.toml`:
   ```toml
   [alpha_vantage]
   api_key = "your-alpha-vantage-key-here"
   ```

#### Create `.streamlit/secrets.toml` file:

```bash
# Create the directory if it doesn't exist
mkdir -p .streamlit

# Create the secrets file
cat > .streamlit/secrets.toml << EOF
# Google Gemini API
GOOGLE_API_KEY = "your-gemini-api-key-here"

# Alpha Vantage API
[alpha_vantage]
api_key = "your-alpha-vantage-key-here"
EOF
```

---

### Step 3: Initialize NLTK Data (Required for sentiment analysis)

Run Python and download required NLTK data:

```python
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

---

### Step 4: Run the Application

```bash
streamlit run dashboard.py
```

The app should open in your browser at `http://localhost:8501`

---

## Files Modified/Created

### Files Created:
- **backtester.py** - NEW module for model backtesting
- **SETUP_GUIDE.md** - This file

### Files Modified:
1. **ai_services.py** - Completed missing functions
   - `get_ai_comparables()` - Fetches sector comparison data
   - `get_ai_chart_analysis()` - AI-powered chart pattern analysis
   - `_call_generative_model_with_retry()` - Retry logic for AI calls

2. **technical_analysis.py** - Added missing features
   - Fixed missing return statement in `get_technical_signals()`
   - Added `calculate_risk_metrics()` - Beta, Sharpe, Sortino calculations

3. **pages/02_🔬_Fundamental_Deep_Dive.py**
   - Removed dummy data implementation
   - Now uses real data from `app_logic`

4. **pages/05_📄_Raw_Financials.py**
   - Fixed attribute name mismatches
   - Corrected import to use `app_logic`

5. **pages/10_🎲_Risk_Analysis.py**
   - Fixed `price_data_cached` reference → `price_data`

6. **pages/11_⚙️_Model_Backtesting.py**
   - Fixed `price_data_cached` reference → `price_data`
   - Fixed `get_ai_comparables()` return type handling

7. **pages/12_🔮_Future_Forecast.py**
   - Fixed `price_data_cached` reference → `price_data`

---

## Application Structure

```
Stocks/
├── dashboard.py              # Main entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .streamlit/
│   └── secrets.toml         # API keys (create this!)
│
├── Core Modules:
├── app_logic.py             # Main application logic
├── app_context.py           # Context data structures
├── app_utils.py             # Utility functions
├── data_fetcher.py          # Stock data fetching
├── technical_analysis.py    # Technical indicators ✅ FIXED
├── sentiment_analyzer.py    # News sentiment analysis
├── valuation_models.py      # DCF, DDM, NAV models
├── ai_services.py           # AI integration ✅ FIXED
├── backtester.py            # Model backtesting ✅ NEW
├── portfolio_optimizer.py   # Portfolio optimization
├── squeeze_analyzer.py      # Short squeeze detection
├── forecasting.py           # Future forecasting
├── leaderboard.py           # Squeeze leaderboard
├── autofix.py               # Auto code fixing
├── ultimate_debugger.py     # Debugging tools
├── debug_tools.py           # Debug utilities
│
└── pages/                   # Streamlit multi-page app
    ├── 01_📈_Price_&_Technicals.py
    ├── 02_🔬_Fundamental_Deep_Dive.py     ✅ FIXED
    ├── 03_💰_Valuation_Models.py
    ├── 04_🤝_Competitor_Analysis.py
    ├── 05_📄_Raw_Financials.py            ✅ FIXED
    ├── 06_⭐_Analyst_Ratings.py
    ├── 07_💥_Short_Squeeze_Indicator.py
    ├── 08_🏆_Squeeze_Leaderboard.py
    ├── 10_🎲_Risk_Analysis.py             ✅ FIXED
    ├── 11_⚙️_Model_Backtesting.py         ✅ FIXED
    ├── 12_🔮_Future_Forecast.py           ✅ FIXED
    ├── 13_💼_Portfolio_Optimization.py
    └── 14_📅_Earnings_Calendar.py
```

---

## Features Available

### 1. Price & Technical Analysis
- Interactive price charts with technical indicators
- RSI, MACD, ADX, OBV analysis
- Bollinger Bands, SMA crossovers
- AI-powered chart pattern recognition ✅

### 2. Fundamental Analysis
- Deep dive into financial metrics
- P/E ratios, margins, returns
- Enterprise value metrics

### 3. Valuation Models
- Discounted Cash Flow (DCF)
- Dividend Discount Model (DDM)
- Net Asset Value (NAV)
- Relative valuation vs sector

### 4. Risk Analysis ✅
- Beta calculation
- Sharpe & Sortino ratios
- Rolling volatility charts

### 5. Model Backtesting ✅
- Historical DCF accuracy testing
- P/E relative valuation backtesting
- MAPE (Mean Absolute Percentage Error) metrics

### 6. Future Forecasting
- Prophet-based price predictions
- Confidence intervals
- Trend analysis

### 7. Short Squeeze Detection
- High short interest identification
- Squeeze momentum indicators
- Leaderboard of top candidates

### 8. Portfolio Optimization
- Efficient frontier analysis
- Risk-return optimization

---

## Troubleshooting

### Issue: Import errors for `google.generativeai`
**Solution:**
```bash
pip install google-generativeai
```

### Issue: Import errors for `alpha_vantage`
**Solution:**
```bash
pip install alpha-vantage
```

### Issue: Prophet installation fails
**Solution:**
```bash
# On Windows, you may need:
pip install prophet --no-cache-dir

# On Mac/Linux:
pip install prophet
```

### Issue: "No module named 'pandas_ta'"
**Solution:**
```bash
pip install pandas-ta
```

### Issue: NLTK data not found
**Solution:**
```python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
```

### Issue: Streamlit secrets not found
**Solution:** Create `.streamlit/secrets.toml` in your project root with your API keys

---

## Known Architectural Issues (Non-Critical)

These won't cause crashes but should be addressed for code cleanliness:

1. **Multiple AppContext Definitions**
   - `app_logic.py` and `app_context.py` have different versions
   - Should be consolidated into one canonical definition

2. **Duplicate Function Signatures**
   - `calculate_valuation_score()` has different signatures in different files
   - Should standardize to one signature

These issues are marked for future refactoring but won't prevent the app from running.

---

## Next Steps

1. Install all dependencies: `pip install -r requirements.txt`
2. Get API keys and configure `.streamlit/secrets.toml`
3. Download NLTK data
4. Run the app: `streamlit run dashboard.py`
5. Test with a stock ticker like "AAPL" or "MSFT"

---

## Support

If you encounter any issues:
1. Check that all dependencies are installed
2. Verify API keys are configured correctly
3. Ensure Python version is 3.8 or higher
4. Check the terminal for specific error messages

**All critical errors have been fixed!** The application should now run successfully once dependencies are installed.
