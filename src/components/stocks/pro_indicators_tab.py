"""
Pro Indicators Tab Component
Displays advanced indicators from 7-tier system (60+ indicators)
"""
import streamlit as st

from src.ui_utils.indicator_panel import get_indicator_panel, render_summary_bar, render_indicator_charts
from indicators.master_engine import get_master_engine


def show_pro_indicators_tab(data, components):
    """
    Show professional technical indicators with AI/ML (60+ indicators)
    
    Args:
        data: Dict containing df, ticker, historical_data
        components: Dict containing indicator components
    """
    st.markdown("## 🎯 Professional Technical Indicators")
    st.markdown("""
    **TradingView Pro Equivalent** - 60+ indicators across 7 tiers:
    - 📈 **Tier 1 (Core)**: Essential indicators (SMA, EMA, RSI, MACD, Bollinger)
    - 📊 **Tier 2 (Pro)**: Professional tools (Ichimoku, Fibonacci, Stochastic, ADX)
    - 📦 **Tier 3 (Volume)**: Volume analysis (Volume Profile, A/D Line, PVT)
    - ⚡ **Tier 4 (Momentum)**: Momentum oscillators (ROC, TRIX, Connors RSI)
    - 🌐 **Tier 5 (Market Breadth)**: Market-wide indicators (Put/Call, VIX, TRIN)
    - 📐 **Tier 6 (Quant)**: Quantitative analysis (Beta, Alpha, Sharpe, Sortino)
    - 🤖 **Tier 7 (AI/ML)**: AI-powered predictions (ML Trend, Regime Detection)
    """)
    
    # Get historical data
    try:
        df = data.get('historical_data')
        if df is None or df.empty:
            st.warning("⚠️ No historical data available. Fetching...")
            ticker = data.get('ticker', 'META')
            import yfinance as yf
            stock = yf.Ticker(ticker)
            df = stock.history(period='1y')
        
        if df.empty:
            st.error("❌ Unable to fetch historical data for indicator calculation")
            return
        
        st.success(f"✅ Loaded {len(df)} trading days of data")
        
        # Initialize components
        panel = get_indicator_panel()
        engine = get_master_engine()
        
        # Control panel
        st.markdown("### 🎛️ Indicator Control Panel")
        selected_indicators = panel.render()
        
        # Quick tier selector
        st.markdown("### 🚀 Quick Select")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calculate_core = st.checkbox("📈 Core Indicators", value=True)
        with col2:
            calculate_pro = st.checkbox("📊 Pro + Volume", value=False)
        with col3:
            calculate_ai = st.checkbox("🤖 AI/ML Indicators", value=False)
        
        # Determine tiers
        tiers_to_calculate = []
        if calculate_core:
            tiers_to_calculate.extend([1])
        if calculate_pro:
            tiers_to_calculate.extend([2, 3, 4])
        if calculate_ai:
            tiers_to_calculate.extend([5, 6, 7])
        
        if not tiers_to_calculate:
            st.info("💡 Select at least one tier to calculate indicators")
            return
        
        # Calculate indicators
        with st.spinner(f"🧮 Calculating {len(tiers_to_calculate)} tiers of indicators..."):
            df_with_indicators = engine.calculate_all(df, tiers=tiers_to_calculate)
            summary = engine.get_summary(df_with_indicators)
        
        st.success(f"✅ Calculated {len(tiers_to_calculate)} tiers successfully!")
        
        # Show summary
        st.markdown("---")
        render_summary_bar(summary)
        
        st.markdown("---")
        
        # Show charts
        render_indicator_charts(df_with_indicators, selected_indicators)
        
        # Raw data viewer
        _render_raw_data_viewer(df_with_indicators)
    
    except Exception as e:
        st.error(f"❌ Error calculating indicators: {str(e)}")
        st.exception(e)


def _render_raw_data_viewer(df_with_indicators):
    """Render raw indicator data viewer"""
    with st.expander("📊 View Raw Indicator Data", expanded=False):
        st.markdown("### Latest Indicator Values")
        
        latest = df_with_indicators.iloc[-1]
        
        # Group by category
        core_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['SMA', 'EMA', 'RSI', 'MACD', 'BB'])]
        volume_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['Volume', 'OBV', 'AD', 'PVT'])]
        momentum_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['ROC', 'TRIX', 'Stoch', 'Williams', 'Momentum'])]
        ai_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['ML', 'Regime', 'Anomaly', 'Score'])]
        
        if core_cols:
            st.markdown("#### 📈 Core Indicators")
            core_data = {col: latest[col] for col in core_cols if col in latest.index}
            st.json(core_data)
        
        if volume_cols:
            st.markdown("#### 📦 Volume Indicators")
            volume_data = {col: latest[col] for col in volume_cols if col in latest.index}
            st.json(volume_data)
        
        if momentum_cols:
            st.markdown("#### ⚡ Momentum Indicators")
            momentum_data = {col: latest[col] for col in momentum_cols if col in latest.index}
            st.json(momentum_data)
        
        if ai_cols:
            st.markdown("#### 🤖 AI/ML Indicators")
            ai_data = {col: latest[col] for col in ai_cols if col in latest.index}
            st.json(ai_data)
        
        # Full dataframe
        st.markdown("#### 📊 Full DataFrame (Last 20 Rows)")
        st.dataframe(df_with_indicators.tail(20), use_container_width=True)
