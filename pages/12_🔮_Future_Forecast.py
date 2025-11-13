import streamlit as st
from prophet.plot import plot_plotly
from app_logic import initialize_data_and_context
from forecasting import get_prophet_forecast

def render_page():
    """Main function to render the Future Forecast page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"🔮 Future Price Forecast for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
    st.write("This model uses Facebook's Prophet time-series forecasting to predict future price movements, including a probabilistic range.")
    
    weeks_to_forecast = st.slider("Weeks to Forecast", 4, 104, 52)

    if st.button("Generate Forecast"):
        with st.spinner("Running Prophet forecast... this may take a moment."):
            model, forecast = get_prophet_forecast(ctx.price_data, weeks_to_forecast)
            
            st.subheader("Forecasted Price Trend")
            fig1 = plot_plotly(model, forecast)
            fig1.update_layout(xaxis_title="Date", yaxis_title="Price", template="plotly_white")
            st.plotly_chart(fig1, use_container_width=True)
            
            st.subheader("Forecast Components")
            fig2 = model.plot_components(forecast)
            st.pyplot(fig2)

if __name__ == "__main__":
    render_page()