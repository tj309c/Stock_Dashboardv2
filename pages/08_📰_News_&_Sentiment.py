import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from news_fetcher import (
    get_all_news, get_news_sentiment_summary,
    format_time_ago, truncate_text,
    get_comprehensive_social_sentiment
)
from performance_optimizer import PerformanceMonitor, optimize_dataframe
from ticker_utils import setup_sidebar_ticker_input
from app_utils import plotly_full_width
from mode_config import render_mode_info, should_show_feature
from ai_model_config import get_configured_model, call_ai_model

def render_page():
    """Main News & Sentiment Dashboard - Deep dive into sentiment analysis"""
    st.title("📰 News & Sentiment Intelligence")
    st.caption("Comprehensive sentiment analysis across news, social media, and market trends")

    # Display current trading mode
    render_mode_info()

    # Setup sidebar ticker input
    ticker = setup_sidebar_ticker_input("news_sentiment")

    # Get company info for name
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info.get('longName', stock.info.get('shortName', ticker))
    except:
        company_name = ticker

    # ========================================
    # CONTROL PANEL
    # ========================================
    st.markdown("## ⚙️ Analysis Settings")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        days_back = st.slider("📅 Days of News Coverage", min_value=1, max_value=30, value=7,
                             help="How far back to search for news articles")

    with col2:
        use_ai = st.checkbox("🤖 AI Sentiment", value=False,
                            help="Uses AI for deeper sentiment analysis (slower)")

    with col3:
        load_social = st.checkbox("📊 Social Media", value=False,
                                 help="Load X/Twitter and Google Trends (adds 5-10 seconds)")

    with col4:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")

    # ========================================
    # FETCH NEWS DATA
    # ========================================
    with PerformanceMonitor(f"news_fetch_{ticker}"):
        with st.spinner("Fetching latest news..."):
            news_df = get_all_news(ticker, company_name, days_back=days_back, use_ai_sentiment=use_ai)

            if not news_df.empty:
                news_df = optimize_dataframe(news_df)

    if news_df.empty:
        st.warning(f"No news found for {ticker} in the last {days_back} days.")
        st.info("This could mean:\n- The ticker symbol is incorrect\n- There's no recent news coverage\n- API rate limits have been reached")
        return

    # Get sentiment summary
    summary = get_news_sentiment_summary(news_df)

    # ========================================
    # LOAD SOCIAL DATA (Optional)
    # ========================================
    social_data = None
    if load_social:
        with st.spinner("Analyzing X/Twitter and Google Trends..."):
            social_data = get_comprehensive_social_sentiment(ticker, company_name)

    # ========================================
    # EXECUTIVE SENTIMENT DASHBOARD
    # ========================================
    render_executive_sentiment_summary(ticker, summary, news_df, social_data, days_back)

    st.divider()

    # ========================================
    # SENTIMENT SOURCE COMPARISON
    # ========================================
    render_sentiment_source_comparison(summary, social_data)

    st.divider()

    # ========================================
    # NEWS ARTICLES ANALYSIS
    # ========================================
    render_news_articles_section(ticker, news_df, summary, use_ai, days_back)

    st.divider()

    # ========================================
    # DETAILED SOCIAL INSIGHTS (if loaded)
    # ========================================
    if social_data:
        render_detailed_social_insights(social_data)

    # ========================================
    # SENTIMENT TRENDS & PATTERNS
    # ========================================
    render_sentiment_trends_section(news_df, ticker)

    st.divider()

    # ========================================
    # CUSTOM ANALYSIS MODULES (Future Expansion)
    # ========================================
    render_advanced_modules_section(ticker, news_df, summary)


