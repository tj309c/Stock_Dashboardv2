import streamlit as st
import pandas as pd
from app_logic import initialize_data_and_context

# Optional import for prophet
try:
    from prophet.plot import plot_plotly
    from forecasting import get_prophet_forecast
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Optional import for advanced ML models
try:
    from advanced_ml_models import render_advanced_ml_analysis
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False

def render_page():
    """Consolidated Risk & Forecasting Dashboard"""
    st.title("🎲 Risk & Forecasting")

    ticker = st.query_params.get("ticker", "AAPL")

    # Create tabs for the three sections
    if ADVANCED_ML_AVAILABLE:
        tab1, tab2, tab3 = st.tabs([
            "📊 Risk Analysis",
            "🤖 Advanced ML Models",
            "🔮 Forecasting & Predictions"
        ])
    else:
        tab1, tab3 = st.tabs([
            "📊 Risk Analysis",
            "🔮 Forecasting & Predictions"
        ])
        tab2 = None

    with tab1:
        render_risk_analysis_tab(ticker)

    if tab2 is not None:
        with tab2:
            render_advanced_ml_tab(ticker)

    with tab3:
        render_forecasting_tab(ticker)


def render_risk_analysis_tab(ticker):
    """Risk metrics and analysis"""
    st.subheader(f"Risk Analysis for {ticker}")

    ctx = initialize_data_and_context(ticker, light_load=True)

    if not ctx or not ctx.info or ctx.price_data.empty:
        st.error(f"Could not load data for '{ticker}'.")
        st.stop()

    st.info("🚧 Comprehensive risk analysis coming soon! This will include volatility metrics, downside risk, correlation analysis, and more.")

    # Display basic risk metrics for now
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Volatility")
        beta = ctx.info.get('beta', 'N/A')
        st.metric("Beta", f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A")

        # Calculate simple volatility from price data
        if not ctx.price_data.empty and len(ctx.price_data) > 1:
            returns = ctx.price_data['Close'].pct_change()
            volatility = returns.std() * (252 ** 0.5)  # Annualized
            st.metric("Annualized Volatility", f"{volatility * 100:.2f}%")
        else:
            st.metric("Annualized Volatility", "N/A")

    with col2:
        st.markdown("#### Price Range")
        fifty_two_week_high = ctx.info.get('fiftyTwoWeekHigh', 'N/A')
        fifty_two_week_low = ctx.info.get('fiftyTwoWeekLow', 'N/A')
        st.metric("52-Week High", f"${fifty_two_week_high:.2f}" if isinstance(fifty_two_week_high, (int, float)) else "N/A")
        st.metric("52-Week Low", f"${fifty_two_week_low:.2f}" if isinstance(fifty_two_week_low, (int, float)) else "N/A")

    with col3:
        st.markdown("#### Performance")
        if not ctx.price_data.empty and len(ctx.price_data) > 252:
            ytd_return = (ctx.price_data['Close'].iloc[-1] / ctx.price_data['Close'].iloc[-252] - 1) * 100
            st.metric("1Y Return", f"{ytd_return:+.2f}%")
        else:
            st.metric("1Y Return", "N/A")


def render_advanced_ml_tab(ticker):
    """Advanced ML models: HMMs and Kernel Methods"""
    st.subheader(f"Advanced ML Analysis for {ticker}")

    if not ADVANCED_ML_AVAILABLE:
        st.warning("⚠️ Advanced ML libraries not installed. To use these features, install them with:")
        st.code("pip install hmmlearn scikit-learn", language="bash")
        st.info("These are optional dependencies for advanced market regime detection and kernel-based predictions.")
        return

    ctx = initialize_data_and_context(ticker)

    if not ctx or ctx.price_data.empty:
        st.error(f"Could not load price data for '{ticker}'.")
        return

    # Render the advanced ML analysis from the module
    render_advanced_ml_analysis(ticker, ctx.price_data)


def render_forecasting_tab(ticker):
    """Future forecasting using Prophet"""
    st.subheader(f"Forecasting & Predictions for {ticker}")

    if not PROPHET_AVAILABLE:
        st.warning("⚠️ Prophet library not installed. To use forecasting features, install it with: `pip install prophet`")
        st.info("Prophet is an optional dependency for time-series forecasting. The rest of the application works without it.")
        return

    ctx = initialize_data_and_context(ticker)

    st.write("This model uses Facebook's Prophet time-series forecasting to predict future price movements, including a probabilistic range.")

    weeks_to_forecast = st.slider("Weeks to Forecast", 4, 104, 52)

    if st.button("Generate Forecast"):
        with st.spinner("Generating forecast..."):
            model, forecast = get_prophet_forecast(ctx.price_data, weeks_to_forecast, use_fast=True)

            if forecast is not None:
                st.success("Forecast generated successfully!")

                # Display the forecast plot
                if model == 'fast_ema_model':
                    # Use custom plotly chart for fast forecast
                    import plotly.graph_objects as go
                    fig = go.Figure()

                    # Historical data
                    historical = forecast[forecast['ds'] <= ctx.price_data.index[-1]]
                    fig.add_trace(go.Scatter(
                        x=historical['ds'],
                        y=historical['yhat'],
                        mode='lines',
                        name='Historical Trend',
                        line=dict(color='blue')
                    ))

                    # Forecast
                    future = forecast[forecast['ds'] > ctx.price_data.index[-1]]
                    fig.add_trace(go.Scatter(
                        x=future['ds'],
                        y=future['yhat'],
                        mode='lines',
                        name='Forecast',
                        line=dict(color='red', dash='dash')
                    ))

                    # Confidence interval
                    fig.add_trace(go.Scatter(
                        x=pd.concat([future['ds'], future['ds'][::-1]]),
                        y=pd.concat([future['yhat_upper'], future['yhat_lower'][::-1]]),
                        fill='toself',
                        fillcolor='rgba(255,0,0,0.1)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='95% Confidence'
                    ))

                    fig.update_layout(
                        title_text=f"{ticker} Price Forecast ({weeks_to_forecast} weeks)",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        template="plotly_white"
                    )
                else:
                    # Use Prophet's built-in plotting
                    fig = plot_plotly(model, forecast)
                    fig.update_layout(
                        title_text=f"{ticker} Price Forecast ({weeks_to_forecast} weeks)",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        template="plotly_white"
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Show forecast statistics
                st.subheader("Forecast Summary")
                col1, col2, col3 = st.columns(3)

                last_actual = ctx.price_data['Close'].iloc[-1]
                forecast_end = forecast['yhat'].iloc[-1]
                forecast_upper = forecast['yhat_upper'].iloc[-1]
                forecast_lower = forecast['yhat_lower'].iloc[-1]

                with col1:
                    st.metric("Current Price", f"${last_actual:.2f}")

                with col2:
                    change = ((forecast_end - last_actual) / last_actual) * 100
                    st.metric(f"Forecast ({weeks_to_forecast}w)", f"${forecast_end:.2f}", f"{change:+.1f}%")

                with col3:
                    range_text = f"${forecast_lower:.2f} - ${forecast_upper:.2f}"
                    st.metric("Confidence Range", range_text)

            else:
                st.error("Could not generate forecast. Please try different parameters or check data quality.")


if __name__ == "__main__":
    render_page()
