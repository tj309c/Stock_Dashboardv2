import streamlit as st
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from squeeze_analyzer import calculate_squeeze_score
from app_utils import create_gauge_chart, create_radar_chart, plotly_full_width, display_dataframe_full_width
from leaderboard import generate_squeeze_leaderboard
from mode_config import render_mode_info, should_show_feature

def render_page():
    """Consolidated Competitive & Market Analysis Dashboard"""
    st.title("🤝 Competitive & Market Analysis")
    st.caption("Competitor benchmarking, industry analysis, and short squeeze detection")

    # Display current trading mode
    render_mode_info()

    ticker = st.query_params.get("ticker", "AAPL")

    # Create tabs for the two sections
    tab1, tab2, tab3 = st.tabs([
        "📊 Competitor Analysis",
        "💥 Short Squeeze Analysis",
        "🔧 Debug"
    ])

    with tab1:
        render_competitor_analysis_tab(ticker)

    with tab2:
        render_short_squeeze_tab(ticker)

    with tab3:
        render_debug_tab_competitive(ticker)


def render_competitor_analysis_tab(ticker):
    """Competitor comparison and analysis"""
    st.subheader(f"Competitor Analysis for {ticker}")

    ctx = initialize_data_and_context(ticker, light_load=True)

    if not ctx or not ctx.info:
        st.error(f"Could not load data for '{ticker}'.")
        st.stop()

    st.info("🚧 Competitor analysis coming soon! This will include peer comparison, industry benchmarks, and competitive positioning.")

    # Display basic company info for now
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Company Info")
        st.write(f"**Sector:** {ctx.info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {ctx.info.get('industry', 'N/A')}")
        market_cap = ctx.info.get('marketCap', 0)
        st.write(f"**Market Cap:** ${market_cap:,.0f}" if market_cap else "N/A")

    with col2:
        st.markdown("#### Market Position")
        st.write(f"**Exchange:** {ctx.info.get('exchange', 'N/A')}")
        st.write(f"**Full Time Employees:** {ctx.info.get('fullTimeEmployees', 'N/A'):,}" if ctx.info.get('fullTimeEmployees') else "**Full Time Employees:** N/A")


def render_short_squeeze_tab(ticker):
    """Short squeeze indicator and leaderboard"""
    st.subheader("Short Squeeze Analysis")

    # Create sub-tabs for single stock vs leaderboard
    subtab1, subtab2 = st.tabs(["📈 Single Stock", "🏆 Leaderboard"])

    with subtab1:
        render_single_stock_squeeze(ticker)

    with subtab2:
        render_squeeze_leaderboard()


def render_single_stock_squeeze(ticker):
    """Single stock squeeze analysis"""
    st.markdown(f"#### Ultimate Short Squeeze Indicator (USSI) for {ticker}")

    ctx = initialize_data_and_context(ticker)
    include_reddit = st.session_state.get('include_reddit_sentiment', True)

    with st.spinner("Calculating Squeeze Score..."):
        final_score, components = calculate_squeeze_score(ctx.info, ctx.price_data, include_reddit=include_reddit)

    col1, col2 = st.columns(2)
    with col1:
        plotly_full_width(create_gauge_chart(final_score, "Squeeze Score", 0, 100))
        if final_score > 80:
            st.error("EXTREME SQUEEZE POTENTIAL", icon="🔥")
        elif final_score > 60:
            st.warning("High Squeeze Potential", icon="⚠️")
        elif final_score > 40:
            st.info("Moderate Squeeze Potential", icon="🧐")
        else:
            st.success("Low Squeeze Potential", icon="✅")

    with col2:
        radar_data = {
            name: data['score'] for name, data in components.items() if data['weight'] > 0
        }
        plotly_full_width(create_radar_chart(radar_data))

    # Google Trends Chart
    if include_reddit and 'Social Buzz' in components:
        sentiment_data = components['Social Buzz'].get('raw_data')
        if sentiment_data:
            trends_df = sentiment_data.get('google_trends_df')
            if trends_df is not None and not trends_df.empty:
                st.subheader("Google Search Trends (Last 7 Days)")
                fig_trends = go.Figure()
                fig_trends.add_trace(go.Scatter(x=trends_df.index, y=trends_df[ticker], mode='lines', name='Trend Score'))
                fig_trends.update_layout(
                    title_text=f"Google Search Interest for '{ticker}'",
                    yaxis_title="Normalized Interest (0-100)",
                    template="plotly_white"
                )
                plotly_full_width(fig_trends)


