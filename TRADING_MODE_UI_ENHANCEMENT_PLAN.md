# Trading Mode UI Enhancement Plan

**Date:** November 23, 2025
**Goal:** Create distinct visual themes and page layouts for Trader vs Investor modes

---

## Executive Summary

Transform the Trading Mode selector from a simple toggle into two distinct user interfaces with:
1. **Different color themes** (visual distinction)
2. **Mode-specific pages** (different nav structure)
3. **Tailored features** (show/hide based on mode)

---

## Proposed Color Themes

### Trader Mode 🔴 (Short-term, Active)
**Theme:** Energetic, action-oriented, real-time focus

**Color Palette:**
- **Primary:** `#FF6B35` (Orange-red) - Energy, urgency
- **Secondary:** `#004E89` (Deep blue) - Trust, stability
- **Accent:** `#00C9A7` (Teal green) - Profit, growth
- **Background:** `#F7F9FC` (Light gray-blue) - Clean, modern
- **Text:** `#1A1A2E` (Dark blue-black) - High contrast
- **Success:** `#26A69A` (Teal) - Bullish
- **Danger:** `#EF5350` (Red) - Bearish

**Visual Style:**
- Compact layouts (more data density)
- Smaller fonts for indicators
- Real-time update badges (🔴 LIVE)
- Candlestick charts (default)
- Intraday timeframes prominent
- Quick action buttons

### Investor Mode 🔵 (Long-term, Analytical)
**Theme:** Calm, analytical, research-oriented

**Color Palette:**
- **Primary:** `#3F51B5` (Indigo blue) - Wisdom, analysis
- **Secondary:** `#1565C0` (Blue) - Trust, stability
- **Accent:** `#43A047` (Green) - Long-term growth
- **Background:** `#FAFBFC` (Off-white) - Clean, readable
- **Text:** `#263238` (Blue-gray) - Comfortable reading
- **Success:** `#4CAF50` (Green) - Growth
- **Danger:** `#F44336` (Red) - Caution

**Visual Style:**
- Spacious layouts (more whitespace)
- Larger fonts for readability
- Emphasis on fundamentals
- Line/area charts (default)
- Long-term timeframes prominent
- Educational tooltips

---

## Page Assignment Recommendations

### 📊 Trader Mode Pages (Short-term Focus)

#### **1. Market Pulse Dashboard** (New/Redesigned)
**Current:** Part of Market Overview
**Recommendation:** Make this the Trader Mode homepage

