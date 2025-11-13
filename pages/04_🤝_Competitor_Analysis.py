import streamlit as st
import pandas as pd
from app_logic import initialize_data_and_context
from data_fetcher import get_competitor_data

def display_competitor_analysis(main_ticker_info: dict, competitor_info_list: list):
    """
    Renders the competitor analysis UI with a summary table and charts.
    """
    if not main_ticker_info or not isinstance(main_ticker_info, dict):
        st.error('Invalid main ticker information. Please ensure a valid main ticker is selected.')
        return

    all_data = [main_ticker_info] + competitor_info_list

    # --- 1. Build the Summary DataFrame ---
    metrics_to_compare = {
        "Symbol": "symbol", "Market Cap": "marketCap", "P/E Ratio": "trailingPE",
        "P/S Ratio": "priceToSalesTrailing12Months", "P/B Ratio": "priceToBook",
        "EV/EBITDA": "enterpriseToEbitda", "Revenue Growth (YoY)": "revenueGrowth",
        "Profit Margin": "profitMargins", "ROE": "returnOnEquity", "Dividend Yield": "dividendYield"
    }
    summary_data = [{display_name: info.get(key) for display_name, key in metrics_to_compare.items()} for info in all_data]
    df = pd.DataFrame(summary_data).set_index("Symbol")

    # --- 2. Display the Summary Table ---
    st.subheader("Key Metric Comparison")
    
    pe_max = df["P/E Ratio"].max() if not df["P/E Ratio"].empty and df["P/E Ratio"].max() > 0 else 30
    ps_max = df["P/S Ratio"].max() if not df["P/S Ratio"].empty and df["P/S Ratio"].max() > 0 else 5
    pb_max = df["P/B Ratio"].max() if not df["P/B Ratio"].empty and df["P/B Ratio"].max() > 0 else 5
    evebitda_max = df["EV/EBITDA"].max() if not df["EV/EBITDA"].empty and df["EV/EBITDA"].max() > 0 else 20
    revg_max = df["Revenue Growth (YoY)"].max() if not df["Revenue Growth (YoY)"].empty and df["Revenue Growth (YoY)"].max() > 0 else 0.5
    pm_max = df["Profit Margin"].max() if not df["Profit Margin"].empty and df["Profit Margin"].max() > 0 else 0.3
    roe_max = df["ROE"].max() if not df["ROE"].empty and df["ROE"].max() > 0 else 0.4
    div_max = df["Dividend Yield"].max() if not df["Dividend Yield"].empty and df["Dividend Yield"].max() > 0 else 0.05

    st.data_editor(
        df,
        column_config={
            "Market Cap": st.column_config.NumberColumn(format="$%d"),
            "P/E Ratio": st.column_config.BarChartColumn(y_min=0, y_max=pe_max),
            "P/S Ratio": st.column_config.BarChartColumn(y_min=0, y_max=ps_max),
            "P/B Ratio": st.column_config.BarChartColumn(y_min=0, y_max=pb_max),
            "EV/EBITDA": st.column_config.BarChartColumn(y_min=0, y_max=evebitda_max),
            "Revenue Growth (YoY)": st.column_config.BarChartColumn(y_min=0, y_max=revg_max, format="%.2f"),
            "Profit Margin": st.column_config.BarChartColumn(y_min=0, y_max=pm_max, format="%.2f"),
            "ROE": st.column_config.BarChartColumn(y_min=0, y_max=roe_max, format="%.2f"),
            "Dividend Yield": st.column_config.BarChartColumn(y_min=0, y_max=div_max, format="%.2f"),
        },
        use_container_width=True
    )

def render_page():
    """Main function to render the Competitor Analysis page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"🤝 Competitor Analysis for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
    if not ctx or not ctx.info:
        st.error("Could not load company data for the specified ticker. Please check the ticker symbol.")
        return

    # Get sector information
    sector = ctx.info.get('sector', 'Unknown')
    industry = ctx.info.get('industry', 'Unknown')

    st.write(f"**Sector:** {sector}")
    st.write(f"**Industry:** {industry}")

    # Get competitor tickers
    # You can customize this list based on the sector/industry
    competitor_tickers = st.text_input(
        "Enter competitor tickers (comma-separated)",
        value="",
        help="Example: MSFT,GOOGL,META"
    )

    if competitor_tickers:
        # Parse the competitor tickers
        competitor_list = [t.strip().upper() for t in competitor_tickers.split(',') if t.strip()]

        if competitor_list:
            with st.spinner("Fetching competitor data..."):
                # Fetch competitor data
                competitor_info_list = get_competitor_data(competitor_list)

                if competitor_info_list:
                    # Display the analysis
                    display_competitor_analysis(ctx.info, competitor_info_list)
                else:
                    st.warning("No valid competitor data could be retrieved.")
        else:
            st.info("Please enter at least one competitor ticker.")
    else:
        st.info("Enter competitor ticker symbols above to compare metrics.")

if __name__ == "__main__":
    render_page()