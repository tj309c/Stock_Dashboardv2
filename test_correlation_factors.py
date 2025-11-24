"""
Test suite for correlation_factors.py

Tests that different factors produce different correlation scores
and that the rolling correlation calculation is working correctly.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from correlation_factors import (
    calculate_correlation_strength,
    calculate_lead_lag_correlation,
    calculate_rolling_correlation,
    calculate_key_factor_score,
    fetch_factor_data
)


def test_rolling_correlation_different_factors():
    """
    Test that different factors produce different rolling correlations.
    This is the main bug we're fixing - all factors were showing identical scores.
    """
    # Create synthetic stock data (S&P 500 proxy)
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=365, freq='D')

    stock_returns = pd.Series(
        np.random.normal(0.001, 0.02, 365),
        index=dates,
        name='stock'
    )

    # Factor 1: Highly correlated with stock (0.8 correlation)
    factor1_returns = pd.Series(
        stock_returns * 0.8 + np.random.normal(0, 0.01, 365),
        index=dates,
        name='factor1'
    )

    # Factor 2: Moderately correlated with stock (0.4 correlation)
    factor2_returns = pd.Series(
        stock_returns * 0.4 + np.random.normal(0, 0.015, 365),
        index=dates,
        name='factor2'
    )

    # Factor 3: Negatively correlated with stock (-0.6 correlation)
    factor3_returns = pd.Series(
        stock_returns * -0.6 + np.random.normal(0, 0.012, 365),
        index=dates,
        name='factor3'
    )

    # Calculate rolling correlations
    rolling1 = calculate_rolling_correlation(stock_returns, factor1_returns, window=60)
    rolling2 = calculate_rolling_correlation(stock_returns, factor2_returns, window=60)
    rolling3 = calculate_rolling_correlation(stock_returns, factor3_returns, window=60)

    print("\n=== Rolling Correlation Results ===")
    print(f"Factor 1 (high correlation): mean={rolling1['mean_correlation']:.3f}, std={rolling1['std_correlation']:.3f}")
    print(f"Factor 2 (medium correlation): mean={rolling2['mean_correlation']:.3f}, std={rolling2['std_correlation']:.3f}")
    print(f"Factor 3 (negative correlation): mean={rolling3['mean_correlation']:.3f}, std={rolling3['std_correlation']:.3f}")

    # Assert that rolling correlations are DIFFERENT
    assert rolling1['mean_correlation'] != rolling2['mean_correlation'], \
        "Factor 1 and Factor 2 should have different mean correlations"

    assert rolling1['mean_correlation'] != rolling3['mean_correlation'], \
        "Factor 1 and Factor 3 should have different mean correlations"

    assert rolling2['mean_correlation'] != rolling3['mean_correlation'], \
        "Factor 2 and Factor 3 should have different mean correlations"

    # Assert that Factor 1 has highest positive correlation
    assert rolling1['mean_correlation'] > rolling2['mean_correlation'], \
        "Factor 1 should have higher correlation than Factor 2"

    # Assert that Factor 3 has negative correlation
    assert rolling3['mean_correlation'] < 0, \
        "Factor 3 should have negative correlation"

    print("✅ All rolling correlations are DIFFERENT (bug is fixed!)")


def test_key_factor_scores_different():
    """
    Test that different factors produce different Key Factor Scores.
    This is the ultimate test - the bug caused all factors to show 24.2/100.
    """
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=365, freq='D')

    stock_returns = pd.Series(
        np.random.normal(0.001, 0.02, 365),
        index=dates,
        name='stock'
    )

    # Factor 1: Strong correlation + predictive
    factor1_returns = pd.Series(
        stock_returns.shift(1).fillna(0) * 0.7 + np.random.normal(0, 0.01, 365),
        index=dates,
        name='factor1'
    )

    # Factor 2: Weak correlation + not predictive
    factor2_returns = pd.Series(
        stock_returns * 0.2 + np.random.normal(0, 0.02, 365),
        index=dates,
        name='factor2'
    )

    # Factor 3: No correlation (random)
    factor3_returns = pd.Series(
        np.random.normal(0, 0.015, 365),
        index=dates,
        name='factor3'
    )

    # Calculate Key Factor Scores
    score1 = calculate_key_factor_score(stock_returns, factor1_returns, "Strong Factor")
    score2 = calculate_key_factor_score(stock_returns, factor2_returns, "Weak Factor")
    score3 = calculate_key_factor_score(stock_returns, factor3_returns, "Random Factor")

    print("\n=== Key Factor Scores ===")
    print(f"Factor 1 (strong): {score1['key_score']}/100 - {score1['rank']}")
    print(f"  Components: strength={score1['details']['component_scores']['strength_score']:.1f}, "
          f"predictive={score1['details']['component_scores']['predictive_score']:.1f}, "
          f"stability={score1['details']['component_scores']['stability_score']:.1f}")

    print(f"Factor 2 (weak): {score2['key_score']}/100 - {score2['rank']}")
    print(f"  Components: strength={score2['details']['component_scores']['strength_score']:.1f}, "
          f"predictive={score2['details']['component_scores']['predictive_score']:.1f}, "
          f"stability={score2['details']['component_scores']['stability_score']:.1f}")

    print(f"Factor 3 (random): {score3['key_score']}/100 - {score3['rank']}")
    print(f"  Components: strength={score3['details']['component_scores']['strength_score']:.1f}, "
          f"predictive={score3['details']['component_scores']['predictive_score']:.1f}, "
          f"stability={score3['details']['component_scores']['stability_score']:.1f}")

    # Assert that scores are DIFFERENT
    assert score1['key_score'] != score2['key_score'], \
        "Strong and Weak factors should have different scores"

    assert score1['key_score'] != score3['key_score'], \
        "Strong and Random factors should have different scores"

    assert score2['key_score'] != score3['key_score'], \
        "Weak and Random factors should have different scores"

    # Assert that strong factor has highest score
    assert score1['key_score'] > score2['key_score'], \
        "Strong factor should score higher than Weak factor"

    assert score1['key_score'] > score3['key_score'], \
        "Strong factor should score higher than Random factor"

    print("✅ All Key Factor Scores are DIFFERENT (bug is fixed!)")


def test_real_market_data():
    """
    Test with actual market data to see if different factors produce different scores.
    """
    # Fetch real data for S&P 500 and factors
    print("\n=== Testing with Real Market Data ===")

    # Fetch S&P 500
    sp500_returns = fetch_factor_data("^GSPC", days=365)

    if sp500_returns.empty:
        pytest.skip("Unable to fetch S&P 500 data - skipping real data test")

    # Fetch VIX
    vix_returns = fetch_factor_data("^VIX", days=365)

    # Fetch Oil
    oil_returns = fetch_factor_data("CL=F", days=365)

    # Fetch Gold
    gold_returns = fetch_factor_data("GC=F", days=365)

    if vix_returns.empty or oil_returns.empty or gold_returns.empty:
        pytest.skip("Unable to fetch factor data - skipping real data test")

    # Calculate scores
    vix_score = calculate_key_factor_score(sp500_returns, vix_returns, "VIX")
    oil_score = calculate_key_factor_score(sp500_returns, oil_returns, "Oil")
    gold_score = calculate_key_factor_score(sp500_returns, gold_returns, "Gold")

    print(f"VIX Score: {vix_score['key_score']}/100")
    print(f"Oil Score: {oil_score['key_score']}/100")
    print(f"Gold Score: {gold_score['key_score']}/100")

    # These should NOT all be 24.2
    scores = [vix_score['key_score'], oil_score['key_score'], gold_score['key_score']]
    unique_scores = len(set(scores))

    print(f"\nUnique scores: {unique_scores}/3")

    assert unique_scores > 1, \
        f"ERROR: All factors have identical scores: {scores}. The bug is NOT fixed!"

    print("✅ Real market data produces DIFFERENT scores (bug is fixed!)")


def test_correlation_strength():
    """
    Test that correlation strength calculation works correctly.
    """
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')

    # Create perfectly correlated data
    stock_returns = pd.Series(np.random.normal(0, 0.01, 100), index=dates)
    perfect_factor = stock_returns.copy()

    # Create uncorrelated data
    random_factor = pd.Series(np.random.normal(0, 0.01, 100), index=dates)

    # Test perfect correlation
    perfect_result = calculate_correlation_strength(stock_returns, perfect_factor)
    print(f"\nPerfect correlation: {perfect_result['correlation']:.3f}")
    assert abs(perfect_result['correlation'] - 1.0) < 0.01, "Perfect correlation should be ~1.0"

    # Test random correlation
    random_result = calculate_correlation_strength(stock_returns, random_factor)
    print(f"Random correlation: {random_result['correlation']:.3f}")
    assert abs(random_result['correlation']) < 0.3, "Random correlation should be near 0"

    print("✅ Correlation strength calculation works correctly")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