def render_executive_sentiment_summary(ticker, summary, news_df, social_data, days_back):
    """Professional executive summary of overall sentiment"""
    st.markdown("## 🎯 Executive Sentiment Summary")

    # Prepare sentiment data from all sources
    sentiment_sources = []

    # News sentiment
    news_sentiment_score = (summary['avg_sentiment'] + 1) / 2
    sentiment_sources.append({
        'source': 'News Articles',
        'sentiment': summary['sentiment_trend'].title(),
        'score': news_sentiment_score,
        'count': summary['total_articles'],
        'emoji': summary['trend_emoji'],
        'color': '#00CC96' if news_sentiment_score > 0.6 else '#EF553B' if news_sentiment_score < 0.4 else '#636EFA'
    })

    # Twitter sentiment (if available)
    if social_data and social_data.get('twitter', {}).get('available', False):
        twitter = social_data['twitter']
        twitter_score = 0.5
        if twitter['sentiment'] == 'positive':
            twitter_score = 0.65 + (twitter['confidence'] * 0.25)
        elif twitter['sentiment'] == 'negative':
            twitter_score = 0.35 - (twitter['confidence'] * 0.25)

        sentiment_sources.append({
            'source': 'X/Twitter',
            'sentiment': twitter['sentiment'].title(),
            'score': twitter_score,
            'count': f"{twitter['trending_score']}/10 trending",
            'emoji': '📈' if twitter['sentiment'] == 'positive' else '📉' if twitter['sentiment'] == 'negative' else '➖',
            'color': '#00CC96' if twitter['sentiment'] == 'positive' else '#EF553B' if twitter['sentiment'] == 'negative' else '#636EFA'
        })

    # Google Trends sentiment (if available)
    if social_data and social_data.get('google_trends', {}).get('available', False):
        trends = social_data['google_trends']
        trends_score = trends['current_interest'] / 100

        sentiment_sources.append({
            'source': 'Google Trends',
            'sentiment': trends['trend_direction'].title(),
            'score': trends_score,
            'count': f"{trends['current_interest']}/100 interest",
            'emoji': trends['trend_emoji'],
            'color': '#00CC96' if trends['trend_direction'] == 'rising' else '#EF553B' if trends['trend_direction'] == 'falling' else '#636EFA'
        })

    # Calculate alignment, momentum, and overall sentiment
    alignment_score, alignment_interpretation, risk_flag = calculate_sentiment_alignment(sentiment_sources)
    momentum_direction, momentum_emoji, momentum_text = calculate_sentiment_momentum(summary['avg_sentiment'], news_df)
    overall_score = sum(s['score'] for s in sentiment_sources) / len(sentiment_sources)

    # Determine overall sentiment label
    if overall_score > 0.65:
        overall_sentiment = "Bullish"
        overall_emoji = "📈"
    elif overall_score < 0.35:
        overall_sentiment = "Bearish"
        overall_emoji = "📉"
    else:
        overall_sentiment = "Neutral"
        overall_emoji = "➡️"

    # Generate key insight
    if len(sentiment_sources) == 1:
        key_insight = f"Analysis based on {sentiment_sources[0]['source']} only"
    elif alignment_score > 0.75:
        key_insight = f"All sources showing consistent {overall_sentiment.lower()} sentiment"
    elif risk_flag:
        key_insight = f"⚠️ Sources show conflicting signals - exercise caution"
    else:
        key_insight = f"Moderate agreement across sources trending {overall_sentiment.lower()}"

    # Display summary card
    card_cols = st.columns([1, 1, 1, 2])

    with card_cols[0]:
        st.metric("Overall Sentiment", f"{overall_emoji} {overall_sentiment}", delta=f"Score: {overall_score:.2f}")

    with card_cols[1]:
        st.metric("Source Consensus", alignment_interpretation, delta=f"Alignment: {alignment_score:.0%}")

    with card_cols[2]:
        st.metric("Momentum", f"{momentum_emoji} {momentum_direction.title()}", delta=momentum_text)

    with card_cols[3]:
        if risk_flag:
            st.warning(f"**Key Insight:** {key_insight}")
        else:
            st.info(f"**Key Insight:** {key_insight}")

    # Optional: AI Executive Summary
    if st.session_state.get('enable_ai_features', False):
        with st.expander("🤖 AI Executive Summary", expanded=False):
            ai_summary_key = f"ai_sentiment_summary_{ticker}_{days_back}"

            if ai_summary_key not in st.session_state or st.button("🔄 Regenerate AI Summary"):
                with st.spinner("Generating AI summary..."):
                    ai_summary = generate_ai_sentiment_summary(sentiment_sources, news_df, ticker, summary)
                    st.session_state[ai_summary_key] = ai_summary

            st.markdown(st.session_state.get(ai_summary_key, "AI summary not available"))


