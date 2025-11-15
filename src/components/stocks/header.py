"""
Stocks Dashboard Header Component
Handles ticker input, watchlist, analyze button, and service layer toggle
"""
import streamlit as st
from wsb_quotes import get_dashboard_tagline
from src.ui_utils.watchlist_manager import render_add_to_watchlist_button
from src.ui_utils.market_hours import render_compact_market_status


def render_stocks_header(ticker: str = "META") -> tuple[str, bool]:
    """
    Render the stocks dashboard header with ticker input and controls
    
    Args:
        ticker: Default ticker symbol
        
    Returns:
        tuple: (selected_ticker, use_service_layer)
    """
    # Initialize session state
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = ticker
    
    # Display title and tagline
    tagline = get_dashboard_tagline("stocks")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 5px; font-weight: 700; letter-spacing: -0.5px;">
            📈 STONKS ANALYSIS
        </h1>
        <p style="font-size: 0.95rem; opacity: 0.95; font-style: italic; margin-top: 0;">
            {tagline}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Market hours indicator
    st.markdown(
        f'<div style="text-align: center;">{render_compact_market_status()}</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ticker input controls
    col1, col2, col3, col4, col5 = st.columns([2.5, 0.5, 1, 1, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Ticker Symbol",
            value=ticker,
            placeholder="e.g., AAPL, TSLA, GME",
            help="Enter a stock ticker (e.g., AAPL, TSLA, GME, AMC)"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if ticker_input:
            render_add_to_watchlist_button(ticker_input)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Analyze", type="primary", key="analyze_stock"):
            st.session_state.active_ticker = ticker_input
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        use_service = st.checkbox(
            "🎯 Service Layer",
            value=False,
            help="Use new Service Layer (cleaner, testable)",
            key="use_service"
        )
    
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_stocks"):
            st.rerun()
    
    # Get active ticker
    active_ticker = st.session_state.get("active_ticker", ticker_input)
    
    return active_ticker, use_service


def render_stocks_title_only(tagline: str = None):
    """
    Render just the title section without inputs (for use in other contexts)
    
    Args:
        tagline: Optional custom tagline, otherwise generates random one
    """
    if tagline is None:
        tagline = get_dashboard_tagline("stocks")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 5px; font-weight: 700;">
            📈 STONKS ANALYSIS
        </h1>
        <p style="font-size: 0.95rem; opacity: 0.95; font-style: italic;">
            {tagline}
        </p>
    </div>
    """, unsafe_allow_html=True)
