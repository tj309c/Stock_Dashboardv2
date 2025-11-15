"""
Centralized Design System - Single Source of Truth for Styling
Replace all hardcoded colors with this module for consistent theming
"""

from dataclasses import dataclass
from typing import Literal
import streamlit as st


@dataclass
class Colors:
    """All app colors in one place - change theme by editing this class"""
    
    # Primary colors
    primary: str = "#22C55E"       # Green (Robinhood-inspired)
    primary_dark: str = "#15803D"
    primary_light: str = "#86EFAC"
    
    # Secondary colors
    secondary: str = "#1F2937"     # Dark gray
    secondary_dark: str = "#111827"
    secondary_light: str = "#9CA3AF"
    
    # Status colors
    success: str = "#10B981"       # Green for positive
    warning: str = "#FBBF24"       # Yellow/Orange for caution
    danger: str = "#EF4444"        # Red for negative
    info: str = "#3B82F6"          # Blue for information
    neutral: str = "#9CA3AF"       # Gray for neutral
    
    # Asset class colors (use consistently across all dashboards)
    stocks: str = "#22C55E"        # Green
    options: str = "#F59E0B"       # Orange
    crypto: str = "#3B82F6"        # Blue
    portfolio: str = "#EC4899"     # Pink
    advanced: str = "#8B5CF6"      # Purple
    
    # Sentiment colors
    bullish: str = "#10B981"       # Green - bulls win
    bearish: str = "#EF4444"       # Red - bears attack
    neutral_sentiment: str = "#9CA3AF"  # Gray - sideways
    
    # Chart colors
    chart_up: str = "#22C55E"      # Green candles
    chart_down: str = "#EF4444"    # Red candles
    chart_neutral: str = "#9CA3AF" # Gray
    chart_line: str = "#3B82F6"    # Blue line charts
    
    # Background colors (for dark mode compatibility)
    bg_primary: str = "#0E1117"    # Main background
    bg_secondary: str = "#262730"  # Card background
    bg_tertiary: str = "#1E1E1E"   # Sidebar background
    
    # Text colors
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#9CA3AF"
    text_muted: str = "#6B7280"


@dataclass
class Spacing:
    """Consistent spacing throughout app"""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass
class Typography:
    """Font sizes and weights"""
    h1: str = "2.5rem"
    h2: str = "2rem"
    h3: str = "1.5rem"
    h4: str = "1.25rem"
    body: str = "1rem"
    small: str = "0.875rem"
    caption: str = "0.75rem"


class ThemeManager:
    """Manage theme application and consistent styling"""
    
    colors = Colors()
    spacing = Spacing()
    typography = Typography()
    
    @staticmethod
    def get_asset_color(asset_type: Literal["stocks", "options", "crypto", "portfolio", "advanced"]) -> str:
        """Get color for asset type"""
        return getattr(ThemeManager.colors, asset_type)
    
    @staticmethod
    def get_sentiment_color(sentiment: Literal["bullish", "bearish", "neutral"]) -> str:
        """Get color for sentiment"""
        if sentiment.lower() == "bullish":
            return ThemeManager.colors.bullish
        elif sentiment.lower() == "bearish":
            return ThemeManager.colors.bearish
        else:
            return ThemeManager.colors.neutral_sentiment
    
    @staticmethod
    def get_status_color(status: Literal["success", "warning", "danger", "info", "neutral"]) -> str:
        """Get color for status"""
        return getattr(ThemeManager.colors, status)
    
    @staticmethod
    def apply_metric_card_style():
        """Apply consistent metric card styling across all dashboards"""
        st.markdown("""
        <style>
        /* Metric Card Styling */
        .metric-card {
            background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #3F3F3F;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .metric-title {
            font-size: 0.875rem;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        
        .metric-change {
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .metric-positive {
            color: #10B981;
        }
        
        .metric-negative {
            color: #EF4444;
        }
        
        .metric-neutral {
            color: #9CA3AF;
        }
        </style>
        """, unsafe_allow_html=True)


