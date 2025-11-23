import streamlit as st
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from squeeze_analyzer import calculate_squeeze_score
from app_utils import create_gauge_chart, create_radar_chart
from leaderboard import generate_squeeze_leaderboard

def render_page():
    """Consolidated Competitive & Market Analysis Dashboard"""
    st.title("🤝 Competitive & Market Analysis")

    ticker = st.query_params.get("ticker", "AAPL")

    # Create tabs for the two sections
    tab1, tab2 = st.tabs([
        "📊 Competitor Analysis",
        "💥 Short Squeeze Analysis"
    ])

    with tab1:
        render_competitor_analysis_tab(ticker)

    with tab2:
        render_short_squeeze_tab(ticker)


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
        st.plotly_chart(create_gauge_chart(final_score, "Squeeze Score", 0, 100), use_container_width=True)
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
        st.plotly_chart(create_radar_chart(radar_data), use_container_width=True)

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
                st.plotly_chart(fig_trends, use_container_width=True)


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
        st.dataframe(
            st.session_state.leaderboard_df,
            column_config={
                "Dashboard Link": st.column_config.LinkColumn(
                    "Ticker",
                    display_text="View"
                )
            },
            column_order=("Dashboard Link", "Ticker", "Company", "Squeeze Score", "Short % Float", "Volume Z-Score", "Social Mentions (7d)"),
            hide_index=True,
            use_container_width=True
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
                    st.plotly_chart(fig_trends, use_container_width=True)
                else:
                    st.warning(f"No Google Trends data available for {trend_ticker}.")
    else:
        st.write("Click the button above to start scanning.")


if __name__ == "__main__":
    render_page()
