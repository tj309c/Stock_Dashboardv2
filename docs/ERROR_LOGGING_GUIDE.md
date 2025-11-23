# Error Logging System Guide

## Overview

The Stock Analysis Dashboard now includes a **centralized error logging system** that tracks errors, warnings, and informational messages across all pages and modules. This system provides:

- 📊 **Real-time error tracking** in session state
- 🔍 **Detailed error information** with context and tracebacks
- 📈 **Error analytics** with filtering and severity levels
- 📥 **Export capabilities** to CSV for analysis
- 🎯 **Multiple integration methods** (decorator, context manager, manual)

## Quick Start

### Viewing Errors

1. Navigate to **🔧 Debug Dashboard** (Page 06)
2. Click the **"Logs & Errors"** tab
3. View error counts, filter by severity, and inspect details

### Logging Your First Error

```python
from error_logger import log_error, log_warning, log_info

try:
    result = risky_operation()
except Exception as e:
    log_error(e, "my_module.my_function", {"param": value})
```

---

## Core Functions

### `log_error(error, location, context=None, severity="ERROR")`

Log an exception with full details including traceback.

**Parameters:**
- `error` (Exception): The exception that was caught
- `location` (str): Where the error occurred (e.g., "data_fetcher.get_stock_price_data")
- `context` (dict, optional): Additional context information
- `severity` (str): "ERROR", "WARNING", "CRITICAL", or "INFO"

**Example:**
```python
from error_logger import log_error

try:
    ticker_data = fetch_ticker("INVALID_SYMBOL")
except Exception as e:
    log_error(
        e,
        "data_fetcher.fetch_ticker",
        {"ticker": "INVALID_SYMBOL", "retry_count": 3},
        "ERROR"
    )
```

---

### `log_warning(message, location, context=None)`

Log a warning message (not an exception).

**Example:**
```python
from error_logger import log_warning

if cache_size > 100_000_000:  # 100 MB
    log_warning(
        "Cache size exceeding recommended limit",
        "cache_manager.check_cache",
        {"cache_size_mb": cache_size / 1_000_000}
    )
```

---

### `log_info(message, location, context=None)`

Log an informational message for tracking important events.

**Example:**
```python
from error_logger import log_info

log_info(
    "Successfully fetched data for 50 tickers",
    "batch_fetcher.process_batch",
    {"ticker_count": 50, "duration_seconds": 12.5}
)
```

---

## Integration Methods

### Method 1: Decorator (Recommended for Functions)

The `@with_error_logging` decorator automatically catches and logs exceptions.

**Syntax:**
```python
from error_logger import with_error_logging

@with_error_logging("module_name.function_name", show_error=True)
def my_function(param1, param2):
    # Your code here
    return result
```

**Parameters:**
- `location` (str, optional): Custom location string (defaults to `module.function`)
- `show_error` (bool): Whether to display error in Streamlit UI (default: True)

**Full Example:**
```python
from error_logger import with_error_logging
import pandas as pd

@with_error_logging("data_processor.calculate_metrics")
def calculate_metrics(df: pd.DataFrame, ticker: str):
    """Calculate financial metrics from DataFrame"""
    if df.empty:
        raise ValueError(f"Empty DataFrame for ticker {ticker}")

    metrics = {
        'avg_close': df['Close'].mean(),
        'volatility': df['Close'].std(),
        'max_close': df['Close'].max()
    }
    return metrics

# Usage - errors are automatically logged!
try:
    metrics = calculate_metrics(stock_data, "AAPL")
except ValueError:
    st.error("Could not calculate metrics")
```

**Benefits:**
- ✅ Zero boilerplate in function body
- ✅ Automatic context extraction from args/kwargs
- ✅ Function names preserved with `@functools.wraps`
- ✅ Exceptions are re-raised for normal error handling

---

### Method 2: Context Manager (Recommended for Code Blocks)

The `ErrorLoggingContext` context manager logs errors in specific code blocks.

**Syntax:**
```python
from error_logger import ErrorLoggingContext

with ErrorLoggingContext("location", context={"key": "value"}, show_error=True):
    # Your risky code here
    risky_operation()
```

**Full Example:**
```python
from error_logger import ErrorLoggingContext
import yfinance as yf

ticker_symbol = "AAPL"

with ErrorLoggingContext(
    "fetch_and_process_ticker",
    context={"ticker": ticker_symbol, "source": "yfinance"},
    show_error=True
):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="1mo")

    if hist.empty:
        raise ValueError(f"No data returned for {ticker_symbol}")

    # Process data
    processed = process_historical_data(hist)
```

**Benefits:**
- ✅ Granular control over error logging
- ✅ Can wrap multiple operations
- ✅ Custom context per code block
- ✅ Clean separation of concerns

---

### Method 3: Manual Logging (Most Flexible)

