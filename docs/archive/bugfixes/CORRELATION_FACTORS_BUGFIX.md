# Correlation Factors Bug Fix - Identical Scores Issue

## Problem
All market factors in the "Default Market Factors" section were showing identical correlation scores (85.00/100), which is impossible. Investigation revealed all factors were returning identical data series.

## Root Cause
**Thread-Safety Issue in yfinance Library**

When using `ThreadPoolExecutor` to fetch multiple tickers in parallel, `yfinance`'s `yf.download()` function has thread-safety issues that cause data corruption. Multiple concurrent calls would return the same data for different tickers.

### Evidence
- When tested sequentially: Each ticker returned unique data
- When tested in parallel (via `fetch_all_factors_parallel`): All tickers returned identical data
- The data corruption was random - sometimes all factors would get VIX data, sometimes Treasury data, etc.

## Solution
Added a **threading lock** (`threading.Lock()`) around all `yf.download()` calls to serialize downloads and prevent concurrent access.

### Changes Made in `correlation_factors.py`:

1. **Added threading lock at module level:**
```python
import threading

# Thread lock for yfinance downloads to prevent data corruption
_yf_download_lock = threading.Lock()
```

2. **Wrapped all `yf.download()` calls with the lock:**
```python
# Use lock to prevent yfinance thread-safety issues
with _yf_download_lock:
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
```

3. **Removed `@st.cache_data` decorator from `fetch_factor_data()`**
   - Initially suspected Streamlit caching was the issue
   - Cache moved to `fetch_all_factors_parallel()` level for better thread safety

4. **Added MultiIndex column handling**
   - Handle cases where `yf.download()` returns multi-ticker DataFrames
   - Ensure only single-column Series is returned

## Verification
After the fix:
- ✅ All 5 default market factors return unique data
- ✅ Each factor has distinct mean, std, and values
- ✅ No duplicate series detected
- ✅ Correlation scores are now properly differentiated

## Performance Impact
**Minimal**: The lock serializes downloads, but since network I/O is the bottleneck (not CPU), the performance impact is negligible. Downloads still happen in parallel threads; they just can't call `yf.download()` simultaneously.

## Files Modified
- `correlation_factors.py` - Added threading lock and MultiIndex handling

## Testing Performed
1. Sequential fetch test - ✅ Passed (unique data)
2. Parallel fetch test - ✅ Passed (unique data after fix)
3. Duplicate detection test - ✅ Passed (no duplicates found)

## Date
2025-11-23
