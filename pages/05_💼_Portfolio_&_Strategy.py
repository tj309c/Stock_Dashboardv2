import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from portfolio_optimizer import run_portfolio_optimization
from app_logic import initialize_data_and_context
from backtester import run_dcf_backtest, run_relative_backtest
from ai_services import get_ai_comparables

def render_page():
    """Consolidated Portfolio & Strategy Tools Dashboard"""
    st.title("💼 Portfolio & Strategy Tools")

    # Create tabs for the two sections
    tab1, tab2 = st.tabs([
        "📊 Portfolio Optimization",
        "⚙️ Strategy Backtesting"
    ])

    with tab1:
        render_portfolio_optimization_tab()

    with tab2:
        render_strategy_backtesting_tab()


def render_portfolio_optimization_tab():
    """Portfolio optimization using Modern Portfolio Theory"""
    st.subheader("Portfolio Optimization (Modern Portfolio Theory)")
    st.write("This tool analyzes a portfolio of 2-5 stocks to find the optimal weighting for maximum risk-adjusted return (Sharpe Ratio).")

    tickers_input = st.text_input("Enter 2-5 Tickers (comma-separated)", "AAPL,MSFT,GOOG,AMZN")

    if st.button("Optimize Portfolio"):
        with st.spinner("Fetching 3 years of portfolio data and running 10,000 simulations..."):
            opt_results = run_portfolio_optimization(tickers_input)

            if opt_results:
                results_df, max_sharpe_stats, max_sharpe_weights, min_vol_stats, min_vol_weights, tickers = opt_results

                st.subheader("Optimal Portfolios")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 🎯 Max Sharpe Ratio (Best Risk vs. Reward)")

                    weights_df_sharpe = pd.DataFrame({'Ticker': tickers, 'Weight': max_sharpe_weights})
                    weights_df_sharpe = weights_df_sharpe[weights_df_sharpe['Weight'] > 0.001]
                    fig_sharpe = go.Figure(data=[go.Pie(labels=weights_df_sharpe['Ticker'], values=weights_df_sharpe['Weight'], hole=.3)])
                    fig_sharpe.update_layout(
                        title_text='Asset Allocation',
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_sharpe, use_container_width=True)

                    st.metric("Expected Return", f"{max_sharpe_stats['Return'] * 100:.2f}%")
                    st.metric("Volatility", f"{max_sharpe_stats['Volatility'] * 100:.2f}%")
                    st.metric("Sharpe Ratio", f"{max_sharpe_stats['Sharpe']:.2f}")

                with col2:
                    st.markdown("#### 🛡️ Min Volatility (Lowest Risk)")

                    weights_df_vol = pd.DataFrame({'Ticker': tickers, 'Weight': min_vol_weights})
                    weights_df_vol = weights_df_vol[weights_df_vol['Weight'] > 0.001]
                    fig_vol = go.Figure(data=[go.Pie(labels=weights_df_vol['Ticker'], values=weights_df_vol['Weight'], hole=.3)])
                    fig_vol.update_layout(
                        title_text='Asset Allocation',
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)

                    st.metric("Expected Return", f"{min_vol_stats['Return'] * 100:.2f}%")
                    st.metric("Volatility", f"{min_vol_stats['Volatility'] * 100:.2f}%")
                    st.metric("Sharpe Ratio", f"{min_vol_stats['Sharpe']:.2f}")

                # Show efficient frontier
                st.subheader("Efficient Frontier")
                fig_frontier = go.Figure()
                fig_frontier.add_trace(go.Scatter(
                    x=results_df['Volatility'],
                    y=results_df['Return'],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=results_df['Sharpe'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Sharpe Ratio")
                    ),
                    name='Portfolios'
                ))
                # Highlight optimal portfolios
                fig_frontier.add_trace(go.Scatter(
                    x=[max_sharpe_stats['Volatility']],
                    y=[max_sharpe_stats['Return']],
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='star'),
                    name='Max Sharpe'
                ))
                fig_frontier.add_trace(go.Scatter(
                    x=[min_vol_stats['Volatility']],
                    y=[min_vol_stats['Return']],
                    mode='markers',
                    marker=dict(size=15, color='green', symbol='star'),
                    name='Min Volatility'
                ))
                fig_frontier.update_layout(
                    title='Efficient Frontier',
                    xaxis_title='Volatility (Risk)',
                    yaxis_title='Expected Return',
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig_frontier, use_container_width=True)
            else:
                st.error("Could not optimize portfolio. Check tickers and try again.")


def render_strategy_backtesting_tab():
    """Strategy backtesting tools"""
    ticker = st.query_params.get("ticker", "AAPL")
    st.subheader(f"Strategy Backtesting for {ticker}")

    ctx = initialize_data_and_context(ticker)

    # DCF Backtest Section
    with st.container(border=True):
        st.markdown("### DCF Model Backtest")
        st.info("""
        This tool tests the historical accuracy of the DCF model. It takes your **current** growth and WACC assumptions from the sidebar and applies them to the financial data (FCF, debt, cash) from previous years.
        The "Calculated Value" is what the model would have predicted for that year, which is then compared to the "Actual Price" of the stock at that time.
        """)

        # Use default assumptions
        backtest_assumptions = {
            "growth_rates": [0.10, 0.10, 0.08, 0.08, 0.06],
            "ebit_margin": 0.20,
            "tax_rate": 0.21,
            "depreciation_pct": 0.03,
            "capex_pct": 0.05,
            "nwc_pct": 0.10,
            "terminal_growth": 0.025,
            "wacc": 0.10,
        }

        if st.button("Run DCF Backtest", key="dcf_backtest"):
            with st.spinner("Running DCF backtest..."):
                backtest_df = run_dcf_backtest(ctx, backtest_assumptions)

                if backtest_df is not None and not backtest_df.empty:
                    st.success("Backtest complete!")
                    st.dataframe(backtest_df, use_container_width=True)

                    # Calculate accuracy metrics
                    avg_error = backtest_df['Error (%)'].mean()
                    st.metric("Average Error", f"{avg_error:.1f}%")
                else:
                    st.warning("Could not run backtest with available data.")

    # Relative Valuation Backtest
    with st.container(border=True):
        st.markdown("### Relative Valuation Backtest")
        st.info("Tests P/E ratio valuation against historical data using comparable companies.")

        if st.button("Run Relative Valuation Backtest", key="rel_backtest"):
            with st.spinner("Running relative valuation backtest..."):
                comparables = get_ai_comparables(ticker)
                backtest_results = run_relative_backtest(ctx, comparables)

                if backtest_results:
                    st.success("Backtest complete!")
                    st.write(backtest_results)
                else:
                    st.warning("Could not run backtest with available data.")


if __name__ == "__main__":
    render_page()
