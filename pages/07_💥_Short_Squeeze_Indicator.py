import streamlit as st
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from squeeze_analyzer import calculate_squeeze_score
from app_utils import create_gauge_chart, create_radar_chart

def render_page():
    """Main function to render the Short Squeeze Indicator page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"💥 Ultimate Short Squeeze Indicator (USSI) for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
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
        # Prepare data for radar chart
        radar_data = {
            name: data['score'] for name, data in components.items() if data['weight'] > 0
        }
        st.plotly_chart(create_radar_chart(radar_data), use_container_width=True)

    # --- Google Trends Chart ---
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

if __name__ == "__main__":
    render_page()