# RetailAnalyst - Changelog

All notable changes, bug fixes, and feature additions to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### To Be Implemented (MVP Blockers)
- Technical strategy backtesting (RSI, MA crossovers, Bollinger Bands)
- Comprehensive risk analysis (VaR, CVaR, Sortino ratio)
- Competitor analysis module
- Sharpe ratio, max drawdown, win rate calculations

---

## [0.7.5] - 2025-11-23

### Added
- **Bug Fix Validation Tests** (`test_recent_fixes.py`)
  - Automated tests for Google API key configuration
  - Validation for Plotly annotation fix
  - AI model config dual key support verification

### Fixed
- **Google API Key Configuration** (Issue #1)
  - Added `GOOGLE_API_KEY` alias in `.streamlit/secrets.toml`
  - Code already supported both `GOOGLE_API_KEY` and `GEMINI_API_KEY`
  - Fixed "API key not found" errors when using Google AI

- **Plotly Annotation Font Error** (Issue #2)
  - Removed invalid `bgcolor` property from `annotation_font` in `visual_analysis_presets.py:1549`
  - Fixed "Invalid property specified for object of type plotly.graph_objs.layout.annotation.Font" error
  - Support/resistance chart now renders correctly

### Documentation
- Created `docs/BUSINESS_OVERVIEW.md` - Consolidated business plan, market analysis, roadmap
- Created `docs/DEVELOPER_GUIDE.md` - Comprehensive technical documentation
- Created `CHANGELOG.md` - This file

---

## [0.7.0] - 2025-11-23 (Phase 1: Hybrid Trading Mode)

### Added
- **Hybrid Trading Mode System** (`mode_config.py`)
  - Trader Mode: Short-term focused, fast data refresh (60s-900s cache TTLs)
  - Investor Mode: Long-term focused, slower refresh (300s-3600s cache TTLs)
  - Mode toggle in global sidebar with visual feedback
  - Mode-specific default timeframes and features

- **Mode-Aware Caching** (23 cache decorators updated)
  - `data_fetcher.py`: 10 functions updated
  - `advanced_charting.py`: 2 functions updated
  - `visual_analysis_presets.py`: 3 functions updated
  - `performance_optimizer.py`: 3 functions updated
  - `pages/01_📊_Market_Overview_&_Economy.py`: 5 functions updated

- **Advanced Market Visualizations** (`market_overview_advanced_visuals.py`)
  - Market Volume Profile
  - Market Strength Meter
  - Integration with Market Overview page

- **Mode Notification System** (`MODE_NOTIFICATIONS_GUIDE.md`)
  - User-facing mode descriptions
  - Recommended pages per mode
  - Feature availability indicators

### Changed
- **Global Sidebar** (`global_sidebar.py`)
  - Added Trader/Investor mode toggle buttons
  - Mode details expander with cache TTLs and features
  - Persistent mode across sessions

- **Market Overview Page** (`pages/01_📊_Market_Overview_&_Economy.py`)
  - Added mode info banner
  - Updated all cache decorators to use `get_cache_ttl()`

- **Individual Charts Page** (`pages/02_📈_Individual_Charts_&_Visuals.py`)
  - Added mode info banner
  - Ready for conditional feature rendering

### Fixed
- Put/Call Ratio calculation accuracy
- Sector rotation timeframe selector
- Tab reset issues when switching between pages
- Treasury yield curve data fetching
- Fear & Greed Index historical data
- Market Pulse accuracy improvements
- Sector heatmap display issues

### Testing
- Created `test_mode_switching_comprehensive.py` (8 tests, 100% pass)
- Created `test_individual_charts_mode_aware.py` (6 tests, 100% pass)
- Created `test_sector_rotation_timeframes.py`
- Created `test_advanced_visuals_accuracy.py`
- Created `test_market_pulse_accuracy.py`

### Performance
- Expected API call reduction: 30-40% (Trader), 50-70% (Investor)
- Improved page load times with optimized caching
- Reduced redundant API calls across mode switches

### Documentation
- `HYBRID_MODE_IMPLEMENTATION_GUIDE.md` - Developer guide for mode system
- `HYBRID_MODE_COMPLETE_SUMMARY.md` - Executive summary
- `PHASE_1_COMPLETION_REPORT.md` - Detailed completion report
- `MODE_NOTIFICATIONS_GUIDE.md` - User-facing mode documentation

---

## [0.6.0] - 2025-11-22 (News & Sentiment Dashboard)

### Added
- **News & Sentiment Page** (`pages/08_📰_News_&_Sentiment.py`)
  - Multi-source news aggregation (Finnhub, NewsAPI, yfinance)
  - AI-powered sentiment analysis (VADER, FinBERT, LLM-based)
  - Social sentiment tracking (Reddit mentions, Google Trends)
  - News timeline visualization
  - Sentiment distribution charts

- **Earnings & Estimates Page** (`pages/09_📅_Earnings_&_Estimates.py`)
  - Earnings calendar with analyst estimates
  - Historical earnings surprises
  - EPS estimate tracking
  - Earnings call transcripts (if available)

- **Enhanced AI Features** (`ai_services.py`, `ai_model_config.py`)
  - Multi-provider AI support (OpenAI, Anthropic, Google Gemini, xAI)
  - Automatic provider selection based on configured keys
  - Cost optimization (prefer cheaper models)
  - AI chart pattern analysis
  - AI competitor discovery

### Changed
- **Sentiment Analysis Enhancement** (`news_fetcher.py`)
  - Added FinBERT integration for financial text sentiment
  - Improved VADER sentiment scoring
  - LLM-based sentiment as fallback
  - Sentiment aggregation across multiple sources

### Documentation
- `SENTIMENT_ENHANCEMENTS_SUMMARY.md`
- `SENTIMENT_VISUAL_GUIDE.md`
- `GLOBAL_AI_CONFIGURATION.md`
- `GLOBAL_AI_UPDATE_SUMMARY.md`
- `AI_MODEL_CONFIGURATION_GUIDE.md`
- `AI_SETUP_QUICKSTART.md`

---

## [0.5.0] - 2025-11-21 (Market Overview Enhancements)

### Added
- **Fear & Greed Index** (`fear_greed_history.py`)
  - Historical Fear & Greed data fetching
  - Sentiment classification (Extreme Fear to Extreme Greed)
  - Trend analysis and visualizations

- **Correlation Factors Analysis** (`correlation_factors.py`)
  - VIX correlation with stock prices
  - Treasury yield impact analysis
  - Dollar strength correlation
  - Safe haven demand indicators

- **Advanced Economic Indicators**
  - Fed Funds Rate from FRED API
  - Treasury Yield Curve (2Y, 10Y, 30Y)
  - Put/Call Ratio
  - Advance/Decline Line
  - New Highs/Lows
  - Junk Bond Spread

### Fixed
- **Treasury Yield Curve** - Fixed data fetching from FRED API
- **Fed Funds Rate** - Clarified effective vs. target rate
- **Correlation Factors** - Fixed duplicate factor series bug
- **Market Pulse** - Improved accuracy of market sentiment calculation
- **Sector Heatmap** - Fixed display and data issues

### Testing
- `test_fed_funds_rate.py` - Validates FRED API integration
- `test_correlation_factors.py` - Tests factor calculations
- `test_market_pulse_accuracy.py` - Validates market sentiment
- `test_sector_rotation_accuracy.py` - Tests sector data

### Documentation
- `FEAR_GREED_PROFESSIONAL_ANALYSIS.md`
- `FED_FUNDS_RATE_CLARIFICATION.md`
- `CORRELATION_FACTORS_BUGFIX.md`
- `CORRELATING_FACTORS_SUMMARY.md`
- `TREASURY_YIELD_CURVE_FIX.md`
- `MARKET_PULSE_FIX_SUMMARY.md`
- `MARKET_PULSE_AUDIT.md`
- `SECTOR_HEATMAP_FIX.md`
- `SECTOR_ROTATION_FIX.md`

---

## [0.4.0] - 2025-11-20 (Advanced Charting & Technical Analysis)

### Added
- **50+ Technical Indicators** (`advanced_charting.py`)
  - Trend: SMA, EMA, MACD, ADX, Ichimoku Cloud
  - Momentum: RSI, Stochastic, CCI, ROC, Williams %R
  - Volatility: Bollinger Bands, ATR, Keltner Channels
  - Volume: OBV, MFI, VWAP, Volume Profile

- **Chart Pattern Recognition**
  - Head & Shoulders (bullish/bearish)
  - Double Top / Double Bottom
  - Triangle patterns (Ascending, Descending, Symmetrical)
  - Wedges (Rising, Falling)

- **Visual Analysis Presets** (`visual_analysis_presets.py`)
  - Multi-timeframe analysis (1min to 1mo)
  - Support/resistance level detection
  - Volume profile analysis
  - Market structure visualization
  - Trend confidence scoring

- **Advanced Visuals** (`market_overview_advanced_visuals.py`)
  - Sector rotation heatmaps
  - Market breadth indicators
  - Volume-weighted price analysis

### Changed
- **Individual Charts Page** - Complete overhaul with advanced features
- **Charting Engine** - Switched to Plotly for interactivity

### Testing
- `test_advanced_charting_enhancements.py`
- `test_individual_charts_visuals.py`
- `test_visual_analysis_accuracy.py`
- `test_advanced_visuals_accuracy.py`

### Documentation
- `ADVANCED_VISUAL_ANALYSIS_REPORT.md`
- `ADVANCED_VISUALS_VALIDATION.md`

---

## [0.3.0] - 2025-11-19 (Fundamental Analysis & Valuation)

### Added
- **DCF Valuation Model** (`valuation_models.py`)
  - Institutional-grade DCF calculator
  - WACC calculation
  - Free Cash Flow projection
  - Terminal value (Gordon Growth Model)
  - Margin fade and ROIC adjustments
  - Scenario analysis (Bear/Base/Bull)
  - Monte Carlo simulation

- **Dividend Discount Model (DDM)**
  - Gordon Growth Model implementation
  - Dividend sustainability checks
  - Yield-based valuation

- **Fundamental Analysis Page** (`pages/03_🔬_Fundamental_Analysis.py`)
  - Key metrics dashboard
  - Financial statement display (Income, Balance Sheet, Cash Flow)
  - Interactive DCF calculator with sliders
  - Sensitivity analysis
  - Valuation comparisons

- **Smart DCF Recommendations** (`DCF_SMART_RECOMMENDATIONS_GUIDE.md`)
  - Industry-specific default assumptions
  - Automated parameter suggestions
  - Risk-adjusted discount rates

### Testing
- `tests/test_valuation_accuracy.py` - Validates DCF calculations
- `tests/test_dividend_utils.py` - Tests DDM model

### Documentation
- `DCF_SMART_RECOMMENDATIONS_GUIDE.md`

---

## [0.2.0] - 2025-11-18 (Data Architecture & Performance)

### Added
- **Performance Optimizer** (`performance_optimizer.py`)
  - Batch ticker fetching
  - Data compression for large datasets
  - Intelligent caching strategies
  - Memory usage monitoring

- **Data Fetching Architecture** (`DATA_FETCHING_ARCHITECTURE.md`)
  - Multi-provider fallback system (yfinance → yahooquery → Alpha Vantage)
  - Rate limit handling with exponential backoff
  - Data validation and quality checks

- **Portfolio & Strategy Module** (`pages/06_💼_Portfolio_&_Strategy.py`)
  - Portfolio optimization (Modern Portfolio Theory)
  - Efficient frontier calculation
  - Valuation backtesting (DCF, P/E ratio)

- **Risk & Forecasting Module** (`pages/05_🎲_Risk_&_Forecasting.py`)
  - Basic risk metrics (beta, volatility, 52-week range)
  - ML forecasting integration (Prophet, ARIMA, GARCH)

### Changed
- **Data Fetcher** (`data_fetcher.py`)
  - Added yahooquery as secondary provider
  - Improved error handling and logging
  - Optimized cache TTLs

### Testing
- `tests/test_performance_optimizer_enhancements.py`
- `tests/test_fetch_all_factors_parallel.py`
- `tests/test_dividend_crosscheck.py`

### Documentation
- `DATA_FETCHING_ARCHITECTURE.md`
- `PERFORMANCE_TRACKING.md`

---

## [0.1.0] - 2025-11-17 (MVP Foundation)

### Added
- **Project Structure**
  - Multi-page Streamlit app architecture
  - Modular component design
  - Global sidebar configuration

- **Home Page** (`Home.py`)
  - Landing page with ticker search
  - Project overview

- **Market Overview Page** (`pages/01_📊_Market_Overview_&_Economy.py`)
  - Major market indices (S&P 500, NASDAQ, DOW)
  - Economic indicators (VIX, Put/Call ratio)
  - Sector performance

- **Stock Analysis Page** (`pages/02_📈_Individual_Charts_&_Visuals.py`)
  - Price charts (line, candlestick)
  - Basic technical indicators (SMA, volume)

- **Core Data Engine** (`data_fetcher.py`)
  - yfinance integration
  - Basic caching with Streamlit
  - Company info, price data, news fetching

- **Competitive Analysis Placeholder** (`pages/04_🤝_Competitive_&_Market.py`)
  - Short squeeze analysis
  - Placeholder for competitor comparison

- **Debug Dashboard** (`pages/07_🔧_Debug_Dashboard.py`)
  - API key validation
  - Cache monitoring
  - Error logging

### Security
- Added `.gitignore` for secrets management
- Created `.env.example` template
- Implemented detect-secrets baseline
- Security documentation (`.github/SECURITY_REMOVE_ENV.md`, `.github/ROTATE_COMPROMISED_KEYS.md`)

### Documentation
- `PROJECT_PLAN.md` - 6-week MVP roadmap
- `BUSINESS PLAN.md` - Business strategy and market analysis
- `MVP_COMPLETION_ANALYSIS.md` - Current progress assessment
- `docs/SETUP_GUIDE.md` - Installation and configuration
- `docs/README-STARTUP.md` - Quick start guide

---

## Version History Summary

| Version | Date | Major Features |
|---------|------|----------------|
| 0.7.5 | 2025-11-23 | Bug fixes (Google API, Plotly), Documentation consolidation |
| 0.7.0 | 2025-11-23 | Hybrid Trading Mode (Trader/Investor), Mode-aware caching |
| 0.6.0 | 2025-11-22 | News & Sentiment dashboard, Multi-provider AI integration |
| 0.5.0 | 2025-11-21 | Market indicators (Fear & Greed, Correlation Factors) |
| 0.4.0 | 2025-11-20 | Advanced charting (50+ indicators, pattern recognition) |
| 0.3.0 | 2025-11-19 | Fundamental analysis (DCF, DDM valuation models) |
| 0.2.0 | 2025-11-18 | Data architecture, Performance optimization |
| 0.1.0 | 2025-11-17 | MVP foundation (core pages, data engine) |

---

## Known Issues

### High Priority (MVP Blockers)
- ❌ Technical strategy backtesting (RSI, MA, BB) not implemented
- ❌ Comprehensive risk analysis is placeholder ("coming soon")
- ❌ Competitor analysis is placeholder ("coming soon")
- ❌ Missing Sharpe ratio, max drawdown, win rate metrics

### Medium Priority
- ⚠️ AI news summarization not in exact 3-bullet format (has sentiment summaries instead)
- ⚠️ Performance benchmarks not measured in production
- ⚠️ Mobile responsiveness needs improvement

### Low Priority
- Social media integration (Reddit API) has rate limits
- Some advanced ML models (GARCH) require additional dependencies
- International market support limited

---

## Roadmap

### Next Release (0.8.0) - MVP Completion
**Target: 2-3 weeks**

- [ ] Implement RSI backtesting strategy
- [ ] Implement MA crossover backtesting
- [ ] Implement Bollinger Band strategy
- [ ] Add Sharpe ratio, max drawdown, win rate calculations
- [ ] Complete risk analysis module (VaR, CVaR, Sortino)
- [ ] Complete competitor analysis module
- [ ] Production deployment to Streamlit Cloud
- [ ] Beta launch with 10-20 users

### Future Releases

**0.9.0 - Beta Improvements** (Month 2)
- User feedback integration
- Bug fixes from beta testing
- Performance optimization
- UI/UX refinements

**1.0.0 - Public Launch** (Month 3)
- Stripe payment integration
- User authentication system
- Free/Premium tier implementation
- Legal compliance (Terms, Privacy Policy)

**1.1.0 - Advanced Features** (Month 4-6)
- Portfolio tracker (user holdings)
- Alerts & notifications (email/SMS)
- Advanced ML forecasting
- Options analysis

**2.0.0 - Enterprise Features** (Year 2)
- API access for developers
- Social sentiment engine (Reddit, Twitter)
- Satellite imagery verification
- International market support

---

## Contributors

**Lead Developer:** [Your Name]

**Special Thanks:**
- Streamlit team for the amazing framework
- Open-source community for data libraries (yfinance, pandas, plotly)
- AI providers (OpenAI, Anthropic, Google) for LLM access

---

## License

[To be determined - likely MIT or Apache 2.0 for open-source components]

---

**Changelog Maintained By:** Development Team
**Last Updated:** 2025-11-23
**Format:** Keep a Changelog 1.0.0
