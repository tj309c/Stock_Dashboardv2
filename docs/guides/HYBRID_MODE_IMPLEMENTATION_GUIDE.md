# Hybrid Trading Mode Implementation Guide

**Date:** November 23, 2025
**Status:** ✅ Core Infrastructure Complete - Ready for Gradual Rollout

---

## Executive Summary

This guide documents the implementation of a **Hybrid Trading Mode** system that optimizes the stock analysis platform for two distinct use cases:

1. **📊 Trader Mode** - Short-term trading with real-time data (1D-1M timeframes)
2. **📈 Investor Mode** - Long-term investing with fundamental analysis (3M-5Y timeframes)

### Key Benefits

- ✅ **Reduced API Calls** - Mode-specific cache TTLs prevent redundant fetching
- ✅ **Better Performance** - Load only relevant data for each mode
- ✅ **Improved UX** - Clear user intent reduces cognitive load
- ✅ **Cost Savings** - Optimized caching reduces API usage
- ✅ **Flexible** - Easy mode switching without losing session state

---

## Architecture Overview

### Core Components

```
mode_config.py          → Mode definitions and configuration
global_sidebar.py       → Mode toggle UI (updated)
data_fetcher.py         → Will be updated with mode-aware caching
pages/*.py              → Will be gradually updated to respect modes
```

### Mode Configuration Structure

Each mode defines:
- **Display Settings**: Name, icon, description, color
- **Data Settings**: Default period/interval, available timeframes
- **Cache Settings**: TTL for fast/medium/slow data
- **Feature Toggles**: Which features to show/hide
- **Performance Settings**: Chart limits, preloading behavior

---

## Implementation Details

### 1. Mode Configuration ([mode_config.py](mode_config.py))

**Status: ✅ Complete**

#### Trader Mode Settings
```python
default_period="5d"
default_interval="15m"
available_periods=["1d", "5d", "1mo", "3mo"]

cache_ttl_fast=60       # 1 min for prices
cache_ttl_medium=300    # 5 min for indicators
cache_ttl_slow=900      # 15 min for fundamentals

show_intraday_charts=True
show_fundamental_analysis=False  # Less relevant for traders
enable_quick_refresh=True
```

#### Investor Mode Settings
```python
default_period="1y"
default_interval="1d"
available_periods=["3mo", "6mo", "1y", "2y", "5y", "max"]

cache_ttl_fast=300      # 5 min for prices (less critical)
cache_ttl_medium=1800   # 30 min for indicators
cache_ttl_slow=3600     # 1 hour for fundamentals

show_intraday_charts=False
show_fundamental_analysis=True  # Critical for investors
enable_quick_refresh=False
```

#### Key Functions

```python
get_current_mode() → ModeConfig
    # Get active mode configuration

set_mode(mode: ModeType) → None
    # Switch modes (triggers cache clear and toast)

get_cache_ttl(data_type: str) → int
    # Get appropriate TTL for current mode
    # data_type: "fast", "medium", or "slow"

should_show_feature(feature: str) → bool
    # Check if feature should be shown
    # feature: "intraday_charts", "fundamental_analysis", etc.

get_default_timeframe() → Dict
    # Get default period/interval for mode

render_mode_info() → None
    # Display mode banner in pages
```

### 2. Global Sidebar Integration ([global_sidebar.py](global_sidebar.py))

**Status: ✅ Complete**

Added mode toggle at top of sidebar:

```python
# Two-button toggle
[📊 Trader] [📈 Investor]

# Shows current mode description
# Expandable details panel with:
# - Default timeframe
# - Cache strategy
# - Enabled features
# - Recommended pages
```

**Return Value Updated:**
```python
{
    'theme': str,
    'enable_ai_features': bool,
    'selected_ai_model': str or None,
    'trading_mode': str,           # NEW
    'mode_config': ModeConfig      # NEW
}
```

---

## Migration Strategy

### Phase 1: Core Infrastructure (✅ DONE)

- [x] Create `mode_config.py`
- [x] Update `global_sidebar.py`
- [x] Test mode switching

### Phase 2: Data Layer Updates (🔄 IN PROGRESS)

**Priority Files to Update:**

1. **`data_fetcher.py`** - Core data fetching
   ```python
   # BEFORE
   @st.cache_data(ttl=300)
   def fetch_stock_data(ticker, period="1mo"):
       ...

   # AFTER
   @st.cache_data(ttl=get_cache_ttl("fast"))
   def fetch_stock_data(ticker, period=None):
       if period is None:
           period = get_default_timeframe()["period"]
       ...
   ```

2. **`advanced_charting.py`** - Technical analysis
   ```python
   # Check if feature should be shown
   if should_show_feature("intraday_charts"):
       render_intraday_chart(...)
   ```

