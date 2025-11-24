import streamlit as st
import pandas as pd
from app_logic import initialize_data_and_context
from app_utils import plotly_full_width, display_dataframe_full_width
from mode_config import render_mode_info, should_show_feature

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
    st.caption("Risk analysis, volatility metrics, and long-term forecasting models")

    # Display current trading mode
    render_mode_info()

    ticker = st.query_params.get("ticker", "AAPL")

    # Create tabs for the three sections
    if ADVANCED_ML_AVAILABLE:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Risk Analysis",
            "🤖 Advanced ML Models",
            "🔮 Forecasting & Predictions",
            "🔧 Debug"
        ])
    else:
        tab1, tab3, tab4 = st.tabs([
            "📊 Risk Analysis",
            "🔮 Forecasting & Predictions",
            "🔧 Debug"
        ])
        tab2 = None

    with tab1:
        render_risk_analysis_tab(ticker)

    if tab2 is not None:
        with tab2:
            render_advanced_ml_tab(ticker)

    with tab3:
        render_forecasting_tab(ticker)

    with tab4:
        render_debug_tab_risk(ticker)


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

                plotly_full_width(fig)

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


# ========================================
# DEBUG TAB
# ========================================

def render_debug_tab_risk(ticker):
    """Debug tab for Risk & Forecasting page"""
    st.markdown("### 🔧 Risk & Forecasting Debug Panel")

    st.info("""
    **Purpose**: Diagnose risk calculation data, forecasting model availability, and ML model status.
    """)

    # Section 1: Session State Variables
    with st.expander("📦 Session State Variables", expanded=False):
        st.markdown("**Current session state keys and values:**")
        if st.session_state:
            state_dict = {k: str(v)[:200] for k, v in st.session_state.items()}
            st.json(state_dict)
        else:
            st.write("No session state variables found")

    # Section 2: Risk Calculation Data Quality
    with st.expander("📊 Risk Calculation Data Quality", expanded=True):
        st.markdown(f"**Checking risk metrics data for {ticker}:**")

        ctx = initialize_data_and_context(ticker, light_load=True)
        info = ctx.info if ctx and ctx.info else {}

        # Define critical risk data points
        checks = {
            "Beta": info.get('beta') is not None,
            "52 Week High": info.get('fiftyTwoWeekHigh') is not None,
            "52 Week Low": info.get('fiftyTwoWeekLow') is not None,
            "Current Price": info.get('currentPrice') or info.get('regularMarketPrice'),
            "Price Data Available": ctx.price_data is not None and not ctx.price_data.empty if ctx else False,
            "Sufficient History": len(ctx.price_data) >= 30 if ctx and ctx.price_data is not None and not ctx.price_data.empty else False
        }

        # Display check results
        for check_name, passed in checks.items():
            st.markdown(f"{'✅' if passed else '❌'} {check_name}")

        # Display actual values
        st.markdown("---")
        st.markdown("**Risk Metrics:**")
        col1, col2 = st.columns(2)
        with col1:
            beta = info.get('beta', 'N/A')
            st.metric("Beta", f"{beta:.2f}" if isinstance(beta, (int, float)) else "N/A")
            st.metric("52W High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}" if info.get('fiftyTwoWeekHigh') else "N/A")
            st.metric("52W Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}" if info.get('fiftyTwoWeekLow') else "N/A")
        with col2:
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                st.metric("Price Data Points", len(ctx.price_data))
                volatility = ctx.price_data['Close'].pct_change().std() * 100
                st.metric("Historical Volatility", f"{volatility:.2f}%")

        completeness_score = sum(checks.values())
        total_checks = len(checks)
        completeness_pct = (completeness_score / total_checks) * 100

        st.markdown("---")
        st.metric("Risk Data Completeness", f"{completeness_pct:.0f}%")

        if completeness_pct < 60:
            st.error("❌ Critical risk data is missing. Risk calculations may be unreliable.")
        elif completeness_pct < 80:
            st.warning("⚠️ Some risk data is missing. Results may be incomplete.")
        else:
            st.success("✅ Risk data is comprehensive!")

    # Section 3: Forecasting Models Status
    with st.expander("🔮 Forecasting Models Status", expanded=True):
        st.markdown("**Checking forecasting model availability:**")

        st.markdown(f"**Prophet Model**: {'✅ Available' if PROPHET_AVAILABLE else '❌ Not Installed'}")
        if not PROPHET_AVAILABLE:
            st.warning("Install Prophet with: `pip install prophet`")

        st.markdown(f"**Advanced ML Models**: {'✅ Available' if ADVANCED_ML_AVAILABLE else '❌ Not Available'}")
        if not ADVANCED_ML_AVAILABLE:
            st.info("Advanced ML models module not found. This is optional.")

        # Check if data is suitable for forecasting
        if PROPHET_AVAILABLE:
            st.markdown("---")
            st.markdown("**Data Quality for Forecasting:**")

            ctx = initialize_data_and_context(ticker)
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                data_points = len(ctx.price_data)
                has_volume = 'Volume' in ctx.price_data.columns
                has_close = 'Close' in ctx.price_data.columns

                st.markdown(f"{'✅' if data_points >= 365 else '⚠️'} Data Points: {data_points} (minimum 365 recommended)")
                st.markdown(f"{'✅' if has_close else '❌'} Has Close Price")
                st.markdown(f"{'✅' if has_volume else '❌'} Has Volume Data")

                if data_points < 100:
                    st.error("❌ Insufficient data for reliable forecasting. Need at least 100 data points.")
                elif data_points < 365:
                    st.warning("⚠️ Limited historical data. Forecasts may be less reliable. Recommend at least 1 year of data.")
                else:
                    st.success("✅ Sufficient historical data for forecasting!")
            else:
                st.error("❌ No price data available for forecasting")

    # Section 4: Price Data Statistics
    with st.expander("📈 Price Data Statistics", expanded=False):
        st.markdown("**Historical price data analysis:**")

        ctx = initialize_data_and_context(ticker)
        if ctx and ctx.price_data is not None and not ctx.price_data.empty:
            df = ctx.price_data

            st.markdown("**Basic Statistics:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Days", len(df))
                st.metric("Date Range", f"{df.index[0].date()} to {df.index[-1].date()}")
            with col2:
                st.metric("Mean Price", f"${df['Close'].mean():.2f}")
                st.metric("Std Dev", f"${df['Close'].std():.2f}")
            with col3:
                st.metric("Min Price", f"${df['Close'].min():.2f}")
                st.metric("Max Price", f"${df['Close'].max():.2f}")

            st.markdown("---")
            st.markdown("**Return Statistics:**")
            returns = df['Close'].pct_change().dropna()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Daily Return", f"{returns.mean() * 100:.3f}%")
            with col2:
                st.metric("Daily Volatility", f"{returns.std() * 100:.2f}%")
            with col3:
                st.metric("Sharpe Ratio (approx)", f"{(returns.mean() / returns.std() * (252**0.5)):.2f}")

            # Check for data quality issues
            st.markdown("---")
            st.markdown("**Data Quality Checks:**")
            missing_values = df.isnull().sum().sum()
            zero_volume_days = (df['Volume'] == 0).sum() if 'Volume' in df.columns else 0

            st.markdown(f"{'✅' if missing_values == 0 else '⚠️'} Missing Values: {missing_values}")
            st.markdown(f"{'✅' if zero_volume_days < len(df) * 0.05 else '⚠️'} Zero Volume Days: {zero_volume_days} ({zero_volume_days/len(df)*100:.1f}%)")
        else:
            st.error("❌ No price data available")

    # Section 5: Cache Status
    with st.expander("💾 Cache Status", expanded=False):
        st.markdown("**Streamlit cache information:**")

        st.markdown("""
        **Cached functions in this page:**
        - `initialize_data_and_context()` - Ticker data loader
        - `get_prophet_forecast()` - Prophet forecasting (if available)
        - `render_advanced_ml_analysis()` - ML models (if available)

        **Note**: Cache is automatically managed by Streamlit with TTL (Time-To-Live).
        """)

        if st.button("🗑️ Clear All Caches", key="clear_cache_risk"):
            st.cache_data.clear()
            st.success("✅ All caches cleared! Refresh the page to reload data.")

    # Section 6: Performance Metrics
    with st.expander("⚡ Performance Metrics", expanded=False):
        st.markdown("**Data loading and model performance:**")

        import time

        # Test ticker data fetch
        start = time.time()
        try:
            test_ctx = initialize_data_and_context(ticker, light_load=True)
            load_time = time.time() - start
            load_status = '✅' if test_ctx else '❌'
        except Exception as e:
            load_time = time.time() - start
            load_status = f'❌ Error: {str(e)[:50]}'

        st.metric("Ticker Data Load", f"{load_time:.2f}s", delta=load_status)

        # Test Prophet forecast if available
        if PROPHET_AVAILABLE:
            start = time.time()
            try:
                test_ctx = initialize_data_and_context(ticker)
                model, forecast = get_prophet_forecast(test_ctx.price_data, weeks_ahead=4)
                forecast_time = time.time() - start
                forecast_status = '✅' if forecast is not None else '❌'
            except Exception as e:
                forecast_time = time.time() - start
                forecast_status = f'❌ Error: {str(e)[:50]}'

            st.metric("Prophet Forecast (4w)", f"{forecast_time:.2f}s", delta=forecast_status)

        if load_time > 5:
            st.warning("⚠️ Data loading is slow. Consider checking API connectivity.")

    # Section 7: Raw Data Inspector
    with st.expander("🔍 Raw Data Inspector", expanded=False):
        st.markdown("**Inspect raw data structures:**")

        ctx = initialize_data_and_context(ticker)

        data_source = st.selectbox(
            "Select data source to inspect:",
            ["Company Info (Risk Metrics)", "Price Data (OHLCV)", "Returns Distribution"],
            key="data_inspector_risk"
        )

        if data_source == "Company Info (Risk Metrics)":
            if ctx and ctx.info:
                risk_data = {
                    'beta': ctx.info.get('beta'),
                    'fiftyTwoWeekHigh': ctx.info.get('fiftyTwoWeekHigh'),
                    'fiftyTwoWeekLow': ctx.info.get('fiftyTwoWeekLow'),
                    'currentPrice': ctx.info.get('currentPrice'),
                    'regularMarketPrice': ctx.info.get('regularMarketPrice'),
                    'trailingPE': ctx.info.get('trailingPE'),
                    'forwardPE': ctx.info.get('forwardPE'),
                    'averageVolume': ctx.info.get('averageVolume'),
                    'marketCap': ctx.info.get('marketCap')
                }
                st.json(risk_data)
            else:
                st.error("No company info available")

        elif data_source == "Price Data (OHLCV)":
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                display_dataframe_full_width(ctx.price_data.tail(30))
            else:
                st.error("No price data available")

        elif data_source == "Returns Distribution":
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                import plotly.graph_objects as go
                returns = ctx.price_data['Close'].pct_change().dropna() * 100

                fig = go.Figure()
                fig.add_trace(go.Histogram(x=returns, nbinsx=50, name='Daily Returns'))
                fig.update_layout(
                    title="Daily Returns Distribution",
                    xaxis_title="Return (%)",
                    yaxis_title="Frequency",
                    template="plotly_white"
                )
                plotly_full_width(fig)

                st.markdown("**Statistics:**")
                st.write(returns.describe())
            else:
                st.error("No price data available")


if __name__ == "__main__":
    render_page()
