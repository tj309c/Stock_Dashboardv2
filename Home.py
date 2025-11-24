from app_logic import initialize_data_and_context
import streamlit as st
import google.generativeai as genai
import yfinance as yf
from datetime import datetime, timedelta
import altair as alt
import pandas as pd
import requests
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from global_sidebar import render_global_sidebar, apply_theme_css

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# GLOBAL SIDEBAR (Theme, AI Settings)
# ============================
sidebar_config = render_global_sidebar()
apply_theme_css(sidebar_config['theme'])

# --- GOOGLE AI CONFIG ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.session_state.google_ai_configured = True
except Exception as e:
    st.session_state.google_ai_configured = False
    st.error(f"Error configuring Google AI. Is your API key in .streamlit/secrets.toml? Error: {e}")

# --- SIDEBAR (Controls) ---

# Function to update URL query parameter when ticker input changes
def update_query_params_from_ticker_input():
    # Only update if the value in session_state is different from the current URL param
    if st.query_params.get('ticker') != st.session_state.ticker_input:
        st.query_params['ticker'] = st.session_state.ticker_input

# Initialize session_state.ticker_input only once per session
if 'ticker_input' not in st.session_state:
    # Get initial ticker from URL query param, or default to 'AAPL'
    st.session_state.ticker_input = st.query_params.get('ticker', 'AAPL')
    # After initialization, ensure the URL reflects the session_state.
    # This handles cases where user landed on the page without a ticker param
    # and we defaulted it, so the URL should now show 'AAPL'.
    if st.query_params.get('ticker') != st.session_state.ticker_input:
        st.query_params['ticker'] = st.session_state.ticker_input
else:
    # If 'ticker_input' is already in session_state, but the URL param has changed
    # (e.g., user manually edited URL, or navigated back/forward with a different param),
    # update session_state to reflect the URL.
    # This ensures the widget shows the URL's value on subsequent runs if URL changed externally.
    url_ticker = st.query_params.get('ticker')
    if url_ticker and url_ticker != st.session_state.ticker_input:
        st.session_state.ticker_input = url_ticker
        # We don't update st.query_params here, as the URL is the source of truth in this case.
        # The widget will be rendered with the updated st.session_state.ticker_input.

# Create the ticker input widget in the sidebar
# Its value is bound to st.session_state.ticker_input via 'key'
st.sidebar.text_input(
    "Enter Ticker Symbol",
    value=st.session_state.ticker_input,
    key="ticker_input", # This links the widget's value to st.session_state.ticker_input
    on_change=update_query_params_from_ticker_input # Callback to sync URL when input changes
)

# The 'ticker' variable used throughout the rest of the application
# should always refer to the value in st.session_state.ticker_input
ticker = st.session_state.ticker_input

# ============================
# HOME PAGE CONTENT
# ============================

st.title(f"Stock Analysis Dashboard")
st.subheader(f"Now analyzing: {ticker}")

# Show AI configuration status
if sidebar_config['enable_ai_features'] and sidebar_config['selected_ai_model']:
    from ai_model_config import get_model_info
    model_info = get_model_info(sidebar_config['selected_ai_model'])
    if model_info:
        st.success(f"AI Features Enabled - Using: {model_info.full_name}")
    else:
        st.success(f"AI Features Enabled - Using: {sidebar_config['selected_ai_model']}")
elif sidebar_config['enable_ai_features']:
    st.warning("AI Features enabled but no model selected or configured")
else:
    st.info("AI Features disabled - Enable in sidebar for AI-powered analysis")

st.info("Select a page from the sidebar to begin your analysis.")