"""
Technical Indicators Control Panel
Interactive toggle panel for all 60+ indicators with tier-based organization
"""
import streamlit as st
from typing import Dict, List, Set
import pandas as pd


class IndicatorPanel:
    """
    Interactive control panel for managing technical indicators.
    Provides toggle switches, tier organization, and configuration options.
    """
    
    def __init__(self):
        self.tier_descriptions = {
            'Tier 1 - Core': 'Essential indicators (SMA, EMA, RSI, MACD, Bollinger, ATR, VWAP)',
            'Tier 2 - Pro': 'Professional indicators (Ichimoku, Fibonacci, Stochastic, ADX)',
            'Tier 3 - Volume': 'Volume analysis (Volume Profile, A/D Line, PVT, Force Index)',
            'Tier 4 - Momentum': 'Momentum oscillators (ROC, TRIX, Connors RSI, Williams %R)',
            'Tier 5 - Market Breadth': 'Market-wide indicators (Put/Call, VIX, TRIN, Dark Pool)',
            'Tier 6 - Quant': 'Quantitative analysis (Beta, Alpha, Sharpe, Sortino, Z-Score)',
            'Tier 7 - AI/ML': 'AI-powered indicators (ML Trend, Regime Detection, Anomaly Detection)'
        }
        
        self.tier_indicators = {
            'Tier 1 - Core': [
                '📈 SMA (Simple Moving Averages)',
                '📊 EMA (Exponential Moving Averages)',
                '📉 Bollinger Bands',
                '🌊 MACD (Moving Average Convergence Divergence)',
                '⚡ RSI (Relative Strength Index)',
                '📦 OBV (On-Balance Volume)',
                '🎯 ATR (Average True Range)',
                '💧 VWAP (Volume Weighted Average Price)',
                '🕐 Market Hours Detection'
            ],
            'Tier 2 - Pro': [
                '☁️ Ichimoku Cloud',
                '📐 Fibonacci Retracement & Extensions',
                '🔄 Stochastic Oscillator',
                '💰 Chaikin Money Flow (CMF)',
                '💵 Money Flow Index (MFI)',
                '📏 Donchian Channels',
                '🔔 Keltner Channels',
                '💪 ADX + Directional Indicators',
                '🪂 Parabolic SAR',
                '🎲 Pivot Points (Classic/Fibonacci/Camarilla)'
            ],
            'Tier 3 - Volume': [
                '🏔️ Volume Profile (POC, Value Area)',
                '⚖️ VWMA (Volume Weighted Moving Average)',
                '📊 Accumulation/Distribution Line',
                '📈 Price Volume Trend (PVT)',
                '🎈 Ease of Movement (EOM)',
                '⚔️ Force Index',
                '🌊 Volume Oscillator',
                '🎸 Klinger Oscillator'
            ],
            'Tier 4 - Momentum': [
                '🚀 Rate of Change (ROC)',
                '3️⃣ TRIX (Triple EMA)',
                '📊 Chande Momentum Oscillator',
                '📉 Detrended Price Oscillator (DPO)',
                '📈 Coppock Curve',
                '🔥 Connors RSI',
                '🎯 Williams %R'
            ],
            'Tier 5 - Market Breadth': [
                '📞 Put/Call Ratio',
                '📊 High-Low Index',
                '📈 Advance/Decline Line',
                '⚖️ TRIN Index (Arms Index)',
                '😱 VIX (Volatility Index)',
                '🕶️ Dark Pool Volume Estimate'
            ],
            'Tier 6 - Quant': [
                '📏 Z-Score (Standardized Price)',
                '📊 Rolling Beta (vs SPY/QQQ)',
                '⭐ Rolling Alpha (Excess Returns)',
                '🔗 Correlation Matrix',
                '📈 Sharpe Ratio',
                '📉 Sortino Ratio',
                '🎪 Volatility Cones'
            ],
            'Tier 7 - AI/ML': [
                '🤖 Regime Detection (ML)',
                '🔔 Volume Anomaly Detection',
                '⚠️ Price Anomaly Detection',
                '📊 VIX-Adjusted Volatility Bands',
                '🧠 ML Trend Classifier (Random Forest)',
                '💯 Composite Momentum Score'
            ]
        }
    
    def render(self) -> Dict[str, List[str]]:
        """
        Render the indicator control panel and return selected indicators.
        Returns: Dict mapping tier names to lists of selected indicators
        """
        st.markdown("### 📊 Technical Indicators Control Panel")
        st.markdown("Select indicators to display on charts and analysis")
        
        # Quick selection buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("✅ Select All", use_container_width=True):
                st.session_state.indicator_selection = self._get_all_indicators()
                st.rerun()
        with col2:
            if st.button("❌ Deselect All", use_container_width=True):
                st.session_state.indicator_selection = {}
                st.rerun()
        with col3:
            if st.button("⭐ Core Only", use_container_width=True):
                st.session_state.indicator_selection = {'Tier 1 - Core': self.tier_indicators['Tier 1 - Core']}
                st.rerun()
        with col4:
            if st.button("🚀 Pro + AI", use_container_width=True):
                st.session_state.indicator_selection = {
                    'Tier 2 - Pro': self.tier_indicators['Tier 2 - Pro'],
                    'Tier 7 - AI/ML': self.tier_indicators['Tier 7 - AI/ML']
                }
                st.rerun()
        
        st.markdown("---")
        
        # Initialize session state
        if 'indicator_selection' not in st.session_state:
            st.session_state.indicator_selection = {
                'Tier 1 - Core': self.tier_indicators['Tier 1 - Core'][:5]  # Default: first 5 core
            }
        
        selected_indicators = {}
        
        # Render each tier in an expander
        for tier_name, indicators in self.tier_indicators.items():
            with st.expander(f"{tier_name} ({len(indicators)} indicators)", expanded=(tier_name == 'Tier 1 - Core')):
                st.caption(self.tier_descriptions[tier_name])
                
                # Select all/none for this tier
                tier_col1, tier_col2 = st.columns([1, 1])
                with tier_col1:
                    if st.button(f"Select All", key=f"select_{tier_name}", use_container_width=True):
                        if tier_name not in st.session_state.indicator_selection:
                            st.session_state.indicator_selection[tier_name] = []
                        st.session_state.indicator_selection[tier_name] = indicators.copy()
                        st.rerun()
                with tier_col2:
                    if st.button(f"Deselect All", key=f"deselect_{tier_name}", use_container_width=True):
                        if tier_name in st.session_state.indicator_selection:
                            st.session_state.indicator_selection[tier_name] = []
                        st.rerun()
                
                # Multi-select for indicators
                selected = st.multiselect(
                    "Select indicators:",
                    options=indicators,
                    default=st.session_state.indicator_selection.get(tier_name, []),
                    key=f"multi_{tier_name}",
                    label_visibility="collapsed"
                )
                
                selected_indicators[tier_name] = selected
                st.session_state.indicator_selection[tier_name] = selected
                
                # Show selection count
                if selected:
                    st.success(f"✅ {len(selected)} indicators selected")
        
        # Summary at bottom
        st.markdown("---")
        total_selected = sum(len(v) for v in selected_indicators.values())
        st.info(f"**Total Selected: {total_selected} indicators across {len([k for k, v in selected_indicators.items() if v])} tiers**")
        
        return selected_indicators
    
    def render_compact(self) -> List[int]:
        """
        Render a compact tier selector (returns list of tier numbers).
        """
        st.markdown("### 🎛️ Indicator Tiers")
        
        selected_tiers = st.multiselect(
            "Select tiers to calculate:",
            options=[
                "Tier 1 - Core",
                "Tier 2 - Pro",
                "Tier 3 - Volume",
                "Tier 4 - Momentum",
                "Tier 5 - Market Breadth",
                "Tier 6 - Quant",
                "Tier 7 - AI/ML"
            ],
            default=["Tier 1 - Core"],
            format_func=lambda x: f"{x} - {self.tier_descriptions[x]}"
        )
        
        # Convert to tier numbers
        tier_nums = [int(tier.split()[1]) for tier in selected_tiers]
        
        st.caption(f"💡 {len(tier_nums)} tiers selected")
        
        return tier_nums
    
    def _get_all_indicators(self) -> Dict[str, List[str]]:
        """Get all indicators across all tiers."""
        return {tier: indicators.copy() for tier, indicators in self.tier_indicators.items()}


