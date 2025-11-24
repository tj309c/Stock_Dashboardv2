"""
Correlation Factors Analysis Module

Provides comprehensive correlation analysis for identifying key factors that drive
stock or market movements. Uses a 4-layer approach to separate truly predictive
factors from spurious correlations.

Layers:
1. Statistical Correlation Strength (Pearson r, p-value, R²)
2. Predictive Power (lead/lag analysis)
3. Stability Over Time (rolling correlation)
4. Key Factor Score (0-100 combining all layers)

Performance: ~300-500ms per factor with caching
"""

from scipy.stats import pearsonr
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import threading

# Thread lock for yfinance downloads to prevent data corruption
_yf_download_lock = threading.Lock()


# ========================================
# Layer 1: Statistical Correlation Strength
# ========================================

def calculate_correlation_strength(stock_returns: pd.Series, factor_returns: pd.Series) -> Dict:
    """
    Calculate Pearson correlation, p-value, R², and strength rating.

    Args:
        stock_returns: Daily returns of stock/market
        factor_returns: Daily returns of factor

    Returns:
        dict with keys:
            - correlation: Pearson correlation coefficient (-1 to 1)
            - p_value: Statistical significance (0 to 1, lower = more significant)
            - r_squared: R² value (0 to 1, variance explained)
            - strength: Rating (Very Strong/Strong/Moderate/Weak/Very Weak)
            - stars: Visual rating (⭐⭐⭐⭐⭐ to ⭐)
            - is_significant: Boolean (p < 0.05)
            - direction: Positive/Negative/None
    """
    # Align the series by index
    aligned_data = pd.concat([stock_returns, factor_returns], axis=1, join='inner').dropna()

    if len(aligned_data) < 30:
        return {
            'correlation': 0.0,
            'p_value': 1.0,
            'r_squared': 0.0,
            'strength': 'Insufficient Data',
            'stars': '',
            'is_significant': False,
            'direction': 'None'
        }

    stock_data = aligned_data.iloc[:, 0]
    factor_data = aligned_data.iloc[:, 1]

    # Calculate Pearson correlation
    correlation, p_value = pearsonr(stock_data, factor_data)

    # R-squared (variance explained)
    r_squared = correlation ** 2

    # Determine strength based on absolute correlation
    abs_corr = abs(correlation)
    if abs_corr >= 0.7:
        strength = "Very Strong"
        stars = "⭐⭐⭐⭐⭐"
    elif abs_corr >= 0.5:
        strength = "Strong"
        stars = "⭐⭐⭐⭐"
    elif abs_corr >= 0.3:
        strength = "Moderate"
        stars = "⭐⭐⭐"
    elif abs_corr >= 0.1:
        strength = "Weak"
        stars = "⭐⭐"
    else:
        strength = "Very Weak"
        stars = "⭐"

    # Direction
    if correlation > 0.1:
        direction = "Positive"
    elif correlation < -0.1:
        direction = "Negative"
    else:
        direction = "None"

    return {
        'correlation': round(correlation, 3),
        'p_value': round(p_value, 4),
        'r_squared': round(r_squared, 3),
        'strength': strength,
        'stars': stars,
        'is_significant': p_value < 0.05,
        'direction': direction
    }


# ========================================
# Layer 2: Predictive Power (Lead/Lag Analysis)
# ========================================