def render_squeeze_leaderboard():
    """Squeeze leaderboard for multiple stocks"""
    st.markdown("#### Squeeze Leaderboard")
    st.info("This scans popular 'meme' and high-short-interest stocks to rank them by USSI score.")

    stocks_to_scan = [
        'GME', 'AMC', 'BBBYQ', 'KOSS', 'EXPR', 'RIVN', 'LCID', 'PLTR',
        'SOFI', 'HOOD', 'UPST', 'CVNA', 'AI', 'MARA', 'RIOT', 'MSTR',
        'BYND', 'SPCE', 'W', 'CLOV', 'WISH', 'SNDL', 'TLRY'
    ]

    include_reddit_leaderboard = st.session_state.get('include_reddit_leaderboard', True)

    if st.button("🚀 Scan for Squeeze Candidates"):
        leaderboard_df, sentiment_data_dict = generate_squeeze_leaderboard(stocks_to_scan, include_reddit=include_reddit_leaderboard)
        st.session_state.leaderboard_df = leaderboard_df
        st.session_state.sentiment_data_dict = sentiment_data_dict

    if 'leaderboard_df' in st.session_state and not st.session_state.leaderboard_df.empty:
        display_dataframe_full_width(
            st.session_state.leaderboard_df,
            column_config={
                "Dashboard Link": st.column_config.LinkColumn(
                    "Ticker",
                    display_text="View"
                )
            },
            column_order=("Dashboard Link", "Ticker", "Company", "Squeeze Score", "Short % Float", "Volume Z-Score", "Social Mentions (7d)"),
            hide_index=True
        )
        st.info("Click the 'View' link in any row to load the full dashboard for that ticker.")

        st.subheader("Google Search Trends (Last 7 Days)")
        trend_ticker = st.selectbox("Select Ticker to View Trend", options=st.session_state.leaderboard_df['Ticker'].tolist())

        if trend_ticker and 'sentiment_data_dict' in st.session_state:
            sentiment_data = st.session_state.sentiment_data_dict.get(trend_ticker)
            if sentiment_data:
                trends_df = sentiment_data.get('google_trends_df')
                if trends_df is not None and not trends_df.empty and trend_ticker in trends_df.columns:
                    fig_trends = go.Figure()
                    fig_trends.add_trace(go.Scatter(x=trends_df.index, y=trends_df[trend_ticker], mode='lines', name='Trend Score'))
                    fig_trends.update_layout(
                        title_text=f"Google Search Interest for '{trend_ticker}'",
                        yaxis_title="Normalized Interest (0-100)",
                        template="plotly_white"
                    )
                    plotly_full_width(fig_trends)
                else:
                    st.warning(f"No Google Trends data available for {trend_ticker}.")
    else:
        st.write("Click the button above to start scanning.")


# ========================================
# DEBUG TAB
# ========================================

