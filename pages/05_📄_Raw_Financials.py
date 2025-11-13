import streamlit as st
import pandas as pd
import numpy as np

# Import from app_logic which has the full initialize_data_and_context implementation
from app_logic import initialize_data_and_context 

def display_financial_statement(title: str, dataframe: pd.DataFrame, period_type: str, currency_format: str):
    """
    Displays a financial statement DataFrame in a Streamlit app.

    Args:
        title (str): The subheader title for the statement.
        dataframe (pd.DataFrame): The financial data to display.
        period_type (str): 'Annual' or 'Quarterly' to determine column formatting.
        currency_format (str): The format string for currency values.
    """
    if dataframe.empty:
        st.info('No data available for this statement.')
        return
    st.subheader(title)
    df = dataframe.copy()
    if period_type == 'Annual':
        df.columns = df.columns.strftime('%Y')
    elif period_type == 'Quarterly':
        df.columns = df.columns.to_period('Q').strftime('Q%q %Y')
    
    numeric_cols = df.select_dtypes(include=np.number).columns
    formatters = {col: currency_format for col in numeric_cols}
    st.dataframe(df.style.format(formatters, na_rep="-"), use_container_width=True)

 
def render_page():
    """Main function to render the Raw Financials page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"📄 Raw Financials for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
    view_type = st.radio("Select View", ["Annual", "Quarterly"], horizontal=True, label_visibility="collapsed")
    
    # Check if context was successfully initialized and data is available
    if not ctx or ctx.income_data is None or ctx.income_data.empty:
        st.error("Could not load financial data for the specified ticker. Please check the ticker symbol.")
        return

    # Dynamically select the correct financial statement data based on view_type
    # Use the correct attribute names from app_logic's AppContext
    balance_sheet_data = ctx.balance_sheet_data if view_type == 'Annual' else ctx.quarterly_balance_sheet
    income_statement_data = ctx.income_data if view_type == 'Annual' else ctx.quarterly_income_data
    cash_flow_data = ctx.cash_flow_data if view_type == 'Annual' else ctx.quarterly_cash_flow

    # Display all three financial statements
    display_financial_statement("Balance Sheet", balance_sheet_data, view_type, "${:,.0f}")
    display_financial_statement("Income Statement", income_statement_data, view_type, "${:,.0f}")
    display_financial_statement("Cash Flow Statement", cash_flow_data, view_type, "${:,.0f}")

if __name__ == "__main__":
    render_page()