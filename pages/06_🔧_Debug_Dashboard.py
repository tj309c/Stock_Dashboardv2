"""
Debug Dashboard - System diagnostics and monitoring
"""
import streamlit as st
import sys
import os
import platform
import psutil
from datetime import datetime
import pandas as pd
import yfinance as yf
import json
from pathlib import Path
from error_logger import (
    init_error_log, get_error_count, get_recent_errors,
    clear_error_log, display_error_summary
)

# Page config
st.set_page_config(page_title="Debug Dashboard", page_icon="🔧", layout="wide")
st.title("🔧 Debug Dashboard")
st.markdown("System diagnostics, API health checks, and performance monitoring")

# Create tabs for different debug sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 System Info",
    "🔌 API Status",
    "💾 Cache Management",
    "📝 Logs & Errors",
    "⚡ Performance"
])

# ========================================
# TAB 1: SYSTEM INFO
# ========================================
with tab1:
    st.header("System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Python Environment")

        # Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        st.metric("Python Version", python_version)

        # Platform info
        st.metric("Platform", platform.system())
        st.metric("Architecture", platform.machine())

        # Working directory
        st.text_input("Working Directory", os.getcwd(), disabled=True)

        st.subheader("Installed Packages")
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                df_packages = pd.DataFrame(packages)

                # Filter for key packages
                key_packages = ['streamlit', 'yfinance', 'pandas', 'numpy',
                               'plotly', 'prophet', 'yahooquery', 'pytrends']
                df_key = df_packages[df_packages['name'].isin(key_packages)]

                if not df_key.empty:
                    st.dataframe(df_key, use_container_width=True, hide_index=True)
                else:
                    st.warning("No key packages found")
            else:
                st.error("Failed to retrieve package list")
        except Exception as e:
            st.error(f"Error getting packages: {e}")

    with col2:
        st.subheader("System Resources")

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        st.metric("CPU Usage", f"{cpu_percent}%")

        # Memory
        memory = psutil.virtual_memory()
        st.metric("Memory Usage", f"{memory.percent}%",
                 help=f"Used: {memory.used / (1024**3):.1f} GB / Total: {memory.total / (1024**3):.1f} GB")

        # Disk
        disk = psutil.disk_usage('/')
        st.metric("Disk Usage", f"{disk.percent}%",
                 help=f"Used: {disk.used / (1024**3):.1f} GB / Total: {disk.total / (1024**3):.1f} GB")

        st.subheader("Streamlit Info")
        st.metric("Streamlit Version", st.__version__)

        # Session state size
        st.metric("Session State Keys", len(st.session_state))

        with st.expander("View Session State"):
            if st.session_state:
                for key, value in st.session_state.items():
                    value_str = str(value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    st.text(f"{key}: {value_str}")
            else:
                st.info("Session state is empty")

# ========================================
# TAB 2: API STATUS
# ========================================
with tab2:
    st.header("API Health Checks")

    st.info("Testing connections to external data sources...")

    # Test yfinance
    st.subheader("1. yfinance (Yahoo Finance)")
    with st.spinner("Testing yfinance..."):
        try:
            test_ticker = yf.Ticker("AAPL")
            test_data = test_ticker.history(period="1d")

            if not test_data.empty:
                st.success("✅ yfinance is working correctly")
                st.metric("Last Close Price (AAPL)", f"${test_data['Close'].iloc[-1]:.2f}")
                st.caption(f"Last updated: {test_data.index[-1]}")
            else:
                st.error("❌ yfinance returned empty data")
        except Exception as e:
            st.error(f"❌ yfinance error: {e}")

    # Test yahooquery
    st.subheader("2. yahooquery")
    with st.spinner("Testing yahooquery..."):
        try:
            from yahooquery import Ticker as YQTicker
            yq_ticker = YQTicker("AAPL")
            yq_info = yq_ticker.summary_detail

            if isinstance(yq_info, dict) and 'AAPL' in yq_info:
                st.success("✅ yahooquery is working correctly")
                if 'marketCap' in yq_info['AAPL']:
                    market_cap = yq_info['AAPL']['marketCap']
                    st.metric("Market Cap (AAPL)", f"${market_cap / 1e9:.1f}B")
            else:
                st.warning("⚠️ yahooquery returned unexpected format")
        except ImportError:
            st.warning("⚠️ yahooquery not installed (optional)")
        except Exception as e:
            st.error(f"❌ yahooquery error: {e}")

    # Test Google Gemini API
    st.subheader("3. Google Gemini AI")
    with st.spinner("Testing Gemini API..."):
        try:
            if 'GOOGLE_API_KEY' in st.secrets:
                import google.generativeai as genai

                genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
                model = genai.GenerativeModel('gemini-pro')

                # Simple test
                response = model.generate_content("Reply with just 'OK'")

                if response and response.text:
                    st.success("✅ Gemini API is working correctly")
                    st.caption(f"Response: {response.text}")
                else:
                    st.error("❌ Gemini API returned empty response")
            else:
                st.warning("⚠️ GOOGLE_API_KEY not configured in secrets.toml")
        except Exception as e:
            st.error(f"❌ Gemini API error: {e}")

    # Test Alpha Vantage (if configured)
    st.subheader("4. Alpha Vantage")
    with st.spinner("Testing Alpha Vantage..."):
        try:
            if 'alpha_vantage' in st.secrets and 'api_key' in st.secrets['alpha_vantage']:
                import requests

                api_key = st.secrets['alpha_vantage']['api_key']
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"

                response = requests.get(url, timeout=10)
                data = response.json()

                if 'Global Quote' in data and data['Global Quote']:
                    st.success("✅ Alpha Vantage API is working correctly")
                    quote = data['Global Quote']
                    if '05. price' in quote:
                        st.metric("Current Price (AAPL)", f"${float(quote['05. price']):.2f}")
                else:
                    st.error(f"❌ Alpha Vantage API error: {data.get('Note', 'Unknown error')}")
            else:
                st.warning("⚠️ Alpha Vantage API key not configured in secrets.toml")
        except Exception as e:
            st.error(f"❌ Alpha Vantage error: {e}")

    # Test pytrends (Google Trends)
    st.subheader("5. Google Trends (pytrends)")
    with st.spinner("Testing pytrends..."):
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload(['AAPL'], timeframe='now 7-d')
            trends_data = pytrends.interest_over_time()

            if not trends_data.empty:
                st.success("✅ Google Trends (pytrends) is working correctly")
                st.caption(f"Retrieved {len(trends_data)} data points")
            else:
                st.warning("⚠️ pytrends returned empty data")
        except ImportError:
            st.warning("⚠️ pytrends not installed (optional)")
        except Exception as e:
            st.error(f"❌ pytrends error: {e}")

# ========================================
# TAB 3: CACHE MANAGEMENT
# ========================================
with tab3:
    st.header("Cache Management")

    st.markdown("""
    Streamlit caches data to improve performance. Use these tools to manage cached data.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Cache Controls")

        if st.button("🗑️ Clear All Caches", type="primary"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("All caches cleared successfully!")
            st.rerun()

        if st.button("🔄 Clear Data Cache Only"):
            st.cache_data.clear()
            st.success("Data cache cleared!")
            st.rerun()

        if st.button("🔄 Clear Resource Cache Only"):
            st.cache_resource.clear()
            st.success("Resource cache cleared!")
            st.rerun()

    with col2:
        st.subheader("Cache Info")

        st.info("""
        **Data Cache**: Stores computed results (DataFrames, calculations)

        **Resource Cache**: Stores connections and expensive objects

        Clear caches if you're seeing stale data or experiencing memory issues.
        """)

    st.subheader("Streamlit Cache Directory")
    cache_dir = Path.home() / ".streamlit" / "cache"

    if cache_dir.exists():
        st.text_input("Cache Directory", str(cache_dir), disabled=True)

        # Get cache size
        try:
            total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            st.metric("Cache Size", f"{total_size / (1024**2):.2f} MB")
        except Exception as e:
            st.warning(f"Could not calculate cache size: {e}")
    else:
        st.info("No cache directory found")

# ========================================
# TAB 4: LOGS & ERRORS
# ========================================
with tab4:
    st.header("Logs & Error Tracking")

    # Initialize error log
    init_error_log()

    # Error summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        critical_count = get_error_count('CRITICAL')
        st.metric("Critical", critical_count, delta=None,
                 delta_color="inverse" if critical_count > 0 else "off")

    with col2:
        error_count = get_error_count('ERROR')
        st.metric("Errors", error_count, delta=None,
                 delta_color="inverse" if error_count > 0 else "off")

    with col3:
        warning_count = get_error_count('WARNING')
        st.metric("Warnings", warning_count, delta=None,
                 delta_color="inverse" if warning_count > 0 else "off")

    with col4:
        info_count = get_error_count('INFO')
        st.metric("Info", info_count)

    st.divider()

    # Filter controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All", "CRITICAL", "ERROR", "WARNING", "INFO"],
            index=0
        )

    with col2:
        limit = st.number_input("Show last N entries", min_value=5, max_value=100, value=20)

    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()

    st.subheader("Recent Session Errors")

    # Get filtered errors
    if severity_filter == "All":
        recent_errors = get_recent_errors(limit=limit)
    else:
        all_errors = st.session_state.error_log
        filtered = [e for e in all_errors if e.get('severity') == severity_filter]
        recent_errors = filtered[-limit:] if len(filtered) > limit else filtered

    if recent_errors:
        for idx, error in enumerate(reversed(recent_errors)):  # Show newest first
            severity = error.get('severity', 'ERROR')

            # Set color based on severity
            if severity == 'CRITICAL':
                icon = "🔴"
                severity_color = "red"
            elif severity == 'ERROR':
                icon = "🟠"
                severity_color = "orange"
            elif severity == 'WARNING':
                icon = "🟡"
                severity_color = "yellow"
            else:
                icon = "🔵"
                severity_color = "blue"

            timestamp = error.get('timestamp', 'N/A')
            error_type = error.get('type', 'Unknown')
            location = error.get('location', 'Unknown')

            with st.expander(f"{icon} [{severity}] {error_type} - {timestamp}"):
                st.markdown(f"**Location:** `{location}`")
                st.markdown(f"**Type:** {error_type}")
                st.markdown(f"**Time:** {timestamp}")

                # Show message
                st.markdown("**Message:**")
                st.code(error.get('message', 'No message'), language='python')

                # Show context if available
                context = error.get('context', {})
                if context:
                    st.markdown("**Context:**")
                    st.json(context)

                # Show traceback if available
                traceback_text = error.get('traceback')
                if traceback_text and traceback_text != 'NoneType: None\n':
                    with st.expander("View Full Traceback"):
                        st.code(traceback_text, language='python')
    else:
        st.success("✅ No errors recorded in this session")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Error Log", type="secondary"):
            clear_error_log()
            st.success("Error log cleared!")
            st.rerun()

    with col2:
        if st.button("📥 Export Error Log"):
            if st.session_state.error_log:
                df_errors = pd.DataFrame(st.session_state.error_log)
                csv = df_errors.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "error_log.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.info("No errors to export")

    st.divider()

    st.subheader("Test Error Logging")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Generate Test Error"):
            from error_logger import log_error
            try:
                raise ValueError("This is a test error for debugging purposes")
            except Exception as e:
                log_error(e, "Debug Dashboard - Test Error", {"test": True}, "ERROR")
                st.error(f"Test error logged: {e}")
                st.rerun()

    with col2:
        if st.button("Generate Test Warning"):
            from error_logger import log_warning
            log_warning("This is a test warning", "Debug Dashboard - Test Warning", {"test": True})
            st.warning("Test warning logged")
            st.rerun()

    with col3:
        if st.button("Generate Test Info"):
            from error_logger import log_info
            log_info("This is a test info message", "Debug Dashboard - Test Info", {"test": True})
            st.info("Test info logged")
            st.rerun()

    st.divider()

    st.subheader("Error Logging Integration")

    st.markdown("""
    ### How to Add Error Logging to Your Code

    **Method 1: Using the Decorator**
    ```python
    from error_logger import with_error_logging

    @with_error_logging("my_module.my_function")
    def my_function(ticker):
        # Your code here
        data = fetch_data(ticker)
        return data
    ```

    **Method 2: Using the Context Manager**
    ```python
    from error_logger import ErrorLoggingContext

    with ErrorLoggingContext("processing_data", {"ticker": "AAPL"}):
        # Your code here
        result = process_data()
    ```

    **Method 3: Manual Logging**
    ```python
    from error_logger import log_error, log_warning

    try:
        result = risky_operation()
    except Exception as e:
        log_error(e, "my_module.risky_operation", {"param": value})
        # Handle error
    ```
    """)

    st.subheader("Streamlit Debug Logs")
    st.info("""
    To view full Streamlit logs, run the application with:
    ```
    streamlit run Home.py --logger.level debug
    ```

    Or use `start-dev.bat` which enables debug logging automatically.
    """)

# ========================================
# TAB 5: PERFORMANCE
# ========================================
with tab5:
    st.header("Performance Metrics")

    st.subheader("Timing Tests")

    # Data fetching benchmark
    st.markdown("### Data Fetching Speed")

    if st.button("Run Data Fetch Benchmark"):
        import time

        with st.spinner("Running benchmarks..."):
            results = []

            # Test 1: Single ticker fetch
            start = time.time()
            try:
                ticker = yf.Ticker("AAPL")
                data = ticker.history(period="1mo")
                duration = time.time() - start
                results.append({
                    'Test': 'Single Ticker (1 month)',
                    'Duration (s)': f"{duration:.3f}",
                    'Status': '✅' if not data.empty else '❌'
                })
            except Exception as e:
                results.append({
                    'Test': 'Single Ticker (1 month)',
                    'Duration (s)': 'N/A',
                    'Status': f'❌ {str(e)[:30]}'
                })

            # Test 2: Company info fetch
            start = time.time()
            try:
                ticker = yf.Ticker("AAPL")
                info = ticker.info
                duration = time.time() - start
                results.append({
                    'Test': 'Company Info',
                    'Duration (s)': f"{duration:.3f}",
                    'Status': '✅' if info else '❌'
                })
            except Exception as e:
                results.append({
                    'Test': 'Company Info',
                    'Duration (s)': 'N/A',
                    'Status': f'❌ {str(e)[:30]}'
                })

            # Test 3: Multiple tickers
            start = time.time()
            try:
                tickers = ['AAPL', 'MSFT', 'GOOGL']
                for symbol in tickers:
                    ticker = yf.Ticker(symbol)
                    ticker.history(period="5d")
                duration = time.time() - start
                results.append({
                    'Test': '3 Tickers (5 days each)',
                    'Duration (s)': f"{duration:.3f}",
                    'Status': '✅'
                })
            except Exception as e:
                results.append({
                    'Test': '3 Tickers (5 days each)',
                    'Duration (s)': 'N/A',
                    'Status': f'❌ {str(e)[:30]}'
                })

            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, hide_index=True)

    st.subheader("Memory Usage Tracking")

    col1, col2, col3 = st.columns(3)

    with col1:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)
        st.metric("Current Process Memory", f"{memory_mb:.1f} MB")

    with col2:
        cpu_percent = process.cpu_percent(interval=0.1)
        st.metric("Current Process CPU", f"{cpu_percent:.1f}%")

    with col3:
        num_threads = process.num_threads()
        st.metric("Active Threads", num_threads)

    st.subheader("Page Load Performance")
    st.info("""
    To measure page load times:
    1. Open browser DevTools (F12)
    2. Go to Network tab
    3. Navigate to different pages
    4. Check the total load time in the Network tab

    Typical load times:
    - Fast: < 2 seconds
    - Normal: 2-5 seconds
    - Slow: > 5 seconds (may indicate caching issues)
    """)

# ========================================
# FOOTER
# ========================================
st.divider()
st.caption(f"Debug Dashboard · Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🔄 Refresh All Diagnostics"):
    st.rerun()
