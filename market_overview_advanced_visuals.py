"""
Advanced Visual Analysis for Market Overview & Economy Page
Provides similar advanced visualization capabilities as the Stock Analysis page,
but focused on market-level data instead of individual stocks.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from app_utils import plotly_full_width


def render_market_volume_profile(market_data):
    """
    Render market-level volume profile for S&P 500
    Shows volume distribution across price levels
    """
    st.markdown("###📊 Market Volume Profile (S&P 500)")
    st.caption("Horizontal histogram showing volume traded at each price level across the market.")

    try:
        # Use S&P 500 data
        df = market_data.copy()

        if len(df) < 20:
            st.warning("Insufficient data for volume profile analysis")
            return

        # Determine number of price bins
        num_bins = min(50, max(24, len(df) // 10))

        # Get price range
        price_min = df['Low'].min()
        price_max = df['High'].max()
        price_range = price_max - price_min

        # Create price bins
        bins = np.linspace(price_min, price_max, num_bins + 1)

        # Calculate volume at each price level
        volume_profile = np.zeros(num_bins)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        # Distribute volume across touched bins
        for idx, row in df.iterrows():
            low = row['Low']
            high = row['High']
            volume = row['Volume']

            touched_bins = (bins[:-1] <= high) & (bins[1:] >= low)
            num_touched = touched_bins.sum()

            if num_touched > 0:
                volume_profile[touched_bins] += volume / num_touched

        # Calculate key levels
        total_volume = volume_profile.sum()
        poc_idx = np.argmax(volume_profile)
        poc_price = bin_centers[poc_idx]
        poc_volume = volume_profile[poc_idx]

        # Value Area (70%)
        sorted_indices = np.argsort(volume_profile)[::-1]
        cumulative_volume = 0
        va_threshold = total_volume * 0.70
        value_area_bins = []

        for idx in sorted_indices:
            cumulative_volume += volume_profile[idx]
            value_area_bins.append(idx)
            if cumulative_volume >= va_threshold:
                break

        vah_price = bin_centers[max(value_area_bins)]
        val_price = bin_centers[min(value_area_bins)]
        current_price = df['Close'].iloc[-1]

        # Create visualization
        col1, col2 = st.columns([3, 1])

        with col1:
            fig = go.Figure()

            colors = ['#2196F3' if i in value_area_bins else '#B0BEC5'
                     for i in range(num_bins)]
            colors[poc_idx] = '#00C853'

            fig.add_trace(go.Bar(
                y=bin_centers,
                x=volume_profile,
                orientation='h',
                marker=dict(color=colors),
                hovertemplate='Price: $%{y:.2f}<br>Volume: %{x:,.0f}<extra></extra>',
                showlegend=False
            ))

            fig.add_hline(
                y=poc_price,
                line=dict(color='#00C853', width=3, dash='solid'),
                annotation_text=f"POC: ${poc_price:.2f}",
                annotation_position="right"
            )

            fig.add_hline(
                y=vah_price,
                line=dict(color='#FF6F00', width=2, dash='dash'),
                annotation_text=f"VAH: ${vah_price:.2f}",
                annotation_position="right"
            )

            fig.add_hline(
                y=val_price,
                line=dict(color='#FF6F00', width=2, dash='dash'),
                annotation_text=f"VAL: ${val_price:.2f}",
                annotation_position="right"
            )

            fig.add_hline(
                y=current_price,
                line=dict(color='#FFA726', width=2, dash='dot'),
                annotation_text=f"Current: ${current_price:.2f}",
                annotation_position="right"
            )

            fig.add_hrect(
                y0=val_price, y1=vah_price,
                fillcolor='rgba(33, 150, 243, 0.1)',
                line_width=0,
                layer='below'
            )

            fig.update_layout(
                title="S&P 500 Volume Profile",
                xaxis_title="Volume",
                yaxis_title="Price Level ($)",
                height=500,
                showlegend=False,
                hovermode='y',
                margin=dict(r=120)
            )

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 📊 Key Levels")

            st.markdown(f"""
            <div style='background-color: #00C853; color: white; padding: 10px;
                 border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Point of Control</div>
                <div style='font-size: 18px; font-weight: bold;'>${poc_price:.2f}</div>
                <div style='font-size: 10px; opacity: 0.8;'>{poc_volume:,.0f} vol</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='background-color: #FF6F00; color: white; padding: 10px;
                 border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Value Area (70%)</div>
                <div style='font-size: 16px; font-weight: bold;'>${val_price:.2f} - ${vah_price:.2f}</div>
                <div style='font-size: 10px; opacity: 0.8;'>Range: ${vah_price - val_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            if current_price > vah_price:
                position = "Above Value Area"
                position_color = "#4CAF50"
                position_emoji = "🔼"
                interpretation = "Bullish - market above fair value"
            elif current_price < val_price:
                position = "Below Value Area"
                position_color = "#F44336"
                position_emoji = "🔽"
                interpretation = "Bearish - market below fair value"
            else:
                position = "Inside Value Area"
                position_color = "#2196F3"
                position_emoji = "↔️"
                interpretation = "Neutral - market at fair value"

            st.markdown(f"""
            <div style='background-color: {position_color}; color: white; padding: 10px;
                 border-radius: 5px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Market Position</div>
                <div style='font-size: 16px; font-weight: bold;'>{position_emoji} {position}</div>
                <div style='font-size: 10px; opacity: 0.8;'>{interpretation}</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error calculating market volume profile: {str(e)}")


def render_market_strength_meter(indices_data):
    """
    Render composite market strength meter
    Uses multiple market indices and indicators
    """
    st.markdown("### 💪 Market Strength Meter")
    st.caption("Composite confidence score from multiple market indicators")

    try:
        # Fetch market data
        sp500 = yf.Ticker('^GSPC')
        vix = yf.Ticker('^VIX')

        sp500_hist = sp500.history(period='1y')
        vix_hist = vix.history(period='5d')

        if sp500_hist.empty:
            st.warning("Could not fetch market data")
            return

        df = sp500_hist.copy()

        # Calculate indicators
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Volume
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

        # Get current values
        current_price = df['Close'].iloc[-1]
        current_rsi = df['RSI'].iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume_SMA'].iloc[-1]

        # Get VIX
        current_vix = vix_hist['Close'].iloc[-1] if not vix_hist.empty else 20

        # Calculate component scores

        # 1. Trend Strength (MA alignment)
        trend_score = 0
        if pd.notna(df['SMA20'].iloc[-1]) and pd.notna(df['SMA50'].iloc[-1]) and pd.notna(df['SMA200'].iloc[-1]):
            if current_price > df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
                trend_score = 100
            elif current_price > df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
                trend_score = 75
            elif current_price > df['SMA20'].iloc[-1]:
                trend_score = 50
            elif current_price < df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1] < df['SMA200'].iloc[-1]:
                trend_score = 0
            elif current_price < df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
                trend_score = 25
            else:
                trend_score = 50

        # 2. Momentum (RSI)
        if pd.notna(current_rsi):
            if 40 <= current_rsi <= 60:
                momentum_score = 50
            elif current_rsi > 60:
                momentum_score = min(100, 50 + (current_rsi - 60) * 1.25)
            else:
                momentum_score = max(0, 50 - (40 - current_rsi) * 1.25)
        else:
            momentum_score = 50

        # 3. Volatility (VIX - inverted)
        if current_vix < 15:
            vix_score = 100  # Low volatility = bullish
        elif current_vix < 20:
            vix_score = 75
        elif current_vix < 25:
            vix_score = 50
        elif current_vix < 30:
            vix_score = 25
        else:
            vix_score = 0  # High volatility = bearish

        # 4. Volume Confirmation
        if pd.notna(current_volume) and pd.notna(avg_volume) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:
                volume_score = 100
            elif volume_ratio > 1.0:
                volume_score = 75
            elif volume_ratio > 0.75:
                volume_score = 50
            else:
                volume_score = 25
        else:
            volume_score = 50

        # 5. Market Breadth (price distance from 52w high)
        high_52w = df['High'].max()
        distance_from_high = (current_price / high_52w - 1) * 100
        if distance_from_high > -2:
            breadth_score = 100
        elif distance_from_high > -5:
            breadth_score = 75
        elif distance_from_high > -10:
            breadth_score = 50
        elif distance_from_high > -15:
            breadth_score = 25
        else:
            breadth_score = 0

        # Calculate overall score (weighted)
        weights = {
            'trend': 0.30,
            'momentum': 0.20,
            'vix': 0.20,
            'breadth': 0.20,
            'volume': 0.10
        }

        overall_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            vix_score * weights['vix'] +
            breadth_score * weights['breadth'] +
            volume_score * weights['volume']
        )

        # Determine sentiment
        if overall_score >= 70:
            sentiment = "Strong Bullish"
            sentiment_color = "#4CAF50"
            sentiment_emoji = "🚀"
        elif overall_score >= 55:
            sentiment = "Bullish"
            sentiment_color = "#8BC34A"
            sentiment_emoji = "📈"
        elif overall_score >= 45:
            sentiment = "Neutral"
            sentiment_color = "#FFC107"
            sentiment_emoji = "➡️"
        elif overall_score >= 30:
            sentiment = "Bearish"
            sentiment_color = "#FF9800"
            sentiment_emoji = "📉"
        else:
            sentiment = "Strong Bearish"
            sentiment_color = "#F44336"
            sentiment_emoji = "⚠️"

        # Create visualization
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_score,
                title={'text': "Overall Market Confidence", 'font': {'size': 20}},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': sentiment_color, 'thickness': 0.75},
                    'steps': [
                        {'range': [0, 30], 'color': '#FFCDD2'},
                        {'range': [30, 45], 'color': '#FFE0B2'},
                        {'range': [45, 55], 'color': '#FFF9C4'},
                        {'range': [55, 70], 'color': '#C8E6C9'},
                        {'range': [70, 100], 'color': '#A5D6A7'}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'value': 50}
                }
            ))

            fig.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Assessment")
            st.markdown(f"""
            <div style='background-color: {sentiment_color}; color: white; padding: 15px;
                 border-radius: 5px; text-align: center; margin-bottom: 10px;'>
                <div style='font-size: 24px; font-weight: bold;'>{sentiment_emoji} {sentiment}</div>
                <div style='font-size: 18px; margin-top: 5px;'>{overall_score:.1f}/100</div>
            </div>
            """, unsafe_allow_html=True)

            if overall_score >= 70:
                st.success("✓ Strong bullish signals across multiple indicators")
            elif overall_score >= 55:
                st.info("✓ Moderately bullish conditions")
            elif overall_score >= 45:
                st.warning("⚠️ Mixed signals - no clear direction")
            elif overall_score >= 30:
                st.info("✓ Moderately bearish conditions")
            else:
                st.error("⛔ High confidence in bearish trend")

        # Component breakdown
        st.markdown("---")
        st.markdown("#### 📊 Component Breakdown")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Trend",
                f"{trend_score:.0f}/100",
                help="Moving average alignment"
            )
            st.caption(f"Weight: {weights['trend']:.0%}")

        with col2:
            st.metric(
                "Momentum",
                f"{momentum_score:.0f}/100",
                delta=f"RSI: {current_rsi:.1f}" if pd.notna(current_rsi) else None,
                help="RSI-based momentum"
            )
            st.caption(f"Weight: {weights['momentum']:.0%}")

        with col3:
            st.metric(
                "Volatility",
                f"{vix_score:.0f}/100",
                delta=f"VIX: {current_vix:.1f}",
                help="VIX fear gauge (inverted)"
            )
            st.caption(f"Weight: {weights['vix']:.0%}")

        with col4:
            st.metric(
                "Breadth",
                f"{breadth_score:.0f}/100",
                delta=f"{distance_from_high:.1f}% from 52w high",
                help="Distance from 52-week high"
            )
            st.caption(f"Weight: {weights['breadth']:.0%}")

        with col5:
            st.metric(
                "Volume",
                f"{volume_score:.0f}/100",
                delta=f"{volume_ratio:.2f}x avg" if pd.notna(current_volume) and pd.notna(avg_volume) else None,
                help="Volume confirmation"
            )
            st.caption(f"Weight: {weights['volume']:.0%}")

    except Exception as e:
        st.error(f"Error calculating market strength meter: {str(e)}")


def render_market_advanced_visual_analysis(indices_data, market_health):
    """
    Main entry point for Market Overview Advanced Visual Analysis
    """
    st.markdown("---")
    st.markdown("## 🔬 Advanced Market Visual Analysis")
    st.caption("Institutional-grade technical analysis for market-level data")

    # Fetch S&P 500 data for volume profile
    sp500 = yf.Ticker('^GSPC')
    sp500_hist = sp500.history(period='6mo')

    if not sp500_hist.empty:
        render_market_volume_profile(sp500_hist)
    else:
        st.warning("Could not load S&P 500 data for volume profile")

    st.markdown("---")

    render_market_strength_meter(indices_data)

    st.markdown("---")

    # Trading implications
    st.markdown("### 💡 How to Use These Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📊 Market Volume Profile**
        - Identifies key support/resistance for the overall market
        - POC shows where most trading activity occurred
        - Value Area shows "fair price" range for market
        - Use for understanding market structure

        **💪 Market Strength Meter**
        - Composite view of market health
        - Combines trend, momentum, volatility, breadth
        - Use for overall market sentiment assessment
        """)

    with col2:
        st.markdown("""
        **📈 Trading Strategies**
        - When market above VAH + high strength = go long
        - When market below VAL + low strength = reduce exposure
        - When market in Value Area = range-bound trading
        - Use strength meter for position sizing

        **⚠️ Risk Management**
        - Low strength score = reduce position sizes
        - High VIX component = increase hedges
        - Weak breadth = be selective with longs
        """)
