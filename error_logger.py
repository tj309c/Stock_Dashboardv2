"""
Centralized Error Logging Utility
Provides consistent error tracking across the Stock Analysis Dashboard
"""
import streamlit as st
from datetime import datetime
import traceback
import functools
from typing import Optional, Callable, Any


def init_error_log():
    """Initialize error log in session state if not present"""
    if 'error_log' not in st.session_state:
        st.session_state.error_log = []


def log_error(
    error: Exception,
    location: str,
    context: Optional[dict] = None,
    severity: str = "ERROR"
):
    """
    Log an error to the session state error log

    Args:
        error: The exception that was caught
        location: Where the error occurred (e.g., "data_fetcher.get_stock_price_data")
        context: Additional context information (e.g., {"ticker": "AAPL", "period": "1mo"})
        severity: Error severity level (ERROR, WARNING, CRITICAL)
    """
    init_error_log()

    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': type(error).__name__,
        'message': str(error),
        'location': location,
        'severity': severity,
        'context': context or {},
        'traceback': traceback.format_exc()
    }

    st.session_state.error_log.append(error_entry)

    # Keep only last 100 errors to prevent memory issues
    if len(st.session_state.error_log) > 100:
        st.session_state.error_log = st.session_state.error_log[-100:]


def log_warning(message: str, location: str, context: Optional[dict] = None):
    """
    Log a warning (not an exception)

    Args:
        message: Warning message
        location: Where the warning occurred
        context: Additional context information
    """
    init_error_log()

    warning_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'Warning',
        'message': message,
        'location': location,
        'severity': 'WARNING',
        'context': context or {},
        'traceback': None
    }

    st.session_state.error_log.append(warning_entry)


def log_info(message: str, location: str, context: Optional[dict] = None):
    """
    Log an informational message

    Args:
        message: Info message
        location: Where the info was logged
        context: Additional context information
    """
    init_error_log()

    info_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': 'Info',
        'message': message,
        'location': location,
        'severity': 'INFO',
        'context': context or {},
        'traceback': None
    }

    st.session_state.error_log.append(info_entry)


def with_error_logging(location: Optional[str] = None, show_error: bool = True):
    """
    Decorator to automatically log errors from functions

    Args:
        location: Custom location string (defaults to function name)
        show_error: Whether to display error in Streamlit UI

    Usage:
        @with_error_logging("data_fetcher.get_stock_price_data")
        def get_stock_price_data(ticker, period):
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_location = location or f"{func.__module__}.{func.__name__}"

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Extract context from args/kwargs
                context = {}
                if args:
                    context['args'] = str(args)[:200]  # Limit size
                if kwargs:
                    context['kwargs'] = str(kwargs)[:200]  # Limit size

                # Log the error
                log_error(e, func_location, context)

                # Optionally show in UI
                if show_error:
                    st.error(f"Error in {func_location}: {str(e)}")

                # Re-raise the exception so calling code can handle it
                raise

        return wrapper
    return decorator


def get_error_count(severity: Optional[str] = None) -> int:
    """
    Get count of logged errors

    Args:
        severity: Filter by severity (ERROR, WARNING, CRITICAL, INFO)

    Returns:
        Count of errors matching the severity filter
    """
    init_error_log()

    if severity:
        return sum(1 for e in st.session_state.error_log if e.get('severity') == severity)

    return len(st.session_state.error_log)


def get_recent_errors(limit: int = 10, severity: Optional[str] = None) -> list:
    """
    Get recent errors from the log

    Args:
        limit: Maximum number of errors to return
        severity: Filter by severity

    Returns:
        List of recent error entries
    """
    init_error_log()

    errors = st.session_state.error_log

    if severity:
        errors = [e for e in errors if e.get('severity') == severity]

    return errors[-limit:]


def clear_error_log():
    """Clear all logged errors"""
    init_error_log()
    st.session_state.error_log = []


def display_error_summary():
    """
    Display a summary of errors in the Streamlit UI
    Useful for showing error counts in a sidebar or footer
    """
    init_error_log()

    error_count = get_error_count('ERROR')
    warning_count = get_error_count('WARNING')
    critical_count = get_error_count('CRITICAL')

    if critical_count > 0:
        st.error(f"🔴 {critical_count} critical error(s)")

    if error_count > 0:
        st.warning(f"⚠️ {error_count} error(s)")

    if warning_count > 0:
        st.info(f"ℹ️ {warning_count} warning(s)")

    if critical_count == 0 and error_count == 0 and warning_count == 0:
        st.success("✅ No errors")


# Context manager for error logging
class ErrorLoggingContext:
    """
    Context manager for logging errors in a code block

    Usage:
        with ErrorLoggingContext("processing_ticker", {"ticker": "AAPL"}):
            # Your code here
            risky_operation()
    """

    def __init__(self, location: str, context: Optional[dict] = None, show_error: bool = True):
        self.location = location
        self.context = context
        self.show_error = show_error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log_error(exc_val, self.location, self.context)

            if self.show_error:
                st.error(f"Error in {self.location}: {str(exc_val)}")

            # Return False to propagate the exception
            return False


# Example usage functions
def example_with_decorator():
    """Example of using the decorator"""

    @with_error_logging("example.fetch_data")
    def fetch_data(ticker: str):
        if ticker == "INVALID":
            raise ValueError("Invalid ticker symbol")
        return f"Data for {ticker}"

    # This will automatically log errors
    try:
        result = fetch_data("AAPL")
        print(result)
    except ValueError:
        print("Error was logged automatically")


def example_with_context_manager():
    """Example of using the context manager"""

    ticker = "AAPL"

    with ErrorLoggingContext("example.process_ticker", {"ticker": ticker}):
        # Your risky code here
        if ticker == "INVALID":
            raise ValueError("Invalid ticker")
        print(f"Processing {ticker}")


def example_manual_logging():
    """Example of manual error logging"""

    try:
        ticker = "AAPL"
        # Some operation that might fail
        result = 1 / 0
    except Exception as e:
        log_error(e, "example.manual_operation", {"ticker": ticker})
        print("Error logged manually")
