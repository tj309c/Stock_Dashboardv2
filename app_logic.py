import pandas as pd
import yfinance as yf
import streamlit as st
from typing import List, Dict, Any, Tuple, Optional
from app_context import AppContext # Import the central AppContext

# --- Helper functions ---
def get_technical_signals(price_data: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Calculates simple technical signals based on price data.
    """
    bullish_signals = []
    bearish_signals = []

    if price_data.empty:
        return [], []

    # Example: Simple Moving Average (SMA) Crossover
    # Ensure 'Close' column exists
    if 'Close' in price_data.columns:
        price_data['MA20'] = price_data['Close'].rolling(window=20).mean()
        price_data['MA50'] = price_data['Close'].rolling(window=50).mean()

        # Check for crossover on the most recent day
        if len(price_data) >= 2:
            ma20_current = price_data['MA20'].iloc[-1]
            ma50_current = price_data['MA50'].iloc[-1]
            ma20_prev = price_data['MA20'].iloc[-2]
            ma50_prev = price_data['MA50'].iloc[-2]

            if ma20_current > ma50_current and ma20_prev <= ma50_prev:
                bullish_signals.append("MA20 crossed above MA50 (Bullish Crossover)")
            elif ma20_current < ma50_current and ma20_prev >= ma50_prev:
                bearish_signals.append("MA20 crossed below MA50 (Bearish Crossover)")

    # Add more signals as needed (e.g., RSI, MACD, etc.)

    return bullish_signals, bearish_signals


# --- Stock Class ---
class Stock:
    def __init__(self, ticker_symbol: str):
        self._ticker = yf.Ticker(ticker_symbol)

    def get_info(self) -> Dict[str, Any]:
        try:
            return self._ticker.info
        except Exception:
            return {}  # Return empty dict on error

    def get_financials(self) -> pd.DataFrame:
        try:
            return self._ticker.financials
        except Exception:
            return pd.DataFrame()  # Return empty DataFrame on error

    def get_balance_sheet(self) -> pd.DataFrame:
        try:
            return self._ticker.balance_sheet
        except Exception:
            return pd.DataFrame()

    def get_cash_flow(self) -> pd.DataFrame:
        try:
            # FIX: The correct yfinance property is 'cash_flow' with an underscore.
            return self._ticker.cash_flow
        except Exception:
            return pd.DataFrame()

    def get_quarterly_financials(self) -> pd.DataFrame:
        try:
            return self._ticker.quarterly_financials
        except Exception:
            return pd.DataFrame()

    def get_quarterly_balance_sheet(self) -> pd.DataFrame:
        try:
            return self._ticker.quarterly_balance_sheet
        except Exception:
            return pd.DataFrame()

    def get_quarterly_cash_flow(self) -> pd.DataFrame:
        try:
            return self._ticker.quarterly_cash_flow
        except Exception:
            return pd.DataFrame()

    def get_news(self) -> List[Dict[str, Any]]:
        try:
            return self._ticker.news
        except Exception:
            return []

    def get_history(self, period: str = '5y') -> pd.DataFrame:
        try:
            return self._ticker.history(period=period)
        except Exception:
            return pd.DataFrame()  # Return empty DataFrame on error


@st.cache_data(ttl=900, show_spinner="Fetching stock data...") # Cache for 15 minutes
def _fetch_stock_data(stock_object: Stock, light_load: bool) -> Dict[str, Any]:
    """
    Fetches all necessary raw data for a stock.
    Separates data fetching from data processing.
    """
    data = {
        "info": stock_object.get_info(),
        "price_data": stock_object.get_history(period='5y'),
        "income_data": pd.DataFrame(),
        "balance_sheet_data": pd.DataFrame(),
        "cash_flow_data": pd.DataFrame(),
        "quarterly_income_data": pd.DataFrame(),
        "quarterly_balance_sheet": pd.DataFrame(),
        "quarterly_cash_flow": pd.DataFrame(),
        "news_data": []
    }

    if not light_load:
        data["income_data"] = stock_object.get_financials()
        data["balance_sheet_data"] = stock_object.get_balance_sheet()
        data["cash_flow_data"] = stock_object.get_cash_flow()
        data["quarterly_income_data"] = stock_object.get_quarterly_financials()
        data["quarterly_balance_sheet"] = stock_object.get_quarterly_balance_sheet()
        data["quarterly_cash_flow"] = stock_object.get_quarterly_cash_flow()
        data["news_data"] = stock_object.get_news()

    return data


def initialize_data_and_context(ticker_symbol: str, light_load: bool = False) -> AppContext:
    """
    Initializes and returns an AppContext object with relevant financial data.
    If light_load is True, it performs a minimal data load for faster startup
    without full financial statement analysis.
    """
    # --- 1. Data Fetching ---
    stock_object = Stock(ticker_symbol)
    raw_data = _fetch_stock_data(stock_object, light_load)

    # --- CRITICAL FIX: Validate Ticker ---
    # If 'info' is empty, it means the ticker is invalid or no data was returned.
    # Stop execution early to prevent errors and provide clear feedback.
    if not raw_data.get("info"):
        st.error(f"Could not retrieve any data for ticker '{ticker_symbol}'. It may be an invalid symbol.")
        return None # Return None to signal failure to the calling page

    # --- 2. Initial Data Processing ---
    # Calculate technical signals, regardless of light_load.
    bullish_signals, bearish_signals = get_technical_signals(raw_data["price_data"])

    # --- Graceful exit for light_load where financial data is absent ---
    if light_load:
        # CRITICAL FIX: The previous implementation using dictionary unpacking (**raw_data, **defaults)
        # caused a TypeError because some keys existed in both dictionaries, leading to duplicate
        # keyword arguments. This fully explicit initialization is safer and guarantees correctness.
        defaults = _get_default_app_context_fields()
        return AppContext(
            # Core Data
            ticker_symbol=ticker_symbol,
            stock_object=stock_object,
            info=raw_data["info"],
            price_data=raw_data["price_data"],
            price_data_cached=defaults['price_data_cached'],
            income_data=raw_data["income_data"],
            balance_sheet_data=raw_data["balance_sheet_data"],
            cash_flow_data=raw_data["cash_flow_data"],
            quarterly_income_data=raw_data["quarterly_income_data"],
            quarterly_balance_sheet=raw_data["quarterly_balance_sheet"],
            quarterly_cash_flow=raw_data["quarterly_cash_flow"],
            news_data=raw_data["news_data"],
            # Calculated Values
            market_price=defaults['market_price'],
            intrinsic_price_per_share=defaults['intrinsic_price_per_share'],
            dcf_intermediates=defaults['dcf_intermediates'],
            bullish_signals=bullish_signals,
            bearish_signals=bearish_signals,
            ddm_value=defaults['ddm_value'],
            ddm_upside=defaults['ddm_upside'],
            nav_value=defaults['nav_value'],
            nav_upside=defaults['nav_upside'],
            # DCF Inputs and other fields are populated from defaults
            **{k: v for k, v in defaults.items() if k not in [
                'price_data_cached', 'market_price', 'intrinsic_price_per_share',
                'dcf_intermediates', 'ddm_value', 'ddm_upside', 'nav_value', 'nav_upside'
            ]}
        )

    # --- Full data load for detailed analysis ---
    # --- 3. Derive default YFinance values for DCF inputs ---
    # These are placeholders; in a real application, robust parsing of
    # income_data, balance_sheet_data, cash_flow_data would happen here.

    yf_ocf_value = 0.0
    if not raw_data["cash_flow_data"].empty and 'Operating Cash Flow' in raw_data["cash_flow_data"].index:
        yf_ocf_value = raw_data["cash_flow_data"].loc['Operating Cash Flow'].iloc[0] if not raw_data["cash_flow_data"].loc['Operating Cash Flow'].empty else 0.0

    yf_capex_value = 0.0
    # Capital Expenditure often appears as a negative number in cash flow.
    if not raw_data["cash_flow_data"].empty and 'Capital Expenditure' in raw_data["cash_flow_data"].index:
        yf_capex_value = raw_data["cash_flow_data"].loc['Capital Expenditure'].iloc[0] if not raw_data["cash_flow_data"].loc['Capital Expenditure'].empty else 0.0

    yf_cash_value = 0.0
    if not raw_data["balance_sheet_data"].empty and 'Cash And Cash Equivalents' in raw_data["balance_sheet_data"].index:
        yf_cash_value = raw_data["balance_sheet_data"].loc['Cash And Cash Equivalents'].iloc[0] if not raw_data["balance_sheet_data"].loc['Cash And Cash Equivalents'].empty else 0.0

    yf_debt_value = 0.0
    # 'Total Debt' might not be directly available, might need to sum 'Long Term Debt' and 'Short Term Debt'
    if not raw_data["balance_sheet_data"].empty and 'Total Debt' in raw_data["balance_sheet_data"].index:
        yf_debt_value = raw_data["balance_sheet_data"].loc['Total Debt'].iloc[0] if not raw_data["balance_sheet_data"].loc['Total Debt'].empty else 0.0
    elif not raw_data["balance_sheet_data"].empty: # Fallback if 'Total Debt' isn't direct
        long_term_debt = raw_data["balance_sheet_data"].loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in raw_data["balance_sheet_data"].index else 0.0
        # FIX: Corrected a syntax error (a stray ']').
        short_term_debt = raw_data["balance_sheet_data"].loc['Short Term Debt'].iloc[0] if 'Short Term Debt' in raw_data["balance_sheet_data"].index else 0.0
        yf_debt_value = long_term_debt + short_term_debt

    yf_shares_value = raw_data["info"].get('sharesOutstanding', 0.0)

    # --- 4. Apply User Overrides for DCF inputs ---
    # Fix: Changed `!= 0` to `is not None` to allow explicit `0.0` as an override.
    # We use `.get()` for robustness in case `override_X` isn't set in session state.
    # This assumes the Streamlit UI initializes `override_X` to `None` if no user input
    # has been provided, or to a numeric value if it has.
    ocf_final = st.session_state.get('override_ocf') if st.session_state.get('override_ocf') is not None else yf_ocf_value
    capex_final = st.session_state.get('override_capex') if st.session_state.get('override_capex') is not None else yf_capex_value
    cash_final = st.session_state.get('override_cash') if st.session_state.get('override_cash') is not None else yf_cash_value
    debt_final = st.session_state.get('override_debt') if st.session_state.get('override_debt') is not None else yf_debt_value
    shares_final = st.session_state.get('override_shares') if st.session_state.get('override_shares') is not None else yf_shares_value

    # --- 5. Assemble the final AppContext ---
    # CRITICAL FIX: The previous implementation using dictionary unpacking (**raw_data, **defaults)
    # caused a TypeError because of duplicate keyword arguments. This explicit initialization
    # is safer, clearer, and guarantees the AppContext is created correctly.
    defaults = _get_default_app_context_fields()
    return AppContext(
        # Core Data
        ticker_symbol=ticker_symbol,
        stock_object=stock_object,
        info=raw_data["info"],
        price_data=raw_data["price_data"],
        price_data_cached=defaults['price_data_cached'],
        income_data=raw_data["income_data"],
        balance_sheet_data=raw_data["balance_sheet_data"],
        cash_flow_data=raw_data["cash_flow_data"],
        quarterly_income_data=raw_data["quarterly_income_data"],
        quarterly_balance_sheet=raw_data["quarterly_balance_sheet"],
        quarterly_cash_flow=raw_data["quarterly_cash_flow"],
        news_data=raw_data["news_data"],
        # Calculated Values
        market_price=defaults['market_price'],
        intrinsic_price_per_share=defaults['intrinsic_price_per_share'],
        dcf_intermediates=defaults['dcf_intermediates'],
        bullish_signals=bullish_signals,
        bearish_signals=bearish_signals,
        ddm_value=defaults['ddm_value'],
        ddm_upside=defaults['ddm_upside'],
        nav_value=defaults['nav_value'],
        nav_upside=defaults['nav_upside'],
        # Finalized values after overrides
        ocf_final=ocf_final,
        capex_final=capex_final,
        cash_final=cash_final,
        debt_final=debt_final,
        shares_final=shares_final,
        # Populate all other fields with their default values
        **{k: v for k, v in defaults.items() if k not in [
            'price_data_cached', 'market_price', 'intrinsic_price_per_share',
            'dcf_intermediates', 'ddm_value', 'ddm_upside', 'nav_value', 'nav_upside'
        ]}
    )

def _get_default_app_context_fields():
    """
    Helper to provide default values for AppContext fields not covered
    in the light_load path to prevent initialization errors.
    """
    return {
        'price_data_cached': pd.DataFrame(),
        'market_price': 0.0,
        'intrinsic_price_per_share': 0.0,
        'dcf_intermediates': {},
        'ddm_value': 0.0,
        'ddm_upside': 0.0,
        'nav_value': 0.0,
        'nav_upside': 0.0,
        'fcf_input': 0.0,
        'cash_input': 0.0,
        'debt_input': 0.0,
        'shares_input': 0.0,
        'fcf_growth_rate': 0.0,
        'discount_rate': 0.0,
        'perpetual_growth_rate': 0.0,
        'projection_years': 0,
        'enable_two_stage': False,
        'high_growth_years': 0,
        'fade_years': 0,
        'fcf_source': '', 'cash_source': '', 'debt_source': '', 'shares_source': '',
        'op_cash_flow_avg': 0.0, 'cap_ex_avg': 0.0, 'cash_yf': 0.0, 'total_debt_yf': 0.0,
        'shares_yf': 0.0, 'ocf_source': '', 'capex_source': '',
        'op_cash_flow_series': pd.Series(dtype=float), 'cap_ex_series': pd.Series(dtype=float),
    }