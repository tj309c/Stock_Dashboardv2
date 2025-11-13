import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
# Note: data_fetcher functions not needed in this module

def get_technical_signals(data):
    """Analyzes the latest data point to generate bullish/bearish signals."""
    if len(data) < 2:
        return [], []
    
    bullish_signals, bearish_signals = [], []
    latest = data.iloc[-1]
    
    if latest['RSI_14'] < 30: bullish_signals.append("RSI is Oversold (< 30)")
    if latest['RSI_14'] > 70: bearish_signals.append("RSI is Overbought (> 70)")
        
    if latest['MACDh_12_26_9'] > 0 and data.iloc[-2]['MACDh_12_26_9'] < 0:
        bullish_signals.append("MACD Crosses Above Signal (Bullish Crossover)")
    elif latest['MACDh_12_26_9'] < 0 and data.iloc[-2]['MACDh_12_26_9'] > 0:
        bearish_signals.append("MACD Crosses Below Signal (Bearish Crossover)")
        
    if latest['Close'] > latest['SMA50']: bullish_signals.append("Price > 50-Day Avg")
    if latest['Close'] < latest['SMA50']: bearish_signals.append("Price < 50-Day Avg")
    if latest['SMA50'] > latest['SMA200'] and data.iloc[-2]['SMA50'] < data.iloc[-2]['SMA200']:
         bullish_signals.append("Golden Cross (SMA 50 crosses SMA 200)")
    if latest['SMA50'] < latest['SMA200'] and data.iloc[-2]['SMA50'] > data.iloc[-2]['SMA200']:
         bearish_signals.append("Death Cross (SMA 50 crosses below SMA 200)")

    if latest['Close'] < latest['BBL_20_2.0_2.0']: bullish_signals.append("Price below Lower Bollinger Band")
    if latest['Close'] > latest['BBU_20_2.0_2.0']: bearish_signals.append("Price above Upper Bollinger Band")

    if latest['ADX_14'] > 25:
        if latest['DMP_14'] > latest['DMN_14']:
            bullish_signals.append(f"Strong Uptrend (ADX: {latest['ADX_14']:.0f})")

    return bullish_signals, bearish_signals

@st.cache_data(ttl=3600)
def calculate_historical_pe(price_data, quarterly_financials):
    try:
        # Try multiple possible column names for EPS
        possible_eps_columns = [
            'Basic EPS', 'Diluted EPS', 'Normalized Basic EPS', 
            'Basic Earnings Per Share', 'EPS'
        ]
        q_eps = None
        for col_name in possible_eps_columns:
            if col_name in quarterly_financials.index:
                q_eps = quarterly_financials.loc[col_name]
                break

        if q_eps is None:
            available_cols_preview = list(quarterly_financials.index[:10])
            return None, f"Could not find a valid EPS column. Available columns start with: {available_cols_preview}"
        
        # Correctly calculate a rolling TTM EPS for historical accuracy
        ttm_eps = q_eps.iloc[::-1].rolling(window=4, min_periods=4).sum().iloc[::-1].dropna()

        if ttm_eps.empty:
            return None, "Not enough quarterly data to calculate TTM EPS."

        daily_prices = price_data[['Close']].copy()
        daily_prices.index = daily_prices.index.tz_convert('UTC')
        ttm_eps.index = ttm_eps.index.tz_localize('UTC')
        
        pe_data = pd.concat([daily_prices, ttm_eps.rename('TTM_EPS')], axis=1)
        pe_data.sort_index(inplace=True)
        pe_data['TTM_EPS'] = pe_data['TTM_EPS'].ffill()
        pe_data = pe_data.dropna()
        pe_data['PE_Ratio'] = pe_data['Close'] / pe_data['TTM_EPS']
        pe_data = pe_data[pe_data['PE_Ratio'] > 0]
        
        return pe_data['PE_Ratio'], None

    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=3600)
def calculate_risk_metrics(price_data, market_ticker='^GSPC'):
    """
    Calculates risk metrics including Beta, Sharpe Ratio, and Sortino Ratio.

    Args:
        price_data: DataFrame with stock price data
        market_ticker: Market index ticker (default: S&P 500)

    Returns:
        beta: Stock beta relative to market
        sharpe: Sharpe ratio
        sortino: Sortino ratio
        rolling_beta: Series of rolling beta values
        rolling_volatility: Series of rolling volatility
        error: Error message if any
    """
    try:
        if price_data.empty or 'Close' not in price_data.columns:
            return 0, 0, 0, None, None, "Price data is empty or missing Close column"

        # Fetch market data
        market_data = yf.download(market_ticker, start=price_data.index[0], end=price_data.index[-1], progress=False)

        if market_data.empty:
            return 0, 0, 0, None, None, f"Could not fetch market data for {market_ticker}"

        # Calculate returns
        stock_returns = price_data['Close'].pct_change().dropna()
        market_returns = market_data['Close'].pct_change().dropna()

        # Align the two series
        combined = pd.DataFrame({
            'stock': stock_returns,
            'market': market_returns
        }).dropna()

        if len(combined) < 30:
            return 0, 0, 0, None, None, "Not enough data points to calculate risk metrics"

        # Calculate Beta
        covariance = combined['stock'].cov(combined['market'])
        market_variance = combined['market'].var()

        if market_variance > 0:
            beta = covariance / market_variance
        else:
            beta = 0

        # Calculate Sharpe Ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        excess_returns = combined['stock'].mean() * 252 - risk_free_rate  # Annualized
        volatility = combined['stock'].std() * np.sqrt(252)  # Annualized

        if volatility > 0:
            sharpe = excess_returns / volatility
        else:
            sharpe = 0

        # Calculate Sortino Ratio (only downside volatility)
        downside_returns = combined['stock'][combined['stock'] < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)

        if downside_volatility > 0:
            sortino = excess_returns / downside_volatility
        else:
            sortino = 0

        # Calculate rolling beta (90-day window)
        rolling_window = 90
        if len(combined) >= rolling_window:
            rolling_cov = combined['stock'].rolling(window=rolling_window).cov(combined['market'])
            rolling_var = combined['market'].rolling(window=rolling_window).var()
            rolling_beta = (rolling_cov / rolling_var).dropna()
        else:
            rolling_beta = pd.Series(dtype=float)

        # Calculate rolling volatility (30-day window)
        rolling_volatility = (combined['stock'].rolling(window=30).std() * np.sqrt(252)).dropna()

        return beta, sharpe, sortino, rolling_beta, rolling_volatility, None

    except Exception as e:
        return 0, 0, 0, None, None, str(e)