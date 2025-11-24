"""
Advanced Visual Analysis Presets
Provides preset configurations for loading groups of advanced technical visualizations
Similar pattern to trading strategy presets for familiar UX
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from app_utils import plotly_full_width, display_dataframe_full_width
import yfinance as yf
from datetime import datetime, timedelta
from mode_config import get_cache_ttl


# ===== SECTOR TO ETF MAPPING =====
SECTOR_ETF_MAP = {
    'Technology': 'XLK',
    'Financials': 'XLF',
    'Health Care': 'XLV',
    'Healthcare': 'XLV',
    'Consumer Discretionary': 'XLY',
    'Consumer Cyclical': 'XLY',
    'Industrials': 'XLI',
    'Energy': 'XLE',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Materials': 'XLB',
    'Consumer Staples': 'XLP',
    'Consumer Defensive': 'XLP',
    'Communication Services': 'XLC',
    'Communication': 'XLC',
    'Financial Services': 'XLF'
}


# ===== CACHED DATA FETCHING FUNCTIONS =====

@st.cache_data(ttl=get_cache_ttl("medium"))
def fetch_spy_data(period="6mo"):
    """Fetch SPY data with caching"""
    try:
        spy = yf.download("SPY", period=period, progress=False)
        return spy if not spy.empty else None
    except Exception as e:
        return None


@st.cache_data(ttl=get_cache_ttl("medium"))
def fetch_sector_etf_data(etf_ticker, period="6mo"):
    """Fetch sector ETF data with caching"""
    try:
        etf = yf.download(etf_ticker, period=period, progress=False)
        return etf if not etf.empty else None
    except Exception as e:
        return None


@st.cache_data(ttl=get_cache_ttl("fast"))
def fetch_multi_timeframe_data(ticker):
    """Fetch multiple timeframes for a ticker with caching"""
    try:
        data = {}

        # Fetch different timeframes
        timeframes = {
            '5m': {'period': '5d', 'interval': '5m'},
            '15m': {'period': '5d', 'interval': '15m'},
            '1h': {'period': '1mo', 'interval': '1h'},
            '1d': {'period': '6mo', 'interval': '1d'},
            '1wk': {'period': '2y', 'interval': '1wk'}
        }

        for tf_name, params in timeframes.items():
            df = yf.download(ticker, period=params['period'], interval=params['interval'], progress=False)
            if not df.empty:
                data[tf_name] = df

        return data if data else None
    except Exception as e:
        return None


def get_sector_etf(ticker):
    """Get sector ETF ticker for a given stock"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get('sector', '')
        return SECTOR_ETF_MAP.get(sector, 'SPY')  # Default to SPY if sector not found
    except:
        return 'SPY'  # Default fallback


# ===== VISUAL ANALYSIS PRESET CONFIGURATION =====
VISUAL_ANALYSIS_PRESETS = {
    'quick_scan': {
        'name': 'Quick Scan',
        'emoji': '⚡',
        'category': 'BEGINNER FRIENDLY',
        'description': 'Essential visuals - fast loading, easy to understand',
        'load_time': '~0.3s',
        'best_for': 'Quick daily check-ins and overview analysis',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': True,
            'support_resistance': False,
            'divergence_scanner': False,
            'correlation_matrix': False,
            'timeframe_alignment': False,
            'regime_detection': False,
            'relative_strength': False,
            'atr_projection': False
        },
        'tutorial': {
            'what': 'Volume Profile shows key price levels, Strength Meter gives trend confidence, Pattern Recognition spots candlestick signals.',
            'why': 'These three visuals answer: Where are the key levels? Is the trend strong? Are there reversal patterns?',
            'when': 'Use daily for quick assessment before diving deeper.'
        }
    },

    'entry_exit': {
        'name': 'Entry/Exit Timing',
        'emoji': '🎯',
        'category': 'TRADING DECISIONS',
        'description': 'Pinpoint when to buy/sell with precision',
        'load_time': '~1.5s',
        'best_for': 'Active traders looking for optimal entry and exit points',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': True,
            'support_resistance': True,
            'divergence_scanner': True,
            'correlation_matrix': False,
            'timeframe_alignment': True,
            'regime_detection': True,
            'relative_strength': False,
            'atr_projection': False
        },
        'tutorial': {
            'what': 'Divergence Scanner spots reversals, Multi-Timeframe Alignment confirms trend across periods, S/R shows bounce zones.',
            'why': 'Combines timing signals from multiple indicators to increase confidence in entry/exit decisions.',
            'when': 'Use when actively looking to open or close positions.'
        }
    },

    'risk_assessment': {
        'name': 'Risk Assessment',
        'emoji': '🛡️',
        'category': 'TRADING DECISIONS',
        'description': 'Evaluate position sizing and volatility',
        'load_time': '~1.2s',
        'best_for': 'Traders who need to size positions and set stop losses',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': False,
            'support_resistance': True,
            'divergence_scanner': False,
            'correlation_matrix': False,
            'timeframe_alignment': False,
            'regime_detection': True,
            'relative_strength': False,
            'atr_projection': True
        },
        'tutorial': {
            'what': 'ATR Projection shows expected price range, Regime Detection identifies market conditions, S/R provides stop-loss levels.',
            'why': 'Understanding volatility and market regime helps you size positions appropriately and set proper stops.',
            'when': 'Use before entering any position to determine proper risk parameters.'
        }
    },

    'market_context': {
        'name': 'Market Context',
        'emoji': '🌍',
        'category': 'COMPARATIVE ANALYSIS',
        'description': 'Compare performance vs market and peers',
        'load_time': '~2.5s',
        'best_for': 'Understanding if a stock is leading or lagging the market',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': False,
            'support_resistance': False,
            'divergence_scanner': False,
            'correlation_matrix': True,
            'timeframe_alignment': False,
            'regime_detection': True,
            'relative_strength': True,
            'atr_projection': False
        },
        'tutorial': {
            'what': 'Relative Strength vs SPY/sector, Correlation Matrix shows relationship with market, Regime Detection identifies broader conditions.',
            'why': 'A stock might look strong, but if the entire market is rallying, it could be underperforming relatively.',
            'when': 'Use for portfolio construction and understanding systematic vs idiosyncratic moves.'
        }
    },

    'reversal_hunter': {
        'name': 'Reversal Hunter',
        'emoji': '🔄',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Catch trend reversals early',
        'load_time': '~1.8s',
        'best_for': 'Contrarian traders looking for turning points',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': True,
            'support_resistance': True,
            'divergence_scanner': True,
            'correlation_matrix': False,
            'timeframe_alignment': True,
            'regime_detection': False,
            'relative_strength': False,
            'atr_projection': False
        },
        'tutorial': {
            'what': 'Divergence Scanner (key!), Candlestick Patterns, Volume Profile value areas, S/R bounce zones.',
            'why': 'Divergences are the #1 reversal indicator. Combined with patterns and S/R, you can catch turns early.',
            'when': 'Use when you suspect a trend is exhausting or price is overextended.'
        }
    },

    'breakout_confirmation': {
        'name': 'Breakout Confirmation',
        'emoji': '🚀',
        'category': 'SPECIALIZED STRATEGIES',
        'description': 'Validate breakouts with volume and momentum',
        'load_time': '~1.5s',
        'best_for': 'Momentum traders riding breakouts',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': False,
            'support_resistance': True,
            'divergence_scanner': False,
            'correlation_matrix': False,
            'timeframe_alignment': True,
            'regime_detection': True,
            'relative_strength': True,
            'atr_projection': True
        },
        'tutorial': {
            'what': 'Volume Profile for breakout levels, S/R clusters, Timeframe Alignment confirms momentum, ATR shows expected move size.',
            'why': 'False breakouts are common. This preset ensures volume confirms the move and multiple timeframes agree.',
            'when': 'Use when price approaches a major resistance level or is breaking out of consolidation.'
        }
    },

    'institutional_view': {
        'name': 'Institutional View',
        'emoji': '🏛️',
        'category': 'ADVANCED ANALYSIS',
        'description': 'See what big money is doing',
        'load_time': '~2.8s',
        'best_for': 'Following smart money and institutional activity',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': False,
            'support_resistance': True,
            'divergence_scanner': False,
            'correlation_matrix': True,
            'timeframe_alignment': False,
            'regime_detection': True,
            'relative_strength': True,
            'atr_projection': False
        },
        'tutorial': {
            'what': 'Volume Profile (where institutions accumulated), Correlation Matrix (systematic flows), Relative Strength (leader/laggard).',
            'why': 'Institutions move markets. Volume Profile shows their footprints, correlation shows their sector bets.',
            'when': 'Use for swing trading and position building where institutional activity matters.'
        }
    },

    'full_diagnostic': {
        'name': 'Full Diagnostic',
        'emoji': '🔬',
        'category': 'ADVANCED ANALYSIS',
        'description': 'Every visual loaded - comprehensive analysis',
        'load_time': '~3.5s',
        'best_for': 'Deep research on high-conviction opportunities',
        'visuals': {
            'volume_profile': True,
            'strength_meter': True,
            'candlestick_patterns': True,
            'support_resistance': True,
            'divergence_scanner': True,
            'correlation_matrix': True,
            'timeframe_alignment': True,
            'regime_detection': True,
            'relative_strength': True,
            'atr_projection': True
        },
        'tutorial': {
            'what': 'All available visualizations loaded for maximum insight.',
            'why': 'When making major trading decisions or portfolio allocations, you want every data point.',
            'when': 'Use sparingly - only when doing comprehensive research on a potential major position.'
        }
    }
}


def apply_visual_preset(preset_key):
    """Apply a visual preset configuration to session state"""
    if preset_key in VISUAL_ANALYSIS_PRESETS:
        preset = VISUAL_ANALYSIS_PRESETS[preset_key]
        st.session_state['active_visual_preset'] = preset_key

        # Store which visuals to show in session state
        for visual_name, should_show in preset['visuals'].items():
            st.session_state[f'show_{visual_name}'] = should_show