**Features:**
- Real-time market indices (S&P 500, NASDAQ, DOW, VIX)
- Intraday charts (5min, 15min, 1hour)
- Put/Call ratio (current day)
- Sector rotation TODAY
- Top gainers/losers (intraday)
- Volume spikes
- Breaking news (last 1 hour)
- Economic calendar (today's events)

**Visual Style:**
- Compact widgets
- 🔴 LIVE badges on real-time data
- Quick-glance metrics (big numbers)
- Heatmaps for sector performance

---

#### **2. Intraday Charts & Scalping** (Redesigned Individual Charts)
**Current:** `pages/02_📈_Individual_Charts_&_Visuals.py`
**Recommendation:** Trader-specific version with intraday focus

**Features:**
- ✅ **Intraday timeframes** (1min, 5min, 15min, 30min, 1hour)
- ✅ **Level II data** (if available from Polygon API)
- ✅ **Volume profile** (current day)
- ✅ **Real-time indicators:** RSI, MACD, Stochastic (for entries/exits)
- ✅ **Support/resistance** (intraday levels)
- ✅ **Pattern recognition** (flags, pennants, breakouts)
- ✅ **Order flow analysis** (if data available)
- ❌ **Remove:** Long-term forecasts, fundamental overlays

**Default Settings:**
- Period: 1 day (today)
- Interval: 15 minutes
- Chart type: Candlestick
- Indicators: SMA(9, 21), RSI(14), Volume

---

#### **3. Technical Screener** (New Page)
**Recommendation:** Build new page for scanning opportunities

**Features:**
- **Pre-built scans:**
  - RSI oversold (<30)
  - RSI overbought (>70)
  - MA crossovers (50/200 SMA)
  - Bollinger Band squeezes
  - Volume breakouts (>2x average)
  - Gap up/down scanners
- **Custom scanner:** User-defined criteria
- **Results table:** Sortable, filterable
- **Quick charts:** Click to see intraday chart

**UI:**
- Compact table layout
- Color-coded signals (🟢 bullish, 🔴 bearish)
- "Scan Now" button for real-time results

---

#### **4. Options Flow** (Future - If budget allows)
**Status:** Not yet implemented
**Recommendation:** High value for traders, but requires premium data

**Features:**
- Unusual options activity
- Large block trades
- Put/Call flow
- Implied volatility changes

---

#### **5. News & Catalysts** (Trader Version)
**Current:** `pages/08_📰_News_&_Sentiment.py`
**Recommendation:** Trader-focused version emphasizing recency

**Features:**
- ✅ **Breaking news** (last 1 hour, 4 hours, today)
- ✅ **Earnings announcements** (today, this week)
- ✅ **Economic calendar** (upcoming events in next 24-48 hours)
- ✅ **Social sentiment spikes** (unusual Reddit/Twitter activity)
- ❌ **Remove:** Long historical sentiment trends, quarterly analysis

**Default Settings:**
- Time filter: Last 4 hours
- Sort by: Recency
- Show: Top 20 articles

---

### 📈 Investor Mode Pages (Long-term Focus)

#### **1. Market Overview & Economy** (Current Home)
**Current:** `pages/01_📊_Market_Overview_&_Economy.py`
**Recommendation:** Keep as Investor Mode homepage

**Features:**
- ✅ **Long-term market trends** (1 year, 5 year charts)
- ✅ **Economic indicators** (GDP, unemployment, inflation)
- ✅ **Sector rotation** (quarterly, annual)
- ✅ **Treasury yield curve**
- ✅ **Fed Funds rate trends**
- ✅ **Correlation factors** (Dollar, commodities)
- ❌ **Remove:** Intraday charts, minute-level data

**Default Settings:**
- Period: 1 year
- Interval: Daily
- Chart type: Line or Area
- Focus: Macro trends

---

#### **2. Fundamental Analysis** (Keep as-is)
**Current:** `pages/03_🔬_Fundamental_Analysis.py`
**Recommendation:** Perfect for Investor mode, hide from Trader mode

**Features:**
- ✅ **DCF Valuation**
- ✅ **DDM (Dividend Discount Model)**
- ✅ **Financial statements** (10 years historical)
- ✅ **Key metrics** (P/E, P/B, ROE, ROIC, debt ratios)
- ✅ **Scenario analysis**
- ✅ **Monte Carlo simulations**

**Visibility:**
- ✅ **Investor Mode:** Featured prominently (top nav)
- ❌ **Trader Mode:** Hide or move to "More" menu

---

#### **3. Competitive Analysis & Market Position**
**Current:** `pages/04_🤝_Competitive_&_Market.py` (placeholder)
**Recommendation:** Essential for Investor mode

**Features (When Built):**
- ✅ **Competitor comparison** (financial metrics)
- ✅ **Industry benchmarking**
- ✅ **Market share analysis**
- ✅ **Competitive advantages** (moat analysis)
- ✅ **Management quality**

**Visibility:**
- ✅ **Investor Mode:** Featured
- ❌ **Trader Mode:** Hide

---

#### **4. Risk & Long-term Forecasting**
**Current:** `pages/05_🎲_Risk_&_Forecasting.py`
**Recommendation:** Split into two versions

**Investor Version:**
- ✅ **Long-term forecasts** (Prophet, ARIMA for 1-3 years)
- ✅ **Risk metrics:** Beta, volatility, Sharpe ratio, max drawdown
- ✅ **Scenario analysis** (recession, bull market, etc.)
- ✅ **Monte Carlo simulations**
- ✅ **Correlation with portfolio** (if user has portfolio)

**Trader Version (Optional):**
- ✅ **Short-term volatility** (implied vol, ATR)
- ✅ **Intraday risk** (stop-loss calculator)
- ❌ **Remove:** Long-term forecasts

---

#### **5. Portfolio & Long-term Strategy**
**Current:** `pages/06_💼_Portfolio_&_Strategy.py`
**Recommendation:** Investor-focused, hide from Trader mode

**Features:**
- ✅ **Portfolio optimization** (Modern Portfolio Theory)
- ✅ **Asset allocation**
- ✅ **Rebalancing suggestions**
- ✅ **Dividend tracking**
- ✅ **Tax-loss harvesting** (future)
- ✅ **Retirement planning** (future)

**Visibility:**
- ✅ **Investor Mode:** Featured
- ❌ **Trader Mode:** Hide or minimal version

---

#### **6. Strategy Backtesting** (When Built)
**Recommendation:** Separate into Trader vs Investor strategies

**Investor Version:**
- DCF-based value investing
- Dividend growth strategies
- Buy-and-hold with rebalancing

**Trader Version:**
- RSI mean reversion
- MA crossovers
- Momentum strategies
- Breakout strategies

---

#### **7. Earnings & Estimates**
**Current:** `pages/09_📅_Earnings_&_Estimates.py`
**Recommendation:** Show in both modes, different emphasis

**Investor Version:**
- ✅ **Long-term earnings trends** (5-10 years)
- ✅ **Analyst estimates** (1-3 years forward)
- ✅ **Earnings quality analysis**
- ✅ **Growth sustainability**

**Trader Version:**
- ✅ **Upcoming earnings** (this week, this month)
- ✅ **Earnings surprises** (beat/miss history)
- ✅ **Post-earnings price moves**
- ✅ **Earnings calendar** (quick reference)

---

#### **8. News & Research** (Investor Version)
**Current:** `pages/08_📰_News_&_Sentiment.py`
**Recommendation:** Different emphasis from Trader version

**Features:**
- ✅ **In-depth articles** (Seeking Alpha, Bloomberg)
- ✅ **Quarterly reports** (10-Q, 10-K summaries)
- ✅ **Industry research**
- ✅ **Long-term sentiment trends** (quarterly, annual)
- ❌ **De-emphasize:** Breaking news, hourly updates

**Default Settings:**
- Time filter: Last 30 days
- Sort by: Relevance or quality
- Show: Top 50 articles

---

## Page Visibility Matrix

| Page | Trader Mode | Investor Mode | Notes |
|------|-------------|---------------|-------|
| **Market Pulse Dashboard** | ✅ **Homepage** | ❌ Hidden | Trader-specific |
| **Intraday Charts & Scalping** | ✅ Featured | ❌ Hidden/Minimal | Trader-specific |
| **Technical Screener** | ✅ Featured | ❌ Hidden | Trader-specific |
| **News & Catalysts (Short-term)** | ✅ Featured | ❌ Hidden | Trader-specific |
| **Market Overview & Economy** | ⚠️ Available | ✅ **Homepage** | Investor-focused |
| **Fundamental Analysis** | ❌ Hidden | ✅ Featured | Investor-only |
| **Competitive Analysis** | ❌ Hidden | ✅ Featured | Investor-only |
| **Risk & Forecasting (Long-term)** | ❌ Hidden | ✅ Featured | Investor-only |
| **Portfolio & Strategy** | ❌ Hidden | ✅ Featured | Investor-only |
| **Earnings & Estimates** | ⚠️ Different view | ⚠️ Different view | Both (different emphasis) |
| **News & Research (Long-term)** | ❌ Hidden | ✅ Featured | Investor-focused |
| **Debug Dashboard** | ✅ Available | ✅ Available | Both |

**Legend:**
- ✅ Featured = Shown in main navigation
- ⚠️ Available = Accessible but not prominent
- ❌ Hidden = Not shown in navigation (or minimal version)

---

## Implementation Plan

### Phase 1: Color Theme System (Week 1)

**File:** `mode_config.py` (extend existing)

```python
# Add to ModeConfig dataclass
@dataclass
class ModeConfig:
    # ... existing fields ...

    # New UI theme fields
    primary_color: str
    secondary_color: str
    accent_color: str
    success_color: str
    danger_color: str
    background_color: str
    text_color: str

TRADER_MODE = ModeConfig(
    # ... existing fields ...
    primary_color="#FF6B35",      # Orange-red
    secondary_color="#004E89",    # Deep blue
    accent_color="#00C9A7",       # Teal
    success_color="#26A69A",      # Teal green
    danger_color="#EF5350",       # Red
    background_color="#F7F9FC",   # Light blue-gray
    text_color="#1A1A2E"          # Dark blue-black
)

INVESTOR_MODE = ModeConfig(
    # ... existing fields ...
    primary_color="#3F51B5",      # Indigo
    secondary_color="#1565C0",    # Blue
    accent_color="#43A047",       # Green
    success_color="#4CAF50",      # Green
    danger_color="#F44336",       # Red
    background_color="#FAFBFC",   # Off-white
    text_color="#263238"          # Blue-gray
)

def get_mode_colors() -> dict:
    """Get current mode color palette"""
    mode_config = get_mode_config()
    return {
        'primary': mode_config.primary_color,
        'secondary': mode_config.secondary_color,
        'accent': mode_config.accent_color,
        'success': mode_config.success_color,
        'danger': mode_config.danger_color,
        'background': mode_config.background_color,
        'text': mode_config.text_color
    }
```

**File:** `global_sidebar.py` (inject CSS)

```python
def apply_mode_theme():
    """Inject CSS for mode-specific theming"""
    colors = get_mode_colors()
    mode = get_current_mode()

    # Trader mode: energetic, compact
    if mode == 'trader':
        css = f"""
        <style>
            /* Global theme */
            .stApp {{
                background-color: {colors['background']};
            }}

            /* Mode badge */
            .mode-badge {{
                background-color: {colors['primary']};
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 10px;
            }}

            /* Live indicator */
            .live-badge {{
                color: {colors['primary']};
                font-weight: bold;
                animation: pulse 2s infinite;
            }}

            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}

            /* Buttons */
            .stButton > button {{
                background-color: {colors['primary']};
                color: white;
                border-radius: 5px;
                font-weight: 600;
            }}

            /* Metrics */
            [data-testid="stMetricValue"] {{
                color: {colors['text']};
                font-size: 1.2rem;
            }}

            /* Success/Danger indicators */
            .metric-up {{
                color: {colors['success']} !important;
            }}

            .metric-down {{
                color: {colors['danger']} !important;
            }}
        </style>
        """

    # Investor mode: calm, spacious
    else:  # investor
        css = f"""
        <style>
            /* Global theme */
            .stApp {{
                background-color: {colors['background']};
            }}

            /* Mode badge */
            .mode-badge {{
                background-color: {colors['primary']};
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 15px;
            }}

            /* Buttons */
            .stButton > button {{
                background-color: {colors['primary']};
                color: white;
                border-radius: 8px;
                font-weight: 500;
                padding: 10px 20px;
            }}

            /* Metrics - larger for readability */
            [data-testid="stMetricValue"] {{
                color: {colors['text']};
                font-size: 1.5rem;
                font-weight: 500;
            }}

            /* Success/Danger indicators */
            .metric-up {{
                color: {colors['success']} !important;
            }}

            .metric-down {{
                color: {colors['danger']} !important;
            }}

            /* Spacious layout */
            .element-container {{
                margin-bottom: 1.5rem;
            }}
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)

# Call in global_sidebar
def render_sidebar():
    apply_mode_theme()  # ← Add this
    # ... rest of sidebar code ...
```

---

### Phase 2: Mode Badge & Visual Indicator (Week 1)

**Update:** `mode_config.py`

```python
def render_mode_banner():
    """Render prominent mode indicator with color theme"""
    mode = get_current_mode()
    colors = get_mode_colors()

    if mode == 'trader':
        badge_html = f"""
        <div class="mode-badge" style="background-color: {colors['primary']};">
            🔴 TRADER MODE <span class="live-badge">● LIVE</span>
        </div>
        <p style="color: {colors['text']}; font-size: 0.9rem; margin-top: 5px;">
            ⚡ Short-term focus • Real-time data • Intraday strategies
        </p>
        """
    else:
        badge_html = f"""
        <div class="mode-badge" style="background-color: {colors['primary']};">
            📈 INVESTOR MODE
        </div>
        <p style="color: {colors['text']}; font-size: 0.95rem; margin-top: 8px;">
            📊 Long-term focus • Fundamental analysis • Quality research
        </p>
        """

    st.markdown(badge_html, unsafe_allow_html=True)
```

---

### Phase 3: Conditional Page Navigation (Week 2)

**Update:** `global_sidebar.py`

```python
def filter_pages_by_mode(mode: str) -> list:
    """Return list of pages to show based on mode"""

    if mode == 'trader':
        return [
            {"name": "📊 Market Pulse", "file": "pages/01_Market_Pulse.py"},  # New
            {"name": "📈 Intraday Charts", "file": "pages/02_Intraday_Charts.py"},  # Redesigned
            {"name": "🔍 Technical Screener", "file": "pages/03_Screener.py"},  # New
            {"name": "📰 News & Catalysts", "file": "pages/08_News_Catalysts.py"},  # Filtered
            {"name": "📅 Earnings Calendar", "file": "pages/09_Earnings.py"},  # Upcoming only
            {"name": "🔧 Debug", "file": "pages/07_Debug.py"}
        ]
    else:  # investor
        return [
            {"name": "🌍 Market Overview", "file": "pages/01_Market_Overview.py"},  # Current
            {"name": "🔬 Fundamental Analysis", "file": "pages/03_Fundamental.py"},
            {"name": "🤝 Competitive Analysis", "file": "pages/04_Competitive.py"},
            {"name": "🎲 Risk & Forecasting", "file": "pages/05_Risk.py"},
            {"name": "💼 Portfolio & Strategy", "file": "pages/06_Portfolio.py"},
            {"name": "📰 News & Research", "file": "pages/08_News_Research.py"},
            {"name": "📅 Earnings & Estimates", "file": "pages/09_Earnings.py"},
            {"name": "🔧 Debug", "file": "pages/07_Debug.py"}
        ]

# In render_sidebar():
mode = get_current_mode()
pages = filter_pages_by_mode(mode)

st.sidebar.markdown("### 📄 Pages")
for page in pages:
    st.sidebar.page_link(page['file'], label=page['name'])
```

---

### Phase 4: Page-Level Customization (Weeks 2-3)

For each page, add mode-aware rendering:

**Example:** `pages/02_📈_Individual_Charts_&_Visuals.py`

```python
from mode_config import get_current_mode, render_mode_banner, get_mode_colors

def render_page():
    mode = get_current_mode()
    colors = get_mode_colors()

    render_mode_banner()

    if mode == 'trader':
        render_trader_charts()  # Intraday focus
    else:
        render_investor_charts()  # Long-term focus

def render_trader_charts():
    """Trader-specific charting"""
    st.markdown("## 📈 Intraday Charts & Technical Analysis")

    # Default to intraday timeframes
    period = st.selectbox("Period", ["1d", "5d"], index=0)
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "30m", "1h"], index=2)

    # Show only trader-relevant indicators
    indicators = st.multiselect(
        "Indicators",
        ["SMA(9,21)", "RSI", "MACD", "Stochastic", "Volume Profile"],
        default=["SMA(9,21)", "RSI"]
    )

    # Real-time badge
    st.markdown('<span class="live-badge">🔴 LIVE DATA</span>', unsafe_allow_html=True)

    # ... render chart ...

def render_investor_charts():
    """Investor-specific charting"""
    st.markdown("## 📊 Long-term Price Analysis")

    # Default to long-term timeframes
    period = st.selectbox("Period", ["1y", "3y", "5y", "10y"], index=0)
    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

    # Show investor-relevant indicators
    indicators = st.multiselect(
        "Indicators",
        ["SMA(50,200)", "Support/Resistance", "Trend Lines", "Moving Averages"],
        default=["SMA(50,200)"]
    )

    # ... render chart ...
```

---

## Timeline & Effort Estimate

### Week 1: Core Theme System
- [ ] Extend `mode_config.py` with color palettes
- [ ] Implement CSS injection in `global_sidebar.py`
- [ ] Update mode banner with colors and badges
- [ ] Test theme switching

**Effort:** 1-2 days

### Week 2: Page Navigation
- [ ] Implement `filter_pages_by_mode()` logic
- [ ] Hide Fundamental Analysis from Trader mode
- [ ] Hide Intraday Charts from Investor mode
- [ ] Test navigation switching

**Effort:** 1 day

### Week 3: Page Customization (High Priority)
- [ ] Customize Market Overview page (both modes)
- [ ] Create/customize Intraday Charts (Trader mode)
- [ ] Customize News page (both modes, different filters)
- [ ] Customize Earnings page (both modes)

**Effort:** 3-4 days

### Week 4: New Trader-Specific Pages (Optional)
- [ ] Build Market Pulse Dashboard (Trader homepage)
- [ ] Build Technical Screener
- [ ] Test all Trader mode flows

**Effort:** 5-7 days (can defer to post-MVP)

---

## Summary & Recommendation

### Immediate Actions (MVP-Ready)
1. ✅ **Add color themes** (1 day) - Easy, high visual impact
2. ✅ **Update mode banner** (2 hours) - Quick win
3. ✅ **Filter page navigation** (4 hours) - Clean UX
4. ⚠️ **Customize 2-3 key pages** (2 days) - Different defaults for Trader vs Investor

### Future Enhancements (Post-MVP)
1. ⏳ **Build Market Pulse Dashboard** (Trader homepage)
2. ⏳ **Build Technical Screener**
3. ⏳ **Separate News pages** (short-term vs long-term)

### Total Estimated Time
- **MVP-Ready (Weeks 1-2):** 3-4 days
- **Full Implementation (Weeks 1-4):** 10-14 days

---

## What Would You Like to Implement First?

**Option A:** Start with color themes and mode banner (quick visual win)
**Option B:** Start with page filtering (hide Fundamental Analysis from Trader mode)
**Option C:** Build new Trader-specific homepage (Market Pulse)
**Option D:** All of the above in sequence

Let me know which approach you prefer!

---

**Created:** November 23, 2025
**Status:** Ready for implementation
**Priority:** High (major UX improvement)
