"""
Overview Tab Component
Displays price chart, key metrics, and export options
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.ui_utils.formatters import format_currency, format_percentage, format_large_number
from src.ui_utils.design_system import get_color
from src.ui_utils.export_utils import render_export_buttons


def show_overview_tab(data):
    """
    Show overview with price chart and key metrics
    
    Args:
        data: Dict containing ticker, stock_data, df, quote, etc.
    """
    col1, col2 = st.columns([2, 1])
    
    df = data.get("df", pd.DataFrame())
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    
    with col1:
        st.subheader("📈 Price Chart")
        
        if not df.empty:
            _render_price_chart(data, df)
        else:
            st.warning("No price data available")
    
    with col2:
        st.subheader("📊 Key Metrics")
        _render_key_metrics(info)
    
    # Export section
    st.markdown("---")
    _render_export_section(data, df, info)


def _render_price_chart(data, df: pd.DataFrame):
    """Render candlestick chart with volume"""
    from src.ui_utils.loading_indicators import show_skeleton_chart
    
    # Show skeleton while rendering chart
    chart_placeholder = st.empty()
    with chart_placeholder.container():
        st.caption("⏳ Rendering price chart...")
        show_skeleton_chart(height=500)
    
    # Render actual chart
    chart_placeholder.empty()
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.03
    )
    
    # Candlestick
    has_ohlc = all(col in df.columns for col in ['Open', 'High', 'Low', 'Close'])
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'] if has_ohlc else df['Close'],
            high=df['High'] if has_ohlc else df['Close'],
            low=df['Low'] if has_ohlc else df['Close'],
            close=df['Close'],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Moving averages
    if len(df) >= 20:
        sma20 = df['Close'].rolling(20).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=sma20, 
                name="SMA20", 
                line=dict(color=get_color('info'), width=1)
            ),
            row=1, col=1
        )
    
    if len(df) >= 50:
        sma50 = df['Close'].rolling(50).mean()
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=sma50, 
                name="SMA50", 
                line=dict(color=get_color('warning'), width=1)
            ),
            row=1, col=1
        )
    
    # Volume bars
    if 'Open' in df.columns:
        colors = [
            'red' if row['Close'] < row['Open'] else 'green' 
            for idx, row in df.iterrows()
        ]
    else:
        colors = ['blue'] * len(df)
    
    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=df.get('Volume', 0), 
            name="Volume", 
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f"{data['ticker']} - To The Moon! 🚀",
        yaxis_title="Price ($)",
        yaxis2_title="Volume",
        template="plotly_dark",
        height=500,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)


def _render_key_metrics(info: dict):
    """Render key stock metrics with emojis"""
    if not info:
        st.warning("No metrics available")
        return
    
    # Market cap with emoji scale
    market_cap = info.get('marketCap', 0)
    if market_cap > 200e9:
        cap_emoji = "🐋"  # Whale
    elif market_cap > 10e9:
        cap_emoji = "🦍"  # Gorilla
    else:
        cap_emoji = "🐒"  # Monkey
    
    st.markdown(
        f"**{cap_emoji} Market Cap:** {format_large_number(market_cap)}" 
        if market_cap > 0 else "**Market Cap:** N/A"
    )
    
    # P/E Ratio
    pe_ratio = info.get('trailingPE', 0)
    st.markdown(
        f"**P/E Ratio:** {pe_ratio:.2f}" 
        if pe_ratio > 0 else "**P/E Ratio:** N/A"
    )
    
    # EPS
    eps = info.get('trailingEps', 0)
    st.markdown(
        f"**EPS:** {format_currency(eps)}" 
        if eps > 0 else "**EPS:** N/A"
    )
    
    # Dividend with fun text
    div_yield = info.get('dividendYield', 0)
    if div_yield > 0:
        st.markdown(f"**💰 Dividend:** {format_percentage(div_yield*100)} (Free tendies!)")
    else:
        st.markdown("**Dividend:** None (Growth mode 🚀)")
    
    # Beta
    beta = info.get('beta', 1)
    st.markdown(f"**Beta:** {beta:.2f} {'🎢' if beta > 1.5 else '📊'}")
    
    # 52-week range
    st.markdown(f"**52W High:** {format_currency(info.get('fiftyTwoWeekHigh', 0))}")
    st.markdown(f"**52W Low:** {format_currency(info.get('fiftyTwoWeekLow', 0))}")
    
    # Volume analysis
    avg_vol = info.get('averageVolume', 0)
    if avg_vol > 0:
        st.markdown(f"**Avg Volume:** {format_large_number(avg_vol)}")


def _render_export_section(data: dict, df: pd.DataFrame, info: dict):
    """Render export buttons for data download"""
    quote = data.get("quote", {})
    
    render_export_buttons(
        ticker=data.get("ticker", ""),
        data={
            'current_price': quote.get('regularMarketPrice', 0) if quote else 0,
            'change': quote.get('regularMarketChange', 0) if quote else 0,
            'change_pct': f"{quote.get('regularMarketChangePercent', 0):.2f}%" if quote else "N/A",
            'volume': quote.get('regularMarketVolume', 0) if quote else 0,
            'market_cap': info.get('marketCap', 0),
            'technical': {},
            'df': df
        },
        show_csv=True,
        show_chart=False
    )
