# Mode-Aware User Notifications Guide

**Date:** November 23, 2025
**Purpose:** Guide for implementing user-friendly notifications when selections conflict with current mode

---

## Overview

The hybrid mode system now includes **intelligent user notifications** that inform users when their selections may not be optimal for their current mode (Trader vs Investor), and when those selections will trigger cache clearing/refreshing.

---

## Key Features

### 1. Automatic Mode Switch Notifications

When a user switches modes, they automatically see:
- ✅ Toast notification (top-right corner)
- ℹ️ Info box explaining what changed
- 🔄 Notification that cache was cleared

**Implementation:** No code needed - happens automatically in `set_mode()`

### 2. Selection Validation

Three new helper functions validate user selections:
- `validate_user_selection()` - Checks if selection is compatible with mode
- `notify_user_if_needed()` - Shows appropriate notification
- `get_mode_optimized_selection()` - One-line validation + notification

---

## Usage Examples

### Example 1: Simple Period Selection with Notification

```python
import streamlit as st
from mode_config import get_mode_optimized_selection

# User selects a period
user_period = st.selectbox(
    "Select Time Period",
    options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2  # Default to "1mo"
)

# Validate and notify user if needed
# This will show a notification if the period isn't optimal for current mode
period_to_use = get_mode_optimized_selection("period", user_period)

# Use the optimized period
st.write(f"Using period: {period_to_use}")
```

**What happens:**
- **Trader mode + selects "5y":** Shows warning that "5y" isn't optimized for Trader mode, recommends "5d"
- **Investor mode + selects "1d":** Shows warning that "1d" isn't optimized for Investor mode, recommends "1y"
- **Compatible selection:** Shows brief confirmation toast

### Example 2: Manual Validation with Custom Handling

```python
from mode_config import validate_user_selection, notify_user_if_needed

# User makes a selection
interval = st.selectbox(
    "Chart Interval",
    options=["1m", "5m", "15m", "1h", "1d", "1wk"]
)

# Validate selection
validation = validate_user_selection("interval", interval)

# Show notification
notify_user_if_needed(validation)

# Handle result based on validity
if validation["is_valid"]:
    # Use user's selection
    fetch_data(ticker, interval=interval)
else:
    # Offer to switch modes or use recommended value
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Use Recommended"):
            fetch_data(ticker, interval=validation["recommended_value"])

    with col2:
        if st.button("Switch Modes"):
            # Logic to switch to opposite mode
            pass
```

**What happens:**
- User gets clear notification about compatibility
- Can choose to use recommended value or switch modes
- Full control over user flow

### Example 3: Feature Availability Check

```python
from mode_config import validate_user_selection, should_show_feature

# Check if a feature should be shown
if should_show_feature("fundamental_analysis"):
    # Show fundamental analysis tab
    with st.expander("📊 Fundamental Analysis"):
        render_fundamental_analysis(ticker)
else:
    # Show message about why it's hidden
    validation = validate_user_selection("feature", "fundamental_analysis")

    if not validation["is_valid"]:
        st.info(
            f"{validation['message']}\n\n"
            f"**Tip:** {validation['recommended_value']} to access this feature.",
            icon="💡"
        )
```

**What happens:**
- **Trader mode:** Shows message explaining fundamental analysis is for Investor mode
- **Investor mode:** Shows fundamental analysis normally
- Clear guidance on how to access hidden features

### Example 4: Combining Defaults with User Selection

```python
from mode_config import get_current_mode, get_mode_optimized_selection

# Get current mode for context
mode = get_current_mode()

# Create selectbox with mode-specific defaults
user_period = st.selectbox(
    f"Time Period (Optimized for {mode.name} Mode)",
    options=mode.available_periods,  # Only show compatible periods
    index=mode.available_periods.index(mode.default_period)  # Default to mode default
)

# Optional: Still validate in case of programmatic changes
final_period = get_mode_optimized_selection("period", user_period)
```

**What happens:**
- Selectbox only shows periods compatible with current mode
- Default is automatically set to mode-appropriate value
- No warnings needed because all options are compatible
- **Best user experience** - prevents issues before they happen

