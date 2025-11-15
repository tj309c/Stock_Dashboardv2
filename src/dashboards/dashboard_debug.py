"""
Debug & Diagnostics Dashboard
Real-time monitoring and troubleshooting panel for Analysis Master.

Features:
- API Health Monitor: Check status of all external APIs
- Data Validator: Inspect DataFrames, flag missing/invalid data
- Model Inspector: DCF calculations, arbitrage logic step-by-step
- Cache Manager: View/clear Streamlit cache, inspect cache hits
- Live Log Viewer: Tail application logs in real-time
- Session State Inspector: View all st.session_state variables
- Performance Profiler: Identify slow functions, bottlenecks

Philosophy:
"You can't fix what you can't see."
This dashboard exposes the internal state of the application, making it
easy to diagnose issues without digging through logs or print statements.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sys
import traceback
from typing import Dict, List, Optional
import json

# Import all pipelines for health checks
try:
    from src.pipelines.get_economic_data import get_economic_data_pipeline
    ECONOMIC_AVAILABLE = True
except ImportError:
    ECONOMIC_AVAILABLE = False

try:
    from src.pipelines.get_political_data import get_political_data_pipeline
    POLITICAL_AVAILABLE = True
except ImportError:
    POLITICAL_AVAILABLE = False

try:
    from src.pipelines.get_market_data import get_market_data_pipeline
    MARKET_AVAILABLE = True
except ImportError:
    MARKET_AVAILABLE = False

try:
    from src.analysis.arbitrage_engine import get_crypto_arbitrage_scanner, get_statistical_arbitrage_scanner
    ARBITRAGE_AVAILABLE = True
except ImportError:
    ARBITRAGE_AVAILABLE = False

try:
    from src.analysis.predictive_models import get_claude_predictor
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# System Health Check
# =============================================================================

def show_system_health():
    """Comprehensive system health check and diagnostics."""
    st.header("🏥 System Health Check")
    st.markdown("Comprehensive diagnostics for dependencies, files, syntax, and environment.")
    
    if st.button("🔄 Run Full Diagnostic", use_container_width=True, type="primary"):
        run_full_system_diagnostic()
    
    st.markdown("---")
    
    # Quick status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        deps_ok = check_dependencies_quick()
        st.metric("Dependencies", "✅ OK" if deps_ok else "❌ Issues", delta=None)
    
    with col2:
        files_ok = check_files_quick()
        st.metric("File Integrity", "✅ OK" if files_ok else "❌ Issues", delta=None)
    
    with col3:
        import yfinance as yf
        try:
            yf.Ticker("AAPL").info.get("symbol")
            conn_ok = True
        except:
            conn_ok = False
        st.metric("API Connection", "✅ OK" if conn_ok else "❌ Issues", delta=None)
    
    with col4:
        from pathlib import Path
        data_ok = Path("data").exists()
        st.metric("Data Directories", "✅ OK" if data_ok else "❌ Issues", delta=None)


def check_dependencies_quick():
    """Quick dependency check."""
    try:
        import streamlit, pandas, numpy, plotly, yfinance, ta, scipy
        return True
    except ImportError:
        return False


def check_files_quick():
    """Quick file integrity check."""
    from pathlib import Path
    required = ["main.py", "data_fetcher.py", "analysis_engine.py", "requirements.txt"]
    return all(Path(f).exists() for f in required)


def run_full_system_diagnostic():
    """Run comprehensive system diagnostic."""
    st.markdown("### 🔍 Running Full Diagnostic...")
    
    progress = st.progress(0)
    status = st.empty()
    
    # 1. Check dependencies
    status.text("Checking dependencies...")
    progress.progress(14)
    deps_results = check_all_dependencies()
    
    # 2. Check file integrity
    status.text("Checking file integrity...")
    progress.progress(28)
    files_results = check_all_files()
    
    # 3. Check syntax
    status.text("Checking Python syntax...")
    progress.progress(42)
    syntax_results = check_all_syntax()
    
    # 4. Check imports
    status.text("Checking imports...")
    progress.progress(56)
    import_results = check_all_imports()
    
    # 5. Check environment
    status.text("Checking environment...")
    progress.progress(70)
    env_results = check_environment()
    
    # 6. Check data directories
    status.text("Checking data directories...")
    progress.progress(84)
    dir_results = check_data_directories()
    
    # 7. Check API connectivity
    status.text("Checking API connectivity...")
    progress.progress(100)
    api_results = check_api_connectivity()
    
    status.text("✅ Diagnostic complete!")
    
    # Display results
    st.markdown("---")
    st.markdown("### 📊 Diagnostic Results")
    
    all_results = {
        "Dependencies": deps_results,
        "File Integrity": files_results,
        "Python Syntax": syntax_results,
        "Imports": import_results,
        "Environment": env_results,
        "Data Directories": dir_results,
        "API Connectivity": api_results
    }
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    total_checks = sum(len(r["checks"]) for r in all_results.values())
    passed = sum(sum(1 for c in r["checks"] if c["status"] == "PASS") for r in all_results.values())
    failed = sum(sum(1 for c in r["checks"] if c["status"] == "FAIL") for r in all_results.values())
    
    with col1:
        st.metric("Total Checks", total_checks)
    with col2:
        st.metric("✅ Passed", passed)
    with col3:
        st.metric("❌ Failed", failed)
    
    # Detailed results
    for category, results in all_results.items():
        with st.expander(f"{'✅' if results['passed'] else '❌'} {category} ({len([c for c in results['checks'] if c['status'] == 'PASS'])}/{len(results['checks'])} passed)", expanded=not results['passed']):
            for check in results["checks"]:
                if check["status"] == "PASS":
                    st.success(f"✅ {check['name']}")
                elif check["status"] == "FAIL":
                    st.error(f"❌ {check['name']}: {check.get('error', 'Failed')}")
                    if check.get("fix"):
                        st.code(check["fix"], language="bash")
                else:
                    st.warning(f"⚠️ {check['name']}: {check.get('warning', '')}")


def check_all_dependencies():
    """Check all required dependencies."""
    required = {
        'streamlit': 'Web framework',
        'pandas': 'Data analysis',
        'numpy': 'Numerical computing',
        'plotly': 'Visualization',
        'yfinance': 'Market data',
        'ta': 'Technical analysis',
        'scipy': 'Scientific computing',
        'beautifulsoup4': 'Web scraping',
        'requests': 'HTTP requests',
    }
    
    checks = []
    for package, desc in required.items():
        try:
            if package == 'beautifulsoup4':
                import bs4
            else:
                __import__(package)
            checks.append({"name": f"{package} ({desc})", "status": "PASS"})
        except ImportError:
            checks.append({
                "name": f"{package} ({desc})",
                "status": "FAIL",
                "error": "Not installed",
                "fix": f"pip install {package}"
            })
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def check_all_files():
    """Check all required files."""
    from pathlib import Path
    required = [
        'main.py', 'data_fetcher.py', 'analysis_engine.py', 'utils.py',
        'dashboard_selector.py', 'dashboard_stocks.py', 'dashboard_options.py',
        'dashboard_crypto.py', 'requirements.txt', 'README.md'
    ]
    
    checks = []
    for file in required:
        path = Path(file)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read(1)
                checks.append({"name": file, "status": "PASS"})
            except Exception as e:
                checks.append({"name": file, "status": "FAIL", "error": f"Cannot read: {str(e)}"})
        else:
            checks.append({"name": file, "status": "FAIL", "error": "File not found"})
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def check_all_syntax():
    """Check Python syntax for all files."""
    from pathlib import Path
    python_files = [p for p in Path('.').glob('*.py') if not p.name.startswith('.')]
    
    checks = []
    for file in python_files[:20]:  # Limit to first 20 files
        try:
            with open(file, 'r', encoding='utf-8') as f:
                compile(f.read(), file.name, 'exec')
            checks.append({"name": file.name, "status": "PASS"})
        except SyntaxError as e:
            checks.append({
                "name": file.name,
                "status": "FAIL",
                "error": f"Line {e.lineno}: {e.msg}"
            })
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def check_all_imports():
    """Check if critical imports work."""
    import_tests = [
        ('data_fetcher', 'MarketDataFetcher'),
        ('analysis_engine', 'ValuationEngine'),
        ('utils', 'format_currency'),
    ]
    
    checks = []
    for module, attr in import_tests:
        try:
            mod = __import__(module)
            getattr(mod, attr)
            checks.append({"name": f"{module}.{attr}", "status": "PASS"})
        except Exception as e:
            checks.append({"name": f"{module}.{attr}", "status": "FAIL", "error": str(e)[:100]})
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def check_environment():
    """Check environment variables."""
    import os
    env_vars = ['GEMINI_API_KEY', 'REDDIT_CLIENT_ID', 'NEWS_API_KEY']
    
    checks = []
    for var in env_vars:
        if os.getenv(var):
            checks.append({"name": var, "status": "PASS"})
        else:
            checks.append({
                "name": var,
                "status": "WARN",
                "warning": "Not set (optional - some features limited)"
            })
    
    return {"checks": checks, "passed": True}  # All optional


def check_data_directories():
    """Check data directories."""
    from pathlib import Path
    dirs = ['data', 'data/cache']
    
    checks = []
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            # Check writable
            test_file = path / '.test_write'
            try:
                test_file.touch()
                test_file.unlink()
                checks.append({"name": dir_path, "status": "PASS"})
            except Exception as e:
                checks.append({"name": dir_path, "status": "FAIL", "error": f"Not writable: {str(e)}"})
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                checks.append({"name": dir_path, "status": "PASS"})
            except Exception as e:
                checks.append({
                    "name": dir_path,
                    "status": "FAIL",
                    "error": f"Cannot create: {str(e)}",
                    "fix": f"mkdir {dir_path}"
                })
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def check_api_connectivity():
    """Check API connectivity."""
    checks = []
    
    # Test yfinance
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        if info and 'symbol' in info:
            checks.append({"name": "Yahoo Finance (yfinance)", "status": "PASS"})
        else:
            checks.append({"name": "Yahoo Finance (yfinance)", "status": "FAIL", "error": "No data returned"})
    except Exception as e:
        checks.append({"name": "Yahoo Finance (yfinance)", "status": "FAIL", "error": str(e)[:100]})
    
    return {"checks": checks, "passed": all(c["status"] == "PASS" for c in checks)}


def show_debug_dashboard():
    """
    Main debug dashboard interface.
    """
    st.title("🔧 Debug & Diagnostics Panel")
    st.caption("Internal monitoring and troubleshooting tools")
    
    # Sidebar navigation
    debug_section = st.sidebar.selectbox(
        "Debug Section",
        ["System Health", "API Health Monitor", "Data Validator", "Model Inspector", 
         "Cache Manager", "Live Logs", "Session State", "Performance Profiler"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** Use this panel to diagnose issues before reporting bugs.")
    
    # Route to appropriate section
    if debug_section == "System Health":
        show_system_health()
    elif debug_section == "API Health Monitor":
        show_api_health_monitor()
    elif debug_section == "Data Validator":
        show_data_validator()
    elif debug_section == "Model Inspector":
        show_model_inspector()
    elif debug_section == "Cache Manager":
        show_cache_manager()
    elif debug_section == "Live Logs":
        show_live_logs()
    elif debug_section == "Session State":
        show_session_state()
    elif debug_section == "Performance Profiler":
        show_performance_profiler()


# =============================================================================
# API Health Monitor
# =============================================================================

def show_api_health_monitor():
    """Check status of all external APIs."""
    st.header("🌐 API Health Monitor")
    st.markdown("Real-time status of all data sources and external services.")
    
    # Refresh button
    if st.button("🔄 Refresh All", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Check each API
    api_status = []
    
    # 1. FRED API (Economic Data)
    st.subheader("1. Federal Reserve Economic Data (FRED)")
    fred_status = check_fred_api()
    api_status.append(fred_status)
    display_api_status(fred_status)
    
    # 2. EIA API (Energy Data)
    st.subheader("2. Energy Information Administration (EIA)")
    eia_status = check_eia_api()
    api_status.append(eia_status)
    display_api_status(eia_status)
    
    # 3. Finnhub API (Insider Trades)
    st.subheader("3. Finnhub (Insider Transactions)")
    finnhub_status = check_finnhub_api()
    api_status.append(finnhub_status)
    display_api_status(finnhub_status)
    
    # 4. Alpha Vantage (Fundamentals)
    st.subheader("4. Alpha Vantage (Fundamental Data)")
    av_status = check_alpha_vantage_api()
    api_status.append(av_status)
    display_api_status(av_status)
    
    # 5. Anthropic Claude (LLM)
    st.subheader("5. Anthropic Claude (Predictions)")
    claude_status = check_claude_api()
    api_status.append(claude_status)
    display_api_status(claude_status)
    
    # 6. ccxt (Crypto Exchanges)
    st.subheader("6. CCXT (Crypto Exchange Data)")
    ccxt_status = check_ccxt_connectivity()
    api_status.append(ccxt_status)
    display_api_status(ccxt_status)
    
    # 7. yfinance (Stock Data)
    st.subheader("7. Yahoo Finance (Stock Prices)")
    yf_status = check_yfinance_api()
    api_status.append(yf_status)
    display_api_status(yf_status)
    
    # 8. News API (Sentiment Data)
    st.subheader("8. News API (News Sentiment)")
    news_status = check_news_api()
    api_status.append(news_status)
    display_api_status(news_status)
    
    # 9. Reddit API (Social Sentiment)
    st.subheader("9. Reddit API (WSB/Social Data)")
    reddit_status = check_reddit_api()
    api_status.append(reddit_status)
    display_api_status(reddit_status)
    
    # Overall summary
    st.markdown("---")
    healthy_count = sum(1 for status in api_status if status['status'] == 'healthy')
    total_count = len(api_status)
    
    if healthy_count == total_count:
        st.success(f"✅ All {total_count} APIs are operational!")
    elif healthy_count > total_count / 2:
        st.warning(f"⚠️ {healthy_count}/{total_count} APIs operational. Some features may be limited.")
    else:
        st.error(f"🔴 Only {healthy_count}/{total_count} APIs operational. Check API keys.")
    
    # Export report
    if st.button("📥 Export Health Report"):
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_apis': total_count,
                'healthy': healthy_count,
                'unhealthy': total_count - healthy_count
            },
            'api_status': api_status
        }
        st.download_button(
            "💾 Download JSON Report",
            data=json.dumps(report, indent=2),
            file_name=f"api_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def display_api_status(status: Dict):
    """Display API status in consistent format."""
    if status['status'] == 'healthy':
        st.success(f"✅ **Status:** {status['message']}")
    elif status['status'] == 'warning':
        st.warning(f"⚠️ **Status:** {status['message']}")
    else:
        st.error(f"🔴 **Status:** {status['message']}")
    
    if status.get('latency'):
        st.caption(f"⏱️ Latency: {status['latency']:.2f}ms")
    
    if status.get('details'):
        with st.expander("View Details"):
            st.json(status['details'])


def check_fred_api() -> Dict:
    """Test FRED API connectivity."""
    try:
        import time
        start = time.time()
        
        if ECONOMIC_AVAILABLE:
            pipeline = get_economic_data_pipeline()
            # Try to fetch inflation data as test
            data = pipeline.get_inflation_data()
            latency = (time.time() - start) * 1000
            
            if data is not None and len(data) > 0:
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'rows': len(data), 'latest_date': str(data.index[-1])}
                }
        
        return {
            'status': 'error',
            'message': 'Pipeline not available or API key not configured',
            'details': {'module_available': ECONOMIC_AVAILABLE}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_eia_api() -> Dict:
    """Test EIA API connectivity."""
    try:
        import time
        start = time.time()
        
        if ECONOMIC_AVAILABLE:
            pipeline = get_economic_data_pipeline()
            data = pipeline.get_crude_oil_prices()
            latency = (time.time() - start) * 1000
            
            if data is not None and len(data) > 0:
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'rows': len(data), 'latest_value': float(data['value'].iloc[-1])}
                }
        
        return {
            'status': 'warning',
            'message': 'API key not configured or module not available',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_finnhub_api() -> Dict:
    """Test Finnhub API connectivity."""
    try:
        import time
        start = time.time()
        
        if POLITICAL_AVAILABLE:
            pipeline = get_political_data_pipeline()
            data = pipeline.get_insider_transactions('AAPL', months=1)
            latency = (time.time() - start) * 1000
            
            if data is not None and len(data) > 0:
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'transactions_fetched': len(data)}
                }
        
        return {
            'status': 'warning',
            'message': 'API key not configured',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_alpha_vantage_api() -> Dict:
    """Test Alpha Vantage API connectivity."""
    try:
        import time
        start = time.time()
        
        if MARKET_AVAILABLE:
            pipeline = get_market_data_pipeline()
            data = pipeline.get_company_overview('AAPL')
            latency = (time.time() - start) * 1000
            
            if data:
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'fields_returned': len(data)}
                }
        
        return {
            'status': 'warning',
            'message': 'API key not configured',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_claude_api() -> Dict:
    """Test Claude API connectivity."""
    try:
        if LLM_AVAILABLE:
            predictor = get_claude_predictor()
            if predictor.client:
                return {
                    'status': 'healthy',
                    'message': 'API key configured successfully',
                    'details': {'model': 'claude-sonnet-4-20250514'}
                }
        
        return {
            'status': 'warning',
            'message': 'API key not configured. Add ANTHROPIC_API_KEY to secrets.toml',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_ccxt_connectivity() -> Dict:
    """Test ccxt exchange connectivity."""
    try:
        import time
        start = time.time()
        
        if ARBITRAGE_AVAILABLE:
            scanner = get_crypto_arbitrage_scanner()
            # Test by fetching BTC/USDT from Binance
            if 'binance' in scanner.exchange_instances:
                exchange = scanner.exchange_instances['binance']
                ticker = exchange.fetch_ticker('BTC/USDT')
                latency = (time.time() - start) * 1000
                
                return {
                    'status': 'healthy',
                    'message': f'Connected to {len(scanner.exchange_instances)} exchanges',
                    'latency': latency,
                    'details': {
                        'exchanges': list(scanner.exchange_instances.keys()),
                        'test_price': ticker['last']
                    }
                }
        
        return {
            'status': 'warning',
            'message': 'ccxt module not available',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_yfinance_api() -> Dict:
    """Test yfinance connectivity."""
    try:
        import time
        start = time.time()
        
        if MARKET_AVAILABLE:
            pipeline = get_market_data_pipeline()
            data = pipeline.get_stock_data('AAPL', period='5d')
            latency = (time.time() - start) * 1000
            
            if data is not None and len(data) > 0:
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'rows': len(data), 'latest_close': float(data['Close'].iloc[-1])}
                }
        
        return {
            'status': 'error',
            'message': 'yfinance module not available',
            'details': {}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_news_api() -> Dict:
    """Test News API connectivity."""
    try:
        import time
        import os
        start = time.time()
        
        news_api_key = st.secrets.get('NEWS_API_KEY') or os.getenv('NEWS_API_KEY')
        
        if not news_api_key:
            return {
                'status': 'warning',
                'message': 'API key not configured. Add NEWS_API_KEY to secrets.toml',
                'details': {}
            }
        
        # Test API with simple request
        import requests
        url = 'https://newsapi.org/v2/top-headlines'
        params = {'country': 'us', 'category': 'business', 'pageSize': 1, 'apiKey': news_api_key}
        response = requests.get(url, params=params, timeout=10)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return {
                    'status': 'healthy',
                    'message': 'Connected successfully',
                    'latency': latency,
                    'details': {'articles_available': data.get('totalResults', 0)}
                }
        
        return {
            'status': 'error',
            'message': f'API returned status {response.status_code}',
            'details': {'response': response.text[:200]}
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


def check_reddit_api() -> Dict:
    """Test Reddit API connectivity."""
    try:
        import os
        
        client_id = st.secrets.get('REDDIT_CLIENT_ID') or os.getenv('REDDIT_CLIENT_ID')
        client_secret = st.secrets.get('REDDIT_CLIENT_SECRET') or os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            return {
                'status': 'warning',
                'message': 'API credentials not configured. Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to secrets.toml',
                'details': {}
            }
        
        # Check if credentials are placeholders
        if 'your_reddit' in client_id.lower() or 'your_reddit' in client_secret.lower():
            return {
                'status': 'warning',
                'message': 'Placeholder credentials detected. Register app at reddit.com/prefs/apps',
                'details': {}
            }
        
        try:
            import praw
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent='StockAnalysis/1.0'
            )
            # Test read-only access
            subreddit = reddit.subreddit('wallstreetbets')
            next(subreddit.hot(limit=1))  # Try to fetch one post
            
            return {
                'status': 'healthy',
                'message': 'Connected successfully (read-only)',
                'details': {'user_agent': 'StockAnalysis/1.0'}
            }
        except ImportError:
            return {
                'status': 'warning',
                'message': 'praw module not installed. Run: pip install praw',
                'details': {}
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Authentication failed: {str(e)}',
                'details': {'exception': str(e)[:200]}
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'details': {'exception': str(e)}
        }


# =============================================================================
# Data Validator
# =============================================================================

def show_data_validator():
    """Inspect DataFrames and validate data quality."""
    st.header("🔍 Data Validator")
    st.markdown("Inspect data quality, detect missing values, and validate ranges.")
    
    st.info("Select a data source to inspect its current state.")
    
    data_source = st.selectbox(
        "Data Source",
        ["Economic Indicators", "Political Trades", "Stock Prices", "Crypto Prices", "Arbitrage Opportunities"]
    )
    
    if data_source == "Economic Indicators":
        validate_economic_data()
    elif data_source == "Political Trades":
        validate_political_data()
    elif data_source == "Stock Prices":
        validate_stock_data()
    elif data_source == "Crypto Prices":
        validate_crypto_data()
    elif data_source == "Arbitrage Opportunities":
        validate_arbitrage_data()


def validate_economic_data():
    """Validate economic indicators data."""
    st.subheader("Economic Indicators Validation")
    
    if not ECONOMIC_AVAILABLE:
        st.error("❌ Economic pipeline not available")
        return
    
    try:
        pipeline = get_economic_data_pipeline()
        data = pipeline.get_all_macro_data()
        
        for key, df in data.items():
            st.markdown(f"**{key}:**")
            
            if df is None or len(df) == 0:
                st.warning(f"⚠️ No data available for {key}")
                continue
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", len(df))
            col2.metric("Columns", len(df.columns))
            col3.metric("Missing Values", df.isnull().sum().sum())
            
            with st.expander(f"Preview {key}"):
                st.dataframe(df.tail(10))
            
            st.markdown("---")
            
    except Exception as e:
        st.error(f"Error validating economic data: {e}")
        st.code(traceback.format_exc())


def validate_political_data():
    """Validate political/insider trades data."""
    st.subheader("Political & Insider Trades Validation")
    
    ticker = st.text_input("Enter ticker to check", value="AAPL")
    
    if not ticker:
        return
    
    if not POLITICAL_AVAILABLE:
        st.error("❌ Political pipeline not available")
        return
    
    try:
        pipeline = get_political_data_pipeline()
        report = pipeline.get_comprehensive_insider_report(ticker)
        
        st.json(report)
        
    except Exception as e:
        st.error(f"Error: {e}")
        st.code(traceback.format_exc())


def validate_stock_data():
    """Validate stock price data."""
    st.subheader("Stock Price Data Validation")
    
    ticker = st.text_input("Enter ticker", value="AAPL")
    
    if not ticker:
        return
    
    if not MARKET_AVAILABLE:
        st.error("❌ Market pipeline not available")
        return
    
    try:
        pipeline = get_market_data_pipeline()
        data = pipeline.get_stock_data(ticker, period='1mo')
        
        if data is None or len(data) == 0:
            st.warning(f"⚠️ No data found for {ticker}")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", len(data))
        col2.metric("Date Range", f"{len(data)} days")
        col3.metric("Missing", data.isnull().sum().sum())
        col4.metric("Latest Close", f"${data['Close'].iloc[-1]:.2f}")
        
        st.dataframe(data.tail(20))
        
    except Exception as e:
        st.error(f"Error: {e}")


def validate_crypto_data():
    """Validate crypto price data."""
    st.subheader("Crypto Price Data Validation")
    
    symbol = st.text_input("Enter crypto pair", value="BTC/USDT")
    exchange = st.selectbox("Exchange", ["binance", "coinbase", "kraken"])
    
    if not MARKET_AVAILABLE:
        st.error("❌ Market pipeline not available")
        return
    
    try:
        pipeline = get_market_data_pipeline()
        data = pipeline.get_crypto_ohlcv(symbol, exchange, timeframe='1h', limit=100)
        
        if data is None or len(data) == 0:
            st.warning(f"⚠️ No data found for {symbol} on {exchange}")
            return
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Candles", len(data))
        col2.metric("Latest Close", f"${data['close'].iloc[-1]:,.2f}")
        col3.metric("24h Change %", f"{((data['close'].iloc[-1] / data['close'].iloc[-24]) - 1) * 100:.2f}%")
        
        st.dataframe(data.tail(20))
        
    except Exception as e:
        st.error(f"Error: {e}")


def validate_arbitrage_data():
    """Validate arbitrage opportunities."""
    st.subheader("Arbitrage Opportunities Validation")
    
    st.info("This scans live exchanges. May take 10-20 seconds.")
    
    if st.button("🔍 Scan for Opportunities"):
        if not ARBITRAGE_AVAILABLE:
            st.error("❌ Arbitrage scanner not available")
            return
        
        try:
            scanner = get_crypto_arbitrage_scanner()
            opportunities = scanner.scan_all_triangular_opportunities()
            
            if len(opportunities) == 0:
                st.warning("⚠️ No arbitrage opportunities found")
            else:
                st.success(f"✅ Found {len(opportunities)} opportunities")
                df = pd.DataFrame(opportunities)
                st.dataframe(df)
                
        except Exception as e:
            st.error(f"Error: {e}")


# =============================================================================
# Model Inspector
# =============================================================================

def show_model_inspector():
    """Step-by-step inspection of model calculations."""
    st.header("🔬 Model Inspector")
    st.markdown("View intermediate calculations for DCF, arbitrage, and predictions.")
    
    model_type = st.selectbox(
        "Select Model Type",
        ["DCF Valuation", "Technical Indicators", "Sentiment Analysis"]
    )
    
    if model_type == "DCF Valuation":
        inspect_dcf_model()
    elif model_type == "Technical Indicators":
        inspect_technical_indicators()
    elif model_type == "Sentiment Analysis":
        inspect_sentiment_model()


def inspect_dcf_model():
    """Inspect DCF calculation step-by-step."""
    st.subheader("DCF Valuation Inspector")
    
    ticker = st.text_input("Enter ticker to inspect", value="AAPL")
    
    if not ticker:
        return
    
    try:
        from enhanced_valuation import run_dcf_valuation
        import yfinance as yf
        
        with st.spinner(f"Analyzing {ticker}..."):
            # Get stock info
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Run DCF
            result = run_dcf_valuation(info)
            
            if 'error' in result:
                st.error(f"❌ {result['error']}")
                return
            
            # Display breakdown
            st.markdown("### 📊 Input Values")
            col1, col2, col3 = st.columns(3)
            col1.metric("Free Cash Flow", f"${result.get('fcf', 0)/1e9:.2f}B")
            col2.metric("Growth Rate", f"{result.get('growth_rate', 0)*100:.1f}%")
            col3.metric("WACC", f"{result.get('wacc', 0)*100:.1f}%")
            
            st.markdown("### 🔢 Year-by-Year Projections")
            if 'cash_flows' in result:
                cf_df = pd.DataFrame({
                    'Year': range(1, len(result['cash_flows']) + 1),
                    'Projected FCF': [f"${cf/1e9:.2f}B" for cf in result['cash_flows']],
                    'Discount Factor': [f"{1/(1+result.get('wacc', 0.1))**i:.4f}" for i in range(1, len(result['cash_flows'])+1)],
                    'Present Value': [f"${cf/(1+result.get('wacc', 0.1))**i/1e9:.2f}B" for i, cf in enumerate(result['cash_flows'], 1)]
                })
                st.dataframe(cf_df, use_container_width=True)
            
            st.markdown("### 💰 Valuation Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Enterprise Value", f"${result.get('enterprise_value', 0)/1e9:.2f}B")
            col2.metric("Equity Value", f"${result.get('equity_value', 0)/1e9:.2f}B")
            col3.metric("Fair Value/Share", f"${result.get('fair_value', 0):.2f}")
            
            # Show calculation steps
            with st.expander("📝 Detailed Calculation Steps"):
                st.markdown("""
                **Step 1:** Calculate Free Cash Flow (FCF)
                - Operating Cash Flow - Capital Expenditures
                
                **Step 2:** Project Future Cash Flows
                - Apply growth rate for 5 years
                - Calculate terminal value using perpetuity growth
                
                **Step 3:** Discount to Present Value
                - Use WACC as discount rate
                - Sum all discounted cash flows
                
                **Step 4:** Calculate Equity Value
                - Enterprise Value - Net Debt
                - Divide by shares outstanding
                """)
                
                st.json(result)
    
    except Exception as e:
        st.error(f"Error inspecting DCF: {e}")
        st.code(traceback.format_exc())


def inspect_technical_indicators():
    """Inspect technical indicator calculations."""
    st.subheader("Technical Indicators Inspector")
    st.info("Select indicators to view their calculation details and intermediate values.")
    
    ticker = st.text_input("Enter ticker", value="AAPL")
    
    if ticker:
        try:
            import yfinance as yf
            data = yf.Ticker(ticker).history(period='3mo')
            
            if len(data) > 0:
                indicator = st.selectbox("Select Indicator", 
                    ["SMA (Simple Moving Average)", "RSI (Relative Strength Index)", 
                     "MACD", "Bollinger Bands"])
                
                if indicator == "SMA (Simple Moving Average)":
                    window = st.slider("Window Size", 5, 200, 20)
                    sma = data['Close'].rolling(window=window).mean()
                    
                    st.line_chart(pd.DataFrame({
                        'Price': data['Close'],
                        f'SMA({window})': sma
                    }))
                    
                    st.markdown(f"**Formula:** SMA = Sum of last {window} closing prices / {window}")
                    st.markdown(f"**Current Value:** ${sma.iloc[-1]:.2f}")
        except Exception as e:
            st.error(f"Error: {e}")


def inspect_sentiment_model():
    """Inspect sentiment analysis model."""
    st.subheader("Sentiment Analysis Inspector")
    st.info("View how sentiment scores are calculated from news and social media.")
    
    sample_text = st.text_area("Enter text to analyze", 
        "Apple stock surges to new highs as iPhone sales exceed expectations!")
    
    if st.button("Analyze Sentiment"):
        try:
            from textblob import TextBlob
            blob = TextBlob(sample_text)
            
            col1, col2 = st.columns(2)
            col1.metric("Polarity", f"{blob.sentiment.polarity:.2f}")
            col2.metric("Subjectivity", f"{blob.sentiment.subjectivity:.2f}")
            
            st.markdown("""
            **Polarity Range:** -1 (very negative) to +1 (very positive)
            **Subjectivity Range:** 0 (objective) to 1 (subjective)
            """)
        except ImportError:
            st.warning("TextBlob not installed. Run: pip install textblob")
        except Exception as e:
            st.error(f"Error: {e}")


# =============================================================================
# Cache Manager
# =============================================================================

def show_cache_manager():
    """Manage Streamlit cache."""
    st.header("🗄️ Cache Manager")
    st.markdown("View and clear cached data to force fresh fetches.")
    
    st.warning("Clearing cache will force all data to be re-fetched, which may be slow.")
    
    if st.button("🗑️ Clear All Cache", type="primary"):
        st.cache_data.clear()
        st.success("✅ Cache cleared successfully!")
        st.rerun()


# =============================================================================
# Live Logs
# =============================================================================

def show_live_logs():
    """Display application logs."""
    st.header("📋 Live Logs")
    st.markdown("Recent application events and errors.")
    
    log_level = st.selectbox("Log Level", ["ALL", "ERROR", "WARNING", "INFO", "DEBUG"])
    max_lines = st.slider("Max lines to display", 10, 500, 100)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (every 5s)")
    with col2:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Get logs from various sources
    st.markdown("### 📝 Application Logs")
    
    try:
        # Try to read streamlit debug log
        import glob
        log_files = glob.glob("streamlit_debug.log") + glob.glob("*.log")
        
        if log_files:
            selected_log = st.selectbox("Select log file", log_files)
            
            with open(selected_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Filter by level
            if log_level != "ALL":
                lines = [line for line in lines if log_level in line.upper()]
            
            # Show last N lines
            recent_lines = lines[-max_lines:]
            
            if recent_lines:
                log_text = ''.join(recent_lines)
                st.text_area("Log Output", log_text, height=400)
                
                # Download button
                st.download_button(
                    "💾 Download Full Log",
                    data=''.join(lines),
                    file_name=f"{selected_log}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                    mime="text/plain"
                )
            else:
                st.info(f"No {log_level} level logs found.")
        else:
            st.warning("No log files found in current directory.")
            st.info("Logs may be in terminal output or system logs.")
    
    except Exception as e:
        st.error(f"Error reading logs: {e}")
        st.info("💡 Try checking terminal/console output directly.")
    
    # Show Python logging handlers
    with st.expander("🔧 Active Log Handlers"):
        root_logger = logging.getLogger()
        st.markdown(f"**Root Logger Level:** {logging.getLevelName(root_logger.level)}")
        st.markdown(f"**Active Handlers:** {len(root_logger.handlers)}")
        
        for i, handler in enumerate(root_logger.handlers):
            st.markdown(f"- Handler {i+1}: {type(handler).__name__}")
    
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()


# =============================================================================
# Session State Inspector
# =============================================================================

def show_session_state():
    """Display all session state variables."""
    st.header("💾 Session State Inspector")
    st.markdown("View all variables stored in `st.session_state`.")
    
    if len(st.session_state) == 0:
        st.info("No session state variables set.")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Variables", len(st.session_state))
    
    # Count types
    type_counts = {}
    for key, value in st.session_state.items():
        type_name = type(value).__name__
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    col2.metric("Data Types", len(type_counts))
    col3.metric("Memory (approx)", f"{sys.getsizeof(dict(st.session_state)) / 1024:.1f} KB")
    
    # Search/filter
    search = st.text_input("🔍 Search variables", placeholder="Filter by key name...")
    
    # Display mode
    display_mode = st.radio("Display Mode", ["Table", "JSON", "Detailed"], horizontal=True)
    
    # Filter variables
    filtered_state = {}
    for key, value in st.session_state.items():
        if search.lower() in key.lower():
            filtered_state[key] = value
    
    if not filtered_state:
        st.warning(f"No variables match '{search}'")
        return
    
    if display_mode == "Table":
        # Show as table
        table_data = []
        for key, value in filtered_state.items():
            table_data.append({
                'Variable': key,
                'Type': type(value).__name__,
                'Value': str(value)[:100] + ('...' if len(str(value)) > 100 else ''),
                'Size (bytes)': sys.getsizeof(value)
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
    
    elif display_mode == "JSON":
        # Convert complex objects to strings
        json_state = {}
        for key, value in filtered_state.items():
            try:
                json.dumps(value)  # Test if JSON serializable
                json_state[key] = value
            except:
                json_state[key] = str(value)
        
        st.json(json_state)
    
    elif display_mode == "Detailed":
        # Show detailed view with expanders
        for key, value in filtered_state.items():
            with st.expander(f"📌 {key} ({type(value).__name__})"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**Type:** `{type(value).__name__}`")
                    st.markdown(f"**Size:** {sys.getsizeof(value)} bytes")
                
                with col2:
                    st.markdown("**Value:**")
                    
                    # Pretty print based on type
                    if isinstance(value, (dict, list)):
                        st.json(value)
                    elif isinstance(value, pd.DataFrame):
                        st.dataframe(value, use_container_width=True)
                    elif isinstance(value, (int, float, str, bool)):
                        st.code(repr(value))
                    else:
                        st.text(str(value)[:500])
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Session State"):
        export_data = {}
        for key, value in st.session_state.items():
            try:
                json.dumps(value)
                export_data[key] = value
            except:
                export_data[key] = str(value)
        
        st.download_button(
            "💾 Download as JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"session_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Clear session state
    if st.button("🗑️ Clear All Session State", type="secondary"):
        if st.button("⚠️ Confirm Clear", type="primary"):
            st.session_state.clear()
            st.success("Session state cleared!")
            st.rerun()


# =============================================================================
# Performance Profiler
# =============================================================================

def show_performance_profiler():
    """Profile slow functions."""
    st.header("⚡ Performance Profiler")
    st.markdown("Identify bottlenecks and slow operations.")
    
    st.info("📊 Measure execution time for different components")
    
    profiling_target = st.selectbox(
        "Select Component to Profile",
        ["Data Fetching", "Technical Analysis", "DCF Calculation", "API Calls"]
    )
    
    if profiling_target == "Data Fetching":
        profile_data_fetching()
    elif profiling_target == "Technical Analysis":
        profile_technical_analysis()
    elif profiling_target == "DCF Calculation":
        profile_dcf_calculation()
    elif profiling_target == "API Calls":
        profile_api_calls()


def profile_data_fetching():
    """Profile data fetching performance."""
    st.subheader("Data Fetching Performance")
    
    ticker = st.text_input("Enter ticker to profile", value="AAPL")
    
    if st.button("🔍 Run Profile"):
        import time
        
        results = []
        
        # Test yfinance
        st.write("Testing yfinance...")
        start = time.time()
        try:
            import yfinance as yf
            data = yf.Ticker(ticker).history(period='1mo')
            elapsed = (time.time() - start) * 1000
            results.append({'Operation': 'yfinance (1 month)', 'Time (ms)': elapsed, 'Status': '✅'})
        except Exception as e:
            results.append({'Operation': 'yfinance (1 month)', 'Time (ms)': 0, 'Status': f'❌ {str(e)[:50]}'})
        
        # Test longer period
        start = time.time()
        try:
            data = yf.Ticker(ticker).history(period='1y')
            elapsed = (time.time() - start) * 1000
            results.append({'Operation': 'yfinance (1 year)', 'Time (ms)': elapsed, 'Status': '✅'})
        except Exception as e:
            results.append({'Operation': 'yfinance (1 year)', 'Time (ms)': 0, 'Status': f'❌ {str(e)[:50]}'})
        
        # Display results
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # Performance recommendations
        st.markdown("### 💡 Recommendations")
        avg_time = df[df['Status'] == '✅']['Time (ms)'].mean()
        if avg_time > 2000:
            st.warning("⚠️ Slow data fetching detected (>2s). Consider enabling caching.")
        elif avg_time > 1000:
            st.info("ℹ️ Moderate performance (1-2s). Within normal range.")
        else:
            st.success("✅ Fast data fetching (<1s). Excellent performance!")


def profile_technical_analysis():
    """Profile technical indicator calculations."""
    st.subheader("Technical Analysis Performance")
    st.info("Measure time to calculate various technical indicators.")
    
    if st.button("🔍 Run Profile"):
        import time
        import yfinance as yf
        
        # Get sample data
        data = yf.Ticker('AAPL').history(period='1y')
        
        results = []
        
        # Test SMA
        start = time.time()
        _ = data['Close'].rolling(window=20).mean()
        results.append({'Indicator': 'SMA(20)', 'Time (ms)': (time.time() - start) * 1000})
        
        # Test RSI
        start = time.time()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        results.append({'Indicator': 'RSI(14)', 'Time (ms)': (time.time() - start) * 1000})
        
        st.dataframe(pd.DataFrame(results), use_container_width=True)


def profile_dcf_calculation():
    """Profile DCF calculation performance."""
    st.subheader("DCF Calculation Performance")
    st.info("Measure time to complete full DCF valuation.")


def profile_api_calls():
    """Profile all API call latencies."""
    st.subheader("API Call Performance")
    
    if st.button("🔍 Test All APIs"):
        import time
        
        with st.spinner("Testing APIs..."):
            results = []
            
            # Test each API
            apis = [
                ('FRED', check_fred_api),
                ('EIA', check_eia_api),
                ('Finnhub', check_finnhub_api),
                ('Alpha Vantage', check_alpha_vantage_api),
                ('yfinance', check_yfinance_api)
            ]
            
            for name, check_func in apis:
                start = time.time()
                result = check_func()
                elapsed = (time.time() - start) * 1000
                
                results.append({
                    'API': name,
                    'Status': result['status'],
                    'Latency (ms)': round(elapsed, 2)
                })
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Highlight slow APIs
            slow_apis = df[df['Latency (ms)'] > 5000]
            if len(slow_apis) > 0:
                st.warning(f"⚠️ Slow APIs detected (>5s): {', '.join(slow_apis['API'].tolist())}")


if __name__ == "__main__":
    show_debug_dashboard()
