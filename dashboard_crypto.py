"""
Crypto Dashboard - Degen Mode 🚀
For HODLers and degens chasing 100x gains
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Migrated to new formatters module
from src.ui_utils.formatters import (format_currency, format_percentage, format_large_number)
from utils import safe_divide

def show_crypto_dashboard(components, ticker="BTC-USD"):
    """Display the crypto analysis dashboard"""
    
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="margin: 0; font-size: 3em;">🪙 CRYPTO CORNER</h1>
        <p style="color: #FFFFFF; font-size: 1.2em; margin: 10px 0;"><i>When Lambo? When Moon?</i> 🌙</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crypto selector
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        crypto_options = {
            "🟠 Bitcoin": "BTC-USD",
            "💠 Ethereum": "ETH-USD",
            "🔷 XRP": "XRP-USD",
            "💰 Solana": "SOL-USD",
            "🐶 Dogecoin": "DOGE-USD",
            "🌙 Cardano": "ADA-USD",
            "⚡ Polygon": "MATIC-USD",
            "🔗 Chainlink": "LINK-USD"
        }
        
        selected = st.selectbox(
            "Select Crypto",
            list(crypto_options.keys()),
            index=0
        )
        ticker = crypto_options[selected]
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Analyze", type="primary", key="analyze_crypto"):
            st.session_state.active_ticker = ticker
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_crypto"):
            st.rerun()
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        hodl_mode = st.checkbox("💎 HODL", value=True, help="Diamond Hands Mode")
    
    ticker = st.session_state.get("active_ticker", ticker)
    
    # Fetch data with progressive loading
    from src.ui_utils.loading_indicators import spinner_with_timer
    
    with spinner_with_timer(f"Loading {ticker.replace('-USD', '')} data", 10):
        data = fetch_crypto_data(components, ticker)
    
    if not data or "error" in data:
        st.error(f"❌ Unable to fetch data for {ticker}")
        return
    
    # Main overview
    show_crypto_overview(data, hodl_mode)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Price Action",
        "📈 Technical Analysis",
        "🌡️ Fear & Greed",
        "💰 HODL Calculator"
    ])
    
    with tab1:
        show_price_action_tab(data)
    
    with tab2:
        show_crypto_technical_tab(data, components)
    
    with tab3:
        show_fear_greed_tab(data)
    
    with tab4:
        show_hodl_calculator_tab(data)


@st.cache_data(ttl=300)
def fetch_crypto_data(_components, ticker):
    """Fetch crypto data with caching"""
    components = _components
    try:
        data = {
            "ticker": ticker,
            "stock_data": components["fetcher"].get_stock_data(ticker, period="1y"),
            "quote": components["fetcher"].get_realtime_quote(ticker),
        }
        
        # Process DataFrame
        if data["stock_data"] and "history" in data["stock_data"]:
            df = pd.DataFrame(data["stock_data"]["history"])
            if not df.empty:
                df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
                data["df"] = df
        
        # Get current price
        info = data["stock_data"].get("info", {}) if data["stock_data"] else {}
        data["current_price"] = info.get("currentPrice", info.get("regularMarketPrice", 0))
        
        # Sanitize all data for caching (fixes Timestamp errors)
        from utils import sanitize_dict_for_cache
        data = sanitize_dict_for_cache(data)
        
        return data
    except Exception as e:
        return {"error": str(e)}


def show_crypto_overview(data, hodl_mode=True):
    """Show crypto overview with key metrics"""
    
    st.markdown("---")
    
    current_price = data["current_price"]
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    df = data.get("df", pd.DataFrame())
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        prev_close = info.get('previousClose', current_price)
        price_change = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
        
        st.metric(
            "💰 Price",
            f"${current_price:,.2f}" if current_price > 100 else f"${current_price:.6f}",
            f"{price_change:.2f}%"
        )
    
    with col2:
        # 24h high/low
        day_high = info.get('dayHigh', current_price)
        day_low = info.get('dayLow', current_price)
        st.metric(
            "📊 24h High",
            f"${day_high:,.2f}" if day_high > 100 else f"${day_high:.6f}",
            ""
        )
    
    with col3:
        st.metric(
            "📉 24h Low",
            f"${day_low:,.2f}" if day_low > 100 else f"${day_low:.6f}",
            ""
        )
    
    with col4:
        # Market cap
        market_cap = info.get('marketCap', 0)
        if market_cap > 1e12:
            cap_str = f"${market_cap/1e12:.2f}T"
        elif market_cap > 1e9:
            cap_str = f"${market_cap/1e9:.2f}B"
        else:
            cap_str = f"${market_cap/1e6:.2f}M"
        
        st.metric("💎 Market Cap", cap_str, "")
    
    with col5:
        # Volume
        volume = info.get('volume', 0)
        if volume > 1e9:
            vol_str = f"${volume/1e9:.2f}B"
        else:
            vol_str = f"${volume/1e6:.2f}M"
        
        st.metric("📈 Volume", vol_str, "24h")
    
    # Price performance
    if not df.empty and len(df) > 7:
        st.markdown("### 📊 Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate returns
        price_7d = df['Close'].iloc[-7] if len(df) >= 7 else current_price
        price_30d = df['Close'].iloc[-30] if len(df) >= 30 else current_price
        price_90d = df['Close'].iloc[-90] if len(df) >= 90 else current_price
        price_365d = df['Close'].iloc[0] if len(df) >= 365 else current_price
        
        ret_7d = ((current_price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        ret_30d = ((current_price - price_30d) / price_30d * 100) if price_30d > 0 else 0
        ret_90d = ((current_price - price_90d) / price_90d * 100) if price_90d > 0 else 0
        ret_1y = ((current_price - price_365d) / price_365d * 100) if price_365d > 0 else 0
        
        with col1:
            emoji = "🚀" if ret_7d > 10 else "📈" if ret_7d > 0 else "📉"
            st.metric(f"{emoji} 7 Days", f"{ret_7d:+,.1f}%", "")
        
        with col2:
            emoji = "🚀" if ret_30d > 20 else "📈" if ret_30d > 0 else "📉"
            st.metric(f"{emoji} 30 Days", f"{ret_30d:+,.1f}%", "")
        
        with col3:
            emoji = "🚀" if ret_90d > 50 else "📈" if ret_90d > 0 else "📉"
            st.metric(f"{emoji} 90 Days", f"{ret_90d:+,.1f}%", "")
        
        with col4:
            emoji = "🌙" if ret_1y > 100 else "🚀" if ret_1y > 50 else "📈" if ret_1y > 0 else "📉"
            st.metric(f"{emoji} 1 Year", f"{ret_1y:+,.1f}%", "")
    
    # Hodl message
    if hodl_mode:
        if ret_1y > 100:
            st.success("💎🙌 DIAMOND HANDS PAID OFF! YOU'RE A LEGEND! 🚀🌙")
        elif ret_1y > 0:
            st.info("💎 Keep HODLing! Gains are gains! 📈")
        else:
            st.warning("🧻 No paper hands! Hold through the dip! This is the way! 💪")


def show_price_action_tab(data):
    """Show price charts"""
    st.subheader("📊 Price Action")
    
    df = data.get("df", pd.DataFrame())
    
    if df.empty:
        st.warning("No price data available")
        return
    
    # Time period selector
    period = st.selectbox(
        "Time Period",
        ["7D", "1M", "3M", "6M", "1Y", "ALL"],
        index=4
    )
    
    # Filter data based on period
    if period == "7D":
        df_filtered = df.tail(7)
    elif period == "1M":
        df_filtered = df.tail(30)
    elif period == "3M":
        df_filtered = df.tail(90)
    elif period == "6M":
        df_filtered = df.tail(180)
    elif period == "1Y":
        df_filtered = df.tail(365)
    else:
        df_filtered = df
    
    # Create chart
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.03
    )
    
    # Candlestick
    has_ohlc = all(col in df_filtered.columns for col in ['Open', 'High', 'Low', 'Close'])
    fig.add_trace(
        go.Candlestick(
            x=df_filtered.index,
            open=df_filtered['Open'] if has_ohlc else df_filtered['Close'],
            high=df_filtered['High'] if has_ohlc else df_filtered['Close'],
            low=df_filtered['Low'] if has_ohlc else df_filtered['Close'],
            close=df_filtered['Close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Add moving averages
    if len(df_filtered) >= 20:
        sma20 = df_filtered['Close'].rolling(20).mean()
        fig.add_trace(
            go.Scatter(x=df_filtered.index, y=sma20, name="SMA20", 
                      line=dict(color="#3B82F6", width=1)),
            row=1, col=1
        )
    
    # Volume
    if 'Volume' in df_filtered.columns:
        if 'Open' in df_filtered.columns:
            colors = ['red' if row['Close'] < row['Open'] else 'green' 
                     for idx, row in df_filtered.iterrows()]
        else:
            colors = ['blue'] * len(df_filtered)
        
        fig.add_trace(
            go.Bar(x=df_filtered.index, y=df_filtered['Volume'], 
                  name="Volume", marker_color=colors),
            row=2, col=1
        )
    
    fig.update_layout(
        title=f"{data['ticker'].replace('-USD', '')} - To The Moon! 🚀",
        yaxis_title="Price ($)",
        yaxis2_title="Volume",
        template="plotly_dark",
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # All-time high/low
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        
        ath = df['High'].max()
        atl = df['Low'].min()
        current = df['Close'].iloc[-1]
        
        with col1:
            st.metric("🏆 All-Time High", f"${ath:,.2f}", "")
        
        with col2:
            st.metric("💀 All-Time Low", f"${atl:.8f}", "")
        
        with col3:
            ath_diff = ((current - ath) / ath * 100) if ath > 0 else 0
            st.metric("📊 From ATH", f"{ath_diff:+,.1f}%", 
                     "Moon soon!" if ath_diff > -20 else "Accumulation phase" if ath_diff > -50 else "Buy the dip!")


def show_crypto_technical_tab(data, components):
    """Show technical analysis for crypto"""
    st.subheader("📈 Technical Analysis")
    
    df = data.get("df", pd.DataFrame())
    
    if df.empty or len(df) < 20:
        st.warning("Insufficient data for TA")
        return
    
    technical = components["technical"].analyze(df)
    
    if "error" in technical:
        st.error(f"TA Error: {technical['error']}")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # RSI
        rsi_val = technical.get("rsi", {}).get("value", 50)
        rsi_signal = technical.get("rsi", {}).get("signal", "neutral")
        
        st.markdown("### 🔥 RSI")
        
        if rsi_signal == "oversold":
            st.success(f"**{rsi_val:,.1f}** - OVERSOLD! Buy signal! 🚀")
        elif rsi_signal == "overbought":
            st.warning(f"**{rsi_val:,.1f}** - OVERBOUGHT! Take profits? 💰")
        else:
            st.info(f"**{rsi_val:,.1f}** - Neutral 📊")
    
    with col2:
        # MACD
        st.markdown("### 📊 MACD")
        macd_bull = technical.get("macd", {}).get("bullish", False)
        
        if macd_bull:
            st.success("**BULLISH** 🚀\nMomentum up!")
        else:
            st.warning("**BEARISH** 📉\nWait for reversal")
    
    with col3:
        # Trend
        st.markdown("### 📈 Trend")
        trend = technical.get("trend", "unknown")
        
        if "bullish" in trend:
            st.success(f"**{trend.upper()}** 🚀")
        elif "bearish" in trend:
            st.error(f"**{trend.upper()}** 📉")
        else:
            st.info(f"**{trend.upper()}** 📊")
    
    # Support and Resistance
    st.markdown("---")
    st.markdown("### 🎯 Key Levels")
    
    col1, col2 = st.columns(2)
    
    support = technical.get("support_resistance", {}).get("support", 0)
    resistance = technical.get("support_resistance", {}).get("resistance", 0)
    current_price = data["current_price"]
    
    with col1:
        st.markdown(f"#### 🛡️ Support: ${support:,.2f}")
        if current_price < support * 1.02:
            st.success("Near support! Good buy zone! 🎯")
    
    with col2:
        st.markdown(f"#### 🚧 Resistance: ${resistance:,.2f}")
        if current_price > resistance * 0.98:
            st.warning("Near resistance! Breakout or rejection? 🤔")


def show_fear_greed_tab(data):
    """Show fear & greed index (simplified)"""
    st.subheader("🌡️ Fear & Greed Index")
    
    # Calculate simple fear/greed from price action
    df = data.get("df", pd.DataFrame())
    
    if not df.empty and len(df) >= 30:
        # Use 30-day returns as proxy
        ret_30d = ((df['Close'].iloc[-1] - df['Close'].iloc[-30]) / df['Close'].iloc[-30] * 100)
        
        # Map to 0-100 scale
        if ret_30d > 50:
            score = 90  # Extreme Greed
            label = "EXTREME GREED"
            color = "#22C55E"
            emoji = "🤑"
        elif ret_30d > 20:
            score = 70  # Greed
            label = "GREED"
            color = "#3B82F6"
            emoji = "💰"
        elif ret_30d > -10:
            score = 50  # Neutral
            label = "NEUTRAL"
            color = "#F59E0B"
            emoji = "😐"
        elif ret_30d > -30:
            score = 30  # Fear
            label = "FEAR"
            color = "#F59E0B"
            emoji = "😰"
        else:
            score = 10  # Extreme Fear
            label = "EXTREME FEAR"
            color = "#EF4444"
            emoji = "😱"
        
        # Display gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': f"{emoji} {label}", 'font': {'color': '#FFFFFF'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 25], 'color': "#EF4444"},
                    {'range': [25, 45], 'color': "#F59E0B"},
                    {'range': [45, 55], 'color': "#F59E0B"},
                    {'range': [55, 75], 'color': "#3B82F6"},
                    {'range': [75, 100], 'color': "#22C55E"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Interpretation
        if score > 75:
            st.warning("🤑 **Market is greedy!** Consider taking profits or waiting for dip.")
        elif score < 25:
            st.success("😱 **Market is fearful!** Time to buy? Be greedy when others are fearful!")
        else:
            st.info("😐 **Market is neutral.** Wait for clearer signal.")
    else:
        st.info("Insufficient data to calculate Fear & Greed index")


def show_hodl_calculator_tab(data):
    """Show HODL profit calculator"""
    st.subheader("💰 HODL Calculator - When Lambo? 🏎️")
    
    current_price = data["current_price"]
    ticker = data["ticker"].replace("-USD", "")
    
    col1, col2 = st.columns(2)
    
    with col1:
        investment = st.number_input(
            "Initial Investment ($)",
            min_value=10.0,
            max_value=1000000.0,
            value=1000.0,
            step=100.0
        )
    
    with col2:
        target_multiple = st.slider(
            "Target Return (x)",
            min_value=2.0,
            max_value=100.0,
            value=10.0,
            step=1.0
        )
    
    # Calculate
    coins = investment / current_price
    target_price = current_price * target_multiple
    target_value = investment * target_multiple
    profit = target_value - investment
    
    st.markdown("---")
    st.markdown("### 📊 Your HODL Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"💎 {ticker} Amount",
            f"{coins:,.6f}",
            "coins"
        )
    
    with col2:
        st.metric(
            "🎯 Target Price",
            f"${target_price:,.2f}",
            f"{target_multiple}x"
        )
    
    with col3:
        st.metric(
            "💰 Profit",
            f"${profit:,.2f}",
            f"+{(target_multiple-1)*100:,.0f}%"
        )
    
    # Lambo calculator
    st.markdown("---")
    st.markdown("### 🏎️ When Lambo?")
    
    lambo_price = st.slider(
        "Lambo Price ($)",
        min_value=100000,
        max_value=500000,
        value=200000,
        step=10000
    )
    
    lambo_multiple = lambo_price / investment
    lambo_target_price = current_price * lambo_multiple
    
    if lambo_multiple < 1:
        st.success(f"🏎️ **YOU CAN ALREADY AFFORD A LAMBO!** Go get it, legend! 🚀")
    else:
        st.info(f"""
        🏎️ **Lambo Math:**
        - Need {ticker} to reach **${lambo_target_price:,.2f}** ({lambo_multiple:,.1f}x from here)
        - That's a **${lambo_price:,.0f}** lambo!
        - Keep HODLing! 💎🙌
        """)
    
    # DCA Calculator
    st.markdown("---")
    st.markdown("### 📈 DCA Strategy (Dollar Cost Average)")
    
    monthly_dca = st.number_input(
        "Monthly Investment ($)",
        min_value=10.0,
        max_value=10000.0,
        value=100.0,
        step=10.0
    )
    
    months = st.slider("DCA Period (months)", 1, 60, 12)
    
    total_invested = investment + (monthly_dca * months)
    total_coins = coins + (monthly_dca * months / current_price)
    
    st.success(f"""
    💰 **After {months} months of DCA:**
    - Total Invested: ${total_invested:,.2f}
    - Total {ticker}: {total_coins:,.6f}
    - Average Cost: ${total_invested/total_coins:.2f}
    """)