3. **`ticker_utils.py`** - Stock utilities
   ```python
   # Use mode-aware cache TTL
   @st.cache_data(ttl=get_cache_ttl("medium"))
   def get_stock_info(ticker):
       ...
   ```

### Phase 3: Page Updates (📋 TODO)

**Update pages to:**
1. Display mode indicator
2. Respect mode preferences
3. Use mode-appropriate defaults

**Example Implementation:**

```python
# At top of page
from mode_config import get_current_mode, render_mode_info, should_show_feature

# Show mode banner
render_mode_info()

# Get mode config
mode = get_current_mode()

# Use mode defaults
default_period = mode.default_period

# Conditional features
if should_show_feature("fundamental_analysis"):
    render_fundamental_tab()
```

**Pages to Update (Priority Order):**

1. **Market Overview & Economy** - Most impacted by mode
2. **Stock Analysis** - Core page, highest usage
3. **Portfolio & Strategy** - Investor-focused
4. **Fundamental Analysis** - Investor-focused
5. **Risk & Forecasting** - Both modes
6. **Competitive & Market** - Investor-focused
7. **Earnings & Estimates** - Both modes

### Phase 4: Testing & Refinement (📋 TODO)

- [ ] Test mode switching across all pages
- [ ] Verify cache TTLs working correctly
- [ ] Validate feature toggles
- [ ] Performance benchmarks
- [ ] User acceptance testing

---

## Usage Examples

### For Developers

#### Example 1: Mode-Aware Data Fetching

```python
from mode_config import get_cache_ttl, get_default_timeframe

# Old way (hardcoded)
@st.cache_data(ttl=300)
def fetch_data(ticker, period="1mo"):
    stock = yf.Ticker(ticker)
    return stock.history(period=period)

# New way (mode-aware)
@st.cache_data(ttl=get_cache_ttl("fast"))
def fetch_data(ticker, period=None):
    if period is None:
        period = get_default_timeframe()["period"]
    stock = yf.Ticker(ticker)
    return stock.history(period=period)
```

#### Example 2: Conditional Features

```python
from mode_config import should_show_feature

# Only show for Investor mode
if should_show_feature("fundamental_analysis"):
    st.markdown("### 📊 Fundamental Analysis")
    render_pe_ratio(ticker)
    render_earnings_growth(ticker)

# Only show for Trader mode
if should_show_feature("intraday_charts"):
    st.markdown("### ⏱️ Intraday Analysis")
    render_15min_chart(ticker)
```

#### Example 3: Mode-Specific UI

```python
from mode_config import get_current_mode, render_mode_info

# Show mode banner
render_mode_info()

# Get mode config
mode = get_current_mode()

# Customize UI based on mode
if mode.name == "Trader":
    st.info("💡 Trader Mode: Showing recent 5-day activity with 15-minute intervals")
    available_periods = ["1d", "5d", "1mo"]
else:
    st.info("💡 Investor Mode: Showing long-term trends with daily intervals")
    available_periods = ["3mo", "6mo", "1y", "5y"]

period = st.selectbox("Timeframe", available_periods)
```

### For Users

#### How to Switch Modes

1. Look for **🎯 Trading Mode** section in sidebar (top)
2. Click either:
   - **📊 Trader** - For short-term trading
   - **📈 Investor** - For long-term investing
3. Page will reload with mode-optimized settings

#### What Changes When You Switch?

**Trader Mode (📊):**
- Default timeframe: 5 days, 15-minute intervals
- Faster data updates (1-5 min cache)
- Shows intraday charts
- Hides long-term forecasts
- Emphasizes technical indicators

**Investor Mode (📈):**
- Default timeframe: 1 year, daily intervals
- Slower data updates (5-60 min cache)
- Shows fundamental analysis
- Shows long-term forecasts
- Emphasizes P/E ratios, earnings, etc.

---

## Testing Guide

### Manual Testing Checklist

#### Mode Switching
- [ ] Switch from Investor → Trader
- [ ] Verify toast notification appears
- [ ] Confirm mode indicator updates
- [ ] Switch from Trader → Investor
- [ ] Verify settings persist across page navigation

#### Data Fetching
- [ ] In Trader mode, data updates quickly (1-5 min)
- [ ] In Investor mode, data updates less frequently (5-60 min)
- [ ] Cache keys separate per mode (inspect Streamlit cache)

#### Feature Toggles
- [ ] Trader mode hides fundamental analysis
- [ ] Investor mode hides intraday charts
- [ ] Both modes show common features

#### Performance
- [ ] Page load time in Trader mode (should be fast)
- [ ] Page load time in Investor mode (should be fast)
- [ ] No redundant API calls when switching modes
- [ ] Cache hit rate improves over time

### Automated Testing

Create test file: `test_mode_switching.py`

