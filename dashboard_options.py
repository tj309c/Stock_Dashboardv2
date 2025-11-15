"""
Options Dashboard - YOLO Edition ⚡
For degens who love 0DTE plays and gamma squeezes
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
# Migrated to new formatters module
from src.ui_utils.formatters import format_currency, format_percentage, format_large_number
from utils import safe_divide
from src.ui_utils.delta_divergence_chart import render_delta_divergence_chart
from src.services import OptionsAnalysisService


def show_options_dashboard(components, ticker="SPY"):
    """Display the options analysis dashboard"""
    
    # Initialize session state for active tab to prevent jumping
    if 'options_active_tab' not in st.session_state:
        st.session_state.options_active_tab = 0
    
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="margin: 0; font-size: 3em;">📊 OPTIONS FLOW</h1>
        <p style="color: #FFFFFF; font-size: 1.2em; margin: 10px 0;"><i>YOLO plays and gamma squeezes</i> 🎰</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Service Layer Toggle
    col_toggle1, col_toggle2 = st.columns([3, 1])
    with col_toggle1:
        st.markdown("")
    with col_toggle2:
        use_service = st.checkbox(
            "🎯 Service Layer",
            value=st.session_state.get('use_service_options', False),
            help="Use new OptionsAnalysisService (faster, testable)",
            key="use_service_options"
        )
    
    # Ticker input
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Ticker Symbol",
            value=ticker,
            help="Works best with liquid stocks (SPY, AAPL, TSLA, etc.)"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Analyze", type="primary", key="analyze_options"):
            ticker = ticker_input
            st.session_state.active_ticker = ticker
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", key="refresh_options"):
            st.rerun()
    
    ticker = st.session_state.get("active_ticker", ticker_input)
    
    # Get service layer preference
    use_service_layer = st.session_state.get('use_service_options', False)
    
    # Fetch data
    with st.spinner(f"Loading options chain for {ticker}... ⚡"):
        if use_service_layer:
            data = fetch_options_data_via_service(components, ticker)
        else:
            data = fetch_options_data(components, ticker)
    
    if not data or "error" in data:
        st.error(f"❌ No options data for {ticker}. Try a more liquid ticker!")
        return
    
    # Show current price and key metrics
    show_options_overview(data, components)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Unusual Activity",
        "📊 Options Chain",
        "📈 Greeks Analysis",
        "🎯 Strategy Builder"
    ])
    
    with tab1:
        show_unusual_activity_tab(data, components)
    
    with tab2:
        show_options_chain_tab(data)
    
    with tab3:
        show_greeks_tab(data)
    
    with tab4:
        show_strategy_tab(data)


@st.cache_data(ttl=300)
def fetch_options_data_via_service(_components, ticker):
    """NEW: Fetch options data using OptionsAnalysisService"""
    components = _components
    try:
        st.info("✅ Loading via Service Layer...")
        
        # Initialize service
        service = OptionsAnalysisService(components)
        
        # Analyze options chain
        options_result = service.analyze_options_chain(ticker)
        
        if not options_result:
            return {"error": "No options data available"}
        
        # Get stock data for context
        stock_data = components["fetcher"].get_stock_data(ticker, period="3mo")
        quote = components["fetcher"].get_realtime_quote(ticker)
        
        # Convert service result to dashboard format
        data = {
            "ticker": ticker,
            "stock_data": stock_data,
            "quote": quote,
            "current_price": options_result.spot_price,
            "service_result": options_result,  # Store full service result
            "options": {
                "expirations": options_result.expiration_dates,
                "calls": options_result.calls,
                "puts": options_result.puts,
            }
        }
        
        # Sanitize for caching
        from utils import sanitize_dict_for_cache
        data = sanitize_dict_for_cache(data)
        
        return data
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=300)
def fetch_options_data(_components, ticker):
    """LEGACY: Fetch options data with caching"""
    components = _components
    try:
        data = {
            "ticker": ticker,
            "stock_data": components["fetcher"].get_stock_data(ticker, period="3mo"),
            "quote": components["fetcher"].get_realtime_quote(ticker),
            "options": components["fetcher"].get_options_chain(ticker),
        }
        
        # Get current price
        info = data["stock_data"].get("info", {}) if data["stock_data"] else {}
        data["current_price"] = info.get("currentPrice", info.get("regularMarketPrice", 0))
        
        # Sanitize all data for caching (fixes Timestamp errors)
        from utils import sanitize_dict_for_cache
        data = sanitize_dict_for_cache(data)
        
        return data
    except Exception as e:
        return {"error": str(e)}


def show_options_overview(data, components):
    """Show current price and quick stats"""
    
    st.markdown("---")
    
    current_price = data["current_price"]
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prev_close = info.get('previousClose', current_price)
        price_change = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
        st.metric(
            "💰 Stock Price",
            format_currency(current_price),
            format_percentage(price_change)
        )
    
    with col2:
        # Count available expirations
        expirations = data["options"].get("expirations", [])
        st.metric(
            "📅 Expirations",
            len(expirations),
            "Available dates"
        )
    
    with col3:
        # IV if available
        iv = info.get("impliedVolatility", 0)
        if iv > 0:
            st.metric(
                "📊 IV",
                format_percentage(iv*100),
                "Implied Vol"
            )
        else:
            st.metric("📊 IV", "N/A", "Check options")
    
    with col4:
        # Volume indicator
        volume = info.get("volume", 0)
        avg_volume = info.get("averageVolume", 1)
        vol_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        st.metric(
            "📈 Volume",
            f"{vol_ratio:,.2f}x",
            "vs Average"
        )


def show_unusual_activity_tab(data, components):
    """Show unusual options activity"""
    st.subheader("🔥 Unusual Options Activity (Whales Buying)")
    
    current_price = data["current_price"]
    
    # Check if we have service layer results
    if "service_result" in data:
        service = OptionsAnalysisService(components)
        unusual_activity = service.detect_unusual_activity(data["ticker"])
        
        # Convert to legacy format
        opportunities = []
        for activity in unusual_activity:
            opp = {
                "type": activity.contract.option_type,
                "strike": activity.contract.strike,
                "expiration": activity.contract.expiration,
                "volume": activity.contract.volume,
                "open_interest": activity.contract.open_interest,
                "vol_oi_ratio": activity.contract.volume / max(activity.contract.open_interest, 1),
                "unusual_score": activity.score,
                "reason": activity.reason
            }
            opportunities.append(opp)
    else:
        # Legacy approach
        opportunities = components["options"].find_best_opportunities(
            data["options"],
            current_price
        )
    
    if opportunities:
        st.success(f"🚨 Found {len(opportunities)} unusual options flows!")
        
        # Convert to DataFrame for display
        opp_df = pd.DataFrame(opportunities)
        
        # Color code by type
        def color_type(val):
            if val == "CALL":
                return 'background-color: rgba(0, 255, 136, 0.25)'
            else:
                return 'background-color: rgba(255, 56, 96, 0.25)'
        
        if 'type' in opp_df.columns:
            styled_df = opp_df.style.map(color_type, subset=['type'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.dataframe(opp_df, use_container_width=True)
        
        st.markdown("### 🦍 What This Means:")
        st.info("""
        **High Volume/OI Ratio** = Smart money is entering new positions!
        - **Unusual Call Activity** 🚀 = Bullish whale bets
        - **Unusual Put Activity** 📉 = Bearish hedge or directional play
        - **Near-the-money** = Most likely to move stock price
        """)
    else:
        st.warning("No unusual activity detected. Market is quiet... 😴")
        st.info("💡 Try a more liquid ticker like SPY, QQQ, AAPL, or TSLA")


def show_options_chain_tab(data):
    """Show full options chain"""
    st.subheader("📊 Options Chain Explorer")
    
    options_data = data["options"]
    current_price = data["current_price"]
    
    if not options_data or "expirations" not in options_data:
        st.warning("No options chain available")
        return
    
    expirations = options_data["expirations"]
    
    # Expiration selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_exp = st.selectbox(
            "Select Expiration Date",
            expirations[:10],  # Show first 10
            help="Choose an expiration to view the options chain"
        )
    
    with col2:
        # Calculate DTE
        try:
            exp_date = datetime.strptime(selected_exp, '%Y-%m-%d')
            dte = (exp_date - datetime.now()).days
            st.metric("Days to Expiry", dte, "DTE" if dte > 1 else "⚠️ 0DTE!" if dte == 0 else "EXPIRED")
        except (ValueError, TypeError) as e:
            print(f"Date parsing error for options expiry: {e}")
            dte = 0
    
    if selected_exp and selected_exp in options_data["chains"]:
        chain = options_data["chains"][selected_exp]
        
        # Show calls and puts side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 CALLS (Bullish)")
            if "calls" in chain and chain["calls"]:
                calls_df = pd.DataFrame(chain["calls"])
                
                # Filter to show strikes around current price
                if 'strike' in calls_df.columns and len(calls_df) > 0:
                    calls_df = calls_df[
                        (calls_df['strike'] >= current_price * 0.9) &
                        (calls_df['strike'] <= current_price * 1.2)
                    ]
                
                display_cols = ['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']
                available_cols = [col for col in display_cols if col in calls_df.columns]
                
                if available_cols and not calls_df.empty:
                    # Highlight ITM options
                    def highlight_itm(row):
                        if row['strike'] < current_price:
                            return ['background-color: rgba(0, 255, 136, 0.1)'] * len(row)
                        return [''] * len(row)
                    
                    styled_calls = calls_df[available_cols].head(20).style.apply(highlight_itm, axis=1)
                    st.dataframe(styled_calls, use_container_width=True, height=400)
                else:
                    st.info("No calls data")
            else:
                st.info("No calls available")
        
        with col2:
            st.markdown("#### 📉 PUTS (Bearish)")
            if "puts" in chain and chain["puts"]:
                puts_df = pd.DataFrame(chain["puts"])
                
                # Filter to show strikes around current price
                if 'strike' in puts_df.columns and len(puts_df) > 0:
                    puts_df = puts_df[
                        (puts_df['strike'] >= current_price * 0.8) &
                        (puts_df['strike'] <= current_price * 1.1)
                    ]
                
                display_cols = ['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']
                available_cols = [col for col in display_cols if col in puts_df.columns]
                
                if available_cols and not puts_df.empty:
                    # Highlight ITM options
                    def highlight_itm(row):
                        if row['strike'] > current_price:
                            return ['background-color: rgba(255, 56, 96, 0.1)'] * len(row)
                        return [''] * len(row)
                    
                    styled_puts = puts_df[available_cols].head(20).style.apply(highlight_itm, axis=1)
                    st.dataframe(styled_puts, use_container_width=True, height=400)
                else:
                    st.info("No puts data")
            else:
                st.info("No puts available")
        
        # Legend
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.info("💡 **ITM (In The Money)** = Highlighted options have intrinsic value")
        with col2:
            st.info("📊 **Volume > OI** = New positions being opened (bullish signal)")
        
        # Advanced Options Analysis Section
        st.markdown("---")
        st.markdown("### 📊 Advanced Options Analysis")
        
        # Create tabs for different analysis types
        analysis_tabs = st.tabs([
            "📊 Delta Divergence",
            "⚡ Gamma Exposure (GEX)",
            "📈 Open Interest Profile",
            "📉 Put/Call Ratio",
            "📐 IV Skew"
        ])
        
        with analysis_tabs[0]:
            st.markdown("#### 📊 Delta Divergence Options Analysis")
            st.caption("Shows divergence between option delta flow and underlying price movement")
            render_delta_divergence_chart(data["ticker"])
        
        with analysis_tabs[1]:
            st.markdown("#### ⚡ Gamma Exposure (GEX) Profile")
            st.caption("Dealer hedging impact at different strike prices - shows where price might be attracted (positive gamma) or repelled (negative gamma)")
            render_gex_profile(chain, current_price, selected_exp)
        
        with analysis_tabs[2]:
            st.markdown("#### 📈 Open Interest (OI) Profile")
            st.caption("Total outstanding contracts at each strike - larger bars (OI Walls) act as support or resistance")
            render_oi_profile(chain, current_price)
        
        with analysis_tabs[3]:
            st.markdown("#### 📉 Put/Call Ratio (PCR) Over Time")
            st.caption("Sentiment indicator: Higher values (more puts) suggest fear, lower values (more calls) suggest greed")
            render_pcr_chart(data["ticker"])
        
        with analysis_tabs[4]:
            st.markdown("#### 📐 Implied Volatility (IV) Skew")
            st.caption("How implied volatility changes across strikes - upward slope on puts indicates demand for downside protection")
            render_iv_skew(chain, current_price, selected_exp)


def calculate_black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Calculate Black-Scholes Greeks
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate (annual)
        sigma: Implied volatility (annual)
        option_type: 'call' or 'put'
    """
    from scipy.stats import norm
    
    if T <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0, 'price': 0}
    
    d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    
    if option_type == 'call':
        price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) 
                - r*K*np.exp(-r*T)*norm.cdf(d2)) / 365
    else:  # put
        price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
        delta = -norm.cdf(-d1)
        theta = (-(S*norm.pdf(d1)*sigma)/(2*np.sqrt(T)) 
                + r*K*np.exp(-r*T)*norm.cdf(-d2)) / 365
    
    gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
    vega = S*norm.pdf(d1)*np.sqrt(T) / 100  # Per 1% change in IV
    
    if option_type == 'call':
        rho = K*T*np.exp(-r*T)*norm.cdf(d2) / 100  # Per 1% change in rate
    else:
        rho = -K*T*np.exp(-r*T)*norm.cdf(-d2) / 100
    
    return {
        'price': price,
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }


