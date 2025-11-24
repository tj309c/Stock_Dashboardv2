"""
Global Sidebar Configuration
Centralized sidebar setup for consistent UI across all pages
"""
import streamlit as st
from ai_model_config import render_model_selector, display_provider_status
from app_utils import full_width_button
from mode_config import get_current_mode, set_mode, MODES, ModeType


def render_global_sidebar():
    """
    Render global sidebar controls that should appear on all pages

    This function handles:
    - Theme toggle
    - AI features toggle
    - AI model selection (global to all pages)

    Returns:
        dict: Configuration values from sidebar
            {
                'theme': str,  # 'light' or 'dark'
                'enable_ai_features': bool,
                'selected_ai_model': str or None
            }
    """

    # ============================
    # TRADING MODE SELECTOR
    # ============================

    st.sidebar.markdown("### 🎯 Trading Mode")

    current_mode = get_current_mode()

    # Create two columns for mode buttons
    col1, col2 = st.sidebar.columns(2)

    with col1:
        trader_selected = st.session_state.get('trading_mode', 'investor') == 'trader'
        if full_width_button(
            f"{'✓ ' if trader_selected else ''}{MODES['trader'].icon} Trader",
            key="trader_mode_btn",
            type="primary" if trader_selected else "secondary"
        ):
            if not trader_selected:
                set_mode('trader')
                st.rerun()

    with col2:
        investor_selected = st.session_state.get('trading_mode', 'investor') == 'investor'
        if full_width_button(
            f"{'✓ ' if investor_selected else ''}{MODES['investor'].icon} Investor",
            key="investor_mode_btn",
            type="primary" if investor_selected else "secondary"
        ):
            if not investor_selected:
                set_mode('investor')
                st.rerun()

    # Display current mode info
    st.sidebar.caption(f"**{current_mode.name} Mode:** {current_mode.description}")

    # Show mode-specific settings
    with st.sidebar.expander("ℹ️ Mode Details", expanded=False):
        st.markdown(f"""
        **Default Timeframe:** {current_mode.default_period}

        **Cache Strategy:**
        - Price data: {current_mode.cache_ttl_fast}s
        - Indicators: {current_mode.cache_ttl_medium}s
        - Fundamentals: {current_mode.cache_ttl_slow}s

        **Features:**
        - {'✅' if current_mode.show_intraday_charts else '❌'} Intraday charts
        - {'✅' if current_mode.show_advanced_technicals else '❌'} Advanced technicals
        - {'✅' if current_mode.show_fundamental_analysis else '❌'} Fundamental analysis
        - {'✅' if current_mode.show_long_term_forecasts else '❌'} Long-term forecasts

        **Recommended Pages:**
        {chr(10).join(f"- {page}" for page in current_mode.recommended_pages)}
        """)

    st.sidebar.markdown("---")

    # ============================
    # THEME TOGGLE
    # ============================

    # Function to get current theme
    def get_theme():
        if 'theme' in st.query_params:
            return st.query_params['theme']
        if 'theme' in st.session_state:
            return st.session_state['theme']
        return "light"

    # Set theme based on initial load or user selection
    if 'theme' not in st.session_state:
        st.session_state.theme = get_theme()

    # Toggle button
    if st.sidebar.button(f"Switch to {'Dark' if st.session_state.theme == 'light' else 'Light'} Theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.query_params['theme'] = st.session_state.theme
        st.rerun()

    # ============================
    # SETTINGS SECTION
    # ============================

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")

    # ============================
    # AI FEATURES TOGGLE (GLOBAL)
    # ============================

    # Initialize AI toggle if not already in session state
    if 'enable_ai_features' not in st.session_state:
        st.session_state.enable_ai_features = True

    st.session_state.enable_ai_features = st.sidebar.checkbox(
        "Enable AI Features",
        value=st.session_state.enable_ai_features,
        help="Toggle AI-powered analysis across all pages (market intelligence, competitor analysis, chart insights, etc.). Disabling can improve performance and reduce API costs."
    )

    # ============================
    # AI MODEL SELECTOR (GLOBAL)
    # ============================

    selected_model = None

    # Only show AI configuration if AI features are enabled
    # COMMENTED OUT - Each page will handle its own AI model selection
    # if st.session_state.enable_ai_features:
    #     st.sidebar.markdown("---")
    #     st.sidebar.markdown("### 🤖 AI Configuration")
    #     st.sidebar.caption("This AI model will be used across all pages")
    #
    #     # Render model selector with a GLOBAL session key
    #     # This ensures all pages reference the same selected model
    #     selected_model = render_model_selector(
    #         session_key="global_ai_model",  # GLOBAL key used by all pages
    #         label="AI Model:",
    #         help_text="Choose which AI model to use for all AI-powered features across the dashboard",
    #         show_cost=True,
    #         show_details=True
    #     )
    #
    #     # Show provider status
    #     display_provider_status()

    # ============================
    # RETURN CONFIGURATION
    # ============================

    return {
        'theme': st.session_state.theme,
        'enable_ai_features': st.session_state.enable_ai_features,
        'selected_ai_model': selected_model,
        'trading_mode': st.session_state.get('trading_mode', 'investor'),
        'mode_config': current_mode
    }


def apply_theme_css(theme: str):
    """
    Apply CSS based on selected theme

    Args:
        theme: 'light' or 'dark'
    """
    if theme == "dark":
        dark_theme_css = """
        <style>
        :root {
            --primary-color: #6C63FF;
            --background-color: #1a1a2e;
            --secondary-background-color: #16213e;
            --text-color: #e0e0e0;
            --border-color: #0f3460;
            --card-bg-color: #16213e;
        }
        body {
            color: var(--text-color);
            background-color: var(--background-color);
        }
        .stApp {
            background-color: var(--background-color);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div, .stDateInput>div>div>input {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }
        .stMarkdown, .stText {
            color: var(--text-color);
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color);
        }
        .stMetric {
            background-color: var(--card-bg-color);
            border: 1px solid var(--border-color);
            border-radius: 5px;
            padding: 10px;
        }
        .stMetric label {
            color: var(--text-color);
        }
        .st-emotion-cache-1pxazr-0 > div {
            background-color: #0f1626;
        }
        .ai-response-box {
            background-color: #0f3460;
            border-left: 5px solid #6C63FF;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            color: var(--text-color);
        }
        .ai-response-box p {
            margin-bottom: 5px;
        }
        </style>
        """
        st.markdown(dark_theme_css, unsafe_allow_html=True)
    else:
        light_theme_css = """
        <style>
        :root {
            --primary-color: #6C63FF;
            --background-color: #FFFFFF;
            --secondary-background-color: #F0F2F6;
            --text-color: #333333;
            --border-color: #E0E0E0;
            --card-bg-color: #FFFFFF;
        }
        body {
            color: var(--text-color);
            background-color: var(--background-color);
        }
        .stApp {
            background-color: var(--background-color);
        }
        .stTextInput>div>div>input, .stSelectbox>div>div, .stDateInput>div>div>input {
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }
        .stMarkdown, .stText {
            color: var(--text-color);
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color);
        }
        [data-testid="stMetric"] {
            background-color: #F8F9FA;
            border: 1px solid #DDD;
            border-radius: 5px;
            padding: 10px;
        }
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }
            h2 {
                font-size: 1.5rem;
            }
            [data-testid="stMetric"] {
                padding-top: 5px;
                padding-bottom: 5px;
            }
            [data-testid="stMetric"] label {
                font-size: 0.9rem;
            }
        }
        </style>
        """
        st.markdown(light_theme_css, unsafe_allow_html=True)


def get_global_ai_model():
    """
    Get the globally selected AI model from session state

    Returns:
        str or None: The selected model ID, or None if no model selected or AI disabled
    """
    if not st.session_state.get('enable_ai_features', False):
        return None

    return st.session_state.get('global_ai_model')