def render_preset_selector():
    """Render the preset dropdown selector UI (matches trading strategy pattern)"""

    # Build preset categories
    preset_categories = {
        'BEGINNER FRIENDLY': [],
        'TRADING DECISIONS': [],
        'COMPARATIVE ANALYSIS': [],
        'SPECIALIZED STRATEGIES': [],
        'ADVANCED ANALYSIS': []
    }

    for key, preset in VISUAL_ANALYSIS_PRESETS.items():
        category = preset['category']
        display_text = f"{preset['emoji']} {preset['name']}"
        preset_categories[category].append({
            'key': key,
            'display': display_text
        })

    # Build dropdown options with category headers
    preset_options = []
    preset_keys_map = {}

    category_order = [
        'BEGINNER FRIENDLY',
        'TRADING DECISIONS',
        'COMPARATIVE ANALYSIS',
        'SPECIALIZED STRATEGIES',
        'ADVANCED ANALYSIS'
    ]

    for category in category_order:
        if category in preset_categories and preset_categories[category]:
            preset_options.append(f"━━━ {category} ━━━")
            preset_keys_map[f"━━━ {category} ━━━"] = None  # Header, not selectable

            for preset in preset_categories[category]:
                display_text = preset['display']
                preset_options.append(f"  {display_text}")
                preset_keys_map[f"  {display_text}"] = preset['key']

    # UI Layout: Dropdown + Info Button + Active Badge
    preset_col1, preset_col2, preset_col3 = st.columns([3, 1, 2])

    with preset_col1:
        # Initialize default selection
        if 'visual_preset_selection' not in st.session_state:
            st.session_state.visual_preset_selection = "  ⚡ Quick Scan"

        selected_display = st.selectbox(
            "Select Visual Analysis Preset:",
            options=preset_options,
            index=preset_options.index(st.session_state.visual_preset_selection)
                  if st.session_state.visual_preset_selection in preset_options else 0,
            key="visual_preset_selector",
            label_visibility="collapsed"
        )

        # Apply preset if selection changed and it's not a category header
        selected_key = preset_keys_map.get(selected_display)
        if selected_key:
            if st.session_state.get('active_visual_preset') != selected_key:
                apply_visual_preset(selected_key)
                st.session_state.visual_preset_selection = selected_display
                st.rerun()

    with preset_col2:
        # Info popover with preset details
        with st.popover("ℹ️ Info"):
            active_key = st.session_state.get('active_visual_preset', 'quick_scan')
            if active_key in VISUAL_ANALYSIS_PRESETS:
                preset_info = VISUAL_ANALYSIS_PRESETS[active_key]
                st.markdown(f"### {preset_info['emoji']} {preset_info['name']}")
                st.markdown(f"**Description:** {preset_info['description']}")
                st.markdown(f"**Best For:** {preset_info['best_for']}")
                st.markdown(f"**Load Time:** {preset_info['load_time']}")

                st.markdown("---")
                st.markdown("#### 📚 Usage Guide")
                st.markdown(f"**What:** {preset_info['tutorial']['what']}")
                st.markdown(f"**Why:** {preset_info['tutorial']['why']}")
                st.markdown(f"**When:** {preset_info['tutorial']['when']}")

    with preset_col3:
        # Active preset badge
        active_key = st.session_state.get('active_visual_preset', 'quick_scan')
        if active_key in VISUAL_ANALYSIS_PRESETS:
            active_preset = VISUAL_ANALYSIS_PRESETS[active_key]
            st.markdown(
                f"""<div style='background-color: #2196F3; color: white; padding: 8px 12px;
                border-radius: 5px; text-align: center; font-weight: bold; margin-top: 0px;'>
                ✓ Active: {active_preset['emoji']} {active_preset['name']}
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Preset comparison table (expandable)
    with st.expander("📊 **COMPARE ALL PRESETS** - View side-by-side comparison", expanded=False):
        st.markdown("**Compare all visual analysis presets to find the best fit for your needs:**")

        comparison_data = []
        for key, preset in VISUAL_ANALYSIS_PRESETS.items():
            num_visuals = sum(preset['visuals'].values())
            comparison_data.append({
                'Preset': f"{preset['emoji']} {preset['name']}",
                'Category': preset['category'],
                'Visuals': f"{num_visuals}/10",
                'Load Time': preset['load_time'],
                'Best For': preset['best_for']
            })

        comparison_df = pd.DataFrame(comparison_data)
        display_dataframe_full_width(comparison_df, hide_index=True)

        st.markdown("**💡 Tip:** Click the ℹ️ Info button above after selecting a preset to see detailed usage guide.")


def render_advanced_visual_analysis_section(ticker, price_data):
    """
    Main entry point for the Advanced Visual Analysis section
    Renders preset selector and all active visualizations
    """
    st.markdown("---")
    st.markdown("## 🔬 Advanced Visual Analysis")
    st.caption("Load preset groups of advanced charts based on your analysis needs")

    # Initialize default preset if not set
    if 'active_visual_preset' not in st.session_state:
        apply_visual_preset('quick_scan')

    # Render preset selector UI
    render_preset_selector()

    st.markdown("---")

    # Render the actual visual charts based on active preset
    render_visual_charts(ticker, price_data)


def render_visual_charts(ticker, price_data):
    """
    Dispatcher function that renders charts based on session state
    Only loads visuals that are enabled in the active preset
    """

    # Volume Profile (Core visual - in most presets)
    if st.session_state.get('show_volume_profile', True):
        with st.spinner("📊 Loading Volume Profile..."):
            render_volume_profile(price_data)

    # Strength Meter (Core visual - in most presets)
    if st.session_state.get('show_strength_meter', True):
        render_strength_meter(price_data)

    # Candlestick Pattern Recognition
    if st.session_state.get('show_candlestick_patterns', True):
        with st.spinner("🕯️ Detecting candlestick patterns..."):
            render_candlestick_patterns(price_data)

    # Support/Resistance Levels
    if st.session_state.get('show_support_resistance', False):
        with st.spinner("🎯 Calculating support/resistance levels..."):
            render_support_resistance(price_data)

    # Momentum Divergence Scanner
    if st.session_state.get('show_divergence_scanner', False):
        with st.spinner("⚠️ Scanning for divergences..."):
            render_divergence_scanner(price_data)

    # Multi-Timeframe Alignment
    if st.session_state.get('show_timeframe_alignment', False):
        with st.spinner("📈 Loading multi-timeframe analysis..."):
            render_timeframe_alignment(ticker)

    # Market Regime Detection
    if st.session_state.get('show_regime_detection', False):
        render_regime_detection(price_data)

    # Relative Strength vs Market
    if st.session_state.get('show_relative_strength', False):
        with st.spinner("🌍 Loading market comparison data..."):
            render_relative_strength(ticker, price_data)

    # ATR Volatility Projection
    if st.session_state.get('show_atr_projection', False):
        render_atr_projection(price_data)

    # Correlation Matrix
    if st.session_state.get('show_correlation_matrix', False):
        with st.spinner("🔢 Calculating correlations..."):
            render_correlation_matrix(ticker, price_data)


# ===== PLACEHOLDER RENDER FUNCTIONS (TO BE IMPLEMENTED) =====
# These are stubs that we'll implement one by one

def render_volume_profile(price_data):
    """
    Render horizontal volume profile chart
    Shows volume distribution across price levels with POC and Value Areas
    """
    st.markdown("### 📊 Volume Profile")
    st.caption("Horizontal histogram showing volume traded at each price level. High volume = strong support/resistance.")

    try:
        # Calculate volume profile
        df = price_data.copy()

        # Determine number of price bins (typically 24-50 for good granularity)
        num_bins = min(50, max(24, len(df) // 10))

        # Get price range
        price_min = df['Low'].min()
        price_max = df['High'].max()
        price_range = price_max - price_min

        # Create price bins
        bin_size = price_range / num_bins
        bins = np.linspace(price_min, price_max, num_bins + 1)

        # Calculate volume at each price level
        volume_profile = np.zeros(num_bins)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        # For each candle, distribute volume across price bins it touched
        for idx, row in df.iterrows():
            low = row['Low']
            high = row['High']
            volume = row['Volume']

            # Find which bins this candle touched
            touched_bins = (bins[:-1] <= high) & (bins[1:] >= low)
            num_touched = touched_bins.sum()

            if num_touched > 0:
                # Distribute volume evenly across touched bins
                volume_profile[touched_bins] += volume / num_touched

        # Calculate key levels
        total_volume = volume_profile.sum()

        # Point of Control (POC) - price level with highest volume
        poc_idx = np.argmax(volume_profile)
        poc_price = bin_centers[poc_idx]
        poc_volume = volume_profile[poc_idx]

        # Value Area (VA) - price range containing 70% of volume
        # Sort bins by volume
        sorted_indices = np.argsort(volume_profile)[::-1]
        cumulative_volume = 0
        va_threshold = total_volume * 0.70
        value_area_bins = []

        for idx in sorted_indices:
            cumulative_volume += volume_profile[idx]
            value_area_bins.append(idx)
            if cumulative_volume >= va_threshold:
                break

        # Value Area High and Low
        vah_price = bin_centers[max(value_area_bins)]
        val_price = bin_centers[min(value_area_bins)]

        # Current price
        current_price = df['Close'].iloc[-1]

        # Create the volume profile chart
        col1, col2 = st.columns([3, 1])

        with col1:
            fig = go.Figure()

            # Add horizontal volume bars
            colors = ['#2196F3' if i in value_area_bins else '#B0BEC5'
                     for i in range(num_bins)]
            colors[poc_idx] = '#00C853'  # Highlight POC in bright green

            fig.add_trace(go.Bar(
                y=bin_centers,
                x=volume_profile,
                orientation='h',
                marker=dict(color=colors),
                hovertemplate='Price: $%{y:.2f}<br>Volume: %{x:,.0f}<extra></extra>',
                showlegend=False
            ))

            # Add POC line
            fig.add_hline(
                y=poc_price,
                line=dict(color='#00C853', width=3, dash='solid'),
                annotation_text=f"POC: ${poc_price:.2f}",
                annotation_position="right",
                annotation_font=dict(size=11, color='#00C853')
            )

            # Add Value Area High line
            fig.add_hline(
                y=vah_price,
                line=dict(color='#FF6F00', width=2, dash='dash'),
                annotation_text=f"VAH: ${vah_price:.2f}",
                annotation_position="right",
                annotation_font=dict(size=10, color='#FF6F00')
            )

            # Add Value Area Low line
            fig.add_hline(
                y=val_price,
                line=dict(color='#FF6F00', width=2, dash='dash'),
                annotation_text=f"VAL: ${val_price:.2f}",
                annotation_position="right",
                annotation_font=dict(size=10, color='#FF6F00')
            )

            # Add current price line
            fig.add_hline(
                y=current_price,
                line=dict(color='#FFA726', width=2, dash='dot'),
                annotation_text=f"Current: ${current_price:.2f}",
                annotation_position="right",
                annotation_font=dict(size=10, color='#FFA726')
            )

            # Shade Value Area
            fig.add_hrect(
                y0=val_price, y1=vah_price,
                fillcolor='rgba(33, 150, 243, 0.1)',
                line_width=0,
                layer='below'
            )

            fig.update_layout(
                title="Volume Profile - Horizontal Volume Distribution",
                xaxis_title="Volume",
                yaxis_title="Price ($)",
                height=500,
                showlegend=False,
                hovermode='y',
                margin=dict(r=120)  # Extra margin for annotations
            )

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 📊 Key Levels")

            # POC
            st.markdown(f"""
            <div style='background-color: #00C853; color: white; padding: 10px;
                 border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Point of Control</div>
                <div style='font-size: 18px; font-weight: bold;'>${poc_price:.2f}</div>
                <div style='font-size: 10px; opacity: 0.8;'>{poc_volume:,.0f} vol</div>
            </div>
            """, unsafe_allow_html=True)

            # Value Area
            st.markdown(f"""
            <div style='background-color: #FF6F00; color: white; padding: 10px;
                 border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Value Area (70%)</div>
                <div style='font-size: 16px; font-weight: bold;'>${val_price:.2f} - ${vah_price:.2f}</div>
                <div style='font-size: 10px; opacity: 0.8;'>Range: ${vah_price - val_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Current Price Position
            if current_price > vah_price:
                position = "Above Value Area"
                position_color = "#4CAF50"
                position_emoji = "🔼"
                interpretation = "Bullish - trading above fair value"
            elif current_price < val_price:
                position = "Below Value Area"
                position_color = "#F44336"
                position_emoji = "🔽"
                interpretation = "Bearish - trading below fair value"
            else:
                position = "Inside Value Area"
                position_color = "#2196F3"
                position_emoji = "↔️"
                interpretation = "Neutral - trading at fair value"

            st.markdown(f"""
            <div style='background-color: {position_color}; color: white; padding: 10px;
                 border-radius: 5px; text-align: center;'>
                <div style='font-size: 11px; opacity: 0.9;'>Price Position</div>
                <div style='font-size: 16px; font-weight: bold;'>{position_emoji} {position}</div>
                <div style='font-size: 10px; opacity: 0.8;'>{interpretation}</div>
            </div>
            """, unsafe_allow_html=True)

        # Trading implications
        st.markdown("---")
        st.markdown("#### 💡 How to Use Volume Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Point of Control (POC)**
            - Green line = highest volume
            - Strong support/resistance
            - Price tends to return to POC
            - Good for mean reversion trades
            """)

            st.markdown("""
            **📊 Value Area (Orange zone)**
            - Contains 70% of volume
            - "Fair price" range
            - Above VAH = bullish
            - Below VAL = bearish
            """)

        with col2:
            st.markdown("""
            **📈 Trading Strategies**
            - Buy at VAL, sell at VAH (range)
            - Breakout above VAH = bullish continuation
            - Breakdown below VAL = bearish continuation
            - POC acts as magnet for price
            """)

            st.markdown("""
            **⚠️ High Volume Nodes (HVN)**
            - Tall bars = strong levels
            - Price consolidates at HVNs
            - Difficult to break through
            - Low Volume Nodes = easy breakouts
            """)

    except Exception as e:
        st.error(f"Error calculating volume profile: {str(e)}")
        st.info("Volume profile requires OHLCV data with at least 20 bars.")


def render_strength_meter(price_data):
    """
    Render composite strength/confidence meter
    Aggregates multiple indicators into a single trend strength score
    """
    st.markdown("### 💪 Trend Strength Meter")
    st.caption("Composite confidence score from multiple indicators - higher = stronger trend")

    try:
        df = price_data.copy()

        # Calculate all necessary indicators
        # Moving Averages
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        # Prevent division by zero: replace 0 with small number
        rs = gain / loss.replace(0, 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # ADX (simplified)
        high = df['High']
        low = df['Low']
        close = df['Close']
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1, join='inner').max(axis=1)
        atr = tr.rolling(14).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10))
        minus_di = abs(100 * (minus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10)))
        # Prevent division by zero in DX calculation
        denominator = abs(plus_di + minus_di).replace(0, 1e-10)
        dx = (abs(plus_di - minus_di) / denominator) * 100
        df['ADX'] = dx.ewm(alpha=1/14).mean()

        # Volume
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()

        # Get current values
        current_price = df['Close'].iloc[-1]
        current_rsi = df['RSI'].iloc[-1]
        current_macd = df['MACD'].iloc[-1]
        current_macd_signal = df['MACD_Signal'].iloc[-1]
        current_adx = df['ADX'].iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume_SMA'].iloc[-1]

        # Calculate individual component scores (0-100)

        # 1. Trend Strength (MA alignment)
        trend_score = 0
        if pd.notna(df['SMA20'].iloc[-1]) and pd.notna(df['SMA50'].iloc[-1]) and pd.notna(df['SMA200'].iloc[-1]):
            if current_price > df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
                trend_score = 100  # Perfect bullish alignment
            elif current_price > df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
                trend_score = 75
            elif current_price > df['SMA20'].iloc[-1]:
                trend_score = 50
            elif current_price < df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1] < df['SMA200'].iloc[-1]:
                trend_score = 0  # Perfect bearish alignment
            elif current_price < df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
                trend_score = 25
            else:
                trend_score = 50  # Mixed signals

        # 2. Momentum Strength (RSI)
        if pd.notna(current_rsi):
            if 40 <= current_rsi <= 60:
                momentum_score = 50  # Neutral
            elif current_rsi > 60:
                momentum_score = min(100, 50 + (current_rsi - 60) * 1.25)  # Bullish
            else:
                momentum_score = max(0, 50 - (40 - current_rsi) * 1.25)  # Bearish
        else:
            momentum_score = 50

        # 3. MACD Strength
        if pd.notna(current_macd) and pd.notna(current_macd_signal):
            macd_diff = current_macd - current_macd_signal
            if macd_diff > 0:
                macd_score = min(100, 50 + abs(macd_diff) * 50)
            else:
                macd_score = max(0, 50 - abs(macd_diff) * 50)
        else:
            macd_score = 50

        # 4. Trend Intensity (ADX)
        if pd.notna(current_adx):
            # ADX: <20 weak, 20-40 developing, 40-60 strong, >60 very strong
            adx_score = min(100, (current_adx / 60) * 100)
        else:
            adx_score = 50

        # 5. Volume Confirmation
        if pd.notna(current_volume) and pd.notna(avg_volume) and avg_volume > 0:
            volume_ratio = current_volume / avg_volume
            if volume_ratio > 1.5:
                volume_score = 100  # High volume confirmation
            elif volume_ratio > 1.0:
                volume_score = 75
            elif volume_ratio > 0.75:
                volume_score = 50
            else:
                volume_score = 25  # Low volume - weak confidence
        else:
            volume_score = 50

        # Calculate overall confidence score (weighted average)
        weights = {
            'trend': 0.30,      # 30% - Most important
            'momentum': 0.20,   # 20%
            'macd': 0.20,       # 20%
            'adx': 0.20,        # 20%
            'volume': 0.10      # 10% - Confirmation factor
        }

        overall_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            macd_score * weights['macd'] +
            adx_score * weights['adx'] +
            volume_score * weights['volume']
        )

        # Determine overall sentiment
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

        # Create gauge charts
        col1, col2 = st.columns([2, 1])

        with col1:
            # Main overall confidence gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=overall_score,
                title={'text': "Overall Trend Confidence", 'font': {'size': 20}},
                delta={'reference': 50, 'increasing': {'color': "#4CAF50"}, 'decreasing': {'color': "#F44336"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': sentiment_color, 'thickness': 0.75},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 30], 'color': '#FFCDD2'},
                        {'range': [30, 45], 'color': '#FFE0B2'},
                        {'range': [45, 55], 'color': '#FFF9C4'},
                        {'range': [55, 70], 'color': '#C8E6C9'},
                        {'range': [70, 100], 'color': '#A5D6A7'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))

            fig.update_layout(
                height=350,
                margin=dict(l=20, r=20, t=50, b=20)
            )

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Assessment")
            st.markdown(f"""
            <div style='background-color: {sentiment_color}; color: white; padding: 15px;
                 border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                <div style='font-size: 40px;'>{sentiment_emoji}</div>
                <div style='font-size: 20px; font-weight: bold;'>{sentiment}</div>
                <div style='font-size: 16px; margin-top: 5px;'>{overall_score:.1f}/100</div>
            </div>
            """, unsafe_allow_html=True)

            # Interpretation
            if overall_score >= 70:
                st.success("✅ High confidence in uptrend. Strong entry signal.")
            elif overall_score >= 55:
                st.info("✓ Moderate uptrend. Consider scaling in.")
            elif overall_score >= 45:
                st.warning("⚠️ Mixed signals. Wait for clarity.")
            elif overall_score >= 30:
                st.info("✓ Moderate downtrend. Consider reducing exposure.")
            else:
                st.error("⛔ High confidence in downtrend. Avoid longs.")

        # Component breakdown
        st.markdown("---")
        st.markdown("#### 📊 Component Breakdown")

        components = [
            ("Trend (MA Alignment)", trend_score, weights['trend']),
            ("Momentum (RSI)", momentum_score, weights['momentum']),
            ("MACD Signal", macd_score, weights['macd']),
            ("Trend Intensity (ADX)", adx_score, weights['adx']),
            ("Volume Confirmation", volume_score, weights['volume'])
        ]

        cols = st.columns(5)
        for idx, (name, score, weight) in enumerate(components):
            with cols[idx]:
                # Mini gauge for each component
                fig_mini = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={'text': name, 'font': {'size': 11}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': '#4CAF50' if score >= 50 else '#F44336', 'thickness': 0.6},
                        'bgcolor': "white",
                        'steps': [
                            {'range': [0, 50], 'color': '#FFCDD2'},
                            {'range': [50, 100], 'color': '#C8E6C9'}
                        ]
                    }
                ))
                fig_mini.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
                plotly_full_width(fig_mini)
                st.caption(f"Weight: {weight*100:.0f}%")

        # Explanation
        st.markdown("---")
        st.markdown("#### 💡 How to Interpret")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🎯 Confidence Levels**
            - **70-100**: Strong trend, high confidence trades
            - **55-70**: Moderate trend, scale positions
            - **45-55**: No clear trend, stay cautious
            - **30-45**: Weak opposite trend emerging
            - **0-30**: Strong opposite trend, avoid
            """)

        with col2:
            st.markdown("""
            **📈 Component Weights**
            - **Trend (30%)**: MA alignment is key
            - **Momentum (20%)**: RSI confirms direction
            - **MACD (20%)**: Momentum crossover signal
            - **ADX (20%)**: Measures trend strength
            - **Volume (10%)**: Confirms conviction
            """)

    except Exception as e:
        st.error(f"Error calculating strength meter: {str(e)}")
        st.info("Strength meter requires OHLCV data with at least 200 bars for accurate calculation.")


def render_candlestick_patterns(price_data):
    """
    Detect and display candlestick patterns
    Recognizes common reversal and continuation patterns
    """
    st.markdown("### 🕯️ Candlestick Pattern Recognition")
    st.caption("Automatically detects bullish and bearish candlestick patterns")

    try:
        df = price_data.copy()

        # Calculate body and wick sizes
        df['Body'] = abs(df['Close'] - df['Open'])
        df['UpperWick'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['LowerWick'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        df['Range'] = df['High'] - df['Low']
        df['BodyPercent'] = df['Body'] / df['Range']

        # Determine candle direction
        df['Bullish'] = df['Close'] > df['Open']

        # Pattern detection functions
        def is_doji(i):
            """Small body, long wicks"""
            return df['BodyPercent'].iloc[i] < 0.1 and df['Range'].iloc[i] > 0

        def is_hammer(i):
            """Small body at top, long lower wick (bullish)"""
            if i < 1:
                return False
            body_pct = df['BodyPercent'].iloc[i]
            lower_wick = df['LowerWick'].iloc[i]
            upper_wick = df['UpperWick'].iloc[i]
            body = df['Body'].iloc[i]
            return (body_pct < 0.3 and
                   lower_wick > body * 2 and
                   upper_wick < body * 0.5 and
                   not df['Bullish'].iloc[i-1])  # After downtrend

        def is_inverted_hammer(i):
            """Small body at bottom, long upper wick (bullish)"""
            if i < 1:
                return False
            body_pct = df['BodyPercent'].iloc[i]
            lower_wick = df['LowerWick'].iloc[i]
            upper_wick = df['UpperWick'].iloc[i]
            body = df['Body'].iloc[i]
            return (body_pct < 0.3 and
                   upper_wick > body * 2 and
                   lower_wick < body * 0.5 and
                   not df['Bullish'].iloc[i-1])

        def is_shooting_star(i):
            """Small body at bottom, long upper wick (bearish)"""
            if i < 1:
                return False
            body_pct = df['BodyPercent'].iloc[i]
            lower_wick = df['LowerWick'].iloc[i]
            upper_wick = df['UpperWick'].iloc[i]
            body = df['Body'].iloc[i]
            return (body_pct < 0.3 and
                   upper_wick > body * 2 and
                   lower_wick < body * 0.5 and
                   df['Bullish'].iloc[i-1])  # After uptrend

        def is_hanging_man(i):
            """Small body at top, long lower wick (bearish)"""
            if i < 1:
                return False
            body_pct = df['BodyPercent'].iloc[i]
            lower_wick = df['LowerWick'].iloc[i]
            upper_wick = df['UpperWick'].iloc[i]
            body = df['Body'].iloc[i]
            return (body_pct < 0.3 and
                   lower_wick > body * 2 and
                   upper_wick < body * 0.5 and
                   df['Bullish'].iloc[i-1])  # After uptrend

        def is_bullish_engulfing(i):
            """Current bullish candle engulfs previous bearish candle"""
            if i < 1:
                return False
            prev_bearish = not df['Bullish'].iloc[i-1]
            curr_bullish = df['Bullish'].iloc[i]
            curr_open = df['Open'].iloc[i]
            curr_close = df['Close'].iloc[i]
            prev_open = df['Open'].iloc[i-1]
            prev_close = df['Close'].iloc[i-1]
            return (prev_bearish and curr_bullish and
                   curr_open <= prev_close and
                   curr_close >= prev_open)

        def is_bearish_engulfing(i):
            """Current bearish candle engulfs previous bullish candle"""
            if i < 1:
                return False
            prev_bullish = df['Bullish'].iloc[i-1]
            curr_bearish = not df['Bullish'].iloc[i]
            curr_open = df['Open'].iloc[i]
            curr_close = df['Close'].iloc[i]
            prev_open = df['Open'].iloc[i-1]
            prev_close = df['Close'].iloc[i-1]
            return (prev_bullish and curr_bearish and
                   curr_open >= prev_close and
                   curr_close <= prev_open)

        def is_morning_star(i):
            """Three-candle bullish reversal"""
            if i < 2:
                return False
            first_bearish = not df['Bullish'].iloc[i-2] and df['Body'].iloc[i-2] > df['Body'].iloc[i-1]
            middle_small = df['BodyPercent'].iloc[i-1] < 0.3
            third_bullish = df['Bullish'].iloc[i] and df['Body'].iloc[i] > df['Body'].iloc[i-1]
            return first_bearish and middle_small and third_bullish

        def is_evening_star(i):
            """Three-candle bearish reversal"""
            if i < 2:
                return False
            first_bullish = df['Bullish'].iloc[i-2] and df['Body'].iloc[i-2] > df['Body'].iloc[i-1]
            middle_small = df['BodyPercent'].iloc[i-1] < 0.3
            third_bearish = not df['Bullish'].iloc[i] and df['Body'].iloc[i] > df['Body'].iloc[i-1]
            return first_bullish and middle_small and third_bearish

        # Scan for patterns
        patterns = []

        for i in range(2, len(df)):
            date = df.index[i]
            price = df['Close'].iloc[i]

            # Check each pattern
            if is_doji(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Doji', 'type': 'Neutral', 'strength': 'Weak'})
            elif is_hammer(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Hammer', 'type': 'Bullish', 'strength': 'Strong'})
            elif is_inverted_hammer(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Inverted Hammer', 'type': 'Bullish', 'strength': 'Moderate'})
            elif is_shooting_star(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Shooting Star', 'type': 'Bearish', 'strength': 'Strong'})
            elif is_hanging_man(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Hanging Man', 'type': 'Bearish', 'strength': 'Moderate'})
            elif is_bullish_engulfing(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Bullish Engulfing', 'type': 'Bullish', 'strength': 'Strong'})
            elif is_bearish_engulfing(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Bearish Engulfing', 'type': 'Bearish', 'strength': 'Strong'})
            elif is_morning_star(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Morning Star', 'type': 'Bullish', 'strength': 'Very Strong'})
            elif is_evening_star(i):
                patterns.append({'date': date, 'price': price, 'pattern': 'Evening Star', 'type': 'Bearish', 'strength': 'Very Strong'})

        # Filter to recent patterns (last 60 bars)
        recent_patterns = [p for p in patterns if (df.index[-1] - p['date']).days <= 60] if len(df) > 0 else patterns

        if len(recent_patterns) == 0:
            st.info("✅ No significant candlestick patterns detected in the recent period.")
            return

        # ===== VISUALIZATION =====
        st.markdown(f"#### 🕯️ {len(recent_patterns)} Pattern(s) Detected")

        col1, col2 = st.columns([3, 1])

        with col1:
            # Price chart with pattern markers
            fig = go.Figure()

            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ))

            # Add pattern markers
            for pattern in recent_patterns:
                if pattern['type'] == 'Bullish':
                    color = '#4CAF50'
                    symbol = 'triangle-up'
                elif pattern['type'] == 'Bearish':
                    color = '#F44336'
                    symbol = 'triangle-down'
                else:
                    color = '#FFC107'
                    symbol = 'diamond'

                fig.add_trace(go.Scatter(
                    x=[pattern['date']],
                    y=[pattern['price']],
                    mode='markers+text',
                    marker=dict(size=15, color=color, symbol=symbol, line=dict(width=2, color='white')),
                    text=[pattern['pattern']],
                    textposition='top center',
                    textfont=dict(size=9, color=color),
                    name=pattern['pattern'],
                    showlegend=False
                ))

            fig.update_layout(
                title="Price Chart with Candlestick Patterns",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=500,
                hovermode='x unified',
                showlegend=False
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Latest Pattern")

            if recent_patterns:
                latest = recent_patterns[-1]

                if latest['type'] == 'Bullish':
                    color = '#4CAF50'
                    emoji = '📈'
                elif latest['type'] == 'Bearish':
                    color = '#F44336'
                    emoji = '📉'
                else:
                    color = '#FFC107'
                    emoji = '➡️'

                st.markdown(f"""
                <div style='background-color: {color}; color: white; padding: 15px;
                     border-radius: 10px; text-align: center;'>
                    <div style='font-size: 40px;'>{emoji}</div>
                    <div style='font-size: 16px; font-weight: bold;'>{latest['pattern']}</div>
                    <div style='font-size: 14px; margin-top: 5px;'>{latest['type']}</div>
                    <div style='font-size: 12px; opacity: 0.9;'>{latest['strength']}</div>
                </div>
                """, unsafe_allow_html=True)

                bars_ago = len(df) - df.index.get_loc(latest['date']) - 1
                st.caption(f"Detected {bars_ago} bar(s) ago")

        # Pattern table
        st.markdown("---")
        st.markdown("#### 📊 All Recent Patterns")

        table_data = []
        for p in recent_patterns:
            bars_ago = len(df) - df.index.get_loc(p['date']) - 1
            type_emoji = '🟢' if p['type'] == 'Bullish' else ('🔴' if p['type'] == 'Bearish' else '🟡')

            table_data.append({
                'Pattern': f"{type_emoji} {p['pattern']}",
                'Type': p['type'],
                'Strength': p['strength'],
                'Price': f"${p['price']:.2f}",
                'Date': p['date'].strftime('%Y-%m-%d'),
                'Bars Ago': bars_ago
            })

        if table_data:
            table_df = pd.DataFrame(table_data)
            display_dataframe_full_width(table_df, hide_index=True)

        # Educational guide
        st.markdown("---")
        st.markdown("#### 💡 Pattern Reference Guide")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🟢 Bullish Patterns (Reversal)**
            - **Hammer**: Small body, long lower wick at bottom
            - **Inverted Hammer**: Small body, long upper wick at bottom
            - **Bullish Engulfing**: Big green engulfs previous red
            - **Morning Star**: 3-candle bottom reversal

            **🟡 Neutral Patterns**
            - **Doji**: Tiny body, indecision signal
            """)

        with col2:
            st.markdown("""
            **🔴 Bearish Patterns (Reversal)**
            - **Shooting Star**: Small body, long upper wick at top
            - **Hanging Man**: Small body, long lower wick at top
            - **Bearish Engulfing**: Big red engulfs previous green
            - **Evening Star**: 3-candle top reversal

            **⚠️ Confirmation Required**
            - Wait for next candle to confirm direction
            """)

    except Exception as e:
        st.error(f"Error detecting candlestick patterns: {str(e)}")
        st.info("Pattern recognition requires OHLCV data with at least 10 bars.")


def render_support_resistance(price_data):
    """
    Calculate and display support/resistance levels
    Uses swing highs/lows with clustering and strength scoring
    """
    st.markdown("### 🎯 Support & Resistance Levels")
    st.caption("Key price levels where the stock tends to bounce or break. Thicker lines = stronger levels.")

    try:
        df = price_data.copy()

        # Parameters
        lookback_window = 5  # How many bars to look back/forward for swing detection
        min_touches = 2  # Minimum touches to be considered a level
        cluster_threshold_pct = 0.015  # 1.5% - levels within this % are clustered together

        current_price = df['Close'].iloc[-1]
        price_min = df['Low'].min()
        price_max = df['High'].max()

        # ===== STEP 1: FIND SWING HIGHS AND LOWS =====
        swing_highs = []
        swing_lows = []

        for i in range(lookback_window, len(df) - lookback_window):
            # Swing High: Higher than surrounding candles
            is_swing_high = True
            for j in range(1, lookback_window + 1):
                if df['High'].iloc[i] <= df['High'].iloc[i-j] or df['High'].iloc[i] <= df['High'].iloc[i+j]:
                    is_swing_high = False
                    break
            if is_swing_high:
                swing_highs.append({
                    'price': df['High'].iloc[i],
                    'index': i,
                    'date': df.index[i]
                })

            # Swing Low: Lower than surrounding candles
            is_swing_low = True
            for j in range(1, lookback_window + 1):
                if df['Low'].iloc[i] >= df['Low'].iloc[i-j] or df['Low'].iloc[i] >= df['Low'].iloc[i+j]:
                    is_swing_low = False
                    break
            if is_swing_low:
                swing_lows.append({
                    'price': df['Low'].iloc[i],
                    'index': i,
                    'date': df.index[i]
                })

        # Combine all potential levels
        all_levels = swing_highs + swing_lows

        if len(all_levels) < 2:
            st.warning("Not enough data to identify support/resistance levels. Need at least 20+ bars.")
            return

        # ===== STEP 2: CLUSTER NEARBY LEVELS =====
        # Sort by price
        all_levels_sorted = sorted(all_levels, key=lambda x: x['price'])

        clustered_levels = []
        current_cluster = [all_levels_sorted[0]]

        for i in range(1, len(all_levels_sorted)):
            level = all_levels_sorted[i]
            cluster_avg = np.mean([l['price'] for l in current_cluster])

            # Check if this level is within cluster threshold of current cluster
            if abs(level['price'] - cluster_avg) / cluster_avg < cluster_threshold_pct:
                current_cluster.append(level)
            else:
                # Save the current cluster and start a new one
                clustered_levels.append(current_cluster)
                current_cluster = [level]

        # Add the last cluster
        clustered_levels.append(current_cluster)

        # ===== STEP 3: CALCULATE LEVEL STATISTICS =====
        sr_levels = []

        for cluster in clustered_levels:
            avg_price = np.mean([l['price'] for l in cluster])
            num_touches = len(cluster)

            # Calculate volume at these levels (sum volume from all touch points)
            total_volume = sum([df['Volume'].iloc[l['index']] for l in cluster if l['index'] < len(df)])
            avg_volume = total_volume / num_touches if num_touches > 0 else 0

            # Determine if it's support or resistance based on recent price action
            recent_bars = df.tail(20)
            recent_avg = recent_bars['Close'].mean()

            if avg_price < recent_avg:
                level_type = 'Support'
            else:
                level_type = 'Resistance'

            # Check for recent bounces (last 10 bars)
            recent_bounce = False
            for l in cluster:
                if l['index'] >= len(df) - 10:
                    recent_bounce = True
                    break

            # Check if level was broken recently
            recent_break = False
            if level_type == 'Support':
                # Check if price broke below and stayed below
                recent_lows = df.tail(5)['Low']
                if (recent_lows < avg_price * 0.98).any():
                    recent_break = True
            else:
                # Check if price broke above and stayed above
                recent_highs = df.tail(5)['High']
                if (recent_highs > avg_price * 1.02).any():
                    recent_break = True

            # Strength score (0-100)
            strength = min(100, (num_touches * 15) + (min(avg_volume / df['Volume'].mean(), 2) * 25))

            sr_levels.append({
                'price': avg_price,
                'type': level_type,
                'touches': num_touches,
                'strength': strength,
                'volume': avg_volume,
                'recent_bounce': recent_bounce,
                'recent_break': recent_break,
                'distance_pct': ((avg_price - current_price) / current_price) * 100
            })

        # Filter to only significant levels (min touches threshold)
        sr_levels = [l for l in sr_levels if l['touches'] >= min_touches]

        # Sort by strength
        sr_levels = sorted(sr_levels, key=lambda x: x['strength'], reverse=True)

        # Take top 10 most significant levels
        sr_levels = sr_levels[:10]

        if len(sr_levels) == 0:
            st.warning("No significant support/resistance levels found with current parameters.")
            return

        # ===== STEP 4: VISUALIZE =====
        col1, col2 = st.columns([3, 1])

        with col1:
            # Create price chart with S/R levels
            fig = go.Figure()

            # Add candlestick chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ))

            # Add S/R levels as horizontal lines
            for level in sr_levels:
                # Color and style based on type and status
                if level['recent_break']:
                    color = '#9E9E9E'  # Grey for broken levels
                    dash = 'dot'
                    opacity = 0.4
                elif level['type'] == 'Support':
                    color = '#4CAF50'  # Green for support
                    dash = 'solid'
                    opacity = 0.7
                else:
                    color = '#F44336'  # Red for resistance
                    dash = 'solid'
                    opacity = 0.7

                # Line width based on strength
                line_width = max(1, min(5, level['strength'] / 20))

                # Add horizontal line
                fig.add_hline(
                    y=level['price'],
                    line=dict(color=color, width=line_width, dash=dash),
                    opacity=opacity,
                    annotation_text=f"${level['price']:.2f} ({level['touches']} touches)",
                    annotation_position="right",
                    annotation_font=dict(size=9, color=color)
                )

            # Highlight current price
            fig.add_hline(
                y=current_price,
                line=dict(color='#FFA726', width=2, dash='dash'),
                annotation_text=f"Current: ${current_price:.2f}",
                annotation_position="left",
                annotation_font=dict(size=10, color='#FFA726')
            )

            fig.update_layout(
                title="Price Chart with Support/Resistance Levels",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=500,
                hovermode='x unified',
                showlegend=False,
                margin=dict(r=150)
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Key Levels")

            # Find nearest support and resistance
            supports = [l for l in sr_levels if l['type'] == 'Support' and l['price'] < current_price]
            resistances = [l for l in sr_levels if l['type'] == 'Resistance' and l['price'] > current_price]

            # Nearest support
            if supports:
                nearest_support = min(supports, key=lambda x: abs(x['distance_pct']))
                st.markdown(f"""
                <div style='background-color: #4CAF50; color: white; padding: 10px;
                     border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                    <div style='font-size: 11px; opacity: 0.9;'>Nearest Support</div>
                    <div style='font-size: 18px; font-weight: bold;'>${nearest_support['price']:.2f}</div>
                    <div style='font-size: 10px; opacity: 0.8;'>{abs(nearest_support['distance_pct']):.1f}% below</div>
                    <div style='font-size: 10px; opacity: 0.8;'>{nearest_support['touches']} touches</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No support levels below current price")

            # Nearest resistance
            if resistances:
                nearest_resistance = min(resistances, key=lambda x: abs(x['distance_pct']))
                st.markdown(f"""
                <div style='background-color: #F44336; color: white; padding: 10px;
                     border-radius: 5px; margin-bottom: 10px; text-align: center;'>
                    <div style='font-size: 11px; opacity: 0.9;'>Nearest Resistance</div>
                    <div style='font-size: 18px; font-weight: bold;'>${nearest_resistance['price']:.2f}</div>
                    <div style='font-size: 10px; opacity: 0.8;'>{abs(nearest_resistance['distance_pct']):.1f}% above</div>
                    <div style='font-size: 10px; opacity: 0.8;'>{nearest_resistance['touches']} touches</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No resistance levels above current price")

            # Trading zone info
            if supports and resistances:
                zone_range = nearest_resistance['price'] - nearest_support['price']
                zone_pct = (zone_range / current_price) * 100

                st.markdown(f"""
                <div style='background-color: #2196F3; color: white; padding: 10px;
                     border-radius: 5px; text-align: center;'>
                    <div style='font-size: 11px; opacity: 0.9;'>Trading Zone</div>
                    <div style='font-size: 16px; font-weight: bold;'>${zone_range:.2f}</div>
                    <div style='font-size: 10px; opacity: 0.8;'>{zone_pct:.1f}% range</div>
                </div>
                """, unsafe_allow_html=True)

        # ===== STEP 5: DETAILED LEVELS TABLE =====
        st.markdown("---")
        st.markdown("#### 📊 All Significant Levels")

        # Build table data
        table_data = []
        for level in sr_levels:
            # Status emoji
            if level['recent_break']:
                status = "🔓 Broken"
            elif level['recent_bounce']:
                status = "✅ Active"
            else:
                status = "⏸️ Historical"

            # Strength bar
            strength_pct = level['strength']
            if strength_pct >= 75:
                strength_display = "🟢🟢🟢 Strong"
            elif strength_pct >= 50:
                strength_display = "🟡🟡 Moderate"
            else:
                strength_display = "🔴 Weak"

            table_data.append({
                'Type': f"{'🟢' if level['type'] == 'Support' else '🔴'} {level['type']}",
                'Price': f"${level['price']:.2f}",
                'Distance': f"{level['distance_pct']:+.1f}%",
                'Touches': level['touches'],
                'Strength': strength_display,
                'Status': status
            })

        table_df = pd.DataFrame(table_data)
        display_dataframe_full_width(table_df, hide_index=True)

        # ===== STEP 6: TRADING GUIDANCE =====
        st.markdown("---")
        st.markdown("#### 💡 How to Use Support & Resistance")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Trading Strategies**
            - **Buy at support**, sell at resistance (range trading)
            - **Breakout**: Strong move through resistance = bullish
            - **Breakdown**: Strong move through support = bearish
            - **Bounce**: Price respects level = continuation

            **📊 Strength Indicators**
            - **Thick lines** = stronger levels (more touches)
            - **Green** = support below current price
            - **Red** = resistance above current price
            - **Grey/dotted** = recently broken levels
            """)

        with col2:
            st.markdown("""
            **⚠️ Important Notes**
            - Support becomes resistance after break (and vice versa)
            - Higher volume at level = stronger level
            - Multiple touches increase reliability
            - Recent bounces show level is still active

            **🎓 Pro Tips**
            - Wait for confirmation before trading breakouts
            - Use stop losses just beyond S/R levels
            - Strong levels often create "zones" not exact prices
            - Watch for false breakouts (test and reject)
            """)

        # Trading suggestion based on price position
        st.markdown("---")

        if supports and resistances:
            nearest_support_pct = abs(nearest_support['distance_pct'])
            nearest_resistance_pct = abs(nearest_resistance['distance_pct'])

            if nearest_support_pct < 2 and nearest_support['strength'] > 60:
                st.success(f"💡 **Trading Idea**: Price near strong support (${nearest_support['price']:.2f}). Watch for bounce or breakdown.")
            elif nearest_resistance_pct < 2 and nearest_resistance['strength'] > 60:
                st.warning(f"💡 **Trading Idea**: Price near strong resistance (${nearest_resistance['price']:.2f}). Watch for rejection or breakout.")
            elif nearest_support_pct < 5 and nearest_resistance_pct < 5:
                st.info(f"💡 **Trading Idea**: Price in middle of range (${nearest_support['price']:.2f} - ${nearest_resistance['price']:.2f}). Wait for direction.")
            else:
                st.info("💡 **Trading Idea**: Price between major levels. Monitor for approach to nearest S/R.")

    except Exception as e:
        st.error(f"Error calculating support/resistance: {str(e)}")
        st.info("Support/Resistance detection requires OHLCV data with at least 30+ bars.")


def render_divergence_scanner(price_data):
    """
    Scan for price-momentum divergences
    Detects bullish/bearish divergences between price and RSI/MACD
    """
    st.markdown("### ⚠️ Momentum Divergence Scanner")
    st.caption("Divergences signal potential reversals - when price and momentum disagree")

    try:
        df = price_data.copy()

        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calculate MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # ===== DIVERGENCE DETECTION ALGORITHM =====

        # Parameters
        lookback = 5  # Window for finding swing points
        min_bars_between = 10  # Minimum bars between swing points
        divergence_threshold = 0.02  # 2% price move required

        # Find swing highs and lows in PRICE
        price_swing_highs = []
        price_swing_lows = []

        for i in range(lookback, len(df) - lookback):
            # Price swing high
            is_high = True
            for j in range(1, lookback + 1):
                if df['High'].iloc[i] <= df['High'].iloc[i-j] or df['High'].iloc[i] <= df['High'].iloc[i+j]:
                    is_high = False
                    break
            if is_high:
                price_swing_highs.append({
                    'index': i,
                    'price': df['High'].iloc[i],
                    'rsi': df['RSI'].iloc[i],
                    'macd': df['MACD'].iloc[i],
                    'date': df.index[i]
                })

            # Price swing low
            is_low = True
            for j in range(1, lookback + 1):
                if df['Low'].iloc[i] >= df['Low'].iloc[i-j] or df['Low'].iloc[i] >= df['Low'].iloc[i+j]:
                    is_low = False
                    break
            if is_low:
                price_swing_lows.append({
                    'index': i,
                    'price': df['Low'].iloc[i],
                    'rsi': df['RSI'].iloc[i],
                    'macd': df['MACD'].iloc[i],
                    'date': df.index[i]
                })

        # Detect divergences
        divergences = []

        # BEARISH DIVERGENCE: Price makes higher high, but RSI/MACD makes lower high
        for i in range(len(price_swing_highs) - 1):
            current = price_swing_highs[i]
            for j in range(i + 1, len(price_swing_highs)):
                next_swing = price_swing_highs[j]

                # Check minimum bars between
                if next_swing['index'] - current['index'] < min_bars_between:
                    continue

                # Price higher high but indicator lower high
                price_higher = next_swing['price'] > current['price'] * (1 + divergence_threshold)
                rsi_lower = next_swing['rsi'] < current['rsi']
                macd_lower = next_swing['macd'] < current['macd']

                if price_higher and (rsi_lower or macd_lower):
                    indicator_type = []
                    if rsi_lower:
                        indicator_type.append('RSI')
                    if macd_lower:
                        indicator_type.append('MACD')

                    divergences.append({
                        'type': 'Bearish',
                        'signal': 'SELL',
                        'indicator': ' + '.join(indicator_type),
                        'start_idx': current['index'],
                        'end_idx': next_swing['index'],
                        'start_date': current['date'],
                        'end_date': next_swing['date'],
                        'start_price': current['price'],
                        'end_price': next_swing['price'],
                        'strength': 'Strong' if (rsi_lower and macd_lower) else 'Moderate'
                    })
                    break  # Found divergence, move to next swing point

        # BULLISH DIVERGENCE: Price makes lower low, but RSI/MACD makes higher low
        for i in range(len(price_swing_lows) - 1):
            current = price_swing_lows[i]
            for j in range(i + 1, len(price_swing_lows)):
                next_swing = price_swing_lows[j]

                # Check minimum bars between
                if next_swing['index'] - current['index'] < min_bars_between:
                    continue

                # Price lower low but indicator higher low
                price_lower = next_swing['price'] < current['price'] * (1 - divergence_threshold)
                rsi_higher = next_swing['rsi'] > current['rsi']
                macd_higher = next_swing['macd'] > current['macd']

                if price_lower and (rsi_higher or macd_higher):
                    indicator_type = []
                    if rsi_higher:
                        indicator_type.append('RSI')
                    if macd_higher:
                        indicator_type.append('MACD')

                    divergences.append({
                        'type': 'Bullish',
                        'signal': 'BUY',
                        'indicator': ' + '.join(indicator_type),
                        'start_idx': current['index'],
                        'end_idx': next_swing['index'],
                        'start_date': current['date'],
                        'end_date': next_swing['date'],
                        'start_price': current['price'],
                        'end_price': next_swing['price'],
                        'strength': 'Strong' if (rsi_higher and macd_higher) else 'Moderate'
                    })
                    break  # Found divergence, move to next swing point

        # Filter to most recent divergences (last 60 bars)
        recent_divergences = [d for d in divergences if d['end_idx'] >= len(df) - 60]

        # ===== VISUALIZATION =====

        if len(recent_divergences) == 0:
            st.info("✅ No divergences detected in the recent period. Market momentum and price are aligned.")

            # Still show the charts for educational purposes
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=('Price Action', 'RSI (14)', 'MACD')
            )

            # Price chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ), row=1, col=1)

            # RSI
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#2196F3', width=2)
            ), row=2, col=1)

            fig.add_hline(y=70, line=dict(color='red', dash='dash', width=1), row=2, col=1)
            fig.add_hline(y=30, line=dict(color='green', dash='dash', width=1), row=2, col=1)

            # MACD
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#FF6F00', width=2)
            ), row=3, col=1)

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD_Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#9C27B0', width=1)
            ), row=3, col=1)

            fig.update_layout(
                height=700,
                showlegend=True,
                hovermode='x unified',
                xaxis3_title="Date"
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

            st.markdown("#### 💡 What Are Divergences?")
            st.markdown("""
            **Divergences occur when price and momentum indicators disagree:**
            - **Bullish Divergence**: Price makes lower low, but RSI/MACD makes higher low → Reversal UP
            - **Bearish Divergence**: Price makes higher high, but RSI/MACD makes lower high → Reversal DOWN

            No divergences detected means the current trend has healthy momentum confirmation.
            """)

            return

        # Display divergence summary
        st.markdown(f"#### 🚨 {len(recent_divergences)} Divergence(s) Detected")

        col1, col2 = st.columns([3, 1])

        with col1:
            # Create multi-panel chart
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.5, 0.25, 0.25],
                subplot_titles=('Price Action with Divergences', 'RSI (14)', 'MACD')
            )

            # Price chart
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ), row=1, col=1)

            # Draw divergence lines on price chart
            for div in recent_divergences:
                color = '#F44336' if div['type'] == 'Bearish' else '#4CAF50'

                # Line connecting the two swing points
                fig.add_trace(go.Scatter(
                    x=[div['start_date'], div['end_date']],
                    y=[div['start_price'], div['end_price']],
                    mode='lines+markers+text',
                    name=f"{div['type']} Div",
                    line=dict(color=color, width=3, dash='dash'),
                    marker=dict(size=10, symbol='triangle-up' if div['type'] == 'Bullish' else 'triangle-down'),
                    text=['', f"{div['type']}"],
                    textposition='top center',
                    textfont=dict(size=10, color=color),
                    showlegend=False
                ), row=1, col=1)

            # RSI
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#2196F3', width=2)
            ), row=2, col=1)

            fig.add_hline(y=70, line=dict(color='red', dash='dash', width=1), row=2, col=1)
            fig.add_hline(y=30, line=dict(color='green', dash='dash', width=1), row=2, col=1)

            # Mark RSI swing points for divergences
            for div in recent_divergences:
                if 'RSI' in div['indicator']:
                    color = '#F44336' if div['type'] == 'Bearish' else '#4CAF50'
                    rsi_start = df['RSI'].iloc[div['start_idx']]
                    rsi_end = df['RSI'].iloc[div['end_idx']]

                    fig.add_trace(go.Scatter(
                        x=[div['start_date'], div['end_date']],
                        y=[rsi_start, rsi_end],
                        mode='lines+markers',
                        line=dict(color=color, width=2, dash='dot'),
                        marker=dict(size=8),
                        showlegend=False
                    ), row=2, col=1)

            # MACD
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#FF6F00', width=2)
            ), row=3, col=1)

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD_Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#9C27B0', width=1)
            ), row=3, col=1)

            # Mark MACD swing points for divergences
            for div in recent_divergences:
                if 'MACD' in div['indicator']:
                    color = '#F44336' if div['type'] == 'Bearish' else '#4CAF50'
                    macd_start = df['MACD'].iloc[div['start_idx']]
                    macd_end = df['MACD'].iloc[div['end_idx']]

                    fig.add_trace(go.Scatter(
                        x=[div['start_date'], div['end_date']],
                        y=[macd_start, macd_end],
                        mode='lines+markers',
                        line=dict(color=color, width=2, dash='dot'),
                        marker=dict(size=8),
                        showlegend=False
                    ), row=3, col=1)

            fig.update_layout(
                height=700,
                showlegend=True,
                hovermode='x unified',
                xaxis3_title="Date"
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Active Signals")

            # Show most recent divergence
            if recent_divergences:
                most_recent = recent_divergences[-1]

                signal_color = '#F44336' if most_recent['type'] == 'Bearish' else '#4CAF50'
                signal_emoji = '⚠️' if most_recent['type'] == 'Bearish' else '✅'

                st.markdown(f"""
                <div style='background-color: {signal_color}; color: white; padding: 15px;
                     border-radius: 10px; margin-bottom: 15px; text-align: center;'>
                    <div style='font-size: 40px;'>{signal_emoji}</div>
                    <div style='font-size: 20px; font-weight: bold;'>{most_recent['type']}</div>
                    <div style='font-size: 16px; margin-top: 5px;'>{most_recent['signal']} Signal</div>
                    <div style='font-size: 12px; margin-top: 10px; opacity: 0.9;'>{most_recent['indicator']}</div>
                    <div style='font-size: 12px; opacity: 0.9;'>{most_recent['strength']} Strength</div>
                </div>
                """, unsafe_allow_html=True)

                # Interpretation
                if most_recent['type'] == 'Bearish':
                    st.error("⚠️ Bearish divergence suggests weakening upward momentum. Consider taking profits or tightening stops.")
                else:
                    st.success("✅ Bullish divergence suggests reversal potential. Watch for confirmation before entering long positions.")

                # Time info
                bars_ago = len(df) - most_recent['end_idx'] - 1
                st.caption(f"Detected {bars_ago} bar(s) ago")

        # ===== DIVERGENCE TABLE =====
        st.markdown("---")
        st.markdown("#### 📊 All Recent Divergences")

        table_data = []
        for div in recent_divergences:
            bars_ago = len(df) - div['end_idx'] - 1

            table_data.append({
                'Type': f"{'🔴' if div['type'] == 'Bearish' else '🟢'} {div['type']}",
                'Signal': div['signal'],
                'Indicator': div['indicator'],
                'Strength': div['strength'],
                'Date': div['end_date'].strftime('%Y-%m-%d'),
                'Bars Ago': bars_ago,
                'Price Range': f"${div['start_price']:.2f} → ${div['end_price']:.2f}"
            })

        if table_data:
            table_df = pd.DataFrame(table_data)
            display_dataframe_full_width(table_df, hide_index=True)

        # ===== EDUCATIONAL GUIDE =====
        st.markdown("---")
        st.markdown("#### 💡 How to Trade Divergences")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🟢 Bullish Divergence**
            - **Setup**: Price makes lower low, indicator makes higher low
            - **Meaning**: Selling pressure weakening
            - **Action**: Look for reversal UP
            - **Entry**: Wait for confirmation (price bounce, MACD cross)
            - **Stop**: Below recent swing low

            **Best in**: Downtrends, oversold conditions
            """)

        with col2:
            st.markdown("""
            **🔴 Bearish Divergence**
            - **Setup**: Price makes higher high, indicator makes lower high
            - **Meaning**: Buying pressure weakening
            - **Action**: Look for reversal DOWN
            - **Entry**: Wait for confirmation (price rejection, MACD cross)
            - **Stop**: Above recent swing high

            **Best in**: Uptrends, overbought conditions
            """)

        st.markdown("---")
        st.markdown("""
        **⚠️ Important Notes:**
        - **Strong divergences** (both RSI + MACD) are more reliable
        - **Wait for confirmation** - divergences can persist in strong trends
        - **Best when combined with** support/resistance levels
        - **False signals** possible - use proper risk management
        - **Higher timeframes** = more reliable divergences
        """)

    except Exception as e:
        st.error(f"Error detecting divergences: {str(e)}")
        st.info("Divergence scanner requires OHLCV data with at least 50 bars for accurate detection.")


def render_timeframe_alignment(ticker):
    """
    Show trend alignment across multiple timeframes
    Helps identify if trends align across short/medium/long term
    """
    st.markdown("### 📈 Multi-Timeframe Trend Alignment")
    st.caption("See if trends agree across different timeframes - alignment = higher conviction")

    try:
        # Fetch multi-timeframe data with caching
        with st.spinner("Loading multi-timeframe data..."):
            mtf_data = fetch_multi_timeframe_data(ticker)

        if not mtf_data:
            st.error("Unable to fetch multi-timeframe data. Please try again.")
            return

        # Analyze trend for each timeframe
        timeframe_analysis = {}

        for tf_name, df in mtf_data.items():
            if len(df) < 50:
                continue

            # Calculate trend indicators
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=min(50, len(df)//2)).mean()
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

            current_price = df['Close'].iloc[-1]
            sma20 = df['SMA20'].iloc[-1]
            sma50 = df['SMA50'].iloc[-1]

            # Determine trend
            if pd.notna(sma20) and pd.notna(sma50):
                if current_price > sma20 > sma50:
                    trend = "Strong Bullish"
                    trend_score = 100
                    color = "#4CAF50"
                    emoji = "🟢🟢"
                elif current_price > sma20:
                    trend = "Bullish"
                    trend_score = 75
                    color = "#8BC34A"
                    emoji = "🟢"
                elif current_price < sma20 < sma50:
                    trend = "Strong Bearish"
                    trend_score = 0
                    color = "#F44336"
                    emoji = "🔴🔴"
                elif current_price < sma20:
                    trend = "Bearish"
                    trend_score = 25
                    color = "#FF5722"
                    emoji = "🔴"
                else:
                    trend = "Neutral"
                    trend_score = 50
                    color = "#FFC107"
                    emoji = "🟡"
            else:
                trend = "Insufficient Data"
                trend_score = 50
                color = "#9E9E9E"
                emoji = "⚪"

            # Calculate momentum (price vs SMA20)
            momentum_pct = ((current_price - sma20) / sma20 * 100) if pd.notna(sma20) else 0

            timeframe_analysis[tf_name] = {
                'trend': trend,
                'score': trend_score,
                'color': color,
                'emoji': emoji,
                'price': current_price,
                'sma20': sma20,
                'sma50': sma50,
                'momentum_pct': momentum_pct,
                'bars': len(df)
            }

        # ===== VISUALIZATION =====

        # Determine overall alignment
        scores = [ta['score'] for ta in timeframe_analysis.values()]
        avg_score = np.mean(scores)

        if all(s >= 75 for s in scores):
            alignment = "Perfect Bullish Alignment"
            alignment_color = "#4CAF50"
            alignment_emoji = "🎯"
            alignment_confidence = 100
        elif all(s <= 25 for s in scores):
            alignment = "Perfect Bearish Alignment"
            alignment_color = "#F44336"
            alignment_emoji = "🎯"
            alignment_confidence = 100
        elif std_score := np.std(scores) < 15:
            alignment = "Good Alignment"
            alignment_color = "#2196F3"
            alignment_emoji = "✓"
            alignment_confidence = 80
        else:
            alignment = "Mixed/Conflicting"
            alignment_color = "#FF9800"
            alignment_emoji = "⚠️"
            alignment_confidence = 40

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create timeline visualization
            timeframe_order = ['5m', '15m', '1h', '1d', '1wk']
            timeframe_labels = {
                '5m': '5 Minute',
                '15m': '15 Minute',
                '1h': '1 Hour',
                '1d': 'Daily',
                '1wk': 'Weekly'
            }

            fig = go.Figure()

            # Create horizontal bars showing trend direction
            y_positions = []
            colors_list = []
            scores_list = []
            labels_list = []

            for i, tf in enumerate(timeframe_order):
                if tf in timeframe_analysis:
                    ta = timeframe_analysis[tf]
                    y_positions.append(i)
                    colors_list.append(ta['color'])
                    scores_list.append(ta['score'])
                    labels_list.append(f"{ta['emoji']} {timeframe_labels[tf]}: {ta['trend']}")

            fig.add_trace(go.Bar(
                x=scores_list,
                y=labels_list,
                orientation='h',
                marker=dict(color=colors_list),
                text=[f"{s:.0f}" for s in scores_list],
                textposition='inside',
                hovertemplate='%{y}<br>Score: %{x:.0f}<extra></extra>'
            ))

            # Add center line
            fig.add_vline(x=50, line=dict(color='gray', dash='dash', width=2))

            fig.update_layout(
                title="Trend Strength Across Timeframes",
                xaxis_title="Trend Score (0=Bearish, 100=Bullish)",
                yaxis_title="",
                height=400,
                showlegend=False,
                xaxis=dict(range=[0, 100])
            )

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Alignment Status")

            st.markdown(f"""
            <div style='background-color: {alignment_color}; color: white; padding: 20px;
                 border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                <div style='font-size: 50px;'>{alignment_emoji}</div>
                <div style='font-size: 18px; font-weight: bold;'>{alignment}</div>
                <div style='font-size: 14px; margin-top: 10px; opacity: 0.9;'>Confidence: {alignment_confidence}%</div>
            </div>
            """, unsafe_allow_html=True)

            # Trading suggestion
            if alignment_confidence >= 80:
                if avg_score >= 75:
                    st.success("✅ High-probability long setup. All timeframes bullish.")
                elif avg_score <= 25:
                    st.error("⚠️ High-probability short setup. All timeframes bearish.")
            else:
                st.warning("⚠️ Mixed signals. Wait for timeframe alignment before entering.")

        # Detailed table
        st.markdown("---")
        st.markdown("#### 📊 Timeframe Details")

        table_data = []
        for tf in timeframe_order:
            if tf in timeframe_analysis:
                ta = timeframe_analysis[tf]
                table_data.append({
                    'Timeframe': f"{ta['emoji']} {timeframe_labels[tf]}",
                    'Trend': ta['trend'],
                    'Price': f"${ta['price']:.2f}",
                    'vs SMA20': f"{ta['momentum_pct']:+.2f}%",
                    'Score': f"{ta['score']:.0f}/100",
                    'Bars': ta['bars']
                })

        if table_data:
            df_table = pd.DataFrame(table_data)
            display_dataframe_full_width(df_table, hide_index=True)

        # Educational guide
        st.markdown("---")
        st.markdown("#### 💡 How to Use Multi-Timeframe Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Alignment Strategies**
            - **Perfect Alignment** (all green/red): Highest conviction trades
            - **Good Alignment**: Safe to trade in aligned direction
            - **Mixed**: Wait for clarity or trade smaller size
            - **Opposite**: Avoid - conflicting signals

            **⏰ Timeframe Priority**
            - **Weekly/Daily**: Defines overall trend (most important)
            - **1H/15m**: Entry/exit timing (medium-term)
            - **5m**: Precise entries (short-term noise)
            """)

        with col2:
            st.markdown("""
            **📈 Trading Rules**
            - Only trade WITH the higher timeframe trend
            - Use lower timeframes for entry timing
            - If Daily is bullish, only look for longs on 1H pullbacks
            - If all timeframes align, increase position size

            **⚠️ Warning Signs**
            - Lower timeframes opposite higher = potential reversal
            - Diverging alignment = trend exhaustion
            - Wait for realignment before new trades
            """)

        # Specific insights
        st.markdown("---")

        if '1d' in timeframe_analysis and '1h' in timeframe_analysis:
            daily_score = timeframe_analysis['1d']['score']
            hourly_score = timeframe_analysis['1h']['score']

            if abs(daily_score - hourly_score) > 40:
                st.warning(f"""
                ⚠️ **Divergence Alert**: Daily ({timeframe_analysis['1d']['trend']}) and 1H ({timeframe_analysis['1h']['trend']})
                trends are conflicting. This could signal:
                - Trend reversal in progress
                - Short-term pullback in longer trend
                - Wait for alignment before trading
                """)
            elif daily_score >= 75 and hourly_score >= 75:
                st.success("""
                ✅ **Strong Bullish Setup**: Both Daily and 1H trends are bullish.
                Look for pullbacks to support for long entries.
                """)
            elif daily_score <= 25 and hourly_score <= 25:
                st.error("""
                ⚠️ **Strong Bearish Setup**: Both Daily and 1H trends are bearish.
                Look for rallies to resistance for short entries.
                """)

    except Exception as e:
        st.error(f"Error analyzing multi-timeframe data: {str(e)}")
        st.info("Multi-timeframe alignment requires market hours data for intraday timeframes.")