def show_greeks_tab(data):
    """Show Greeks analysis"""
    st.subheader("📈 Greeks Analysis")
    
    current_price = data.get("current_price", 0)
    ticker = data.get("ticker", "")
    
    if current_price == 0:
        st.error("Unable to fetch current price")
        return
    
    st.markdown(f"### Current {ticker} Price: {format_currency(current_price)}")
    
    # Input parameters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        strike = st.number_input("Strike Price ($)", 
                                value=float(current_price), 
                                min_value=float(current_price)*0.5,
                                max_value=float(current_price)*1.5,
                                step=1.0)
    
    with col2:
        days_to_expiry = st.slider("Days to Expiry", 1, 365, 30)
        time_to_expiry = days_to_expiry / 365.0
    
    with col3:
        iv = st.slider("Implied Volatility (%)", 10, 150, 30) / 100.0
    
    with col4:
        option_type = st.selectbox("Option Type", ["call", "put"])
    
    # Calculate Greeks
    risk_free_rate = 0.045  # 4.5% risk-free rate
    greeks = calculate_black_scholes_greeks(
        S=current_price,
        K=strike,
        T=time_to_expiry,
        r=risk_free_rate,
        sigma=iv,
        option_type=option_type
    )
    
    # Display results
    st.markdown("---")
    st.markdown("### 📊 Option Greeks & Price")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Option Price", format_currency(greeks['price']))
        moneyness = ((current_price - strike) / strike * 100)
        if option_type == 'call':
            money_status = "ITM ✅" if current_price > strike else ("ATM" if abs(moneyness) < 2 else "OTM")
        else:
            money_status = "ITM ✅" if current_price < strike else ("ATM" if abs(moneyness) < 2 else "OTM")
        st.caption(f"{money_status} • {moneyness:+.1f}%")
    
    with col2:
        st.metric("Delta (Δ)", f"{greeks['delta']:.4f}")
        st.caption(f"${abs(greeks['delta']):.2f} move per $1 stock move")
    
    with col3:
        st.metric("Gamma (Γ)", f"{greeks['gamma']:.4f}")
        st.caption(f"Delta changes by {greeks['gamma']:.4f}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Theta (Θ)", f"{greeks['theta']:.4f}")
        st.caption(f"${abs(greeks['theta']):.2f} decay per day ⏰")
    
    with col2:
        st.metric("Vega (V)", f"{greeks['vega']:.4f}")
        st.caption(f"${greeks['vega']:.2f} per 1% IV change")
    
    with col3:
        st.metric("Rho (ρ)", f"{greeks['rho']:.4f}")
        st.caption(f"${abs(greeks['rho']):.2f} per 1% rate change")
    
    # Scenario analysis
    st.markdown("---")
    st.markdown("### 🎯 Scenario Analysis")
    
    stock_moves = [-10, -5, -2, 0, 2, 5, 10]
    scenarios = []
    
    for move in stock_moves:
        new_price = current_price * (1 + move/100)
        new_greeks = calculate_black_scholes_greeks(
            S=new_price, K=strike, T=time_to_expiry, 
            r=risk_free_rate, sigma=iv, option_type=option_type
        )
        profit = (new_greeks['price'] - greeks['price']) * 100  # Per contract
        
        scenarios.append({
            'Stock Move': f"{move:+.0f}%",
            'Stock Price': format_currency(new_price),
            'Option Price': format_currency(new_greeks['price']),
            'P&L': format_currency(profit),
            'Delta': f"{new_greeks['delta']:.3f}"
        })
    
    df_scenarios = pd.DataFrame(scenarios)
    st.dataframe(df_scenarios, use_container_width=True, hide_index=True)
    
    # Educational content
    with st.expander("📚 What do these Greeks mean?"):
        st.markdown("""
        - **Delta (Δ)**: How much option price changes per $1 stock move
            - Calls: 0 to 1 | Puts: -1 to 0
            - 0.50 Delta = $0.50 option move per $1 stock move
        
        - **Gamma (Γ)**: Rate of change of Delta
            - High gamma = Delta changes fast (risky but profitable!)
            - Highest at-the-money
        
        - **Theta (Θ)**: Time decay per day
            - How much option loses value each day
            - Sellers love theta! Buyers hate it! ⏰
        
        - **Vega (V)**: Sensitivity to IV changes
            - High vega = Big moves when IV spikes
            - Great for earnings plays
        
        - **Rho (ρ)**: Sensitivity to interest rates
            - Usually least important for retail
        """)
    
    st.warning("⚠️ **Remember**: Options can expire worthless! Don't YOLO your rent money! 🏠")


