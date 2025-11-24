"""
Trading Mode Configuration System
Defines settings and optimizations for Trader vs Investor modes
"""
from dataclasses import dataclass
from typing import Literal, Dict, Any
import streamlit as st

# Mode types
ModeType = Literal["trader", "investor"]


@dataclass
class ModeConfig:
    """Configuration for a specific trading mode"""

    # Display settings
    name: str
    icon: str
    description: str
    color: str  # Legacy: primary color (kept for backwards compatibility)

    # UI Theme Colors
    primary_color: str      # Main brand color for the mode
    secondary_color: str    # Supporting color
    accent_color: str       # Highlight color for CTAs
    success_color: str      # Bullish/positive indicators
    danger_color: str       # Bearish/negative indicators
    background_color: str   # Page background
    text_color: str         # Primary text color

    # Data settings
    default_period: str  # For yfinance: "1d", "5d", "1mo", "3mo", "1y", "5y", "max"
    default_interval: str  # For yfinance: "1m", "5m", "15m", "1h", "1d", "1wk", "1mo"
    available_periods: list[str]

    # Cache settings (in seconds)
    cache_ttl_fast: int  # For real-time data (price, volume)
    cache_ttl_medium: int  # For indicators, technicals
    cache_ttl_slow: int  # For fundamentals, earnings

    # Feature preferences
    show_intraday_charts: bool
    show_advanced_technicals: bool
    show_fundamental_analysis: bool
    show_long_term_forecasts: bool
    enable_quick_refresh: bool

    # Page recommendations
    recommended_pages: list[str]

    # Performance settings
    chart_data_points_limit: int  # Max candles to display
    preload_indicators: bool
    lazy_load_fundamentals: bool


# Trader Mode Configuration
TRADER_MODE = ModeConfig(
    name="Trader",
    icon="📊",
    description="Optimized for short-term trading with real-time data and technical analysis",
    color="#FF6B35",  # Legacy field - now using primary_color

    # UI Theme Colors (Energetic, action-oriented)
    primary_color="#FF6B35",      # Orange-red - Energy, urgency
    secondary_color="#004E89",    # Deep blue - Trust, stability
    accent_color="#00C9A7",       # Teal green - Profit, growth
    success_color="#26A69A",      # Teal - Bullish
    danger_color="#EF5350",       # Red - Bearish
    background_color="#F7F9FC",   # Light gray-blue - Clean, modern
    text_color="#1A1A2E",         # Dark blue-black - High contrast

    # Short-term data settings
    default_period="5d",
    default_interval="15m",
    available_periods=["1d", "5d", "1mo", "3mo"],

    # Aggressive caching for real-time feel
    cache_ttl_fast=60,      # 1 minute for price data
    cache_ttl_medium=300,   # 5 minutes for indicators
    cache_ttl_slow=900,     # 15 minutes for fundamentals

    # Feature preferences
    show_intraday_charts=True,
    show_advanced_technicals=True,
    show_fundamental_analysis=False,  # Less relevant for day trading
    show_long_term_forecasts=False,
    enable_quick_refresh=True,

    # Recommended pages
    recommended_pages=[
        "Stock Analysis",
        "Market Overview & Economy",
        "Advanced Visuals"
    ],

    # Performance settings
    chart_data_points_limit=500,  # Show more recent detail
    preload_indicators=True,      # Calculate RSI, MACD immediately
    lazy_load_fundamentals=True   # Don't load P/E, earnings by default
)


