import streamlit as st
import plotly.graph_objects as go
from leaderboard import generate_squeeze_leaderboard

def render_page():
    """Main function to render the Squeeze Leaderboard page."""
    st.title("🏆 Squeeze Leaderboard")
    st.info("This page scans a predefined list of popular 'meme' and high-short-interest stocks to rank them by their USSI score.")

    # Predefined list of stocks to scan
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

    # Display the leaderboard and trends chart from session state
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