import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from portfolio_optimizer import run_portfolio_optimization
from app_logic import initialize_data_and_context
from app_utils import plotly_full_width, display_dataframe_full_width
from backtester import run_dcf_backtest, run_relative_backtest
from ai_services import get_ai_comparables
from mode_config import render_mode_info, should_show_feature

def render_page():
    """Consolidated Portfolio & Strategy Tools Dashboard"""
    st.title("💼 Portfolio & Strategy Tools")
    st.caption("Long-term portfolio optimization, strategy backtesting, and risk-adjusted return analysis")

    # Display current trading mode
    render_mode_info()

    # Create tabs for the two sections
    tab1, tab2, tab3 = st.tabs([
        "📊 Portfolio Optimization",
        "⚙️ Strategy Backtesting",
        "🔧 Debug"
    ])

    with tab1:
        render_portfolio_optimization_tab()

    with tab2:
        render_strategy_backtesting_tab()

    with tab3:
        render_debug_tab_portfolio()


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
                    plotly_full_width(fig_sharpe)

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
                    plotly_full_width(fig_vol)

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
                plotly_full_width(fig_frontier)
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
                    display_dataframe_full_width(backtest_df)

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


# ========================================
# DEBUG TAB
# ========================================

def render_debug_tab_portfolio():
    """Debug tab for Portfolio & Strategy page"""
    st.markdown("### 🔧 Portfolio & Strategy Debug Panel")

    st.info("""
    **Purpose**: Diagnose portfolio optimization inputs, backtesting data, and strategy performance metrics.
    """)

    # Section 1: Session State Variables
    with st.expander("📦 Session State Variables", expanded=False):
        st.markdown("**Current session state keys and values:**")
        if st.session_state:
            state_dict = {k: str(v)[:200] for k, v in st.session_state.items()}
            st.json(state_dict)
        else:
            st.write("No session state variables found")

    # Section 2: Portfolio Optimization Data Check
    with st.expander("📊 Portfolio Optimization Data Quality", expanded=True):
        st.markdown("**Test portfolio optimization with sample tickers:**")

        test_tickers = st.text_input("Test Tickers (comma-separated)", "AAPL,MSFT,GOOG", key="test_portfolio_tickers")

        if st.button("Test Portfolio Data Fetch", key="test_portfolio_fetch"):
            with st.spinner("Fetching portfolio data..."):
                import yfinance as yf
                tickers_list = [t.strip().upper() for t in test_tickers.split(",")]

                data_quality = {}
                for ticker in tickers_list:
                    try:
                        data = yf.download(ticker, period='3y', progress=False)
                        if not data.empty:
                            data_quality[ticker] = {
                                'Status': '✅ Success',
                                'Data Points': len(data),
                                'Date Range': f"{data.index[0].date()} to {data.index[-1].date()}",
                                'Has Returns': 'Close' in data.columns
                            }
                        else:
                            data_quality[ticker] = {
                                'Status': '❌ No Data',
                                'Data Points': 0,
                                'Date Range': 'N/A',
                                'Has Returns': False
                            }
                    except Exception as e:
                        data_quality[ticker] = {
                            'Status': f'❌ Error: {str(e)[:30]}',
                            'Data Points': 0,
                            'Date Range': 'N/A',
                            'Has Returns': False
                        }

                # Display results
                for ticker, quality in data_quality.items():
                    st.markdown(f"**{ticker}**")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Status", quality['Status'])
                    col2.metric("Data Points", quality['Data Points'])
                    col3.text(f"Range: {quality['Date Range']}")

                # Overall assessment
                successful = sum(1 for q in data_quality.values() if '✅' in q['Status'])
                st.markdown("---")
                st.metric("Tickers Ready", f"{successful}/{len(tickers_list)}")

                if successful < 2:
                    st.error("❌ Need at least 2 tickers with valid data for portfolio optimization")
                elif successful < len(tickers_list):
                    st.warning(f"⚠️ Only {successful} out of {len(tickers_list)} tickers have data")
                else:
                    st.success("✅ All tickers have sufficient data for optimization!")

    # Section 3: Backtesting Requirements Check
    with st.expander("⚙️ Backtesting Requirements", expanded=True):
        st.markdown("**Checking backtesting data availability:**")

        test_ticker = st.text_input("Test Ticker for Backtesting", "AAPL", key="test_backtest_ticker")

        if st.button("Check Backtest Data", key="check_backtest"):
            ctx = initialize_data_and_context(test_ticker)

            if not ctx or not ctx.info:
                st.error(f"❌ Could not load data for {test_ticker}")
            else:
                st.success(f"✅ Successfully loaded data for {test_ticker}")

                # DCF Backtest Requirements
                st.markdown("**DCF Backtest Requirements:**")
                dcf_checks = {
                    "Revenue Data": ctx.info.get('totalRevenue') is not None,
                    "Shares Outstanding": ctx.info.get('sharesOutstanding') is not None,
                    "Financial Statements": not ctx.income_data.empty,
                    "Historical Prices": ctx.price_data is not None and not ctx.price_data.empty,
                    "Sufficient History": len(ctx.price_data) >= 252 if ctx.price_data is not None and not ctx.price_data.empty else False
                }

                for check_name, passed in dcf_checks.items():
                    st.markdown(f"{'✅' if passed else '❌'} {check_name}")

                dcf_ready = all(dcf_checks.values())
                if dcf_ready:
                    st.success("✅ All DCF backtest requirements met!")
                else:
                    st.warning("⚠️ Some DCF backtest requirements not met")

                # Relative Valuation Backtest Requirements
                st.markdown("---")
                st.markdown("**Relative Valuation Backtest Requirements:**")
                rel_checks = {
                    "P/E Ratio": ctx.info.get('trailingPE') is not None,
                    "Forward P/E": ctx.info.get('forwardPE') is not None,
                    "Sector Info": ctx.info.get('sector') is not None,
                    "Industry Info": ctx.info.get('industry') is not None
                }

                for check_name, passed in rel_checks.items():
                    st.markdown(f"{'✅' if passed else '❌'} {check_name}")

                rel_ready = all(rel_checks.values())
                if rel_ready:
                    st.success("✅ All relative valuation backtest requirements met!")
                else:
                    st.warning("⚠️ Some relative valuation backtest requirements not met")

    # Section 4: Module Availability Check
    with st.expander("📦 Module & Function Availability", expanded=False):
        st.markdown("**Checking required modules and functions:**")

        modules_status = {}

        # Check portfolio optimizer
        try:
            from portfolio_optimizer import run_portfolio_optimization
            modules_status['Portfolio Optimizer'] = '✅ Available'
        except ImportError as e:
            modules_status['Portfolio Optimizer'] = f'❌ Error: {str(e)[:50]}'

        # Check backtester
        try:
            from backtester import run_dcf_backtest, run_relative_backtest
            modules_status['Backtester'] = '✅ Available'
        except ImportError as e:
            modules_status['Backtester'] = f'❌ Error: {str(e)[:50]}'

        # Check AI services
        try:
            from ai_services import get_ai_comparables
            modules_status['AI Services (Comparables)'] = '✅ Available'
        except ImportError as e:
            modules_status['AI Services (Comparables)'] = f'❌ Error: {str(e)[:50]}'

        for module, status in modules_status.items():
            st.markdown(f"**{module}**: {status}")

        available_count = sum(1 for s in modules_status.values() if '✅' in s)
        st.markdown("---")
        st.metric("Modules Available", f"{available_count}/{len(modules_status)}")

    # Section 5: Cache Status
    with st.expander("💾 Cache Status", expanded=False):
        st.markdown("**Streamlit cache information:**")

        st.markdown("""
        **Cached functions in this page:**
        - `run_portfolio_optimization()` - Portfolio simulation and optimization
        - `run_dcf_backtest()` - DCF valuation backtesting
        - `run_relative_backtest()` - Relative valuation backtesting
        - `initialize_data_and_context()` - Ticker data loader

        **Note**: Cache is automatically managed by Streamlit with TTL (Time-To-Live).
        """)

        if st.button("🗑️ Clear All Caches", key="clear_cache_portfolio"):
            st.cache_data.clear()
            st.success("✅ All caches cleared! Refresh the page to reload data.")

    # Section 6: Performance Metrics
    with st.expander("⚡ Performance Metrics", expanded=False):
        st.markdown("**Module performance testing:**")

        import time

        # Test portfolio optimization
        if st.button("Test Portfolio Optimization Performance", key="test_opt_perf"):
            test_tickers = "AAPL,MSFT"
            start = time.time()
            try:
                with st.spinner("Running optimization..."):
                    opt_results = run_portfolio_optimization(test_tickers)
                opt_time = time.time() - start
                opt_status = '✅' if opt_results else '❌'
                st.metric("Portfolio Optimization (2 tickers)", f"{opt_time:.2f}s", delta=opt_status)

                if opt_time > 30:
                    st.warning("⚠️ Optimization is slow. Consider reducing number of simulations.")
            except Exception as e:
                opt_time = time.time() - start
                st.metric("Portfolio Optimization", f"{opt_time:.2f}s", delta=f"❌ Error: {str(e)[:30]}")

    # Section 7: Raw Data Inspector
    with st.expander("🔍 Raw Data Inspector", expanded=False):
        st.markdown("**Inspect optimization and backtest results:**")

        data_source = st.selectbox(
            "Select data source to inspect:",
            ["Portfolio Optimization Results", "Backtest Assumptions", "Sample Historical Data"],
            key="data_inspector_portfolio"
        )

        if data_source == "Portfolio Optimization Results":
            st.info("Run a portfolio optimization first to see results here.")
            if st.session_state.get('last_optimization_results'):
                st.json(st.session_state.last_optimization_results)
            else:
                st.write("No optimization results available in session state")

        elif data_source == "Backtest Assumptions":
            st.markdown("**Default DCF Backtest Assumptions:**")
            default_assumptions = {
                "revenue_growth": 0.15,
                "ebitda_margin": 0.25,
                "tax_rate": 0.21,
                "capex_pct": 0.05,
                "nwc_pct": 0.10,
                "terminal_growth": 0.025,
                "wacc": 0.10
            }
            st.json(default_assumptions)

        elif data_source == "Sample Historical Data":
            test_ticker = st.text_input("Enter ticker to inspect:", "AAPL", key="inspect_ticker")
            if st.button("Load Data", key="load_inspect_data"):
                ctx = initialize_data_and_context(test_ticker)
                    if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                    st.markdown(f"**Price Data for {test_ticker}:**")
                    from app_utils import display_dataframe_full_width
                    display_dataframe_full_width(ctx.price_data.tail(20))
                else:
                    st.error("No data available")


if __name__ == "__main__":
    render_page()
