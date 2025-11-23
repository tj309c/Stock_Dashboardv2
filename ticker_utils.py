"""
Ticker Input Utilities - Reusable ticker input components with quick-pick functionality
"""
import streamlit as st
from typing import List


def render_ticker_input_with_quick_picks(
    global_ticker: str,
    session_key: str,
    label: str = "Analyze Ticker:",
    quick_picks: List[str] = None,
    show_indicator: bool = True
) -> str:
    """
    Renders a ticker input with quick-pick buttons for easy ticker switching.

    This creates a local ticker override that allows users to quickly switch tickers
    within a specific tab without changing the global ticker selection.

    Args:
        global_ticker: The global ticker from query params/sidebar
        session_key: Unique session state key for this tab's ticker override
        label: Label for the ticker input
        quick_picks: List of popular tickers for quick access (defaults to AAPL, TSLA, NVDA, SPY)
        show_indicator: Whether to show a visual indicator when override is active

    Returns:
        str: The active ticker (local override or global ticker)

    Example:
        ```python
        def render_price_technicals_tab(ticker):
            active_ticker = render_ticker_input_with_quick_picks(
                global_ticker=ticker,
                session_key="price_tech_ticker",
                label="📊 Analyze Ticker:",
                quick_picks=["AAPL", "TSLA", "NVDA", "SPY"]
            )

            # Use active_ticker for all operations in this tab
            render_advanced_chart(active_ticker, ...)
        ```
    """
    if quick_picks is None:
        quick_picks = ["AAPL", "TSLA", "NVDA", "SPY"]

    # Initialize session state for this tab's ticker if not present
    if session_key not in st.session_state:
        st.session_state[session_key] = global_ticker

    # Create layout: ticker input + quick-pick buttons
    col1, col2 = st.columns([3, 2])

    with col1:
        # Ticker input with validation
        ticker_input = st.text_input(
            label,
            value=st.session_state[session_key],
            key=f"{session_key}_input",
            max_chars=10,
            help="Enter a stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
        ).upper().strip()

        # Update session state if ticker changed
        if ticker_input and ticker_input != st.session_state[session_key]:
            st.session_state[session_key] = ticker_input
            st.rerun()

    with col2:
        st.caption("Quick picks:")
        # Create quick-pick buttons
        quick_cols = st.columns(len(quick_picks))

        for idx, quick_ticker in enumerate(quick_picks):
            with quick_cols[idx]:
                if st.button(
                    quick_ticker,
                    key=f"{session_key}_quick_{quick_ticker}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state[session_key] = quick_ticker
                    st.rerun()

    # Get the active ticker
    active_ticker = st.session_state[session_key]

    # Show visual indicator if viewing a different ticker than global
    if show_indicator and active_ticker != global_ticker:
        st.info(
            f"📍 Currently viewing **{active_ticker}** "
            f"(Global ticker: **{global_ticker}**)",
            icon="ℹ️"
        )

    return active_ticker


def reset_ticker_override(session_key: str):
    """
    Resets a ticker override to None, allowing the tab to fall back to the global ticker.

    Args:
        session_key: The session state key for the ticker override to reset
    """
    if session_key in st.session_state:
        del st.session_state[session_key]


def sync_ticker_to_global(ticker: str):
    """
    Syncs a ticker to the global query params.

    This is useful when you want to "promote" a local ticker override to become
    the global ticker for the entire app.

    Args:
        ticker: The ticker symbol to set as global
    """
    st.query_params['ticker'] = ticker
    if 'ticker_input' in st.session_state:
        st.session_state.ticker_input = ticker


def setup_sidebar_ticker_input(page_key: str = "default") -> str:
    """
    Setup ticker input in sidebar with URL synchronization for any page.
    This provides a consistent ticker input experience across all pages.

    Args:
        page_key: Unique key for this page (to avoid session state conflicts)

    Returns:
        str: Current ticker symbol

    Example:
        ```python
        def render_page():
            ticker = setup_sidebar_ticker_input("fundamental_analysis")
            # Use ticker for analysis...
        ```
    """
    # Function to update URL query parameter when ticker input changes
    def update_query_params():
        session_key = f"ticker_input_{page_key}"
        if st.query_params.get('ticker') != st.session_state[session_key]:
            st.query_params['ticker'] = st.session_state[session_key]

    # Session state key for this page
    session_key = f"ticker_input_{page_key}"

    # Initialize session_state only once per session
    if session_key not in st.session_state:
        # Get initial ticker from URL query param, or default to 'AAPL'
        st.session_state[session_key] = st.query_params.get('ticker', 'AAPL')
        # Ensure the URL reflects the session_state
        if st.query_params.get('ticker') != st.session_state[session_key]:
            st.query_params['ticker'] = st.session_state[session_key]
    else:
        # If URL param has changed externally, update session_state
        url_ticker = st.query_params.get('ticker')
        if url_ticker and url_ticker != st.session_state[session_key]:
            st.session_state[session_key] = url_ticker

    # Create the ticker input widget in the sidebar
    st.sidebar.text_input(
        "Enter Ticker Symbol",
        value=st.session_state[session_key],
        key=session_key,
        on_change=update_query_params,
        help="Enter a stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
    )

    # Return the current ticker
    return st.session_state[session_key]
