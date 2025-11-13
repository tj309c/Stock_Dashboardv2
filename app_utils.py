import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

@st.cache_data(ttl=600) 
def get_api_status():
    """Checks the status of all critical external APIs."""
    status = {}
    # yfinance
    try:
        test_ticker = yf.Ticker("AAPL") 
        status['yfinance'] = "✅ Responsive" if test_ticker.info else "⚠️ No Data"
    except Exception:
        status['yfinance'] = "❌ Unreachable"

    # Google AI
    status['Google AI'] = "✅ Configured" if st.session_state.get("google_ai_configured") else "❌ Not Configured"
    return status

def create_gauge_chart(value, title, min_val, max_val, lower_is_better=False):
    """Creates a Plotly bullet gauge chart."""
    if lower_is_better:
        colors = ["#28a745", "#ffc107", "#dc3545"] # Green, Yellow, Red
    else:
        colors = ["#dc3545", "#ffc107", "#28a745"] # Red, Yellow, Green

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [min_val, min_val + (max_val - min_val) * 0.4], 'color': colors[0]},
                {'range': [min_val + (max_val - min_val) * 0.4, min_val + (max_val - min_val) * 0.7], 'color': colors[1]},
                {'range': [min_val + (max_val - min_val) * 0.7, max_val], 'color': colors[2]}
            ],
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_radar_chart(data_dict):
    """
    Creates a Plotly radar chart from a dictionary of scores.
    Expects data_dict = {'Metric1': score1, 'Metric2': score2, ...}
    """
    labels = list(data_dict.keys())
    values = list(data_dict.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='Score Breakdown'
    ))
    fig.update_layout(height=300, margin=dict(l=40, r=40, t=40, b=40))
    return fig