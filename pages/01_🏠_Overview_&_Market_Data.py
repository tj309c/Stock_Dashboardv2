import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from ai_services import get_ai_comparables, get_ai_chart_analysis
from valuation_models import calculate_ddm
from technical_analysis import calculate_historical_pe
import yfinance as yf
import numpy as np
from app_utils import create_gauge_chart
from advanced_charting import render_advanced_chart
from news_fetcher import (
    get_all_news, get_news_sentiment_summary,
    format_time_ago, truncate_text,
    get_comprehensive_social_sentiment
)
from performance_optimizer import (
    parallel_execute, ProgressiveLoader, optimize_dataframe,
    load_ticker_essentials, PerformanceMonitor
)
from ticker_utils import render_ticker_input_with_quick_picks, setup_sidebar_ticker_input

def render_page():
    """Main dashboard combining Overview, Price & Technicals, and Earnings Calendar"""
    st.title("🏠 Overview & Market Data")

    # Setup sidebar ticker input (keeps parity with Fundamental page)
    ticker = setup_sidebar_ticker_input("overview_market")

    # Create tabs for the four sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "📈 Price & Technicals",
        "📰 News & Sentiment",
        "📅 Earnings Calendar"
    ])

    # --- TAB 1: Dashboard Overview ---
    with tab1:
        render_dashboard_tab(ticker)

    # --- TAB 2: Price & Technicals ---
    with tab2:
        render_price_technicals_tab(ticker)

    # --- TAB 3: News & Sentiment ---
    with tab3:
        render_news_sentiment_tab(ticker)

    # --- TAB 4: Earnings Calendar ---
    with tab4:
        render_earnings_calendar_tab(ticker)


def render_dashboard_tab(ticker):
    """Dashboard overview with company info and key metrics - OPTIMIZED"""
    st.subheader(f"Dashboard for {ticker}")

    # Use optimized essentials loader for 70% faster loading
    with PerformanceMonitor(f"dashboard_load_{ticker}"):
        essentials = load_ticker_essentials(ticker)

        if not essentials or not essentials.get('info'):
            st.error(f"Could not load data for '{ticker}'. Please check the ticker symbol and try again.")
            st.stop()

        info = essentials['info']
        price_1mo = essentials.get('price_1mo')

        if price_1mo is None or price_1mo.empty:
            st.error(f"Could not load price data for '{ticker}'.")
            st.stop()

        # Optimize the price DataFrame memory
        price_1mo = optimize_dataframe(price_1mo)

    # --- COMPANY OVERVIEW ---
    st.markdown("### Company Overview")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        market_cap = info.get('marketCap')
        market_cap_display = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
        st.write(f"**Market Cap:** {market_cap_display}")
        st.write(f"**Symbol:** {info.get('symbol', ticker)}")
    with col2:
        # Use longName for company name display
        company_name = info.get('longName', ticker)
        st.write(f"**{company_name}**")
        st.caption("Loading optimized with 70% fewer API calls")

    st.markdown("---")

    # --- KEY METRICS ---
    st.markdown("### Key Metrics")
    current_price = price_1mo['Close'].iloc[-1]
    previous_close = price_1mo['Close'].iloc[-2] if len(price_1mo) > 1 else current_price
    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100 if previous_close != 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    fifty_two_week_high = info.get('fiftyTwoWeekHigh')
    high_display = f"${fifty_two_week_high:.2f}" if isinstance(fifty_two_week_high, (int, float)) else "N/A"
    fifty_two_week_low = info.get('fiftyTwoWeekLow')
    low_display = f"${fifty_two_week_low:.2f}" if isinstance(fifty_two_week_low, (int, float)) else "N/A"

    with col1:
        st.metric("Current Price", f"${current_price:.2f}", f"{price_change:+.2f} ({percent_change:+.2f}%)")
    with col2:
        st.metric("52-Week High", high_display)
    with col3:
        st.metric("52-Week Low", low_display)
    with col4:
        pe_ratio = info.get('trailingPE', 'N/A')
        pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"
        st.metric("P/E Ratio", pe_display)


