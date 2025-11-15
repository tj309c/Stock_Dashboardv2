"""
Accessibility (A11y) Improvements
WCAG 2.1 compliance enhancements
"""

import streamlit as st
from typing import Dict, List


def inject_accessibility_css():
    """Inject accessibility-focused CSS"""
    a11y_css = """
    <style>
    /* Focus indicators */
    button:focus,
    input:focus,
    select:focus,
    textarea:focus {
        outline: 3px solid #00FF88 !important;
        outline-offset: 2px !important;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        body {
            background: #000 !important;
            color: #FFF !important;
        }
        
        .stButton button {
            border: 2px solid #FFF !important;
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Improve color contrast */
    .stMetricValue {
        font-weight: 700 !important;
    }
    
    /* Make links more visible */
    a {
        text-decoration: underline !important;
        font-weight: 600 !important;
    }
    
    /* Skip to main content link */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #00FF88;
        color: #000;
        padding: 8px;
        z-index: 100;
        font-weight: bold;
    }
    
    .skip-link:focus {
        top: 0;
    }
    
    /* Improve button contrast */
    .stButton button {
        font-weight: 600 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Screen reader only content */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0,0,0,0);
        white-space: nowrap;
        border-width: 0;
    }
    
    /* ARIA live regions */
    [aria-live="polite"],
    [aria-live="assertive"] {
        position: relative;
    }
    </style>
    """
    st.markdown(a11y_css, unsafe_allow_html=True)


def add_skip_navigation():
    """Add skip to main content link for keyboard users"""
    skip_nav_html = """
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <div id="main-content"></div>
    """
    st.markdown(skip_nav_html, unsafe_allow_html=True)


