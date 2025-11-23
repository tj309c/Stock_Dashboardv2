"""
Tests for forecasting.py
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from forecasting import get_fast_forecast, get_prophet_forecast


@pytest.fixture
def sample_price_data():
    """Generate sample price data for testing"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    # Create a deterministic price series with upward trend
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    df = pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.99,
        'High': prices * 1.01,
        'Low': prices * 0.98,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    return df


@pytest.fixture
def upward_trend_data():
    """Generate data with clear upward trend"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Close': np.linspace(100, 200, 100)
    }, index=dates)
    return df


@pytest.fixture
def downward_trend_data():
    """Generate data with clear downward trend"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Close': np.linspace(200, 100, 100)
    }, index=dates)
    return df


@pytest.mark.unit
def test_get_fast_forecast_basic(sample_price_data):
    """Test basic fast forecast functionality"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    assert model == 'fast_ema_model'
    assert forecast is not None
    assert isinstance(forecast, pd.DataFrame)
    assert 'ds' in forecast.columns
    assert 'yhat' in forecast.columns
    assert 'yhat_upper' in forecast.columns
    assert 'yhat_lower' in forecast.columns


@pytest.mark.unit
def test_get_fast_forecast_length(sample_price_data):
    """Test that forecast has correct length"""
    weeks = 4
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=weeks)

    # Should have historical + forecast data
    expected_future_days = weeks * 7
    assert len(forecast) >= expected_future_days


@pytest.mark.unit
def test_get_fast_forecast_confidence_interval(sample_price_data):
    """Test that confidence intervals are properly calculated"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    # Upper bound should be greater than forecast
    future = forecast[forecast['ds'] > sample_price_data.index[-1]]
    assert all(future['yhat_upper'] >= future['yhat'])
    assert all(future['yhat_lower'] <= future['yhat'])


@pytest.mark.unit
def test_get_fast_forecast_confidence_interval_widens(sample_price_data):
    """Test that confidence interval widens over time"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=8)

    future = forecast[forecast['ds'] > sample_price_data.index[-1]]
    # Calculate interval width
    interval_width = future['yhat_upper'] - future['yhat_lower']

    # First interval should be narrower than last interval
    assert interval_width.iloc[0] < interval_width.iloc[-1]


@pytest.mark.unit
def test_get_fast_forecast_different_periods(sample_price_data):
    """Test forecast with different time periods"""
    for weeks in [1, 4, 12, 52]:
        model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=weeks)
        assert forecast is not None
        assert len(forecast) > 0

        # Verify we have approximately the right number of forecast points
        future = forecast[forecast['ds'] > sample_price_data.index[-1]]
        assert len(future) == weeks * 7


@pytest.mark.unit
def test_get_prophet_forecast_fast_mode(sample_price_data):
    """Test that prophet wrapper defaults to fast mode"""
    model, forecast = get_prophet_forecast(sample_price_data, weeks_to_forecast=4, use_fast=True)

    assert model == 'fast_ema_model'
    assert forecast is not None


@pytest.mark.unit
def test_get_fast_forecast_with_short_history():
    """Test forecast with minimal historical data"""
    dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
    df = pd.DataFrame({
        'Close': np.linspace(100, 110, 10)
    }, index=dates)

    model, forecast = get_fast_forecast(df, weeks_to_forecast=1)
    assert forecast is not None
    assert len(forecast) > 0


@pytest.mark.unit
def test_get_fast_forecast_upward_trend(upward_trend_data):
    """Test that forecast captures upward trend direction"""
    model, forecast = get_fast_forecast(upward_trend_data, weeks_to_forecast=4)
    future = forecast[forecast['ds'] > upward_trend_data.index[-1]]

    # First forecast value should be higher than last historical value
    # (with some tolerance for volatility adjustments)
    last_historical = upward_trend_data['Close'].iloc[-1]
    first_forecast = future['yhat'].iloc[0]
    assert first_forecast >= last_historical * 0.95  # Allow 5% tolerance


@pytest.mark.unit
def test_get_fast_forecast_downward_trend(downward_trend_data):
    """Test that forecast captures downward trend direction"""
    model, forecast = get_fast_forecast(downward_trend_data, weeks_to_forecast=4)
    future = forecast[forecast['ds'] > downward_trend_data.index[-1]]

    # Forecast should continue downward trend
    last_historical = downward_trend_data['Close'].iloc[-1]
    first_forecast = future['yhat'].iloc[0]
    assert first_forecast <= last_historical * 1.05  # Allow 5% tolerance


@pytest.mark.unit
def test_get_fast_forecast_returns_timestamps(sample_price_data):
    """Test that forecast returns proper datetime objects"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    assert pd.api.types.is_datetime64_any_dtype(forecast['ds'])


@pytest.mark.unit
def test_get_fast_forecast_no_nan_values(sample_price_data):
    """Test that forecast doesn't contain NaN values"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    future = forecast[forecast['ds'] > sample_price_data.index[-1]]
    assert not future['yhat'].isna().any()
    assert not future['yhat_upper'].isna().any()
    assert not future['yhat_lower'].isna().any()


@pytest.mark.unit
def test_get_fast_forecast_deterministic(sample_price_data):
    """Test that forecast is deterministic (same input = same output)"""
    model1, forecast1 = get_fast_forecast(sample_price_data, weeks_to_forecast=4)
    model2, forecast2 = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    # Results should be identical
    pd.testing.assert_frame_equal(forecast1, forecast2)


@pytest.mark.unit
def test_get_fast_forecast_positive_values(sample_price_data):
    """Test that forecast maintains reasonable positive values"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    future = forecast[forecast['ds'] > sample_price_data.index[-1]]
    # All forecast values should be positive (stock prices can't be negative)
    assert all(future['yhat'] > 0)
    assert all(future['yhat_lower'] > 0)


@pytest.mark.unit
def test_get_fast_forecast_continuous_dates(sample_price_data):
    """Test that forecast dates are continuous without gaps"""
    model, forecast = get_fast_forecast(sample_price_data, weeks_to_forecast=4)

    future = forecast[forecast['ds'] > sample_price_data.index[-1]]
    date_diffs = future['ds'].diff().dropna()

    # All date differences should be exactly 1 day
    assert all(date_diffs == pd.Timedelta(days=1))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
