"""
Professional visualization components for Fear & Greed Index
Tier 1-3 features organized for institutional-grade analysis
"""

import streamlit as st
from app_utils import plotly_full_width
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def render_component_breakdown(components, weights, overall_score):
    """
    TIER 1: Component breakdown waterfall chart
    Shows which indicators are driving the current score
    """
    st.markdown("#### 📊 Component Breakdown")

    from fear_greed_history import calculate_component_contributions
    contributions = calculate_component_contributions(components, weights)

    if not contributions:
        st.warning("No component data available")
        return

    # Create waterfall chart
    fig = go.Figure()

    # Prepare data for waterfall
    component_names = []
    component_values = []
    component_colors = []

    for contrib in contributions:
        name = contrib['component'].replace('_', ' ').title()
        score = contrib['score']
        weight = contrib['weight']

        component_names.append(f"{name}<br>({weight*100:.0f}% weight)")
        component_values.append(score)

        # Color code based on score
        if score >= 75:
            component_colors.append('#00CC96')  # Extreme greed - green
        elif score >= 55:
            component_colors.append('#26C281')  # Greed - light green
        elif score >= 45:
            component_colors.append('#FED766')  # Neutral - yellow
        elif score >= 25:
            component_colors.append('#FFB84D')  # Fear - orange
        else:
            component_colors.append('#EF553B')  # Extreme fear - red

    # Create horizontal bar chart
    fig = go.Figure(go.Bar(
        y=component_names,
        x=component_values,
        orientation='h',
        marker=dict(
            color=component_colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=[f"{v:.0f}" for v in component_values],
        textposition='auto',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}/100<extra></extra>'
    ))

    # Add reference line at 50 (neutral)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="Neutral (50)")

    # Add overall score line
    fig.add_vline(x=overall_score, line_dash="solid", line_color="white", line_width=2,
                  annotation_text=f"Overall: {overall_score}", annotation_position="top")

    fig.update_layout(
        title="Component Scores (0=Fear, 100=Greed)",
        xaxis_title="Score",
        yaxis_title="",
        height=max(300, len(contributions) * 50),
        showlegend=False,
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=11)
    )

    plotly_full_width(fig)

    # Show key drivers
    top_fearful = [c for c in contributions if c['score'] < 35]
    top_greedy = [c for c in contributions if c['score'] > 65]

    if top_fearful or top_greedy:
        st.markdown("**Key Drivers:**")
        if top_fearful:
            fear_list = ", ".join([c['component'].replace('_', ' ').title() for c in top_fearful])
            st.markdown(f"🔴 **Fearful**: {fear_list}")
        if top_greedy:
            greed_list = ", ".join([c['component'].replace('_', ' ').title() for c in top_greedy])
            st.markdown(f"🟢 **Greedy**: {greed_list}")