Directly call logging functions for maximum control.

**Example:**
```python
from error_logger import log_error, log_warning
import requests

def fetch_external_api(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()

    except requests.Timeout as e:
        log_error(
            e,
            "api_client.fetch_external_api",
            {"url": url, "timeout": timeout},
            "ERROR"
        )
        return None

    except requests.HTTPError as e:
        if e.response.status_code == 429:  # Rate limit
            log_warning(
                "API rate limit exceeded",
                "api_client.fetch_external_api",
                {"url": url, "status_code": 429}
            )
        else:
            log_error(e, "api_client.fetch_external_api", {"url": url})
        return None
```

**Benefits:**
- ✅ Complete control over what gets logged
- ✅ Different handling for different exception types
- ✅ Custom severity levels per error
- ✅ Conditional logging based on error type

---

## Error Log Structure

Each logged error contains:

```python
{
    'timestamp': '2025-11-23T14:30:45.123456',
    'type': 'ValueError',
    'message': 'Invalid ticker symbol',
    'location': 'data_fetcher.get_stock_price_data',
    'severity': 'ERROR',  # CRITICAL, ERROR, WARNING, or INFO
    'context': {
        'ticker': 'INVALID',
        'period': '1mo',
        'user_input': True
    },
    'traceback': 'Traceback (most recent call last):\n  File ...'
}
```

---

## Viewing and Managing Errors

### Debug Dashboard (Web UI)

Navigate to **🔧 Debug Dashboard → Logs & Errors** tab:

#### Error Summary Metrics
- **Critical Count**: Number of CRITICAL severity errors
- **Error Count**: Number of ERROR severity errors
- **Warning Count**: Number of WARNING severity warnings
- **Info Count**: Number of INFO messages

#### Filtering
- **Filter by Severity**: All, CRITICAL, ERROR, WARNING, INFO
- **Show last N entries**: 5-100 entries

#### Error Details
Each error expands to show:
- Location (module.function)
- Error type (ValueError, KeyError, etc.)
- Timestamp (ISO format)
- Message
- Context (as JSON)
- Full traceback (if available)

#### Actions
- **🗑️ Clear Error Log**: Remove all logged errors
- **📥 Export Error Log**: Download as CSV file
- **🔄 Refresh**: Reload the error display

---

### Programmatic Access

```python
from error_logger import (
    get_error_count,
    get_recent_errors,
    clear_error_log,
    display_error_summary
)

# Get error counts
total_errors = get_error_count()
critical_only = get_error_count('CRITICAL')

# Get recent errors
last_10_errors = get_recent_errors(limit=10)
last_5_critical = get_recent_errors(limit=5, severity='CRITICAL')

# Display summary in any Streamlit page
display_error_summary()  # Shows metrics with colored indicators

# Clear all errors
clear_error_log()
```

---

## Best Practices

### 1. Use Descriptive Locations

❌ **Bad:**
```python
log_error(e, "function1", {})
```

✅ **Good:**
```python
log_error(e, "data_fetcher.get_stock_price_data", {"ticker": "AAPL"})
```

### 2. Provide Useful Context

❌ **Bad:**
```python
log_error(e, "process_data", {})
```

✅ **Good:**
```python
log_error(e, "process_data", {
    "ticker": ticker,
    "data_points": len(df),
    "date_range": f"{df.index[0]} to {df.index[-1]}",
    "user_initiated": True
})
```

### 3. Choose Appropriate Severity

- **CRITICAL**: System-breaking errors (API keys invalid, database down)
- **ERROR**: Operation failed but app continues (ticker not found, calculation failed)
- **WARNING**: Potential issues (high cache size, deprecated function)
- **INFO**: Important events (successful batch operation, cache cleared)

### 4. Don't Over-Log

❌ **Bad:**
```python
for ticker in tickers:
    log_info(f"Processing {ticker}", "loop", {"ticker": ticker})  # 100 log entries!
```

✅ **Good:**
```python
log_info(f"Starting batch process", "batch_processor", {"ticker_count": len(tickers)})
# Process all tickers
log_info(f"Batch complete", "batch_processor", {"success": success_count, "failed": fail_count})
```

### 5. Include Error Context in UI Messages

```python
@with_error_logging("fetch_data")
def fetch_stock_data(ticker):
    try:
        data = expensive_api_call(ticker)
        return data
    except Exception as e:
        st.error(f"❌ Failed to fetch data for {ticker}: {str(e)}")
        st.info("Check the Debug Dashboard → Logs & Errors for details")
        raise
```

---

## Real-World Examples

### Example 1: Data Fetcher with Retries

