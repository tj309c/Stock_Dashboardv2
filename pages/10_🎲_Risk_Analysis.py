import streamlit as st
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from technical_analysis import calculate_risk_metrics

def render_page():
    """Main function to render the Risk Analysis page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"🎲 Risk Analysis for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
    st.write("This page analyzes the stock's volatility and risk-adjusted returns relative to the S&P 500 (`^GSPC`).")
    
    market_ticker = st.text_input("Market Index Ticker", "^GSPC", help="Enter the ticker for the market index to compare against (e.g., ^GSPC for S&P 500, ^FTSE for FTSE 100).")

    with st.spinner("Calculating risk metrics..."):
        beta, sharpe, sortino, rolling_beta, rolling_volatility, error = calculate_risk_metrics(
            ctx.price_data, market_ticker=market_ticker
        )

    if error:
        st.error(f"Could not calculate risk metrics: {error}")
    else:
        st.subheader("Key Risk Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Beta", f"{beta:.2f}", help="Measures volatility relative to the market. > 1 means more volatile; < 1 means less volatile.")
        col2.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Measures risk-adjusted return (using total volatility). Higher is better.")
        col3.metric("Sortino Ratio", f"{sortino:.2f}", help="Similar to Sharpe, but only considers downside volatility. Higher is better.")

        st.subheader("Interpretation")
        if beta > 1.2: st.warning(f"**High Beta ({beta:.2f}):** This stock is significantly more volatile than the overall market.")
        elif beta < 0.8: st.success(f"**Low Beta ({beta:.2f}):** This stock is less volatile than the overall market.")
        else: st.info(f"**Neutral Beta ({beta:.2f}):** This stock's volatility is similar to the overall market.")

        st.info(f"A Sharpe Ratio of **{sharpe:.2f}** and Sortino Ratio of **{sortino:.2f}** suggest how effectively the stock has generated returns for the amount of risk taken. Generally, ratios above 1.0 are considered good.")

        st.divider()

        st.subheader("Rolling 1-Year Beta")
        if rolling_beta is not None and not rolling_beta.empty:
            fig_beta = go.Figure()
            fig_beta.add_trace(go.Scatter(x=rolling_beta.index, y=rolling_beta, mode='lines', name='Rolling Beta'))
            fig_beta.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Market Volatility", annotation_position="bottom right")
            fig_beta.update_layout(title_text="Stock Volatility vs. Market Over Time", yaxis_title="Beta", template="plotly_white")
            st.plotly_chart(fig_beta, use_container_width=True)
        else:
            st.warning("Could not generate rolling beta chart due to insufficient data.")
        
        st.subheader("Rolling 90-Day Volatility")
        if rolling_volatility is not None and not rolling_volatility.empty:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(x=rolling_volatility.index, y=rolling_volatility, mode='lines', name='Rolling Volatility', line=dict(color='purple')))
            fig_vol.update_layout(
                title_text="Stock's Annualized Volatility Over Time", 
                yaxis_title="Annualized Volatility",
                yaxis_tickformat='.0%',
                template="plotly_white"
            )
            st.plotly_chart(fig_vol, use_container_width=True)

if __name__ == "__main__":
    render_page()