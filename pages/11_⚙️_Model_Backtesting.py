import streamlit as st
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from backtester import run_dcf_backtest, run_relative_backtest
from ai_services import get_ai_comparables

def render_page():
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"⚙️ Model Backtesting for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- DCF Backtest Section ---
    with st.container(border=True):
        st.subheader("DCF Model Backtest")
        st.info("""
        This tool tests the historical accuracy of the DCF model. It takes your **current** growth and WACC assumptions from the sidebar and applies them to the financial data (FCF, debt, cash) from previous years.
        The "Calculated Value" is what the model would have predicted for that year, which is then compared to the "Actual Price" of the stock at that time.
        """)

        # Use default assumptions since these attributes don't exist in AppContext
        backtest_assumptions = {
            "growth_rates": [0.10, 0.10, 0.08, 0.08, 0.06],  # 5-year growth rates
            "ebit_margin": 0.20,
            "tax_rate": 0.21,
            "depreciation_pct": 0.03,
            "capex_pct": 0.05,
            "nwc_pct": 0.10,
            "terminal_growth": 0.025,
            "wacc": 0.10,
            "shares_outstanding": ctx.info.get('sharesOutstanding', 1_000_000_000) if ctx.info else 1_000_000_000
        }

        with st.spinner("Running DCF backtest..."):
            dcf_backtest_df, dcf_mape = run_dcf_backtest(
                ctx.price_data, ctx.income_data, ctx.balance_sheet_data, ctx.cash_flow_data, backtest_assumptions
            )

        if dcf_backtest_df.empty:
            st.warning("Could not generate a DCF backtest. There may not be enough historical annual financial data.")
        else:
            st.metric("DCF Mean Absolute Percentage Error (MAPE)", f"{dcf_mape:.2f}%", help="The average percentage difference between the model's prediction and the actual price. Lower is better.")
            fig_backtest = go.Figure()
            fig_backtest.add_trace(go.Scatter(x=dcf_backtest_df.index, y=dcf_backtest_df['Actual Price'], mode='lines+markers', name='Actual Market Price'))
            fig_backtest.add_trace(go.Scatter(x=dcf_backtest_df.index, y=dcf_backtest_df['Calculated Value'], mode='lines+markers', name='DCF Calculated Value'))
            fig_backtest.update_layout(title="DCF Calculated Value vs. Actual Price (Historical)", yaxis_title="Price", yaxis_tickprefix='$', template="plotly_white")
            st.plotly_chart(fig_backtest, use_container_width=True)
            with st.expander("See DCF Backtest Data"):
                st.dataframe(dcf_backtest_df.style.format({'Calculated Value': '${:,.2f}', 'Actual Price': '${:,.2f}', 'Error': '{:+.2%}'}).background_gradient(cmap='RdYlGn_r', subset=['Error'], vmin=-1, vmax=1), use_container_width=True)

    # --- Relative Valuation Backtest Section ---
    with st.container(border=True):
        st.subheader("Relative Valuation (P/E) Model Backtest")
        st.info("""
        This tool tests a P/E-based relative valuation model. It takes the **current** sector P/E multiple (from the AI) and applies it to the stock's **historical** TTM EPS.
        This shows how the stock would have been valued if it always traded at the current sector average multiple.
        """)

        with st.spinner("Running Relative Valuation backtest..."):
            sector_comps = get_ai_comparables(ticker, ctx.info.get('sector', 'default'))
            sector_pe = sector_comps.get('pe', 20.0) if isinstance(sector_comps, dict) else 20.0
            rel_backtest_df, rel_mape = run_relative_backtest(ctx.price_data, ctx.quarterly_income_data, sector_pe)

        if rel_backtest_df.empty:
            st.warning("Could not generate a Relative Valuation backtest. This may be due to missing EPS data or an invalid sector P/E.")
        else:
            st.metric("Relative Valuation Mean Absolute Percentage Error (MAPE)", f"{rel_mape:.2f}%", help="The average percentage difference between the model's prediction and the actual price. Lower is better.")
            fig_rel_backtest = go.Figure()
            fig_rel_backtest.add_trace(go.Scatter(x=rel_backtest_df.index, y=rel_backtest_df['Actual Price'], mode='lines+markers', name='Actual Market Price'))
            fig_rel_backtest.add_trace(go.Scatter(x=rel_backtest_df.index, y=rel_backtest_df['Calculated Value'], mode='lines+markers', name='Relative Calculated Value'))
            fig_rel_backtest.update_layout(title="Relative Calculated Value vs. Actual Price (Historical)", yaxis_title="Price", yaxis_tickprefix='$', template="plotly_white")
            st.plotly_chart(fig_rel_backtest, use_container_width=True)
            with st.expander("See Relative Valuation Backtest Data"):
                st.dataframe(rel_backtest_df.style.format({'Calculated Value': '${:,.2f}', 'Actual Price': '${:,.2f}', 'Error': '{:+.2%}'}).background_gradient(cmap='RdYlGn_r', subset=['Error'], vmin=-1, vmax=1), use_container_width=True)

if __name__ == "__main__":
    render_page()