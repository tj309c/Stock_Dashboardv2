import streamlit as st
from prophet import Prophet

@st.cache_data(ttl=86400)
def get_prophet_forecast(price_data, weeks_to_forecast):
    prophet_df = price_data.reset_index()
    prophet_df = prophet_df[['Date', 'Close']]
    prophet_df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
    prophet_df['ds'] = prophet_df['ds'].dt.tz_localize(None)
    model = Prophet(weekly_seasonality=True, yearly_seasonality=True, daily_seasonality=False)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=weeks_to_forecast * 7)
    forecast = model.predict(future)
    return model, forecast