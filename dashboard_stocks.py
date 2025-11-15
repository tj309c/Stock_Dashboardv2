"""
Stocks Dashboard - Diamond Hands Edition 💎🙌
For analyzing stonks with ape-approved metrics
Where technical analysis meets autism

Robinhood-inspired aesthetics with expert-level analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging

# Initialize logger
logger = logging.getLogger(__name__)
from wsb_quotes import (get_confidence_message, get_sentiment_comment, 
                        get_technical_comment, get_loading_message, 
                        get_error_message, get_dashboard_tagline)
# Migrated to new formatters module - eliminates duplicate code across dashboards
from src.ui_utils.formatters import (format_currency, format_percentage, format_large_number,
                                  format_price, get_color_for_value)
from src.ui_utils.design_system import (ThemeManager, get_color, get_change_color, MetricCardRenderer)
from utils import (safe_get, safe_divide, sanitize_dict_for_cache, get_confidence_color)
from enhanced_valuation_ui import show_enhanced_valuation_tab
from src.ui_utils.watchlist_manager import render_watchlist_sidebar, render_add_to_watchlist_button
from src.ui_utils.market_hours import render_compact_market_status
from src.ui_utils.export_utils import render_export_buttons
from src.ui_utils.sentiment_correlation_display import show_sentiment_correlation_tab
from src.ui_utils.indicator_panel import (get_indicator_panel, render_summary_bar, 
                                       render_indicator_charts)
from indicators.master_engine import get_master_engine
from src.ui_utils.delta_divergence_chart import render_delta_divergence_chart
from src.ui_utils.global_ai_panel import render_floating_ai_button, check_and_run_global_ai

# Service Layer Integration
from src.services import StocksAnalysisService

def show_stocks_dashboard(components, ticker="META"):
    """Display the stocks analysis dashboard"""
    
    # Initialize session state keys if not present
    if 'data' not in st.session_state:
        st.session_state.data = {}
    if 'current_ticker' not in st.session_state:
        st.session_state.current_ticker = ticker
    if 'data_timestamp' not in st.session_state:
        st.session_state.data_timestamp = None
    if 'trigger_global_ai_analysis' not in st.session_state:
        st.session_state.trigger_global_ai_analysis = False
    if 'selected_ai_models' not in st.session_state:
        st.session_state.selected_ai_models = []
    if 'show_global_ai_panel' not in st.session_state:
        st.session_state.show_global_ai_panel = False
    if 'global_ai_results' not in st.session_state:
        st.session_state.global_ai_results = {}
    
    tagline = get_dashboard_tagline("stocks")
    
    # Professional header with WSB humor and market hours
    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 5px; font-weight: 700; letter-spacing: -0.5px;">
            📈 STONKS ANALYSIS
        </h1>
        <p style="font-size: 0.95rem; opacity: 0.95; font-style: italic; margin-top: 0;">
            {tagline}
        </p>
    </div>
    """.replace("{tagline}", tagline), unsafe_allow_html=True)
    
    # Market hours indicator
    st.markdown(f'<div style="text-align: center;">{render_compact_market_status()}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Ticker input section with watchlist integration
    col1, col2, col3, col4, col5 = st.columns([2.5, 0.5, 1, 1, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Ticker Symbol",
            value=ticker,
            placeholder="e.g., AAPL, TSLA, GME",
            help="Enter a stock ticker (e.g., AAPL, TSLA, GME, AMC)"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if ticker_input:
            render_add_to_watchlist_button(ticker_input)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Analyze", type="primary", key="analyze_stock"):
            ticker = ticker_input
            st.session_state.active_ticker = ticker
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        use_service = st.checkbox("🎯 Service Layer", value=False, help="Use new Service Layer (cleaner, testable)", key="use_service")
    
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_stock"):
            st.rerun()
    
    with col5:
        st.markdown("<br>", unsafe_allow_html=True)
        diamond_hands = st.checkbox("💎🙌", value=True, help="Diamond Hands Mode")
    
    # Render watchlist sidebar
    render_watchlist_sidebar()
    
    # Global AI Analysis Button (floating)
    render_floating_ai_button()
    
    # BLS Employment Regime (NEW!)
    try:
        from src.ui_utils.bls_valuation_display import show_employment_regime_panel
        show_employment_regime_panel()
    except Exception as e:
        # Silently skip if unavailable
        logger.debug(f"BLS module not available: {e}")
    
    # Fetch data
    ticker = st.session_state.get("active_ticker", ticker_input)
    
    # Handle empty ticker gracefully
    if not ticker or not ticker.strip():
        st.info("👆 **Enter a stock ticker above to begin your analysis**")
        st.markdown("""
        **Popular tickers to try:**
        - 🚀 GME, AMC - Meme stocks
        - 💎 TSLA, NVDA - Tech growth
        - 🏦 AAPL, MSFT - Blue chips
        - 📈 SPY, QQQ - Index ETFs
        """)
        return
    
    # Progressive loading with visual feedback
    from src.ui_utils.loading_indicators import ProgressiveDataFetcher
    
    # Use service layer if checkbox enabled
    use_service_layer = st.session_state.get('use_service', False)
    
    fetcher = ProgressiveDataFetcher(components, use_service_layer=use_service_layer)
    data = fetcher.fetch_stock_data_progressive(ticker)
    
    # Store in session state for global AI analysis
    if data and "error" not in data:
        st.session_state.data = data
        st.session_state.current_ticker = ticker
        st.session_state.data_timestamp = data.get('timestamp', datetime.now().isoformat())
    
    if not data or "error" in data:
        st.error(f"❌ **Unable to load data for {ticker}**")
        st.markdown("""
        **This could mean:**
        - Invalid or misspelled ticker symbol
        - Stock may be delisted or suspended
        - Temporary data service issue
        
        **What to try:**
        - Double-check the ticker spelling
        - Try another ticker: AAPL, TSLA, GME, NVDA
        - Click 🔄 Refresh to try again
        """)
        return
    
    # Data freshness indicator with load time
    col_fresh, col_refresh = st.columns([4, 1])
    with col_fresh:
        timestamp = data.get('timestamp', 'Unknown')
        fetch_time = data.get('fetch_time', 'N/A')
        mode = data.get('mode', 'Unknown')
        st.caption(f"📊 **Data fetched:** {timestamp} | **Load time:** {fetch_time} | **Mode:** {mode}")
    with col_refresh:
        if st.button("🔄 Clear Cache", key="clear_cache_btn"):
            st.cache_data.clear()
            st.success("Cache cleared! Click Analyze to refresh.")
    
    # Main metrics and buy signal
    show_buy_signal_section(data, components, diamond_hands)
    
    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Overview",
        "💰 Valuation (DD)",
        "🎛️ Interactive DCF",
        "📈 Technical (Charts)",
        "🎯 Pro Indicators (60+)",
        "💬 Ape Sentiment",
        "🔗 Sentiment Correlation",
        "🏢 Smart Money",
        "🤖 AI Analysis"
    ])
    
    with tab1:
        show_overview_tab(data)
    
    with tab2:
        show_valuation_tab(data, components)
    
    with tab3:
        # Enhanced valuation with interactive DCF and Monte Carlo
        show_enhanced_valuation_tab(data, components)
    
    with tab4:
        show_technical_tab(data, components)
    
    with tab5:
        # NEW: Professional indicators with AI/ML
        show_pro_indicators_tab(data, components)
    
    with tab6:
        show_sentiment_tab(data, components)
    
    with tab7:
        # NEW: Sentiment-market correlation analysis
        show_sentiment_correlation_tab(data["ticker"])
    
    with tab8:
        show_institutional_tab(data)
    
    with tab9:
        # NEW: Global AI Analysis with multi-model consensus
        st.markdown("### 🤖 Global AI Analysis")
        st.markdown("Click the **'🚀 Analyze Everything'** button in the sidebar to run a comprehensive multi-model AI analysis.")
        st.markdown("---")
        
        # Check and run global AI analysis if triggered
        check_and_run_global_ai()
        
        # Instructions if not run yet
        if not st.session_state.get('show_global_ai_panel', False):
            st.info("""
            **Multi-Model AI Consensus Analysis**
            
            This feature queries 4 leading AI models simultaneously:
            - 🧠 **Claude 3.5 Sonnet** (Anthropic) - 40% weight
            - 💬 **GPT-4 Turbo** (OpenAI) - 30% weight  
            - 🔮 **Gemini Pro** (Google) - 20% weight
            - ⚡ **Grok Beta** (xAI) - 10% weight
            
            **What gets analyzed:**
            - All valuation models (DCF, Zero-FCF, multiples)
            - 60+ technical indicators and chart patterns
            - Sentiment data (Reddit, social media)
            - Options flow and delta divergence
            - Economic context (BLS data, macro trends)
            - Insider trading activity
            
            **Output includes:**
            - Weighted consensus recommendation (BUY/HOLD/SELL)
            - Confidence score (0-100%)
            - Bull/Bear case analysis
            - Risk factors and suggested adjustments
            - Individual model responses
            
            **Cost:** ~$0.05-0.15 per analysis (cached for 1 hour)
            
            👉 **Click the sidebar button to start!**
            
            💡 **Tip:** Check the '🔑 AI Model Status & Configuration' expander in the sidebar 
            to see which models are available and configure API keys if needed.
            """)


def fetch_stock_data_via_service(_components, ticker):
    """
    NEW: Fetch stock data using StocksAnalysisService
    Clean service-based approach with type-safe results
    """
    import time
    
    try:
        st.info(f"⏱️ Analyzing {ticker} with Service Layer...")
        start_time = time.time()
        
        # Initialize service
        service = StocksAnalysisService(_components)
        
        # Get complete analysis
        analysis_result = service.analyze_stock(ticker)
        
        # Also fetch sentiment data (not in service yet)
        sentiment_data = {
            "stocktwits": _components["sentiment"].get_stocktwits_sentiment(ticker),
            "news": _components["sentiment"].get_news_sentiment(ticker)
        }
        
        elapsed = time.time() - start_time
        
        # Convert service result to dashboard-compatible format
        data = {
            "ticker": analysis_result.ticker,
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            "fetch_time": f"{elapsed:.2f}s",
            "service_result": analysis_result,  # Store complete service result
            "sentiment": sentiment_data,
            # Legacy format for backward compatibility
            "stock_data": {
                "info": {
                    "regularMarketPrice": analysis_result.price.current,
                    "regularMarketOpen": analysis_result.price.open,
                    "regularMarketDayHigh": analysis_result.price.high,
                    "regularMarketDayLow": analysis_result.price.low,
                    "regularMarketVolume": analysis_result.price.volume,
                    "marketCap": analysis_result.price.market_cap,
                    "fiftyTwoWeekHigh": analysis_result.price.week_52_high,
                    "fiftyTwoWeekLow": analysis_result.price.week_52_low,
                    "trailingPE": analysis_result.fundamentals.pe_ratio if analysis_result.fundamentals else None,
                }
            },
            "quote": {
                "price": analysis_result.price.current,
                "change": analysis_result.price.day_change,
                "changePercent": analysis_result.price.day_change_percent
            }
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Service-based fetch failed: {e}")
        return {"error": str(e)}


def fetch_stock_data(_components, ticker):
    """Fetch all stock data with caching and mode-aware parallel fetching"""
    from src.config.performance_config import (
        get_adjusted_ttl, 
        show_eta_indicator,
        should_fetch_institutional,
        should_fetch_sentiment,
        calculate_eta,
        get_current_mode
    )
    import concurrent.futures
    import time
    
    components = _components
    
    # Always show ETA for full analysis
    eta_components = ["stock_data", "quote", "fundamentals", "institutional", "sentiment_scraping"]
    eta_info = calculate_eta(eta_components)
    st.info(f"⏱️ Estimated load time: **{eta_info['eta_formatted']}** (Full Analysis)")
    
    try:
        start_time = time.time()
        
        # Use dynamic TTL based on performance mode
        ttl = get_adjusted_ttl(300)  # Base 5 minutes
        
        # Parallel fetching for independent data sources
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all fetch operations in parallel
            future_stock = executor.submit(components["fetcher"].get_stock_data, ticker)
            future_quote = executor.submit(components["fetcher"].get_realtime_quote, ticker)
            future_fundamentals = executor.submit(components["fetcher"].get_fundamentals, ticker)
            future_institutional = executor.submit(components["fetcher"].get_institutional_data, ticker)
            
            # Sentiment fetching - always enabled
            future_stocktwits = executor.submit(components["sentiment"].get_stocktwits_sentiment, ticker)
            future_news = executor.submit(components["sentiment"].get_news_sentiment, ticker)
            
            # Collect results
            data = {
                "ticker": ticker,
                "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
                "stock_data": future_stock.result(),
                "quote": future_quote.result(),
                "fundamentals": future_fundamentals.result(),
                "institutional": future_institutional.result(),
                "sentiment": {
                    "stocktwits": future_stocktwits.result(),
                    "news": future_news.result()
                }
            }
        
        elapsed = time.time() - start_time
        data["fetch_time"] = f"{elapsed:.2f}s"
        
        # Process DataFrame
        if data["stock_data"] and "history" in data["stock_data"]:
            df = pd.DataFrame(data["stock_data"]["history"])
            if not df.empty:
                df.index = pd.to_datetime(df.index) if not isinstance(df.index, pd.DatetimeIndex) else df.index
                data["df"] = df
        
        # Sanitize all data for caching (fixes Timestamp errors)
        data = sanitize_dict_for_cache(data)
        
        return data
    except Exception as e:
        return {"error": str(e)}


def show_buy_signal_section(data, components, diamond_hands=True):
    """Display the good buy analysis section"""
    
    df = data.get("df", pd.DataFrame())
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    
    # Run analysis
    valuation = components["valuation"].calculate_dcf(data["fundamentals"], info)
    if "error" in valuation:
        valuation = components["valuation"].calculate_multiples_valuation(info)
    
    technical = components["technical"].analyze(df) if not df.empty else {}
    sentiment = data["sentiment"]["stocktwits"]
    
    buy_analysis = components["goodbuy"].analyze_buy_opportunity(
        data["ticker"], valuation, technical, sentiment, info, df
    )
    
    # Display buy signal
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    current_price = buy_analysis["current_price"]
    buy_low = buy_analysis["buy_range"]["low"]
    buy_high = buy_analysis["buy_range"]["high"]
    target = buy_analysis["target_price"]
    confidence = buy_analysis["total_score"]
    
    with col1:
        prev_close = info.get('previousClose', current_price)
        price_change = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
        price_emoji = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "⚪"
        st.metric(
            f"{price_emoji} Bag Holding At",
            format_currency(current_price),
            format_percentage(price_change) + (" (green is good)" if price_change > 0 else " (ouch)" if price_change < 0 else "")
        )
    
    with col2:
        color = get_color('success') if confidence >= 70 else get_color('warning') if confidence >= 50 else get_color('danger')
        emoji = "🚀🌕" if confidence >= 70 else "📈💰" if confidence >= 50 else "🤔🎰"
        zone_label = "APE ENTRY ZONE" if confidence >= 70 else "MAYBE BUY?" if confidence >= 50 else "WAIT FOR DIP"
        
        st.markdown(f"""
        <div style="background: {color}20; border: 2px solid {color}; padding: 10px; border-radius: 10px; text-align: center;">
            <h3 style="color: {color}; margin: 0;">{emoji} {zone_label}</h3>
            <h2 style="color: #FFFFFF; margin: 5px 0;">{format_currency(buy_low)} - {format_currency(buy_high)}</h2>
            <p style="color: #E0E0E0; font-size: 0.8em; margin: 0;">(Not financial advice, obviously)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        upside = ((target - current_price) / current_price * 100) if current_price > 0 else 0
        target_label = "🌕 Moon Price" if upside > 50 else "🎯 Realistic Target" if upside > 20 else "💼 Conservative"
        st.metric(
            target_label,
            format_currency(target),
            f"+{upside:.1f}%" + (" 🚀🚀🚀" if upside > 50 else " 🚀" if upside > 20 else "")
        )
    
    with col4:
        confidence_emoji = "🔥💎" if confidence >= 70 else "👍📊" if confidence >= 50 else "🤷‍♂️🎲"
        confidence_label = "Autism Level"
        st.metric(
            f"{confidence_emoji} {confidence_label}",
            f"{confidence:.0f}/100",
            buy_analysis["confidence"] + " trust"
        )
    
    # Buy signals
    if buy_analysis["signals"]:
        signals_text = " | ".join(buy_analysis["signals"][:3])
        st.success(f"**🦍 Ape Signals:** {signals_text}")
    
    # Recommendation
    rec = buy_analysis["recommendation"]
    rec_color = get_color('success') if rec == "STRONG BUY" else get_color('warning') if rec == "BUY" else get_color('danger')
    rec_emoji = "💎🙌" if rec == "STRONG BUY" else "👍" if rec == "BUY" else "🧻👎"
    
    # Get WSB-style message based on confidence
    wsb_message = get_confidence_message(confidence)
    
    st.markdown(f"""
    <div style="background: {rec_color}20; border: 2px solid {rec_color}; padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0;">
        <h1 style="color: {rec_color}; margin: 0;">{rec_emoji} {rec}</h1>
        <p style="color: #FFFFFF; font-size: 1.1em; margin: 10px 0;"><i>"{wsb_message}"</i></p>
        <p style="color: #FFFFFF;">Risk/Reward: {buy_analysis['risk_reward_ratio']:.2f} | Stop Loss: {format_currency(buy_analysis['stop_loss'])}</p>
        <p style="color: #E0E0E0; font-size: 0.8em;">{"HODL with diamond hands! 💎🙌" if rec == "STRONG BUY" else "Solid play, ape! 🦍" if rec == "BUY" else "Maybe wait behind the Wendy's dumpster... 🗑️"}</p>
    </div>
    """, unsafe_allow_html=True)


def show_overview_tab(data):
    """Show overview with price chart and key metrics"""
    
    col1, col2 = st.columns([2, 1])
    
    df = data.get("df", pd.DataFrame())
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    
    with col1:
        st.subheader("📈 Price Chart")
        
        if not df.empty:
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
                    go.Scatter(x=df.index, y=sma20, name="SMA20", line=dict(color=get_color('info'), width=1)),
                    row=1, col=1
                )
            
            if len(df) >= 50:
                sma50 = df['Close'].rolling(50).mean()
                fig.add_trace(
                    go.Scatter(x=df.index, y=sma50, name="SMA50", line=dict(color=get_color('warning'), width=1)),
                    row=1, col=1
                )
            
            # Volume
            if 'Open' in df.columns:
                colors = ['red' if row['Close'] < row['Open'] else 'green' for idx, row in df.iterrows()]
            else:
                colors = ['blue'] * len(df)
            
            fig.add_trace(
                go.Bar(x=df.index, y=df.get('Volume', 0), name="Volume", marker_color=colors),
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
        else:
            st.warning("No price data available")
    
    with col2:
        st.subheader("📊 Key Metrics")
        
        if info:
            # Market cap with emoji scale
            market_cap = info.get('marketCap', 0)
            if market_cap > 200e9:
                cap_emoji = "🐋"  # Whale
            elif market_cap > 10e9:
                cap_emoji = "🦍"  # Gorilla
            else:
                cap_emoji = "🐒"  # Monkey
            
            st.markdown(f"**{cap_emoji} Market Cap:** {format_large_number(market_cap)}" if market_cap > 0 else "**Market Cap:** N/A")
            st.markdown(f"**P/E Ratio:** {info.get('trailingPE', 0):.2f}" if info.get('trailingPE', 0) > 0 else "**P/E Ratio:** N/A")
            st.markdown(f"**EPS:** {format_currency(info.get('trailingEps', 0))}" if info.get('trailingEps', 0) > 0 else "**EPS:** N/A")
            
            # Dividend with fun text
            div_yield = info.get('dividendYield', 0)
            if div_yield > 0:
                st.markdown(f"**💰 Dividend:** {format_percentage(div_yield*100)} (Free tendies!)")
            else:
                st.markdown("**Dividend:** None (Growth mode 🚀)")
            
            st.markdown(f"**Beta:** {info.get('beta', 1):.2f} {'🎢' if info.get('beta', 1) > 1.5 else '📊'}")
            st.markdown(f"**52W High:** {format_currency(info.get('fiftyTwoWeekHigh', 0))}")
            st.markdown(f"**52W Low:** {format_currency(info.get('fiftyTwoWeekLow', 0))}")
            
            # Volume analysis
            avg_vol = info.get('averageVolume', 0)
            if avg_vol > 0:
                st.markdown(f"**Avg Volume:** {format_large_number(avg_vol)}")
    
    # Export section
    st.markdown("---")
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


def show_valuation_tab(data, components):
    """Show valuation analysis (Due Diligence)"""
    st.subheader("💰 Valuation DD (Due Diligence)")
    
    try:
        info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
        
        if not info:
            st.warning("⚠️ No stock info available for valuation analysis")
            return
        
        # Calculate valuation
        valuation = components["valuation"].calculate_dcf(data.get("fundamentals", {}), info)
        if "error" in valuation:
            valuation = components["valuation"].calculate_multiples_valuation(info)
    except Exception as e:
        st.error(f"❌ Error loading valuation data: {str(e)}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "error" not in valuation:
            st.markdown("### 🧮 Fair Value Calc")
            
            fair_value = valuation.get('fair_value', 0)
            current_price = valuation.get('current_price', 0)
            upside = valuation.get('upside', 0)
            
            # Check for invalid valuation (zero or negative)
            if fair_value <= 0 or current_price <= 0:
                st.error("❌ **Cannot Calculate Fair Value**")
                st.markdown("""
                **Possible reasons:**
                - Insufficient financial data (company too new)
                - Negative or missing cash flows
                - Missing balance sheet information
                
                **What to try:**
                - Use the **🎛️ Interactive DCF** tab to manually input values
                - Check the **📐 Multiples** section for alternative valuation methods
                - Try a more established company ticker
                """)
            else:
                st.markdown(f"**Fair Value:** {format_currency(fair_value)}")
                st.markdown(f"**Current Price:** {format_currency(current_price)}")
                
                if upside > 20:
                    st.success(f"**Upside:** {format_percentage(upside)} 🚀 (UNDERVALUED!)")
                elif upside > 0:
                    st.info(f"**Upside:** {format_percentage(upside)} 📈")
                else:
                    st.warning(f"**Downside:** {format_percentage(upside)} 📉")
                
                st.markdown(f"**Method:** {valuation.get('method', 'Unknown')}")
            
            # Scenarios
            if "scenarios" in valuation:
                st.markdown("### 📊 Price Scenarios")
                try:
                    scenarios_df = pd.DataFrame({
                        'Scenario': ['🐻 Bear', '📊 Base', '🚀 Bull'],
                        'Price': [
                            valuation['scenarios']['bear'],
                            valuation['scenarios']['base'],
                            valuation['scenarios']['bull']
                        ]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=scenarios_df['Scenario'],
                            y=scenarios_df['Price'],
                            marker_color=[get_color('danger'), get_color('warning'), get_color('success')]
                        )
                    ])
                    
                    if current_price and current_price > 0:
                        fig.add_hline(y=current_price, line_dash="dash", line_color="white",
                                    annotation_text="Current Price")
                    
                    fig.update_layout(
                        yaxis_title="Price ($)",
                        template="plotly_dark",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating scenarios chart: {str(e)}")
        else:
            st.warning(f"⚠️ Valuation unavailable: {valuation.get('error', 'Unknown error')}")
        
        # BLS-Enhanced Valuation (NEW!)
        if "error" not in valuation and fair_value > 0:
            try:
                from src.ui_utils.bls_valuation_display import show_bls_enhanced_valuation
                sector = info.get('sector', 'Unknown')
                show_bls_enhanced_valuation(
                    ticker=data.get("ticker", ""),
                    sector=sector,
                    base_dcf_value=fair_value,
                    current_price=current_price
                )
            except Exception as e:
                # BLS module unavailable - show warning
                st.info("💡 BLS employment analysis available with additional setup")
                logger.debug(f"BLS module not available: {e}")
    
    with col2:
        st.markdown("### 📐 Multiples")
        
        multiples = {
            "P/E": info.get('trailingPE', 0),
            "Forward P/E": info.get('forwardPE', 0),
            "P/B": info.get('priceToBook', 0),
            "P/S": info.get('priceToSalesTrailing12Months', 0),
            "PEG": info.get('pegRatio', 0),
        }
        
        multiples = {k: v for k, v in multiples.items() if v > 0}
        
        if multiples:
            for metric, value in multiples.items():
                if metric == "PEG" and value < 1:
                    st.success(f"**{metric}:** {value:.2f} (CHEAP! 🤑)")
                elif metric == "P/E" and value < 15:
                    st.success(f"**{metric}:** {value:.2f} (Value play! 💰)")
                else:
                    st.markdown(f"**{metric}:** {value:.2f}")
        else:
            st.info("No multiples data available")
    
    # Zero-FCF Valuation Section (for high-growth companies)
    st.markdown("---")
    st.markdown("### 🎯 Zero-FCF Valuation (High-Growth Alternative)")
    st.markdown("*For companies with negative or minimal free cash flow*")
    
    try:
        from zero_fcf_valuation import ZeroFCFValuationEngine
        from src.ui_utils.zero_fcf_display import show_zero_fcf_valuation_tab
        
        stock_data = data.get("stock_data", {})
        info_for_zero = stock_data.get("info", {}) if stock_data else {}
        financials = data.get("financials", {})
        ticker = data.get("ticker", "")
        
        if info_for_zero:
            engine = ZeroFCFValuationEngine()
            
            with st.spinner("Calculating Zero-FCF valuation..."):
                valuation_result = engine.calculate_comprehensive_valuation(info_for_zero, financials)
            
            # Display results
            show_zero_fcf_valuation_tab(valuation_result, ticker)
        else:
            st.warning("⚠️ Insufficient data for Zero-FCF valuation")
    except Exception as e:
        st.error(f"❌ Error calculating Zero-FCF valuation: {str(e)}")
        st.info("💡 This alternative valuation method is best for high-growth companies with negative free cash flow.")


def show_technical_tab(data, components):
    """Show technical analysis with progressive loading"""
    from src.ui_utils.loading_indicators import show_skeleton_chart, show_skeleton_metric
    
    st.subheader("📈 Technical Analysis (TA)")
    
    df = data.get("df", pd.DataFrame())
    
    if df.empty:
        st.warning("Insufficient data for TA")
        return
    
    # Show skeleton loaders while analyzing
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    
    with metrics_placeholder.container():
        st.caption("⏳ Analyzing technical indicators...")
        show_skeleton_metric(count=3)
    
    with chart_placeholder.container():
        show_skeleton_chart(height=400)
    
    # Perform analysis
    technical = components["technical"].analyze(df)
    
    # Clear placeholders
    metrics_placeholder.empty()
    chart_placeholder.empty()
    
    if "error" in technical:
        st.error(f"TA Error: {technical['error']}")
        return
    
    # Row 1: RSI, MACD, Bollinger Bands
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # RSI
        rsi_val = technical.get("rsi", {}).get("value", 50)
        rsi_signal = technical.get("rsi", {}).get("signal", "neutral")
        
        st.markdown("### 🔥 RSI")
        
        if rsi_signal == "oversold":
            st.success(f"**{rsi_val:.1f}** - OVERSOLD! Time to buy the dip! 🦍")
        elif rsi_signal == "overbought":
            st.warning(f"**{rsi_val:.1f}** - OVERBOUGHT! Moon soon? 🚀")
        else:
            st.info(f"**{rsi_val:.1f}** - Neutral 📊")
    
    with col2:
        # MACD
        st.markdown("### 📊 MACD")
        macd_bull = technical.get("macd", {}).get("bullish", False)
        
        if macd_bull:
            st.success("**BULLISH** Crossover! 🚀")
        else:
            st.warning("**BEARISH** Watch out! 📉")
    
    with col3:
        # Bollinger Bands
        st.markdown("### 📊 Bollinger Bands")
        bb_data = technical.get("bollinger", {})
        bb_upper = bb_data.get("upper", 0)
        bb_middle = bb_data.get("middle", 0)
        bb_lower = bb_data.get("lower", 0)
        bb_signal = bb_data.get("signal", "neutral")
        current_price = bb_data.get("price", 0)
        
        st.markdown(f"**Upper:** {format_currency(bb_upper)}")
        st.markdown(f"**Middle:** {format_currency(bb_middle)}")
        st.markdown(f"**Lower:** {format_currency(bb_lower)}")
        
        if bb_signal == "oversold":
            st.success("📍 Below lower band! Buy signal! 🚀")
        elif bb_signal == "overbought":
            st.warning("⚠️ Above upper band! Overbought!")
        else:
            st.info("📊 Within bands - Normal range")
    
    # Row 2: Moving Averages and Support/Resistance
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # SMA 50
        st.markdown("### 📈 SMA 50")
        price_action = technical.get("price_action", {})
        sma_50 = price_action.get("sma_50", 0)
        above_sma_50 = price_action.get("above_sma_50", False)
        current_price = price_action.get("price", 0)
        
        st.markdown(f"**SMA 50:** {format_currency(sma_50)}")
        st.markdown(f"**Current:** {format_currency(current_price)}")
        
        if above_sma_50:
            st.success("✅ Above SMA 50 - Bullish!")
        else:
            st.warning("⚠️ Below SMA 50 - Bearish")
    
    with col2:
        # SMA 200
        st.markdown("### 📈 SMA 200")
        sma_200 = price_action.get("sma_200", 0)
        above_sma_200 = price_action.get("above_sma_200", False)
        
        st.markdown(f"**SMA 200:** {format_currency(sma_200)}")
        st.markdown(f"**Current:** {format_currency(current_price)}")
        
        if above_sma_200:
            st.success("✅ Above SMA 200 - Strong trend!")
        else:
            st.warning("⚠️ Below SMA 200 - Weak trend")
    
    with col3:
        # Support/Resistance
        st.markdown("### 🎯 Support/Resistance")
        support = technical.get("support_resistance", {}).get("support", 0)
        resistance = technical.get("support_resistance", {}).get("resistance", 0)
        
        st.markdown(f"**Resistance:** {format_currency(resistance)}")
        st.markdown(f"**Support:** {format_currency(support)}")
        
        if technical.get("support_resistance", {}).get("near_support", False):
            st.success("📍 Near support! Buy opportunity!")
        elif technical.get("support_resistance", {}).get("near_resistance", False):
            st.warning("🚧 Near resistance! Take profits?")
    
    # Patterns
    st.markdown("---")
    st.markdown("### 🔍 Chart Patterns")
    
    patterns = components["technical"].detect_patterns(df)
    if patterns:
        for pattern in patterns:
            signal_color = get_color('bullish') if pattern['signal'] == "bullish" else get_color('bearish')
            signal_emoji = "🚀" if pattern['signal'] == "bullish" else "📉"
            st.markdown(
                f"<span style='color: {signal_color}'>{signal_emoji} {pattern['pattern'].replace('_', ' ').title()} - {pattern['signal'].upper()}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No major patterns detected. Sideways trading 📊")


def show_pro_indicators_tab(data, components):
    """Show professional technical indicators with AI/ML (60+ indicators)"""
    st.markdown("## 🎯 Professional Technical Indicators")
    st.markdown("""
    **TradingView Pro Equivalent** - 60+ indicators across 7 tiers:
    - 📈 **Tier 1 (Core)**: Essential indicators (SMA, EMA, RSI, MACD, Bollinger)
    - 📊 **Tier 2 (Pro)**: Professional tools (Ichimoku, Fibonacci, Stochastic, ADX)
    - 📦 **Tier 3 (Volume)**: Volume analysis (Volume Profile, A/D Line, PVT)
    - ⚡ **Tier 4 (Momentum)**: Momentum oscillators (ROC, TRIX, Connors RSI)
    - 🌐 **Tier 5 (Market Breadth)**: Market-wide indicators (Put/Call, VIX, TRIN)
    - 📐 **Tier 6 (Quant)**: Quantitative analysis (Beta, Alpha, Sharpe, Sortino)
    - 🤖 **Tier 7 (AI/ML)**: AI-powered predictions (ML Trend, Regime Detection)
    """)
    
    # Get historical data for indicators
    try:
        df = data.get('historical_data')
        if df is None or df.empty:
            st.warning("⚠️ No historical data available. Fetching...")
            # Fetch data
            ticker = data.get('ticker', 'META')
            import yfinance as yf
            stock = yf.Ticker(ticker)
            df = stock.history(period='1y')
        
        if df.empty:
            st.error("❌ Unable to fetch historical data for indicator calculation")
            return
        
        st.success(f"✅ Loaded {len(df)} trading days of data")
        
        # Initialize indicator components
        panel = get_indicator_panel()
        engine = get_master_engine()
        
        # Render control panel (no outer expander - panel.render() uses expanders internally)
        st.markdown("### 🎛️ Indicator Control Panel")
        selected_indicators = panel.render()
        
        # Quick tier selector
        st.markdown("### 🚀 Quick Select")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calculate_core = st.checkbox("📈 Core Indicators", value=True)
        with col2:
            calculate_pro = st.checkbox("📊 Pro + Volume", value=False)
        with col3:
            calculate_ai = st.checkbox("🤖 AI/ML Indicators", value=False)
        
        # Determine which tiers to calculate
        tiers_to_calculate = []
        if calculate_core:
            tiers_to_calculate.extend([1])
        if calculate_pro:
            tiers_to_calculate.extend([2, 3, 4])
        if calculate_ai:
            tiers_to_calculate.extend([5, 6, 7])
        
        if not tiers_to_calculate:
            st.info("💡 Select at least one tier to calculate indicators")
            return
        
        # Calculate indicators
        with st.spinner(f"🧮 Calculating {len(tiers_to_calculate)} tiers of indicators..."):
            df_with_indicators = engine.calculate_all(df, tiers=tiers_to_calculate)
            summary = engine.get_summary(df_with_indicators)
        
        st.success(f"✅ Calculated {len(tiers_to_calculate)} tiers successfully!")
        
        # Show summary bar
        st.markdown("---")
        render_summary_bar(summary)
        
        st.markdown("---")
        
        # Show indicator charts
        render_indicator_charts(df_with_indicators, selected_indicators)
        
        # Raw indicator data viewer
        with st.expander("📊 View Raw Indicator Data", expanded=False):
            st.markdown("### Latest Indicator Values")
            
            # Show latest values in a nice format
            latest = df_with_indicators.iloc[-1]
            
            # Group by category
            core_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['SMA', 'EMA', 'RSI', 'MACD', 'BB'])]
            volume_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['Volume', 'OBV', 'AD', 'PVT'])]
            momentum_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['ROC', 'TRIX', 'Stoch', 'Williams', 'Momentum'])]
            ai_cols = [col for col in df_with_indicators.columns if any(x in col for x in ['ML', 'Regime', 'Anomaly', 'Score'])]
            
            if core_cols:
                st.markdown("#### 📈 Core Indicators")
                core_data = {col: latest[col] for col in core_cols if col in latest.index}
                st.json(core_data)
            
            if volume_cols:
                st.markdown("#### 📦 Volume Indicators")
                volume_data = {col: latest[col] for col in volume_cols if col in latest.index}
                st.json(volume_data)
            
            if momentum_cols:
                st.markdown("#### ⚡ Momentum Indicators")
                momentum_data = {col: latest[col] for col in momentum_cols if col in latest.index}
                st.json(momentum_data)
            
            if ai_cols:
                st.markdown("#### 🤖 AI/ML Indicators")
                ai_data = {col: latest[col] for col in ai_cols if col in latest.index}
                st.json(ai_data)
            
            # Full dataframe
            st.markdown("#### 📊 Full DataFrame (Last 20 Rows)")
            st.dataframe(df_with_indicators.tail(20), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error calculating indicators: {str(e)}")
        st.exception(e)


def show_delta_divergence_tab(data):
    """Show Delta Divergence Options Chart"""
    ticker = data.get('ticker', 'META')
    render_delta_divergence_chart(ticker)


def show_sentiment_tab(data, components):
    """Show sentiment analysis using real scraper data"""
    from src.ui_utils.sentiment_scraper import get_scraper, display_sentiment_metrics, display_recent_posts
    from src.config.settings import Config
    
    st.subheader("💬 Ape Sentiment Tracker")
    
    # Get configuration for API keys
    config_obj = Config()
    api_config = {
        'reddit_client_id': config_obj.get('api.reddit.client_id', ''),
        'reddit_client_secret': config_obj.get('api.reddit.client_secret', ''),
        'reddit_user_agent': config_obj.get('api.reddit.user_agent', 'StocksV2App/1.0'),
        'news_api_key': config_obj.get('api.news.api_key', '')
    }
    
    # Initialize scraper
    scraper = get_scraper(api_config)
    
    # Add refresh button
    col_refresh, col_info = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refresh Data", key="refresh_sentiment"):
            scraper.get_sentiment_data.clear()
            st.rerun()
    
    with col_info:
        st.caption("Real-time sentiment from Reddit (wallstreetbets, stocks, investing) and news sources")
    
    # Get sentiment data
    ticker = data["ticker"]
    with st.spinner(f"Scraping sentiment data for ${ticker}..."):
        summary = scraper.get_sentiment_summary(ticker)
    
    if summary['data_available']:
        # Display metrics
        display_sentiment_metrics(summary)
        
        st.divider()
        
        # Create two columns for visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Sentiment Breakdown")
            
            # Sentiment pie chart
            sentiment_data = {
                "🟢 Positive": summary['positive_pct'],
                "🔴 Negative": summary['negative_pct'],
                "⚪ Neutral": summary['neutral_pct']
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(sentiment_data.keys()),
                values=list(sentiment_data.values()),
                hole=.3,
                marker_colors=[get_color('success'), get_color('danger'), get_color('warning')]
            )])
            
            fig.update_layout(
                title=f"Sentiment Distribution ({summary['total_mentions']} mentions)",
                template="plotly_dark",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sentiment score interpretation
            avg_polarity = summary['avg_polarity']
            if avg_polarity > 0.3:
                st.success(f"**Polarity: {avg_polarity:.2f}** - Apes are BULLISH! 🦍🚀")
            elif avg_polarity > 0:
                st.info(f"**Polarity: {avg_polarity:.2f}** - Slightly bullish 📈")
            elif avg_polarity > -0.3:
                st.warning(f"**Polarity: {avg_polarity:.2f}** - Slightly bearish 📉")
            else:
                st.error(f"**Polarity: {avg_polarity:.2f}** - Bears winning 🐻")
        
        with col2:
            st.markdown("### 📈 Trending Sources")
            
            # Source distribution bar chart
            sources = summary['trending_sources']
            if sources:
                fig_sources = go.Figure(data=[go.Bar(
                    x=list(sources.values()),
                    y=list(sources.keys()),
                    orientation='h',
                    marker_color=get_color('info')
                )])
                
                fig_sources.update_layout(
                    title="Mentions by Source",
                    template="plotly_dark",
                    height=350,
                    xaxis_title="Number of Mentions",
                    yaxis_title="Source"
                )
                
                st.plotly_chart(fig_sources, use_container_width=True)
            else:
                st.info("No source data available")
            
            # Subjectivity meter
            subjectivity = summary['avg_subjectivity']
            st.metric(
                "Avg Subjectivity",
                f"{subjectivity:.2f}",
                help="0 = Objective, 1 = Highly Subjective/Opinionated"
            )
        
        st.divider()
        
        # Display recent posts
        st.markdown("### 🔥 Recent Social Activity")
        display_recent_posts(summary['recent_posts'], max_posts=10)
        
        # Sentiment over time (if we have enough data)
        sentiment_over_time = scraper.get_sentiment_over_time(ticker, days=7)
        if not sentiment_over_time.empty:
            st.markdown("### 📅 Sentiment Trend (Last 7 Days)")
            
            fig_trend = go.Figure()
            
            if 'positive' in sentiment_over_time.columns:
                fig_trend.add_trace(go.Scatter(
                    x=sentiment_over_time['date_only'],
                    y=sentiment_over_time['positive'],
                    mode='lines+markers',
                    name='Positive',
                    line=dict(color=get_color('success'), width=2)
                ))
            
            if 'negative' in sentiment_over_time.columns:
                fig_trend.add_trace(go.Scatter(
                    x=sentiment_over_time['date_only'],
                    y=sentiment_over_time['negative'],
                    mode='lines+markers',
                    name='Negative',
                    line=dict(color=get_color('danger'), width=2)
                ))
            
            if 'neutral' in sentiment_over_time.columns:
                fig_trend.add_trace(go.Scatter(
                    x=sentiment_over_time['date_only'],
                    y=sentiment_over_time['neutral'],
                    mode='lines+markers',
                    name='Neutral',
                    line=dict(color=get_color('warning'), width=2)
                ))
            
            fig_trend.update_layout(
                title="Daily Sentiment Mentions",
                template="plotly_dark",
                height=400,
                xaxis_title="Date",
                yaxis_title="Number of Mentions",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
    
    else:
        # Fallback to old sentiment display if no scraper data
        st.warning("⚠️ Real-time sentiment scraping unavailable. Configure API keys for live data.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🦍 StockTwits Vibes")
            sentiment = data["sentiment"]["stocktwits"]
            
            if "error" not in sentiment:
                sentiment_data = {
                    "🚀 Bullish": sentiment.get("bullish", 0),
                    "📉 Bearish": sentiment.get("bearish", 0),
                    "🤷 Neutral": sentiment.get("neutral", 0)
                }
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(sentiment_data.keys()),
                    values=list(sentiment_data.values()),
                    hole=.3,
                    marker_colors=["#00FF88", "#FF3860", "#FFB700"]
                )])
                
                fig.update_layout(
                    title="Community Sentiment",
                    template="plotly_dark",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                score = sentiment.get('sentiment_score', 0)
                if score > 30:
                    st.success(f"**Score: {score:,.1f}** - Apes are BULLISH! 🦍🚀")
                elif score > 0:
                    st.info(f"**Score: {score:,.1f}** - Slightly bullish 📈")
                elif score > -30:
                    st.warning(f"**Score: {score:,.1f}** - Slightly bearish 📉")
                else:
                    st.error(f"**Score: {score:,.1f}** - Bears winning 🐻")
            else:
                st.info("No sentiment data available")
        
        with col2:
            st.markdown("### 📰 Latest News")
            news = data["sentiment"]["news"]
            if news:
                for article in news[:5]:
                    with st.expander(f"📰 {article['title'][:60]}..."):
                        st.markdown(f"**Publisher:** {article['publisher']}")
                        st.markdown(f"**Time:** {article['timestamp']}")
                        st.markdown(f"[Read More]({article['link']})")
            else:
                st.info("No recent news")


def show_institutional_tab(data):
    """Show institutional holdings and Congressional trades"""
    st.subheader("🏢 Smart Money Tracker")
    
    inst_data = data.get("institutional", {})
    ticker = data.get("ticker", "")
    
    # Check if institutional data is available
    if inst_data.get("skipped") or not inst_data:
        st.info("⚠️ Institutional data temporarily unavailable")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐋 Major Holders")
        if "major_holders" in inst_data and inst_data["major_holders"]:
            holders_df = pd.DataFrame(inst_data["major_holders"])
            st.dataframe(holders_df, use_container_width=True)
        else:
            st.info("No major holders data")
    
    with col2:
        st.markdown("### 🏦 Top Institutional Holders")
        if "institutional_holders" in inst_data and inst_data["institutional_holders"]:
            inst_df = pd.DataFrame(inst_data["institutional_holders"])
            if not inst_df.empty:
                # Format the dataframe
                display_df = inst_df.head(5).copy()
                
                # Rename columns for clarity
                column_renames = {
                    'Date Reported': 'Report Date',
                    'Holder': 'Institution',
                    'Shares': 'Shares Held',
                    'Value': 'Position Value',
                    '% Out': '% Outstanding'
                }
                display_df = display_df.rename(columns={k: v for k, v in column_renames.items() if k in display_df.columns})
                
                # Format date column if exists
                if 'Report Date' in display_df.columns:
                    display_df['Report Date'] = pd.to_datetime(display_df['Report Date']).dt.strftime('%b %d, %Y')
                
                # Format numeric columns with commas
                if 'Shares Held' in display_df.columns:
                    display_df['Shares Held'] = display_df['Shares Held'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                
                if 'Position Value' in display_df.columns:
                    display_df['Position Value'] = display_df['Position Value'].apply(
                        lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
                    )
                
                if '% Outstanding' in display_df.columns:
                    display_df['% Outstanding'] = display_df['% Outstanding'].apply(
                        lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
                    )
                
                # Drop any irrelevant columns (unnamed index columns)
                display_df = display_df.loc[:, ~display_df.columns.str.contains('^Unnamed')]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No institutional data")
    
    st.markdown("### 👔 Recent Insider Transactions")
    if "insider_transactions" in inst_data and inst_data["insider_transactions"]:
        insider_df = pd.DataFrame(inst_data["insider_transactions"])
        if not insider_df.empty:
            display_insider = insider_df.head(10).copy()
            
            # Rename columns for clarity
            insider_renames = {
                'Insider': 'Name',
                'Position': 'Title',
                'Date': 'Transaction Date',
                'Transaction': 'Type',
                'Shares': 'Shares',
                'Value': 'Transaction Value',
                'Text': 'Details'
            }
            display_insider = display_insider.rename(columns={k: v for k, v in insider_renames.items() if k in display_insider.columns})
            
            # Format date
            if 'Transaction Date' in display_insider.columns:
                display_insider['Transaction Date'] = pd.to_datetime(display_insider['Transaction Date']).dt.strftime('%b %d, %Y')
            
            # Format shares with commas
            if 'Shares' in display_insider.columns:
                display_insider['Shares'] = display_insider['Shares'].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) and x != 0 else "N/A"
                )
            
            # Format transaction value
            if 'Transaction Value' in display_insider.columns:
                display_insider['Transaction Value'] = display_insider['Transaction Value'].apply(
                    lambda x: f"${x:,.0f}" if pd.notna(x) and x != 0 else "N/A"
                )
            
            # Drop irrelevant columns
            display_insider = display_insider.loc[:, ~display_insider.columns.str.contains('^Unnamed')]
            
            st.dataframe(display_insider, use_container_width=True, hide_index=True)
            
            # Check for insider buying
            if 'Shares' in insider_df.columns:
                recent_buys = insider_df[insider_df['Shares'] > 0]
                if not recent_buys.empty:
                    st.success("🚨 Insiders are buying! Bullish signal! 🚀")
    else:
        st.info("No insider transaction data")
    
    # Congressional Trading Activity (NEW!)
    if ticker:
        try:
            from src.ui_utils.congressional_display import show_congressional_trades
            show_congressional_trades(ticker, days=90)
        except ImportError:
            st.warning("⚠️ Congressional trading data not available. Install required dependencies.")
        except Exception as e:
            st.error(f"Error loading Congressional trades: {e}")
