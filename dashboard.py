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

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME (Dark/Light Mode) ---
# Function to get current theme
def get_theme():
    # Attempt to read theme from query parameters first
    if 'theme' in st.query_params:
        return st.query_params['theme']
    # If not in query params, check session state
    if 'theme' in st.session_state:
        return st.session_state['theme']
    # Default to light if not set anywhere
    return "light"

# Set theme based on initial load or user selection
if 'theme' not in st.session_state:
    st.session_state.theme = get_theme()

# Toggle button
if st.sidebar.button(f"Switch to {'Dark' if st.session_state.theme == 'light' else 'Light'} Theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.query_params['theme'] = st.session_state.theme # Update URL
    st.rerun() # Rerun to apply theme immediately

# CSS for styling based on theme
if st.session_state.theme == "dark":
    dark_theme_css = """
    <style>
    :root {
        --primary-color: #6C63FF; /* Purple-blue for highlights */
        --background-color: #1a1a2e; /* Dark background */
        --secondary-background-color: #16213e; /* Slightly lighter dark for components */
        --text-color: #e0e0e0; /* Light gray text */
        --border-color: #0f3460; /* Darker blue for borders */
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
    /* Sidebar adjustments for dark theme */
    .st-emotion-cache-1pxazr-0 > div { /* Target the sidebar background */
        background-color: #0f1626; /* Even darker sidebar */
    }
    /* Specific styling for the AI response box */
    .ai-response-box {
        background-color: #0f3460; /* Dark blue for AI box */
        border-left: 5px solid #6C63FF; /* Highlight with primary color */
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

/* Metric Component - Desktop */
[data-testid="stMetric"] {
    background-color: #F8F9FA;
    border: 1px solid #DDD;
    border-radius: 5px;
    padding: 10px;
}

/* --- Mobile-Specific Adjustments --- */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem;
    }
    h2 {
        font-size: 1.5rem;
    }
    /* Make metrics even more compact on mobile */
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
st.title(f"Stock Analysis Dashboard")
st.subheader(f"Now analyzing: {ticker}")
st.info("Select a page from the sidebar to begin your analysis.")