def calculate_lead_lag_correlation(stock_returns: pd.Series, factor_returns: pd.Series, max_lag: int = 10) -> Dict:
    """
    Test if factor predicts stock movement 1-10 days ahead.

    Lead/lag analysis checks if changes in the factor today predict
    changes in the stock in future days.

    Args:
        stock_returns: Daily returns of stock/market
        factor_returns: Daily returns of factor
        max_lag: Maximum days to test (default 10)

    Returns:
        dict with keys:
            - best_lag: Days ahead where correlation is strongest (0-10)
            - best_correlation: Correlation at best lag
            - is_predictive: Boolean (best_lag > 0 and significant)
            - direction: Leading/Coincident/Lagging
            - insight: Plain English explanation
    """
    # Align the series
    aligned_data = pd.concat([stock_returns, factor_returns], axis=1, join='inner').dropna()

    if len(aligned_data) < 30:
        return {
            'best_lag': 0,
            'best_correlation': 0.0,
            'is_predictive': False,
            'direction': 'Unknown',
            'insight': 'Insufficient data for lead/lag analysis'
        }

    stock_data = aligned_data.iloc[:, 0]
    factor_data = aligned_data.iloc[:, 1]

    # Test correlations at different lags
    lag_correlations = {}

    for lag in range(0, max_lag + 1):
        if lag == 0:
            # Coincident correlation
            corr, p_val = pearsonr(stock_data, factor_data)
        else:
            # Factor leads stock by 'lag' days
            # Shift stock forward (future) and correlate with factor today
            if len(stock_data) > lag:
                stock_future = stock_data.shift(-lag).dropna()
                factor_aligned = factor_data.loc[stock_future.index]

                if len(stock_future) >= 30 and len(factor_aligned) >= 30:
                    corr, p_val = pearsonr(stock_future, factor_aligned)
                else:
                    corr = 0.0
            else:
                corr = 0.0

        lag_correlations[lag] = abs(corr)

    # Find best lag
    best_lag = max(lag_correlations, key=lag_correlations.get)
    best_correlation = lag_correlations[best_lag]

    # Original correlation at lag 0 for comparison
    original_corr = lag_correlations[0]

    # Determine if predictive
    is_predictive = best_lag > 0 and best_correlation > 0.3

    # Direction
    if best_lag == 0:
        direction = "Coincident"
        insight = f"Factor moves with the stock simultaneously (no predictive power)"
    elif best_lag > 0:
        direction = "Leading"
        if is_predictive:
            insight = f"Factor predicts stock movement {best_lag} day{'s' if best_lag > 1 else ''} ahead (correlation: {best_correlation:.2f})"
        else:
            insight = f"Weak leading relationship ({best_lag} days ahead, correlation: {best_correlation:.2f})"
    else:
        direction = "Lagging"
        insight = f"Stock moves before factor (not useful for prediction)"

    return {
        'best_lag': best_lag,
        'best_correlation': round(best_correlation, 3),
        'is_predictive': is_predictive,
        'direction': direction,
        'insight': insight
    }


# ========================================
# Layer 3: Stability Over Time
# ========================================

def calculate_rolling_correlation(stock_returns: pd.Series, factor_returns: pd.Series, window: int = 60) -> Dict:
    """
    Calculate 60-day rolling correlation to check stability over time.

    A stable correlation is more reliable than one that varies wildly.

    Args:
        stock_returns: Daily returns of stock/market
        factor_returns: Daily returns of factor
        window: Rolling window size in days (default 60)

    Returns:
        dict with keys:
            - mean_correlation: Average rolling correlation
            - std_correlation: Standard deviation of rolling correlation
            - stability: Rating (Very Stable/Stable/Moderate/Unstable/Very Unstable)
            - rolling_series: pd.Series of rolling correlations (for plotting)
            - insight: Plain English explanation
    """
    # Align the series
    aligned_data = pd.concat([stock_returns, factor_returns], axis=1, join='inner').dropna()

    if len(aligned_data) < window + 30:
        return {
            'mean_correlation': 0.0,
            'std_correlation': 0.0,
            'stability': 'Insufficient Data',
            'rolling_series': pd.Series(),
            'insight': f'Need at least {window + 30} days of data for rolling correlation analysis'
        }

    # Rename columns for clarity - handle case where concat creates extra columns
    if aligned_data.shape[1] == 2:
        aligned_data.columns = ['stock', 'factor']
    else:
        # If we have more than 2 columns, take first 2
        aligned_data = aligned_data.iloc[:, :2]
        aligned_data.columns = ['stock', 'factor']

    # Calculate rolling correlation properly
    # We need to manually calculate correlation for each rolling window
    rolling_correlations = []
    dates = []

    for i in range(window, len(aligned_data) + 1):
        window_data = aligned_data.iloc[i-window:i]
        if len(window_data) == window:
            corr, _ = pearsonr(window_data['stock'], window_data['factor'])
            rolling_correlations.append(corr)
            dates.append(aligned_data.index[i-1])

    rolling_corr = pd.Series(rolling_correlations, index=dates)
    rolling_corr = rolling_corr.dropna()

    if len(rolling_corr) < 10:
        return {
            'mean_correlation': 0.0,
            'std_correlation': 0.0,
            'stability': 'Insufficient Data',
            'rolling_series': pd.Series(),
            'insight': 'Insufficient rolling periods for stability analysis'
        }

    # Calculate statistics
    mean_corr = rolling_corr.mean()
    std_corr = rolling_corr.std()

    # Determine stability based on standard deviation
    if std_corr < 0.1:
        stability = "Very Stable"
        insight = f"Correlation is very consistent over time (avg: {mean_corr:.2f}, volatility: {std_corr:.2f})"
    elif std_corr < 0.2:
        stability = "Stable"
        insight = f"Correlation is fairly consistent over time (avg: {mean_corr:.2f}, volatility: {std_corr:.2f})"
    elif std_corr < 0.3:
        stability = "Moderate"
        insight = f"Correlation varies moderately over time (avg: {mean_corr:.2f}, volatility: {std_corr:.2f})"
    elif std_corr < 0.4:
        stability = "Unstable"
        insight = f"Correlation changes significantly over time (avg: {mean_corr:.2f}, volatility: {std_corr:.2f})"
    else:
        stability = "Very Unstable"
        insight = f"Correlation is highly inconsistent over time (avg: {mean_corr:.2f}, volatility: {std_corr:.2f})"

    return {
        'mean_correlation': round(mean_corr, 3),
        'std_correlation': round(std_corr, 3),
        'stability': stability,
        'rolling_series': rolling_corr,
        'insight': insight
    }