# Investor Mode Configuration
INVESTOR_MODE = ModeConfig(
    name="Investor",
    icon="📈",
    description="Optimized for long-term investing with fundamentals and strategic analysis",
    color="#3F51B5",  # Legacy field - now using primary_color

    # UI Theme Colors (Calm, analytical)
    primary_color="#3F51B5",      # Indigo blue - Wisdom, analysis
    secondary_color="#1565C0",    # Blue - Trust, stability
    accent_color="#43A047",       # Green - Long-term growth
    success_color="#4CAF50",      # Green - Growth
    danger_color="#F44336",       # Red - Caution
    background_color="#FAFBFC",   # Off-white - Clean, readable
    text_color="#263238",         # Blue-gray - Comfortable reading

    # Long-term data settings
    default_period="1y",
    default_interval="1d",
    available_periods=["3mo", "6mo", "1y", "2y", "5y", "max"],

    # Conservative caching for stability
    cache_ttl_fast=300,     # 5 minutes for price data (less critical)
    cache_ttl_medium=1800,  # 30 minutes for indicators
    cache_ttl_slow=3600,    # 1 hour for fundamentals

    # Feature preferences
    show_intraday_charts=False,
    show_advanced_technicals=True,
    show_fundamental_analysis=True,  # Critical for investors
    show_long_term_forecasts=True,
    enable_quick_refresh=False,

    # Recommended pages
    recommended_pages=[
        "Fundamental Analysis",
        "Portfolio & Strategy",
        "Risk & Forecasting",
        "Competitive & Market"
    ],

    # Performance settings
    chart_data_points_limit=2000,  # Show full history
    preload_indicators=False,      # Don't need immediate RSI
    lazy_load_fundamentals=False   # Load P/E, earnings upfront
)


# Mode registry
MODES: Dict[ModeType, ModeConfig] = {
    "trader": TRADER_MODE,
    "investor": INVESTOR_MODE
}


def get_current_mode() -> ModeConfig:
    """
    Get the current trading mode from session state
    Returns the mode configuration
    """
    # Initialize mode if not set
    if 'trading_mode' not in st.session_state:
        st.session_state.trading_mode = "investor"  # Default to investor mode

    mode_type: ModeType = st.session_state.trading_mode
    return MODES[mode_type]


def set_mode(mode: ModeType) -> None:
    """
    Set the trading mode in session state
    Triggers appropriate cache invalidation and UI updates

    When mode changes:
    - Clears mode-specific session data
    - Clears Streamlit cache (data will refresh with new TTLs)
    - Stores notification to show after rerun
    - Page will rerun with new settings
    """
    old_mode = st.session_state.get('trading_mode')

    if old_mode != mode:
        # Get mode names for notification
        new_mode_name = MODES[mode].name
        new_mode_icon = MODES[mode].icon

        # Clear mode-specific cached data in session state
        if 'mode_cached_data' in st.session_state:
            st.session_state.mode_cached_data = {}

        # Clear Streamlit cache to refresh with new TTLs
        # This ensures data fetches use the new mode's cache settings
        st.cache_data.clear()

        # Update mode FIRST
        st.session_state.trading_mode = mode

        # Store notification to show AFTER rerun
        st.session_state.mode_switch_notification = {
            'name': new_mode_name,
            'icon': new_mode_icon,
            'show': True
        }

        # Show toast notification (works before rerun)
        st.toast(
            f"✅ Switched to {new_mode_name} Mode {new_mode_icon}\n"
            f"🔄 Cache cleared - data will refresh with {new_mode_name.lower()} settings",
            icon="✅"
        )


def get_cache_ttl(data_type: Literal["fast", "medium", "slow"]) -> int:
    """
    Get the appropriate cache TTL for the current mode

    Args:
        data_type: Type of data being cached
            - "fast": Real-time price/volume data
            - "medium": Technical indicators
            - "slow": Fundamental data

    Returns:
        Cache TTL in seconds
    """
    mode = get_current_mode()

    if data_type == "fast":
        return mode.cache_ttl_fast
    elif data_type == "medium":
        return mode.cache_ttl_medium
    else:
        return mode.cache_ttl_slow


def should_show_feature(feature: str) -> bool:
    """
    Check if a feature should be shown in the current mode

    Args:
        feature: Feature name (e.g., "intraday_charts", "fundamental_analysis")

    Returns:
        True if feature should be displayed
    """
    mode = get_current_mode()

    feature_map = {
        "intraday_charts": mode.show_intraday_charts,
        "advanced_technicals": mode.show_advanced_technicals,
        "fundamental_analysis": mode.show_fundamental_analysis,
        "long_term_forecasts": mode.show_long_term_forecasts,
        "quick_refresh": mode.enable_quick_refresh
    }

    return feature_map.get(feature, True)  # Default to showing if unknown


def get_default_timeframe() -> Dict[str, Any]:
    """
    Get the default timeframe settings for the current mode

    Returns:
        Dictionary with 'period' and 'interval' keys
    """
    mode = get_current_mode()
    return {
        "period": mode.default_period,
        "interval": mode.default_interval,
        "available_periods": mode.available_periods
    }


