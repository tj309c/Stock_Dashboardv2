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


def normalize_dividend_yield(info: dict, current_price: float | None = None, max_reasonable_pct: float = 50.0):
    """Normalize and validate dividend yield from provider info.

    Strategy (preferred -> fallback):
      1. If dividendRate and current_price are available, compute dividendRate / current_price * 100.
      2. Else, use dividendYield field. If it's fractional (<= 1) convert to percent (*100).
      3. If dividendYield looks like a raw percent (1 < value <= max_reasonable_pct) accept it.

    Protect against implausible yields by returning None when computed percentage
    is larger than `max_reasonable_pct`.

    Returns: (yield_pct: float | None, source: str)
    """
    try:
        # Prefer explicit rate / current price when possible
        div_rate = info.get('dividendRate')
        # Accept either explicit current_price param or info dict values commonly used
        price = current_price if current_price is not None else info.get('currentPrice') or info.get('regularMarketPrice')

        if div_rate is not None and price:
            try:
                yield_pct = float(div_rate) / float(price) * 100.0
                if 0 < yield_pct <= max_reasonable_pct:
                    return yield_pct, 'computed_from_rate_and_price'
                else:
                    # Implausible value
                    return None, 'suspicious_computed_value'
            except Exception:
                pass

        # Fallback to dividendYield field
        div_yield = info.get('dividendYield')
        if isinstance(div_yield, (int, float)):
            try:
                if 0 < div_yield <= 1:
                    yield_pct = float(div_yield) * 100.0
                    if yield_pct <= max_reasonable_pct:
                        return yield_pct, 'dividendYield_fraction'
                    else:
                        return None, 'suspicious_dividendYield_fraction'
                elif 1 < div_yield <= max_reasonable_pct:
                    # Already a percent value
                    return float(div_yield), 'dividendYield_raw_percent'
                else:
                    # Implausible (e.g., >max_reasonable_pct)
                    return None, 'suspicious_dividendYield'
            except Exception:
                pass

        # Nothing usable found
        return None, 'not_available'
    except Exception:
        return None, 'error'


def format_money(value, currency_symbol='$', decimals: int = 2, show_symbol: bool = True):
    """Format a number into a human-friendly currency string.

    - Uses thousands separators and fixed decimals.
    - If value is None or not a number, returns a short placeholder 'N/A'.
    - `show_symbol=False` will omit the currency symbol (useful for indices like VIX).

    Examples:
      format_money(12345.678) -> "$12,345.68"
      format_money(1234.5, show_symbol=False) -> "1,234.50"
    """
    try:
        if value is None:
            return "N/A"

        # cast to float for robust formatting
        n = float(value)

        fmt = f"{{:,.{decimals}f}}"
        formatted = fmt.format(n)

        return f"{currency_symbol}{formatted}" if show_symbol else formatted
    except Exception:
        return "N/A"


def display_dataframe_full_width(df, height: int | None = None, **kwargs):
    """Display a DataFrame using the container full width without relying on use_container_width.

    - Uses a container to ensure the component occupies its available width.
    - Accepts same arguments as st.dataframe (height) and passes additional kwargs through.
    """
    container = st.container()
    # st.dataframe enforces that height must be an int or 'stretch' — don't pass None explicitly
    if height is None:
        return container.dataframe(df, **kwargs)
    return container.dataframe(df, height=height, **kwargs)


def plotly_full_width(fig, height: int | None = None, **kwargs):
    """Render a Plotly figure reliably across Streamlit versions without use_container_width.

    - Sets autosize in the figure layout and applies optional height.
    - Passes other kwargs to st.plotly_chart.
    """
    try:
        # Update layout to be responsive
        if hasattr(fig, 'update_layout'):
            fig.update_layout(autosize=True)
            if height is not None:
                fig.update_layout(height=height)
    except Exception:
        pass

    return st.plotly_chart(fig, **kwargs)


def full_width_button(*args, **kwargs):
    """Create a full-width button by placing it into a single-column container.

    Usage mirrors st.button signature. Returns the boolean result of the button press.
    """
    col = st.columns([1])[0]
    return col.button(*args, **kwargs)