def render_summary_bar(summary: Dict[str, Dict]):
    """
    Render a visual summary bar showing key indicator signals.
    Args:
        summary: Summary dict from MasterIndicatorEngine.get_summary()
    """
    if not summary:
        st.warning("⚠️ No indicator data available")
        return
    
    st.markdown("### 📊 Indicator Summary Dashboard")
    
    # Create 6 columns for each category
    cols = st.columns(6)
    
    # TREND
    with cols[0]:
        trend = summary.get('trend', {})
        overall = trend.get('overall', 'neutral')
        
        if overall == 'bullish':
            st.markdown("### 📈 TREND")
            st.success("**BULLISH**")
        elif overall == 'bearish':
            st.markdown("### 📉 TREND")
            st.error("**BEARISH**")
        else:
            st.markdown("### ➡️ TREND")
            st.info("**NEUTRAL**")
        
        signals = trend.get('signals', [])
        for signal_type, signal_text in signals[:3]:  # Show top 3
            st.caption(f"• {signal_text}")
    
    # MOMENTUM
    with cols[1]:
        momentum = summary.get('momentum', {})
        overall = momentum.get('overall', 'neutral')
        
        st.markdown("### ⚡ MOMENTUM")
        if overall == 'bullish':
            st.success("**POSITIVE**")
        elif overall == 'bearish':
            st.error("**NEGATIVE**")
        else:
            st.info("**NEUTRAL**")
        
        signals = momentum.get('signals', [])
        for signal_type, signal_text in signals[:3]:
            st.caption(f"• {signal_text}")
    
    # VOLATILITY
    with cols[2]:
        volatility = summary.get('volatility', {})
        overall = volatility.get('overall', 'normal')
        
        st.markdown("### 🌪️ VOLATILITY")
        if overall == 'high':
            st.warning("**HIGH**")
        elif overall == 'low':
            st.success("**LOW**")
        else:
            st.info("**NORMAL**")
        
        signals = volatility.get('signals', [])
        for signal_type, signal_text in signals[:3]:
            st.caption(f"• {signal_text}")
    
    # VOLUME
    with cols[3]:
        volume = summary.get('volume', {})
        overall = volume.get('overall', 'normal')
        
        st.markdown("### 📊 VOLUME")
        if overall == 'strong':
            st.success("**STRONG**")
        elif overall == 'weak':
            st.error("**WEAK**")
        else:
            st.info("**NORMAL**")
        
        signals = volume.get('signals', [])
        for signal_type, signal_text in signals[:3]:
            st.caption(f"• {signal_text}")
    
    # BREADTH
    with cols[4]:
        breadth = summary.get('breadth', {})
        overall = breadth.get('overall', 'neutral')
        
        st.markdown("### 🌐 BREADTH")
        if overall == 'positive':
            st.success("**POSITIVE**")
        elif overall == 'negative':
            st.error("**NEGATIVE**")
        else:
            st.info("**NEUTRAL**")
        
        signals = breadth.get('signals', [])
        for signal_type, signal_text in signals[:3]:
            st.caption(f"• {signal_text}")
    
    # SENTIMENT (AI)
    with cols[5]:
        sentiment = summary.get('sentiment', {})
        overall = sentiment.get('overall', 'neutral')
        
        st.markdown("### 🤖 AI/ML")
        if overall == 'bullish':
            st.success("**BULLISH**")
        elif overall == 'bearish':
            st.error("**BEARISH**")
        else:
            st.info("**NEUTRAL**")
        
        signals = sentiment.get('signals', [])
        for signal_type, signal_text in signals[:3]:
            st.caption(f"• {signal_text}")
    
    st.markdown("---")