---

## Notification Types

### 1. Toast Notification (✅)
**When:** Mode switch successful
**Location:** Top-right corner
**Duration:** 3-5 seconds
**Example:**
```
✅ Switched to Trader Mode 📊
🔄 Cache cleared - data will refresh with trader settings
```

### 2. Info Box (ℹ️)
**When:** Mode switch or selection needs explanation
**Location:** Main content area
**Persistent:** Yes (stays until page reload)
**Example:**
```
ℹ️ Mode Changed: 📊 Trader Mode Active

✓ Cache settings updated
✓ Default timeframes adjusted
✓ Page will reload with optimized settings

Your data will refresh automatically with trader-optimized cache times.
```

### 3. Warning Box (⚠️)
**When:** User selection conflicts with mode
**Location:** Main content area
**Persistent:** Yes
**Example:**
```
⚠️ Period '5y' not optimized for Trader Mode

The period you selected is outside the recommended range for Trader mode.
Your selection will work, but consider using 5d for optimal performance.

Available periods for Trader mode: 1d, 5d, 1mo, 3mo
```

---

## Best Practices

### 1. Prevent Issues Before They Happen

**Good:**
```python
mode = get_current_mode()
period = st.selectbox("Period", options=mode.available_periods)
```

**Why:** Only shows compatible options, no warnings needed

**Avoid:**
```python
period = st.selectbox("Period", options=["1d", "1mo", "1y", "5y"])  # All periods
# May show warnings for incompatible selections
```

### 2. Use Defaults Appropriately

**Good:**
```python
mode = get_current_mode()
period = st.selectbox(
    "Period",
    options=mode.available_periods,
    index=mode.available_periods.index(mode.default_period)
)
```

**Why:** Automatically sets mode-appropriate default

### 3. Combine Validation with Action

**Good:**
```python
validation = validate_user_selection("period", period)

if not validation["is_valid"]:
    notify_user_if_needed(validation)

    # Offer quick fix
    if st.button(f"Switch to {validation['recommended_value']}"):
        period = validation["recommended_value"]
        st.rerun()
```

**Why:** Gives user immediate action to fix the issue

### 4. Don't Over-Notify

**Good:**
```python
# Only show notification if selection is problematic
if user_period not in mode.available_periods:
    st.warning("This period isn't optimized for your current mode")
```

**Avoid:**
```python
# Don't spam users with notifications for every selection
st.info("You selected 1mo")
st.info("This is a valid period")
st.success("Your selection was successful")
```

---

## Function Reference

### `validate_user_selection(selection_type, selection_value)`

**Purpose:** Check if user's selection is compatible with current mode

**Parameters:**
- `selection_type`: "period", "interval", or "feature"
- `selection_value`: The value user selected

**Returns:**
```python
{
    "is_valid": bool,              # True if compatible
    "needs_cache_clear": bool,     # True if will clear cache
    "message": str,                # Notification message
    "recommended_value": Any       # Mode-appropriate alternative
}
```

**Example:**
```python
result = validate_user_selection("period", "5y")
# In Trader mode: {"is_valid": False, "needs_cache_clear": True, "message": "...", "recommended_value": "5d"}
# In Investor mode: {"is_valid": True, "needs_cache_clear": False, "message": "✓...", "recommended_value": "5y"}
```

### `notify_user_if_needed(validation_result, show_toast=True)`

**Purpose:** Display notification based on validation result

**Parameters:**
- `validation_result`: Result from `validate_user_selection()`
- `show_toast`: Whether to show toast notification (default: True)

**Example:**
```python
validation = validate_user_selection("period", period)
notify_user_if_needed(validation)
# Shows appropriate notification (warning, info, or toast)
```

### `get_mode_optimized_selection(selection_type, user_value=None)`

**Purpose:** One-line validation + notification + return optimal value

**Parameters:**
- `selection_type`: "period" or "interval"
- `user_value`: User's selected value (None = use mode default)

