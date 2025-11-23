import pandas as pd
import yfinance as yf
import streamlit as st
from typing import List, Dict, Any, Tuple, Optional
from app_context import AppContext # Import the central AppContext

# Optional import for technical indicators
try:
    from ta.trend import SMAIndicator, MACD, ADXIndicator
    from ta.momentum import RSIIndicator
    from ta.volatility import BollingerBands
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

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


def _add_technical_indicators(price_data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators to price data using the ta library.
    Falls back to basic indicators if ta is not available.
    """
    if price_data.empty:
        return price_data

    df = price_data.copy()

    if TA_AVAILABLE:
        # Add all technical indicators using the ta library
        # RSI
        rsi = RSIIndicator(close=df['Close'], window=14)
        df['RSI_14'] = rsi.rsi()

        # MACD
        macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD_12_26_9'] = macd.macd()
        df['MACDs_12_26_9'] = macd.macd_signal()
        df['MACDh_12_26_9'] = macd.macd_diff()

        # Simple Moving Averages
        sma50 = SMAIndicator(close=df['Close'], window=50)
        df['SMA50'] = sma50.sma_indicator()
        sma200 = SMAIndicator(close=df['Close'], window=200)
        df['SMA200'] = sma200.sma_indicator()

        # Bollinger Bands
        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BBU_20_2.0_2.0'] = bb.bollinger_hband()
        df['BBL_20_2.0_2.0'] = bb.bollinger_lband()
        df['BBM_20_2.0_2.0'] = bb.bollinger_mavg()

        # ADX
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX_14'] = adx.adx()
        df['DMP_14'] = adx.adx_pos()
        df['DMN_14'] = adx.adx_neg()
    else:
        # Fallback: Calculate basic indicators manually
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # Simple Moving Averages
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        df['SMA200'] = df['Close'].rolling(window=200).mean()

        # Basic MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD_12_26_9'] = exp1 - exp2
        df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
        df['MACDh_12_26_9'] = df['MACD_12_26_9'] - df['MACDs_12_26_9']

        # Bollinger Bands
        df['BBM_20_2.0_2.0'] = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        df['BBU_20_2.0_2.0'] = df['BBM_20_2.0_2.0'] + (std * 2)
        df['BBL_20_2.0_2.0'] = df['BBM_20_2.0_2.0'] - (std * 2)

        # Basic ADX (simplified)
        df['ADX_14'] = 25  # Default neutral value
        df['DMP_14'] = 0
        df['DMN_14'] = 0

    return df


@st.cache_data(ttl=3600, show_spinner="Fetching stock data...") # Cache for 1 hour
def _fetch_stock_data(_stock_object: Stock, light_load: bool) -> Dict[str, Any]:
    """
    Fetches all necessary raw data for a stock.
    Separates data fetching from data processing.
    """
    price_data = _stock_object.get_history(period='5y')

    # Add technical indicators to price data
    if not price_data.empty:
        price_data = _add_technical_indicators(price_data)

    data = {
        "info": _stock_object.get_info(),
        "price_data": price_data,
        "income_data": pd.DataFrame(),
        "balance_sheet_data": pd.DataFrame(),
        "cash_flow_data": pd.DataFrame(),
        "quarterly_income_data": pd.DataFrame(),
        "quarterly_balance_sheet": pd.DataFrame(),
        "quarterly_cash_flow": pd.DataFrame(),
        "news_data": []
    }

    if not light_load:
        data["income_data"] = _stock_object.get_financials()
        data["balance_sheet_data"] = _stock_object.get_balance_sheet()
        data["cash_flow_data"] = _stock_object.get_cash_flow()
        data["quarterly_income_data"] = _stock_object.get_quarterly_financials()
        data["quarterly_balance_sheet"] = _stock_object.get_quarterly_balance_sheet()
        data["quarterly_cash_flow"] = _stock_object.get_quarterly_cash_flow()
        data["news_data"] = _stock_object.get_news()

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
        # Get market price for light load
        light_market_price = 0.0
        if raw_data["info"].get('currentPrice'):
            light_market_price = float(raw_data["info"].get('currentPrice'))
        elif raw_data["info"].get('regularMarketPrice'):
            light_market_price = float(raw_data["info"].get('regularMarketPrice'))
        elif raw_data["info"].get('previousClose'):
            light_market_price = float(raw_data["info"].get('previousClose'))
        elif not raw_data["price_data"].empty and 'Close' in raw_data["price_data"].columns:
            light_market_price = float(raw_data["price_data"]["Close"].iloc[-1])

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
            market_price=light_market_price,
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

    # --- Get Market Price ---
    # Try multiple sources to get the most accurate current market price
    market_price = 0.0

    # Priority 1: Current price from info
    if raw_data["info"].get('currentPrice'):
        market_price = float(raw_data["info"].get('currentPrice'))
    # Priority 2: Regular market price from info
    elif raw_data["info"].get('regularMarketPrice'):
        market_price = float(raw_data["info"].get('regularMarketPrice'))
    # Priority 3: Previous close from info
    elif raw_data["info"].get('previousClose'):
        market_price = float(raw_data["info"].get('previousClose'))
    # Priority 4: Most recent closing price from price data
    elif not raw_data["price_data"].empty and 'Close' in raw_data["price_data"].columns:
        market_price = float(raw_data["price_data"]["Close"].iloc[-1])

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
        market_price=market_price,
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
            'dcf_intermediates', 'ddm_value', 'ddm_upside', 'nav_value', 'nav_upside',
            'ocf_final', 'capex_final', 'cash_final', 'debt_final', 'shares_final'
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
        # Missing required fields for AppContext
        'ocf_final': 0.0,
        'capex_final': 0.0,
        'cash_final': 0.0,
        'debt_final': 0.0,
        'shares_final': 0.0,
    }