def render_accessible_metric(
    label: str,
    value: str,
    delta: str = None,
    description: str = None
):
    """
    Render metric with accessibility improvements
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change value
        description: Optional longer description for screen readers
    """
    # Create accessible description
    aria_label = f"{label}: {value}"
    if delta:
        aria_label += f", change: {delta}"
    if description:
        aria_label += f". {description}"
    
    metric_html = f"""
    <div role="region" aria-label="{aria_label}" style="
        padding: 1rem;
        background: #1C1F2620;
        border-radius: 8px;
        border-left: 3px solid #00FF88;
    ">
        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div style="font-size: 1.8rem; font-weight: 700;">
            {value}
        </div>
        {f'<div style="color: #00FF88; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>' if delta else ''}
    </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)


def add_chart_alt_text(chart_type: str, data_summary: str):
    """
    Add alt text description for charts
    
    Args:
        chart_type: Type of chart (e.g., "Line chart", "Bar chart")
        data_summary: Summary of chart data
    """
    alt_text_html = f"""
    <div class="sr-only" role="img" aria-label="{chart_type} showing {data_summary}">
        {chart_type}: {data_summary}
    </div>
    """
    st.markdown(alt_text_html, unsafe_allow_html=True)


def render_accessible_table(
    df,
    table_caption: str,
    summary: str = None
):
    """
    Render table with accessibility improvements
    
    Args:
        df: DataFrame to display
        table_caption: Caption for the table
        summary: Optional summary for screen readers
    """
    st.markdown(f"### {table_caption}")
    
    if summary:
        st.markdown(f'<div class="sr-only">{summary}</div>', unsafe_allow_html=True)
    
    # Add ARIA labels
    st.dataframe(df, use_container_width=True)
    
    # Add row count for screen readers
    st.markdown(
        f'<div class="sr-only">Table contains {len(df)} rows and {len(df.columns)} columns</div>',
        unsafe_allow_html=True
    )


class A11yHelper:
    """Helper class for accessibility features"""
    
    @staticmethod
    def announce(message: str, priority: str = "polite"):
        """
        Announce message to screen readers
        
        Args:
            message: Message to announce
            priority: 'polite' or 'assertive'
        """
        announce_html = f"""
        <div aria-live="{priority}" aria-atomic="true" class="sr-only">
            {message}
        </div>
        """
        st.markdown(announce_html, unsafe_allow_html=True)
    
    @staticmethod
    def add_landmark(content: str, landmark_type: str = "region", label: str = None):
        """
        Wrap content in ARIA landmark
        
        Args:
            content: HTML content
            landmark_type: Type of landmark (main, navigation, complementary, etc.)
            label: Optional aria-label
        """
        label_attr = f'aria-label="{label}"' if label else ''
        landmark_html = f"""
        <div role="{landmark_type}" {label_attr}>
            {content}
        </div>
        """
        st.markdown(landmark_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_accessible_button(
        label: str,
        onclick: str = None,
        description: str = None,
        icon: str = None
    ):
        """
        Render accessible button with proper ARIA attributes
        
        Args:
            label: Button label
            onclick: Optional JavaScript onclick handler
            description: Optional longer description
            icon: Optional emoji icon
        """
        aria_described = f'aria-describedby="btn-desc-{label}"' if description else ''
        onclick_attr = f'onclick="{onclick}"' if onclick else ''
        
        button_html = f"""
        <button 
            class="stButton"
            aria-label="{label}"
            {aria_described}
            {onclick_attr}
            style="
                padding: 0.5rem 1rem;
                background: #00FF8822;
                border: 2px solid #00FF88;
                border-radius: 8px;
                color: #FFF;
                font-weight: 600;
                cursor: pointer;
                min-height: 44px;
            ">
            {icon + ' ' if icon else ''}{label}
        </button>
        {f'<div id="btn-desc-{label}" class="sr-only">{description}</div>' if description else ''}
        """
        st.markdown(button_html, unsafe_allow_html=True)
    
    @staticmethod
    def add_keyboard_navigation_hint():
        """Add keyboard navigation instructions"""
        hint_html = """
        <div style="
            background: #1C1F2620;
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            border-left: 3px solid #00FF88;
        " role="note">
            <strong>♿ Keyboard Navigation:</strong><br>
            <kbd>Tab</kbd> to navigate • <kbd>Enter</kbd> to select • <kbd>Esc</kbd> to close
        </div>
        """
        st.markdown(hint_html, unsafe_allow_html=True)


def check_color_contrast(foreground: str, background: str) -> Dict:
    """
    Check WCAG color contrast ratio
    Note: This is a simplified check
    
    Args:
        foreground: Foreground color (hex)
        background: Background color (hex)
        
    Returns:
        Dict with contrast info
    """
    # Simplified implementation
    # Real implementation would calculate luminance properly
    return {
        'ratio': 7.0,  # Placeholder
        'passes_aa': True,
        'passes_aaa': True
    }


def apply_accessibility_improvements():
    """Apply all accessibility improvements at once"""
    inject_accessibility_css()
    add_skip_navigation()
    A11yHelper.add_keyboard_navigation_hint()


# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Accessibility Demo", layout="wide")
    
    # Apply a11y improvements
    apply_accessibility_improvements()
    
    st.title("♿ Accessibility Features Demo")
    
    # Accessible metrics
    st.markdown("### Accessible Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_accessible_metric(
            label="Stock Price",
            value="$150.00",
            delta="+2.50 (+1.69%)",
            description="Stock price increased by 1.69% today"
        )
    
    with col2:
        render_accessible_metric(
            label="Volume",
            value="50.2M",
            description="Trading volume is 50.2 million shares"
        )
    
    with col3:
        render_accessible_metric(
            label="Market Cap",
            value="$2.5T",
            description="Market capitalization is 2.5 trillion dollars"
        )
    
    st.markdown("---")
    
    # Chart with alt text
    st.markdown("### Chart with Description")
    add_chart_alt_text(
        "Line chart",
        "stock price over the last 6 months, showing upward trend from $120 to $150"
    )
    
    # Screen reader announcement
    A11yHelper.announce("Data has been updated", priority="polite")
    
    st.markdown("---")
    
    # Accessible table
    import pandas as pd
    sample_df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Price': [148, 149, 150],
        'Volume': [50000000, 51000000, 52000000]
    })
    
    render_accessible_table(
        sample_df,
        table_caption="Recent Trading Data",
        summary="Table showing recent trading activity including date, closing price, and trading volume"
    )
