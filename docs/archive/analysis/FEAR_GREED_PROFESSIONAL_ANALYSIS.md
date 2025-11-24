# Fear & Greed Index - Professional Analysis Suite

## Overview
A comprehensive, institutional-grade Fear & Greed Index analysis system with 3 tiers of professional features, inspired by how professional traders analyze market sentiment.

## 🎯 What Was Implemented

### **Core Infrastructure**
- **Historical Tracking System** ([fear_greed_history.py](fear_greed_history.py))
  - JSON-based persistence (stores last 90 days)
  - Automatic deduplication (prevents duplicate hourly entries)
  - Trend calculation with linear regression
  - Divergence detection algorithms
  - Percentile analysis

- **Professional Visualizations** ([fear_greed_visualizations.py](fear_greed_visualizations.py))
  - 9 specialized rendering functions
  - Plotly-based interactive charts
  - Color-coded sentiment indicators

---

## 📊 **TIER 1: Core Professional Analysis** (Must-Have)

### 1. Component Breakdown Chart
**What it shows:** Which specific indicators are driving the overall Fear & Greed score

**Features:**
- Horizontal bar chart showing each component's score (0-100)
- Color-coded by sentiment (red=fear, green=greed, yellow=neutral)
- Weight percentages displayed
- Highlights key drivers (fearful vs greedy components)
- Overall score reference line

**Professional Value:**
- Identifies whether fear/greed is broad-based or driven by specific factors
- Example: "VIX shows fear but breadth is strong" → Options market fear, not fundamental weakness

### 2. 7/30-Day Trend Analysis
**What it shows:** Historical Fear & Greed momentum and direction

**Features:**
- **7-Day Trend**: Short-term momentum with change in points
- **30-Day Trend**: Medium-term trend with regression slope
- **Historical Chart**: 30-day line chart with sentiment zones color-coded
- **Trend Direction**: Bullish, Bearish, or Neutral classification

**Professional Value:**
- Rate of change matters more than absolute level
- Accelerating fear = potential bottom; Decelerating greed = potential top
- Mean reversion signals for contrarian trades

### 3. Divergence Detection Alerts
**What it shows:** When individual components send conflicting signals

**Features:**
- **VIX vs Put/Call Divergence**: Low VIX but heavy put buying → Smart money hedging
- **Breadth vs Safe Haven Divergence**: Strong breadth but gold outperforming → Mixed signals
- **Credit vs Equity Divergence**: Stocks greedy but junk bonds fearful → Professional caution

**Professional Value:**
- Divergences often precede market reversals
- Credit market fear + equity greed = Warning sign (2007-2008 pattern)
- Identifies when retail sentiment differs from institutional

---

## 🎯 **TIER 2: Advanced Context** (High Value)

### 4. Historical Percentile Analysis
**What it shows:** How current score compares to recent history

**Features:**
- **30-Day Percentile**: Current score vs. last month
- **90-Day Percentile**: Current score vs. last quarter
- **Interpretation**: Automatic signals (unusually high/low vs normal range)
- **Trading Signals**: "Consider taking profits" or "Potential buy signal"

**Professional Value:**
- Context matters: Fear at 30 in a bull market ≠ Fear at 30 in a bear market
- Percentile > 90% or < 10% = Extreme conditions = Contrarian opportunity
- Helps time entries/exits based on historical extremes

### 5. Regime Context (Built into percentile)
**What it shows:** Historical pattern matching for forward-looking insights

**Features:**
- Tracks similar score occurrences in history
- Shows how often scores moved up/down from current level

**Professional Value:**
- "Last 5 times fear hit this level, market rallied 8% over next month"
- Pattern recognition for probabilistic forecasting

### 6. Sector Rotation Heatmap
**What it shows:** Defensive vs. Cyclical sector performance

**Features:**
- **Color-Coded Bar Chart**: Sector returns with red/green gradient
- **Category Classification**: Defensive, Cyclical, Sensitive
- **Rotation Signal**: Risk-on (cyclical leading) vs. Risk-off (defensive leading)

**Professional Value:**
- More valuable than index comparison (tells you WHERE money is flowing)
- Utilities/Staples outperforming → Hidden fear despite greed score
- Tech/Discretionary leading → True risk appetite

---

## 🌐 **TIER 3: Institutional Insights** (Nice to Have)

### 7. Cross-Asset Dashboard
**What it shows:** Sentiment across bonds, commodities, currencies

**Features:**
- **Asset Tracking**: 20Y Treasury (TLT), Gold (GLD), US Dollar (DXY), Oil (USO)
- **5-Day Performance**: Recent changes in safe havens and risk assets
- **Market Regime Detection**:
  - Flight to Safety: Gold + Bonds rising
  - Risk-On: Safe havens weak
  - Mixed Signals: Cross-asset divergence

**Professional Value:**
- Bonds + Gold rising with equity greed = False greed signal
- Dollar strength context (flight to safety vs. rate differentials)
- Commodity correlation (copper = economic health)

### 8. Options Flow Detail Breakdown
**What it shows:** Deep dive into Put/Call ratio with context

