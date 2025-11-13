import streamlit as st
import datetime

# Import from app_logic which has the real implementation
from app_logic import initialize_data_and_context

# --- Page Rendering Logic ---
def render_page():
    # --- Get Ticker from Query Params ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"🔬 Fundamental Deep Dive for {ticker}")

    context = initialize_data_and_context(ticker)

    # Robustly handle cases where context or context.info might be None
    # This prevents AttributeErrors when trying to access context.info.get()
    info = context.info if context and context.info else {}

    st.subheader(f"Key Metrics for {ticker}")

    if not info:
        st.warning(f"No fundamental data found for ticker '{ticker}'. "
                   "Please try 'MSFT' or 'GOOG' for sample data.")
        return # Stop rendering further metrics if no data

    # Apply robust checks for None values before formatting.
    # This prevents TypeError if a metric is None.

    # Trailing P/E Ratio (example of original problematic line if pe_ratio was None)
    # pe_ratio = info.get('trailingPE')
    # st.write(f"Trailing P/E: {pe_ratio:.2f}") # This would cause TypeError if pe_ratio is None

    # Corrected usage pattern:
    pe_ratio = info.get('trailingPE')
    pe_ratio_display = f"{pe_ratio:.2f}" if pe_ratio is not None else 'N/A'
    st.write(f"Trailing P/E: {pe_ratio_display}")

    forward_pe = info.get('forwardPE')
    forward_pe_display = f"{forward_pe:.2f}" if forward_pe is not None else 'N/A'
    st.write(f"Forward P/E: {forward_pe_display}")

    market_cap = info.get('marketCap')
    market_cap_display = f"${market_cap:,.0f}" if market_cap is not None else 'N/A'
    st.write(f"Market Cap: {market_cap_display}")

    enterprise_value = info.get('enterpriseValue')
    enterprise_value_display = f"${enterprise_value:,.0f}" if enterprise_value is not None else 'N/A'
    st.write(f"Enterprise Value: {enterprise_value_display}")

    price_to_sales = info.get('priceToSalesTrailing12Months')
    price_to_sales_display = f"{price_to_sales:.2f}" if price_to_sales is not None else 'N/A'
    st.write(f"Price to Sales (TTM): {price_to_sales_display}")

    forward_ps = info.get('forwardPS')
    forward_ps_display = f"{forward_ps:.2f}" if forward_ps is not None else 'N/A'
    st.write(f"Forward P/S: {forward_ps_display}")

    enterprise_to_revenue = info.get('enterpriseToRevenue')
    enterprise_to_revenue_display = f"{enterprise_to_revenue:.2f}" if enterprise_to_revenue is not None else 'N/A'
    st.write(f"Enterprise to Revenue: {enterprise_to_revenue_display}")

    revenue_growth = info.get('revenueGrowth')
    revenue_growth_display = f"{revenue_growth:.2%}" if revenue_growth is not None else 'N/A'
    st.write(f"Revenue Growth: {revenue_growth_display}")

    book_value = info.get('bookValue')
    book_value_display = f"${book_value:.2f}" if book_value is not None else 'N/A'
    st.write(f"Book Value: {book_value_display}")

    enterprise_to_ebitda = info.get('enterpriseToEbitda')
    enterprise_to_ebitda_display = f"{enterprise_to_ebitda:.2f}" if enterprise_to_ebitda is not None else 'N/A'
    st.write(f"Enterprise to EBITDA: {enterprise_to_ebitda_display}")

    gross_margins = info.get('grossMargins')
    gross_margins_display = f"{gross_margins:.2%}" if gross_margins is not None else 'N/A'
    st.write(f"Gross Margins: {gross_margins_display}")

    profit_margins = info.get('profitMargins')
    profit_margins_display = f"{profit_margins:.2%}" if profit_margins is not None else 'N/A'
    st.write(f"Profit Margins: {profit_margins_display}")

    operating_margins = info.get('operatingMargins')
    operating_margins_display = f"{operating_margins:.2%}" if operating_margins is not None else 'N/A'
    st.write(f"Operating Margins: {operating_margins_display}")

    return_on_assets = info.get('returnOnAssets')
    return_on_assets_display = f"{return_on_assets:.2%}" if return_on_assets is not None else 'N/A'
    st.write(f"Return on Assets: {return_on_assets_display}")

    return_on_equity = info.get('returnOnEquity')
    return_on_equity_display = f"{return_on_equity:.2%}" if return_on_equity is not None else 'N/A'
    st.write(f"Return on Equity: {return_on_equity_display}")

    dividend_yield = info.get('dividendYield')
    dividend_yield_display = f"{dividend_yield:.2%}" if dividend_yield is not None else 'N/A'
    st.write(f"Dividend Yield: {dividend_yield_display}")

    # Handle earnings timestamp separately as it requires date formatting
    earnings_timestamp = info.get('earningsTimestamp')
    if earnings_timestamp is not None:
        earnings_date = datetime.datetime.fromtimestamp(earnings_timestamp).strftime('%Y-%m-%d')
    else:
        earnings_date = 'N/A'
    st.write(f"Last Earnings Date: {earnings_date}")

# This ensures render_page is called when the script is run directly (e.g., by Streamlit)
if __name__ == "__main__":
    render_page()