def render_regime_detection(price_data):
    """
    Detect current market regime
    Classifies market as Trending, Ranging, or Volatile
    """
    st.markdown("### 🎚️ Market Regime Detection")
    st.caption("Identifies the current market condition to help choose the right trading strategy")

    try:
        df = price_data.copy()

        # Calculate indicators for regime detection
        # ATR for volatility
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100

        # ADX for trend strength
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr = true_range
        atr = tr.rolling(14).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10))
        minus_di = abs(100 * (minus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10)))
        # Prevent division by zero in DX calculation
        denominator = abs(plus_di + minus_di).replace(0, 1e-10)
        dx = (abs(plus_di - minus_di) / denominator) * 100
        df['ADX'] = dx.ewm(alpha=1/14).mean()

        # Bollinger Band Width for ranging detection
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['StdDev'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['SMA20'] + (df['StdDev'] * 2)
        df['BB_Lower'] = df['SMA20'] - (df['StdDev'] * 2)
        df['BB_Width'] = ((df['BB_Upper'] - df['BB_Lower']) / df['SMA20']) * 100

        # Price vs MA for trend direction
        df['SMA50'] = df['Close'].rolling(window=50).mean()

        # Get current values
        current_adx = df['ADX'].iloc[-1]
        current_atr_pct = df['ATR_Pct'].iloc[-1]
        current_bb_width = df['BB_Width'].iloc[-1]
        current_price = df['Close'].iloc[-1]
        current_sma20 = df['SMA20'].iloc[-1]
        current_sma50 = df['SMA50'].iloc[-1]

        # Historical averages
        avg_atr_pct = df['ATR_Pct'].tail(60).mean()
        avg_bb_width = df['BB_Width'].tail(60).mean()

        # ===== REGIME CLASSIFICATION =====

        regime = None
        regime_score = 0
        regime_color = None
        regime_emoji = None

        # Criteria for regime detection
        is_high_adx = current_adx > 25
        is_low_adx = current_adx < 20
        is_high_volatility = current_atr_pct > avg_atr_pct * 1.2
        is_low_volatility = current_atr_pct < avg_atr_pct * 0.8
        is_narrow_bb = current_bb_width < avg_bb_width * 0.8
        is_wide_bb = current_bb_width > avg_bb_width * 1.2

        # Price position
        above_sma20 = current_price > current_sma20
        above_sma50 = current_price > current_sma50 if pd.notna(current_sma50) else False

        # Regime Classification Logic
        if is_high_adx and not is_high_volatility:
            # Strong trend, normal volatility
            regime = "Strong Trend"
            regime_emoji = "📈" if above_sma50 else "📉"
            regime_color = "#4CAF50" if above_sma50 else "#F44336"
            regime_score = min(100, current_adx * 2)
            best_strategy = "Trend Following"
            description = f"Clear {'uptrend' if above_sma50 else 'downtrend'} with conviction. Trade WITH the trend."

        elif is_high_volatility and is_wide_bb:
            # High volatility, wide bands
            regime = "High Volatility"
            regime_emoji = "⚡"
            regime_color = "#FF9800"
            regime_score = min(100, (current_atr_pct / avg_atr_pct) * 50)
            best_strategy = "Wide Stops / Options"
            description = "Expect large price swings. Use wider stops or reduce position size."

        elif is_low_adx and is_narrow_bb:
            # Ranging market
            regime = "Range-Bound"
            regime_emoji = "↔️"
            regime_color = "#2196F3"
            regime_score = max(0, 100 - current_adx * 3)
            best_strategy = "Mean Reversion"
            description = "Price oscillating in a range. Trade support/resistance bounces."

        elif is_low_volatility:
            # Quiet market
            regime = "Low Volatility"
            regime_emoji = "😴"
            regime_color = "#9E9E9E"
            regime_score = max(0, 100 - (current_atr_pct / avg_atr_pct) * 50)
            best_strategy = "Wait / Tight Stops"
            description = "Market sleeping. Small moves, consider waiting for breakout."

        else:
            # Transitional / Mixed
            regime = "Transitional"
            regime_emoji = "🔄"
            regime_color = "#9C27B0"
            regime_score = 50
            best_strategy = "Wait for Clarity"
            description = "Market in transition. Mixed signals - wait for clear regime."

        # ===== VISUALIZATION =====

        col1, col2 = st.columns([3, 1])

        with col1:
            # Multi-panel chart showing regime indicators
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.4, 0.2, 0.2, 0.2],
                subplot_titles=('Price with Bollinger Bands', 'ADX (Trend Strength)', 'ATR % (Volatility)', 'Regime Timeline')
            )

            # Price with Bollinger Bands
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Upper'],
                line=dict(color='rgba(128,128,128,0.5)', width=1),
                name='BB Upper',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_Lower'],
                line=dict(color='rgba(128,128,128,0.5)', width=1),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                name='BB Lower',
                showlegend=False
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA20'],
                line=dict(color='#2196F3', width=2),
                name='SMA20',
                showlegend=False
            ), row=1, col=1)

            # ADX
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ADX'],
                line=dict(color='#FF6F00', width=2),
                name='ADX',
                showlegend=False
            ), row=2, col=1)

            fig.add_hline(y=25, line=dict(color='green', dash='dash', width=1), row=2, col=1)
            fig.add_hline(y=20, line=dict(color='red', dash='dash', width=1), row=2, col=1)

            # ATR %
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ATR_Pct'],
                line=dict(color='#9C27B0', width=2),
                fill='tozeroy',
                fillcolor='rgba(156,39,176,0.2)',
                name='ATR %',
                showlegend=False
            ), row=3, col=1)

            # Regime timeline (simplified - color coded bars)
            regime_colors = []
            for i in range(len(df)):
                adx_val = df['ADX'].iloc[i]
                atr_val = df['ATR_Pct'].iloc[i] if pd.notna(df['ATR_Pct'].iloc[i]) else avg_atr_pct
                bb_val = df['BB_Width'].iloc[i] if pd.notna(df['BB_Width'].iloc[i]) else avg_bb_width

                if adx_val > 25 and atr_val < avg_atr_pct * 1.2:
                    regime_colors.append(1)  # Trending
                elif atr_val > avg_atr_pct * 1.2:
                    regime_colors.append(2)  # Volatile
                elif adx_val < 20 and bb_val < avg_bb_width * 0.8:
                    regime_colors.append(3)  # Ranging
                else:
                    regime_colors.append(0)  # Transitional

            fig.add_trace(go.Scatter(
                x=df.index,
                y=regime_colors,
                mode='lines',
                fill='tozeroy',
                line=dict(width=0),
                fillcolor='rgba(76,175,80,0.3)',
                name='Regime',
                showlegend=False
            ), row=4, col=1)

            fig.update_layout(
                height=800,
                showlegend=False,
                hovermode='x unified',
                xaxis4_title="Date"
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Current Regime")

            st.markdown(f"""
            <div style='background-color: {regime_color}; color: white; padding: 20px;
                 border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                <div style='font-size: 50px;'>{regime_emoji}</div>
                <div style='font-size: 22px; font-weight: bold;'>{regime}</div>
                <div style='font-size: 14px; margin-top: 10px; opacity: 0.9;'>Confidence: {regime_score:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Best Strategy:**")
            st.info(best_strategy)

            st.markdown(f"**Description:**")
            st.caption(description)

        # Metrics
        st.markdown("---")
        st.markdown("#### 📊 Regime Indicators")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "ADX",
                f"{current_adx:.1f}",
                f"{'Strong' if current_adx > 25 else 'Weak'} Trend"
            )

        with col2:
            atr_vs_avg = ((current_atr_pct / avg_atr_pct) - 1) * 100
            st.metric(
                "ATR %",
                f"{current_atr_pct:.2f}%",
                f"{atr_vs_avg:+.1f}% vs avg"
            )

        with col3:
            bb_vs_avg = ((current_bb_width / avg_bb_width) - 1) * 100
            st.metric(
                "BB Width %",
                f"{current_bb_width:.2f}%",
                f"{bb_vs_avg:+.1f}% vs avg"
            )

        with col4:
            trend_direction = "Bullish" if above_sma50 else "Bearish"
            st.metric(
                "Trend",
                trend_direction,
                f"Price {'>' if above_sma50 else '<'} SMA50"
            )

        # Strategy guide
        st.markdown("---")
        st.markdown("#### 💡 Trading Strategies by Regime")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **📈 Strong Trend**
            - **Strategy**: Trend following
            - **Entry**: Pullbacks to moving averages
            - **Exit**: Trailing stops
            - **Avoid**: Counter-trend trades

            **↔️ Range-Bound**
            - **Strategy**: Mean reversion
            - **Entry**: Support/resistance bounces
            - **Exit**: Take profits at opposite end
            - **Avoid**: Breakout trades (usually fail)
            """)

        with col2:
            st.markdown("""
            **⚡ High Volatility**
            - **Strategy**: Options or reduce size
            - **Entry**: Wait for consolidation
            - **Exit**: Wider stops (2-3x ATR)
            - **Avoid**: Over-leveraging

            **🔄 Transitional**
            - **Strategy**: Wait for clarity
            - **Entry**: After regime confirms
            - **Exit**: Quick stops
            - **Avoid**: Large positions
            """)

    except Exception as e:
        st.error(f"Error detecting market regime: {str(e)}")
        st.info("Regime detection requires OHLCV data with at least 60 bars.")


def render_relative_strength(ticker, price_data):
    """
    Compare stock performance vs SPY and sector ETF
    Shows if stock is outperforming or underperforming the market
    """
    st.markdown("### 🌍 Relative Strength Analysis")
    st.caption("Compare performance vs market (SPY) and sector - identify leaders and laggards")

    try:
        # Fetch comparison data with caching
        with st.spinner("Loading market comparison data..."):
            spy_data = fetch_spy_data(period="6mo")
            sector_etf_ticker = get_sector_etf(ticker)
            sector_data = fetch_sector_etf_data(sector_etf_ticker, period="6mo")

        if spy_data is None:
            st.error("Unable to fetch SPY data. Please try again.")
            return

        # Normalize price data to start at 100 for comparison
        stock_df = price_data.copy()

        # Align dates (use intersection of available dates)
        common_dates = stock_df.index.intersection(spy_data.index)

        if len(common_dates) < 20:
            st.warning("Insufficient overlapping data for comparison. Need at least 20 common trading days.")
            return

        stock_aligned = stock_df.loc[common_dates]['Close']
        spy_aligned = spy_data.loc[common_dates]['Close']

        # Normalize to 100
        stock_normalized = (stock_aligned / stock_aligned.iloc[0]) * 100
        spy_normalized = (spy_aligned / spy_aligned.iloc[0]) * 100

        # Calculate relative strength ratio
        rs_ratio = stock_normalized / spy_normalized * 100

        # Sector comparison (if available)
        sector_normalized = None
        rs_vs_sector = None

        if sector_data is not None:
            sector_common_dates = common_dates.intersection(sector_data.index)
            if len(sector_common_dates) >= 20:
                sector_aligned = sector_data.loc[sector_common_dates]['Close']
                sector_normalized = (sector_aligned / sector_aligned.iloc[0]) * 100
                rs_vs_sector = (stock_aligned.loc[sector_common_dates] / sector_aligned) * 100

        # Calculate performance metrics
        periods = {
            '1W': 5,
            '1M': 21,
            '3M': 63,
            '6M': 126
        }

        performance_comparison = {}

        for period_name, days in periods.items():
            if len(stock_normalized) >= days:
                stock_return = ((stock_normalized.iloc[-1] / stock_normalized.iloc[-days]) - 1) * 100
                spy_return = ((spy_normalized.iloc[-1] / spy_normalized.iloc[-days]) - 1) * 100
                outperformance = stock_return - spy_return

                performance_comparison[period_name] = {
                    'stock': stock_return,
                    'spy': spy_return,
                    'diff': outperformance
                }

                if sector_normalized is not None and len(sector_normalized) >= days:
                    sector_return = ((sector_normalized.iloc[-1] / sector_normalized.iloc[-days]) - 1) * 100
                    sector_outperformance = stock_return - sector_return
                    performance_comparison[period_name]['sector'] = sector_return
                    performance_comparison[period_name]['sector_diff'] = sector_outperformance

        # ===== VISUALIZATION =====

        # Determine overall relative strength
        current_rs = rs_ratio.iloc[-1]

        if current_rs > 105:
            rs_status = "Strong Outperformance"
            rs_color = "#4CAF50"
            rs_emoji = "🚀"
        elif current_rs > 100:
            rs_status = "Moderate Outperformance"
            rs_color = "#8BC34A"
            rs_emoji = "📈"
        elif current_rs > 95:
            rs_status = "In-Line with Market"
            rs_color = "#FFC107"
            rs_emoji = "➡️"
        elif current_rs > 90:
            rs_status = "Moderate Underperformance"
            rs_color = "#FF9800"
            rs_emoji = "📉"
        else:
            rs_status = "Strong Underperformance"
            rs_color = "#F44336"
            rs_emoji = "⚠️"

        col1, col2 = st.columns([3, 1])

        with col1:
            # Create performance comparison chart
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3],
                subplot_titles=('Normalized Performance Comparison', 'Relative Strength Ratio')
            )

            # Performance lines
            fig.add_trace(go.Scatter(
                x=stock_normalized.index,
                y=stock_normalized,
                mode='lines',
                name=ticker,
                line=dict(color='#2196F3', width=3)
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=spy_normalized.index,
                y=spy_normalized,
                mode='lines',
                name='SPY (Market)',
                line=dict(color='#FF9800', width=2)
            ), row=1, col=1)

            if sector_normalized is not None:
                fig.add_trace(go.Scatter(
                    x=sector_normalized.index,
                    y=sector_normalized,
                    mode='lines',
                    name=f'{sector_etf_ticker} (Sector)',
                    line=dict(color='#9C27B0', width=2, dash='dash')
                ), row=1, col=1)

            # Baseline at 100
            fig.add_hline(y=100, line=dict(color='gray', dash='dot', width=1), row=1, col=1)

            # Relative Strength Ratio
            fig.add_trace(go.Scatter(
                x=rs_ratio.index,
                y=rs_ratio,
                mode='lines',
                name='RS Ratio',
                line=dict(color='#4CAF50', width=2),
                fill='tonexty',
                fillcolor='rgba(76,175,80,0.1)'
            ), row=2, col=1)

            fig.add_hline(y=100, line=dict(color='red', dash='dash', width=2), row=2, col=1)

            fig.update_layout(
                height=600,
                showlegend=True,
                hovermode='x unified',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )

            fig.update_yaxes(title_text="Indexed Price (Base=100)", row=1, col=1)
            fig.update_yaxes(title_text="RS Ratio", row=2, col=1)
            fig.update_xaxes(title_text="Date", row=2, col=1)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 RS Status")

            st.markdown(f"""
            <div style='background-color: {rs_color}; color: white; padding: 20px;
                 border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                <div style='font-size: 50px;'>{rs_emoji}</div>
                <div style='font-size: 16px; font-weight: bold;'>{rs_status}</div>
                <div style='font-size: 14px; margin-top: 10px; opacity: 0.9;'>RS: {current_rs:.1f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Interpretation
            if current_rs > 105:
                st.success("✅ Stock is a market leader. Strong buy candidate.")
            elif current_rs > 100:
                st.info("✓ Stock outperforming. Positive momentum.")
            elif current_rs > 95:
                st.warning("➡️ Stock moving with market. Neutral.")
            else:
                st.error("⚠️ Stock underperforming. Avoid or wait for improvement.")

            st.caption(f"Sector: {sector_etf_ticker}")

        # Performance table
        st.markdown("---")
        st.markdown("#### 📊 Performance Comparison")

        table_data = []
        for period, metrics in performance_comparison.items():
            row = {
                'Period': period,
                f'{ticker}': f"{metrics['stock']:+.2f}%",
                'SPY': f"{metrics['spy']:+.2f}%",
                'vs SPY': f"{metrics['diff']:+.2f}%"
            }

            if 'sector' in metrics:
                row[f'{sector_etf_ticker}'] = f"{metrics['sector']:+.2f}%"
                row[f'vs {sector_etf_ticker}'] = f"{metrics['sector_diff']:+.2f}%"

            table_data.append(row)

        if table_data:
            perf_df = pd.DataFrame(table_data)
            display_dataframe_full_width(perf_df, hide_index=True)

        # Trend analysis
        st.markdown("---")
        st.markdown("#### 📈 Relative Strength Trend")

        # Calculate RS trend (is it improving or deteriorating?)
        rs_20d_ago = rs_ratio.iloc[-20] if len(rs_ratio) >= 20 else rs_ratio.iloc[0]
        rs_change = current_rs - rs_20d_ago

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Current RS",
                f"{current_rs:.1f}",
                help="Relative Strength vs SPY (100 = equal performance)"
            )

        with col2:
            st.metric(
                "20-Day Change",
                f"{rs_20d_ago:.1f}",
                f"{rs_change:+.1f}",
                delta_color="normal"
            )

        with col3:
            trend = "Improving" if rs_change > 2 else ("Deteriorating" if rs_change < -2 else "Stable")
            trend_emoji = "📈" if rs_change > 2 else ("📉" if rs_change < -2 else "➡️")
            st.metric(
                "RS Trend",
                f"{trend_emoji} {trend}",
                help="20-day RS trend direction"
            )

        # Educational guide
        st.markdown("---")
        st.markdown("#### 💡 How to Use Relative Strength")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Interpretation**
            - **RS > 100**: Stock outperforming market (leader)
            - **RS = 100**: Stock moving with market
            - **RS < 100**: Stock underperforming market (laggard)
            - **Rising RS**: Gaining momentum vs market
            - **Falling RS**: Losing momentum vs market

            **📈 Trading Applications**
            - Buy leaders (RS > 100) in bull markets
            - Avoid laggards (RS < 100) in bull markets
            - Rotate into improving RS stocks
            - Exit when RS starts deteriorating
            """)

        with col2:
            st.markdown("""
            **⚠️ Important Notes**
            - **Sector matters**: Compare to sector ETF too
            - **Market direction**: RS works best in trending markets
            - **Momentum**: Rising RS = institutional buying
            - **Mean reversion**: Extreme RS can reverse

            **💡 Pro Tips**
            - **Leaders stay leaders**: High RS stocks tend to continue outperforming
            - **Sector rotation**: Watch for sector RS changes
            - **Combine with technicals**: Best when RS + chart both strong
            - **Risk-off**: RS fails in market crashes (all correlate to 1)
            """)

        # Specific insights
        st.markdown("---")

        if '1M' in performance_comparison and '3M' in performance_comparison:
            m1_diff = performance_comparison['1M']['diff']
            m3_diff = performance_comparison['3M']['diff']

            if m1_diff > 5 and m3_diff > 5:
                st.success("""
                ✅ **Consistent Outperformance**: Stock has beaten SPY over both 1M and 3M periods.
                This shows sustained relative strength - a positive sign for continuation.
                """)
            elif m1_diff > 0 and m3_diff < 0:
                st.info("""
                📈 **Recent Improvement**: Stock underperformed over 3M but is now outperforming over 1M.
                Potential momentum shift - monitor for continued improvement.
                """)
            elif m1_diff < 0 and m3_diff > 0:
                st.warning("""
                ⚠️ **Losing Momentum**: Stock outperformed over 3M but now underperforming over 1M.
                RS deteriorating - consider taking profits or tightening stops.
                """)
            elif m1_diff < -5 and m3_diff < -5:
                st.error("""
                ⛔ **Persistent Weakness**: Stock has underperformed SPY over both 1M and 3M periods.
                Avoid new positions until RS improves.
                """)

    except Exception as e:
        st.error(f"Error calculating relative strength: {str(e)}")
        st.info("Relative strength analysis requires market data for SPY comparison.")


