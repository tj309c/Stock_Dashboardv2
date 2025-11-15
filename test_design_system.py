"""
Design System Test & Demo
Run this to verify the design system is working correctly
"""
import streamlit as st
from src.ui_utils.design_system import (
    ThemeManager, 
    MetricCardRenderer, 
    ChartTheme,
    get_color, 
    get_change_color,
    format_metric_html
)
import plotly.graph_objects as go

st.set_page_config(page_title="Design System Demo", layout="wide")

st.title("🎨 Design System Demo")
st.markdown("Testing the centralized design system")

# Apply metric card styling
ThemeManager.apply_metric_card_style()

st.markdown("---")

# Section 1: Color Palette
st.header("1. Color Palette")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("Primary Colors")
    st.markdown(f'<div style="background: {get_color("primary")}; padding: 20px; border-radius: 8px; text-align: center;">Primary</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("secondary")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Secondary</div>', unsafe_allow_html=True)

with col2:
    st.subheader("Status Colors")
    st.markdown(f'<div style="background: {get_color("success")}; padding: 20px; border-radius: 8px; text-align: center;">Success</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("warning")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Warning</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("danger")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Danger</div>', unsafe_allow_html=True)

with col3:
    st.subheader("Asset Colors")
    st.markdown(f'<div style="background: {get_color("stocks")}; padding: 20px; border-radius: 8px; text-align: center;">Stocks</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("options")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Options</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("crypto")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Crypto</div>', unsafe_allow_html=True)

with col4:
    st.subheader("Sentiment Colors")
    st.markdown(f'<div style="background: {get_color("bullish")}; padding: 20px; border-radius: 8px; text-align: center;">Bullish 🚀</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("bearish")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Bearish 🐻</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: {get_color("neutral_sentiment")}; padding: 20px; border-radius: 8px; text-align: center; margin-top: 10px;">Neutral ➡️</div>', unsafe_allow_html=True)

st.markdown("---")

# Section 2: Metric Cards
st.header("2. Metric Cards")
st.markdown("Professional metric display with consistent styling")

col1, col2, col3, col4 = st.columns(4)

with col1:
    MetricCardRenderer.render(
        title="Current Price",
        value="$175.50",
        change=2.35,
        asset_type="stocks"
    )

with col2:
    MetricCardRenderer.render(
        title="Options Premium",
        value="$8.25",
        change=-1.20,
        asset_type="options"
    )

with col3:
    MetricCardRenderer.render(
        title="BTC/USD",
        value="$43,250",
        change=5.80,
        asset_type="crypto"
    )

with col4:
    MetricCardRenderer.render(
        title="Portfolio Value",
        value="$125,430",
        change=0.00,
        asset_type="portfolio"
    )

st.markdown("---")

# Section 3: Chart Theming
st.header("3. Chart Theming")
st.markdown("Consistent Plotly chart styling")

# Create sample chart
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[10, 15, 13, 17, 20],
    mode='lines+markers',
    name='Stock Price',
    line=dict(color=get_color('stocks'), width=3)
))

fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[9, 12, 11, 14, 16],
    mode='lines',
    name='SMA',
    line=dict(color=get_color('info'), width=2, dash='dash')
))

# Apply theme
fig = ChartTheme.apply_to_figure(fig)
fig.update_layout(
    title="Sample Stock Chart with Design System Theme",
    xaxis_title="Time",
    yaxis_title="Price ($)",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Section 4: Dynamic Color Selection
st.header("4. Dynamic Color Selection")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Change-based Colors")
    change_value = st.slider("Adjust change value", -10.0, 10.0, 2.5, 0.1)
    color = get_change_color(change_value)
    st.markdown(f'<h2 style="color: {color}; text-align: center;">{change_value:+.2f}%</h2>', unsafe_allow_html=True)

with col2:
    st.subheader("Asset Type Colors")
    asset = st.selectbox("Select asset type", ["stocks", "options", "crypto", "portfolio", "advanced"])
    asset_color = ThemeManager.get_asset_color(asset)
    st.markdown(f'<div style="background: {asset_color}; padding: 30px; border-radius: 12px; text-align: center; font-size: 1.5rem; font-weight: bold;">{asset.upper()}</div>', unsafe_allow_html=True)

st.markdown("---")

# Section 5: Before & After Comparison
st.header("5. Before & After Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("❌ Old Way (Hardcoded)")
    st.code("""
# Hardcoded colors everywhere
st.markdown('<div style="color: #22C55E;">
    Price: $100
</div>', unsafe_allow_html=True)

# Different greens in different files
# File 1: #22C55E
# File 2: #10B981  
# File 3: #16A34A
# Inconsistent! 😱
    """)

with col2:
    st.subheader("✅ New Way (Design System)")
    st.code("""
# Import once, use everywhere
from src.ui_utils.design_system import get_color

st.markdown(f'<div style="color: {get_color("success")};">
    Price: $100
</div>', unsafe_allow_html=True)

# Same green everywhere! 
# Change theme in ONE place 🎉
    """)

st.markdown("---")

# Section 6: Benefits Summary
st.header("6. Benefits Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("**Consistency**")
    st.write("✅ Same colors everywhere")
    st.write("✅ Same spacing")
    st.write("✅ Same styling")

with col2:
    st.info("**Maintainability**")
    st.write("✅ Change theme in 1 file")
    st.write("✅ No searching for colors")
    st.write("✅ Easy to update")

with col3:
    st.warning("**Developer Experience**")
    st.write("✅ IDE autocomplete")
    st.write("✅ Type safety")
    st.write("✅ Self-documenting")

st.markdown("---")

st.success("✅ **Design System is Working!** You can now use these components across all dashboards.")
st.info("💡 **Next Steps:** Replace remaining hardcoded colors in dashboard_options.py, dashboard_crypto.py, etc.")
