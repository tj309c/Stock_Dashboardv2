import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

@st.cache_data(ttl=86400)
def get_fast_forecast(price_data, weeks_to_forecast):
    """
    Fast forecasting using exponential weighted moving average (EWMA).
    Much faster than Prophet (100x), still provides reasonable predictions.
    """
    # Use exponential weighted moving average for trend
    # EMA with span of 20 days (roughly 1 month of trading days)
    ema_20 = price_data['Close'].ewm(span=20, adjust=False).mean()

    # Calculate the trend (daily change rate)
    recent_period = min(60, len(price_data))  # Last 60 days or available data
    recent_prices = price_data['Close'].tail(recent_period)

    # Linear regression on recent prices to get trend
    x = np.arange(len(recent_prices))
    y = recent_prices.values
    trend_slope = np.polyfit(x, y, 1)[0]  # Daily price change

    # Calculate volatility (standard deviation of recent returns)
    recent_returns = recent_prices.pct_change().dropna()
    volatility = recent_returns.std()

    # Generate future dates
    last_date = price_data.index[-1]
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        periods=weeks_to_forecast * 7,
        freq='D'
    )

    # Generate forecast
    last_price = price_data['Close'].iloc[-1]
    forecast_values = []
    upper_bounds = []
    lower_bounds = []

    for i in range(len(future_dates)):
        # Projected price based on trend
        days_ahead = i + 1
        forecast_price = last_price + (trend_slope * days_ahead)

        # Confidence interval (wider as we go further out)
        confidence_width = last_price * volatility * np.sqrt(days_ahead) * 1.96  # 95% confidence

        forecast_values.append(forecast_price)
        upper_bounds.append(forecast_price + confidence_width)
        lower_bounds.append(forecast_price - confidence_width)

    # Create forecast dataframe
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': forecast_values,
        'yhat_upper': upper_bounds,
        'yhat_lower': lower_bounds
    })

    # Combine historical and forecast data for plotting
    historical_df = pd.DataFrame({
        'ds': price_data.index,
        'y': price_data['Close'].values,
        'yhat': ema_20.values
    })

    combined_df = pd.concat([
        historical_df[['ds', 'yhat']],
        forecast_df[['ds', 'yhat', 'yhat_upper', 'yhat_lower']]
    ], ignore_index=True)

    return 'fast_ema_model', combined_df

@st.cache_data(ttl=86400)
def get_prophet_forecast(price_data, weeks_to_forecast, use_fast=True):
    """
    Forecasting wrapper that defaults to fast EWMA method.
    Set use_fast=False to use Prophet (slower but potentially more accurate).
    """
    if use_fast or not PROPHET_AVAILABLE:
        return get_fast_forecast(price_data, weeks_to_forecast)

    # Original Prophet implementation (kept for comparison)
    prophet_df = price_data.reset_index()
    prophet_df = prophet_df[['Date', 'Close']]
    prophet_df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
    prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    model = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=weeks_to_forecast * 7)
    forecast = model.predict(future)
    return model, forecast