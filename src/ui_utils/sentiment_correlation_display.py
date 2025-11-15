"""
Sentiment Correlation Dashboard Display

Visualizes the relationship between sentiment data and market movements.
Integrates with existing Stock_Scrapper sentiment data.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Optional
from datetime import datetime, timedelta

from src.analysis.sentiment_market_correlation import get_sentiment_correlation_analyzer
from src.ui_utils.sentiment_scraper import get_scraper


def show_sentiment_correlation_section(ticker: str, sentiment_df: Optional[pd.DataFrame] = None):
    """
    Display comprehensive sentiment-market correlation analysis.
    
    Args:
        ticker: Stock symbol
        sentiment_df: Optional pre-loaded sentiment data
    """
    st.markdown("---")
    st.subheader("🔗 Sentiment-Market Correlation Analysis")
    
    # Initialize analyzer
    analyzer = get_sentiment_correlation_analyzer()
    
    # Get sentiment data if not provided
    if sentiment_df is None or len(sentiment_df) == 0:
        st.info("💡 Loading sentiment data from Reddit/News sources...")
        scraper = get_scraper()
        sentiment_df = scraper.get_sentiment_data(ticker)
    
    if sentiment_df is None or len(sentiment_df) == 0:
        st.warning("⚠️ No sentiment data available. Cannot perform correlation analysis.")
        st.caption("💡 Tip: Try the 'Ape Sentiment' tab to generate sentiment data first.")
        return
    
    # Generate comprehensive report
    with st.spinner("🔬 Analyzing sentiment-price correlations..."):
        report = analyzer.generate_comprehensive_report(ticker, sentiment_df)
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Trading Signal", 
        "🔗 Correlation Analysis", 
        "🎯 Sentiment Metrics",
        "📈 Market Context"
    ])
    
    with tab1:
        _show_trading_signal(report)
    
    with tab2:
        _show_correlation_analysis(report, sentiment_df)
    
    with tab3:
        _show_sentiment_metrics(report)
    
    with tab4:
        _show_market_context(report)


def _show_trading_signal(report: Dict):
    """Display the derived trading signal."""
    signal = report.get('trading_signal', {})
    
    # Signal header
    direction = signal.get('direction', 'HOLD')
    confidence = signal.get('confidence', 'LOW')
    strength = signal.get('strength', 0)
    
    # Color coding
    if direction == 'BUY':
        color = 'green'
        emoji = '🚀'
    elif direction == 'SELL':
        color = 'red'
        emoji = '📉'
    else:
        color = 'gray'
        emoji = '⏸️'
    
    st.markdown(f"### {emoji} Signal: **:{color}[{direction}]** ({confidence} Confidence)")
    
    # Signal strength gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=strength,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Signal Strength"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 30], 'color': "lightgray"},
                {'range': [30, 70], 'color': "gray"},
                {'range': [70, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Rationale
    st.markdown("#### 📝 Rationale")
    st.info(signal.get('rationale', 'No rationale available'))
    
    # Risk factors
    st.markdown("#### ⚠️ Risk Factors")
    risks = signal.get('risk_factors', [])
    for risk in risks:
        st.markdown(f"- {risk}")
    
    # Data sources used
    st.markdown("#### 📚 Data Sources")
    sources = report.get('data_sources', [])
    st.caption(", ".join(sources))


def _show_correlation_analysis(report: Dict, sentiment_df: pd.DataFrame):
    """Display detailed correlation metrics."""
    correlation = report.get('correlation', {})
    
    if 'error' in correlation:
        st.error(f"❌ Correlation analysis error: {correlation['error']}")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Best Correlation",
            f"{correlation.get('best_correlation', 0):.3f}",
            help="Highest absolute correlation between sentiment and forward returns"
        )
    
    with col2:
        power = correlation.get('predictive_power', 'unknown')
        st.metric(
            "Predictive Power",
            power.upper(),
            help="How well sentiment predicts future price moves"
        )
    
    with col3:
        reliability = correlation.get('reliability', 'unknown')
        st.metric(
            "Reliability",
            reliability.upper(),
            help="Statistical confidence in the correlation"
        )
    
    with col4:
        sample_size = correlation.get('sample_size', 0)
        st.metric(
            "Sample Size",
            sample_size,
            help="Number of data points analyzed"
        )
    
    st.markdown("---")
    
    # Correlation by timeframe
    st.markdown("#### 📊 Correlation by Forward Return Period")
    
    correlations = correlation.get('correlations', {})
    p_values = correlation.get('p_values', {})
    
    if correlations:
        corr_df = pd.DataFrame([
            {
                'Period': period.upper(),
                'Correlation': corr,
                'P-Value': p_values.get(period, 1.0),
                'Significant': '✅' if p_values.get(period, 1.0) < 0.05 else '❌'
            }
            for period, corr in correlations.items()
        ])
        
        st.dataframe(corr_df, use_container_width=True)
        
        # Visualization
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=corr_df['Period'],
            y=corr_df['Correlation'],
            marker_color=['green' if c > 0 else 'red' for c in corr_df['Correlation']],
            text=[f"{c:.3f}" for c in corr_df['Correlation']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title="Sentiment-Price Correlation by Period",
            xaxis_title="Forward Return Period",
            yaxis_title="Correlation Coefficient",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    st.markdown("#### 🧠 Interpretation")
    interpretation = correlation.get('interpretation', 'No interpretation available')
    st.info(interpretation)
    
    # What this means for trading
    st.markdown("#### 💡 Trading Implications")
    
    best_corr = correlation.get('best_correlation', 0)
    
    if best_corr > 0.5:
        st.success(
            "🎯 **STRONG SIGNAL**: Sentiment has historically been a reliable predictor "
            "of price movements for this stock. Consider sentiment as a primary factor "
            "in trading decisions."
        )
    elif best_corr > 0.3:
        st.warning(
            "📊 **MODERATE SIGNAL**: Sentiment shows some predictive power but should "
            "be combined with other indicators (technicals, fundamentals) for optimal results."
        )
    elif best_corr > 0.15:
        st.info(
            "🔍 **WEAK SIGNAL**: Sentiment has limited predictive power. Use as "
            "supplementary information rather than primary trading signal."
        )
    else:
        st.error(
            "❌ **NO SIGNAL**: Sentiment shows negligible correlation with price movements. "
            "This stock may be driven more by fundamentals, insider activity, or macro events."
        )


def _show_sentiment_metrics(report: Dict):
    """Display detailed sentiment breakdown."""
    sentiment = report.get('sentiment_metrics', {})
    
    # Score gauge
    sentiment_score = sentiment.get('sentiment_score', 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Sentiment score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Sentiment Score"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [-100, 100]},
                'bar': {'color': 'green' if sentiment_score > 0 else 'red'},
                'steps': [
                    {'range': [-100, -30], 'color': "lightcoral"},
                    {'range': [-30, 30], 'color': "lightgray"},
                    {'range': [30, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': sentiment_score
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sentiment breakdown pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Positive', 'Neutral', 'Negative'],
            values=[
                sentiment.get('positive_pct', 0),
                sentiment.get('neutral_pct', 0),
                sentiment.get('negative_pct', 0)
            ],
            marker_colors=['green', 'gray', 'red'],
            hole=0.3
        )])
        fig.update_layout(
            title="Sentiment Distribution",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics
    st.markdown("---")
    st.markdown("#### 📊 Detailed Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Positive %",
            f"{sentiment.get('positive_pct', 0):.1f}%",
            help="Percentage of positive sentiment posts/articles"
        )
    
    with col2:
        st.metric(
            "Negative %",
            f"{sentiment.get('negative_pct', 0):.1f}%",
            help="Percentage of negative sentiment posts/articles"
        )
    
    with col3:
        st.metric(
            "Volume",
            sentiment.get('volume', 0),
            help="Total posts/articles analyzed"
        )
    
    with col4:
        quality = sentiment.get('data_quality', 'unknown')
        st.metric(
            "Data Quality",
            quality.upper(),
            help="Assessment of sample size adequacy"
        )
    
    # Average polarity
    avg_polarity = sentiment.get('avg_polarity', 0)
    st.metric(
        "Average Polarity (TextBlob)",
        f"{avg_polarity:.3f}",
        help="Average sentiment polarity from -1 (negative) to +1 (positive)"
    )


def _show_market_context(report: Dict):
    """Display market context and sentiment beta."""
    
    # Market sentiment
    market = report.get('market_sentiment', {})
    
    if market:
        st.markdown("#### 📈 Overall Market Sentiment")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            regime = market.get('regime', 'unknown')
            regime_emoji = '🐂' if regime == 'bull' else '🐻' if regime == 'bear' else '😐'
            st.metric(
                "Market Regime",
                f"{regime_emoji} {regime.upper()}",
                help="Current SPY market regime"
            )
        
        with col2:
            spy_return = market.get('spy_return', 0)
            st.metric(
                "SPY Daily Return",
                f"{spy_return:+.2f}%",
                help="Latest S&P 500 daily return"
            )
        
        with col3:
            volatility = market.get('volatility', 0)
            st.metric(
                "Market Volatility",
                f"{volatility:.2f}%",
                help="10-day rolling volatility"
            )
    
    # Sentiment beta
    sentiment_beta = report.get('sentiment_beta', {})
    
    if sentiment_beta and 'error' not in sentiment_beta:
        st.markdown("---")
        st.markdown("#### 🎯 Sentiment Beta Analysis")
        
        beta_type = sentiment_beta.get('beta_type', 'unknown')
        interpretation = sentiment_beta.get('interpretation', '')
        
        if beta_type == 'high_beta':
            st.info(f"**High Beta Stock**: {interpretation}")
            st.caption(
                "💡 This stock's sentiment follows the overall market. Consider it a "
                "sector/market play rather than company-specific opportunity."
            )
        else:
            st.success(f"**Low Beta Stock**: {interpretation}")
            st.caption(
                "💡 This stock's sentiment is independent of market trends. Price moves "
                "likely driven by company-specific news/events."
            )
        
        # Comparison
        col1, col2 = st.columns(2)
        
        with col1:
            stock_sentiment = sentiment_beta.get('stock_sentiment', 0)
            st.metric(
                f"{report.get('ticker')} Sentiment",
                f"{stock_sentiment:+.1f}",
                help="Stock-specific sentiment score"
            )
        
        with col2:
            market_return = sentiment_beta.get('market_return', 0)
            st.metric(
                "Market Return",
                f"{market_return:+.2f}%",
                help="Overall market return"
            )
    
    # Price momentum context
    st.markdown("---")
    st.markdown("#### 📊 Price Momentum Context")
    
    momentum = report.get('price_momentum', {})
    
    if momentum and 'error' not in momentum:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_return = momentum.get('total_return', 0)
            st.metric(
                "30-Day Return",
                f"{total_return:+.2f}%",
                help="Total return over analysis period"
            )
        
        with col2:
            trend = momentum.get('trend', 'unknown')
            trend_emoji = '📈' if trend == 'bullish' else '📉'
            st.metric(
                "Trend",
                f"{trend_emoji} {trend.upper()}",
                help="10-day vs 20-day SMA"
            )
        
        with col3:
            volatility = momentum.get('volatility', 0)
            st.metric(
                "Volatility",
                f"{volatility:.2f}%",
                help="30-day price volatility"
            )
        
        # Volume analysis
        volume_surge = momentum.get('volume_surge', 0)
        if abs(volume_surge) > 20:
            if volume_surge > 0:
                st.success(f"📊 Volume surge detected: +{volume_surge:.1f}% vs average")
            else:
                st.warning(f"📊 Volume decline: {volume_surge:.1f}% vs average")


def show_sentiment_correlation_tab(ticker: str):
    """
    Full tab view for sentiment correlation analysis.
    Use this in the main stock dashboard.
    """
    st.markdown("### 🔗 How Does Sentiment Correlate with Price?")
    
    st.info(
        "💡 **What this shows**: This analysis examines whether positive/negative sentiment "
        "from Reddit and news actually predicts future price movements. It combines "
        "sentiment data with historical price action to quantify predictive power."
    )
    
    # Get sentiment data
    from src.config.settings import Config
    config_obj = Config()
    api_config = {
        'reddit_client_id': config_obj.get('api.reddit.client_id', ''),
        'reddit_client_secret': config_obj.get('api.reddit.client_secret', ''),
        'reddit_user_agent': config_obj.get('api.reddit.user_agent', 'StocksV2App/1.0'),
        'news_api_key': config_obj.get('api.news.api_key', '')
    }
    
    scraper = get_scraper(api_config)
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Analysis", key="refresh_correlation"):
            scraper.get_sentiment_data.clear()
            st.rerun()
    
    with col2:
        st.caption("Updates sentiment data and recalculates correlations")
    
    # Get sentiment data
    with st.spinner(f"📊 Fetching sentiment data for ${ticker}..."):
        sentiment_df = scraper.get_sentiment_data(ticker)
    
    # Show analysis
    show_sentiment_correlation_section(ticker, sentiment_df)


# Add to dashboard_stocks.py
def integrate_correlation_tab():
    """
    Integration instructions for dashboard_stocks.py:
    
    Add this tab to your existing stock dashboard:
    
    ```python
    from src.ui_utils.sentiment_correlation_display import show_sentiment_correlation_tab
    
    # In your tab section:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Overview", "Valuation", "Ape Sentiment", 
        "Sentiment Correlation",  # NEW TAB
        "Predictive", "Portfolio"
    ])
    
    with tab4:
        show_sentiment_correlation_tab(ticker)
    ```
    """
    pass
