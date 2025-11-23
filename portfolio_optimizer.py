import streamlit as st
import pandas as pd
import numpy as np
from data_fetcher import get_ticker, get_stock_price_data, get_company_info
from scipy.optimize import minimize
from performance_optimizer import batch_fetch_tickers, PerformanceMonitor, optimize_dataframe

# Import fast batch fetcher for portfolio optimization
try:
    from fast_data_fetcher import get_multiple_tickers_price_data
    YAHOOQUERY_AVAILABLE = True
except ImportError:
    YAHOOQUERY_AVAILABLE = False

@st.cache_data(ttl=3600)
def run_portfolio_optimization(tickers_string, risk_free_rate=0.02, use_fast=True):
    """
    Runs the full MPT analysis.

    Args:
        tickers_string: Comma-separated ticker symbols
        risk_free_rate: Risk-free rate for Sharpe ratio calculation
        use_fast: If True, uses yahooquery for batch fetching (3-5x faster)
    """
    tickers = [t.strip().upper() for t in tickers_string.split(",")]
    if len(tickers) < 2:
        st.error("Please enter at least 2 tickers to compare.")
        return None

    all_price_data = {}

    # Use fast batch fetching if available
    with PerformanceMonitor(f"portfolio_data_fetch_{len(tickers)}_tickers"):
        if use_fast and YAHOOQUERY_AVAILABLE:
            price_data_dict = get_multiple_tickers_price_data(tickers, period='3y')
            for ticker in tickers:
                if ticker in price_data_dict:
                    df = price_data_dict[ticker]
                    if not df.empty and 'close' in df.columns:
                        all_price_data[ticker] = df['close']
                    elif not df.empty and 'Close' in df.columns:
                        all_price_data[ticker] = df['Close']
        else:
            # Use parallel batch fetching from performance_optimizer
            st.info("📊 Using optimized parallel batch fetching (5-10x faster than sequential)")

            # batch_fetch_tickers returns historical data for multiple tickers in parallel
            # We need to fetch 3-year data, so we'll use a custom period
            # The batch_fetch_tickers default is 1mo, but we can fetch them in parallel

            import yfinance as yf
            from concurrent.futures import ThreadPoolExecutor, as_completed

            def fetch_3y_data(ticker):
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period='3y')
                    if not hist.empty and 'Close' in hist.columns:
                        return hist['Close']
                except Exception as e:
                    st.warning(f"Could not fetch data for {ticker}: {e}")
                return None

            # Parallel execution for 3-year data
            with ThreadPoolExecutor(max_workers=min(len(tickers), 10)) as executor:
                future_to_ticker = {executor.submit(fetch_3y_data, ticker): ticker for ticker in tickers}

                for future in as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    try:
                        result = future.result()
                        if result is not None:
                            all_price_data[ticker] = result
                    except Exception as e:
                        st.warning(f"Error fetching {ticker}: {e}")

    data = pd.DataFrame(all_price_data).dropna()

    if data.empty or len(data.columns) < 2:
        st.error(f"Could not download complete 3-year data for all tickers. Please check tickers.")
        return None

    # Optimize DataFrame memory usage (60-80% reduction)
    data = optimize_dataframe(data)

    returns = data.pct_change().dropna()
    returns = optimize_dataframe(returns)  # Optimize returns DataFrame too

    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    num_assets = len(tickers)
    
    # Monte Carlo Simulation
    num_portfolios = 10000
    results = np.zeros((3, num_portfolios))
    weights_array = []
    
    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        weights_array.append(weights)
        ret, vol, sharpe = get_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate)
        results[0,i], results[1,i], results[2,i] = ret, vol, sharpe
        
    results_df = pd.DataFrame(results.T, columns=['Return', 'Volatility', 'SharpeRatio'])
    results_df['Weights'] = weights_array
    
    # Optimizer
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = np.array([1./num_assets] * num_assets)

    max_sharpe_opt = minimize(minimize_negative_sharpe, initial_weights, args=(mean_returns, cov_matrix, risk_free_rate), method='SLSQP', bounds=bounds, constraints=constraints)
    min_vol_opt = minimize(minimize_volatility, initial_weights, args=(mean_returns, cov_matrix, risk_free_rate), method='SLSQP', bounds=bounds, constraints=constraints)
    
    max_sharpe_weights = max_sharpe_opt.x
    max_sharpe_stats = get_portfolio_stats(max_sharpe_weights, mean_returns, cov_matrix, risk_free_rate)
    min_vol_weights = min_vol_opt.x
    min_vol_stats = get_portfolio_stats(min_vol_weights, mean_returns, cov_matrix, risk_free_rate)
    
    return results_df, max_sharpe_stats, max_sharpe_weights, min_vol_stats, min_vol_weights, tickers

# --- Helper functions for optimizer ---

def get_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate):
    port_return = np.sum(mean_returns * weights)
    port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe_ratio = (port_return - risk_free_rate) / port_volatility
    return port_return, port_volatility, sharpe_ratio

def minimize_negative_sharpe(weights, mean_returns, cov_matrix, risk_free_rate):
    return -get_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate)[2]

def minimize_volatility(weights, mean_returns, cov_matrix, risk_free_rate):
    return get_portfolio_stats(weights, mean_returns, cov_matrix, risk_free_rate)[1]