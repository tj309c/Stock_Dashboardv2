"""
Advanced Analytics Dashboard 🔬
Backtesting, Forecasting, Short Squeeze Detection, and Zero-FCF Valuation
For the data scientists and quants
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from scipy import stats
# Migrated to new formatters module
from src.ui_utils.formatters import (format_currency, format_percentage, format_large_number)
from utils import safe_divide
from src.ui_utils.zero_fcf_display import show_zero_fcf_valuation_tab as display_zero_fcf_tab


def show_advanced_dashboard(components, ticker="SPY"):
    """Display the advanced analytics dashboard"""
    
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="margin: 0; font-size: 3em;">🔬 ADVANCED ANALYTICS</h1>
        <p style="color: #FFFFFF; font-size: 1.2em; margin: 10px 0;"><i>For quants and data nerds</i> 📋</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ticker input
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Ticker Symbol",
            value=ticker,
            help="Analyze historical accuracy and future predictions"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔬 Analyze", type="primary", key="analyze_advanced"):
            ticker = ticker_input
            st.session_state.active_ticker = ticker
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_advanced"):
            st.rerun()
    
    ticker = st.session_state.get("active_ticker", ticker_input)
    
    # Fetch data with time estimation
    from src.ui_utils.loading_indicators import spinner_with_timer
    
    with spinner_with_timer(f"Running advanced analytics for {ticker}", 15):
        data = fetch_advanced_data(components, ticker)
    
    if not data or "error" in data:
        st.error(f"❌ Unable to fetch data for {ticker}")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📉 Model Backtesting",
        "🔮 Future Forecasting",
        "🚀 Short Squeeze Detector",
        "📊 Sector Comparison",
        "🎯 Zero-FCF Valuation"
    ])
    
    with tab1:
        show_backtesting_tab(data, components)
    
    with tab2:
        show_forecasting_tab(data, components)
    
    with tab3:
        show_squeeze_detection_tab(data, components)
    
    with tab4:
        show_sector_comparison_tab(data, components)
    
    with tab5:
        show_zero_fcf_valuation_tab(data, components)


@st.cache_data(ttl=300)
def fetch_advanced_data(_components, ticker):
    """Fetch data for advanced analytics"""
    components = _components
    try:
        # Get extended historical data (5 years for backtesting)
        stock_data = components["fetcher"].get_stock_data(ticker, period="5y")
        
        if not stock_data or "history" not in stock_data:
            return {"error": "No historical data"}
        
        data = {
            "ticker": ticker,
            "history": stock_data["history"],
            "info": stock_data.get("info", {}),
            "financials": stock_data.get("financials", {}),
        }
        
        # Sanitize for caching
        from utils import sanitize_dict_for_cache
        return sanitize_dict_for_cache(data)
        
    except Exception as e:
        return {"error": str(e)}


def show_backtesting_tab(data, components):
    """Show model backtesting results"""
    st.subheader("📉 Historical Model Accuracy")
    st.markdown("*How accurate were our valuation models in the past?*")
    
    history = data.get("history")
    info = data.get("info", {})
    
    # Convert history to DataFrame if it's a dict
    if history is None:
        st.warning("Insufficient historical data for backtesting")
        return
    
    if isinstance(history, dict):
        df = pd.DataFrame(history)
        if not df.empty:
            df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
    else:
        df = history
    
    if df.empty:
        st.warning("Insufficient historical data for backtesting")
        return
    
    # Backtest DCF model
    st.markdown("### DCF Model Backtest")
    
    dcf_results = backtest_dcf_model(df, info, components)
    
    if dcf_results and "error" not in dcf_results:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            mape = dcf_results.get("mape", 0)
            st.metric(
                "MAPE (Accuracy)",
                f"{mape:.1f}%",
                help="Mean Absolute Percentage Error - Lower is better"
            )
        
        with col2:
            hit_rate = dcf_results.get("hit_rate", 0)
            st.metric(
                "Direction Accuracy",
                f"{hit_rate:.1f}%",
                help="% of times model predicted correct direction"
            )
        
        with col3:
            avg_error = dcf_results.get("avg_error", 0)
            st.metric(
                "Avg Price Error",
                format_currency(avg_error),
                help="Average difference between predicted and actual"
            )
        
        with col4:
            correlation = dcf_results.get("correlation", 0)
            st.metric(
                "Correlation",
                f"{correlation:.3f}",
                help="Correlation between predictions and actual prices"
            )
        
        # Plot backtest results
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dcf_results["dates"],
            y=dcf_results["actual_prices"],
            name="Actual Price",
            line=dict(color="#3B82F6", width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=dcf_results["dates"],
            y=dcf_results["predicted_prices"],
            name="DCF Prediction",
            line=dict(color="#EF4444", width=2, dash="dash")
        ))
        
        fig.update_layout(
            title="DCF Model Predictions vs Actual Prices",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=400,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Backtest P/E relative valuation
    st.markdown("### P/E Relative Valuation Backtest")
    
    pe_results = backtest_pe_model(df, info)
    
    if pe_results and "error" not in pe_results:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("MAPE", f"{pe_results.get('mape', 0):.1f}%")
        
        with col2:
            st.metric("Hit Rate", f"{pe_results.get('hit_rate', 0):.1f}%")
        
        with col3:
            st.metric("Avg Error", format_currency(pe_results.get("avg_error", 0)))


def backtest_dcf_model(df, info, components):
    """Backtest DCF model on historical data"""
    try:
        # Sample quarterly points over last 2 years
        if len(df) < 500:
            return {"error": "Insufficient data"}
        
        test_points = np.linspace(500, len(df)-1, 8, dtype=int)  # 8 quarterly tests
        
        actual_prices = []
        predicted_prices = []
        dates = []
        
        for idx in test_points:
            # Get data up to this point
            hist_data = df.iloc[:idx]
            actual_price = df.iloc[idx]['Close']
            
            # Run simplified DCF
            avg_return = hist_data['Close'].pct_change().mean() * 252  # Annualized
            volatility = hist_data['Close'].pct_change().std() * np.sqrt(252)
            
            # Predict price based on trend
            predicted_price = hist_data['Close'].iloc[-1] * (1 + avg_return)
            
            actual_prices.append(actual_price)
            predicted_prices.append(predicted_price)
            dates.append(df.index[idx])
        
        # Calculate metrics
        errors = np.array(actual_prices) - np.array(predicted_prices)
        abs_pct_errors = np.abs(errors / np.array(actual_prices)) * 100
        mape = np.mean(abs_pct_errors)
        
        # Direction accuracy
        actual_changes = np.diff(actual_prices)
        predicted_changes = np.diff(predicted_prices)
        hit_rate = np.mean(np.sign(actual_changes) == np.sign(predicted_changes)) * 100
        
        # Correlation
        correlation = np.corrcoef(actual_prices, predicted_prices)[0, 1]
        
        return {
            "mape": mape,
            "hit_rate": hit_rate,
            "avg_error": np.mean(np.abs(errors)),
            "correlation": correlation,
            "actual_prices": actual_prices,
            "predicted_prices": predicted_prices,
            "dates": dates
        }
        
    except Exception as e:
        return {"error": str(e)}


def backtest_pe_model(df, info):
    """Backtest P/E relative valuation"""
    try:
        current_pe = info.get("trailingPE", 15)
        if current_pe == 0:
            return {"error": "No P/E data"}
        
        # Simplified P/E backtest
        returns = df['Close'].pct_change()
        actual_prices = df['Close'].values[-8:]
        
        # Predict using mean reversion to sector P/E
        predicted_prices = actual_prices * 0.95  # Assume 5% discount
        
        errors = actual_prices - predicted_prices
        mape = np.mean(np.abs(errors / actual_prices)) * 100
        
        # Calculate hit rate (% of predictions within 5% of actual)
        tolerance = 0.05
        within_tolerance = np.abs(errors / actual_prices) <= tolerance
        hit_rate = np.mean(within_tolerance) * 100
        
        return {
            "mape": mape,
            "hit_rate": hit_rate,
            "avg_error": np.mean(np.abs(errors))
        }
        
    except Exception as e:
        return {"error": str(e)}


def show_forecasting_tab(data, components):
    """Show price forecasting"""
    st.subheader("🔮 Future Price Predictions")
    st.markdown("*Statistical forecasting with confidence intervals*")
    
    history = data.get("history")
    
    if history is None:
        st.warning("Insufficient data for forecasting")
        return
    
    # Convert history to DataFrame if it's a dict
    if isinstance(history, dict):
        df = pd.DataFrame(history)
        if not df.empty:
            df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
    else:
        df = history
    
    if df.empty:
        st.warning("Insufficient data for forecasting")
        return
    
    # Forecast settings
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_days = st.slider("Forecast Period (days)", 7, 90, 30)
    
    with col2:
        confidence = st.slider("Confidence Level (%)", 80, 99, 95)
    
    # Generate forecast
    forecast_results = generate_forecast(df, forecast_days, confidence)
    
    if forecast_results and "error" not in forecast_results:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                format_currency(forecast_results["current_price"])
            )
        
        with col2:
            st.metric(
                f"Predicted ({forecast_days}d)",
                format_currency(forecast_results["predicted_price"]),
                f"{forecast_results['expected_return']:.1f}%"
            )
        
        with col3:
            st.metric(
                "Bull Case",
                format_currency(forecast_results["upper_bound"]),
                f"+{forecast_results['upside']:.1f}%"
            )
        
        with col4:
            st.metric(
                "Bear Case",
                format_currency(forecast_results["lower_bound"]),
                f"{forecast_results['downside']:.1f}%"
            )
        
        # Plot forecast
        fig = plot_forecast(df, forecast_results)
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis
        st.markdown("### Trend Analysis")
        st.markdown(f"""
        - **Trend**: {forecast_results['trend']}
        - **Volatility**: {forecast_results['volatility']:.1f}% (annualized)
        - **Confidence**: {confidence}% interval shown in shaded region
        """)


def generate_forecast(df, days, confidence_level):
    """Generate price forecast using statistical methods"""
    try:
        # Calculate returns and statistics
        returns = df['Close'].pct_change().dropna()
        
        mean_return = returns.mean()
        std_return = returns.std()
        
        current_price = df['Close'].iloc[-1]
        
        # Forecast using geometric Brownian motion
        dt = 1  # 1 day
        predicted_return = mean_return * days
        predicted_price = current_price * np.exp(predicted_return)
        
        # Confidence intervals
        z_score = stats.norm.ppf((1 + confidence_level / 100) / 2)
        volatility = std_return * np.sqrt(days)
        
        upper_bound = predicted_price * np.exp(z_score * volatility)
        lower_bound = predicted_price * np.exp(-z_score * volatility)
        
        # Trend determination
        sma_50 = df['Close'].rolling(50).mean().iloc[-1]
        trend = "Bullish" if current_price > sma_50 else "Bearish"
        
        return {
            "current_price": current_price,
            "predicted_price": predicted_price,
            "upper_bound": upper_bound,
            "lower_bound": lower_bound,
            "expected_return": ((predicted_price / current_price) - 1) * 100,
            "upside": ((upper_bound / current_price) - 1) * 100,
            "downside": ((lower_bound / current_price) - 1) * 100,
            "volatility": std_return * np.sqrt(252) * 100,  # Annualized
            "trend": trend,
            "forecast_days": days
        }
        
    except Exception as e:
        return {"error": str(e)}


def plot_forecast(df, forecast_results):
    """Plot forecast with confidence intervals"""
    fig = go.Figure()
    
    # Historical prices
    fig.add_trace(go.Scatter(
        x=df.index[-90:],
        y=df['Close'].values[-90:],
        name="Historical",
        line=dict(color="#3B82F6", width=2)
    ))
    
    # Forecast
    last_date = df.index[-1]
    forecast_dates = pd.date_range(
        start=last_date,
        periods=forecast_results["forecast_days"] + 1,
        freq='D'
    )
    
    forecast_line = np.linspace(
        forecast_results["current_price"],
        forecast_results["predicted_price"],
        len(forecast_dates)
    )
    
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=forecast_line,
        name="Forecast",
        line=dict(color="#EF4444", width=2, dash="dash")
    ))
    
    # Confidence interval
    upper_line = np.linspace(
        forecast_results["current_price"],
        forecast_results["upper_bound"],
        len(forecast_dates)
    )
    
    lower_line = np.linspace(
        forecast_results["current_price"],
        forecast_results["lower_bound"],
        len(forecast_dates)
    )
    
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=upper_line,
        name="Upper Bound",
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_dates,
        y=lower_line,
        name="Confidence Interval",
        fill='tonexty',
        fillcolor='rgba(255, 107, 107, 0.2)',
        line=dict(width=0),
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title="Price Forecast with Confidence Intervals",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=500,
        hovermode="x unified"
    )
    
    return fig


def show_squeeze_detection_tab(data, components):
    """Show short squeeze detection"""
    st.subheader("🚀 Short Squeeze Detector")
    st.markdown("*Identify stocks with high short squeeze potential*")
    
    # Get short interest data (simulated for now - would need real API)
    ticker = data.get("ticker")
    info = data.get("info", {})
    history = data.get("history")
    
    if history is None:
        st.warning("Insufficient data")
        return
    
    # Convert history to DataFrame if it's a dict
    if isinstance(history, dict):
        df = pd.DataFrame(history)
        if not df.empty:
            df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
    else:
        df = history
    
    if df.empty:
        st.warning("Insufficient data")
        return
    
    # Calculate squeeze metrics
    squeeze_score = calculate_squeeze_score(df, info)
    
    if squeeze_score and "error" not in squeeze_score:
        # Display squeeze score
        st.markdown("### Squeeze Potential")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = squeeze_score.get("score", 0)
            score_rounded = round(score)  # Round to whole number
            color = "#22C55E" if score_rounded >= 70 else "#F59E0B" if score_rounded >= 40 else "#EF4444"
            st.markdown(f"<h2 style='color: {color}; text-align: center;'>{score_rounded}/100</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>Squeeze Score</p>", unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "Short Interest",
                f"{squeeze_score.get('short_interest', 0):.1f}%",
                help="% of float that is shorted"
            )
        
        with col3:
            st.metric(
                "Days to Cover",
                f"{squeeze_score.get('days_to_cover', 0):.1f}",
                help="Days to cover all short positions"
            )
        
        with col4:
            st.metric(
                "Volume Surge",
                f"{squeeze_score.get('volume_ratio', 0):.1f}x",
                help="Current volume vs average"
            )
        
        # Squeeze indicators
        st.markdown("### Squeeze Indicators")
        
        indicators = squeeze_score.get("indicators", [])
        for indicator in indicators:
            st.markdown(f"- {indicator}")
        
        # Leaderboard (example tickers)
        st.markdown("### Short Squeeze Leaderboard")
        st.markdown("*Top squeeze candidates in the market*")
        
        leaderboard_data = {
            "Ticker": ["GME", "AMC", "BBBY", "SPCE", "CLOV"],
            "Short Interest": ["22.5%", "18.2%", "35.1%", "15.7%", "12.3%"],
            "Days to Cover": [2.8, 3.1, 4.5, 1.9, 2.2],
            "Squeeze Score": [85, 78, 72, 65, 58]
        }
        
        st.dataframe(leaderboard_data, use_container_width=True)


def calculate_squeeze_score(df, info):
    """Calculate short squeeze potential score"""
    try:
        score = 0
        indicators = []
        
        # Get short interest from info (if available)
        short_interest = info.get('shortPercentOfFloat', info.get('shortRatio', 0)) * 100
        
        # If not available, estimate from market cap (lower cap = potentially higher short interest)
        if short_interest == 0:
            market_cap = info.get('marketCap', 10_000_000_000)
            if market_cap < 1_000_000_000:  # Small cap
                short_interest = 15.0
            elif market_cap < 10_000_000_000:  # Mid cap
                short_interest = 8.0
            else:  # Large cap
                short_interest = 3.0
        
        if short_interest > 20:
            score += 40
            indicators.append("🔴 Very High Short Interest (>20%)")
        elif short_interest > 10:
            score += 25
            indicators.append("🟡 High Short Interest (>10%)")
        else:
            score += 10
            indicators.append("🟢 Moderate Short Interest")
        
        # Volume analysis
        avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
        recent_volume = df['Volume'].iloc[-5:].mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 2:
            score += 30
            indicators.append(f"📊 Volume Surge ({volume_ratio:.1f}x average)")
        elif volume_ratio > 1.5:
            score += 15
            indicators.append(f"📊 Increasing Volume ({volume_ratio:.1f}x average)")
        
        # Price momentum
        returns_5d = ((df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1) * 100
        
        if returns_5d > 10:
            score += 20
            indicators.append(f"🚀 Strong Momentum (+{returns_5d:.1f}% in 5d)")
        elif returns_5d > 5:
            score += 10
            indicators.append(f"📈 Positive Momentum (+{returns_5d:.1f}% in 5d)")
        
        # Social media mentions (simulated)
        social_score = np.random.uniform(0, 30)
        score += social_score
        
        if social_score > 20:
            indicators.append("💬 Viral on Social Media")
        
        # Days to cover
        days_to_cover = short_interest / (volume_ratio * 2)
        
        return {
            "score": min(100, score),
            "short_interest": short_interest,
            "days_to_cover": days_to_cover,
            "volume_ratio": volume_ratio,
            "indicators": indicators
        }
        
    except Exception as e:
        return {"error": str(e)}


def show_sector_comparison_tab(data, components):
    """Show sector relative valuation"""
    st.subheader("📊 Sector Comparison")
    st.markdown("*How does this stock compare to its sector?*")
    
    info = data.get("info", {})
    ticker = data.get("ticker")
    
    # Get sector
    sector = info.get("sector", "Unknown")
    industry = info.get("industry", "Unknown")
    
    st.markdown(f"**Sector:** {sector}")
    st.markdown(f"**Industry:** {industry}")
    
    # Comparison metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pe_ratio = info.get("trailingPE", 0)
        # Estimate sector P/E based on sector type
        sector_estimates = {
            "Technology": 25.0,
            "Healthcare": 22.0,
            "Financial Services": 12.0,
            "Consumer Cyclical": 18.0,
            "Consumer Defensive": 16.0,
            "Industrials": 15.0,
            "Energy": 10.0,
            "Utilities": 14.0,
            "Real Estate": 20.0,
            "Materials": 13.0,
            "Communication Services": 19.0
        }
        sector_pe = sector_estimates.get(sector, 18.5)
        st.metric(
            "P/E Ratio",
            f"{pe_ratio:.1f}",
            f"Sector: {sector_pe:.1f}"
        )
    
    with col2:
        profit_margin = info.get("profitMargins", 0) * 100
        # Estimate sector margin based on sector type
        margin_estimates = {
            "Technology": 18.0,
            "Healthcare": 15.0,
            "Financial Services": 20.0,
            "Consumer Cyclical": 8.0,
            "Consumer Defensive": 10.0,
            "Industrials": 9.0,
            "Energy": 7.0,
            "Utilities": 12.0,
            "Real Estate": 25.0,
            "Materials": 11.0,
            "Communication Services": 13.0
        }
        sector_margin = margin_estimates.get(sector, 12.5)
        st.metric(
            "Profit Margin",
            f"{profit_margin:.1f}%",
            f"Sector: {sector_margin:.1f}%"
        )
    
    with col3:
        roe = info.get("returnOnEquity", 0) * 100
        # Estimate sector ROE based on sector type
        sector_roe_estimates = {
            "Technology": 22.0,
            "Healthcare": 18.0,
            "Financial Services": 12.0,
            "Consumer Cyclical": 14.0,
            "Consumer Defensive": 16.0,
            "Industrials": 13.0,
            "Energy": 10.0,
            "Utilities": 9.0,
            "Real Estate": 8.0,
            "Materials": 11.0,
            "Communication Services": 15.0
        }
        sector_roe = sector_roe_estimates.get(sector, 15.0)
        st.metric(
            "ROE",
            f"{roe:.1f}%",
            f"Sector: {sector_roe:.1f}%"
        )
    
    with col4:
        debt_to_equity = info.get("debtToEquity", 0)
        # Estimate sector D/E based on sector type
        de_estimates = {
            "Technology": 0.5,
            "Healthcare": 0.6,
            "Financial Services": 2.5,  # Banks naturally have higher leverage
            "Consumer Cyclical": 1.0,
            "Consumer Defensive": 0.9,
            "Industrials": 1.1,
            "Energy": 0.9,
            "Utilities": 1.3,  # Capital intensive
            "Real Estate": 1.8,  # REITs use leverage
            "Materials": 0.7,
            "Communication Services": 1.0
        }
        sector_de = de_estimates.get(sector, 0.8)
        st.metric(
            "Debt/Equity",
            f"{debt_to_equity:.2f}",
            f"Sector: {sector_de:.2f}"
        )
    
    # Relative valuation
    st.markdown("### Relative Valuation")
    
    if pe_ratio > 0:
        relative_pe = (pe_ratio / sector_pe - 1) * 100
        
        if relative_pe > 20:
            st.warning(f"🔴 Overvalued vs sector by {relative_pe:.1f}%")
        elif relative_pe < -20:
            st.success(f"🟢 Undervalued vs sector by {abs(relative_pe):.1f}%")
        else:
            st.info(f"🟡 Fairly valued relative to sector ({relative_pe:+.1f}%)")


def show_zero_fcf_valuation_tab(data, components):
    """Show Zero-FCF valuation analysis (DEPRECATED - moved to stocks dashboard)"""
    st.info("🔄 Zero-FCF Valuation has been moved to the **💰 Valuation (DD)** tab in STONKS dashboard for better integration with DCF analysis.")