def render_indicator_charts(df: pd.DataFrame, selected_indicators: Dict[str, List[str]]):
    """
    Render charts for selected indicators.
    Args:
        df: DataFrame with calculated indicators
        selected_indicators: Dict of selected indicators by tier
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    if df.empty:
        st.warning("No data available for charting")
        return
    
    # Count total indicators to chart
    total_indicators = sum(len(v) for v in selected_indicators.values())
    
    if total_indicators == 0:
        st.info("💡 Select indicators from the control panel to display charts")
        return
    
    st.markdown(f"### 📈 Indicator Charts ({total_indicators} active)")
    
    # Create tabs for different indicator categories
    tabs = st.tabs(["📊 Price + Overlays", "⚡ Oscillators", "📦 Volume", "🤖 AI/ML"])
    
    # TAB 1: Price + Overlays
    with tabs[0]:
        fig = go.Figure()
        
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ))
        
        # Add overlay indicators (SMAs, EMAs, Bollinger, etc.)
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(width=1)))
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(width=1.5)))
        if 'SMA_200' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], name='SMA 200', line=dict(width=2)))
        
        if 'BB_Upper' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', 
                                    line=dict(dash='dash', color='gray')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                                    line=dict(dash='dash', color='gray'), fill='tonexty'))
        
        if 'Ichimoku_SpanA' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Ichimoku_SpanA'], name='Ichimoku Span A',
                                    line=dict(color='green', width=0.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['Ichimoku_SpanB'], name='Ichimoku Span B',
                                    line=dict(color='red', width=0.5), fill='tonexty'))
        
        fig.update_layout(title="Price Chart with Overlays", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Oscillators
    with tabs[1]:
        oscillator_cols = ['RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram', 'Stoch_K', 'Stoch_D', 
                          'ADX', 'Williams_R', 'ROC', 'Momentum_Score']
        available_oscillators = [col for col in oscillator_cols if col in df.columns]
        
        if available_oscillators:
            num_plots = len(available_oscillators)
            fig = make_subplots(rows=num_plots, cols=1, shared_xaxes=True,
                               subplot_titles=available_oscillators)
            
            for i, col in enumerate(available_oscillators, 1):
                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=i, col=1)
                
                # Add reference lines
                if 'RSI' in col:
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=i, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=i, col=1)
                elif 'Stoch' in col:
                    fig.add_hline(y=80, line_dash="dash", line_color="red", row=i, col=1)
                    fig.add_hline(y=20, line_dash="dash", line_color="green", row=i, col=1)
            
            fig.update_layout(height=300*num_plots, title="Oscillator Indicators")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No oscillator indicators calculated yet")
    
    # TAB 3: Volume
    with tabs[2]:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=['Volume', 'Volume Indicators'])
        
        # Volume bars
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                 for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'),
                     row=1, col=1)
        
        # Volume indicators
        if 'OBV' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['OBV'], name='OBV'), row=2, col=1)
        if 'Volume_SMA' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'], name='Volume SMA', 
                                    line=dict(dash='dash')), row=1, col=1)
        
        fig.update_layout(height=600, title="Volume Analysis")
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: AI/ML
    with tabs[3]:
        ai_cols = ['ML_Trend', 'Regime', 'Momentum_Score', 'ML_Confidence']
        available_ai = [col for col in ai_cols if col in df.columns]
        
        if available_ai:
            st.markdown("#### 🤖 AI-Powered Analysis")
            
            # Show latest AI predictions
            latest = df.iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if 'ML_Trend' in df.columns:
                    trend = latest['ML_Trend']
                    confidence = latest.get('ML_Confidence', 0) * 100
                    if trend == 'bullish':
                        st.success(f"**ML Trend:** {trend.upper()}")
                        st.caption(f"Confidence: {confidence:.1f}%")
                    elif trend == 'bearish':
                        st.error(f"**ML Trend:** {trend.upper()}")
                        st.caption(f"Confidence: {confidence:.1f}%")
            
            with col2:
                if 'Regime' in df.columns:
                    regime = latest['Regime']
                    st.info(f"**Regime:** {regime.title()}")
            
            with col3:
                if 'Momentum_Score' in df.columns:
                    score = latest['Momentum_Score']
                    st.metric("Momentum Score", f"{score:.0f}/100")
            
            with col4:
                if 'Volume_Anomaly' in df.columns:
                    if latest['Volume_Anomaly']:
                        st.warning("⚠️ **Volume Anomaly**")
                    if latest.get('Price_Anomaly', False):
                        st.warning("⚠️ **Price Anomaly**")
            
            # Chart momentum score over time
            if 'Momentum_Score' in df.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Momentum_Score'], 
                                        name='Momentum Score', fill='tozeroy'))
                fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Overbought")
                fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Oversold")
                fig.update_layout(title="AI Composite Momentum Score (0-100)", height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Enable Tier 7 (AI/ML) indicators to see ML predictions")


def get_indicator_panel():
    """Factory function to get IndicatorPanel instance."""
    return IndicatorPanel()
