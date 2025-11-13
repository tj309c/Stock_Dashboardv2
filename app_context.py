from dataclasses import dataclass
import pandas as pd
import yfinance as yf
from typing import Dict, Any, List

@dataclass
class AppContext:
    """
    A dataclass to hold all the shared data and state for the application.
    This avoids passing a large number of arguments to page-rendering functions.
    """
    # Core Data
    ticker_symbol: str
    stock_object: yf.Ticker
    info: Dict[str, Any]
    price_data: pd.DataFrame
    price_data_cached: pd.DataFrame
    income_data: pd.DataFrame
    balance_sheet_data: pd.DataFrame
    cash_flow_data: pd.DataFrame
    quarterly_income_data: pd.DataFrame
    quarterly_balance_sheet: pd.DataFrame
    quarterly_cash_flow: pd.DataFrame
    news_data: List[Dict[str, Any]]

    # Calculated Values
    market_price: float
    intrinsic_price_per_share: float
    dcf_intermediates: Dict[str, Any]
    bullish_signals: List[str]
    bearish_signals: List[str]
    ddm_value: float
    ddm_upside: float
    nav_value: float
    nav_upside: float

    # DCF Inputs
    fcf_input: float
    cash_input: float
    debt_input: float
    shares_input: float
    fcf_growth_rate: float
    discount_rate: float
    perpetual_growth_rate: float
    projection_years: int
    enable_two_stage: bool
    high_growth_years: int
    fade_years: int

    # Source Strings for Debugging
    fcf_source: str
    cash_source: str
    debt_source: str
    shares_source: str
    op_cash_flow_avg: float
    cap_ex_avg: float
    cash_yf: float
    total_debt_yf: float
    shares_yf: float
    ocf_source: str
    capex_source: str
    op_cash_flow_series: pd.Series
    cap_ex_series: pd.Series

    # Finalized DCF inputs after user overrides
    ocf_final: float
    capex_final: float
    cash_final: float
    debt_final: float
    shares_final: float