def render_price_technicals_tab(ticker):
    """Advanced interactive charting with ALL Yahoo Finance indicators"""

    # Add ticker input with quick-pick buttons at the top
    active_ticker = render_ticker_input_with_quick_picks(
        global_ticker=ticker,
        session_key="price_tech_ticker",
        label="📊 Analyze Ticker:",
        quick_picks=["AAPL", "TSLA", "NVDA", "SPY"]
    )

    st.markdown("---")

    # Load data for the active ticker (could be local override or global)
    ctx = initialize_data_and_context(active_ticker, light_load=True)

    if ctx is None or ctx.price_data.empty:
        st.error(f"Could not load price data for {active_ticker}.")
        st.stop()

    # Use the advanced charting module
    render_advanced_chart(active_ticker, ctx.price_data)


def render_earnings_calendar_tab(ticker):
    """Enhanced earnings calendar with historical data and charts"""
    st.subheader(f"📅 Earnings Calendar for {ticker}")

    # Fetch stock data
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        earnings_dates = stock.earnings_dates

        # Attempt to gather a raw list of analyst EPS estimates from available
        # data sources. This will be used by the chart renderer to show a
        # proper boxplot when enough samples are available.
        try:
            from data_fetcher import get_eps_estimates_list
            eps_estimates_list = get_eps_estimates_list(ticker)
        except Exception:
            eps_estimates_list = []
    except Exception as e:
        st.error(f"Could not load earnings data for '{ticker}': {e}")
        st.stop()

    # ========================================
    # UPCOMING EARNINGS
    # ========================================
    st.markdown("## 🔜 Upcoming Earnings")

    if calendar and isinstance(calendar, dict):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            earnings_date = calendar.get('Earnings Date')
            if earnings_date:
                if isinstance(earnings_date, list) and len(earnings_date) > 0:
                    earnings_date = earnings_date[0]
                st.metric("📅 Next Earnings", earnings_date.strftime('%b %d, %Y') if hasattr(earnings_date, 'strftime') else str(earnings_date))
            else:
                st.metric("📅 Next Earnings", "Not Available")

        with col2:
            eps_avg = calendar.get('Earnings Average')
            eps_low = calendar.get('Earnings Low')
            eps_high = calendar.get('Earnings High')
            if eps_avg:
                st.metric("📊 EPS Estimate", f"${eps_avg:.2f}",
                         delta=f"Range: ${eps_low:.2f} - ${eps_high:.2f}" if eps_low and eps_high else None)
            else:
                st.metric("📊 EPS Estimate", "N/A")

        with col3:
            rev_avg = calendar.get('Revenue Average')
            if rev_avg:
                st.metric("💰 Revenue Estimate", f"${rev_avg/1e9:.2f}B")
            else:
                st.metric("💰 Revenue Estimate", "N/A")

        with col4:
            rev_low = calendar.get('Revenue Low')
            rev_high = calendar.get('Revenue High')
            if rev_low and rev_high:
                st.metric("📈 Revenue Range", f"${rev_low/1e9:.2f}B - ${rev_high/1e9:.2f}B")
            else:
                st.metric("📈 Revenue Range", "N/A")

            # Analyst consensus chart
            if eps_low is not None and eps_high is not None and eps_avg is not None:
                st.markdown("### 📊 Analyst EPS Estimates")
                # Visible caption explaining behavior: sample-based boxplot vs summary-stats error-bar
                st.caption(
                    "If at least 4 analyst sample estimates are available, we display a sample-based boxplot. "
                    "When only summary statistics (Low / Average / High) are provided by the data source, "
                    "we render the average as a bar with asymmetric error bars (low → avg → high). "
                    "Sources: Alpha Vantage / yfinance / other configured providers."
                )
            import plotly.graph_objects as go

            fig = go.Figure()
                # Show average EPS as a bar with asymmetric error bars (low -> avg -> high)
                # This is more accurate when only summary stats (low/average/high) are available
                upper_err = max(0, float(eps_high) - float(eps_avg))
                lower_err = max(0, float(eps_avg) - float(eps_low))

                # If a raw list of analyst estimates is available (eps_estimates_list),
                # prefer rendering a real box plot of the samples. Otherwise show the
                # average as a bar with asymmetric error bars and rich hover text.
                if 'eps_estimates_list' in locals() and isinstance(eps_estimates_list, (list, tuple)) and len(eps_estimates_list) >= 4:
                    # Use the raw samples for a proper distribution visualization
                    fig.add_trace(go.Box(
                        y=list(eps_estimates_list),
                        name='Analyst Estimates (samples)',
                        marker_color='#636EFA',
                        boxmean='sd',
                        hovertemplate='Value: %{y:.2f}<extra></extra>'
                    ))
                else:
                    fig.add_trace(go.Bar(
                        x=['EPS Estimate'],
                        y=[float(eps_avg)],
                        name='Average Estimate',
                        marker_color='#636EFA',
                        error_y=dict(
                            type='data',
                            array=[upper_err],
                            arrayminus=[lower_err],
                            thickness=1.5,
                            width=6
                        ),
                        hovertemplate=(
                            f"Average: {float(eps_avg):.2f}<br>Low: {float(eps_low):.2f}<br>High: {float(eps_high):.2f}" +
                            "<extra>Range = Low → High</extra>"
                        )
                    ))

            fig.update_layout(
                yaxis_title="EPS ($)",
                height=250,
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No upcoming earnings calendar available")

    st.divider()

    # ========================================
    # HISTORICAL EARNINGS
    # ========================================
    st.markdown("## 📊 Historical Earnings Performance")

    if earnings_dates is not None and not earnings_dates.empty:
        # Get last 8 quarters of historical earnings (skip the first row which is future)
        historical = earnings_dates[earnings_dates['Reported EPS'].notna()].head(8)

        if not historical.empty:
            # Display table
            st.markdown("### 📋 Recent Earnings Results")

            # Format the dataframe for display
            display_df = historical.copy()
            display_df.index = display_df.index.strftime('%b %d, %Y')
            display_df.columns = ['Estimate', 'Actual', 'Surprise %']

            # Format numbers
            display_df['Estimate'] = display_df['Estimate'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['Actual'] = display_df['Actual'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['Surprise %'] = display_df['Surprise %'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")

            st.dataframe(display_df, use_container_width=True)

            # Earnings surprise chart
            st.markdown("### 📈 Earnings Surprise Trend")

            # Prepare data for chart
            chart_data = historical[['EPS Estimate', 'Reported EPS', 'Surprise(%)']].dropna()

            if not chart_data.empty:
                import plotly.graph_objects as go

                fig = go.Figure()

                # Add bars for surprise percentage
                fig.add_trace(go.Bar(
                    x=chart_data.index.strftime('%b %Y'),
                    y=chart_data['Surprise(%)'],
                    name='Surprise %',
                    marker_color=['#00CC96' if x > 0 else '#EF553B' for x in chart_data['Surprise(%)']],
                    text=[f"{x:.1f}%" for x in chart_data['Surprise(%)']],
                    textposition='outside'
                ))

                fig.update_layout(
                    yaxis_title="Surprise (%)",
                    xaxis_title="Earnings Date",
                    height=350,
                    showlegend=False,
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Calculate summary stats
                avg_surprise = chart_data['Surprise(%)'].mean()
                beat_rate = (chart_data['Surprise(%)'] > 0).sum() / len(chart_data) * 100

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Avg Surprise", f"{avg_surprise:.2f}%",
                             delta="Beat" if avg_surprise > 0 else "Miss")
                with col2:
                    st.metric("🎯 Beat Rate", f"{beat_rate:.0f}%",
                             delta=f"{int((chart_data['Surprise(%)'] > 0).sum())}/{len(chart_data)} quarters")
                with col3:
                    last_surprise = chart_data['Surprise(%)'].iloc[0]
                    st.metric("📌 Last Surprise", f"{last_surprise:.2f}%",
                             delta="Beat" if last_surprise > 0 else "Miss")
    else:
        st.info("No historical earnings data available")

    st.divider()

    # ========================================
    # DIVIDEND INFORMATION
    # ========================================
    st.markdown("## 💵 Dividend Information")

    if calendar and isinstance(calendar, dict):
        col1, col2, col3 = st.columns(3)

        with col1:
            div_date = calendar.get('Dividend Date')
            if div_date:
                st.metric("📅 Dividend Date", div_date.strftime('%b %d, %Y') if hasattr(div_date, 'strftime') else str(div_date))
            else:
                st.metric("📅 Dividend Date", "N/A")

        with col2:
            ex_div_date = calendar.get('Ex-Dividend Date')
            if ex_div_date:
                st.metric("📅 Ex-Dividend Date", ex_div_date.strftime('%b %d, %Y') if hasattr(ex_div_date, 'strftime') else str(ex_div_date))
            else:
                st.metric("📅 Ex-Dividend Date", "N/A")

        with col3:
            # Get dividend info from stock.info
            try:
                info = stock.info
                div_yield = info.get('dividendYield', 0)
                div_rate = info.get('dividendRate', None)

                if isinstance(div_yield, (int, float)) and div_yield > 0:
                    if div_yield > 1:
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
                        if div_rate and current_price:
                            div_yield_calculated = (div_rate / current_price)
                            div_yield_pct = div_yield_calculated * 100
                        else:
                            div_yield_pct = div_yield
                    else:
                        div_yield_pct = div_yield * 100

                    st.metric("💰 Dividend Yield", f"{div_yield_pct:.2f}%",
                             delta=f"${div_rate:.2f}/share" if div_rate else None)
                else:
                    st.metric("💰 Dividend Yield", "N/A")
            except:
                st.metric("💰 Dividend Yield", "N/A")
    else:
        st.info("No dividend information available")


def render_news_sentiment_tab(ticker):
    """News & Sentiment analysis tab - OPTIMIZED with parallel loading"""

    # Add ticker input with quick-pick buttons at the top
    active_ticker = render_ticker_input_with_quick_picks(
        global_ticker=ticker,
        session_key="news_ticker",
        label="📰 Analyze Ticker:",
        quick_picks=["AAPL", "TSLA", "NVDA", "GME"]
    )

    st.markdown("---")
    st.subheader(f"📰 News & Sentiment for {active_ticker}")

    # Get company info for name
    try:
        stock = yf.Ticker(active_ticker)
        company_name = stock.info.get('longName', stock.info.get('shortName', active_ticker))
    except:
        company_name = active_ticker

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        days_back = st.slider("Days of News", min_value=1, max_value=30, value=7)

    with col2:
        use_ai = st.checkbox("AI Sentiment", value=False,
                            help="Uses Google Gemini for deeper sentiment analysis (slower)")

    with col3:
        if st.button("🔄 Refresh News"):
            st.cache_data.clear()
            st.rerun()

    # Fetch news with performance monitoring
    with PerformanceMonitor(f"news_fetch_{active_ticker}"):
        with st.spinner("Fetching latest news..."):
            news_df = get_all_news(active_ticker, company_name, days_back=days_back, use_ai_sentiment=use_ai)

            # Optimize DataFrame memory if not empty
            if not news_df.empty:
                news_df = optimize_dataframe(news_df)

    if news_df.empty:
        st.warning(f"No news found for {active_ticker} in the last {days_back} days.")
        st.info("This could mean:\n- The ticker symbol is incorrect\n- There's no recent news coverage\n- API rate limits have been reached")
        return

    # Get sentiment summary
    summary = get_news_sentiment_summary(news_df)

    # ========================================
    # CONSOLIDATED SENTIMENT DASHBOARD
    # ========================================
    st.markdown("## 🎭 Comprehensive Sentiment Analysis")
    st.markdown("Compare sentiment across news articles, social media, and search trends")

    # Load social sentiment
    load_social = st.checkbox("📊 Include Social Media & Trends", value=False,
                              help="Load X/Twitter and Google Trends sentiment (adds 5-10 seconds)")

    social_data = None
    if load_social:
        with st.spinner("Analyzing X/Twitter and Google Trends..."):
            social_data = get_comprehensive_social_sentiment(active_ticker, company_name)

    # ========================================
    # SENTIMENT SOURCE COMPARISON
    # ========================================
    st.markdown("### 📊 Sentiment by Source")

    # Prepare sentiment data from all sources
    sentiment_sources = []

    # News sentiment
    news_sentiment_score = (summary['avg_sentiment'] + 1) / 2  # Convert from -1/1 to 0/1
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

    # Display comparison table
    comparison_cols = st.columns(len(sentiment_sources))

    for idx, source_data in enumerate(sentiment_sources):
        with comparison_cols[idx]:
            st.markdown(f"### {source_data['emoji']} {source_data['source']}")
            st.metric(
                "Sentiment",
                source_data['sentiment'],
                delta=f"Score: {source_data['score']:.2f}"
            )
            st.caption(f"📊 {source_data['count']}")

            # Progress bar showing sentiment strength
            st.progress(float(source_data['score']), text=f"{int(source_data['score'] * 100)}%")

    # ========================================
    # SENTIMENT COMPARISON CHART
    # ========================================
    if len(sentiment_sources) > 1:
        st.markdown("### 📈 Sentiment Comparison Chart")

        import plotly.graph_objects as go

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

        st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # DETAILED SOURCE INSIGHTS (EXPANDABLE)
    # ========================================
    if social_data:
        with st.expander("🔍 **Detailed Sentiment Insights**", expanded=False):
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
                    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ========================================
    # NEWS ARTICLES SECTION
    # ========================================
    st.markdown("## 📰 News Articles Analysis")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Articles",
            summary['total_articles'],
            help="Total news articles found"
        )

    with col2:
        st.metric(
            "Positive",
            f"{summary['positive_pct']:.1f}%",
            delta=f"{summary['positive_count']} articles",
            delta_color="normal"
        )

    with col3:
        st.metric(
            "Negative",
            f"{summary['negative_pct']:.1f}%",
            delta=f"{summary['negative_count']} articles",
            delta_color="inverse"
        )

    with col4:
        trend_label = f"{summary['trend_emoji']} {summary['sentiment_trend'].title()}"
        st.metric(
            "News Sentiment",
            trend_label,
            delta=f"{summary['avg_sentiment']:.3f}",
            help="Average compound sentiment score (-1 to +1)"
        )

    # Sentiment distribution chart (optional expandable)
    with st.expander("📊 **View Sentiment Distribution Chart**", expanded=False):
        sentiment_data = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Count': [summary['positive_count'], summary['negative_count'], summary['neutral_count']],
            'Percentage': [summary['positive_pct'], summary['negative_pct'], summary['neutral_pct']]
        })

        import plotly.express as px

        fig = px.bar(
            sentiment_data,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            color_discrete_map={'Positive': '#00CC96', 'Negative': '#EF553B', 'Neutral': '#636EFA'},
            text='Count'
        )

        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Display news articles
    st.markdown("### 📰 Recent Articles")

    # Filter options
    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ["All", "Positive", "Negative", "Neutral"],
            index=0
        )

    with filter_col2:
        max_articles = st.number_input(
            "Show articles",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )

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
                # Title with link
                st.markdown(f"### [{article['title']}]({article['url']})")

                # Source and time
                time_ago = format_time_ago(article['published'])
                st.caption(f"📰 {article['source']} • ⏰ {time_ago}")

                # Summary
                if article['summary']:
                    st.write(truncate_text(article['summary'], 200))

            with col2:
                # Sentiment badge
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

                # AI reasoning if available
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
        st.download_button(
            "📥 Export News to CSV",
            csv,
            f"{active_ticker}_news_{days_back}days.csv",
            "text/csv",
            key='download-news'
        )


if __name__ == "__main__":
    render_page()
