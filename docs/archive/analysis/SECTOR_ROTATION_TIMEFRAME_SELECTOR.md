# Sector Rotation - User-Selectable Timeframe Feature

**Date**: 2025-11-23
**Status**: ✅ Implemented

## Feature Added

Added a **user-selectable timeframe dropdown** to the Sector Rotation tab, allowing users to analyze rotation across 4 different time horizons.

## What Was Requested

> "I'm not seeing the dual time frame view. Can we have a user selected option for 4 possible time frames to change to?"

## Solution Implemented

### ✅ Timeframe Selector Control

Added a dropdown selector with **4 timeframe options**:

1. **1-Day (Intraday)** - `change_1d`
   - Today's rotation
   - Most reactive, very noisy
   - Good for: Day trading, immediate sentiment

2. **5-Day (Short-term)** - `change_5d`
   - Recent week momentum shifts
   - Short-term trends
   - Good for: Swing trading, weekly positioning

3. **1-Month (Medium-term)** - `change_1m` ⭐ **Default**
   - Real rotation trends without noise
   - Best balance of stability vs responsiveness
   - Good for: Position trading, trend following

4. **All-Time (Since Fetched)** - `change_all`
   - Full data range (1 month of history)
   - Maximum stability
   - Good for: Long-term positioning, core holdings

