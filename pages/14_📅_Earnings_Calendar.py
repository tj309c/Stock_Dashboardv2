import streamlit as st
from data_fetcher import get_earnings_calendar

def render_page():
    """Main function to render the Earnings Calendar page."""
    st.title("📅 Upcoming Earnings Calendar (Next 30 Days)")
    
    st.info("""
    **API LIMITATION:** This feature uses the free Alpha Vantage API, which has a limit of 25 calls per day. The data is cached for 1 hour to minimize usage.
    """)
    
    try:
        # --- Flexible API key loading ---
        av_key = None
        if st.secrets.get("alpha_vantage") and st.secrets.alpha_vantage.get("API_KEY"):
            av_key = st.secrets.alpha_vantage.API_KEY # Try nested first
        elif st.secrets.get("AV_API_KEY"):
            av_key = st.secrets.AV_API_KEY # Fallback to top-level

        if not av_key:
            raise ValueError("Alpha Vantage API Key not found in Streamlit secrets.")

        with st.spinner("Fetching earnings calendar..."):
            earnings_df = get_earnings_calendar(av_key)
        
        if earnings_df is not None and not earnings_df.empty:
            # Group by date and display
            for report_date, group in earnings_df.groupby('Report Date'):
                st.subheader(report_date.strftime('%Y-%m-%d'))
                st.dataframe(group[['Ticker', 'Company Name', 'Analyst EPS']], use_container_width=True, hide_index=True)
        else:
            st.warning("No upcoming earnings found in the next 30 days, or the API call failed.")
            
    except Exception as e:
        st.error(f"Failed to load or use Alpha Vantage API key. Error: {e}")
        st.warning("""
        Please add your key to `.streamlit/secrets.toml`. Two formats are supported:
        
        **Option 1 (Recommended):**
        ```toml
        AV_API_KEY = "YOUR_KEY"
        ```
        """)

if __name__ == "__main__":
    render_page()