```python
from error_logger import ErrorLoggingContext, log_warning
import time

def fetch_with_retry(ticker, max_retries=3):
    """Fetch ticker data with automatic retries"""

    for attempt in range(max_retries):
        with ErrorLoggingContext(
            "data_fetcher.fetch_with_retry",
            context={
                "ticker": ticker,
                "attempt": attempt + 1,
                "max_retries": max_retries
            }
        ):
            data = yf.Ticker(ticker).history(period="1mo")

            if not data.empty:
                if attempt > 0:
                    log_warning(
                        f"Succeeded on retry {attempt + 1}",
                        "data_fetcher.fetch_with_retry",
                        {"ticker": ticker, "attempts": attempt + 1}
                    )
                return data

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

    raise ValueError(f"Failed to fetch data for {ticker} after {max_retries} attempts")
```

### Example 2: Portfolio Validator

```python
from error_logger import with_error_logging, log_warning

@with_error_logging("portfolio.validate_portfolio")
def validate_portfolio(tickers, weights):
    """Validate portfolio configuration"""

    if len(tickers) != len(weights):
        raise ValueError(f"Ticker count ({len(tickers)}) doesn't match weight count ({len(weights)})")

    total_weight = sum(weights)
    if abs(total_weight - 1.0) > 0.01:
        log_warning(
            f"Portfolio weights sum to {total_weight:.4f}, not 1.0",
            "portfolio.validate_portfolio",
            {"tickers": tickers, "weights": weights, "sum": total_weight}
        )

    # Check for duplicate tickers
    if len(tickers) != len(set(tickers)):
        duplicates = [t for t in tickers if tickers.count(t) > 1]
        raise ValueError(f"Duplicate tickers found: {duplicates}")

    return True
```

### Example 3: API Health Monitor

```python
from error_logger import log_error, log_info
import streamlit as st

def check_api_health(api_name, test_function):
    """Test API connectivity and log results"""

    try:
        result = test_function()

        if result:
            log_info(
                f"{api_name} API is healthy",
                "health_check.check_api_health",
                {"api": api_name, "status": "healthy"}
            )
            st.success(f"✅ {api_name} is working")
            return True
        else:
            log_warning(
                f"{api_name} API returned empty result",
                "health_check.check_api_health",
                {"api": api_name, "status": "empty_result"}
            )
            st.warning(f"⚠️ {api_name} returned no data")
            return False

    except Exception as e:
        log_error(
            e,
            "health_check.check_api_health",
            {"api": api_name, "status": "failed"},
            "CRITICAL"
        )
        st.error(f"❌ {api_name} failed: {str(e)}")
        return False
```

---

## Integration Checklist

When adding error logging to a new module:

- [ ] Import error logging functions at top of file
- [ ] Add `@with_error_logging` decorator to public functions
- [ ] Use `ErrorLoggingContext` for complex code blocks
- [ ] Add manual logging for edge cases with specific handling
- [ ] Include relevant context in all log calls
- [ ] Choose appropriate severity levels
- [ ] Test error logging with invalid inputs
- [ ] Check Debug Dashboard to verify logs appear correctly

---

## Performance Considerations

### Memory Management

The error log automatically limits to **100 most recent entries** to prevent memory issues. Older entries are automatically discarded.

### Cache Interaction

Error logging works with Streamlit's cache:
- Errors from cached functions are logged once per cache hit
- Use `st.cache_data.clear()` to reset error tracking for cached functions

### Session State

Errors are stored in `st.session_state.error_log`:
- Persists for the duration of the user session
- Cleared when user refreshes the page or session times out
- Can be manually cleared via Debug Dashboard

---

## Troubleshooting

### "Error log not appearing in Debug Dashboard"

1. Verify error logging is initialized:
   ```python
   from error_logger import init_error_log
   init_error_log()
   ```

2. Check that errors are actually being raised and caught

3. Try generating a test error from the Debug Dashboard

### "ImportError: cannot import name 'log_error'"

- Ensure `error_logger.py` is in the project root directory
- Check Python path includes the project directory

### "Errors logged multiple times"

- This can happen with Streamlit's rerun behavior
- Use caching strategically to prevent duplicate logging
- Check for errors in loops or frequently called functions

---

## Future Enhancements

Potential future additions to the error logging system:

- 📧 **Email notifications** for CRITICAL errors
- 📊 **Error analytics dashboard** with charts and trends
- 💾 **Persistent logging** to database or file
- 🔍 **Search and filtering** by location or message content
- 📱 **Slack/Discord integration** for real-time alerts
- 🎯 **Error grouping** by similarity
- 📈 **Performance impact tracking** (execution time when errors occur)

---

## Support

For issues or questions about the error logging system:

1. Check the **Debug Dashboard → Logs & Errors** tab
2. Review this documentation
3. Examine `error_logger.py` for implementation details
4. Test with the "Generate Test Error" buttons in Debug Dashboard

---

**Last Updated:** 2025-11-23
**Version:** 1.0