# ========================================
# Layer 4: Comprehensive Key Factor Score
# ========================================

def calculate_key_factor_score(stock_returns: pd.Series, factor_returns: pd.Series, factor_name: str) -> Dict:
    """
    Combine all layers into a single Key Factor Score (0-100).

    Scoring components:
    - 40 points: Correlation strength (|r| and significance)
    - 30 points: Predictive power (lead/lag)
    - 30 points: Stability (rolling correlation consistency)

    Args:
        stock_returns: Daily returns of stock/market
        factor_returns: Daily returns of factor
        factor_name: Name of the factor for reporting

    Returns:
        dict with keys:
            - key_score: Overall score (0-100)
            - badge: Emoji badge (🏆/🥇/🥈/🥉/📊)
            - rank: Rating (Elite/Strong/Moderate/Weak/Minimal)
            - explanation: Why this score was assigned
            - details: Dict containing all layer results
    """
    # Run all three layers
    layer1 = calculate_correlation_strength(stock_returns, factor_returns)
    layer2 = calculate_lead_lag_correlation(stock_returns, factor_returns)
    layer3 = calculate_rolling_correlation(stock_returns, factor_returns)

    # Component 1: Correlation Strength (40 points max)
    abs_corr = abs(layer1['correlation'])
    is_significant = layer1['is_significant']

    if is_significant:
        strength_score = min(40, abs_corr * 50)  # Scale to 40 max
    else:
        strength_score = min(20, abs_corr * 25)  # Penalize non-significant

    # Component 2: Predictive Power (30 points max)
    if layer2['is_predictive']:
        predictive_score = 30
    elif layer2['best_lag'] > 0:
        predictive_score = min(20, layer2['best_correlation'] * 30)
    else:
        predictive_score = min(15, layer2['best_correlation'] * 20)

    # Component 3: Stability (30 points max)
    std_corr = layer3['std_correlation']

    if std_corr < 0.1:
        stability_score = 30
    elif std_corr < 0.2:
        stability_score = 25
    elif std_corr < 0.3:
        stability_score = 15
    elif std_corr < 0.4:
        stability_score = 10
    else:
        stability_score = 5

    # Total Key Factor Score - keep two decimals to reduce rounding collisions
    key_score = round(strength_score + predictive_score + stability_score, 2)

    # Badge and Rank
    if key_score >= 80:
        badge = "🏆"
        rank = "Elite Key Factor"
    elif key_score >= 60:
        badge = "🥇"
        rank = "Strong Key Factor"
    elif key_score >= 40:
        badge = "🥈"
        rank = "Moderate Key Factor"
    elif key_score >= 20:
        badge = "🥉"
        rank = "Weak Key Factor"
    else:
        badge = "📊"
        rank = "Minimal Key Factor"

    # Generate explanation
    explanation_parts = []

    if layer1['is_significant'] and abs_corr >= 0.5:
        explanation_parts.append(f"Strong correlation ({layer1['correlation']:.2f})")
    elif layer1['is_significant']:
        explanation_parts.append(f"Significant correlation ({layer1['correlation']:.2f})")
    else:
        explanation_parts.append(f"Weak/insignificant correlation ({layer1['correlation']:.2f})")

    if layer2['is_predictive']:
        explanation_parts.append(f"predicts {layer2['best_lag']} days ahead")
    else:
        explanation_parts.append("limited predictive power")

    if layer3['stability'] in ['Very Stable', 'Stable']:
        explanation_parts.append("stable over time")
    else:
        explanation_parts.append("unstable over time")

    explanation = f"{factor_name}: " + ", ".join(explanation_parts) + "."

    return {
        'key_score': key_score,
        'badge': badge,
        'rank': rank,
        'explanation': explanation,
        'details': {
            'correlation': layer1,
            'predictive': layer2,
            'stability': layer3,
            'component_scores': {
                'strength_score': round(strength_score, 2),
                'predictive_score': round(predictive_score, 2),
                'stability_score': round(stability_score, 2)
            }
        }
    }