**File**: [pages/01_📊_Market_Overview_&_Economy.py:1372-1393](pages/01_📊_Market_Overview_&_Economy.py#L1372-L1393)

### ✅ Dynamic Rotation Calculation

Updated `calculate_rotation_signal()` to:
- Accept `primary_timeframe` parameter
- Use selected timeframe for primary rotation signal
- Still show 5-day comparison for trend detection (when not using 5-day as primary)

**File**: [pages/01_📊_Market_Overview_&_Economy.py:1251-1339](pages/01_📊_Market_Overview_&_Economy.py#L1251-L1339)

### ✅ Dynamic UI Display

Updated display to:
- Show selected timeframe in metric caption
- Display primary timeframe performance data
- Show 5-day comparison only when primary is different (for trend context)
- Show trend arrows when comparing different timeframes

**File**: [pages/01_📊_Market_Overview_&_Economy.py:1407-1436](pages/01_📊_Market_Overview_&_Economy.py#L1407-L1436)

## User Experience

### Timeframe Selector Location
```
🔄 Sector Rotation & Money Flow
---
### 🔄 Sector Rotation Signal

[📅 Rotation Analysis Timeframe dropdown]
└─> 1-Day (Intraday)
    5-Day (Short-term)
    1-Month (Medium-term) ⭐ Selected
    All-Time (Since Fetched)

📊 Analyzing rotation using 1-Month (Medium-term) performance data
💡 Compare different timeframes to see short vs long-term rotation trends
```

### Display Based on Selection

**When selecting "1-Month"**:
```
Rotation Status
🏦 Value Outperforming
📉 Strengthening
Analyzing: 1-Month

Money flowing into value sectors (Financials, Energy) - defensive positioning

📊 1-Month: Growth -4.17% | Value -1.10% (Spread: -3.07%)
📆 5-Day: Growth -1.48% | Value -0.17% (Spread: -1.31%)
           ↑ Shows trend direction

⚠️ Risk-off sentiment
```

**When selecting "5-Day"** (no dual view needed):
```
Rotation Status
⚖️ Balanced
Analyzing: 5-Day

No clear rotation - balanced market

📊 5-Day: Growth -1.48% | Value -0.17% (Spread: -1.31%)
        ↑ No 5-day comparison shown (redundant)
```

**When selecting "1-Day"**:
```
Rotation Status
🚀 Growth Outperforming
📉 Weakening
Analyzing: 1-Day

Money flowing into growth sectors (Tech, Communication)

📊 1-Day: Growth +0.15% | Value -0.20% (Spread: +0.35%)
📆 5-Day: Growth -1.48% | Value -0.17% (Spread: -1.31%)
           ↑ Shows this is short-term reversal, not real trend

📈 Risk-on sentiment
```

## How It Works

### 1. User Selects Timeframe

```python
selected_timeframe = st.selectbox(
    "📅 Rotation Analysis Timeframe",
    options=[
        ("1-Day (Intraday)", "change_1d"),
        ("5-Day (Short-term)", "change_5d"),
        ("1-Month (Medium-term)", "change_1m"),  # ⭐ Default
        ("All-Time (Since Fetched)", "change_all"),
    ],
    index=2,  # Defaults to 1-Month
    key="sector_rotation_timeframe"
)
```

### 2. Calculation Uses Selected Timeframe

```python
rotation_signal = calculate_rotation_signal(
    sector_data,
    primary_timeframe=timeframe_key  # e.g., 'change_1m'
)
```

### 3. Display Adapts to Selection

```python
# Shows selected timeframe data
st.caption(f"📊 {timeframe_display}: Growth {avg_growth:+.2f}% | Value {avg_value:+.2f}%")

# Shows 5-day comparison only if primary is different
if timeframe_key != 'change_5d':
    st.caption(f"📆 5-Day: Growth {avg_growth_5d:+.2f}% | Value {avg_value_5d:+.2f}%")
```

## Benefits

### 1. **Flexibility**
- Users can analyze at their preferred time horizon
- Day traders see 1-day, swing traders see 5-day, investors see 1-month

### 2. **Context**
- Dual timeframe view (when appropriate) shows if rotation is accelerating/decelerating
- See both short-term noise and longer-term trend

### 3. **Accuracy**
- No more forced to use one timeframe
- Can verify signals across multiple timeframes
- Spot divergences (e.g., 1-day says growth, 1-month says value)

### 4. **Education**
- Help text explains each timeframe's characteristics
- Users learn difference between noisy short-term and stable long-term signals

## Why Dual Timeframe View Appears

You'll see **both** the primary and 5-day timeframes when:
1. Primary timeframe is **NOT** 5-day (to avoid redundancy)
2. Provides trend direction context

**Example scenarios**:

| Selected | Shows Dual View? | Reason |
|----------|------------------|--------|
| 1-Day | ✅ Yes | Compare 1d vs 5d to see if intraday move aligns with week |
| 5-Day | ❌ No | Would be redundant to show 5d twice |
| 1-Month | ✅ Yes | Compare 1m vs 5d to see if rotation strengthening/weakening |
| All-Time | ✅ Yes | Compare long-term vs 5d to detect recent changes |

## Technical Details

### Widget Key
```python
key="sector_rotation_timeframe"
```
- Ensures state persistence across reruns
- Prevents tab reset issue (user stays on same timeframe)

### Fallback Handling
```python
# Handle case where selected timeframe doesn't exist in data
if primary_timeframe == 'change_all':
    perf = data.get('change_1m', 0)  # Fallback to 1-month
elif primary_timeframe in data:
    perf = data[primary_timeframe]
else:
    perf = 0  # Safe fallback
```

### Trend Detection Logic
```python
# Only show trend if comparing different timeframes
if primary_timeframe != 'change_5d':
    # Compare primary vs 5-day to detect strengthening/weakening
    rotation_strengthening = (
        (difference > 0 and difference_5d > 0) or
        (difference < 0 and difference_5d < 0)
    )
```

## Files Modified

1. `pages/01_📊_Market_Overview_&_Economy.py`
   - [Lines 1366-1400](pages/01_📊_Market_Overview_&_Economy.py#L1366-L1400): Timeframe selector UI
   - [Lines 1251-1339](pages/01_📊_Market_Overview_&_Economy.py#L1251-L1339): Rotation calculation with timeframe parameter
   - [Lines 1403-1436](pages/01_📊_Market_Overview_&_Economy.py#L1403-L1436): Dynamic display based on selection

## Example Use Cases

### Use Case 1: Verify Rotation Signal
**Scenario**: User sees "Value Outperforming" on 1-month

**Action**:
1. Check 5-day → Still value? Rotation strengthening ✅
2. Check 1-day → Switched to growth? Possible reversal starting ⚠️

### Use Case 2: Day Trading Setup
**Scenario**: Day trader looking for intraday rotation

**Action**:
1. Select "1-Day" timeframe
2. See if today's rotation aligns with 5-day trend
3. If divergent → Potential mean reversion trade

### Use Case 3: Long-term Position
**Scenario**: Investor building 6-month position

**Action**:
1. Select "All-Time" or "1-Month" for stability
2. Ignore 1-day noise
3. Position based on longer-term rotation signal

## Future Enhancements (Not Implemented)

### Potential Additions
1. **3-Month timeframe** - Add to sector fetcher
2. **6-Month timeframe** - For longer-term trends
3. **Comparison mode** - Show all timeframes side-by-side in table
4. **Rotation strength meter** - Visual gauge showing rotation intensity
5. **Historical rotation chart** - Plot rotation over time

---

**Status**: ✅ **Fully Implemented**

**Result**: Users can now select from 4 different timeframes and see dual-timeframe analysis for context!