def show_strategy_tab(data):
    """Show options strategy ideas"""
    st.subheader("🎯 Options Strategy Builder")
    
    current_price = data["current_price"]
    ticker = data["ticker"]
    
    st.markdown(f"### Current {ticker} Price: {format_currency(current_price)}")
    
    # Service Layer Recommendations
    if "service_result" in data:
        st.markdown("### 🤖 AI Strategy Recommendations")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            outlook = st.selectbox(
                "Market Outlook",
                ["bullish", "bearish", "neutral"],
                help="What's your view on the stock?"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎯 Get Recommendations", type="primary"):
                from src.services import OptionsAnalysisService
                components = st.session_state.get('components', {})
                service = OptionsAnalysisService(components)
                
                strategies = service.get_strategy_recommendations(ticker, current_price, outlook)
                
                if strategies:
                    st.success(f"✅ Found {len(strategies)} strategies for {outlook} outlook")
                    
                    for i, strat in enumerate(strategies, 1):
                        with st.expander(f"📋 Strategy {i}: {strat['name']}", expanded=(i==1)):
                            st.markdown(f"**Description:** {strat['description']}")
                            st.markdown(f"**Max Profit:** {strat.get('max_profit', 'Unlimited')}")
                            st.markdown(f"**Max Loss:** {strat.get('max_loss', 'Limited')}")
                            st.markdown(f"**Risk Level:** {strat.get('risk_level', 'Medium')}")
                            
                            if 'legs' in strat:
                                st.markdown("**Legs:**")
                                for leg in strat['legs']:
                                    st.code(leg)
                else:
                    st.info("No strategies found for this outlook")
        
        st.markdown("---")
    
    # Strategy selector
    strategy = st.selectbox(
        "Choose a Strategy",
        [
            "🚀 Long Call (Bullish YOLO)",
            "📉 Long Put (Bearish)",
            "💰 Covered Call (Income)",
            "🛡️ Cash-Secured Put (Wheel)",
            "🦋 Iron Condor (Theta Gang)",
            "⚡ Straddle (Earnings Play)",
            "🎯 Bull Call Spread (Moderate Bullish)"
        ]
    )
    
    st.markdown("---")
    
    if "Long Call" in strategy:
        st.markdown("### 🚀 Long Call Strategy")
        st.success("**When to use**: You think stock will moon! 🌙")
        st.markdown(f"""
        **Setup:**
        - Buy 1 call option at strike {format_currency(current_price * 1.05)} (5% OTM)
        - Choose expiration 30-60 days out
        - Max loss: Premium paid
        - Max gain: Unlimited! 🚀
        
        **Example:**
        - Stock at {format_currency(current_price)}
        - Buy {format_currency(current_price * 1.05)} call for $2.00
        - If stock hits {format_currency(current_price * 1.20)}, profit = {format_currency(current_price * 0.15 - 2)} per share!
        - Breakeven: {format_currency(current_price * 1.05 + 2)}
        """)
        
    elif "Long Put" in strategy:
        st.markdown("### 📉 Long Put Strategy")
        st.warning("**When to use**: You think stock will tank! 📉")
        st.markdown(f"""
        **Setup:**
        - Buy 1 put option at strike {format_currency(current_price * 0.95)} (5% OTM)
        - Max loss: Premium paid
        - Max gain: Strike - premium (if stock goes to $0)
        
        **Risk**: Puts can lose value fast if stock rallies!
        """)
        
    elif "Covered Call" in strategy:
        st.markdown("### 💰 Covered Call (Theta Gang)")
        st.success("**When to use**: You own 100 shares, want income! 💵")
        st.markdown(f"""
        **Setup:**
        - Own 100 shares of {ticker}
        - Sell 1 call at {format_currency(current_price * 1.10)} strike
        - Collect premium immediately!
        - If called away: Profit on shares + premium
        
        **Risk**: Limited upside if stock moons past strike
        **Reward**: Consistent income, reduces cost basis
        """)
        
    elif "Iron Condor" in strategy:
        st.markdown("### 🦋 Iron Condor (Theta Gang)")
        st.info("**When to use**: Stock will stay flat 📊")
        st.markdown(f"""
        **Setup** (Complex but profitable!):
        - Sell call at {format_currency(current_price * 1.05)}
        - Buy call at {format_currency(current_price * 1.10)}
        - Sell put at {format_currency(current_price * 0.95)}
        - Buy put at {format_currency(current_price * 0.90)}
        
        **Max Profit**: Premium collected (if stock stays between sold strikes)
        **Max Loss**: Width of spread - premium
        
        **Best for**: High IV, rangebound stocks
        """)
        
    elif "Straddle" in strategy:
        st.markdown("### ⚡ Long Straddle (Earnings Play)")
        st.warning("**When to use**: Big move expected, unsure direction! 📊")
        st.markdown(f"""
        **Setup:**
        - Buy ATM call at {format_currency(current_price)}
        - Buy ATM put at {format_currency(current_price)}
        
        **Wins if**: Stock moves big in EITHER direction!
        **Loses if**: Stock doesn't move (theta decay)
        
        **Perfect for**: Earnings announcements 📣
        """)
    
    st.markdown("---")
    st.error("⚠️ **DISCLAIMER**: Options are risky! Can lose 100% of premium. Not financial advice! 🚨")


def render_gex_profile(chain, current_price, selected_exp):
    """
    Render Gamma Exposure (GEX) Profile
    Shows dealer hedging impact at each strike
    """
    try:
        if not chain or not isinstance(chain, dict):
            st.warning("No options data available for GEX analysis")
            return
        
        # Extract calls and puts from chain dict
        calls_list = chain.get('calls', [])
        puts_list = chain.get('puts', [])
        
        if not calls_list and not puts_list:
            st.warning(f"No options data for expiration {selected_exp}")
            return
        
        # Convert to DataFrames
        calls_df = pd.DataFrame(calls_list) if calls_list else pd.DataFrame()
        puts_df = pd.DataFrame(puts_list) if puts_list else pd.DataFrame()
        
        # Get all unique strikes
        all_strikes = set()
        if not calls_df.empty and 'strike' in calls_df.columns:
            all_strikes.update(calls_df['strike'].tolist())
        if not puts_df.empty and 'strike' in puts_df.columns:
            all_strikes.update(puts_df['strike'].tolist())
        
        if not all_strikes:
            st.warning("No strike data available")
            return
        
        # Calculate GEX for each strike
        gex_data = []
        for strike in sorted(all_strikes):
            # Get call and put data at this strike
            call_rows = calls_df[calls_df['strike'] == strike] if not calls_df.empty else pd.DataFrame()
            put_rows = puts_df[puts_df['strike'] == strike] if not puts_df.empty else pd.DataFrame()
            
            call_gamma = call_rows['gamma'].sum() if not call_rows.empty and 'gamma' in call_rows.columns else 0
            put_gamma = put_rows['gamma'].sum() if not put_rows.empty and 'gamma' in put_rows.columns else 0
            
            call_oi = call_rows['openInterest'].sum() if not call_rows.empty and 'openInterest' in call_rows.columns else 0
            put_oi = put_rows['openInterest'].sum() if not put_rows.empty and 'openInterest' in put_rows.columns else 0
            
            # GEX = (Call Gamma * Call OI - Put Gamma * Put OI) * 100 * Stock Price^2
            gex = (call_gamma * call_oi - put_gamma * put_oi) * 100 * current_price ** 2
            
            gex_data.append({
                'strike': strike,
                'gex': gex / 1e9,  # Convert to billions
                'call_oi': call_oi,
                'put_oi': put_oi
            })
        
        gex_df = pd.DataFrame(gex_data)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Separate positive and negative GEX
        positive_gex = gex_df[gex_df['gex'] >= 0]
        negative_gex = gex_df[gex_df['gex'] < 0]
        
        # Positive GEX (green) - price attraction
        fig.add_trace(go.Bar(
            y=positive_gex['strike'],
            x=positive_gex['gex'],
            orientation='h',
            name='Positive Gamma (Attraction)',
            marker_color='#00ff88',
            text=positive_gex['gex'].apply(lambda x: f'{x:.2f}B'),
            textposition='outside',
            hovertemplate='<b>Strike:</b> $%{y:.2f}<br>' +
                         '<b>GEX:</b> %{x:.2f}B<br>' +
                         '<extra></extra>'
        ))
        
        # Negative GEX (red) - price repulsion
        fig.add_trace(go.Bar(
            y=negative_gex['strike'],
            x=negative_gex['gex'],
            orientation='h',
            name='Negative Gamma (Repulsion)',
            marker_color='#ff4444',
            text=negative_gex['gex'].apply(lambda x: f'{x:.2f}B'),
            textposition='outside',
            hovertemplate='<b>Strike:</b> $%{y:.2f}<br>' +
                         '<b>GEX:</b> %{x:.2f}B<br>' +
                         '<extra></extra>'
        ))
        
        # Add current price line
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="cyan",
            annotation_text=f"Current: ${current_price:.2f}",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="Gamma Exposure (GEX) Profile",
            xaxis_title="Gamma Exposure (Billions)",
            yaxis_title="Strike Price",
            height=600,
            showlegend=True,
            hovermode='closest',
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        max_positive = gex_df.loc[gex_df['gex'].idxmax()] if not gex_df.empty else None
        max_negative = gex_df.loc[gex_df['gex'].idxmin()] if not gex_df.empty else None
        
        col1, col2 = st.columns(2)
        with col1:
            if max_positive is not None and max_positive['gex'] > 0:
                st.metric(
                    "🟢 Max Positive GEX (Attraction)",
                    f"${max_positive['strike']:.2f}",
                    f"{max_positive['gex']:.2f}B"
                )
        with col2:
            if max_negative is not None and max_negative['gex'] < 0:
                st.metric(
                    "🔴 Max Negative GEX (Repulsion)",
                    f"${max_negative['strike']:.2f}",
                    f"{max_negative['gex']:.2f}B"
                )
        
    except Exception as e:
        st.error(f"Error rendering GEX profile: {str(e)}")


def render_oi_profile(chain, current_price):
    """
    Render Open Interest Profile
    Shows concentration of outstanding contracts at each strike
    """
    try:
        if not chain or not isinstance(chain, dict):
            st.warning("No options data available for OI analysis")
            return
        
        # Extract calls and puts
        calls_list = chain.get('calls', [])
        puts_list = chain.get('puts', [])
        
        if not calls_list and not puts_list:
            st.warning("No options data available")
            return
        
        calls_df = pd.DataFrame(calls_list) if calls_list else pd.DataFrame()
        puts_df = pd.DataFrame(puts_list) if puts_list else pd.DataFrame()
        
        # Get all unique strikes
        all_strikes = set()
        if not calls_df.empty and 'strike' in calls_df.columns:
            all_strikes.update(calls_df['strike'].tolist())
        if not puts_df.empty and 'strike' in puts_df.columns:
            all_strikes.update(puts_df['strike'].tolist())
        
        if not all_strikes:
            st.warning("No strike data available")
            return
        
        # Aggregate OI by strike
        oi_data = []
        for strike in sorted(all_strikes):
            call_rows = calls_df[calls_df['strike'] == strike] if not calls_df.empty else pd.DataFrame()
            put_rows = puts_df[puts_df['strike'] == strike] if not puts_df.empty else pd.DataFrame()
            
            call_oi = call_rows['openInterest'].sum() if not call_rows.empty and 'openInterest' in call_rows.columns else 0
            put_oi = put_rows['openInterest'].sum() if not put_rows.empty and 'openInterest' in put_rows.columns else 0
            total_oi = call_oi + put_oi
            
            oi_data.append({
                'strike': strike,
                'call_oi': call_oi,
                'put_oi': put_oi,
                'total_oi': total_oi
            })
        
        oi_df = pd.DataFrame(oi_data)
        
        # Find OI walls (top 5 strikes by total OI)
        oi_walls = oi_df.nlargest(5, 'total_oi')
        
        # Create horizontal stacked bar chart
        fig = go.Figure()
        
        # Put OI (left side, negative values for visual)
        fig.add_trace(go.Bar(
            y=oi_df['strike'],
            x=-oi_df['put_oi'],
            orientation='h',
            name='Put OI',
            marker_color='#ff6b6b',
            text=oi_df['put_oi'].apply(lambda x: f'{x:,.0f}'),
            textposition='inside',
            hovertemplate='<b>Strike:</b> $%{y:.2f}<br>' +
                         '<b>Put OI:</b> %{text}<br>' +
                         '<extra></extra>'
        ))
        
        # Call OI (right side, positive values)
        fig.add_trace(go.Bar(
            y=oi_df['strike'],
            x=oi_df['call_oi'],
            orientation='h',
            name='Call OI',
            marker_color='#51cf66',
            text=oi_df['call_oi'].apply(lambda x: f'{x:,.0f}'),
            textposition='inside',
            hovertemplate='<b>Strike:</b> $%{y:.2f}<br>' +
                         '<b>Call OI:</b> %{text}<br>' +
                         '<extra></extra>'
        ))
        
        # Mark OI walls
        for _, wall in oi_walls.iterrows():
            fig.add_annotation(
                y=wall['strike'],
                x=0,
                text="🏛️ OI WALL",
                showarrow=True,
                arrowhead=2,
                arrowcolor="yellow",
                font=dict(color="yellow", size=10)
            )
        
        # Add current price line
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="cyan",
            annotation_text=f"Current: ${current_price:.2f}",
            annotation_position="right"
        )
        
        fig.update_layout(
            title="Open Interest Profile (Calls vs Puts)",
            xaxis_title="Open Interest (Contracts)",
            yaxis_title="Strike Price",
            height=600,
            showlegend=True,
            barmode='relative',
            hovermode='closest',
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display OI walls
        st.markdown("#### 🏛️ Major OI Walls (Top 5)")
        for i, wall in oi_walls.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Strike", f"${wall['strike']:.2f}")
            with col2:
                st.metric("Total OI", f"{wall['total_oi']:,.0f}")
            with col3:
                st.metric("Call OI", f"{wall['call_oi']:,.0f}")
            with col4:
                st.metric("Put OI", f"{wall['put_oi']:,.0f}")
            st.markdown("---")
        
    except Exception as e:
        st.error(f"Error rendering OI profile: {str(e)}")


def render_pcr_chart(ticker):
    """
    Render Put/Call Ratio over time
    Shows sentiment shifts
    """
    try:
        import yfinance as yf
        
        # Fetch historical options data (last 30 days)
        stock = yf.Ticker(ticker)
        
        # Get available expirations
        expirations = stock.options
        
        if not expirations:
            st.warning("No options data available for PCR analysis")
            return
        
        # Calculate PCR for recent expirations
        pcr_data = []
        for exp in expirations[:10]:  # Last 10 expirations
            try:
                chain = stock.option_chain(exp)
                put_volume = chain.puts['volume'].sum()
                call_volume = chain.calls['volume'].sum()
                
                if call_volume > 0:
                    pcr = put_volume / call_volume
                    pcr_data.append({
                        'date': pd.to_datetime(exp),
                        'pcr': pcr,
                        'put_vol': put_volume,
                        'call_vol': call_volume
                    })
            except:
                continue
        
        if not pcr_data:
            st.warning("Unable to calculate PCR data")
            return
        
        pcr_df = pd.DataFrame(pcr_data).sort_values('date')
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=pcr_df['date'],
            y=pcr_df['pcr'],
            mode='lines+markers',
            name='PCR',
            line=dict(color='cyan', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Date:</b> %{x}<br>' +
                         '<b>PCR:</b> %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add reference lines
        fig.add_hline(y=0.7, line_dash="dot", line_color="green",
                     annotation_text="Greedy (0.7)", annotation_position="right")
        fig.add_hline(y=1.0, line_dash="dash", line_color="yellow",
                     annotation_text="Neutral (1.0)", annotation_position="right")
        fig.add_hline(y=1.3, line_dash="dot", line_color="red",
                     annotation_text="Fearful (1.3)", annotation_position="right")
        
        fig.update_layout(
            title=f"Put/Call Ratio (PCR) - {ticker}",
            xaxis_title="Expiration Date",
            yaxis_title="PCR (Put Volume / Call Volume)",
            height=500,
            hovermode='x unified',
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Current sentiment
        latest_pcr = pcr_df.iloc[-1]
        if latest_pcr['pcr'] < 0.7:
            sentiment = "🟢 GREEDY"
            color = "green"
        elif latest_pcr['pcr'] > 1.3:
            sentiment = "🔴 FEARFUL"
            color = "red"
        else:
            sentiment = "🟡 NEUTRAL"
            color = "yellow"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current PCR", f"{latest_pcr['pcr']:.2f}")
        with col2:
            st.metric("Sentiment", sentiment)
        with col3:
            st.metric("Put Volume", f"{latest_pcr['put_vol']:,.0f}")
        
    except Exception as e:
        st.error(f"Error rendering PCR chart: {str(e)}")


def render_iv_skew(chain, current_price, selected_exp):
    """
    Render Implied Volatility Skew
    Shows how IV changes across strikes
    """
    try:
        if not chain or not isinstance(chain, dict):
            st.warning("No options data available for IV skew analysis")
            return
        
        # Extract calls and puts
        calls_list = chain.get('calls', [])
        puts_list = chain.get('puts', [])
        
        if not calls_list and not puts_list:
            st.warning("No options data available")
            return
        
        # Convert to DataFrames
        calls = pd.DataFrame(calls_list) if calls_list else pd.DataFrame()
        puts = pd.DataFrame(puts_list) if puts_list else pd.DataFrame()
        
        # Calculate moneyness if we have strike and impliedVolatility columns
        if not calls.empty and 'strike' in calls.columns and 'impliedVolatility' in calls.columns:
            calls['moneyness'] = (calls['strike'] / current_price - 1) * 100
            # Filter out invalid IV values
            calls = calls[(calls['impliedVolatility'] > 0) & (calls['impliedVolatility'] < 5)]
        else:
            calls = pd.DataFrame()
        
        if not puts.empty and 'strike' in puts.columns and 'impliedVolatility' in puts.columns:
            puts['moneyness'] = (puts['strike'] / current_price - 1) * 100
            # Filter out invalid IV values
            puts = puts[(puts['impliedVolatility'] > 0) & (puts['impliedVolatility'] < 5)]
        else:
            puts = pd.DataFrame()
        
        if calls.empty and puts.empty:
            st.warning("No valid IV data available for skew analysis")
            return
        
        # Create scatter plot
        fig = go.Figure()
        
        # Calls
        fig.add_trace(go.Scatter(
            x=calls['moneyness'],
            y=calls['impliedVolatility'] * 100,
            mode='markers+lines',
            name='Calls',
            marker=dict(size=8, color='#51cf66'),
            line=dict(width=2),
            hovertemplate='<b>Moneyness:</b> %{x:.1f}%<br>' +
                         '<b>IV:</b> %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Puts
        fig.add_trace(go.Scatter(
            x=puts['moneyness'],
            y=puts['impliedVolatility'] * 100,
            mode='markers+lines',
            name='Puts',
            marker=dict(size=8, color='#ff6b6b'),
            line=dict(width=2),
            hovertemplate='<b>Moneyness:</b> %{x:.1f}%<br>' +
                         '<b>IV:</b> %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Add ATM line
        fig.add_vline(
            x=0,
            line_dash="dash",
            line_color="cyan",
            annotation_text="ATM",
            annotation_position="top"
        )
        
        fig.update_layout(
            title=f"Implied Volatility Skew - {selected_exp}",
            xaxis_title="Moneyness (% from ATM)",
            yaxis_title="Implied Volatility (%)",
            height=500,
            hovermode='closest',
            template='plotly_dark',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate skew metrics
        otm_puts = puts[puts['strike'] < current_price * 0.95]
        atm_calls = calls[(calls['strike'] >= current_price * 0.98) & (calls['strike'] <= current_price * 1.02)]
        
        if not otm_puts.empty and not atm_calls.empty:
            put_iv_avg = otm_puts['impliedVolatility'].mean() * 100
            call_iv_avg = atm_calls['impliedVolatility'].mean() * 100
            skew = put_iv_avg - call_iv_avg
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("OTM Put IV (Avg)", f"{put_iv_avg:.1f}%")
            with col2:
                st.metric("ATM Call IV (Avg)", f"{call_iv_avg:.1f}%")
            with col3:
                skew_label = "🔴 HIGH" if skew > 10 else "🟡 NORMAL" if skew > 5 else "🟢 LOW"
                st.metric("Skew", f"{skew:.1f}%", skew_label)
            
            if skew > 10:
                st.info("📊 **High skew** suggests strong demand for downside protection (puts)")
            elif skew < 0:
                st.warning("⚠️ **Negative skew** is unusual - may indicate strong bullish sentiment")
        
    except Exception as e:
        st.error(f"Error rendering IV skew: {str(e)}")