def get_chart_config() -> Dict[str, Any]:
    """
    Get chart configuration for the current mode

    Returns:
        Dictionary with chart display settings
    """
    mode = get_current_mode()
    return {
        "max_points": mode.chart_data_points_limit,
        "preload_indicators": mode.preload_indicators,
        "lazy_load_fundamentals": mode.lazy_load_fundamentals
    }


def render_mode_info() -> None:
    """
    Render information about the current mode
    Also shows notification if mode was just switched
    """
    mode = get_current_mode()

    # Check if we need to show mode switch notification
    if st.session_state.get('mode_switch_notification', {}).get('show'):
        notif = st.session_state.mode_switch_notification
        st.info(
            f"**Mode Changed: {notif['icon']} {notif['name']} Mode Active**\n\n"
            f"✓ Cache settings updated\n"
            f"✓ Default timeframes adjusted\n"
            f"✓ Data refreshed with {notif['name'].lower()}-optimized cache times",
            icon="ℹ️"
        )
        # Clear notification after showing once
        st.session_state.mode_switch_notification['show'] = False

    # Show mode banner
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, {mode.color}20, transparent);
         border-left: 4px solid {mode.color}; padding: 10px; border-radius: 5px; margin: 10px 0;'>
        <div style='font-size: 14px; color: {mode.color}; font-weight: bold;'>
            {mode.icon} {mode.name} Mode Active
        </div>
        <div style='font-size: 12px; opacity: 0.8; margin-top: 5px;'>
            {mode.description}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_mode_colors() -> Dict[str, str]:
    """
    Get the complete color palette for the current mode

    Returns:
        Dictionary with color keys: primary, secondary, accent, success, danger, background, text
    """
    mode = get_current_mode()
    return {
        'primary': mode.primary_color,
        'secondary': mode.secondary_color,
        'accent': mode.accent_color,
        'success': mode.success_color,
        'danger': mode.danger_color,
        'background': mode.background_color,
        'text': mode.text_color
    }


def get_mode_badge() -> str:
    """
    Get a compact badge showing current mode
    Returns HTML string
    """
    mode = get_current_mode()
    return f"""
    <span style='background-color: {mode.primary_color}; color: white; padding: 3px 8px;
          border-radius: 12px; font-size: 11px; font-weight: bold;'>
        {mode.icon} {mode.name.upper()}
    </span>
    """


# Helper function for migration from existing code
def get_legacy_period_mapping(old_period: str) -> str:
    """
    Map old hardcoded period strings to mode-aware periods
    For gradual migration of existing code

    Args:
        old_period: Old period string (e.g., "1mo")

    Returns:
        Mode-appropriate period string
    """
    mode = get_current_mode()

    # If old period is available in current mode, use it
    if old_period in mode.available_periods:
        return old_period

    # Otherwise, return mode default
    return mode.default_period