def render_atr_projection(price_data):
    """
    Project expected price range based on ATR
    Shows volatility-based price targets and expected ranges
    """
    st.markdown("### 📉 ATR Volatility Projection")
    st.caption("Expected price range based on historical volatility - helps set targets and stops")

    try:
        df = price_data.copy()

        # Calculate ATR
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()

        # Calculate ATR bands (similar to Bollinger Bands but using ATR)
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['ATR_Upper_1x'] = df['SMA20'] + df['ATR']
        df['ATR_Lower_1x'] = df['SMA20'] - df['ATR']
        df['ATR_Upper_2x'] = df['SMA20'] + (df['ATR'] * 2)
        df['ATR_Lower_2x'] = df['SMA20'] - (df['ATR'] * 2)
        df['ATR_Upper_3x'] = df['SMA20'] + (df['ATR'] * 3)
        df['ATR_Lower_3x'] = df['SMA20'] - (df['ATR'] * 3)

        # Current values
        current_price = df['Close'].iloc[-1]
        current_atr = df['ATR'].iloc[-1]
        current_sma = df['SMA20'].iloc[-1]

        # Project future price targets based on ATR
        # Assuming 1-day holding period (adjust multiplier for different timeframes)
        target_1x_up = current_price + current_atr
        target_1x_down = current_price - current_atr
        target_2x_up = current_price + (current_atr * 2)
        target_2x_down = current_price - (current_atr * 2)
        target_3x_up = current_price + (current_atr * 3)
        target_3x_down = current_price - (current_atr * 3)

        # Calculate ATR as percentage of price
        atr_pct = (current_atr / current_price) * 100

        # Historical ATR analysis
        avg_atr = df['ATR'].tail(60).mean()
        atr_vs_avg = ((current_atr / avg_atr) - 1) * 100

        # ===== VISUALIZATION =====

        col1, col2 = st.columns([3, 1])

        with col1:
            # Price chart with ATR bands
            fig = go.Figure()

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ))

            # SMA20 centerline
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA20'],
                line=dict(color='#2196F3', width=2),
                name='SMA20'
            ))

            # ATR Bands - 1x
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ATR_Upper_1x'],
                line=dict(color='rgba(76,175,80,0.5)', width=1, dash='dash'),
                name='ATR +1x',
                showlegend=True
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ATR_Lower_1x'],
                line=dict(color='rgba(244,67,54,0.5)', width=1, dash='dash'),
                name='ATR -1x',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=True
            ))

            # ATR Bands - 2x
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ATR_Upper_2x'],
                line=dict(color='rgba(255,152,0,0.4)', width=1, dash='dot'),
                name='ATR +2x'
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['ATR_Lower_2x'],
                line=dict(color='rgba(255,152,0,0.4)', width=1, dash='dot'),
                name='ATR -2x'
            ))

            # Current price projection lines
            last_date = df.index[-1]

            # Project forward (estimate 5 trading days)
            future_dates = pd.date_range(start=last_date, periods=6, freq='D')[1:]

            # Draw projection fan
            for mult, color, name in [(1, '#4CAF50', '1x ATR'), (2, '#FF9800', '2x ATR'), (3, '#F44336', '3x ATR')]:
                # Upside projection
                fig.add_trace(go.Scatter(
                    x=[last_date, future_dates[-1]],
                    y=[current_price, current_price + (current_atr * mult)],
                    mode='lines',
                    line=dict(color=color, width=2, dash='dash'),
                    name=f'Target +{name}',
                    opacity=0.6
                ))

                # Downside projection
                fig.add_trace(go.Scatter(
                    x=[last_date, future_dates[-1]],
                    y=[current_price, current_price - (current_atr * mult)],
                    mode='lines',
                    line=dict(color=color, width=2, dash='dash'),
                    name=f'Target -{name}',
                    opacity=0.6,
                    showlegend=False
                ))

            fig.update_layout(
                title="Price Chart with ATR Projection Bands",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=600,
                hovermode='x unified',
                showlegend=True,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )

            fig.update_xaxes(rangeslider_visible=False)

            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Volatility Stats")

            st.metric(
                "Current ATR",
                f"${current_atr:.2f}",
                f"{atr_pct:.2f}%"
            )

            st.metric(
                "vs 60-day Avg",
                f"${avg_atr:.2f}",
                f"{atr_vs_avg:+.1f}%"
            )

            # Volatility assessment
            if atr_vs_avg > 20:
                st.error("⚠️ High volatility - use wider stops")
            elif atr_vs_avg < -20:
                st.info("😴 Low volatility - tighten stops")
            else:
                st.success("✅ Normal volatility range")

        # Price targets table
        st.markdown("---")
        st.markdown("#### 🎯 Expected Price Targets (Based on Current ATR)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Upside Targets**")

            targets_up = [
                {"Level": "Conservative (1x ATR)", "Price": f"${target_1x_up:.2f}", "Move": f"+{atr_pct:.1f}%", "Probability": "68%"},
                {"Level": "Moderate (2x ATR)", "Price": f"${target_2x_up:.2f}", "Move": f"+{atr_pct*2:.1f}%", "Probability": "95%"},
                {"Level": "Aggressive (3x ATR)", "Price": f"${target_3x_up:.2f}", "Move": f"+{atr_pct*3:.1f}%", "Probability": "99.7%"}
            ]

            df_targets_up = pd.DataFrame(targets_up)
            display_dataframe_full_width(df_targets_up, hide_index=True)

        with col2:
            st.markdown("**Downside Targets (Stop Loss)**")

            targets_down = [
                {"Level": "Tight Stop (1x ATR)", "Price": f"${target_1x_down:.2f}", "Move": f"-{atr_pct:.1f}%", "Probability": "68%"},
                {"Level": "Standard Stop (2x ATR)", "Price": f"${target_2x_down:.2f}", "Move": f"-{atr_pct*2:.1f}%", "Probability": "95%"},
                {"Level": "Wide Stop (3x ATR)", "Price": f"${target_3x_down:.2f}", "Move": f"-{atr_pct*3:.1f}%", "Probability": "99.7%"}
            ]

            df_targets_down = pd.DataFrame(targets_down)
            display_dataframe_full_width(df_targets_down, hide_index=True)

        st.caption("*Probabilities assume normal distribution - actual market moves may differ")

        # Trading guide
        st.markdown("---")
        st.markdown("#### 💡 How to Use ATR Projections")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Setting Profit Targets**
            - **Day Trading**: Use 1-2x ATR
            - **Swing Trading**: Use 2-3x ATR
            - **Position Trading**: Use 3-5x ATR
            - **Realistic Expectations**: 1x ATR move in one day is normal

            **📊 Interpreting ATR Bands**
            - Price at upper band → Overbought (short-term)
            - Price at lower band → Oversold (short-term)
            - Price between bands → Normal trading
            - Breakout above 2x → Strong momentum
            """)

        with col2:
            st.markdown("""
            **🛡️ Setting Stop Losses**
            - **Tight Stops**: 1x ATR (frequent stops)
            - **Standard Stops**: 2x ATR (recommended)
            - **Wide Stops**: 3x ATR (swing trades)
            - **Never use** < 0.5x ATR (noise stops you out)

            **⚡ Volatility Context**
            - **High ATR** → Bigger moves, wider stops needed
            - **Low ATR** → Smaller moves, tighter stops OK
            - **Expanding ATR** → Breakout potential
            - **Contracting ATR** → Consolidation, low conviction
            """)

        # Risk/Reward calculator
        st.markdown("---")
        st.markdown("#### 📐 Risk/Reward Ratios")

        risk_1x = abs(current_price - target_1x_down)
        reward_scenarios = [
            {"Target": "1x ATR Up", "Risk": f"${risk_1x:.2f}", "Reward": f"${current_atr:.2f}", "R:R Ratio": "1:1"},
            {"Target": "2x ATR Up", "Risk": f"${risk_1x:.2f}", "Reward": f"${current_atr*2:.2f}", "R:R Ratio": "1:2"},
            {"Target": "3x ATR Up", "Risk": f"${risk_1x:.2f}", "Reward": f"${current_atr*3:.2f}", "R:R Ratio": "1:3"}
        ]

        df_rr = pd.DataFrame(risk_scenarios)
        display_dataframe_full_width(df_rr, hide_index=True)

        st.caption("*Assuming 1x ATR stop loss. Aim for minimum 1:2 risk/reward ratio.")

    except Exception as e:
        st.error(f"Error calculating ATR projection: {str(e)}")
        st.info("ATR projection requires OHLCV data with at least 20 bars.")


def render_correlation_matrix(ticker, price_data):
    """
    Show correlation between price, volume, and indicators
    Helps identify which indicators move together or diverge
    """
    st.markdown("### 🔢 Correlation Matrix")
    st.caption("Heatmap showing how indicators relate to each other and to price")

    try:
        df = price_data.copy()

        # Calculate all indicators
        # Price-based
        df['Returns'] = df['Close'].pct_change()
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()

        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        # Prevent division by zero: replace 0 with small number
        rs = gain / loss.replace(0, 1e-10)
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # Bollinger Bands
        df['BB_Width'] = ((df['Close'].rolling(20).std() * 2) / df['SMA20']) * 100

        # ATR
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100

        # Volume
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

        # ADX
        plus_dm = df['High'].diff()
        minus_dm = df['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        atr = true_range.rolling(14).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10))
        minus_di = abs(100 * (minus_dm.ewm(alpha=1/14).mean() / atr.replace(0, 1e-10)))
        # Prevent division by zero in DX calculation
        denominator = abs(plus_di + minus_di).replace(0, 1e-10)
        dx = (abs(plus_di - minus_di) / denominator) * 100
        df['ADX'] = dx.ewm(alpha=1/14).mean()

        # Select columns for correlation
        corr_columns = [
            'Close', 'Returns', 'Volume_Ratio',
            'RSI', 'MACD_Hist', 'BB_Width', 'ATR_Pct', 'ADX'
        ]

        # Calculate correlation matrix
        corr_df = df[corr_columns].dropna()
        correlation_matrix = corr_df.corr()

        # ===== VISUALIZATION =====

        col1, col2 = st.columns([2, 1])

        with col1:
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale=[
                    [0, '#F44336'],      # Strong negative - red
                    [0.25, '#FF9800'],   # Weak negative - orange
                    [0.5, '#FFF9C4'],    # No correlation - yellow
                    [0.75, '#C8E6C9'],   # Weak positive - light green
                    [1, '#4CAF50']       # Strong positive - green
                ],
                zmid=0,
                zmin=-1,
                zmax=1,
                text=correlation_matrix.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(
                    title="Correlation",
                    titleside="right",
                    tickmode="linear",
                    tick0=-1,
                    dtick=0.5
                )
            ))

            fig.update_layout(
                title="Indicator Correlation Heatmap",
                xaxis_title="",
                yaxis_title="",
                height=600,
                width=700
            )

            from app_utils import plotly_full_width
            plotly_full_width(fig)

        with col2:
            st.markdown("#### 🎯 Key Insights")

            # Find strongest correlations (excluding diagonal)
            corr_flat = correlation_matrix.values.copy()
            np.fill_diagonal(corr_flat, 0)  # Remove self-correlation

            # Find strongest positive correlation
            max_idx = np.unravel_index(np.argmax(corr_flat), corr_flat.shape)
            max_corr = corr_flat[max_idx]
            max_pair = f"{correlation_matrix.columns[max_idx[0]]} ↔ {correlation_matrix.columns[max_idx[1]]}"

            # Find strongest negative correlation
            min_idx = np.unravel_index(np.argmin(corr_flat), corr_flat.shape)
            min_corr = corr_flat[min_idx]
            min_pair = f"{correlation_matrix.columns[min_idx[0]]} ↔ {correlation_matrix.columns[min_idx[1]]}"

            st.markdown(f"""
            <div style='background-color: #4CAF50; color: white; padding: 15px;
                 border-radius: 10px; margin-bottom: 15px;'>
                <div style='font-size: 12px; opacity: 0.9;'>Strongest Positive</div>
                <div style='font-size: 16px; font-weight: bold;'>{max_pair}</div>
                <div style='font-size: 20px; margin-top: 5px;'>{max_corr:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            if min_corr < -0.3:
                st.markdown(f"""
                <div style='background-color: #F44336; color: white; padding: 15px;
                     border-radius: 10px;'>
                    <div style='font-size: 12px; opacity: 0.9;'>Strongest Negative</div>
                    <div style='font-size: 16px; font-weight: bold;'>{min_pair}</div>
                    <div style='font-size: 20px; margin-top: 5px;'>{min_corr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Correlation with Returns
            returns_corr = correlation_matrix.loc['Returns'].drop('Returns').sort_values(ascending=False)

            st.markdown("**Top Predictors of Returns:**")

            for i, (indicator, corr_val) in enumerate(returns_corr.head(3).items()):
                emoji = '🟢' if corr_val > 0 else '🔴'
                st.caption(f"{emoji} {indicator}: {corr_val:.2f}")

        # Detailed correlation table
        st.markdown("---")
        st.markdown("#### 📊 Detailed Correlation Table")

        # Show top correlations
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                pair_name = f"{correlation_matrix.columns[i]} ↔ {correlation_matrix.columns[j]}"
                corr_value = correlation_matrix.iloc[i, j]

                if abs(corr_value) > 0.3:  # Only show significant correlations
                    corr_pairs.append({
                        'Pair': pair_name,
                        'Correlation': f"{corr_value:.2f}",
                        'Strength': 'Strong' if abs(corr_value) > 0.7 else 'Moderate',
                        'Direction': 'Positive ↗' if corr_value > 0 else 'Negative ↘'
                    })

        if corr_pairs:
            corr_df_table = pd.DataFrame(corr_pairs).sort_values(
                'Correlation', key=lambda x: abs(x.astype(float)), ascending=False
            )
            from app_utils import display_dataframe_full_width
            display_dataframe_full_width(corr_df_table, hide_index=True)
        else:
            st.info("No significant correlations detected (threshold: |0.3|)")

        # Educational guide
        st.markdown("---")
        st.markdown("#### 💡 Interpreting Correlations")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **📊 Correlation Strength**
            - **0.7 to 1.0**: Strong positive (move together)
            - **0.3 to 0.7**: Moderate positive
            - **-0.3 to 0.3**: Weak/no correlation
            - **-0.7 to -0.3**: Moderate negative
            - **-1.0 to -0.7**: Strong negative (move opposite)

            **🔍 What to Look For**
            - **Redundant indicators**: High correlation (>0.8)
            - **Divergences**: Normally correlated indicators diverging
            - **Leading indicators**: What correlates with future returns
            """)

        with col2:
            st.markdown("""
            **⚠️ Important Notes**
            - **Correlation ≠ Causation**: Indicators moving together doesn't mean one causes the other
            - **Time Period**: Correlations change over time
            - **Non-Linear**: Some relationships aren't captured
            - **Lag Effects**: Some indicators lag others

            **💡 Trading Applications**
            - Avoid redundant indicators (pick one from highly correlated group)
            - Watch for breakdown in normal correlations (regime change)
            - Use uncorrelated indicators for confirmation
            """)

        # Specific insights
        st.markdown("---")
        st.markdown("#### 🎓 Indicator Insights")

        col1, col2 = st.columns(2)

        with col1:
            rsi_macd_corr = correlation_matrix.loc['RSI', 'MACD_Hist']
            st.metric(
                "RSI ↔ MACD",
                f"{rsi_macd_corr:.2f}",
                "Both measure momentum"
            )

            vol_atr_corr = correlation_matrix.loc['Volume_Ratio', 'ATR_Pct']
            st.metric(
                "Volume ↔ ATR",
                f"{vol_atr_corr:.2f}",
                "Volume vs Volatility"
            )

        with col2:
            returns_rsi_corr = correlation_matrix.loc['Returns', 'RSI']
            st.metric(
                "Returns ↔ RSI",
                f"{returns_rsi_corr:.2f}",
                "Price change vs momentum"
            )

            bb_atr_corr = correlation_matrix.loc['BB_Width', 'ATR_Pct']
            st.metric(
                "BB Width ↔ ATR",
                f"{bb_atr_corr:.2f}",
                "Both measure volatility"
            )

    except Exception as e:
        st.error(f"Error calculating correlations: {str(e)}")
        st.info("Correlation matrix requires OHLCV data with at least 50 bars for accurate calculation.")