# ========================================
# Smart Default Factor Selection
# ========================================

def get_default_market_factors() -> Dict[str, str]:
    """
    Get default factors for market-level analysis.

    Returns:
        dict mapping factor names to tickers
    """
    return {
        'Volatility (VIX)': '^VIX',
        '10-Year Treasury': '^TNX',
        'US Dollar (DXY)': 'DX-Y.NYB',
        'Gold': 'GC=F',
        'Oil (WTI)': 'CL=F'
    }


def get_default_stock_factors(ticker: str, ticker_info: Optional[Dict] = None) -> Dict[str, str]:
    """
    Get smart default factors for individual stock analysis.

    Factors are selected based on:
    - Stock sector
    - Market cap
    - International exposure

    Args:
        ticker: Stock ticker symbol
        ticker_info: Optional dict with stock info (sector, marketCap, etc.)
                     If None, will fetch from yfinance

    Returns:
        dict mapping factor names to tickers
    """
    # Always include these
    default_factors = {
        'S&P 500': '^GSPC',
        'Volatility (VIX)': '^VIX'
    }

    # Fetch ticker info if not provided
    if ticker_info is None:
        try:
            stock = yf.Ticker(ticker)
            ticker_info = stock.info
        except:
            ticker_info = {}

    # Get sector
    sector = ticker_info.get('sector', '')

    # Add sector-specific factors
    sector_map = {
        'Technology': ('Technology (XLK)', 'XLK'),
        'Financial Services': ('Financials (XLF)', 'XLF'),
        'Healthcare': ('Healthcare (XLV)', 'XLV'),
        'Energy': ('Energy (XLE)', 'XLE'),
        'Consumer Cyclical': ('Consumer Discretionary (XLY)', 'XLY'),
        'Consumer Defensive': ('Consumer Staples (XLP)', 'XLP'),
        'Industrials': ('Industrials (XLI)', 'XLI'),
        'Basic Materials': ('Materials (XLB)', 'XLB'),
        'Real Estate': ('Real Estate (XLRE)', 'XLRE'),
        'Utilities': ('Utilities (XLU)', 'XLU'),
        'Communication Services': ('Communication (XLC)', 'XLC')
    }

    if sector in sector_map:
        factor_name, ticker_symbol = sector_map[sector]
        default_factors[factor_name] = ticker_symbol
    else:
        # Default to S&P 500 sector fund
        default_factors['Market Sector'] = '^GSPC'

    # Add market cap factor
    market_cap = ticker_info.get('marketCap', 0)

    if market_cap > 200_000_000_000:  # Large cap
        default_factors['Large Cap (SPY)'] = 'SPY'
    elif market_cap > 10_000_000_000:  # Mid cap
        default_factors['Mid Cap (MDY)'] = 'MDY'
    elif market_cap > 2_000_000_000:  # Small cap
        default_factors['Small Cap (IWM)'] = 'IWM'

    # Add interest rate sensitivity for rate-sensitive sectors
    if sector in ['Real Estate', 'Utilities', 'Financial Services']:
        default_factors['10-Year Treasury'] = '^TNX'

    # Add commodity factors for commodity-sensitive sectors
    if sector == 'Energy':
        default_factors['Oil (WTI)'] = 'CL=F'
    elif sector == 'Basic Materials':
        default_factors['Gold'] = 'GC=F'

    # Limit to 6 factors max
    return dict(list(default_factors.items())[:6])


