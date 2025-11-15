"""
Technical Tab Component
Displays RSI, MACD, Bollinger Bands, and technical indicators
"""
import streamlit as st
import pandas as pd

from src.ui_utils.formatters import format_currency
from src.ui_utils.design_system import get_color


def show_technical_tab(data, components):
    """
    Show technical analysis with progressive loading
    
    Args:
        data: Dict containing df, stock_data, indicators
        components: Dict containing technical analysis components
    """
    from src.ui_utils.loading_indicators import show_skeleton_chart, show_skeleton_metric
    
    st.subheader("📈 Technical Analysis (TA)")
    
    df = data.get("df", pd.DataFrame())
    
    if df.empty:
        st.warning("Insufficient data for TA")
        return
    
    # Show skeleton loaders while analyzing
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    with metrics_placeholder.container():
        st.caption("⏳ Analyzing technical indicators...")
        show_skeleton_metric(count=3)
    
    with chart_placeholder.container():
        show_skeleton_chart(height=400)
    
    # Perform analysis
    technical = components["technical"].analyze(df)
    
    # Clear placeholders
    metrics_placeholder.empty()
    chart_placeholder.empty()
    
    if "error" in technical:
        st.error(f"TA Error: {technical['error']}")
        return
    
    # Render sections
    _render_primary_indicators(technical)
    st.markdown("---")
    _render_moving_averages(technical)
    st.markdown("---")
    _render_patterns(components, df)


def _render_primary_indicators(technical: dict):
    """Render RSI, MACD, Bollinger Bands"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # RSI
        rsi_val = technical.get("rsi", {}).get("value", 50)
        rsi_signal = technical.get("rsi", {}).get("signal", "neutral")
        
        st.markdown("### 🔥 RSI")
        
        if rsi_signal == "oversold":
            st.success(f"**{rsi_val:.1f}** - OVERSOLD! Time to buy the dip! 🦍")
        elif rsi_signal == "overbought":
            st.warning(f"**{rsi_val:.1f}** - OVERBOUGHT! Moon soon? 🚀")
        else:
            st.info(f"**{rsi_val:.1f}** - Neutral 📊")
    
    with col2:
        # MACD
        st.markdown("### 📊 MACD")
        macd_bull = technical.get("macd", {}).get("bullish", False)
        
        if macd_bull:
            st.success("**BULLISH** Crossover! 🚀")
        else:
            st.warning("**BEARISH** Watch out! 📉")
    
    with col3:
        # Bollinger Bands
        st.markdown("### 📊 Bollinger Bands")
        bb_data = technical.get("bollinger", {})
        bb_upper = bb_data.get("upper", 0)
        bb_middle = bb_data.get("middle", 0)
        bb_lower = bb_data.get("lower", 0)
        bb_signal = bb_data.get("signal", "neutral")
        
        st.markdown(f"**Upper:** {format_currency(bb_upper)}")
        st.markdown(f"**Middle:** {format_currency(bb_middle)}")
        st.markdown(f"**Lower:** {format_currency(bb_lower)}")
        
        if bb_signal == "oversold":
            st.success("📍 Below lower band! Buy signal! 🚀")
        elif bb_signal == "overbought":
            st.warning("⚠️ Above upper band! Overbought!")
        else:
            st.info("📊 Within bands - Normal range")


def _render_moving_averages(technical: dict):
    """Render SMA 50/200 and support/resistance"""
    col1, col2, col3 = st.columns(3)
    
    price_action = technical.get("price_action", {})
    current_price = price_action.get("price", 0)
    
    with col1:
        # SMA 50
        st.markdown("### 📈 SMA 50")
        sma_50 = price_action.get("sma_50", 0)
        above_sma_50 = price_action.get("above_sma_50", False)
        
        st.markdown(f"**SMA 50:** {format_currency(sma_50)}")
        st.markdown(f"**Current:** {format_currency(current_price)}")
        
        if above_sma_50:
            st.success("✅ Above SMA 50 - Bullish!")
        else:
            st.warning("⚠️ Below SMA 50 - Bearish")
    
    with col2:
        # SMA 200
        st.markdown("### 📈 SMA 200")
        sma_200 = price_action.get("sma_200", 0)
        above_sma_200 = price_action.get("above_sma_200", False)
        
        st.markdown(f"**SMA 200:** {format_currency(sma_200)}")
        st.markdown(f"**Current:** {format_currency(current_price)}")
        
        if above_sma_200:
            st.success("✅ Above SMA 200 - Strong trend!")
        else:
            st.warning("⚠️ Below SMA 200 - Weak trend")
    
    with col3:
        # Support/Resistance
        st.markdown("### 🎯 Support/Resistance")
        support = technical.get("support_resistance", {}).get("support", 0)
        resistance = technical.get("support_resistance", {}).get("resistance", 0)
        
        st.markdown(f"**Resistance:** {format_currency(resistance)}")
        st.markdown(f"**Support:** {format_currency(support)}")
        
        if technical.get("support_resistance", {}).get("near_support", False):
            st.success("📍 Near support! Buy opportunity!")
        elif technical.get("support_resistance", {}).get("near_resistance", False):
            st.warning("🚧 Near resistance! Take profits?")


def _render_patterns(components, df: pd.DataFrame):
    """Render detected chart patterns"""
    st.markdown("### 🔍 Chart Patterns")
    
    patterns = components["technical"].detect_patterns(df)
    if patterns:
        for pattern in patterns:
            signal_color = get_color('success') if pattern['signal'] == "bullish" else get_color('danger')
            signal_emoji = "🚀" if pattern['signal'] == "bullish" else "📉"
            st.markdown(
                f"<span style='color: {signal_color}'>{signal_emoji} {pattern['pattern'].replace('_', ' ').title()} - {pattern['signal'].upper()}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No major patterns detected. Sideways trading 📊")