def render_trend_analysis(history_manager, current_score):
    """
    TIER 1: 7/30-day trend line with momentum indicators
    """
    st.markdown("#### 📈 Trend Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # 7-day trend
        trend_7d = history_manager.get_trend(days=7)
        trend_emoji = "📈" if trend_7d['trend_direction'] == 'bullish' else ("📉" if trend_7d['trend_direction'] == 'bearish' else "➡️")
        trend_color = "green" if trend_7d['trend_direction'] == 'bullish' else ("red" if trend_7d['trend_direction'] == 'bearish' else "gray")

        st.metric(
            "7-Day Trend",
            f"{trend_emoji} {trend_7d['trend_direction'].title()}",
            delta=f"{trend_7d['change']:+.1f} pts",
            delta_color="normal" if trend_7d['change'] > 0 else "inverse"
        )
        st.caption(f"Momentum: {trend_7d['momentum']:+.1f} pts")

    with col2:
        # 30-day trend
        trend_30d = history_manager.get_trend(days=30)
        trend_emoji = "📈" if trend_30d['trend_direction'] == 'bullish' else ("📉" if trend_30d['trend_direction'] == 'bearish' else "➡️")

        st.metric(
            "30-Day Trend",
            f"{trend_emoji} {trend_30d['trend_direction'].title()}",
            delta=f"{trend_30d['change']:+.1f} pts",
            delta_color="normal" if trend_30d['change'] > 0 else "inverse"
        )
        st.caption(f"Slope: {trend_30d['slope']:.2f}")

    # Historical chart
    df = history_manager.get_dataframe(days=30)

    if len(df) >= 2:
        fig = go.Figure()

        # Main line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['score'],
            mode='lines+markers',
            name='Fear & Greed',
            line=dict(color='#636EFA', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(99, 110, 250, 0.1)',
            hovertemplate='<b>%{x|%Y-%m-%d %H:%M}</b><br>Score: %{y:.0f}<extra></extra>'
        ))

        # Add zone colors
        fig.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1, layer="below", line_width=0)
        fig.add_hrect(y0=25, y1=45, fillcolor="orange", opacity=0.1, layer="below", line_width=0)
        fig.add_hrect(y0=45, y1=55, fillcolor="yellow", opacity=0.1, layer="below", line_width=0)
        fig.add_hrect(y0=55, y1=75, fillcolor="lightgreen", opacity=0.1, layer="below", line_width=0)
        fig.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.1, layer="below", line_width=0)

        # Add current point
        fig.add_trace(go.Scatter(
            x=[df['timestamp'].iloc[-1]],
            y=[current_score],
            mode='markers',
            name='Current',
            marker=dict(size=12, color='yellow', line=dict(color='white', width=2)),
            showlegend=False
        ))

        fig.update_layout(
            title="30-Day Fear & Greed History",
            xaxis_title="Date",
            yaxis_title="Score (0=Fear, 100=Greed)",
            height=350,
            yaxis=dict(range=[0, 100]),
            hovermode='x unified',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        plotly_full_width(fig)
    else:
        st.info("📊 Collecting historical data... Check back after a few hours for trend analysis")


def render_divergence_alerts(divergences):
    """
    TIER 1: Divergence detection alerts
    """
    if not divergences:
        st.success("✅ No divergences detected - all indicators aligned")
        return

    st.markdown("#### ⚠️ Divergence Alerts")

    for div in divergences:
        severity = div['severity']

        if severity == 'critical':
            st.error(f"🚨 **{div['type']}**: {div['message']}")
        elif severity == 'high':
            st.warning(f"⚠️ **{div['type']}**: {div['message']}")
        else:
            st.info(f"ℹ️ **{div['type']}**: {div['message']}")


def render_percentile_analysis(history_manager, current_score):
    """
    TIER 2: Historical percentile analysis
    """
    st.markdown("#### 📊 Historical Context")

    col1, col2, col3 = st.columns(3)

    percentile_30d = history_manager.get_percentile(current_score, days=30)
    percentile_90d = history_manager.get_percentile(current_score, days=90)

    with col1:
        if percentile_30d is not None:
            st.metric(
                "30-Day Percentile",
                f"{percentile_30d:.0f}%",
                help="Current score compared to last 30 days"
            )
            if percentile_30d > 80:
                st.caption("🔥 Near 30-day high")
            elif percentile_30d < 20:
                st.caption("❄️ Near 30-day low")
        else:
            st.caption("Insufficient data")

    with col2:
        if percentile_90d is not None:
            st.metric(
                "90-Day Percentile",
                f"{percentile_90d:.0f}%",
                help="Current score compared to last 90 days"
            )
            if percentile_90d > 90:
                st.caption("⚠️ Extreme high")
            elif percentile_90d < 10:
                st.caption("⚠️ Extreme low")
        else:
            st.caption("Insufficient data")

    with col3:
        # Show interpretation
        if percentile_90d is not None:
            if percentile_90d > 75:
                st.metric("Interpretation", "Unusually High", delta="Caution")
                st.caption("📉 Consider taking profits")
            elif percentile_90d < 25:
                st.metric("Interpretation", "Unusually Low", delta="Opportunity")
                st.caption("📈 Potential buy signal")
            else:
                st.metric("Interpretation", "Normal Range")
                st.caption("➡️ No extreme signal")


def render_sector_rotation_heatmap(sector_data):
    """
    TIER 2: Sector rotation heatmap showing defensive vs cyclical
    """
    if not sector_data:
        st.warning("Sector data unavailable")
        return

    st.markdown("#### 🎯 Sector Sentiment Heatmap")

    # Categorize sectors (matching names from fetch_sector_performance)
    defensive = ['Utilities', 'Consumer Staples', 'Healthcare']
    cyclical = ['Technology', 'Consumer Discretionary', 'Industrials', 'Materials']
    sensitive = ['Financials', 'Energy', 'Real Estate', 'Communication']

    sectors = []
    categories = []
    returns = []

    for sector, data in sector_data.items():
        # Use 'change_1d' as the primary metric (daily change)
        # Fallback to 'change_pct' for compatibility with other data sources
        if 'change_1d' in data:
            sectors.append(sector)
            returns.append(data['change_1d'])

            if sector in defensive:
                categories.append('Defensive')
            elif sector in cyclical:
                categories.append('Cyclical')
            else:
                categories.append('Sensitive')
        elif 'change_pct' in data:
            sectors.append(sector)
            returns.append(data['change_pct'])

            if sector in defensive:
                categories.append('Defensive')
            elif sector in cyclical:
                categories.append('Cyclical')
            else:
                categories.append('Sensitive')

    if not sectors:
        st.info("No sector performance data available")
        return

    df = pd.DataFrame({
        'Sector': sectors,
        'Category': categories,
        'Return': returns
    })

    # Create heatmap
    fig = px.bar(
        df,
        x='Return',
        y='Sector',
        color='Return',
        color_continuous_scale=['#EF553B', '#FED766', '#00CC96'],
        color_continuous_midpoint=0,
        orientation='h',
        text=df['Return'].apply(lambda x: f"{x:+.2f}%"),
        hover_data={'Category': True, 'Return': ':.2f%'}
    )

    fig.update_layout(
        title="Sector Performance - 1 Day (% Change)",
        xaxis_title="Return (%)",
        yaxis_title="",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_traces(textposition='auto')

    plotly_full_width(fig)

    # Rotation analysis
    defensive_avg = df[df['Category'] == 'Defensive']['Return'].mean() if len(df[df['Category'] == 'Defensive']) > 0 else 0
    cyclical_avg = df[df['Category'] == 'Cyclical']['Return'].mean() if len(df[df['Category'] == 'Cyclical']) > 0 else 0

    if defensive_avg > cyclical_avg + 0.5:
        st.warning("🛡️ **Defensive Rotation**: Defensive sectors outperforming → Risk-off sentiment")
    elif cyclical_avg > defensive_avg + 0.5:
        st.success("🚀 **Cyclical Rotation**: Cyclical sectors leading → Risk-on sentiment")
    else:
        st.info("⚖️ **Balanced**: No clear sector rotation signal")


def render_cross_asset_dashboard():
    """
    TIER 3: Cross-asset dashboard (bonds, commodities, FX)
    """
    st.markdown("#### 🌐 Cross-Asset Sentiment")

    import yfinance as yf

    try:
        # Fetch cross-asset data
        tickers = {
            'TLT': '20Y Treasury',
            'GLD': 'Gold',
            'DXY': 'US Dollar',
            'USO': 'Oil',
            'UUP': 'Dollar Index'
        }

        data = {}
        for ticker, name in tickers.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period='5d')
                if not hist.empty:
                    change = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
                    data[name] = change
            except:
                continue

        if data:
            col1, col2, col3, col4 = st.columns(4)

            cols = [col1, col2, col3, col4]
            for idx, (asset, change) in enumerate(data.items()):
                with cols[idx % 4]:
                    st.metric(
                        asset,
                        f"{change:+.2f}%",
                        delta="5-day change"
                    )

            # Interpretation
            gold_up = data.get('Gold', 0) > 1
            bonds_up = data.get('20Y Treasury', 0) > 0.5
            dollar_up = data.get('US Dollar', 0) > 0 or data.get('Dollar Index', 0) > 0

            st.markdown("**Market Regime:**")
            if gold_up and bonds_up:
                st.warning("🛡️ **Flight to Safety**: Gold and bonds rising → Fear")
            elif not gold_up and not bonds_up:
                st.success("🚀 **Risk-On**: Safe havens weak → Greed")
            else:
                st.info("⚖️ **Mixed Signals**: Cross-asset divergence")

        else:
            st.warning("Unable to fetch cross-asset data")

    except Exception as e:
        st.error(f"Error loading cross-asset data: {e}")


def render_options_flow_detail(put_call_ratio):
    """
    TIER 3: Options flow detail breakdown
    """
    st.markdown("#### 📊 Options Flow Analysis")

    # Show put/call ratio
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Put/Call Ratio", f"{put_call_ratio:.3f}")

    with col2:
        if put_call_ratio > 1.2:
            sentiment = "Fearful"
            emoji = "😰"
            color = "red"
        elif put_call_ratio < 0.8:
            sentiment = "Greedy"
            emoji = "😊"
            color = "green"
        else:
            sentiment = "Neutral"
            emoji = "😐"
            color = "gray"

        st.metric("Sentiment", f"{emoji} {sentiment}")

    with col3:
        # Historical context
        if put_call_ratio > 1.3:
            st.caption("🔴 Extreme hedging")
        elif put_call_ratio < 0.7:
            st.caption("🟢 Call buying surge")
        else:
            st.caption("⚪ Normal range")

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=put_call_ratio,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Put/Call Ratio"},
        gauge={
            'axis': {'range': [0, 2]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.7], 'color': "#00CC96"},
                {'range': [0.7, 0.9], 'color': "#26C281"},
                {'range': [0.9, 1.1], 'color': "#FED766"},
                {'range': [1.1, 1.3], 'color': "#FFB84D"},
                {'range': [1.3, 2], 'color': "#EF553B"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.0
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    plotly_full_width(fig)

    st.caption("**Interpretation**: Ratio > 1.0 means more puts than calls (bearish hedging)")