# ========================================
# Parallel Factor Data Fetching
# ========================================

def fetch_factor_data(ticker: str, days: int = 365) -> pd.Series:
    """
    Fetch historical price data for a factor.

    Args:
        ticker: Factor ticker symbol
        days: Number of days of history to fetch

    Returns:
        pd.Series of daily returns
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 30)  # Extra buffer

        # Use lock to prevent yfinance thread-safety issues
        with _yf_download_lock:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # If the provider returns completely empty for the primary ticker, try some known aliases
        if data.empty:
            fallback_aliases = {
                'DX-Y.NYB': ['DX=F', 'DXY'],
                'GC=F': ['GLD'],
                'CL=F': ['USO']
            }

            if ticker in fallback_aliases:
                for alt in fallback_aliases[ticker]:
                    try:
                        with _yf_download_lock:
                            alt_data = yf.download(alt, start=start_date, end=end_date, progress=False)
                        if not alt_data.empty:
                            data = alt_data
                            break
                    except Exception:
                        continue

            # If still empty after trying aliases, bail out
            if data.empty:
                return pd.Series()

        # Handle MultiIndex columns (when yf.download accidentally returns multiple tickers)
        # This can happen with certain tickers or data provider issues
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten to just the first level (price type like 'Adj Close', 'Close', etc.)
            # and take the first ticker if multiple are present
            data = data.iloc[:, :len(data.columns.levels[0])]
            data.columns = data.columns.get_level_values(0)

        # Calculate daily returns
        if 'Adj Close' in data.columns:
            prices = data['Adj Close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            return pd.Series()

        # Ensure prices is a Series, not DataFrame
        if isinstance(prices, pd.DataFrame):
            # Take the first column if multiple columns returned
            prices = prices.iloc[:, 0]

        returns = prices.pct_change().dropna()

        # If no returns were found for the primary ticker, attempt alias fallbacks
        if returns.empty:
            fallback_aliases = {
                'DX-Y.NYB': ['DX=F', 'DXY'],
                'GC=F': ['GLD'],
                'CL=F': ['USO']
            }

            # Try known alias list
            if ticker in fallback_aliases:
                for alt in fallback_aliases[ticker]:
                    try:
                        with _yf_download_lock:
                            alt_data = yf.download(alt, start=start_date, end=end_date, progress=False)
                        if alt_data.empty:
                            continue

                        # Handle MultiIndex columns for fallback tickers too
                        if isinstance(alt_data.columns, pd.MultiIndex):
                            alt_data = alt_data.iloc[:, :len(alt_data.columns.levels[0])]
                            alt_data.columns = alt_data.columns.get_level_values(0)

                        if 'Adj Close' in alt_data.columns:
                            alt_prices = alt_data['Adj Close']
                        elif 'Close' in alt_data.columns:
                            alt_prices = alt_data['Close']
                        else:
                            continue

                        # Ensure alt_prices is a Series
                        if isinstance(alt_prices, pd.DataFrame):
                            alt_prices = alt_prices.iloc[:, 0]

                        alt_returns = alt_prices.pct_change().dropna()
                        if not alt_returns.empty:
                            return alt_returns
                    except Exception:
                        continue

        return returns

    except Exception as e:
        return pd.Series()


@st.cache_data(ttl=14400)  # Cache for 4 hours
def fetch_all_factors_parallel(factor_dict: Dict[str, str], days: int = 365) -> Dict[str, pd.Series]:
    """
    Fetch multiple factors in parallel using ThreadPoolExecutor.

    NOTE: Caching is applied at this level (not fetch_factor_data) because
    Streamlit's cache is not thread-safe when used inside ThreadPoolExecutor.

    Args:
        factor_dict: Dict mapping factor names to tickers
        days: Number of days of history to fetch

    Returns:
        dict mapping factor names to return series
    """
    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_factor = {
            executor.submit(fetch_factor_data, ticker, days): name
            for name, ticker in factor_dict.items()
        }

        for future in as_completed(future_to_factor):
            factor_name = future_to_factor[future]
            try:
                returns = future.result()
                if not returns.empty:
                    results[factor_name] = returns
            except Exception as e:
                continue

    return results


def detect_duplicate_factor_series(factor_series: Dict[str, pd.Series], rtol: float = 1e-8, atol: float = 1e-8) -> Dict[str, list]:
    """
    Detect factor series that are effectively identical to each other.

    Returns a mapping where each 'leader' factor maps to a list of factor names
    that are value-equal to it (excluding itself). Only exact/value-equality is
    used here (index alignment via values comparison).

    Purpose: surface rare cases where different tickers return identical series
    (often due to provider errors or mapping collisions) so consumers can debug.
    """
    groups = {}
    keys = list(factor_series.keys())

    for i, k1 in enumerate(keys):
        s1 = factor_series[k1]
        if s1 is None or s1.empty:
            continue

        for k2 in keys[i+1:]:
            s2 = factor_series[k2]
            if s2 is None or s2.empty:
                continue

            # Compare shapes first
            try:
                if len(s1) != len(s2):
                    continue

                # Align values by index order
                v1 = s1.values
                v2 = s2.values

                if v1.shape == v2.shape and (np.allclose(v1, v2, rtol=rtol, atol=atol)):
                    # Add to group for k1
                    groups.setdefault(k1, []).append(k2)
            except Exception:
                # In case of any unexpected type/shape mismatch, skip
                continue

    return groups


# ========================================
# AI Factor Suggestion (Optional Enhancement)
# ========================================

def suggest_factors_with_ai(ticker: str, ticker_info: Dict, api_key: str, model: str = 'gemini') -> List[Dict[str, str]]:
    """
    Use AI to suggest additional relevant factors based on company profile.

    Args:
        ticker: Stock ticker
        ticker_info: Company info dict
        api_key: API key for the selected model
        model: Which AI model to use ('gemini', 'openai', 'claude', 'grok')

    Returns:
        list of dicts with keys: 'name', 'ticker', 'rationale'
    """
    # Build prompt
    company_name = ticker_info.get('shortName', ticker)
    sector = ticker_info.get('sector', 'Unknown')
    industry = ticker_info.get('industry', 'Unknown')
    description = ticker_info.get('longBusinessSummary', '')[:500]  # Truncate

    prompt = f"""Based on this company profile, suggest 2-3 specific market factors (with ticker symbols) that would likely correlate with stock performance. Focus on factors NOT already covered by standard indices.

