import streamlit as st
import pandas as pd
import numpy as np
from data_fetcher import get_ticker, get_stock_price_data, get_company_info
from scipy.optimize import minimize

@st.cache_data(ttl=3600)
def run_portfolio_optimization(tickers_string, risk_free_rate=0.02):
    """Runs the full MPT analysis."""
    tickers = [t.strip().upper() for t in tickers_string.split(",")]
    if len(tickers) < 2:
        st.error("Please enter at least 2 tickers to compare.")
        return None

    all_price_data = {}
    for ticker in tickers:
        try:
            stock_obj = get_ticker(ticker)
            # Validate ticker
            if not get_company_info(stock_obj).get('marketCap'):
                st.warning(f"Could not validate ticker: {ticker}. Skipping.")
                continue
            prices = get_stock_price_data(stock_obj)
            all_price_data[ticker] = prices['Close']
        except Exception:
            st.warning(f"Could not fetch data for {ticker}.")
    
    data = pd.DataFrame(all_price_data).dropna()

    if data.empty or len(data.columns) < 2:
        st.error(f"Could not download complete 3-year data for all tickers. Please check tickers.")
        return None
        
    returns = data.pct_change().dropna()
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