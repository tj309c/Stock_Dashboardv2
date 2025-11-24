"""
Market Overview & Economy Page
Provides broad market analysis, sector rotation, economic indicators,
and predictive signals to understand market health and direction.
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Performance optimization
from performance_optimizer import PerformanceMonitor, optimize_dataframe

# Global sidebar
from global_sidebar import render_global_sidebar, apply_theme_css
from app_utils import format_money, display_dataframe_full_width, plotly_full_width

# Fear & Greed professional analysis
from fear_greed_history import FearGreedHistory
from fear_greed_visualizations import (
    render_component_breakdown,
    render_trend_analysis,
    render_divergence_alerts,
    render_percentile_analysis,
    render_sector_rotation_heatmap,
    render_cross_asset_dashboard,
    render_options_flow_detail
)

# Advanced visual analysis
from market_overview_advanced_visuals import render_market_advanced_visual_analysis

# Mode configuration
from mode_config import get_current_mode, get_cache_ttl, render_mode_info

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Market Overview & Economy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# GLOBAL SIDEBAR (Theme, AI Settings)
# ============================
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# ========================================
# FEAR & GREED INDEX - HELPER FUNCTIONS
# ========================================

# Pre-calculated optimal weights (run offline with historical correlation analysis)
FEAR_GREED_WEIGHTS_L1 = {
    'vix': 0.30,
    'put_call_ratio': 0.25,
    'market_breadth': 0.20,
    'distance_52w_high': 0.15,
    'safe_haven_demand': 0.10
}

FEAR_GREED_WEIGHTS_L2 = {
    'vix': 0.18,
    'put_call_ratio': 0.15,
    'market_breadth': 0.12,
    'distance_52w_high': 0.10,
    'safe_haven_demand': 0.08,
    'advance_decline': 0.09,
    'new_highs_lows': 0.07,
    'junk_bond_spread': 0.11,
    'rsi': 0.10
}

FEAR_GREED_WEIGHTS_L3 = {
    'vix': 0.16,
    'put_call_ratio': 0.13,
    'market_breadth': 0.10,
    'distance_52w_high': 0.08,
    'safe_haven_demand': 0.07,
    'advance_decline': 0.08,
    'new_highs_lows': 0.06,
    'junk_bond_spread': 0.10,
    'rsi': 0.08,
    'options_skew': 0.06,
    'margin_debt': 0.04,
    'aaii_sentiment': 0.02,
    'treasury_stock_gap': 0.02
}


def normalize_vix_to_score(vix_value):
    """Normalize VIX to 0-100 score (higher VIX = more fear = lower score)"""
    if vix_value < 12:
        return 100  # Extreme greed
    elif vix_value < 17:
        return 75
    elif vix_value < 25:
        return 50  # Neutral
    elif vix_value < 35:
        return 25
    else:
        return 0  # Extreme fear


@st.cache_data(ttl=get_cache_ttl("fast"))
def fetch_put_call_ratio():
    """
    Fetch CBOE Put/Call Ratio
    Cache TTL adapts to trading mode (faster for traders, slower for investors)

    Returns tuple: (ratio, data_available)
    - ratio: Put/Call ratio value (1.0 = neutral fallback if unavailable)
    - data_available: Boolean indicating if real data was fetched
    """
    # Try multiple data sources in order of preference
    tickers_to_try = [
        ("^CPCE", "CBOE Equity Put/Call"),  # Most reliable
        ("^PCALL", "CBOE Total Put/Call"),
        ("^PCCE", "CBOE Equity Put/Call Alt")
    ]

    for ticker, name in tickers_to_try:
        try:
            pcr = yf.Ticker(ticker)
            hist = pcr.history(period='5d')
            if not hist.empty and len(hist) > 0:
                ratio = hist['Close'].iloc[-1]
                # Sanity check: put/call ratios are typically between 0.3 and 2.0
                if 0.3 <= ratio <= 2.0:
                    return (ratio, True)
        except:
            continue

    # All sources failed - return neutral fallback with flag
    return (1.0, False)


def normalize_put_call_to_score(pc_ratio):
    """Normalize Put/Call Ratio to 0-100 score (higher ratio = more fear = lower score)"""
    if pc_ratio < 0.7:
        return 100  # Extreme greed (very few puts)
    elif pc_ratio < 0.9:
        return 75
    elif pc_ratio < 1.1:
        return 50  # Neutral
    elif pc_ratio < 1.3:
        return 25
    else:
        return 0  # Extreme fear (many puts)


def calculate_distance_from_high(sp500_data):
    """Calculate distance from 52-week high"""
    try:
        ticker = yf.Ticker('^GSPC')
        hist = ticker.history(period='1y')
        if hist.empty:
            return 50

        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        distance = (current_price / high_52w - 1) * 100

        # Normalize to 0-100 (closer to high = more greed)
        if distance > -2:
            return 100  # Within 2% of high
        elif distance > -5:
            return 75
        elif distance > -10:
            return 50
        elif distance > -15:
            return 25
        else:
            return 0  # More than 15% below high
    except:
        return 50


@st.cache_data(ttl=get_cache_ttl("medium"))
def calculate_safe_haven_demand():
    """
    Calculate Gold/S&P 500 ratio (higher ratio = more fear)
    Cache TTL adapts to trading mode
    """
    try:
        gold = yf.Ticker('GLD')
        spy = yf.Ticker('SPY')

        gold_hist = gold.history(period='10d')
        spy_hist = spy.history(period='10d')

        if gold_hist.empty or spy_hist.empty:
            return 50

        gold_current = gold_hist['Close'].iloc[-1]
        spy_current = spy_hist['Close'].iloc[-1]

        gold_prev = gold_hist['Close'].iloc[0]
        spy_prev = spy_hist['Close'].iloc[0]

        # Calculate relative performance
        gold_return = (gold_current / gold_prev - 1) * 100
        spy_return = (spy_current / spy_prev - 1) * 100

        relative_perf = gold_return - spy_return

        # Normalize (gold outperforming = fear)
        if relative_perf < -3:
            return 100  # Stocks crushing gold = greed
        elif relative_perf < -1:
            return 75
        elif relative_perf < 1:
            return 50
        elif relative_perf < 3:
            return 25
        else:
            return 0  # Gold outperforming = fear
    except:
        return 50


@st.cache_data(ttl=get_cache_ttl("medium"))
def fetch_advance_decline_volume():
    """
    Fetch advance/decline volume ratio (simplified using SPY volume)
    Cache TTL adapts to trading mode
    """
    try:
        spy = yf.Ticker('SPY')
        hist = spy.history(period='5d')
        if hist.empty:
            return 50

        # Use price change as proxy for advance/decline
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = (current_price / prev_price - 1) * 100

        if change > 1:
            return 100
        elif change > 0.5:
            return 75
        elif change > -0.5:
            return 50
        elif change > -1:
            return 25
        else:
            return 0
    except:
        return 50


@st.cache_data(ttl=get_cache_ttl("medium"))
def fetch_new_highs_lows():
    """
    Fetch new highs vs new lows (simplified)
    Cache TTL adapts to trading mode
    """
    try:
        # Using Russell 2000 as breadth indicator
        rut = yf.Ticker('^RUT')
        hist = rut.history(period='1mo')
        if hist.empty:
            return 50

        current = hist['Close'].iloc[-1]
        month_high = hist['High'].max()
        month_low = hist['Low'].min()

        # Position within range
        position = (current - month_low) / (month_high - month_low) * 100

        return position
    except:
        return 50


@st.cache_data(ttl=get_cache_ttl("slow"))
def fetch_junk_bond_spread():
    """
    Fetch HYG/TLT spread (high yield vs treasuries)
    Cache TTL adapts to trading mode (fundamental data)
    """
    try:
        hyg = yf.Ticker('HYG')  # High yield corporate bonds
        tlt = yf.Ticker('TLT')  # Long-term treasuries

        hyg_hist = hyg.history(period='10d')
        tlt_hist = tlt.history(period='10d')

        if hyg_hist.empty or tlt_hist.empty:
            return 50

        hyg_return = (hyg_hist['Close'].iloc[-1] / hyg_hist['Close'].iloc[0] - 1) * 100
        tlt_return = (tlt_hist['Close'].iloc[-1] / tlt_hist['Close'].iloc[0] - 1) * 100

        spread = hyg_return - tlt_return

        # HYG outperforming = risk-on = greed
        if spread > 2:
            return 100
        elif spread > 0.5:
            return 75
        elif spread > -0.5:
            return 50
        elif spread > -2:
            return 25
        else:
            return 0
    except:
        return 50


def calculate_rsi(sp500_data):
    """Calculate RSI for S&P 500"""
    try:
        ticker = yf.Ticker('^GSPC')
        hist = ticker.history(period='1mo')
        if hist.empty or len(hist) < 14:
            return 50

        # Simple RSI calculation
        closes = hist['Close']
        deltas = closes.diff()
        gains = deltas.where(deltas > 0, 0).rolling(window=14).mean()
        losses = -deltas.where(deltas < 0, 0).rolling(window=14).mean()

        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]

        # Normalize RSI to 0-100 fear/greed
        if current_rsi > 70:
            return 100  # Overbought = greed
        elif current_rsi > 60:
            return 75
        elif current_rsi > 40:
            return 50
        elif current_rsi > 30:
            return 25
        else:
            return 0  # Oversold = fear
    except:
        return 50


def classify_fear_greed(score):
    """Classify fear/greed score into categories"""
    if score >= 75:
        category = "Extreme Greed"
        emoji = "💰"
        color = "#00CC96"
        gradient = "#00CC96, #26C281"
        interpretation = "Extreme Greed - Market may be overheated"
    elif score >= 55:
        category = "Greed"
        emoji = "😊"
        color = "#26C281"
        gradient = "#26C281, #95D5B2"
        interpretation = "Greed - Optimistic sentiment prevails"
    elif score >= 45:
        category = "Neutral"
        emoji = "😐"
        color = "#636EFA"
        gradient = "#FED766, #FED766"
        interpretation = "Neutral - Balanced sentiment"
    elif score >= 25:
        category = "Fear"
        emoji = "😰"
        color = "#FFA15A"
        gradient = "#FFB84D, #FF9F40"
        interpretation = "Fear - Cautious sentiment emerging"
    else:
        category = "Extreme Fear"
        emoji = "😱"
        color = "#EF553B"
        gradient = "#EF553B, #E74C3C"
        interpretation = "Extreme Fear - Market may be oversold"

    return {
        'score': int(score),
        'category': category,
        'emoji': emoji,
        'color': color,
        'gradient': gradient,
        'interpretation': interpretation
    }


@st.cache_data(ttl=300)
def calculate_fear_greed_level1(indices_data, market_breadth):
    """
    Fast Fear & Greed calculation using 5 indicators
    Performance: ~300ms first load, <50ms cached
    """
    scores = {}

    # Indicator 1: VIX (0ms - already have)
    if 'VIX' in indices_data:
        vix = indices_data['VIX']['price']
        scores['vix'] = normalize_vix_to_score(vix)
    else:
        scores['vix'] = 50

    # Indicator 2: Put/Call Ratio (+100ms)
    put_call_ratio, pc_available = fetch_put_call_ratio()
    scores['put_call_ratio'] = normalize_put_call_to_score(put_call_ratio)

    # Indicator 3: Market Breadth (0ms - already calculated)
    if market_breadth:
        # Map breadth status to 0-100
        if market_breadth['status'] == 'Strong':
            scores['market_breadth'] = 100
        elif market_breadth['status'] == 'Positive':
            scores['market_breadth'] = 75
        elif market_breadth['status'] == 'Weak':
            scores['market_breadth'] = 25
        else:
            scores['market_breadth'] = 0
    else:
        scores['market_breadth'] = 50

    # Indicator 4: Distance from 52W High (+100ms)
    sp500_data = indices_data.get('S&P 500', {})
    scores['distance_52w_high'] = calculate_distance_from_high(sp500_data)

    # Indicator 5: Safe Haven Demand (+100ms)
    scores['safe_haven_demand'] = calculate_safe_haven_demand()

    # Weighted average using pre-calculated weights
    fear_greed_score = (
        scores['vix'] * FEAR_GREED_WEIGHTS_L1['vix'] +
        scores['put_call_ratio'] * FEAR_GREED_WEIGHTS_L1['put_call_ratio'] +
        scores['market_breadth'] * FEAR_GREED_WEIGHTS_L1['market_breadth'] +
        scores['distance_52w_high'] * FEAR_GREED_WEIGHTS_L1['distance_52w_high'] +
        scores['safe_haven_demand'] * FEAR_GREED_WEIGHTS_L1['safe_haven_demand']
    )

    result = classify_fear_greed(fear_greed_score)
    result['num_indicators'] = 5
    result['components'] = scores  # Include component scores for analysis
    result['weights'] = FEAR_GREED_WEIGHTS_L1  # Include weights for visualization
    result['put_call_ratio'] = put_call_ratio  # Include for options flow analysis
    result['put_call_available'] = pc_available  # Flag for UI to show data quality
    return result


def calculate_fear_greed_level2(indices_data, market_breadth):
    """
    Balanced Fear & Greed calculation using 9 indicators
    Performance: ~1.2s first load

    NOTE: Cache removed to ensure real-time updates when switching between levels.
    The individual data fetch functions are still cached (ttl=600s) for performance.
    """
    scores = {}

    # Get all Level 1 indicators
    level1_result = calculate_fear_greed_level1(indices_data, market_breadth)

    # Recalculate base indicators for proper weighting
    if 'VIX' in indices_data:
        scores['vix'] = normalize_vix_to_score(indices_data['VIX']['price'])
    else:
        scores['vix'] = 50

    put_call_ratio_l2, pc_available_l2 = fetch_put_call_ratio()
    scores['put_call_ratio'] = normalize_put_call_to_score(put_call_ratio_l2)

    if market_breadth:
        if market_breadth['status'] == 'Strong':
            scores['market_breadth'] = 100
        elif market_breadth['status'] == 'Positive':
            scores['market_breadth'] = 75
        elif market_breadth['status'] == 'Weak':
            scores['market_breadth'] = 25
        else:
            scores['market_breadth'] = 0
    else:
        scores['market_breadth'] = 50

    scores['distance_52w_high'] = calculate_distance_from_high(indices_data.get('S&P 500', {}))
    scores['safe_haven_demand'] = calculate_safe_haven_demand()

    # Additional Level 2 indicators
    scores['advance_decline'] = fetch_advance_decline_volume()
    scores['new_highs_lows'] = fetch_new_highs_lows()
    scores['junk_bond_spread'] = fetch_junk_bond_spread()
    scores['rsi'] = calculate_rsi(indices_data.get('S&P 500', {}))

    # Weighted average using Level 2 weights
    fear_greed_score = sum(scores[key] * FEAR_GREED_WEIGHTS_L2[key] for key in FEAR_GREED_WEIGHTS_L2.keys())

    result = classify_fear_greed(fear_greed_score)
    result['num_indicators'] = 9
    result['components'] = scores  # Include component scores for analysis
    result['weights'] = FEAR_GREED_WEIGHTS_L2  # Include weights for visualization
    result['put_call_ratio'] = put_call_ratio_l2  # Include for options flow analysis
    result['put_call_available'] = pc_available_l2  # Flag for UI to show data quality
    return result


def calculate_fear_greed_level3(indices_data, market_breadth):
    """
    Complete Fear & Greed calculation using 9 real indicators
    (Level 3 placeholders removed - they were pulling score to neutral)
    Performance: ~2s first load

    NOTE: Cache removed to ensure real-time updates when switching between levels.
    This is identical to Level 2 for now until we implement:
    - Options Skew API
    - Margin Debt API (FINRA)
    - AAII Sentiment API
    - Treasury/Stock Yield Gap calculation
    """
    # For now, Level 3 = Level 2 (same 9 indicators with same weights)
    # Placeholders were causing scores to converge to neutral
    return calculate_fear_greed_level2(indices_data, market_breadth)


def render_page():
    """Main market overview page with 4 sections"""
    st.title("📊 Market Overview & Economy")
    st.markdown("**Understand broad market health, trends, and economic indicators to inform your investment decisions**")

    # Display current trading mode
    render_mode_info()

    # Fetch all data BEFORE creating tabs (so AI tab has access to everything)
    # This ensures AI Intelligence tab works even if user goes directly to it
    with st.spinner("Loading market data..."):
        # Market Pulse data (use session snapshot to keep a consistent view)
        indices_data, market_breadth, market_health, market_ts = get_market_snapshot(ttl_seconds=15)

        # Sector Rotation data (session snapshot)
        sector_data, sector_ts = get_sector_snapshot(ttl_seconds=15)
        rotation_signal = calculate_rotation_signal(sector_data) if sector_data else None

        # Economic Indicators data (session snapshot)
        fred_data, fred_ts = get_fred_snapshot(ttl_seconds=15)
        yield_signal = calculate_yield_curve_signal(fred_data) if fred_data else None
        inflation_signal = calculate_inflation_signal(fred_data) if fred_data else None

    # Create tabs for the sections
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Market Pulse",
        "🔄 Sector Rotation",
        "📈 Economic Indicators",
        "🔗 Correlating Factors",
        "🔬 Advanced Visuals",
        "🤖 AI Market Intelligence",
        "🔧 Debug"
    ])

    with tab1:
        # Display Market Pulse section (data already fetched above)

        # Display Market Pulse section
        st.markdown("## 🎯 Market Pulse")
        st.markdown("Real-time snapshot of major market indices and overall market health")

        if not indices_data:
            st.error("Unable to load market data. Please try again.")
        else:
            # Market Indices Display
            st.markdown("### 📊 Major Indices")

            index_cols = st.columns(5)
            display_order = ['S&P 500', 'NASDAQ', 'Dow Jones', 'Russell 2000', 'VIX']

            for col, index_name in zip(index_cols, display_order):
                if index_name in indices_data:
                    data = indices_data[index_name]
                    with col:
                        delta_color = "normal" if index_name != 'VIX' else "inverse"
                        st.metric(
                            index_name,
                            format_money(data['price'], show_symbol=(index_name != 'VIX')),
                            f"{data['pct_change']:+.2f}%",
                            delta_color=delta_color
                        )

            # Market Health Score
            if market_health:
                st.markdown("---")
                st.markdown("### 💓 Market Health Score")

                health_cols = st.columns([1, 3])

                with health_cols[0]:
                    st.metric(
                        "Health Score",
                        f"{market_health['score']}/100",
                        delta=market_health['emoji']
                    )

                with health_cols[1]:
                    st.markdown(f"**{market_health['category']}**")
                    st.caption(f"Based on S&P 500 momentum, VIX level, and market breadth")

                    if market_breadth:
                        st.caption(f"Market Breadth: {market_breadth['status']} (Score: {market_breadth['score']:.2f}%)")

                # Add detailed calculation breakdown
                with st.expander("📊 How is this calculated?", expanded=False):
                    st.markdown("#### Health Score Calculation Breakdown")
                    st.markdown(f"**Starting Point**: 50 (Neutral baseline)")
                    st.markdown("")

                    # Factor 1: S&P 500
                    if 'S&P 500' in indices_data:
                        sp_pct = indices_data['S&P 500']['pct_change']
                        if sp_pct > 1:
                            impact = "+20"
                            reason = "Strong positive momentum (>1%)"
                        elif sp_pct > 0:
                            impact = "+10"
                            reason = "Positive momentum (0% to 1%)"
                        elif sp_pct > -1:
                            impact = "-10"
                            reason = "Slightly negative (-1% to 0%)"
                        else:
                            impact = "-20"
                            reason = "Strongly negative (<-1%)"
                        st.markdown(f"**Factor 1 - S&P 500 Momentum** ({sp_pct:+.2f}%): **{impact} points**")
                        st.caption(f"↳ {reason}")

                    # Factor 2: VIX
                    if 'VIX' in indices_data:
                        vix = indices_data['VIX']['price']
                        if vix < 15:
                            impact = "+15"
                            reason = "Very calm market (VIX < 15)"
                        elif vix < 20:
                            impact = "+10"
                            reason = "Calm market (VIX 15-20)"
                        elif vix < 30:
                            impact = "-10"
                            reason = "Elevated volatility (VIX 20-30)"
                        else:
                            impact = "-15"
                            reason = "High fear (VIX > 30)"
                        st.markdown(f"**Factor 2 - VIX Level** ({vix:.2f}): **{impact} points**")
                        st.caption(f"↳ {reason}")

                    # Factor 3: Market Breadth
                    if market_breadth:
                        if market_breadth['status'] == 'Strong':
                            impact = "+15"
                        elif market_breadth['status'] == 'Positive':
                            impact = "+10"
                        elif market_breadth['status'] == 'Weak':
                            impact = "-10"
                        else:
                            impact = "-15"
                        st.markdown(f"**Factor 3 - Market Breadth** ({market_breadth['status']}): **{impact} points**")
                        st.caption(f"↳ Based on SPY position vs 5-day average ({market_breadth['score']:+.2f}%)")

                    st.markdown("---")
                    st.markdown(f"**Final Score**: {market_health['score']}/100 → {market_health['category']} {market_health['emoji']}")
                    st.caption("Score ranges: 0-29 = Weak 🚨, 30-49 = Cautious ⚠️, 50-69 = Neutral ➡️, 70-100 = Healthy 💪")

                # Fear & Greed Index - Professional Analysis
                st.markdown("---")
                st.markdown("### 😱💰 Fear & Greed Index - Professional Analysis")

                # User selectable level
                fear_greed_col1, fear_greed_col2 = st.columns([2, 1])

                with fear_greed_col1:
                    fear_greed_level = st.selectbox(
                        "Analysis Depth",
                        options=[
                            ("Fast (5 indicators, ~0.3s)", 1),
                            ("Balanced (9 indicators, ~1.2s)", 2)
                        ],
                        index=0,  # Default to fastest
                        format_func=lambda x: x[0],
                        key="fear_greed_level_selector",
                        help="Choose analysis depth:\n\n"
                             "**Fast**: VIX, Put/Call Ratio, Market Breadth, Distance from 52W High, Safe Haven Demand\n\n"
                             "**Balanced**: All Fast indicators + Advance/Decline Volume, New Highs/Lows, Junk Bond Demand, RSI\n\n"
                             "Note: Level 3 (Complete) temporarily disabled - placeholders were causing inaccurate scores"
                    )

                with fear_greed_col2:
                    st.caption(f"📊 Using {5 if fear_greed_level[1] == 1 else 9} indicators")

                # Calculate based on user selection
                with st.spinner(f"Calculating Fear & Greed Index..."):
                    if fear_greed_level[1] == 1:
                        fear_greed = calculate_fear_greed_level1(indices_data, market_breadth)
                    elif fear_greed_level[1] == 2:
                        fear_greed = calculate_fear_greed_level2(indices_data, market_breadth)
                    else:
                        fear_greed = calculate_fear_greed_level3(indices_data, market_breadth)

                if fear_greed:
                    # Initialize history manager
                    history_manager = FearGreedHistory()

                    # Save current reading to history
                    if 'components' in fear_greed and 'weights' in fear_greed:
                        history_manager.add_record(
                            score=fear_greed['score'],
                            category=fear_greed['category'],
                            level=fear_greed_level[1],
                            components=fear_greed['components']
                        )

                    # === MAIN SCORE DISPLAY ===
                    fg_cols = st.columns([1, 3])

                    with fg_cols[0]:
                        st.metric(
                            "Fear & Greed",
                            f"{fear_greed['emoji']} {fear_greed['score']}/100",
                            delta=fear_greed['category']
                        )
                        # Show level being used
                        level_name = "Fast" if fear_greed_level[1] == 1 else ("Balanced" if fear_greed_level[1] == 2 else "Complete")
                        st.caption(f"Level: {level_name}")

                    with fg_cols[1]:
                        # Progress bar with color
                        st.markdown(f"<div style='background: linear-gradient(to right, {fear_greed['gradient']}); height: 30px; border-radius: 5px; display: flex; align-items: center; padding: 0 10px;'><span style='color: white; font-weight: bold;'>{fear_greed['interpretation']}</span></div>", unsafe_allow_html=True)
                        st.caption(f"Based on {fear_greed['num_indicators']} market sentiment indicators")

                    st.markdown("---")

                    # === TIER 1: CORE ANALYSIS ===
                    with st.expander("📊 **Tier 1: Component Breakdown & Trends** (Professional Analysis)", expanded=True):
                        tier1_col1, tier1_col2 = st.columns([1, 1])

                        with tier1_col1:
                            # Component breakdown
                            if 'components' in fear_greed and 'weights' in fear_greed:
                                render_component_breakdown(
                                    components=fear_greed['components'],
                                    weights=fear_greed['weights'],
                                    overall_score=fear_greed['score']
                                )

                        with tier1_col2:
                            # Trend analysis
                            render_trend_analysis(history_manager, fear_greed['score'])

                        # Divergence alerts (full width)
                        st.markdown("---")
                        if 'components' in fear_greed:
                            divergences = history_manager.detect_divergence(fear_greed['components'])
                            render_divergence_alerts(divergences)

                    # === TIER 2: ADVANCED CONTEXT ===
                    with st.expander("🎯 **Tier 2: Historical Context & Sector Analysis**", expanded=False):
                        tier2_col1, tier2_col2 = st.columns([1, 1])

                        with tier2_col1:
                            # Historical percentile
                            render_percentile_analysis(history_manager, fear_greed['score'])

                        with tier2_col2:
                            # Sector rotation heatmap
                            if sector_data:
                                render_sector_rotation_heatmap(sector_data)

                    # === TIER 3: INSTITUTIONAL INSIGHTS ===
                    with st.expander("🌐 **Tier 3: Cross-Asset & Options Flow** (Institutional Grade)", expanded=False):
                        tier3_col1, tier3_col2 = st.columns([1, 1])

                        with tier3_col1:
                            # Cross-asset dashboard
                            render_cross_asset_dashboard()

                        with tier3_col2:
                            # Options flow detail
                            if 'put_call_ratio' in fear_greed:
                                if fear_greed.get('put_call_available', False):
                                    render_options_flow_detail(fear_greed['put_call_ratio'])
                                else:
                                    st.warning("⚠️ Put/Call Ratio Data Unavailable")
                                    st.info("CBOE Put/Call ratio tickers (^PCALL, ^PCCE, ^CPCE) are currently unavailable from Yahoo Finance. Using neutral fallback value (1.0) for Fear & Greed calculation.")
                                    st.caption("This affects the accuracy of the Fear & Greed Index by approximately 20% (Level 1) or 11% (Level 2).")
                            else:
                                st.info("Put/Call ratio data unavailable")

    with tab2:
        # Display Sector Rotation (data already fetched above)
        if not sector_data:
            st.error("Unable to load sector data. Please try again.")
        else:
            # Call the existing render function (it handles its own display)
            render_sector_rotation()

    with tab3:
        # Display Economic Indicators (data already fetched above)
        if not fred_data:
            st.warning("⚠️ FRED API key not configured. Economic indicators unavailable.")
            st.info("Add your FRED_API_KEY to .streamlit/secrets.toml to enable this feature")
        else:
            # Call the existing render function (it handles its own display)
            render_economic_indicators()

    with tab4:
        # Correlating Factors tab
        render_correlating_factors_market()

    with tab5:
        # Advanced Visual Analysis tab
        render_market_advanced_visual_analysis(indices_data, market_health)

    with tab6:
        # Pass all collected data to AI Intelligence
        render_ai_market_intelligence(
            indices_data, market_health, sector_data, rotation_signal,
            fred_data, yield_signal, inflation_signal
        )

    with tab7:
        # Debug tab
        render_debug_tab_market(indices_data, market_health, sector_data, fred_data)


# ========================================
# SECTION 1: MARKET PULSE
# ========================================

@st.cache_data(ttl=60)  # Cache for 1 minute (real-time feel, but reduced API calls)
@st.cache_data(ttl=15, show_spinner="Fetching market indices...")
def fetch_market_indices():
    """
    Fetch major market indices in parallel for speed

    Performance: ~1-2 seconds with parallel fetching
    """
    indices = {
        'S&P 500': '^GSPC',
        'NASDAQ': '^IXIC',
        'Dow Jones': '^DJI',
        'Russell 2000': '^RUT',
        'VIX': '^VIX'
    }

    results = {}

    def fetch_single_index(name, ticker):
        try:
            stock = yf.Ticker(ticker)
            # Primary attempt: get a small recent history via the Ticker.history API
            hist = stock.history(period='5d')

            # If history is empty try a more robust download fallback (handles some provider/timezone cases)
            if hist is None or hist.empty:
                try:
                    # yf.download can succeed where Ticker.history returns empty for some tickers
                    hist = yf.download(ticker, period='5d', progress=False)
                except Exception:
                    hist = None

            if hist is None or hist.empty:
                # No data available even after fallback; return None so caller skips this index
                return name, None

            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            pct_change = (change / prev_close * 100) if prev_close != 0 else 0

            return name, {
                'ticker': ticker,
                'price': current_price,
                'change': change,
                'pct_change': pct_change,
                'history': hist
            }
        except Exception as e:
            return name, None

    # Parallel fetching for speed
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_single_index, name, ticker): name
                  for name, ticker in indices.items()}

        for future in as_completed(futures):
            name, data = future.result()
            if data:
                results[name] = data

    return results


def _now_ts():
    import time as _t
    return _t.time()


def get_market_snapshot(ttl_seconds: int = 15):
    """Return a consistent market snapshot (indices, breadth, health, timestamp).

    Uses st.session_state['market_snapshot'] as a short-lived session cache and
    falls back to calling the cached `fetch_market_indices()` and `calculate_market_breadth()`.
    """
    key = 'market_snapshot'
    snapshot = st.session_state.get(key)

    if snapshot:
        age = _now_ts() - snapshot.get('timestamp', 0)
        if age < ttl_seconds:
            return snapshot['indices_data'], snapshot['breadth_data'], snapshot['market_health'], snapshot['timestamp']

    # compute fresh
    indices_data = fetch_market_indices()
    breadth_data = calculate_market_breadth()
    market_health = calculate_market_health_score(indices_data, breadth_data)
    ts = _now_ts()

    st.session_state[key] = {
        'timestamp': ts,
        'indices_data': indices_data,
        'breadth_data': breadth_data,
        'market_health': market_health
    }

    return indices_data, breadth_data, market_health, ts


def get_sector_snapshot(ttl_seconds: int = 15):
    key = 'sector_snapshot'
    snapshot = st.session_state.get(key)

    if snapshot:
        age = _now_ts() - snapshot.get('timestamp', 0)
        if age < ttl_seconds:
            return snapshot['sector_data'], snapshot['timestamp']

    sector_data = fetch_sector_performance()
    ts = _now_ts()
    st.session_state[key] = {'timestamp': ts, 'sector_data': sector_data}
    return sector_data, ts


def get_fred_snapshot(ttl_seconds: int = 15):
    key = 'fred_snapshot'
    snapshot = st.session_state.get(key)

    if snapshot:
        age = _now_ts() - snapshot.get('timestamp', 0)
        if age < ttl_seconds:
            return snapshot['fred_data'], snapshot['timestamp']

    fred_data = fetch_fred_data()
    ts = _now_ts()
    st.session_state[key] = {'timestamp': ts, 'fred_data': fred_data}
    return fred_data, ts


@st.cache_data(ttl=15, show_spinner="Calculating market breadth...")  # Conservative: 15s TTL
def calculate_market_breadth():
    """
    Calculate market breadth using S&P 500 advance/decline

    Performance: ~2-3 seconds
    Note: This is a simplified version. For real-time breadth,
    we'd need a data provider like Finnhub or Polygon with market breadth APIs
    """
    try:
        # Using SPY ETF as proxy for S&P 500
        spy = yf.Ticker('SPY')
        hist = spy.history(period='5d')

        if hist.empty:
            return None

        # Simple breadth indicator: compare current vs 5-day average
        current = hist['Close'].iloc[-1]
        avg_5d = hist['Close'].mean()

        breadth_score = (current / avg_5d - 1) * 100

        # Categorize
        if breadth_score > 1:
            status = "Strong"
            color = "#00CC96"
        elif breadth_score > 0:
            status = "Positive"
            color = "#26C281"
        elif breadth_score > -1:
            status = "Weak"
            color = "#F39C12"
        else:
            status = "Very Weak"
            color = "#E74C3C"

        return {
            'score': breadth_score,
            'status': status,
            'color': color
        }
    except Exception as e:
        return None


def calculate_market_health_score(indices_data, breadth_data):
    """
    Composite market health score (0-100)

    Factors:
    - S&P 500 position vs recent trend (40%)
    - VIX level (30%)
    - Market breadth (30%)
    """
    score = 50  # Neutral baseline

    # Factor 1: S&P 500 momentum (40 points)
    if 'S&P 500' in indices_data:
        sp_pct = indices_data['S&P 500']['pct_change']
        if sp_pct > 1:
            score += 20
        elif sp_pct > 0:
            score += 10
        elif sp_pct > -1:
            score -= 10
        else:
            score -= 20

    # Factor 2: VIX level (30 points)
    if 'VIX' in indices_data:
        vix = indices_data['VIX']['price']
        if vix < 15:
            score += 15  # Very calm
        elif vix < 20:
            score += 10  # Calm
        elif vix < 30:
            score -= 10  # Elevated
        else:
            score -= 15  # High fear

    # Factor 3: Market breadth (30 points)
    if breadth_data:
        if breadth_data['status'] == 'Strong':
            score += 15
        elif breadth_data['status'] == 'Positive':
            score += 10
        elif breadth_data['status'] == 'Weak':
            score -= 10
        else:
            score -= 15

    # Clamp to 0-100
    score = max(0, min(100, score))

    # Categorize
    if score >= 70:
        category = "Healthy"
        emoji = "💪"
        color = "#00CC96"
    elif score >= 50:
        category = "Neutral"
        emoji = "➡️"
        color = "#636EFA"
    elif score >= 30:
        category = "Cautious"
        emoji = "⚠️"
        color = "#F39C12"
    else:
        category = "Weak"
        emoji = "🚨"
        color = "#E74C3C"

    return {
        'score': score,
        'category': category,
        'emoji': emoji,
        'color': color
    }


def render_market_pulse():
    """Section 1: Real-time market pulse with health indicators"""
    st.markdown("## 🎯 Market Pulse")
    st.markdown("Real-time market indices, volatility, and overall market health")

    # Respect the session snapshot; provide manual refresh for real-time users
    refresh_col1, refresh_col2 = st.columns([4, 1])
    with refresh_col1:
        st.caption("Data refreshed conservatively (TTL 15s). Click the button to force an immediate refresh.")
        st.warning("⚠️ Pressing Refresh will clear all cached page data (global cache) — this forces immediate API calls and may increase rate limit usage.")
    with refresh_col2:
        if st.button("🔄 Refresh Market Data"):
            # Clear snapshot to force fresh fetch next call
            if 'market_snapshot' in st.session_state:
                del st.session_state['market_snapshot']
            # Also clear global Streamlit cache so every cached function refreshes
            # (Warning: this will trigger more API calls and may increase rate-limit usage)
            st.cache_data.clear()

    with st.spinner("Loading market data..."):
        with PerformanceMonitor("market_pulse_load"):
            # Get consistent snapshot
            indices_data, breadth_data, _, market_ts = get_market_snapshot(ttl_seconds=15)

    if not indices_data:
        st.error("Unable to load market data. Please try again.")
        return

    # Calculate composite health score (should match snapshot's value if available)
    health_score = calculate_market_health_score(indices_data, breadth_data)

    # Display Market Health Score prominently
    st.markdown("---")
    st.markdown("### 🏥 Market Health Score")

    health_cols = st.columns([1, 2, 1])

    with health_cols[0]:
        st.metric(
            "Health Score",
            f"{health_score['emoji']} {health_score['score']}/100",
            delta=health_score['category']
        )

    # Show last-updated timestamp in the health area
    st.caption(f"Last updated: {pd.to_datetime(market_ts, unit='s').strftime('%Y-%m-%d %H:%M:%S')}")

    with health_cols[1]:
        # Health score progress bar
        st.progress(health_score['score'] / 100, text=f"{health_score['category']} Market Conditions")

    with health_cols[2]:
        if health_score['score'] >= 70:
            st.success("**Strong market conditions**")
        elif health_score['score'] >= 50:
            st.info("**Neutral market conditions**")
        elif health_score['score'] >= 30:
            st.warning("**Cautious market conditions**")
        else:
            st.error("**Weak market conditions**")

    st.markdown("---")

    # Display Major Indices
    st.markdown("### 📊 Major Indices")

    # Create 5 columns for the 5 indices
    idx_cols = st.columns(5)

    index_order = ['S&P 500', 'NASDAQ', 'Dow Jones', 'Russell 2000', 'VIX']

    for idx, col in enumerate(idx_cols):
        if idx < len(index_order):
            index_name = index_order[idx]
            if index_name in indices_data:
                data = indices_data[index_name]

                with col:
                    # Color based on change
                    delta_color = "normal" if index_name == 'VIX' else "normal"

                    st.metric(
                        index_name,
                        format_money(data['price'], show_symbol=(index_name != 'VIX')),
                        delta=f"{data['change']:+.2f} ({data['pct_change']:+.2f}%)",
                        delta_color=delta_color
                    )

    # Market Breadth
    if breadth_data:
        st.markdown("---")
        st.markdown("### 📈 Market Breadth")

        breadth_cols = st.columns([1, 2, 1])

        with breadth_cols[0]:
            st.metric(
                "Breadth Status",
                breadth_data['status'],
                delta=f"Score: {breadth_data['score']:.2f}%"
            )

        with breadth_cols[1]:
            st.markdown(f"""
            **What is Market Breadth?**
            Market breadth measures how many stocks are participating in a market move.
            Strong breadth (more stocks advancing) = healthy market.
            Weak breadth (few stocks advancing) = fragile market.
            """)

        with breadth_cols[2]:
            if breadth_data['status'] in ['Strong', 'Positive']:
                st.success("✅ Broad participation")
            else:
                st.warning("⚠️ Narrow leadership")


# ========================================
# SECTION 2: SECTOR ROTATION
# ========================================

@st.cache_data(ttl=15, show_spinner="Fetching sector performance...")  # Conservative: 15s TTL
def fetch_sector_performance():
    """
    Fetch sector ETF performance in parallel

    Performance: ~1-2 seconds with parallel fetching
    """
    # 11 major sector ETFs
    sectors = {
        'Technology': 'XLK',
        'Financials': 'XLF',
        'Healthcare': 'XLV',
        'Energy': 'XLE',
        'Industrials': 'XLI',
        'Consumer Discretionary': 'XLY',
        'Consumer Staples': 'XLP',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Materials': 'XLB',
        'Communication': 'XLC'
    }

    results = {}

    def fetch_single_sector(name, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')  # 1 month for trend

            if hist.empty:
                return name, None

            current_price = hist['Close'].iloc[-1]
            month_ago_price = hist['Close'].iloc[0]
            change_1m = ((current_price - month_ago_price) / month_ago_price * 100)

            # 5-day performance
            if len(hist) >= 5:
                week_ago_price = hist['Close'].iloc[-5]
                change_5d = ((current_price - week_ago_price) / week_ago_price * 100)
            else:
                change_5d = 0

            # 1-day performance
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                change_1d = ((current_price - prev_close) / prev_close * 100)
            else:
                change_1d = 0

            return name, {
                'ticker': ticker,
                'price': current_price,
                'change_1d': change_1d,
                'change_5d': change_5d,
                'change_1m': change_1m,
                'history': hist
            }
        except Exception as e:
            return name, None

    # Parallel fetching
    with ThreadPoolExecutor(max_workers=11) as executor:
        futures = {executor.submit(fetch_single_sector, name, ticker): name
                  for name, ticker in sectors.items()}

        for future in as_completed(futures):
            name, data = future.result()
            if data:
                results[name] = data

    return results


def calculate_rotation_signal(sector_data, primary_timeframe='change_1m'):
    """
    Determine if market is rotating from Growth to Value or vice versa

    Args:
        sector_data: Dictionary of sector performance data
        primary_timeframe: Which timeframe to use for primary signal
                          ('change_5d', 'change_1m', 'change_3m', etc.)

    Uses user-selected timeframe for primary signal
    Uses 5-day performance to detect if rotation is strengthening/weakening

    Growth sectors: Technology, Communication, Consumer Discretionary
    Value sectors: Financials, Energy, Utilities, Consumer Staples
    """
    if not sector_data:
        return None

    growth_sectors = ['Technology', 'Communication', 'Consumer Discretionary']
    value_sectors = ['Financials', 'Energy', 'Utilities', 'Consumer Staples']

    # Calculate average performance for selected primary timeframe AND 5-day for trend
    growth_perf_primary = []
    value_perf_primary = []
    growth_perf_5d = []
    value_perf_5d = []

    for sector, data in sector_data.items():
        if sector in growth_sectors:
            # Handle special "all-time" option
            if primary_timeframe == 'change_all':
                # Use 1-month as fallback for "all-time" since we fetch 1mo of history
                perf = data.get('change_1m', 0)
            elif primary_timeframe in data:
                perf = data[primary_timeframe]
            else:
                perf = 0
            growth_perf_primary.append(perf)
            growth_perf_5d.append(data.get('change_5d', 0))
        elif sector in value_sectors:
            # Handle special "all-time" option
            if primary_timeframe == 'change_all':
                perf = data.get('change_1m', 0)
            elif primary_timeframe in data:
                perf = data[primary_timeframe]
            else:
                perf = 0
            value_perf_primary.append(perf)
            value_perf_5d.append(data.get('change_5d', 0))

    if not growth_perf_primary or not value_perf_primary:
        return None

    # Primary signal: User-selected timeframe
    avg_growth = sum(growth_perf_primary) / len(growth_perf_primary)
    avg_value = sum(value_perf_primary) / len(value_perf_primary)
    difference = avg_growth - avg_value

    # Secondary: 5-day for trend direction (only if different from primary)
    avg_growth_5d = sum(growth_perf_5d) / len(growth_perf_5d) if growth_perf_5d else 0
    avg_value_5d = sum(value_perf_5d) / len(value_perf_5d) if value_perf_5d else 0
    difference_5d = avg_growth_5d - avg_value_5d

    # Determine signal based on 1-month performance
    if difference > 1.5:
        signal = "Growth Outperforming"
        emoji = "🚀"
        color = "#00CC96"
        interpretation = "Money flowing into growth sectors (Tech, Communication)"
    elif difference < -1.5:
        signal = "Value Outperforming"
        emoji = "🏦"
        color = "#636EFA"
        interpretation = "Money flowing into value sectors (Financials, Energy) - defensive positioning"
    else:
        signal = "Balanced"
        emoji = "⚖️"
        color = "#95A5A6"
        interpretation = "No clear rotation - balanced market"

    # Trend indicator: is rotation strengthening or weakening?
    # Only show trend if primary timeframe is different from 5-day
    if primary_timeframe != 'change_5d':
        rotation_strengthening = (difference > 0 and difference_5d > 0) or (difference < 0 and difference_5d < 0)
    else:
        rotation_strengthening = None  # No trend comparison if primary is 5-day

    return {
        'signal': signal,
        'emoji': emoji,
        'color': color,
        'interpretation': interpretation,
        'difference': difference,
        'avg_growth': avg_growth,
        'avg_value': avg_value,
        # Additional time-based metrics
        'difference_5d': difference_5d,
        'avg_growth_5d': avg_growth_5d,
        'avg_value_5d': avg_value_5d,
        'rotation_strengthening': rotation_strengthening,
        'primary_timeframe': primary_timeframe
    }


def render_sector_rotation():
    """Section 2: Sector performance and rotation signals"""
    st.markdown("## 🔄 Sector Rotation & Money Flow")
    st.markdown("Track where institutional money is moving and identify sector rotation patterns")

    # Refresh UI + session snapshot support
    c1, c2 = st.columns([4, 1])
    with c1:
        st.caption("Sector data cached conservatively (TTL 15s). Use the refresh button to force immediate update.")
        st.warning("⚠️ Refresh will clear the global page cache — network/API calls will run immediately and may increase rate-limit usage.")
    with c2:
        if st.button("🔄 Refresh Sectors"):
            if 'sector_snapshot' in st.session_state:
                del st.session_state['sector_snapshot']
            st.cache_data.clear()

    with st.spinner("Loading sector data..."):
        with PerformanceMonitor("sector_rotation_load"):
            sector_data, sector_ts = get_sector_snapshot(ttl_seconds=15)

    if not sector_data:
        st.error("Unable to load sector data. Please try again.")
        return

    # Timeframe selector for rotation analysis
    st.markdown("---")
    st.markdown("### 🔄 Sector Rotation Signal")

    timeframe_col1, timeframe_col2 = st.columns([2, 2])

    with timeframe_col1:
        # Provide 4 timeframe options (we fetch 1 month of history, so that's our max)
        selected_timeframe = st.selectbox(
            "📅 Rotation Analysis Timeframe",
            options=[
                ("1-Day (Intraday)", "change_1d"),
                ("5-Day (Short-term)", "change_5d"),
                ("1-Month (Medium-term)", "change_1m"),
                ("1-Month Full Range (All Data)", "change_all"),  # Same as change_1m since we fetch 1mo
            ],
            index=2,  # Default to 1-Month
            format_func=lambda x: x[0],
            key="sector_rotation_timeframe",
            help="**Timeframe Guide**:\n\n"
                 "- **1-Day**: Today's rotation (most reactive, very noisy)\n"
                 "- **5-Day**: Recent week momentum shifts (short-term)\n"
                 "- **1-Month**: ⭐ Best balance - real rotation trends without noise\n"
                 "- **1-Month Full Range**: Same as 1-Month (we fetch 1 month of data)\n\n"
                 "**Note**: Data is fetched for the past ~30 calendar days. "
                 "Longer timeframes are more stable but slower to detect new rotations."
        )
        timeframe_key = selected_timeframe[1]
        timeframe_label = selected_timeframe[0]

    with timeframe_col2:
        st.caption(f"📊 Analyzing rotation using **{timeframe_label}** performance data")
        st.caption("💡 Compare different timeframes to see short vs long-term rotation trends")

    # Calculate rotation signal with selected timeframe
    rotation_signal = calculate_rotation_signal(sector_data, primary_timeframe=timeframe_key)

    # Display Rotation Signal
    if rotation_signal:

        rotation_cols = st.columns([1, 2, 1])

        with rotation_cols[0]:
            # Show trend arrow (only if comparing to 5-day)
            if rotation_signal.get('rotation_strengthening') is not None:
                if rotation_signal.get('rotation_strengthening'):
                    trend_arrow = "📈" if rotation_signal['difference'] > 0 else "📉"
                    trend_text = "Strengthening"
                else:
                    trend_arrow = "🔄"
                    trend_text = "Weakening"
                delta_text = f"{trend_arrow} {trend_text}"
            else:
                delta_text = None

            # Use selected timeframe in label
            timeframe_display = timeframe_label.split('(')[0].strip()  # Get "5-Day", "1-Month", etc.

            st.metric(
                f"Rotation Status",
                f"{rotation_signal['emoji']} {rotation_signal['signal']}",
                delta=delta_text
            )
            st.caption(f"Analyzing: {timeframe_display}")

        with rotation_cols[1]:
            st.markdown(f"**{rotation_signal['interpretation']}**")
            # Show primary timeframe performance
            st.caption(f"📊 {timeframe_display}: Growth {rotation_signal['avg_growth']:+.2f}% | Value {rotation_signal['avg_value']:+.2f}% (Spread: {rotation_signal['difference']:+.2f}%)")
            # Show 5-day for comparison (only if primary is not 5-day)
            if timeframe_key != 'change_5d':
                st.caption(f"📆 5-Day: Growth {rotation_signal.get('avg_growth_5d', 0):+.2f}% | Value {rotation_signal.get('avg_value_5d', 0):+.2f}% (Spread: {rotation_signal.get('difference_5d', 0):+.2f}%)")

        with rotation_cols[2]:
            if rotation_signal['signal'] == "Growth Outperforming":
                st.info("📈 Risk-on sentiment")
            elif rotation_signal['signal'] == "Value Outperforming":
                st.warning("⚠️ Risk-off sentiment")
            else:
                st.success("✅ Balanced market")

    st.markdown("---")

    # Show last-updated time so users can see snapshot freshness
    if sector_ts:
        st.caption(f"Last updated: {pd.to_datetime(sector_ts, unit='s').strftime('%Y-%m-%d %H:%M:%S')}")

    # Sector Performance Table
    st.markdown("### 📊 Sector Performance")

    # Sort by 5-day performance
    sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]['change_5d'], reverse=True)

    # Display top 3 and bottom 3
    top3 = sorted_sectors[:3]
    bottom3 = sorted_sectors[-3:]

    perf_cols = st.columns(2)

    with perf_cols[0]:
        st.markdown("#### 🔥 Top Performers (5D)")
        for name, data in top3:
            st.metric(
                name,
                f"{data['ticker']}",
                delta=f"{data['change_5d']:+.2f}%"
            )

    with perf_cols[1]:
        st.markdown("#### ❄️ Bottom Performers (5D)")
        for name, data in bottom3:
            st.metric(
                name,
                f"{data['ticker']}",
                delta=f"{data['change_5d']:+.2f}%",
                delta_color="inverse"
            )

    # Heatmap Visualization
    st.markdown("---")
    st.markdown("### 🗺️ Sector Performance Heatmap")

    # Prepare data for heatmap
    sector_names = []
    performance_1d = []
    performance_5d = []
    performance_1m = []

    for name, data in sorted_sectors:
        sector_names.append(name)
        performance_1d.append(data['change_1d'])
        performance_5d.append(data['change_5d'])
        performance_1m.append(data['change_1m'])

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[performance_1d, performance_5d, performance_1m],
        x=sector_names,
        y=['1 Day', '5 Days', '1 Month'],
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{val:.2f}%" for val in performance_1d],
              [f"{val:.2f}%" for val in performance_5d],
              [f"{val:.2f}%" for val in performance_1m]],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='<b>%{x}</b><br>%{y}: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        height=300,
        xaxis_tickangle=-45,
        margin=dict(l=20, r=20, t=20, b=100)
    )

    plotly_full_width(fig)


# ========================================
# SECTION 3: ECONOMIC INDICATORS
# ========================================

@st.cache_data(ttl=15, show_spinner="Fetching economic indicators...")  # Conservative: 15s TTL
def fetch_fred_data():
    """
    Fetch key economic indicators from FRED API in parallel

    Returns dict with:
    - Treasury yields (10Y, 2Y)
    - Fed Funds Rate
    - CPI (inflation)
    - Unemployment Rate
    """
    fred_api_key = st.secrets.get("FRED_API_KEY")

    if not fred_api_key:
        return None

    # FRED series IDs
    series = {
        'DGS10': '10Y Treasury Yield',  # 10-Year Treasury
        'DGS2': '2Y Treasury Yield',    # 2-Year Treasury
        'FEDFUNDS': 'Fed Funds Rate',   # Federal Funds Rate
        'CPIAUCSL': 'CPI',              # Consumer Price Index
        'UNRATE': 'Unemployment Rate'   # Unemployment Rate
    }

    def fetch_single_fred_series(series_id, name):
        """Fetch a single FRED series"""
        try:
            # IMPORTANT: Use sort_order=desc to get MOST RECENT data first
            # Without this, the API returns data from 1962-1976 (oldest first), causing incorrect yield curve signals
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={fred_api_key}&file_type=json&limit=90&sort_order=desc"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return name, None

            data = response.json()
            observations = data.get('observations', [])

            if not observations:
                return name, None

            # Convert to DataFrame
            df = pd.DataFrame(observations)
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])

            if df.empty:
                return name, None

            df = df.sort_values('date')

            # Calculate change metrics
            current_value = df['value'].iloc[-1]
            prev_value = df['value'].iloc[-2] if len(df) > 1 else current_value
            month_ago_value = df['value'].iloc[-30] if len(df) >= 30 else prev_value

            change_1d = current_value - prev_value
            change_1m = current_value - month_ago_value

            return name, {
                'series_id': series_id,
                'current': current_value,
                'change_1d': change_1d,
                'change_1m': change_1m,
                'df': df,
                'last_updated': df['date'].iloc[-1]
            }

        except Exception as e:
            from error_logger import log_error
            log_error(e, f"fetch_fred_data.fetch_single_fred_series", {"series_id": series_id, "name": name})
            return name, None

    # Parallel fetching
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_single_fred_series, series_id, name): name
                  for series_id, name in series.items()}

        for future in as_completed(futures):
            name, data = future.result()
            if data:
                results[name] = data

    return results


def calculate_yield_curve_signal(fred_data):
    """
    Calculate yield curve signal (10Y-2Y spread)

    Inverted yield curve (negative spread) is a leading recession indicator
    """
    if not fred_data:
        return None

    treasury_10y = fred_data.get('10Y Treasury Yield')
    treasury_2y = fred_data.get('2Y Treasury Yield')

    if not treasury_10y or not treasury_2y:
        return None

    spread = treasury_10y['current'] - treasury_2y['current']

    if spread < -0.2:
        signal = "Inverted"
        emoji = "⚠️"
        color = "#EF553B"
        interpretation = "Recession warning: Inverted yield curve (strong historical predictor)"
        risk_level = "High"
    elif spread < 0:
        signal = "Near Inversion"
        emoji = "⚠️"
        color = "#FFA15A"
        interpretation = "Caution: Yield curve approaching inversion"
        risk_level = "Moderate"
    elif spread < 0.5:
        signal = "Flat"
        emoji = "➡️"
        color = "#FECB52"
        interpretation = "Flat yield curve: Economic slowdown possible"
        risk_level = "Moderate"
    else:
        signal = "Normal"
        emoji = "✅"
        color = "#00CC96"
        interpretation = "Healthy yield curve: Normal economic conditions"
        risk_level = "Low"

    return {
        'spread': spread,
        'signal': signal,
        'emoji': emoji,
        'color': color,
        'interpretation': interpretation,
        'risk_level': risk_level,
        'treasury_10y': treasury_10y['current'],
        'treasury_2y': treasury_2y['current']
    }


def calculate_inflation_signal(fred_data):
    """
    Analyze Fed Funds Rate vs Inflation relationship

    When Fed Funds Rate < Inflation → accommodative policy (bullish)
    When Fed Funds Rate > Inflation → restrictive policy (bearish)
    """
    if not fred_data:
        return None

    fed_funds = fred_data.get('Fed Funds Rate')
    cpi = fred_data.get('CPI')

    if not fed_funds or not cpi:
        return None

    # Calculate YoY inflation rate from CPI
    cpi_df = cpi['df']
    if len(cpi_df) < 12:
        return None

    current_cpi = cpi_df['value'].iloc[-1]
    year_ago_cpi = cpi_df['value'].iloc[-12]
    inflation_rate = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100

    fed_rate = fed_funds['current']

    difference = fed_rate - inflation_rate

    if difference < -2:
        signal = "Highly Accommodative"
        emoji = "🚀"
        color = "#00CC96"
        interpretation = "Fed far behind inflation - very stimulative policy"
        market_impact = "Bullish (easy money)"
    elif difference < 0:
        signal = "Accommodative"
        emoji = "📈"
        color = "#00CC96"
        interpretation = "Fed Funds below inflation - supportive policy"
        market_impact = "Moderately Bullish"
    elif difference < 2:
        signal = "Neutral"
        emoji = "➡️"
        color = "#FECB52"
        interpretation = "Fed Funds near inflation - balanced policy"
        market_impact = "Neutral"
    else:
        signal = "Restrictive"
        emoji = "🔴"
        color = "#EF553B"
        interpretation = "Fed Funds above inflation - tight policy"
        market_impact = "Bearish (expensive money)"

    return {
        'fed_rate': fed_rate,
        'inflation_rate': inflation_rate,
        'difference': difference,
        'signal': signal,
        'emoji': emoji,
        'color': color,
        'interpretation': interpretation,
        'market_impact': market_impact
    }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_economic_calendar():
    """
    Fetch upcoming economic releases from FRED API

    Performance: ~1-2 seconds
    Cache: 1 hour (calendar doesn't change frequently)
    """
    fred_api_key = st.secrets.get("FRED_API_KEY")

    if not fred_api_key:
        return None

    # Key economic releases to track with their FRED release IDs
    important_releases = {
        'Employment Situation': 10,  # Jobs report
        'Consumer Price Index': 10,  # CPI
        'Federal Open Market Committee': 62,  # FOMC
        'Gross Domestic Product': 53,  # GDP
        'ISM Manufacturing': 11,  # Manufacturing PMI
        'Retail Trade': 39,  # Retail sales
        'Producer Price Index': 46,  # PPI
    }

    from datetime import datetime, timedelta

    # Get releases for the next 30 days
    today = datetime.now()
    end_date = today + timedelta(days=30)

    all_events = []

    for release_name, release_id in important_releases.items():
        try:
            url = "https://api.stlouisfed.org/fred/release/dates"
            params = {
                'release_id': release_id,
                'api_key': fred_api_key,
                'file_type': 'json',
                'realtime_start': today.strftime('%Y-%m-%d'),
                'realtime_end': end_date.strftime('%Y-%m-%d'),
                'include_release_dates_with_no_data': 'true'
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if 'release_dates' in data:
                    for release in data['release_dates']:
                        release_date = datetime.strptime(release['date'], '%Y-%m-%d')

                        # Only include future releases
                        if release_date >= today:
                            all_events.append({
                                'name': release_name,
                                'date': release_date,
                                'date_str': release['date']
                            })

        except Exception as e:
            continue  # Skip this release if error

    # Sort by date
    all_events.sort(key=lambda x: x['date'])

    return all_events[:10]  # Return next 10 events


def render_economic_indicators():
    """Section 3: FRED economic data and predictive signals"""
    st.markdown("## 📈 Economic Indicators & Predictive Signals")
    st.markdown("Federal Reserve data to gauge economic health and predict market direction")

    # Session snapshot + refresh
    c1, c2 = st.columns([4, 1])
    with c1:
        st.caption("Economic indicators cached conservatively (TTL 15s). Use Refresh to force update.")
        st.warning("⚠️ Refresh will clear the global page cache — network/API calls will run immediately and may increase rate-limit usage.")
    with c2:
        if st.button("🔄 Refresh FRED Data"):
            if 'fred_snapshot' in st.session_state:
                del st.session_state['fred_snapshot']
            st.cache_data.clear()

    with st.spinner("Loading economic data..."):
        with PerformanceMonitor("economic_indicators_load"):
            fred_data, fred_ts = get_fred_snapshot(ttl_seconds=15)

    if not fred_data:
        st.warning("⚠️ FRED API key not configured. Economic indicators unavailable.")
        st.info("Add your FRED_API_KEY to .streamlit/secrets.toml to enable this feature")
        return

    # Show last-updated timestamp for FRED snapshot
    if fred_ts:
        st.caption(f"Last updated: {pd.to_datetime(fred_ts, unit='s').strftime('%Y-%m-%d %H:%M:%S')}")

    # ============================
    # SUMMARY BOX
    # ============================

    yield_signal = calculate_yield_curve_signal(fred_data)
    inflation_signal = calculate_inflation_signal(fred_data)

    st.markdown("---")
    st.markdown("### 🎯 Economic Summary")

    summary_parts = []

    if yield_signal:
        summary_parts.append(f"**Yield Curve:** {yield_signal['signal']} ({yield_signal['risk_level']} risk)")

    if inflation_signal:
        summary_parts.append(f"**Fed Policy:** {inflation_signal['signal']} → {inflation_signal['market_impact']}")

    if 'Unemployment Rate' in fred_data:
        unemployment_rate = fred_data['Unemployment Rate']['current']
        if unemployment_rate < 4.5:
            labor_status = "Strong labor market"
        elif unemployment_rate < 5.5:
            labor_status = "Healthy labor market"
        else:
            labor_status = "Weakening labor market"
        summary_parts.append(f"**Labor Market:** {labor_status} ({unemployment_rate:.1f}%)")

    if summary_parts:
        summary_text = " | ".join(summary_parts)
        st.info(summary_text)

    # ============================
    # YIELD CURVE ANALYSIS
    # ============================

    if yield_signal:
        st.markdown("---")
        st.markdown("### 📊 Treasury Yield Curve Signal")

        yield_cols = st.columns([1, 1, 2])

        with yield_cols[0]:
            st.metric(
                "Yield Curve Spread",
                f"{yield_signal['spread']:.2f}%",
                delta=f"10Y: {yield_signal['treasury_10y']:.2f}%"
            )

        with yield_cols[1]:
            st.metric(
                "Signal",
                f"{yield_signal['emoji']} {yield_signal['signal']}",
                delta=f"Risk: {yield_signal['risk_level']}"
            )

        with yield_cols[2]:
            st.markdown(f"**{yield_signal['interpretation']}**")
            st.caption(f"10Y Treasury: {yield_signal['treasury_10y']:.2f}% | 2Y Treasury: {yield_signal['treasury_2y']:.2f}%")

        # Yield Curve Chart
        if '10Y Treasury Yield' in fred_data and '2Y Treasury Yield' in fred_data:
            treasury_10y_df = fred_data['10Y Treasury Yield']['df'].tail(90).copy()
            treasury_2y_df = fred_data['2Y Treasury Yield']['df'].tail(90).copy()

            # Debug: Check if dataframes are empty
            if treasury_10y_df.empty or treasury_2y_df.empty:
                st.warning("⚠️ Treasury yield data is empty. Please refresh or check FRED API connection.")
            else:
                # Calculate spread over time
                merged_df = pd.merge(
                    treasury_10y_df[['date', 'value']],
                    treasury_2y_df[['date', 'value']],
                    on='date',
                    suffixes=('_10y', '_2y'),
                    how='inner'  # Only keep matching dates
                )

                if merged_df.empty:
                    st.warning("⚠️ No matching dates found between 10Y and 2Y Treasury data. The FRED API may have returned incomplete data.")
                else:
                    merged_df['spread'] = merged_df['value_10y'] - merged_df['value_2y']

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=merged_df['date'],
                        y=merged_df['value_10y'],
                        name='10Y Treasury',
                        line=dict(color='#636EFA', width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=merged_df['date'],
                        y=merged_df['value_2y'],
                        name='2Y Treasury',
                        line=dict(color='#EF553B', width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=merged_df['date'],
                        y=merged_df['spread'],
                        name='Spread (10Y-2Y)',
                        line=dict(color='#00CC96', width=3, dash='dash'),
                        yaxis='y2'
                    ))

                    # Add zero line for spread
                    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, yref='y2')

                    fig.update_layout(
                        title="Treasury Yield Curve (90 Days)",
                        xaxis_title="Date",
                        yaxis_title="Yield (%)",
                        yaxis2=dict(
                            title="Spread (%)",
                            overlaying='y',
                            side='right'
                        ),
                        height=400,
                        hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )

                    plotly_full_width(fig)
        else:
            st.warning("⚠️ Treasury yield data not available. Please check your FRED API key in secrets.toml")

    # ============================
    # FED FUNDS VS INFLATION
    # ============================

    if inflation_signal:
        st.markdown("---")
        st.markdown("### 💰 Fed Policy vs Inflation")

        inflation_cols = st.columns([1, 1, 2])

        with inflation_cols[0]:
            st.metric(
                "Fed Funds Rate",
                f"{inflation_signal['fed_rate']:.2f}%",
                delta=f"Inflation: {inflation_signal['inflation_rate']:.2f}%"
            )
            # Get the data date from fred_data
            if 'Fed Funds Rate' in fred_data:
                fed_date = fred_data['Fed Funds Rate']['last_updated']
                st.caption(f"📊 Effective rate (monthly) as of {fed_date.strftime('%b %Y')}")
                st.caption("💡 Note: Google shows Fed's target range (e.g., 4.50-4.75%), while this shows the effective rate")

        with inflation_cols[1]:
            st.metric(
                "Policy Stance",
                f"{inflation_signal['emoji']} {inflation_signal['signal']}",
                delta=f"Diff: {inflation_signal['difference']:.2f}%"
            )

        with inflation_cols[2]:
            st.markdown(f"**{inflation_signal['interpretation']}**")
            st.caption(f"Market Impact: {inflation_signal['market_impact']}")

    # ============================
    # UNEMPLOYMENT TRENDS
    # ============================

    if 'Unemployment Rate' in fred_data:
        st.markdown("---")
        st.markdown("### 👷 Unemployment Trends")

        unemployment = fred_data['Unemployment Rate']
        unemployment_df = unemployment['df'].tail(24)  # Last 24 months

        unemployment_cols = st.columns([1, 3])

        with unemployment_cols[0]:
            st.metric(
                "Unemployment Rate",
                f"{unemployment['current']:.1f}%",
                delta=f"{unemployment['change_1m']:.1f}% (1M change)"
            )

            # Interpretation
            if unemployment['current'] < 4.0:
                st.success("✅ **Strong Labor Market**")
            elif unemployment['current'] < 5.0:
                st.info("➡️ **Healthy Labor Market**")
            elif unemployment['current'] < 6.0:
                st.warning("⚠️ **Weakening Labor Market**")
            else:
                st.error("🔴 **Weak Labor Market**")

        with unemployment_cols[1]:
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=unemployment_df['date'],
                y=unemployment_df['value'],
                mode='lines+markers',
                name='Unemployment Rate',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=6)
            ))

            fig.update_layout(
                title="Unemployment Rate (24 Months)",
                xaxis_title="Date",
                yaxis_title="Unemployment Rate (%)",
                height=300,
                hovermode='x unified'
            )

            plotly_full_width(fig)

    # ============================
    # ECONOMIC CALENDAR
    # ============================

    st.markdown("---")
    st.markdown("### 📅 Upcoming Economic Releases")
    st.markdown("Key economic reports that could impact market direction in the next 30 days")

    economic_calendar = fetch_economic_calendar()

    if economic_calendar:
        from datetime import datetime

        # Create a clean table view
        cal_data = []
        today = datetime.now()

        for event in economic_calendar:
            days_until = (event['date'] - today).days

            if days_until == 0:
                timing = "Today"
                badge_color = "#EF553B"
            elif days_until == 1:
                timing = "Tomorrow"
                badge_color = "#FFA15A"
            elif days_until <= 7:
                timing = f"In {days_until} days"
                badge_color = "#FECB52"
            else:
                timing = f"In {days_until} days"
                badge_color = "#636EFA"

            cal_data.append({
                'Release': event['name'],
                'Date': event['date'].strftime('%b %d, %Y'),
                'Timing': timing,
                'Badge_Color': badge_color
            })

        # Display as cards for better visual impact
        if cal_data:
            # Show first 5 in main view
            for i, item in enumerate(cal_data[:5]):
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.markdown(f"**{item['Release']}**")

                with col2:
                    st.markdown(f"{item['Date']}")

                with col3:
                    st.markdown(f"<span style='background-color: {item['Badge_Color']}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em;'>{item['Timing']}</span>", unsafe_allow_html=True)

                if i < len(cal_data[:5]) - 1:
                    st.markdown("<hr style='margin: 8px 0; opacity: 0.3;'>", unsafe_allow_html=True)

            # Show rest in expander
            if len(cal_data) > 5:
                with st.expander(f"Show {len(cal_data) - 5} more releases"):
                    for i, item in enumerate(cal_data[5:]):
                        col1, col2, col3 = st.columns([3, 2, 2])

                        with col1:
                            st.markdown(f"**{item['Release']}**")

                        with col2:
                            st.markdown(f"{item['Date']}")

                        with col3:
                            st.markdown(f"<span style='background-color: {item['Badge_Color']}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em;'>{item['Timing']}</span>", unsafe_allow_html=True)

                        if i < len(cal_data[5:]) - 1:
                            st.markdown("<hr style='margin: 8px 0; opacity: 0.3;'>", unsafe_allow_html=True)

        st.caption("📊 Data Source: FRED Economic Release Calendar | Updated hourly")
    else:
        st.info("Economic calendar unavailable. FRED API key may not be configured.")

    st.caption("📊 Data Source: Federal Reserve Economic Data (FRED) | Updated hourly")


# ========================================
# SECTION 4: AI MARKET INTELLIGENCE
# ========================================

def generate_ai_market_summary(indices_data, market_health, sector_data, rotation_signal, fred_data, yield_signal, inflation_signal):
    """
    Generate AI-powered market intelligence summary

    Args:
        indices_data: Market indices data
        market_health: Market health score and interpretation
        sector_data: Sector performance data
        rotation_signal: Sector rotation signal
        fred_data: Economic indicators from FRED
        yield_signal: Yield curve analysis
        inflation_signal: Fed policy vs inflation analysis

    Returns:
        str: AI-generated market summary (3-4 sentences)
    """
    try:
        from ai_model_config import create_model_client, get_selected_model, get_model_info, AIProvider

        # Use GLOBAL AI model selection (same across all pages)
        model_id = get_selected_model("global_ai_model")
        model_info = get_model_info(model_id)

        if not model_info:
            return None

        # Build context from all market data
        context_parts = []

        # Market indices
        if indices_data:
            sp500 = indices_data.get('S&P 500', {})
            nasdaq = indices_data.get('NASDAQ', {})
            vix = indices_data.get('VIX', {})

            context_parts.append(f"Market Indices: S&P 500 {sp500.get('pct_change', 0):.2f}%, NASDAQ {nasdaq.get('pct_change', 0):.2f}%, VIX {vix.get('price', 0):.2f}")

        # Market health (defensive: keys may be missing)
        if market_health:
            mh_score = market_health.get('score', 'N/A') if isinstance(market_health, dict) else 'N/A'
            mh_cat = market_health.get('category', '') if isinstance(market_health, dict) else ''
            context_parts.append(f"Market Health: {mh_score}/100 ({mh_cat})")

        # Sector rotation
        if rotation_signal:
            signal = rotation_signal.get('signal', 'N/A') if isinstance(rotation_signal, dict) else 'N/A'
            interp = rotation_signal.get('interpretation', '') if isinstance(rotation_signal, dict) else ''
            context_parts.append(f"Sector Rotation: {signal} - {interp}")

        # Top/Bottom sectors
        if sector_data:
            sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]['change_5d'], reverse=True)
            top_sector = sorted_sectors[0]
            bottom_sector = sorted_sectors[-1]
            context_parts.append(f"Best Sector: {top_sector[0]} +{top_sector[1]['change_5d']:.2f}% | Worst: {bottom_sector[0]} {bottom_sector[1]['change_5d']:.2f}%")

        # Yield curve
        if yield_signal:
            y_sig = yield_signal.get('signal', 'N/A') if isinstance(yield_signal, dict) else 'N/A'
            y_spread = yield_signal.get('spread', 0.0) if isinstance(yield_signal, dict) else 0.0
            y_risk = yield_signal.get('risk_level', '') if isinstance(yield_signal, dict) else ''
            context_parts.append(f"Yield Curve: {y_sig} (10Y-2Y spread: {y_spread:.2f}%) - {y_risk} risk")

        # Fed policy
        if inflation_signal:
            i_sig = inflation_signal.get('signal', 'N/A') if isinstance(inflation_signal, dict) else 'N/A'
            fed_rate = inflation_signal.get('fed_rate', 0.0) if isinstance(inflation_signal, dict) else 0.0
            infl_rate = inflation_signal.get('inflation_rate', 0.0) if isinstance(inflation_signal, dict) else 0.0
            market_imp = inflation_signal.get('market_impact', '') if isinstance(inflation_signal, dict) else ''
            context_parts.append(f"Fed Policy: {i_sig} (Fed {fed_rate:.2f}% vs Inflation {infl_rate:.2f}%) - {market_imp}")

        # Unemployment
        if fred_data and 'Unemployment Rate' in fred_data:
            try:
                unemp = fred_data['Unemployment Rate'].get('current')
                if unemp is not None:
                    context_parts.append(f"Labor Market: {unemp:.1f}% unemployment")
            except Exception:
                # Defensive: fred_data may be malformed
                pass

        context_text = "\n".join([f"- {part}" for part in context_parts])

        prompt = f"""Analyze today's market conditions and provide a concise 3-4 sentence professional market summary.

MARKET DATA:
{context_text}

Provide an executive summary that:
1. Assesses overall market sentiment and direction
2. Identifies 1-2 key drivers moving markets today
3. Notes any major risks or opportunities
4. Gives a brief forward-looking assessment

Be objective, professional, and concise (under 80 words)."""

        # Call AI model based on provider (using global key)
        client = create_model_client(model_id, "global_ai_model")

        if model_info.provider == AIProvider.GEMINI:
            response = client.generate_content(prompt)
            return response.text.strip()

        elif model_info.provider == AIProvider.OPENAI or model_info.provider == AIProvider.GROK:
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()

        elif model_info.provider == AIProvider.CLAUDE:
            response = client.messages.create(
                model=model_id,
                max_tokens=250,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        else:
            return None

    except Exception as e:
        return None


def _build_market_context_prompt(indices_data, market_health, sector_data, rotation_signal, fred_data, yield_signal, inflation_signal):
    """Build a compact context string describing market state for AI prompts."""
    parts = []
    if indices_data:
        sp = indices_data.get('S&P 500', {})
        na = indices_data.get('NASDAQ', {})
        v = indices_data.get('VIX', {})
        parts.append(f"Market Indices: S&P500 {sp.get('pct_change', 0):.2f}%, NASDAQ {na.get('pct_change', 0):.2f}%, VIX {v.get('price',0):.2f}")

    if market_health:
        parts.append(f"Market Health: {market_health.get('score', 'N/A')}/100 ({market_health.get('category', '')})")

    if rotation_signal:
        parts.append(f"Sector Rotation: {rotation_signal.get('signal','N/A')} - {rotation_signal.get('interpretation','')}")

    if sector_data:
        try:
            sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1].get('change_5d', 0), reverse=True)
            top = sorted_sectors[0]
            bot = sorted_sectors[-1]
            parts.append(f"Top: {top[0]} +{top[1].get('change_5d',0):.2f}% | Bottom: {bot[0]} {bot[1].get('change_5d',0):.2f}%")
        except Exception:
            pass

    if yield_signal:
        parts.append(f"Yield Curve: {yield_signal.get('signal','N/A')} spread {yield_signal.get('spread',0):.2f}%")

    if inflation_signal:
        parts.append(f"Fed Policy: {inflation_signal.get('signal','N/A')} (Fed {inflation_signal.get('fed_rate',0):.2f}% vs Inflation {inflation_signal.get('inflation_rate',0):.2f}%)")

    if fred_data and 'Unemployment Rate' in fred_data:
        try:
            parts.append(f"Unemployment: {fred_data['Unemployment Rate'].get('current', 'N/A'):.1f}%")
        except Exception:
            pass

    return "\n".join([f"- {p}" for p in parts])


def generate_ai_market_summaries_all(indices_data, market_health, sector_data, rotation_signal, fred_data, yield_signal, inflation_signal, prompt_override: str | None = None):
    """Generate market summaries from all configured AI providers.

    Returns a dict keyed by provider name -> {'model': model_id, 'response': text}
    """
    try:
        from ai_model_config import get_available_providers, get_models_by_provider, call_ai_model

        providers = get_available_providers()
        if not providers:
            return {}

        base_context = _build_market_context_prompt(indices_data, market_health, sector_data, rotation_signal, fred_data, yield_signal, inflation_signal)

        results = {}
        for provider in providers:
            try:
                models = get_models_by_provider(provider)
                if not models:
                    results[provider.value] = {'model': None, 'response': 'no models configured for provider'}
                    continue

                model_info = models[0]

                if prompt_override:
                    prompt = prompt_override + "\n\nMARKET CONTEXT:\n" + base_context
                else:
                    prompt = f"Analyze today's market conditions and provide a concise 3-4 sentence summary.\n\nMARKET CONTEXT:\n{base_context}"

                resp = call_ai_model(model_info, prompt, max_tokens=220, temperature=0.3, session_key="global_ai_model")
                results[provider.value] = {'model': model_info.model_id, 'response': (resp.strip() if isinstance(resp, str) else str(resp))}
            except Exception as e:
                results[provider.value] = {'model': None, 'response': f'failed: {str(e)[:200]}'}

        return results
    except Exception:
        return {}


def render_ai_market_intelligence(indices_data, market_health, sector_data, rotation_signal, fred_data, yield_signal, inflation_signal):
    """Section 4: AI-powered market summary and outlook"""
    st.markdown("## 🤖 AI Market Intelligence")
    st.markdown("AI-powered synthesis of all market signals and economic data")

    # Check if AI features are enabled
    enable_ai = st.session_state.get('enable_ai_features', False)

    if not enable_ai:
        st.info("💡 Enable AI features in the sidebar to unlock AI-powered market analysis")
        return

    # Allow user to edit the prompt (optional)
    default_prompt_example = "Analyze today's market conditions and provide a concise 3-4 sentence professional market summary. Focus on key drivers and near-term risks."
    with st.expander("✍️ Edit AI Prompt (optional)", expanded=False):
        _ = st.text_area("AI prompt", value=st.session_state.get('ai_market_prompt', default_prompt_example), key='ai_market_prompt', height=160)

    # Generate AI summary (with caching via session state)
    cache_key = "ai_market_summary_cache"
    cache_time_key = "ai_market_summary_time"

    # Check cache (5 minute TTL)
    import time
    current_time = time.time()
    cached_summary = st.session_state.get(cache_key)
    cached_time = st.session_state.get(cache_time_key, 0)

    if cached_summary and (current_time - cached_time) < 300:  # 5 minutes
        ai_summary = cached_summary
    else:
        with st.spinner("🤖 Generating AI market intelligence..."):
            with PerformanceMonitor("ai_market_summary_generation"):
                # Prefer multi-provider generation, allow prompt override
                prompt_override = st.session_state.get('ai_market_prompt')
                ai_summary = generate_ai_market_summaries_all(
                    indices_data, market_health, sector_data, rotation_signal,
                    fred_data, yield_signal, inflation_signal, prompt_override=prompt_override
                )

        if ai_summary:
            st.session_state[cache_key] = ai_summary
            st.session_state[cache_time_key] = current_time

    # Display AI summary
    if ai_summary:
        st.markdown("---")
        st.markdown("### 📝 Today's Market Intelligence")

        # Multi-provider: if we have a dict with provider -> {'model', 'response'} entries, show each separately
        if isinstance(ai_summary, dict):
            for provider_label, payload in ai_summary.items():
                model_id = payload.get('model') if isinstance(payload, dict) else None
                response_text = payload.get('response') if isinstance(payload, dict) else str(payload)

                with st.expander(f"{provider_label} {(' — ' + model_id) if model_id else ''}", expanded=False):
                    if response_text:
                        st.write(response_text)
                    else:
                        st.warning("No response from provider")

        else:
            # Single-string fallback for older single-provider behavior
            st.info(ai_summary)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption("🤖 Generated by AI - Synthesizes all market signals above")
        with col2:
            if st.button("🔄 Regenerate", key="regenerate_ai_summary"):
                st.session_state.pop(cache_key, None)
                st.session_state.pop(cache_time_key, None)
                st.rerun()

    else:
        st.warning("⚠️ Unable to generate AI summary. Please check your AI model configuration in the sidebar.")
        st.caption("Make sure you've selected an AI model and configured the required API keys in .streamlit/secrets.toml")


# ========================================
# SECTION 4: CORRELATING FACTORS
# ========================================

def render_correlating_factors_market():
    """
    Render the Correlating Factors tab for market-level analysis.
    Shows which factors correlate most strongly with S&P 500 performance.
    """
    import correlation_factors as cf

    st.markdown("## 🔗 Correlating Factors - Market Analysis")
    st.markdown("Identify which economic factors drive broad market movements with statistical proof")

    # ============================
    # CONTROLS
    # ============================

    time_period = st.selectbox(
        "📅 Analysis Time Period",
        options=[
            ("3 Months", 90),
            ("6 Months", 180),
            ("1 Year (Recommended)", 365),
            ("2 Years", 730),
            ("3 Years", 1095)
        ],
        index=2,  # Default to 1 year
        format_func=lambda x: x[0],
        key="correlating_factors_time_period",
        help="**Time Period Help**\n\n"
             "- **3 Months**: Short-term correlations, more reactive to recent changes\n"
             "- **6 Months**: Medium-term trends\n"
             "- **1 Year**: ⭐ Optimal balance - captures seasonal patterns with 252+ trading days\n"
             "- **2 Years**: Long-term stable relationships\n"
             "- **3 Years**: Very stable, less reactive to recent market shifts\n\n"
             "**Statistical Note**: Longer periods provide more data points (higher confidence), "
             "but may miss recent regime changes. Shorter periods are more responsive but noisier."
    )
    days = time_period[1]

    # Info about cache
    st.caption("💡 Tip: Data is cached for 4 hours. Change the time period above to reload fresh data.")

    st.markdown("---")

    # ============================
    # FETCH MARKET DATA (S&P 500)
    # ============================

    with st.spinner("Fetching market data..."):
        market_ticker = "^GSPC"  # S&P 500
        market_returns = cf.fetch_factor_data(market_ticker, days=days)

        if market_returns.empty:
            st.error("Unable to fetch S&P 500 data. Please try again.")
            return

    # ============================
    # DEFAULT FACTORS
    # ============================

    default_factors = cf.get_default_market_factors()

    st.markdown("### 📊 Default Market Factors")
    st.caption(f"Analyzing {len(default_factors)} key factors that historically drive market performance")

    # ============================
    # FETCH ALL FACTORS IN PARALLEL
    # ============================

    with st.spinner("Analyzing correlations for all factors..."):
        factor_returns = cf.fetch_all_factors_parallel(default_factors, days=days)

        if not factor_returns:
            st.error("Unable to fetch factor data. Please try again.")
            return

    # ============================
    # CALCULATE KEY FACTOR SCORES
    # ============================

    # Defensive: detect duplicate series returned from fetch to avoid mis-attribution
    duplicates = cf.detect_duplicate_factor_series(factor_returns)
    if duplicates:
        dup_lines = []
        for leader, copies in duplicates.items():
            dup_lines.append(f"{leader} == {', '.join(copies)}")
        st.warning("Detected identical factor series for multiple factors — this usually indicates a data source or mapping issue. Examples: " + "; ".join(dup_lines))

    factor_scores = []

    for factor_name, factor_data in factor_returns.items():
        # make a defensive copy so in-memory shared objects don't cause cross-factor contamination
        try:
            factor_data = factor_data.copy()
        except Exception:
            pass
        score_result = cf.calculate_key_factor_score(
            market_returns,
            factor_data,
            factor_name
        )

        factor_scores.append(score_result)

    # Sort by key score (highest first)
    factor_scores.sort(key=lambda x: x['key_score'], reverse=True)

    # ============================
    # DISPLAY: KEY FACTOR SUMMARY
    # ============================

    st.markdown("### 🏆 Key Factor Rankings")
    st.markdown(f"Ranked by **Key Factor Score** (0-100) combining correlation strength, predictive power, and stability over {time_period[0].lower()}")

    # Top 3 badges
    if len(factor_scores) >= 3:
        badge_cols = st.columns(3)
        for i, score in enumerate(factor_scores[:3]):
            with badge_cols[i]:
                st.metric(
                    f"{score['badge']} #{i+1}: {score['explanation'].split(':')[0]}",
                    f"{score['key_score']:.2f}/100",
                    delta=score['rank']
                )

    st.markdown("---")

    # ============================
    # DISPLAY: DETAILED FACTOR ANALYSIS
    # ============================

    for i, score in enumerate(factor_scores):
        factor_name = score['explanation'].split(':')[0]

        with st.expander(f"**{score['badge']} {factor_name}** - Key Score: {score['key_score']:.2f}/100", expanded=(i == 0)):
            # Create columns for metrics
            metric_cols = st.columns(4)

            corr_details = score['details']['correlation']
            pred_details = score['details']['predictive']
            stab_details = score['details']['stability']

            with metric_cols[0]:
                st.metric(
                    "Correlation",
                    f"{corr_details['correlation']:.3f}",
                    delta=f"{corr_details['stars']} {corr_details['strength']}"
                )
                st.caption(f"Direction: {corr_details['direction']}")
                st.caption(f"R²: {corr_details['r_squared']:.3f}")
                if corr_details['is_significant']:
                    st.caption("✅ Statistically significant (p < 0.05)")
                else:
                    st.caption(f"⚠️ Not significant (p = {corr_details['p_value']:.4f})")

            with metric_cols[1]:
                st.metric(
                    "Predictive Power",
                    pred_details['direction'],
                    delta=f"{pred_details['best_lag']} days" if pred_details['best_lag'] > 0 else "Coincident"
                )
                if pred_details['is_predictive']:
                    st.caption(f"🎯 Predicts {pred_details['best_lag']} days ahead")
                    st.caption(f"Correlation: {pred_details['best_correlation']:.3f}")
                else:
                    st.caption("📊 Limited predictive power")

            with metric_cols[2]:
                st.metric(
                    "Stability",
                    stab_details['stability'],
                    delta=f"Volatility: {stab_details['std_correlation']:.3f}"
                )
                st.caption(f"Avg correlation: {stab_details['mean_correlation']:.3f}")

            with metric_cols[3]:
                component_scores = score['details']['component_scores']
                st.metric(
                    "Score Breakdown",
                    f"{score['key_score']:.2f}/100"
                )
                st.caption(f"Strength: {component_scores['strength_score']:.1f}/40")
                st.caption(f"Predictive: {component_scores['predictive_score']:.1f}/30")
                st.caption(f"Stability: {component_scores['stability_score']:.1f}/30")

            # Explanation
            st.markdown("---")
            st.markdown(f"**Summary**: {score['explanation']}")

            # Rolling correlation chart (if stability data available)
            if not stab_details['rolling_series'].empty:
                st.markdown("**Rolling Correlation Chart** (60-day window)")

                import plotly.graph_objects as go

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=stab_details['rolling_series'].index,
                    y=stab_details['rolling_series'].values,
                    mode='lines',
                    name='Rolling Correlation',
                    line=dict(color='#636EFA', width=2)
                ))

                # Add mean line
                fig.add_hline(
                    y=stab_details['mean_correlation'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Mean: {stab_details['mean_correlation']:.3f}"
                )

                fig.update_layout(
                    title=f"{factor_name} vs S&P 500 - Rolling 60-Day Correlation",
                    xaxis_title="Date",
                    yaxis_title="Correlation",
                    yaxis_range=[-1, 1],
                    height=300,
                    hovermode='x unified'
                )

                plotly_full_width(fig)

    # ============================
    # HELP SECTION
    # ============================

    st.markdown("---")

    with st.expander("❓ **Understanding Correlation Analysis - Complete Guide**"):
        st.markdown("""
        ## What Are Correlating Factors?

        Correlating factors are economic variables, indices, or market indicators that move in sync with (or opposite to) the S&P 500.
        Understanding these relationships helps you:
        - Predict market direction based on leading indicators
        - Diversify effectively (avoid factors that move together)
        - Understand what's driving market performance

        ---

        ## Key Metrics Explained

        ### 1. Correlation Coefficient (-1 to +1)
        - **+0.7 to +1.0**: Very strong positive correlation (move together)
        - **+0.5 to +0.7**: Strong positive correlation
        - **+0.3 to +0.5**: Moderate positive correlation
        - **-0.3 to +0.3**: Weak/no correlation
        - **-0.5 to -0.3**: Moderate negative correlation (move opposite)
        - **-0.7 to -0.5**: Strong negative correlation
        - **-1.0 to -0.7**: Very strong negative correlation

        ### 2. P-Value (Statistical Significance)
        - **p < 0.05**: ✅ Statistically significant (likely real relationship, not random)
        - **p ≥ 0.05**: ⚠️ Not significant (could be random chance)

        ### 3. R² (Variance Explained)
        - Percentage of market movement explained by this factor
        - **Example**: R² = 0.64 means 64% of S&P 500 variance explained by this factor

        ### 4. Predictive Power (Lead/Lag)
        - **Leading (1-10 days)**: Factor moves BEFORE market (useful for prediction)
        - **Coincident (0 days)**: Factor moves WITH market (confirmation, not prediction)
        - **Lagging**: Market moves BEFORE factor (not useful)

        ### 5. Stability (Rolling Correlation)
        - Measures how consistent the correlation is over time
        - **Very Stable**: Correlation doesn't change much (reliable)
        - **Unstable**: Correlation varies wildly (less reliable, regime-dependent)

        ### 6. Key Factor Score (0-100)
        Our proprietary score combining:
        - **40 points**: Correlation strength + statistical significance
        - **30 points**: Predictive power (leading indicators score higher)
        - **30 points**: Stability (consistent correlations score higher)

        **Score Interpretation**:
        - **80-100**: 🏆 Elite key factor (strong, predictive, stable)
        - **60-79**: 🥇 Strong key factor (reliable for analysis)
        - **40-59**: 🥈 Moderate key factor (useful but limitations)
        - **20-39**: 🥉 Weak key factor (minimal predictive value)
        - **0-19**: 📊 Not a key factor (spurious/unreliable)

        ---

        ## Time Sensitivity Analysis

        Compares short-term (3-month) vs long-term (1-year) correlations to detect changes:

        - **📈 Strengthening**: Short-term correlation > Long-term (+0.15 or more)
          - *Meaning*: Relationship is getting stronger recently
          - *Example*: Oil correlation was 0.4 (1Y) but now 0.7 (3M) → Energy crisis impact

        - **➡️ Stable**: Short-term ≈ Long-term (within ±0.15)
          - *Meaning*: Relationship is consistent over time (most reliable)

        - **📉 Weakening**: Short-term correlation < Long-term (-0.15 or more)
          - *Meaning*: Relationship is breaking down recently
          - *Example*: Tech correlation was 0.8 (1Y) but now 0.4 (3M) → Sector rotation

        **When to use**: Enable this when you suspect recent market regime changes (Fed policy shifts, crises, etc.)

        ---

        ## Choosing Your Time Period

        | Period | Use Case | Pros | Cons |
        |--------|----------|------|------|
        | **3 Months** | Recent market regime | Reactive, current | Noisy, less statistically significant |
        | **6 Months** | Medium-term trends | Balanced | May miss long-term patterns |
        | **1 Year** ⭐ | Default/recommended | Full seasonal cycle, ~252 data points | May miss very recent changes |
        | **2 Years** | Long-term stability | Very stable, high confidence | May include outdated regimes |
        | **3 Years** | Historical research | Maximum data, highest confidence | Less relevant to current market |

        **Statistical Note**: You need at least 30 data points for significance. Longer = more confidence, but less responsive to changes.

        ---

        ## How to Use This Analysis

        ### For Market Timing:
        1. Look for **leading indicators** (predictive power > 0 days)
        2. Monitor those factors daily for early signals
        3. Combine multiple leading factors for confidence

        ### For Diversification:
        1. Avoid assets with high positive correlation (>0.7) to S&P 500
        2. Seek negative correlations (-0.5 or lower) as hedges
        3. Check stability to ensure correlations hold during stress

        ### For Understanding Market Drivers:
        1. Sort by Key Factor Score (highest = most important)
        2. Read the summary for each top factor
        3. Monitor top 3 factors to understand "why" market moved

        ---

        ## Example Interpretation

        **Factor**: 10-Year Treasury (^TNX)
        - **Correlation**: -0.65 (strong negative)
        - **Predictive Power**: Leading (2 days ahead)
        - **Stability**: Very stable
        - **Key Score**: 85/100 (Elite)
        - **Time Sensitivity**: Strengthening (3M: -0.75, 1Y: -0.65)

        **What This Means**:
        - When interest rates rise, S&P 500 tends to fall (and vice versa)
        - Treasury yields predict stock market 2 days ahead
        - This relationship is very consistent over time
        - Recently strengthening → Interest rates matter more now than before
        - **Action**: Watch 10-year yields closely for market direction signals
        """)


# ========================================
# DEBUG TAB
# ========================================

def render_debug_tab_market(indices_data, market_health, sector_data, fred_data):
    """Debug tab for Market Overview page"""
    st.markdown("### 🔧 Market Overview Debug Panel")

    st.info("""
    **Purpose**: Diagnose data quality, API connectivity, and performance issues for market-level data.
    """)

    # Section 1: Session State Variables
    with st.expander("📦 Session State Variables", expanded=False):
        st.markdown("**Current session state keys and values:**")
        if st.session_state:
            state_dict = {k: str(v)[:200] for k, v in st.session_state.items()}
            st.json(state_dict)
        else:
            st.write("No session state variables found")

    # Section 2: Market Indices Data Quality
    with st.expander("🎯 Market Indices Data Quality", expanded=True):
        # optional manual refresh for debugers
        if st.button("🔄 Refresh Market Snapshot (debug)"):
            if 'market_snapshot' in st.session_state:
                del st.session_state['market_snapshot']

        st.markdown("**Checking data completeness for major indices:**")

        index_symbols = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT",
            "VIX": "^VIX"
        }

        checks = {}
        details = {}

        def _extract_df(obj):
            """Return a pandas.DataFrame if present in obj (itself or nested like {'history': df}).

            Accepts:
              - a DataFrame -> returned as-is
              - a dict with keys 'history' or 'df' containing a DataFrame -> return that
              - otherwise -> None
            """
            try:
                import pandas as _pd

                if obj is None:
                    return None

                # Already a DataFrame or Series -> convert Series to DataFrame for uniformity
                if isinstance(obj, _pd.DataFrame):
                    return obj
                if isinstance(obj, _pd.Series):
                    return obj.to_frame()

                # dict-like: check common keys
                if isinstance(obj, dict):
                    for key in ('history', 'df', 'data'):
                        if key in obj and isinstance(obj[key], _pd.DataFrame):
                            return obj[key]

                return None
            except Exception:
                return None

        for name, symbol in index_symbols.items():
            # indices_data uses index names as keys (e.g., 'S&P 500'), not ticker symbols (e.g., '^GSPC')
            if indices_data is not None and name in indices_data:
                data_raw = indices_data[name]
                data = _extract_df(data_raw)
                has_data = data is not None and not data.empty
                has_price = has_data and 'Close' in data.columns
                has_volume = has_data and 'Volume' in data.columns
                has_recent = has_data and len(data) > 0

                checks[name] = has_data and has_price
                details[name] = {
                    'Has Data': '✅' if has_data else '❌',
                    'Has Price': '✅' if has_price else '❌',
                    'Has Volume': '✅' if has_volume else '❌',
                    'Data Points': len(data) if has_data else 0,
                    'Date Range': f"{data.index[0].date()} to {data.index[-1].date()}" if has_recent else 'N/A'
                }
            else:
                checks[name] = False
                details[name] = {
                    'Has Data': '❌',
                    'Has Price': '❌',
                    'Has Volume': '❌',
                    'Data Points': 0,
                    'Date Range': 'N/A'
                }

        # Display results
        for name, detail in details.items():
            st.markdown(f"**{name}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Status", detail['Has Data'])
            col2.metric("Price Data", detail['Has Price'])
            col3.metric("Data Points", detail['Data Points'])
            col4.text(f"Range: {detail['Date Range']}")

        completeness_score = sum(checks.values())
        completeness_pct = (completeness_score / len(checks)) * 100

        st.markdown("---")
        st.metric("Overall Indices Completeness", f"{completeness_pct:.0f}%")

        if completeness_pct < 80:
            st.warning("⚠️ Some indices are missing data. Check yfinance API connectivity.")
        else:
            st.success("✅ All major indices loaded successfully!")

    # Section 3: Economic Indicators (FRED) Status
    with st.expander("📊 FRED Economic Indicators Status", expanded=True):
        if st.button("🔄 Refresh FRED Snapshot (debug)"):
            if 'fred_snapshot' in st.session_state:
                del st.session_state['fred_snapshot']

        st.markdown("**Checking FRED API data quality:**")

        # Use the actual keys returned by fetch_fred_data()
        expected_indicators = [
            "10Y Treasury Yield",
            "2Y Treasury Yield",
            "Fed Funds Rate",
            "CPI",
            "Unemployment Rate"
        ]

        if fred_data and isinstance(fred_data, dict):
            available = []
            missing = []

            for indicator in expected_indicators:
                if indicator in fred_data and fred_data[indicator] is not None:
                    data = fred_data[indicator]
                    # data is a dict with 'df', 'current', etc.
                    if 'df' in data and data['df'] is not None and not data['df'].empty:
                        available.append({
                            'Indicator': indicator,
                            'Data Points': len(data['df']),
                            'Latest Date': str(data['last_updated'].date()) if 'last_updated' in data else 'N/A',
                            'Latest Value': f"{data['current']:.2f}" if 'current' in data else 'N/A'
                        })
                    else:
                        missing.append(indicator)
                else:
                    missing.append(indicator)

            if available:
                st.markdown("**✅ Available Indicators:**")
                display_dataframe_full_width(pd.DataFrame(available))

            if missing:
                st.markdown("**❌ Missing Indicators:**")
                st.write(", ".join(missing))
                st.warning("⚠️ Some FRED indicators failed to load. Check API key and connectivity.")

            st.metric("FRED Data Completeness", f"{len(available)}/{len(expected_indicators)}")
        else:
            st.error("❌ FRED data not loaded. Check FRED API key in secrets.toml")

    # Section 4: Sector Data Completeness
    with st.expander("🏢 Sector Data Quality", expanded=False):
        if st.button("🔄 Refresh Sector Snapshot (debug)"):
            if 'sector_snapshot' in st.session_state:
                del st.session_state['sector_snapshot']

        st.markdown("**11 GICS Sectors data check:**")

        if sector_data and isinstance(sector_data, dict):
            sector_status = []

            for sector, data_raw in sector_data.items():
                data = _extract_df(data_raw)
                has_data = data is not None and not data.empty
                sector_status.append({
                    'Sector': sector,
                    'Status': '✅' if has_data else '❌',
                    'Data Points': len(data) if has_data else 0,
                    'Latest Date': str(data.index[-1].date()) if has_data and len(data) > 0 else 'N/A'
                })

            display_dataframe_full_width(pd.DataFrame(sector_status))

            available_sectors = sum(1 for s in sector_status if s['Status'] == '✅')
            st.metric("Sectors Loaded", f"{available_sectors}/11")
        else:
            st.error("❌ Sector data not loaded")

    # Section 5: Cache Status
    with st.expander("💾 Cache Status", expanded=False):
        st.markdown("**Streamlit cache information:**")

        st.markdown("""
        **Cached functions in this page:**
        - `fetch_market_indices()` - Market indices data
        - `fetch_sector_data()` - Sector ETF data
        - `fetch_economic_data()` - FRED economic indicators
        - `fetch_fear_greed_index()` - CNN Fear & Greed
        - `fetch_global_indices()` - International markets

        **Note**: Cache is automatically managed by Streamlit with TTL (Time-To-Live).
        """)

        if st.button("🗑️ Clear All Caches", help="Clear all cached data and force fresh API calls"):
            st.cache_data.clear()
            st.success("✅ All caches cleared! Refresh the page to reload data.")

    # Section 6: Performance Metrics
    with st.expander("⚡ Performance Metrics", expanded=False):
        st.markdown("**Data loading performance:**")

        import time

        # Test market indices fetch
        start = time.time()
        try:
            from data_fetcher import fetch_market_indices
            test_indices = fetch_market_indices(period='5d')
            indices_time = time.time() - start
            indices_status = '✅' if test_indices else '❌'
        except Exception as e:
            indices_time = time.time() - start
            indices_status = f'❌ Error: {str(e)[:50]}'

        # Test FRED fetch
        start = time.time()
        try:
            from data_fetcher import fetch_economic_data
            test_fred = fetch_economic_data()
            fred_time = time.time() - start
            fred_status = '✅' if test_fred else '❌'
        except Exception as e:
            fred_time = time.time() - start
            fred_status = f'❌ Error: {str(e)[:50]}'

        st.markdown("**API Response Times:**")
        col1, col2 = st.columns(2)
        col1.metric("Market Indices", f"{indices_time:.2f}s", delta=indices_status)
        col2.metric("FRED Data", f"{fred_time:.2f}s", delta=fred_status)

        total_time = indices_time + fred_time
        st.metric("Total Load Time", f"{total_time:.2f}s")

        if total_time > 10:
            st.warning("⚠️ Load times are high. Consider checking internet connectivity or API rate limits.")

    # Section 7: Raw Data Inspector
    with st.expander("🔍 Raw Data Inspector", expanded=False):
        st.markdown("**Inspect raw data structures:**")

        data_source = st.selectbox(
            "Select data source to inspect:",
            ["Market Indices", "Market Health", "Sector Data", "FRED Data"],
            key="debug_data_source_selector"
        )

        if data_source == "Market Indices":
            if indices_data:
                st.write("**Available indices:**", list(indices_data.keys()))
                selected_index = st.selectbox("Select index:", list(indices_data.keys()), key="debug_index_selector")
                if selected_index:
                    raw = indices_data[selected_index]
                    df = _extract_df(raw)
                    if df is not None:
                        display_dataframe_full_width(df.tail(10))
                    else:
                        st.write(raw)
            else:
                st.error("No indices data available")

        elif data_source == "Market Health":
            if market_health:
                st.json(market_health)
            else:
                st.error("No market health data available")

        elif data_source == "Sector Data":
            if sector_data:
                st.write("**Available sectors:**", list(sector_data.keys()))
                selected_sector = st.selectbox("Select sector:", list(sector_data.keys()), key="debug_sector_selector")
                if selected_sector:
                    display_dataframe_full_width(sector_data[selected_sector].tail(10))
            else:
                st.error("No sector data available")

        elif data_source == "FRED Data":
            if fred_data:
                st.write("**Available indicators:**", list(fred_data.keys()))
                selected_indicator = st.selectbox("Select indicator:", list(fred_data.keys()), key="debug_fred_selector")
                if selected_indicator and fred_data[selected_indicator] is not None:
                    display_dataframe_full_width(fred_data[selected_indicator].tail(10))
            else:
                st.error("No FRED data available")


# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == "__main__":
    render_page()