class MetricCardRenderer:
    """Render consistent metric cards across all dashboards"""
    
    @staticmethod
    def render(
        title: str,
        value: str,
        change: float = None,
        change_label: str = None,
        asset_type: Literal["stocks", "options", "crypto", "portfolio", "advanced"] = "stocks",
        help_text: str = None
    ):
        """
        Render a professional metric card
        
        Args:
            title: Metric title (e.g., "Current Price")
            value: Main value to display (e.g., "$175.50")
            change: Numeric change value (e.g., 2.35 for +2.35%)
            change_label: Custom label for change (default: "+X.XX%")
            asset_type: Type of asset for color theming
            help_text: Tooltip help text
        """
        color = ThemeManager.get_asset_color(asset_type)
        
        # Determine change styling
        change_html = ""
        if change is not None:
            if change > 0:
                change_class = "metric-positive"
                arrow = "↑"
            elif change < 0:
                change_class = "metric-negative"
                arrow = "↓"
            else:
                change_class = "metric-neutral"
                arrow = "→"
            
            change_text = change_label if change_label else f"{change:+.2f}%"
            change_html = f'<div class="metric-change {change_class}">{arrow} {change_text}</div>'
        
        # Build card HTML
        card_html = f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            {change_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        if help_text:
            st.caption(help_text)


class ChartTheme:
    """Consistent Plotly chart theming"""
    
    @staticmethod
    def get_plotly_template() -> dict:
        """Get standard Plotly template for all charts"""
        return {
            'layout': {
                'template': 'plotly_dark',
                'paper_bgcolor': ThemeManager.colors.bg_primary,
                'plot_bgcolor': ThemeManager.colors.bg_secondary,
                'font': {
                    'color': ThemeManager.colors.text_primary,
                    'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
                },
                'xaxis': {
                    'gridcolor': '#2D2D2D',
                    'showgrid': True,
                    'zeroline': False
                },
                'yaxis': {
                    'gridcolor': '#2D2D2D',
                    'showgrid': True,
                    'zeroline': False
                },
                'colorway': [
                    ThemeManager.colors.primary,
                    ThemeManager.colors.info,
                    ThemeManager.colors.warning,
                    ThemeManager.colors.danger,
                    ThemeManager.colors.success
                ]
            }
        }
    
    @staticmethod
    def apply_to_figure(fig):
        """Apply theme to a Plotly figure"""
        fig.update_layout(**ChartTheme.get_plotly_template()['layout'])
        return fig


# Convenience functions for common use cases
def get_color(color_name: str) -> str:
    """
    Get a color by name from the design system
    
    Args:
        color_name: Name of color (e.g., 'primary', 'success', 'bullish', 'stocks')
    
    Returns:
        Hex color code
    """
    return getattr(ThemeManager.colors, color_name, ThemeManager.colors.neutral)


def get_change_color(value: float) -> str:
    """
    Get appropriate color for a numeric change
    
    Args:
        value: Numeric value (positive/negative/zero)
    
    Returns:
        Hex color code (green for positive, red for negative, gray for zero)
    """
    if value > 0:
        return ThemeManager.colors.success
    elif value < 0:
        return ThemeManager.colors.danger
    else:
        return ThemeManager.colors.neutral


def format_metric_html(title: str, value: str, color: str = None) -> str:
    """
    Format a metric as HTML with consistent styling
    
    Args:
        title: Metric title
        value: Metric value
        color: Optional color override
    
    Returns:
        HTML string
    """
    color = color or ThemeManager.colors.primary
    return f"""
    <div style="text-align: center; padding: 10px;">
        <div style="color: #9CA3AF; font-size: 0.875rem; text-transform: uppercase;">{title}</div>
        <div style="color: {color}; font-size: 1.5rem; font-weight: 700; margin-top: 5px;">{value}</div>
    </div>
    """


# USAGE EXAMPLES:
"""
# Example 1: Replace hardcoded colors
# OLD:
# st.markdown(f'<h2 style="color: #22C55E;">Price: $100</h2>', unsafe_allow_html=True)
#
# NEW:
# from src.ui_utils.design_system import get_color
# st.markdown(f'<h2 style="color: {get_color("primary")};">Price: $100</h2>', unsafe_allow_html=True)

# Example 2: Render professional metric cards
# from src.ui_utils.design_system import MetricCardRenderer
# MetricCardRenderer.render(
#     title="Current Price",
#     value="$175.50",
#     change=2.35,
#     asset_type="stocks"
# )

# Example 3: Apply theme to Plotly charts
# from src.ui_utils.design_system import ChartTheme
# fig = go.Figure(...)
# fig = ChartTheme.apply_to_figure(fig)
# st.plotly_chart(fig)

# Example 4: Get sentiment-based colors
# from src.ui_utils.design_system import ThemeManager
# sentiment = "bullish"
# color = ThemeManager.get_sentiment_color(sentiment)
# st.markdown(f'<span style="color: {color};">BULLISH 🚀</span>', unsafe_allow_html=True)
"""