**Returns:** Mode-appropriate value (user's if valid, default if not)

**Example:**
```python
# Simple case - validate user selection
period = st.selectbox("Period", ["1d", "1mo", "1y"])
optimized_period = get_mode_optimized_selection("period", period)

# Use defaults
default_period = get_mode_optimized_selection("period")  # Returns mode.default_period
```

---

## Migration Guide

### Before (No Notifications)

```python
# Old code - no awareness of mode
period = st.selectbox("Period", ["1d", "1mo", "1y", "5y"])
data = fetch_data(ticker, period=period)
```

**Issues:**
- User doesn't know if selection is optimal
- No guidance on mode-appropriate choices
- Silent cache clearing on mode switch

### After (With Notifications)

```python
from mode_config import get_current_mode, get_mode_optimized_selection

mode = get_current_mode()

# Option 1: Restrict to compatible periods (best UX)
period = st.selectbox(
    f"Period (Optimized for {mode.name} Mode)",
    options=mode.available_periods,
    index=mode.available_periods.index(mode.default_period)
)

# Option 2: Allow all periods but notify
period = st.selectbox("Period", ["1d", "1mo", "1y", "5y"])
optimized_period = get_mode_optimized_selection("period", period)
data = fetch_data(ticker, period=optimized_period)
```

**Benefits:**
- User gets clear feedback
- Notifications explain cache behavior
- Recommendations guide better choices
- Mode switches are transparent

---

## Testing Notifications

### Manual Test Checklist

- [ ] Switch from Investor → Trader
  - [ ] Toast notification appears
  - [ ] Info box explains changes
  - [ ] Cache clear message shown

- [ ] Switch from Trader → Investor
  - [ ] Toast notification appears
  - [ ] Info box explains changes
  - [ ] Cache clear message shown

- [ ] Select incompatible period (Trader mode + "5y")
  - [ ] Warning shows
  - [ ] Recommended period shown
  - [ ] Available periods listed

- [ ] Select incompatible interval (Investor mode + "15m")
  - [ ] Info notification shows
  - [ ] Suggestion to switch modes
  - [ ] Explanation of why it's not optimal

- [ ] Select compatible values
  - [ ] Brief confirmation toast (optional)
  - [ ] No warnings
  - [ ] Data loads correctly

### Automated Testing

Create test file: `test_mode_notifications.py`

```python
from mode_config import validate_user_selection, set_mode
import streamlit as st

def test_period_validation():
    # Test Trader mode
    set_mode('trader')

    result = validate_user_selection("period", "5y")
    assert result["is_valid"] == False
    assert result["needs_cache_clear"] == True
    assert "not optimized" in result["message"]
    assert result["recommended_value"] == "5d"

    # Test Investor mode
    set_mode('investor')

    result = validate_user_selection("period", "5y")
    assert result["is_valid"] == True
    assert result["needs_cache_clear"] == False

    print("✅ Period validation tests passed")

def test_interval_validation():
    # Test Trader mode with daily interval
    set_mode('trader')

    result = validate_user_selection("interval", "1d")
    assert result["is_valid"] == True  # Still valid, just not optimal
    assert "better for Investor" in result["message"]

    # Test Investor mode with intraday interval
    set_mode('investor')

    result = validate_user_selection("interval", "15m")
    assert result["is_valid"] == True
    assert "better for Trader" in result["message"]

    print("✅ Interval validation tests passed")

if __name__ == "__main__":
    test_period_validation()
    test_interval_validation()
    print("\n✅ All notification tests passed!")
```

---

## Summary

The mode notification system ensures users:
1. **Understand** when they switch modes (what changes)
2. **Know** when cache will clear (data will refresh)
3. **Get** guidance on optimal selections for their mode
4. **Can** make informed decisions about switching modes

**Key Benefits:**
- ✅ Transparent mode switching
- ✅ Clear cache clearing notifications
- ✅ Helpful recommendations
- ✅ Prevents confusion
- ✅ Improves user experience

**Remember:** The goal is to **guide**, not **restrict**. Users can still make non-optimal selections, but they'll know why it might not be ideal for their current mode.

---

**Document Version:** 1.0
**Last Updated:** November 23, 2025
**Status:** Ready for Use
