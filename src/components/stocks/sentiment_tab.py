"""
Sentiment Tab Component
Displays StockTwits, news sentiment, and social media analysis
"""
import streamlit as st
import plotly.graph_objects as go

from src.ui_utils.design_system import get_color


def show_sentiment_tab(data, components):
    """
    Show sentiment analysis using real scraper data
    
    Args:
        data: Dict containing ticker, sentiment data
        components: Dict containing sentiment components
    """
    from src.ui_utils.sentiment_scraper import get_scraper, display_sentiment_metrics, display_recent_posts
    from src.config.settings import Config
    
    st.subheader("💬 Ape Sentiment Tracker")
    
    # Get configuration
    config_obj = Config()
    api_config = {
        'reddit_client_id': config_obj.get('api.reddit.client_id', ''),
        'reddit_client_secret': config_obj.get('api.reddit.client_secret', ''),
        'reddit_user_agent': config_obj.get('api.reddit.user_agent', 'StocksV2App/1.0'),
        'news_api_key': config_obj.get('api.news.api_key', '')
    }
    
    # Initialize scraper
    scraper = get_scraper(api_config)
    
    # Refresh button
    col_refresh, col_info = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh Data", key="refresh_sentiment"):
            scraper.get_sentiment_data.clear()
            st.rerun()
    
    with col_info:
        st.caption("Real-time sentiment from Reddit (wallstreetbets, stocks, investing) and news sources")
    
    # Get sentiment data
    ticker = data["ticker"]
    with st.spinner(f"Scraping sentiment data for ${ticker}..."):
        summary = scraper.get_sentiment_summary(ticker)
    
    if summary['data_available']:
        # Display metrics
        display_sentiment_metrics(summary)
        
        st.divider()
        
        # Render visualizations
        _render_sentiment_charts(summary)
        
        st.divider()
        
        # Recent posts
        st.markdown("### 🔥 Recent Social Activity")
        display_recent_posts(summary['recent_posts'], max_posts=10)
        
        # Sentiment trend
        _render_sentiment_trend(scraper, ticker)
    else:
        st.warning(f"No sentiment data found for {ticker}")
        st.info("Try a more popular ticker (AAPL, TSLA, GME, AMC, SPY)")


def _render_sentiment_charts(summary: dict):
    """Render sentiment pie chart and source distribution"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Sentiment Breakdown")
        
        # Sentiment pie chart
        sentiment_data = {
            "🟢 Positive": summary['positive_pct'],
            "🔴 Negative": summary['negative_pct'],
            "⚪ Neutral": summary['neutral_pct']
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sentiment_data.keys()),
            values=list(sentiment_data.values()),
            hole=.3,
            marker_colors=[get_color('success'), get_color('danger'), get_color('warning')]
        )])
        
        fig.update_layout(
            title=f"Sentiment Distribution ({summary['total_mentions']} mentions)",
            template="plotly_dark",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Polarity interpretation
        avg_polarity = summary['avg_polarity']
        if avg_polarity > 0.3:
            st.success(f"**Polarity: {avg_polarity:.2f}** - Apes are BULLISH! 🦍🚀")
        elif avg_polarity > 0:
            st.info(f"**Polarity: {avg_polarity:.2f}** - Slightly bullish 📈")
        elif avg_polarity > -0.3:
            st.warning(f"**Polarity: {avg_polarity:.2f}** - Slightly bearish 📉")
        else:
            st.error(f"**Polarity: {avg_polarity:.2f}** - Bears winning 🐻")
    
    with col2:
        st.markdown("### 📈 Trending Sources")
        
        # Source distribution
        sources = summary['trending_sources']
        if sources:
            fig_sources = go.Figure(data=[go.Bar(
                x=list(sources.values()),
                y=list(sources.keys()),
                orientation='h',
                marker_color=get_color('info')
            )])
            
            fig_sources.update_layout(
                title="Mentions by Source",
                template="plotly_dark",
                height=350,
                xaxis_title="Number of Mentions",
                yaxis_title="Source"
            )
            
            st.plotly_chart(fig_sources, use_container_width=True)
        else:
            st.info("No source data available")
        
        # Subjectivity meter
        subjectivity = summary['avg_subjectivity']
        st.metric(
            "Avg Subjectivity",
            f"{subjectivity:.2f}",
            help="0 = Objective, 1 = Highly Subjective/Opinionated"
        )


def _render_sentiment_trend(scraper, ticker: str):
    """Render 7-day sentiment trend"""
    sentiment_over_time = scraper.get_sentiment_over_time(ticker, days=7)
    
    if not sentiment_over_time.empty:
        st.markdown("### 📅 Sentiment Trend (Last 7 Days)")
        
        fig_trend = go.Figure()
        
        if 'positive' in sentiment_over_time.columns:
            fig_trend.add_trace(go.Scatter(
                x=sentiment_over_time['date_only'],
                y=sentiment_over_time['positive'],
                mode='lines+markers',
                name='Positive',
                line=dict(color=get_color('success'), width=2)
            ))
        
        if 'negative' in sentiment_over_time.columns:
            fig_trend.add_trace(go.Scatter(
                x=sentiment_over_time['date_only'],
                y=sentiment_over_time['negative'],
                mode='lines+markers',
                name='Negative',
                line=dict(color=get_color('danger'), width=2)
            ))
        
        if 'neutral' in sentiment_over_time.columns:
            fig_trend.add_trace(go.Scatter(
                x=sentiment_over_time['date_only'],
                y=sentiment_over_time['neutral'],
                mode='lines+markers',
                name='Neutral',
                line=dict(color=get_color('warning'), width=2)
            ))
        
        fig_trend.update_layout(
            title="Sentiment Trend",
            template="plotly_dark",
            height=400,
            xaxis_title="Date",
            yaxis_title="Sentiment Count"
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