def render_debug_tab_competitive(ticker):
    """Debug tab for Competitive & Market page"""
    st.markdown("### 🔧 Competitive & Market Debug Panel")

    st.info("""
    **Purpose**: Diagnose short squeeze calculation data, leaderboard generation, and competitor data availability.
    """)

    # Section 1: Session State Variables
    with st.expander("📦 Session State Variables", expanded=False):
        st.markdown("**Current session state keys and values:**")
        if st.session_state:
            state_dict = {k: str(v)[:200] for k, v in st.session_state.items()}
            st.json(state_dict)
        else:
            st.write("No session state variables found")

    # Section 2: Short Squeeze Data Quality
    with st.expander("💥 Short Squeeze Data Quality", expanded=True):
        st.markdown(f"**Checking short squeeze input data for {ticker}:**")

        ctx = initialize_data_and_context(ticker)
        info = ctx.info if ctx and ctx.info else {}

        # Define critical short squeeze data points
        checks = {
            "Short Ratio": info.get('shortRatio') is not None,
            "Short % of Float": info.get('shortPercentOfFloat') is not None,
            "Shares Short": info.get('sharesShort') is not None,
            "Average Volume": info.get('averageVolume') is not None,
            "Regular Market Volume": info.get('regularMarketVolume') is not None,
            "Price Data Available": ctx.price_data is not None and not ctx.price_data.empty if ctx else False,
            "Volume Data in Price": 'Volume' in ctx.price_data.columns if ctx and ctx.price_data is not None and not ctx.price_data.empty else False
        }

        # Display check results
        for check_name, passed in checks.items():
            st.markdown(f"{'✅' if passed else '❌'} {check_name}")

        # Display actual values
        st.markdown("---")
        st.markdown("**Raw Values:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Short Ratio", info.get('shortRatio', 'N/A'))
            st.metric("Short % of Float", f"{info.get('shortPercentOfFloat', 0) * 100:.2f}%" if info.get('shortPercentOfFloat') else 'N/A')
            st.metric("Shares Short", f"{info.get('sharesShort', 'N/A'):,}" if info.get('sharesShort') else 'N/A')
        with col2:
            st.metric("Average Volume", f"{info.get('averageVolume', 'N/A'):,}" if info.get('averageVolume') else 'N/A')
            st.metric("Regular Market Volume", f"{info.get('regularMarketVolume', 'N/A'):,}" if info.get('regularMarketVolume') else 'N/A')
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                st.metric("Price Data Points", len(ctx.price_data))

        completeness_score = sum(checks.values())
        total_checks = len(checks)
        completeness_pct = (completeness_score / total_checks) * 100

        st.markdown("---")
        st.metric("Short Squeeze Data Completeness", f"{completeness_pct:.0f}%")

        if completeness_pct < 50:
            st.error("❌ Critical short squeeze data is missing. USSI score may be unreliable.")
        elif completeness_pct < 80:
            st.warning("⚠️ Some short squeeze data is missing. Results may be incomplete.")
        else:
            st.success("✅ Short squeeze data is comprehensive!")

    # Section 3: Calculate USSI Score with Components
    with st.expander("🎯 USSI Score Calculation", expanded=True):
        st.markdown("**Ultimate Short Squeeze Indicator (USSI) breakdown:**")

        ctx = initialize_data_and_context(ticker)
        include_reddit = st.session_state.get('include_reddit_sentiment', True)

        try:
            final_score, components = calculate_squeeze_score(ctx.info, ctx.price_data, include_reddit=include_reddit)

            st.metric("Final USSI Score", f"{final_score:.1f}/100")

            st.markdown("**Component Scores:**")
            if components:
                comp_df = {
                    'Component': [],
                    'Raw Score': [],
                    'Normalized (0-100)': [],
                    'Weight': []
                }

                for comp_name, comp_data in components.items():
                    comp_df['Component'].append(comp_name)
                    comp_df['Raw Score'].append(f"{comp_data.get('raw_score', 'N/A')}")
                    comp_df['Normalized (0-100)'].append(f"{comp_data.get('normalized_score', 0):.1f}")
                    comp_df['Weight'].append(f"{comp_data.get('weight', 0) * 100:.0f}%")

                display_dataframe_full_width(pd.DataFrame(comp_df))
            else:
                st.warning("No component breakdown available")

        except Exception as e:
            st.error(f"❌ Error calculating USSI score: {str(e)}")

    # Section 4: Leaderboard Status
    with st.expander("🏆 Leaderboard Status", expanded=False):
        st.markdown("**Checking leaderboard session state:**")

        if 'leaderboard_df' in st.session_state:
            leaderboard = st.session_state.leaderboard_df
            st.success(f"✅ Leaderboard loaded with {len(leaderboard)} stocks")
            display_dataframe_full_width(leaderboard.head(10))
        else:
            st.warning("⚠️ Leaderboard not generated yet. Run the leaderboard scan first.")

        if 'sentiment_data_dict' in st.session_state:
            sentiment_dict = st.session_state.sentiment_data_dict
            st.success(f"✅ Sentiment data cached for {len(sentiment_dict)} tickers")
            st.write("**Cached tickers:**", list(sentiment_dict.keys()))
        else:
            st.warning("⚠️ No sentiment data cached yet.")

    # Section 5: Competitor Data Status
    with st.expander("👥 Competitor Data Status", expanded=False):
        st.markdown(f"**Checking competitor data availability for {ticker}:**")

        ctx = initialize_data_and_context(ticker, light_load=True)

        if ctx and ctx.info:
            sector = ctx.info.get('sector', 'N/A')
            industry = ctx.info.get('industry', 'N/A')
            market_cap = ctx.info.get('marketCap', 0)

            st.markdown(f"**Sector:** {sector}")
            st.markdown(f"**Industry:** {industry}")
            st.markdown(f"**Market Cap:** ${market_cap:,.0f}" if market_cap else "**Market Cap:** N/A")

            st.info("🚧 Competitor comparison feature is under development. When complete, this section will show peer companies in the same industry.")
        else:
            st.error("❌ Unable to load company data")

    # Section 6: Cache Status
    with st.expander("💾 Cache Status", expanded=False):
        st.markdown("**Streamlit cache information:**")

        st.markdown("""
        **Cached functions in this page:**
        - `initialize_data_and_context()` - Ticker data loader
        - `calculate_squeeze_score()` - USSI calculation
        - `generate_squeeze_leaderboard()` - Leaderboard scan

        **Note**: Cache is automatically managed by Streamlit with TTL (Time-To-Live).
        """)

        if st.button("🗑️ Clear All Caches", key="clear_cache_competitive"):
            st.cache_data.clear()
            st.success("✅ All caches cleared! Refresh the page to reload data.")

        if st.button("🧹 Clear Leaderboard Session State", key="clear_leaderboard"):
            if 'leaderboard_df' in st.session_state:
                del st.session_state.leaderboard_df
            if 'sentiment_data_dict' in st.session_state:
                del st.session_state.sentiment_data_dict
            st.success("✅ Leaderboard session state cleared!")

    # Section 7: Performance Metrics
    with st.expander("⚡ Performance Metrics", expanded=False):
        st.markdown("**Data loading performance:**")

        import time

        # Test ticker data fetch
        start = time.time()
        try:
            test_ctx = initialize_data_and_context(ticker, light_load=True)
            load_time = time.time() - start
            load_status = '✅' if test_ctx else '❌'
        except Exception as e:
            load_time = time.time() - start
            load_status = f'❌ Error: {str(e)[:50]}'

        st.metric("Ticker Data Load", f"{load_time:.2f}s", delta=load_status)

        # Test USSI calculation
        start = time.time()
        try:
            test_ctx = initialize_data_and_context(ticker)
            final_score, components = calculate_squeeze_score(test_ctx.info, test_ctx.price_data, include_reddit=False)
            calc_time = time.time() - start
            calc_status = '✅'
        except Exception as e:
            calc_time = time.time() - start
            calc_status = f'❌ Error: {str(e)[:50]}'

        st.metric("USSI Calculation", f"{calc_time:.2f}s", delta=calc_status)

        if load_time + calc_time > 5:
            st.warning("⚠️ Performance is slower than expected. Consider checking API connectivity.")

    # Section 8: Raw Data Inspector
    with st.expander("🔍 Raw Data Inspector", expanded=False):
        st.markdown("**Inspect raw data structures:**")

        ctx = initialize_data_and_context(ticker)

        data_source = st.selectbox(
            "Select data source to inspect:",
            ["Company Info (Short Data)", "Price Data (Volume)", "Leaderboard DataFrame"],
            key="data_inspector_competitive"
        )

        if data_source == "Company Info (Short Data)":
            if ctx and ctx.info:
                short_data = {
                    'shortRatio': ctx.info.get('shortRatio'),
                    'shortPercentOfFloat': ctx.info.get('shortPercentOfFloat'),
                    'sharesShort': ctx.info.get('sharesShort'),
                    'sharesShortPriorMonth': ctx.info.get('sharesShortPriorMonth'),
                    'sharesShortPreviousMonthDate': ctx.info.get('sharesShortPreviousMonthDate'),
                    'dateShortInterest': ctx.info.get('dateShortInterest'),
                    'averageVolume': ctx.info.get('averageVolume'),
                    'averageVolume10days': ctx.info.get('averageVolume10days'),
                    'regularMarketVolume': ctx.info.get('regularMarketVolume')
                }
                st.json(short_data)
            else:
                st.error("No company info available")

        elif data_source == "Price Data (Volume)":
            if ctx and ctx.price_data is not None and not ctx.price_data.empty:
                display_dataframe_full_width(ctx.price_data[['Close', 'Volume']].tail(20))
            else:
                st.error("No price data available")

        elif data_source == "Leaderboard DataFrame":
            if 'leaderboard_df' in st.session_state:
                display_dataframe_full_width(st.session_state.leaderboard_df)
            else:
                st.error("No leaderboard data available. Run the leaderboard scan first.")


if __name__ == "__main__":
    render_page()
