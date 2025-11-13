import streamlit as st
import plotly.graph_objects as go
from valuation_models import calculate_ddm, calculate_valuation_score
from ai_services import get_ai_comparables, get_ai_chart_analysis
from technical_analysis import calculate_historical_pe
from app_utils import create_gauge_chart
from app_logic import initialize_data_and_context

def render_page():
    """Main function to render the Price & Technicals page."""
    # --- Get Ticker from Query Params ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"📈 Price & Technicals for {ticker}")

    # --- Initialize Data ---
    ctx = initialize_data_and_context(ticker)

    # FIX: Add a validation check to prevent a crash if data fetching fails.
    # The 'ocf_final' attribute is a proxy for whether full financial data was loaded.
    if ctx is None or ctx.ocf_final is None:
        st.error(f"Could not load the necessary financial data for {ticker} to render this page.")
        st.warning("This can happen if the ticker is invalid or if there are network issues with the data provider.")
        st.stop()

    # --- Define Plotly Template based on Theme ---
    plotly_template = "plotly_white"

    # Create a 25% / 50% / 25% layout
    col1, col2, col3 = st.columns([1, 2, 1])

    # --- Left Column (col1) ---
    with col1:
        st.subheader("Valuation Score")
        with st.spinner("Calculating Overall Valuation Score..."):
            market_cap = ctx.info.get('marketCap', 0) if ctx.info else 0
            fcf_yield = ((ctx.ocf_final - abs(ctx.capex_final)) / market_cap) if market_cap > 0 and ctx.ocf_final is not None and ctx.capex_final is not None else 0
            sector_comps = get_ai_comparables(ctx.ticker_symbol, ctx.info.get('sector', 'default'))

            # FIX: Correct the function call to match its definition (info, comps)
            # The function returns a single score, not a rating and breakdown.
            final_score_num = calculate_valuation_score(ctx.info, sector_comps)
            
            # Gauge Chart for Valuation Score
            fig_gauge = create_gauge_chart(final_score_num * 5, "Valuation Score (vs Sector)", 1, 5, lower_is_better=True)
            fig_gauge.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.metric("Valuation vs Sector", f"{final_score_num:.2%}", help="A score representing how many of the company's valuation multiples are better (lower) than the sector median. Higher is better.")
        
        st.subheader("Technical Signals")
        st.write("Based on the most recent data point:")
        with st.expander("Bullish Signals", expanded=True):
            if ctx.bullish_signals:
                for signal in ctx.bullish_signals:
                    st.success(f"• {signal}")
            else:
                st.info("No bullish signals detected.")
        with st.expander("Bearish Signals", expanded=True):
            if ctx.bearish_signals:
                for signal in ctx.bearish_signals:
                    st.error(f"• {signal}")
            else:
                st.info("No bearish signals detected.")

    # --- Center Column (col2) ---
    with col2:
        st.subheader("Price Chart & Overlays")
        overlay_options = ['Bollinger Bands', 'SMA 50', 'SMA 200']
        selected_overlays = st.multiselect(
            "Select Chart Overlays", options=overlay_options, default=['Bollinger Bands', 'SMA 50', 'SMA 200']
        )

        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['Close'], mode='lines', line_color='blue', name='Close Price'))

        if 'Bollinger Bands' in selected_overlays:
            fig_price.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['BBU_20_2.0_2.0'], fill=None, mode='lines', line_color='grey', name='Upper Band'))
            fig_price.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['BBL_20_2.0_2.0'], fill='tonexty', mode='lines', line_color='grey', name='Lower Band'))
        if 'SMA 50' in selected_overlays:
            fig_price.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['SMA50'], mode='lines', line_color='orange', name='SMA 50'))
        if 'SMA 200' in selected_overlays:
            fig_price.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['SMA200'], mode='lines', line_color='red', name='SMA 200'))
        
        fig_price.update_layout(title=f"{ctx.ticker_symbol} Price Chart", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False, template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_price, use_container_width=True)

        # --- Tabs for Secondary Charts ---
        rsi_tab, macd_tab, adx_tab, obv_tab = st.tabs(['RSI', 'MACD', 'ADX', 'OBV'])
        with rsi_tab:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['RSI_14'], mode='lines', line_color='purple', name='RSI'))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="Relative Strength Index (RSI)", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rsi, use_container_width=True)
        with macd_tab:
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['MACD_12_26_9'], mode='lines', line_color='blue', name='MACD'))
            fig_macd.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['MACDs_12_26_9'], mode='lines', line_color='orange', name='Signal'))
            fig_macd.add_trace(go.Bar(x=ctx.price_data.index, y=ctx.price_data['MACDh_12_26_9'], name='Histogram', marker_color='grey'))
            fig_macd.update_layout(title="Moving Average Convergence Divergence (MACD)", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_macd, use_container_width=True)
        with adx_tab:
            fig_adx = go.Figure()
            fig_adx.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['ADX_14'], mode='lines', line_color='blue', name='ADX'))
            fig_adx.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['DMP_14'], mode='lines', line_color='green', name='DI+ (Bullish)'))
            fig_adx.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['DMN_14'], mode='lines', line_color='red', name='DI- (Bearish)'))
            fig_adx.add_hline(y=25, line_dash="dash", line_color="grey")
            fig_adx.update_layout(title="Average Directional Index (ADX)", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.info("When ADX (blue) is above 25, it signals a strong trend (green > red = uptrend, red > green = downtrend).")
            st.plotly_chart(fig_adx, use_container_width=True)
        with obv_tab:
            fig_obv = go.Figure()
            fig_obv.add_trace(go.Scatter(x=ctx.price_data.index, y=ctx.price_data['OBV'], mode='lines', line_color='purple', name='OBV'))
            fig_obv.update_layout(title="On-Balance Volume (OBV)", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_obv, use_container_width=True)

    # --- Right Column (col3) ---
    with col3:
        st.subheader("AI Chart Analysis")
        if st.button("🤖 Ask AI to Find Chart Patterns"):
            with st.spinner("Analyzing chart for patterns..."):
                ai_analysis = get_ai_chart_analysis(ctx.ticker_symbol, ctx.price_data)
                st.markdown(ai_analysis)
        
        st.subheader("Historical P/E (TTM)")
        pe_data, pe_error = calculate_historical_pe(ctx.price_data, ctx.quarterly_income_data)
        if pe_data is not None:
            fig_pe = go.Figure()
            fig_pe.add_trace(go.Scatter(x=pe_data.index, y=pe_data, mode='lines', line_color='green', name='Historical P/E'))
            fig_pe.update_layout(title="Calculated P/E (TTM) Over Time", yaxis_title="P/E Ratio", template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pe, use_container_width=True)
            st.info("Calculated by dividing the daily 'Close' price by the Trailing Twelve Month (TTM) EPS. Negative P/E periods are excluded.")
        else:
            st.warning(f"Could not generate P/E chart for {ctx.ticker_symbol}. Financial data may be missing.")
            if pe_error:
                with st.expander("See P/E Error Details"):
                    st.error(f"Debug Info: {pe_error}")
                    st.write("P/E calculation looks for 'Basic EPS' or 'Diluted EPS' in quarterly financials. Available rows:")
                    st.write(ctx.quarterly_income_data.index.to_list())

if __name__ == "__main__":
    render_page()