"""
Debug script to check Treasury Yield data from FRED API
"""
import streamlit as st
from app_utils import display_dataframe_full_width
import requests
import pandas as pd
from datetime import datetime

st.title("🔍 Treasury Yield Curve Debugger")

st.markdown("""
This tool helps diagnose issues with the Treasury Yield Curve signal.
It fetches the latest data from the FRED API and shows you the actual values.
""")

# Get FRED API key from secrets
fred_api_key = st.secrets.get("FRED_API_KEY")

if not fred_api_key:
    st.error("❌ FRED_API_KEY not found in secrets. Please add it to .streamlit/secrets.toml")
    st.stop()

st.success(f"✅ FRED API Key found: {fred_api_key[:10]}...")

# Fetch Treasury data
st.markdown("## Fetching Treasury Yield Data")

series_to_check = {
    'DGS10': '10-Year Treasury Yield',
    'DGS2': '2-Year Treasury Yield',
    'DGS30': '30-Year Treasury Yield',
    'DGS5': '5-Year Treasury Yield',
}

@st.cache_data(ttl=60)
def fetch_fred_series(series_id, api_key):
    """Fetch a FRED series and return the data"""
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&limit=30"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None, f"HTTP Error {response.status_code}"

        data = response.json()
        observations = data.get('observations', [])

        if not observations:
            return None, "No observations returned"

        # Convert to DataFrame
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])

        if df.empty:
            return None, "All values are NaN"

        df = df.sort_values('date')
        return df, None
    except Exception as e:
        return None, str(e)

# Fetch all series
results = {}
for series_id, name in series_to_check.items():
    with st.spinner(f"Fetching {name}..."):
        df, error = fetch_fred_series(series_id, fred_api_key)
        results[name] = {
            'series_id': series_id,
            'df': df,
            'error': error
        }

# Display results
st.markdown("## 📊 Treasury Yield Data")

for name, result in results.items():
    st.markdown(f"### {name} ({result['series_id']})")

    if result['error']:
        st.error(f"❌ Error: {result['error']}")
    elif result['df'] is not None and not result['df'].empty:
        df = result['df']
        current_value = df['value'].iloc[-1]
        current_date = df['date'].iloc[-1]
        prev_value = df['value'].iloc[-2] if len(df) > 1 else None

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Value", f"{current_value:.3f}%")
        with col2:
            st.metric("Last Updated", current_date.strftime('%Y-%m-%d'))
        with col3:
            if prev_value is not None:
                change = current_value - prev_value
                st.metric("Change from Previous", f"{change:+.3f}%")

        # Show last 10 values
        with st.expander(f"📈 Last 10 observations for {name}"):
            display_df = df[['date', 'value']].tail(10).copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df.columns = ['Date', 'Yield (%)']
            display_dataframe_full_width(display_df)
    else:
        st.warning("⚠️ No data available")

    st.markdown("---")

# Calculate yield curve spread
st.markdown("## 📉 Yield Curve Analysis")

treasury_10y = results.get('10-Year Treasury Yield', {}).get('df')
treasury_2y = results.get('2-Year Treasury Yield', {}).get('df')

if treasury_10y is not None and treasury_2y is not None and not treasury_10y.empty and not treasury_2y.empty:
    current_10y = treasury_10y['value'].iloc[-1]
    current_2y = treasury_2y['value'].iloc[-1]
    spread = current_10y - current_2y

    st.markdown(f"### Yield Curve Spread (10Y - 2Y)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("10-Year Yield", f"{current_10y:.3f}%")

    with col2:
        st.metric("2-Year Yield", f"{current_2y:.3f}%")

    with col3:
        st.metric("Spread", f"{spread:+.3f}%",
                 delta="Inverted" if spread < 0 else "Normal",
                 delta_color="inverse" if spread < 0 else "normal")

    # Interpretation
    st.markdown("### 🔍 Interpretation")

    if spread < -0.2:
        st.error(f"⚠️ **Inverted Yield Curve** (spread: {spread:.3f}%)")
        st.markdown("The yield curve is significantly inverted. This is historically a strong recession warning signal.")
    elif spread < 0:
        st.warning(f"⚠️ **Near Inversion** (spread: {spread:.3f}%)")
        st.markdown("The yield curve is slightly inverted. This warrants caution.")
    elif spread < 0.5:
        st.info(f"➡️ **Flat Yield Curve** (spread: {spread:.3f}%)")
        st.markdown("The yield curve is relatively flat. Economic slowdown is possible.")
    else:
        st.success(f"✅ **Normal Yield Curve** (spread: {spread:.3f}%)")
        st.markdown("The yield curve is normal and healthy.")

    # Compare with current real-world data
    st.markdown("### 🌐 Compare with Real-World Data")
    st.markdown("""
    To verify if this data is accurate, you can check:
    - [US Treasury Website](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield)
    - [CNBC Treasury Rates](https://www.cnbc.com/quotes/US10Y)
    - [Bloomberg Markets](https://www.bloomberg.com/markets/rates-bonds/government-bonds/us)

    If the FRED data doesn't match current market data, it may be:
    1. **Delayed update**: FRED updates Treasury data daily, usually by end of business day
    2. **Weekend/Holiday**: No new data on weekends or market holidays
    3. **API cache**: The data might be cached
    """)

else:
    st.error("❌ Cannot calculate yield curve spread - missing Treasury data")

# Show what the app is currently showing
st.markdown("## 🔧 What's in the App Right Now?")

st.markdown("""
The yield curve calculation in the app is at:
- File: `pages/01_📊_Market_Overview_&_Economy.py`
- Function: `calculate_yield_curve_signal()` (line 1367)
- Logic: `spread = treasury_10y['current'] - treasury_2y['current']`

The app considers the curve:
- **Inverted**: spread < -0.2%
- **Near Inversion**: spread < 0%
- **Flat**: spread < 0.5%
- **Normal**: spread >= 0.5%
""")

st.markdown("---")
st.caption("💡 This is a diagnostic tool. To fix issues, check the FRED API data freshness and compare with real-time market data.")