**Features:**
- **Put/Call Ratio Display**: Current ratio with 3-decimal precision
- **Sentiment Gauge**: Visual gauge chart (0-2 range)
- **Color-Coded Zones**:
  - < 0.7 = Extreme greed (call buying surge)
  - 0.7-0.9 = Greed
  - 0.9-1.1 = Neutral
  - 1.1-1.3 = Fear
  - > 1.3 = Extreme fear (heavy hedging)
- **Interpretation**: Explains what the ratio means

**Professional Value:**
- Put/Call > 1.3 historically marks bottoms (2020 March, 2022 October)
- Put/Call < 0.7 marks tops (2021 euphoria)
- Institutions buy puts when retail buys calls

---

## 📁 **File Structure**

```
Stocks/
├── fear_greed_history.py           # Historical data management & analytics
├── fear_greed_visualizations.py   # Professional visualization components
├── data/
│   └── fear_greed_history.json     # Persistent storage (auto-created)
└── pages/
    └── 01_📊_Market_Overview_&_Economy.py  # Main page with integrated features
```

---

## 🎨 **UI Organization**

The Fear & Greed section is now organized as:

1. **Main Score Display** (Always visible)
   - Large score display with emoji and category
   - Progress bar with interpretation
   - Analysis depth selector (Fast/Balanced)

2. **Tier 1 Expander** (Expanded by default)
   - Component Breakdown (left column)
   - Trend Analysis (right column)
   - Divergence Alerts (full width)

3. **Tier 2 Expander** (Collapsed by default)
   - Historical Percentile (left column)
   - Sector Rotation Heatmap (right column)

4. **Tier 3 Expander** (Collapsed by default)
   - Cross-Asset Dashboard (left column)
   - Options Flow Detail (right column)

---

## 🔄 **How It Works**

### Data Flow:
1. User selects analysis depth (Fast = 5 indicators, Balanced = 9 indicators)
2. Fear & Greed score calculated with component scores
3. **History Manager** automatically saves the reading (hourly deduplication)
4. All tiers analyze the data simultaneously:
   - Tier 1: Breaks down components, calculates trends, detects divergences
   - Tier 2: Computes percentiles, analyzes sectors
   - Tier 3: Fetches cross-asset data, displays options flow

### Historical Data:
- Stored in `data/fear_greed_history.json`
- Automatically cleaned (keeps 90 days)
- Builds up over time for better trend analysis
- First run: Limited historical context
- After 1 week: 7-day trend available
- After 1 month: Full percentile analysis

---

## 🚀 **Usage Tips**

### For Day Traders:
- Focus on **Tier 1**: Component breakdown + divergences
- Watch for divergence alerts (VIX vs Put/Call)
- Use 7-day trend for short-term momentum

### For Swing Traders:
- Use **Tier 1 + Tier 2**: Add percentile analysis
- Look for extremes (>90th or <10th percentile)
- Check sector rotation for confirmation

### For Position Traders:
- Use **All Tiers**: Full institutional analysis
- Cross-asset confirmation is critical
- Credit market divergence > equity sentiment
- 30-day trend + regime context for timing

---

## 📈 **Testing Status**

✅ All core features tested and working:
- [x] Historical tracking with persistence
- [x] Component breakdown visualization
- [x] 7/30-day trend analysis
- [x] Divergence detection (3 types)
- [x] Historical percentile calculation
- [x] Sector rotation heatmap
- [x] Cross-asset dashboard
- [x] Options flow detail gauge
- [x] Professional UI layout with expanders
- [x] Syntax validation passed
- [x] Integration test passed

---

## 🎓 **Professional Trading Insight**

This implementation answers the question: **"How do pros look deeper into Fear & Greed?"**

The answer: **They don't just look at the number—they decompose it, trend it, cross-reference it, and contextualize it.**

1. **Decomposition**: What's driving it? (Component breakdown)
2. **Trend**: Is it accelerating or decelerating? (7/30-day trends)
3. **Cross-Reference**: Do other markets agree? (Cross-asset, sectors)
4. **Context**: Is this normal or extreme? (Percentiles, regime analysis)
5. **Divergence**: Are smart money and retail aligned? (Divergence alerts)

**The most valuable insight:** Divergences and percentile extremes matter more than the absolute score.

---

## 🔮 **Future Enhancements** (Optional)

1. **Forward Returns Analysis**: Track actual S&P 500 returns following specific F&G levels
2. **Institutional vs Retail Split**: Separate sentiment indicators by participant type
3. **Real-time Options Flow**: Live tracking of unusual options activity
4. **Machine Learning**: Predict short-term market direction using F&G + components
5. **Alerts System**: Email/notification when extremes or divergences occur

---

## 📝 **Notes**

- Historical data builds over time—full functionality after 30+ days of usage
- Cross-asset data requires active market hours for real-time accuracy
- Divergence detection requires Level 2 (Balanced) with 9 indicators for best results
- Sector rotation uses existing sector data from the page

---

**Status:** ✅ Complete and tested
**Last Updated:** 2025-11-23
**Version:** 1.0.0