```python
import pytest
from mode_config import get_current_mode, set_mode, get_cache_ttl

def test_mode_switching():
    # Test trader mode
    set_mode('trader')
    mode = get_current_mode()
    assert mode.name == "Trader"
    assert mode.default_period == "5d"
    assert get_cache_ttl("fast") == 60

    # Test investor mode
    set_mode('investor')
    mode = get_current_mode()
    assert mode.name == "Investor"
    assert mode.default_period == "1y"
    assert get_cache_ttl("fast") == 300

def test_feature_toggles():
    set_mode('trader')
    mode = get_current_mode()
    assert mode.show_intraday_charts == True
    assert mode.show_fundamental_analysis == False

    set_mode('investor')
    mode = get_current_mode()
    assert mode.show_intraday_charts == False
    assert mode.show_fundamental_analysis == True
```

---

## Performance Impact

### Expected Improvements

**Trader Mode:**
- **30-50% reduction in API calls** (aggressive caching)
- **Faster page loads** (less data to fetch)
- **Better responsiveness** (1-min cache for prices)

**Investor Mode:**
- **50-70% reduction in API calls** (conservative caching)
- **Lower API costs** (1-hour cache for fundamentals)
- **More stable data** (less flickering from updates)

### Monitoring

Track these metrics:
- API call count per mode
- Cache hit rate per mode
- Page load time per mode
- User session duration per mode

---

## Rollout Plan

### Week 1: Infrastructure
- [x] Create mode_config.py
- [x] Update global_sidebar.py
- [x] Test mode switching
- [x] Document architecture

### Week 2: Data Layer
- [ ] Update data_fetcher.py
- [ ] Update ticker_utils.py
- [ ] Update advanced_charting.py
- [ ] Test cache behavior

### Week 3: Page Updates
- [ ] Update Market Overview page
- [ ] Update Stock Analysis page
- [ ] Update Portfolio page
- [ ] Test feature toggles

### Week 4: Testing & Polish
- [ ] End-to-end testing
- [ ] Performance benchmarks
- [ ] User feedback
- [ ] Documentation updates

---

## Troubleshooting

### Common Issues

**Issue:** Mode not persisting across pages
**Solution:** Check `st.session_state.trading_mode` is set

**Issue:** Cache not clearing on mode switch
**Solution:** Verify `set_mode()` clears `mode_cached_data`

**Issue:** Features showing in wrong mode
**Solution:** Check `should_show_feature()` logic

**Issue:** API calls still high
**Solution:** Verify `get_cache_ttl()` is used in @st.cache_data decorators

---

## Future Enhancements

### Potential Additions

1. **Custom Modes**
   - Allow users to create custom mode profiles
   - Save mode preferences per ticker

2. **Auto Mode Detection**
   - Analyze user behavior to suggest mode
   - "Looks like you're day trading - switch to Trader mode?"

3. **Mode-Specific Layouts**
   - Trader mode: Single column, compact
   - Investor mode: Multi-column, detailed

4. **Performance Dashboard**
   - Show API call savings per mode
   - Cache hit rate visualization
   - Cost savings estimator

5. **Smart Prefetching**
   - Predict likely next action
   - Preload data in background

---

## API Reference

### mode_config.py

```python
# Core Functions
get_current_mode() → ModeConfig
set_mode(mode: ModeType) → None
get_cache_ttl(data_type: Literal["fast", "medium", "slow"]) → int
should_show_feature(feature: str) → bool
get_default_timeframe() → Dict[str, Any]
get_chart_config() → Dict[str, Any]
render_mode_info() → None
get_mode_badge() → str

# Classes
class ModeConfig:
    name: str
    icon: str
    description: str
    color: str
    default_period: str
    default_interval: str
    available_periods: list[str]
    cache_ttl_fast: int
    cache_ttl_medium: int
    cache_ttl_slow: int
    show_intraday_charts: bool
    show_advanced_technicals: bool
    show_fundamental_analysis: bool
    show_long_term_forecasts: bool
    enable_quick_refresh: bool
    recommended_pages: list[str]
    chart_data_points_limit: int
    preload_indicators: bool
    lazy_load_fundamentals: bool

# Constants
TRADER_MODE: ModeConfig
INVESTOR_MODE: ModeConfig
MODES: Dict[ModeType, ModeConfig]
```

---

## Conclusion

The Hybrid Trading Mode system provides a flexible, performant foundation for optimizing the platform for different user types. The core infrastructure is complete and ready for gradual rollout across pages.

**Next Steps:**
1. Update data fetching layer (data_fetcher.py)
2. Update 2-3 high-priority pages
3. Gather user feedback
4. Iterate and expand

**Success Metrics:**
- 30%+ reduction in API calls
- Improved user satisfaction scores
- Faster page load times
- Lower infrastructure costs

---

**Document Version:** 1.0
**Last Updated:** November 23, 2025
**Status:** Ready for Implementation