def render_sentiment_source_comparison(summary, social_data):
    """Visual comparison of sentiment across different sources"""
    st.markdown("## 📊 Sentiment by Source")

    # Prepare sentiment sources
    sentiment_sources = []

    news_sentiment_score = (summary['avg_sentiment'] + 1) / 2
    sentiment_sources.append({
        'source': 'News Articles',
        'sentiment': summary['sentiment_trend'].title(),
        'score': news_sentiment_score,
        'count': summary['total_articles'],
        'emoji': summary['trend_emoji'],
        'color': '#00CC96' if news_sentiment_score > 0.6 else '#EF553B' if news_sentiment_score < 0.4 else '#636EFA'
    })

    if social_data and social_data.get('twitter', {}).get('available', False):
        twitter = social_data['twitter']
        twitter_score = 0.5
        if twitter['sentiment'] == 'positive':
            twitter_score = 0.65 + (twitter['confidence'] * 0.25)
        elif twitter['sentiment'] == 'negative':
            twitter_score = 0.35 - (twitter['confidence'] * 0.25)

        sentiment_sources.append({
            'source': 'X/Twitter',
            'sentiment': twitter['sentiment'].title(),
            'score': twitter_score,
            'count': f"{twitter['trending_score']}/10 trending",
            'emoji': '📈' if twitter['sentiment'] == 'positive' else '📉',
            'color': '#00CC96' if twitter['sentiment'] == 'positive' else '#EF553B'
        })

    if social_data and social_data.get('google_trends', {}).get('available', False):
        trends = social_data['google_trends']
        trends_score = trends['current_interest'] / 100

        sentiment_sources.append({
            'source': 'Google Trends',
            'sentiment': trends['trend_direction'].title(),
            'score': trends_score,
            'count': f"{trends['current_interest']}/100 interest",
            'emoji': trends['trend_emoji'],
            'color': '#00CC96' if trends['trend_direction'] == 'rising' else '#EF553B'
        })

    # Display comparison cards
    comparison_cols = st.columns(len(sentiment_sources))

    for idx, source_data in enumerate(sentiment_sources):
        with comparison_cols[idx]:
            st.markdown(f"### {source_data['emoji']} {source_data['source']}")
            st.metric("Sentiment", source_data['sentiment'], delta=f"Score: {source_data['score']:.2f}")
            st.caption(f"📊 {source_data['count']}")
            st.progress(float(source_data['score']), text=f"{int(source_data['score'] * 100)}%")

    # Comparison chart
    if len(sentiment_sources) > 1:
        st.markdown("### 📈 Sentiment Comparison Chart")

        fig = go.Figure(data=[
            go.Bar(
                x=[s['source'] for s in sentiment_sources],
                y=[s['score'] for s in sentiment_sources],
                marker=dict(color=[s['color'] for s in sentiment_sources]),
                text=[f"{s['score']:.2f}<br>{s['sentiment']}" for s in sentiment_sources],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title="Sentiment Score Comparison (0=Very Bearish, 1=Very Bullish)",
            yaxis_title="Sentiment Score",
            yaxis=dict(range=[0, 1]),
            height=400,
            showlegend=False
        )

        plotly_full_width(fig)


def render_news_articles_section(ticker, news_df, summary, use_ai, days_back):
    """Detailed news articles analysis"""
    st.markdown("## 📰 News Articles Analysis")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Articles", summary['total_articles'], help="Total news articles found")

    with col2:
        st.metric("Positive", f"{summary['positive_pct']:.1f}%",
                 delta=f"{summary['positive_count']} articles", delta_color="normal")

    with col3:
        st.metric("Negative", f"{summary['negative_pct']:.1f}%",
                 delta=f"{summary['negative_count']} articles", delta_color="inverse")

    with col4:
        trend_label = f"{summary['trend_emoji']} {summary['sentiment_trend'].title()}"
        st.metric("News Sentiment", trend_label, delta=f"{summary['avg_sentiment']:.3f}",
                 help="Average compound sentiment score (-1 to +1)")

    # Sentiment distribution chart
    with st.expander("📊 **View Sentiment Distribution Chart**", expanded=False):
        import plotly.express as px

        sentiment_data = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Count': [summary['positive_count'], summary['negative_count'], summary['neutral_count']],
            'Percentage': [summary['positive_pct'], summary['negative_pct'], summary['neutral_pct']]
        })

        fig = px.bar(
            sentiment_data,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#636EFA'},
            text='Count'
        )

        fig.update_layout(showlegend=False, height=300, margin=dict(l=20, r=20, t=20, b=20))
        plotly_full_width(fig)

    st.divider()

    # Display articles
    st.markdown("### 📰 Recent Articles")

    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"], index=0)

    with filter_col2:
        max_articles = st.number_input("Show articles", min_value=5, max_value=50, value=10, step=5)

    # Apply filters
    filtered_df = news_df.copy()
    if sentiment_filter != "All":
        filtered_df = filtered_df[filtered_df['sentiment'] == sentiment_filter.lower()]

    filtered_df = filtered_df.head(max_articles)

    # Display articles
    for idx, article in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### [{article['title']}]({article['url']})")
                time_ago = format_time_ago(article['published'])
                st.caption(f"📰 {article['source']} • ⏰ {time_ago}")

                if article['summary']:
                    st.write(truncate_text(article['summary'], 200))

            with col2:
                sentiment = article['sentiment']
                emoji = article['emoji']

                if sentiment == 'positive':
                    badge_color = "#00CC96"
                elif sentiment == 'negative':
                    badge_color = "#EF553B"
                else:
                    badge_color = "#636EFA"

                st.markdown(
                    f"""
                    <div style='text-align: center; padding: 10px;
                         background-color: {badge_color}; border-radius: 10px; color: white;'>
                        <div style='font-size: 32px;'>{emoji}</div>
                        <div style='font-size: 14px; font-weight: bold;'>{sentiment.upper()}</div>
                        <div style='font-size: 12px;'>Score: {article['compound']:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if use_ai and 'reasoning' in article and article['reasoning']:
                    with st.expander("🤖 AI Analysis"):
                        st.write(article['reasoning'])
                        if 'impact' in article:
                            impact = article['impact']
                            if impact == 'high':
                                st.error(f"Impact: {impact.upper()}")
                            elif impact == 'medium':
                                st.warning(f"Impact: {impact.title()}")
                            else:
                                st.info(f"Impact: {impact.title()}")

            st.divider()

    # Export option
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Export News to CSV", csv, f"{ticker}_news_{days_back}days.csv",
                          "text/csv", key='download-news')


def render_detailed_social_insights(social_data):
    """Detailed insights from social media sources"""
    st.markdown("## 🔍 Detailed Social Media Insights")

    with st.expander("🔍 **View Detailed Analysis**", expanded=False):
        # Twitter details
        twitter = social_data.get('twitter', {})
        if twitter.get('available', False):
            st.markdown("#### 𝕏 Twitter/X Analysis")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{twitter['confidence']:.0%}")
            with col2:
                st.metric("Volume", twitter['volume'].title())
            with col3:
                st.metric("Trending", f"{twitter['trending_score']}/10")

            if twitter.get('key_topics'):
                st.markdown("**🔥 Trending Topics:**")
                for topic in twitter['key_topics']:
                    st.markdown(f"- {topic}")

            if twitter.get('summary'):
                st.info(f"**Summary:** {twitter['summary']}")

            if twitter.get('bullish_signals') or twitter.get('bearish_signals'):
                col1, col2 = st.columns(2)
                with col1:
                    if twitter.get('bullish_signals'):
                        st.success("**📈 Bullish Signals:**")
                        for signal in twitter['bullish_signals']:
                            st.write(f"✓ {signal}")
                with col2:
                    if twitter.get('bearish_signals'):
                        st.error("**📉 Bearish Signals:**")
                        for signal in twitter['bearish_signals']:
                            st.write(f"✗ {signal}")

            st.divider()

        # Google Trends details
        trends = social_data.get('google_trends', {})
        if trends.get('available', False):
            st.markdown("#### 🔍 Google Trends Analysis")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Interest", f"{trends['current_interest']}/100")
            with col2:
                st.metric("Peak Interest", f"{trends['peak_interest']}/100")
            with col3:
                st.metric("Trend", f"{trends['trend_emoji']} {trends['trend_direction'].title()}")

            if trends.get('related_queries'):
                st.markdown("**🔎 Related Searches:**")
                cols = st.columns(2)
                for idx, query in enumerate(trends['related_queries'][:6]):
                    with cols[idx % 2]:
                        st.markdown(f"• {query}")

            if trends.get('interest_series'):
                st.markdown("**📈 Search Interest Over Time:**")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=trends['interest_series'],
                    mode='lines+markers',
                    name='Search Interest',
                    line=dict(color='#636EFA', width=2),
                    fill='tozeroy'
                ))
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=20, b=20),
                    yaxis_title="Interest (0-100)",
                    xaxis_title="Time",
                    showlegend=False
                )
                plotly_full_width(fig)


def render_sentiment_trends_section(news_df, ticker):
    """Analyze sentiment trends over time"""
    st.markdown("## 📈 Sentiment Trends & Patterns")

    with st.expander("📊 **View Sentiment Timeline**", expanded=False):
        if 'published_date' in news_df.columns:
            news_df_copy = news_df.copy()

            # Ensure datetime
            if not pd.api.types.is_datetime64_any_dtype(news_df_copy['published_date']):
                news_df_copy['published_date'] = pd.to_datetime(news_df_copy['published_date'])

            # Group by date and calculate average sentiment
            daily_sentiment = news_df_copy.groupby(news_df_copy['published_date'].dt.date).agg({
                'compound': 'mean',
                'title': 'count'
            }).reset_index()

            daily_sentiment.columns = ['Date', 'Avg_Sentiment', 'Article_Count']

            # Create dual-axis chart
            from plotly.subplots import make_subplots

            fig = make_subplots(specs=[[{"secondary_y": True}]])

            fig.add_trace(
                go.Scatter(x=daily_sentiment['Date'], y=daily_sentiment['Avg_Sentiment'],
                          mode='lines+markers', name='Sentiment',
                          line=dict(color='#636EFA', width=2)),
                secondary_y=False
            )

            fig.add_trace(
                go.Bar(x=daily_sentiment['Date'], y=daily_sentiment['Article_Count'],
                      name='Article Count', opacity=0.3, marker_color='#00CC96'),
                secondary_y=True
            )

            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
            fig.update_yaxes(title_text="Article Count", secondary_y=True)

            fig.update_layout(height=400, hovermode='x unified')
            plotly_full_width(fig)
        else:
            st.info("Timeline data not available for this dataset")


def render_advanced_modules_section(ticker, news_df, summary):
    """Placeholder for future advanced analysis modules"""
    st.markdown("## 🧩 Advanced Analysis Modules")

    with st.expander("🚀 **Coming Soon: Advanced Features**", expanded=False):
        st.markdown("""
        ### Future Modules:

        - **🎯 Sentiment Impact Analysis**: Correlate sentiment changes with price movements
        - **📊 Topic Modeling**: Identify key themes and topics in news coverage
        - **🔔 Sentiment Alerts**: Set up alerts for significant sentiment shifts
        - **📈 Predictive Sentiment**: Use historical sentiment to predict price direction
        - **🌐 Multi-Language Analysis**: Analyze news from international sources
        - **🤖 Custom AI Models**: Train custom sentiment models on historical data

        These modules will provide deeper, more actionable insights for trading decisions.
        """)


# ========================================
# UTILITY FUNCTIONS
# ========================================

def calculate_sentiment_alignment(sources):
    """Calculate how aligned sentiment sources are (0=high divergence, 1=perfect consensus)"""
    if len(sources) < 2:
        return 1.0, "Single Source", False

    scores = [s['score'] for s in sources]
    mean_score = sum(scores) / len(scores)

    variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5

    alignment_score = max(0, 1 - (std_dev / 0.35))

    if alignment_score > 0.85:
        interpretation = "Strong Consensus"
        risk_flag = False
    elif alignment_score > 0.65:
        interpretation = "Moderate Consensus"
        risk_flag = False
    elif alignment_score > 0.4:
        interpretation = "Mixed Signals"
        risk_flag = True
    else:
        interpretation = "High Divergence"
        risk_flag = True

    return alignment_score, interpretation, risk_flag


def calculate_sentiment_momentum(current_sentiment, news_df):
    """Calculate sentiment momentum by comparing current to 7-day average"""
    if news_df.empty or 'published_date' not in news_df.columns:
        return "stable", "➡️", "Insufficient historical data"

    try:
        news_df_copy = news_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(news_df_copy['published_date']):
            news_df_copy['published_date'] = pd.to_datetime(news_df_copy['published_date'])

        cutoff_date = datetime.now() - timedelta(days=2)
        historical = news_df_copy[news_df_copy['published_date'] < cutoff_date]

        if len(historical) < 3:
            return "stable", "➡️", "Limited historical data"

        historical_avg = historical['sentiment'].mean() if 'sentiment' in historical.columns else 0
        sentiment_change = current_sentiment - historical_avg

        if sentiment_change > 0.15:
            return "improving", "📈", f"+{sentiment_change:.2f} vs baseline"
        elif sentiment_change < -0.15:
            return "deteriorating", "📉", f"{sentiment_change:.2f} vs baseline"
        else:
            return "stable", "➡️", f"{sentiment_change:+.2f} vs baseline"

    except Exception:
        return "stable", "➡️", "Unable to calculate"


def generate_ai_sentiment_summary(sentiment_sources, news_df, ticker, summary):
    """Generate professional AI summary of overall sentiment"""
    model_info = get_configured_model()

        if not model_info:
            return "⚠️ AI model not configured. Please check AI settings."

        sources_text = "\n".join([
            f"- {s['source']}: {s['sentiment']} (score: {s['score']:.2f}, {s['count']})"
            for s in sentiment_sources
        ])

        recent_headlines = []
        if not news_df.empty and 'title' in news_df.columns:
            if 'published_date' in news_df.columns:
                try:
                    recent_headlines = news_df.nlargest(5, 'published_date')['title'].tolist()
                except:
                    recent_headlines = news_df['title'].head(5).tolist()
            else:
                recent_headlines = news_df['title'].head(5).tolist()

        headlines_text = "\n".join([f"- {h}" for h in recent_headlines[:3]])

        prompt = f"""Analyze the sentiment data for {ticker} and provide a concise 2-3 sentence executive summary.

SENTIMENT DATA:
{sources_text}

Overall News Sentiment: {summary['sentiment_trend'].title()} ({summary['avg_sentiment']:.2f})
Total Articles: {summary['total_articles']}

Recent Headlines:
{headlines_text}

Provide a professional, objective summary that:
1. States the overall market sentiment
2. Mentions key drivers or themes
3. Notes any divergence between sources if significant

Keep it under 50 words. Be direct and factual."""

        response = call_ai_model(
            model_info=model_info,
            prompt=prompt,
            max_tokens=150,
            temperature=0.3
        )

        return response.strip()

    except Exception as e:
        return f"⚠️ Unable to generate AI summary: {str(e)}"


if __name__ == "__main__":
    render_page()
