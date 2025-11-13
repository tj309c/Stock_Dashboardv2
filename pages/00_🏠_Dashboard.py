import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from app_logic import initialize_data_and_context

def render_page():
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"🏠 Dashboard for {ticker}")

    # Use the centralized data loading function
    # light_load=True is efficient as this page doesn't need deep financials
    ctx = initialize_data_and_context(ticker, light_load=True)

    # --- Main Page Logic ---
    if not ctx or not ctx.info or ctx.price_data.empty:
        st.error(f"Could not load data for '{ticker}'. Please check the ticker symbol and try again.")
        st.stop()

    # --- COMPANY OVERVIEW ---
    st.subheader("Company Overview")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**Industry:** {ctx.info.get('industry', 'N/A')}")
        st.write(f"**Sector:** {ctx.info.get('sector', 'N/A')}")
        market_cap = ctx.info.get('marketCap')
        market_cap_display = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
        st.write(f"**Market Cap:** {market_cap_display}")
        st.write(f"**Exchange:** {ctx.info.get('exchange', 'N_A')}")
    with col2:
        st.write(ctx.info.get('longBusinessSummary', 'No business summary available.'))

    st.markdown("---")

    # --- KEY METRICS ---
    st.subheader("Key Metrics")
    current_price = ctx.price_data['Close'].iloc[-1]
    previous_close = ctx.price_data['Close'].iloc[-2] if len(ctx.price_data) > 1 else current_price
    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100 if previous_close != 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    fifty_two_week_high = ctx.info.get('fiftyTwoWeekHigh')
    high_display = f"${fifty_two_week_high:.2f}" if isinstance(fifty_two_week_high, (int, float)) else "N/A"
    fifty_two_week_low = ctx.info.get('fiftyTwoWeekLow')
    low_display = f"${fifty_two_week_low:.2f}" if isinstance(fifty_two_week_low, (int, float)) else "N/A"

    col1.metric("Current Price", f"${current_price:.2f}", f"{price_change:.2f} ({percent_change:.2f}%)")
    col2.metric("Volume", f"{ctx.price_data['Volume'].iloc[-1]:,.0f}")
    col3.metric("52 Week High", high_display)
    col4.metric("52 Week Low", low_display)

    st.markdown("---")

    # --- STOCK PRICE CHART ---
    st.subheader("Stock Price Chart")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(f'{ticker} Share Price', 'Volume'),
                        row_heights=[0.7, 0.3])

    fig.add_trace(go.Candlestick(x=ctx.price_data.index,
                                open=ctx.price_data['Open'],
                                high=ctx.price_data['High'],
                                low=ctx.price_data['Low'],
                                close=ctx.price_data['Close'],
                                name='Candlestick'), row=1, col=1)

    fig.add_trace(go.Bar(x=ctx.price_data.index, y=ctx.price_data['Volume'], name='Volume', marker_color='rgba(102,153,255,0.8)'), row=2, col=1)

    if st.session_state.get("theme") == "dark":
        fig.update_layout(paper_bgcolor="#1a1a2e", plot_bgcolor="#1a1a2e", font=dict(color="#e0e0e0"),
                          xaxis=dict(gridcolor="#0f3460"), yaxis=dict(gridcolor="#0f3460"))

    fig.update_layout(xaxis_rangeslider_visible=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- NEWS HEADLINES ---
    st.subheader(f"Latest News for {ticker}")
    if ctx.news_data:
        for article in ctx.news_data[:5]: # Show top 5
            st.markdown(f"**[{article['title']}]({article['link']})**")
            # yfinance provides timestamp as integer, convert it
            published_time = pd.to_datetime(article['providerPublishTime'], unit='s').strftime('%Y-%m-%d %H:%M')
            st.write(f"*{article['publisher']} - {published_time}*")
            st.markdown("---")
    else:
        st.info(f"No recent news found for {ticker} via yfinance.")

    # --- AI ASSISTANT FOR STOCK ANALYSIS ---
    st.subheader("AI Assistant for Stock Insights")
    if st.session_state.get("google_ai_configured", False):
        prompt = st.text_area(
            "Ask the AI for insights (e.g., 'Summarize the recent performance and future outlook of this stock'):",
            key="ai_prompt_dashboard"
        )
        if st.button("Get AI Insights", use_container_width=True):
            if prompt:
                with st.spinner("Generating insights..."):
                    try:
                        model = genai.GenerativeModel('gemini-pro')
                        context = f"Here is some information about {ticker} ({ctx.info.get('longName', 'the company')}):\n"
                        context += f"Industry: {ctx.info.get('industry', 'N/A')}\n"
                        context += f"Sector: {ctx.info.get('sector', 'N/A')}\n"
                        market_cap = ctx.info.get('marketCap')
                        market_cap_display = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
                        context += f"Market Cap: {market_cap_display}\n"
                        context += f"Business Summary: {ctx.info.get('longBusinessSummary', 'N/A')}\n\n"
                        context += "Recent stock performance (last 5 trading days):\n"
                        context += ctx.price_data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5).to_markdown() + "\n\n"
                        context += f"Please answer the following question about {ticker} based on the provided context and general market knowledge:\n{prompt}"

                        response = model.generate_content(context)
                        st.markdown(f'<div class="ai-response-box">{response.text}</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Error generating AI response: {e}")
            else:
                st.warning("Please enter a prompt for the AI assistant.")
    else:
        st.info("Google AI is not configured. Please add your Google AI API key to `.streamlit/secrets.toml` to use this feature.")

if __name__ == "__main__":
    render_page()