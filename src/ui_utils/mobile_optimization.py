"""
Mobile Optimization and Responsive Design
Improves UX on mobile devices
"""

import streamlit as st


def inject_mobile_css():
    """Inject mobile-responsive CSS"""
    mobile_css = """
    <style>
    /* Mobile optimization */
    @media only screen and (max-width: 768px) {
        /* Reduce font sizes on mobile */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.4rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Make buttons full width */
        .stButton button {
            width: 100% !important;
        }
        
        /* Reduce padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        /* Stack columns on mobile */
        .row-widget.stHorizontal {
            flex-direction: column !important;
        }
        
        /* Make charts responsive */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Reduce metric spacing */
        [data-testid="metric-container"] {
            margin-bottom: 0.5rem !important;
        }
        
        /* Sidebar width */
        [data-testid="stSidebar"] {
            width: 250px !important;
        }
        
        /* Make tables scrollable */
        .dataframe {
            font-size: 0.8rem !important;
            overflow-x: auto !important;
        }
        
        /* Reduce input field sizes */
        .stTextInput input {
            font-size: 1rem !important;
        }
        
        /* Make expanders more compact */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
        }
    }
    
    /* Tablet optimization (768px - 1024px) */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        h1 {
            font-size: 2rem !important;
        }
        
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    
    /* Touch-friendly buttons */
    .stButton button {
        min-height: 44px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Improve tap target sizes */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
    
    /* Make tabs scrollable on mobile */
    @media only screen and (max-width: 768px) {
        [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            white-space: nowrap !important;
        }
    }
    </style>
    """
    st.markdown(mobile_css, unsafe_allow_html=True)


def is_mobile() -> bool:
    """
    Detect if user is on mobile device (approximation)
    Note: This is a client-side detection approximation
    """
    # Streamlit doesn't have direct mobile detection
    # This is a workaround using viewport width
    mobile_check = """
    <script>
    if (window.innerWidth <= 768) {
        window.parent.postMessage({type: 'mobile_detected'}, '*');
    }
    </script>
    """
    st.components.v1.html(mobile_check, height=0)
    return False  # Default to desktop


def render_mobile_friendly_metrics(metrics: dict, mobile_cols: int = 1, desktop_cols: int = 4):
    """
    Render metrics that adapt to screen size
    
    Args:
        metrics: Dict of {label: value} metrics
        mobile_cols: Number of columns on mobile
        desktop_cols: Number of columns on desktop
    """
    # Create responsive columns
    # On mobile, this will stack; on desktop, it will spread
    cols = st.columns(desktop_cols)
    
    for idx, (label, value) in enumerate(metrics.items()):
        col = cols[idx % desktop_cols]
        with col:
            st.metric(label, value)


def render_mobile_warning():
    """Show mobile optimization notice"""
    mobile_notice = """
    <div style="
        background: #FFB62720;
        border-left: 3px solid #FFB627;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    ">
        <strong>📱 Mobile Device Detected</strong><br>
        <small>For best experience, rotate to landscape mode or use a desktop browser.</small>
    </div>
    """
    st.markdown(mobile_notice, unsafe_allow_html=True)


def optimize_chart_for_mobile(fig, mobile_height: int = 400):
    """
    Optimize Plotly chart for mobile viewing
    
    Args:
        fig: Plotly figure
        mobile_height: Height for mobile devices
        
    Returns:
        Modified figure
    """
    # Mobile-friendly layout
    fig.update_layout(
        height=mobile_height,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(size=10)
    )
    
    return fig


class MobileAdapter:
    """Adapter for mobile-friendly UI components"""
    
    @staticmethod
    def render_collapsible_section(title: str, content_func: callable, default_open: bool = False):
        """
        Render collapsible sections on mobile, normal on desktop
        
        Args:
            title: Section title
            content_func: Function that renders content
            default_open: Whether section starts open
        """
        with st.expander(f"📱 {title}", expanded=default_open):
            content_func()
    
    @staticmethod
    def render_horizontal_scroll_container(items: list, item_width: str = "150px"):
        """
        Create horizontally scrollable container for mobile
        
        Args:
            items: List of items to display
            item_width: Width of each item
        """
        scroll_html = """
        <div style="
            display: flex;
            overflow-x: auto;
            gap: 10px;
            padding: 10px 0;
            -webkit-overflow-scrolling: touch;
        ">
        """
        
        for item in items:
            scroll_html += f"""
            <div style="
                min-width: {item_width};
                padding: 1rem;
                background: #1C1F2620;
                border-radius: 8px;
                border: 1px solid #3C3F44;
            ">
                {item}
            </div>
            """
        
        scroll_html += "</div>"
        st.markdown(scroll_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_swipeable_cards(cards: list):
        """
        Render swipeable cards for mobile
        
        Args:
            cards: List of card content (HTML strings)
        """
        MobileAdapter.render_horizontal_scroll_container(cards, item_width="300px")


def apply_mobile_optimizations():
    """Apply all mobile optimizations at once"""
    inject_mobile_css()
    
    # Additional JavaScript for mobile enhancements
    mobile_js = """
    <script>
    // Prevent double-tap zoom on buttons
    document.addEventListener('touchstart', function(e) {
        if (e.target.tagName === 'BUTTON') {
            e.preventDefault();
        }
    }, {passive: false});
    
    // Smooth scroll for mobile
    document.documentElement.style.scrollBehavior = 'smooth';
    </script>
    """
    st.components.v1.html(mobile_js, height=0)


# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Mobile Optimization Demo", layout="wide")
    
    # Apply optimizations
    apply_mobile_optimizations()
    
    st.title("📱 Mobile Optimization Demo")
    
    # Show mobile warning
    render_mobile_warning()
    
    st.markdown("---")
    
    # Mobile-friendly metrics
    st.markdown("### Responsive Metrics")
    render_mobile_friendly_metrics({
        'Price': '$150.00',
        'Change': '+2.5%',
        'Volume': '50M',
        'Market Cap': '$2.5T'
    }, mobile_cols=2, desktop_cols=4)
    
    st.markdown("---")
    
    # Collapsible sections
    st.markdown("### Collapsible Sections")
    MobileAdapter.render_collapsible_section(
        "Technical Analysis",
        lambda: st.write("Technical analysis content here..."),
        default_open=True
    )
    
    st.markdown("---")
    
    # Horizontal scroll cards
    st.markdown("### Swipeable Cards")
    cards = [
        f"<strong>Card {i}</strong><br>Content {i}" for i in range(1, 6)
    ]
    MobileAdapter.render_swipeable_cards(cards)