def validate_user_selection(selection_type: str, selection_value: Any) -> Dict[str, Any]:
    """
    Validate if a user's selection is optimal for the current mode
    Shows notifications if selection would trigger cache clear/refresh

    Args:
        selection_type: Type of selection ("period", "interval", "feature", etc.)
        selection_value: The selected value

    Returns:
        Dictionary with:
        - is_optimal: bool (True if optimal for current mode, False if suboptimal)
        - is_allowed: bool (True if selection will work, False if disabled)
        - needs_cache_clear: bool (True if selection requires cache clear)
        - message: str (notification message for user)
        - recommended_value: Any (mode-appropriate alternative)
    """
    mode = get_current_mode()
    result = {
        "is_optimal": True,
        "is_allowed": True,
        "needs_cache_clear": False,
        "message": "",
        "recommended_value": selection_value
    }

    if selection_type == "period":
        # Check if selected period is available in current mode
        if selection_value not in mode.available_periods:
            result["is_optimal"] = False
            result["is_allowed"] = True  # Still works, just not optimal
            result["needs_cache_clear"] = True
            result["recommended_value"] = mode.default_period
            result["message"] = (
                f"⚠️ **Period '{selection_value}' not optimized for {mode.name} Mode**\n\n"
                f"The period you selected is outside the recommended range for {mode.name} mode. "
                f"Your selection will work, but consider using **{mode.default_period}** for optimal performance.\n\n"
                f"**Available periods for {mode.name} mode:** {', '.join(mode.available_periods)}"
            )
        else:
            result["message"] = f"✓ Period '{selection_value}' is optimized for {mode.name} mode"

    elif selection_type == "interval":
        # For trader mode, warn about daily intervals
        if mode.name == "Trader" and selection_value in ["1d", "1wk", "1mo"]:
            result["is_optimal"] = False
            result["is_allowed"] = True  # Still works, just not optimal
            result["message"] = (
                f"ℹ️ **Interval '{selection_value}' is better for Investor mode**\n\n"
                f"You're in Trader mode, which is optimized for shorter intervals like "
                f"**{mode.default_interval}** (intraday trading).\n\n"
                f"Consider switching to **Investor mode** if you want to analyze long-term trends."
            )

        # For investor mode, warn about intraday intervals
        elif mode.name == "Investor" and selection_value in ["1m", "5m", "15m", "1h"]:
            result["is_optimal"] = False
            result["is_allowed"] = True  # Still works, just not optimal
            result["message"] = (
                f"ℹ️ **Interval '{selection_value}' is better for Trader mode**\n\n"
                f"You're in Investor mode, which is optimized for longer intervals like "
                f"**{mode.default_interval}** (long-term analysis).\n\n"
                f"Consider switching to **Trader mode** if you want intraday charts."
            )

    elif selection_type == "feature":
        # Check if feature should be shown in current mode
        is_feature_enabled = should_show_feature(selection_value)

        if not is_feature_enabled:
            result["is_optimal"] = False
            result["is_allowed"] = False  # Feature is disabled
            result["message"] = (
                f"⚠️ **Feature '{selection_value}' is disabled in {mode.name} mode**\n\n"
                f"This feature is optimized for the opposite mode. "
                f"Switch modes to access this feature."
            )

            # Recommend switching modes
            opposite_mode = "investor" if mode.name == "Trader" else "trader"
            result["recommended_value"] = f"Switch to {opposite_mode} mode"

    return result


def notify_user_if_needed(validation_result: Dict[str, Any], show_toast: bool = True) -> None:
    """
    Display notification to user based on validation result

    Args:
        validation_result: Result from validate_user_selection()
        show_toast: Whether to show toast notification (in addition to info box)
    """
    if validation_result["message"]:
        # Determine icon and notification type based on result
        if not validation_result["is_allowed"]:
            # Feature is disabled - show warning
            icon = "⚠️"
            st.warning(validation_result["message"], icon=icon)
        elif not validation_result["is_optimal"]:
            # Selection is suboptimal - show info
            icon = "ℹ️"
            st.info(validation_result["message"], icon=icon)
        else:
            # Selection is optimal - just show brief confirmation
            if show_toast:
                st.toast(validation_result["message"], icon="✓")


def get_mode_optimized_selection(selection_type: str, user_value: Any = None) -> Any:
    """
    Get mode-optimized selection with automatic validation and notification

    This is a convenience function that:
    1. Validates user's selection against current mode
    2. Shows notification if needed
    3. Returns the selection (or mode-appropriate alternative)

    Args:
        selection_type: Type of selection ("period", "interval", etc.)
        user_value: User's selected value (None = use mode default)

    Returns:
        Mode-appropriate value (user's selection if valid, default if not provided)

    Example:
        # In a page
        period = st.selectbox("Period", ["1d", "1mo", "1y"])
        optimized_period = get_mode_optimized_selection("period", period)
    """
    mode = get_current_mode()

    # If no user value provided, return mode default
    if user_value is None:
        if selection_type == "period":
            return mode.default_period
        elif selection_type == "interval":
            return mode.default_interval

    # Validate user's selection
    validation = validate_user_selection(selection_type, user_value)

    # Show notification if needed
    notify_user_if_needed(validation, show_toast=False)

    # Return user's value if allowed, otherwise return recommended value
    if validation["is_allowed"] and validation["is_optimal"]:
        return user_value
    elif validation["is_allowed"]:
        # Suboptimal but allowed - still use user's value
        return user_value
    else:
        # Not allowed - use recommended value
        return validation["recommended_value"]