Company: {company_name} ({ticker})
Sector: {sector}
Industry: {industry}
Description: {description}

Respond ONLY with a JSON array of objects with this exact format:
[
  {{"name": "Factor Name", "ticker": "TICKER", "rationale": "One sentence why"}},
  ...
]

Example for a chip manufacturer:
[
  {{"name": "Semiconductor ETF", "ticker": "SOXX", "rationale": "Tracks semiconductor industry performance"}},
  {{"name": "Taiwan Semiconductor", "ticker": "TSM", "rationale": "Key supplier and industry bellwether"}}
]

Your suggestions:"""

    try:
        if model == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_obj = genai.GenerativeModel('gemini-pro')
            response = model_obj.generate_content(prompt)
            response_text = response.text

        elif model == 'openai':
            import openai
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3
            )
            response_text = response.choices[0].message.content

        elif model == 'claude':
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{'role': 'user', 'content': prompt}]
            )
            response_text = message.content[0].text

        elif model == 'grok':
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'messages': [{'role': 'user', 'content': prompt}],
                'model': 'grok-beta',
                'temperature': 0.3
            }
            response = requests.post('https://api.x.ai/v1/chat/completions', headers=headers, json=data)
            response_text = response.json()['choices'][0]['message']['content']

        else:
            return []

        # Parse JSON response
        import json
        # Extract JSON array from response (handles markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith('```'):
            # Remove markdown code block
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        suggestions = json.loads(response_text)

        return suggestions[:3]  # Max 3 suggestions

    except Exception as e:
        return []
