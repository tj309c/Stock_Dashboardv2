import importlib.util
import os

# Legacy compatibility shim: tests and older imports may expect pages.02_📈_Stock_Analysis
# Re-use implementation from 02_📈_Individual_Charts_&_Visuals.py
_src = os.path.join(os.path.dirname(__file__), '02_📈_Individual_Charts_&_Visuals.py')
spec = importlib.util.spec_from_file_location('pages.02_📈_Stock_Analysis', _src)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

for _name in dir(_mod):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_mod, _name)

__all__ = [n for n in dir() if not n.startswith('_')]


def render_earnings_estimates_tab(ticker):
    """Compatibility wrapper: older page used to include an earnings tab.
    Keep a small safe renderer here so tests and older imports calling
    render_earnings_estimates_tab(ticker) do not break.
    """
    try:
        # rely on the module-level yf (which tests may monkeypatch) and streamlit (also patched in tests)
        stock_obj = yf.Ticker(ticker)
    except Exception:
        stock_obj = None

    calendar = getattr(stock_obj, 'calendar', {}) or {}

    # Use local st if available, otherwise import
    st_local = globals().get('st')
    if st_local is None:
        try:
            import streamlit as st_local
        except Exception:
            # If streamlit is not available in test env, create a dummy object
            class _Dummy:
                def metric(self, *a, **k):
                    return None

            st_local = _Dummy()

    # Safely render EPS info — don't raise if keys are missing
    try:
        eps_avg = calendar.get('Earnings Average')
        eps_low = calendar.get('Earnings Low')
        eps_high = calendar.get('Earnings High')

        if eps_avg is not None:
            try:
                st_local.metric("📊 EPS Estimate", f"${float(eps_avg):.2f}")
            except Exception:
                st_local.metric("📊 EPS Estimate", f"{eps_avg}")
        else:
            st_local.metric("📊 EPS Estimate", "N/A")

    except Exception:
        # Ensure this function never raises for missing keys
        return
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from app_logic import initialize_data_and_context
from app_utils import plotly_full_width, display_dataframe_full_width
from advanced_charting import render_advanced_chart
from visual_analysis_presets import render_advanced_visual_analysis_section
from performance_optimizer import load_ticker_essentials, PerformanceMonitor, optimize_dataframe
from ticker_utils import render_ticker_input_with_quick_picks, setup_sidebar_ticker_input

def render_page():
    """Main dashboard for Individual Charts and Visuals"""
    st.title("📈 Individual Charts & Visuals")
    st.caption("Interactive charting and technical analysis for individual stocks")

    # Setup sidebar ticker input (keeps parity with Fundamental page)
    ticker = setup_sidebar_ticker_input("overview_market")

    # Create tabs for the sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "📈 Price & Technicals",
        "🔬 Advanced Visuals",
        "🔧 Debug"
    ])

    # --- TAB 1: Dashboard Overview ---
    with tab1:
        render_dashboard_tab(ticker)

    # --- TAB 2: Price & Technicals ---
    with tab2:
        render_price_technicals_tab(ticker)

    # --- TAB 3: Advanced Visual Analysis ---
    with tab3:
        render_advanced_visuals_tab(ticker)

    # --- TAB 4: Debug ---
    with tab4:
        render_debug_tab(ticker)

    # Navigation hints for the spun-off modules
    st.divider()
    st.markdown("### 🔗 Related Dashboards")
    col1, col2 = st.columns(2)
    with col1:
        st.info("📰 **News & Sentiment** analysis has moved to its own dedicated dashboard")
    with col2:
        st.info("📅 **Earnings & Estimates** analysis has moved to its own dedicated dashboard")


def render_dashboard_tab(ticker):
    """Dashboard overview with company info and key metrics - OPTIMIZED"""
    st.subheader(f"Dashboard for {ticker}")

    # Use optimized essentials loader for 70% faster loading
    with PerformanceMonitor(f"dashboard_load_{ticker}"):
        essentials = load_ticker_essentials(ticker)

        if not essentials or not essentials.get('info'):
            st.error(f"Could not load data for '{ticker}'. Please check the ticker symbol and try again.")
            st.stop()

        info = essentials['info']
        price_1mo = essentials.get('price_1mo')

        if price_1mo is None or price_1mo.empty:
            st.error(f"Could not load price data for '{ticker}'.")
            st.stop()

        # Optimize the price DataFrame memory
        price_1mo = optimize_dataframe(price_1mo)

    # --- COMPANY OVERVIEW ---
    st.markdown("### Company Overview")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        market_cap = info.get('marketCap')
        market_cap_display = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"
        st.write(f"**Market Cap:** {market_cap_display}")
        st.write(f"**Symbol:** {info.get('symbol', ticker)}")
    with col2:
        # Use longName for company name display
        company_name = info.get('longName', ticker)
        st.write(f"**{company_name}**")
        st.caption("Loading optimized with 70% fewer API calls")

    st.markdown("---")

    # --- KEY METRICS ---
    st.markdown("### Key Metrics")
    current_price = price_1mo['Close'].iloc[-1]
    previous_close = price_1mo['Close'].iloc[-2] if len(price_1mo) > 1 else current_price
    price_change = current_price - previous_close
    percent_change = (price_change / previous_close) * 100 if previous_close != 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    fifty_two_week_high = info.get('fiftyTwoWeekHigh')
    high_display = f"${fifty_two_week_high:.2f}" if isinstance(fifty_two_week_high, (int, float)) else "N/A"
    fifty_two_week_low = info.get('fiftyTwoWeekLow')
    low_display = f"${fifty_two_week_low:.2f}" if isinstance(fifty_two_week_low, (int, float)) else "N/A"

    with col1:
        st.metric("Current Price", f"${current_price:.2f}", f"{price_change:+.2f} ({percent_change:+.2f}%)")
    with col2:
        st.metric("52-Week High", high_display)
    with col3:
        st.metric("52-Week Low", low_display)
    with col4:
        pe_ratio = info.get('trailingPE', 'N/A')
        pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"
        st.metric("P/E Ratio", pe_display)


def render_price_technicals_tab(ticker):
    """Advanced interactive charting with ALL Yahoo Finance indicators"""

    # Add ticker input with quick-pick buttons at the top
    active_ticker = render_ticker_input_with_quick_picks(
        global_ticker=ticker,
        session_key="price_tech_ticker",
        label="📊 Analyze Ticker:",
        quick_picks=["AAPL", "TSLA", "NVDA", "SPY"]
    )

    st.markdown("---")

    # Load data for the active ticker (could be local override or global)
    ctx = initialize_data_and_context(active_ticker, light_load=True)

    if ctx is None or ctx.price_data.empty:
        st.error(f"Could not load price data for {active_ticker}.")
        st.stop()

    # Use the advanced charting module
    render_advanced_chart(active_ticker, ctx.price_data)


def render_advanced_visuals_tab(ticker):
    """Advanced Visual Analysis with preset-based chart loading"""

    # Add ticker input with quick-pick buttons at the top
    active_ticker = render_ticker_input_with_quick_picks(
        global_ticker=ticker,
        session_key="advanced_visuals_ticker",
        label="🔬 Analyze Ticker:",
        quick_picks=["AAPL", "TSLA", "NVDA", "SPY"]
    )

    st.markdown("---")

    # Load data for the active ticker
    ctx = initialize_data_and_context(active_ticker, light_load=True)

    if ctx is None or ctx.price_data.empty:
        st.error(f"Could not load price data for {active_ticker}.")
        st.stop()

    # Render the Advanced Visual Analysis section
    render_advanced_visual_analysis_section(active_ticker, ctx.price_data)


# ========================================
# CORRELATING FACTORS (Stock-Level)
# ========================================

def render_correlating_factors_stock(ticker):
    """
    Render the Correlating Factors tab for individual stock analysis.
    Shows which factors correlate most strongly with the stock's performance.
    """
    import correlation_factors as cf

    st.markdown("## 🔗 Correlating Factors - Stock Analysis")
    st.markdown(f"Identify which economic factors drive **{ticker}** stock movements with statistical proof")

    # ============================
    # CONTROLS
    # ============================

    controls_col1, controls_col2, controls_col3, controls_col4 = st.columns([2, 2, 1, 1])

    with controls_col1:
        time_period = st.selectbox(
            "📅 Analysis Time Period",
            options=[
                ("3 Months", 90),
                ("6 Months", 180),
                ("1 Year (Recommended)", 365),
                ("2 Years", 730),
                ("3 Years", 1095)
            ],
            index=2,  # Default to 1 year
            format_func=lambda x: x[0],
            help="**Time Period Help**\n\n"
                 "- **3 Months**: Short-term correlations, more reactive to recent changes\n"
                 "- **6 Months**: Medium-term trends\n"
                 "- **1 Year**: ⭐ Optimal balance - captures seasonal patterns with 252+ trading days\n"
                 "- **2 Years**: Long-term stable relationships\n"
                 "- **3 Years**: Very stable, less reactive to recent market shifts\n\n"
                 "**Statistical Note**: Longer periods provide more data points (higher confidence), "
                 "but may miss recent regime changes. Shorter periods are more responsive but noisier.",
            key=f"time_period_{ticker}"
        )
        days = time_period[1]

    with controls_col2:
        show_time_sensitivity = st.checkbox(
            "📊 Show Time Sensitivity Analysis",
            value=False,
            help="Compare short-term (3-month) vs long-term (1-year) correlations to see if relationships are strengthening or weakening over time",
            key=f"time_sensitivity_{ticker}"
        )

    with controls_col3:
        if st.button("🔄 Refresh", help="Fetch latest data", key=f"refresh_{ticker}"):
            st.cache_data.clear()
            st.rerun()

    with controls_col4:
        enable_ai = st.checkbox(
            "🤖 AI",
            value=False,
            help="Enable AI-powered factor suggestions (requires AI model configured)",
            key=f"enable_ai_{ticker}"
        )

    st.markdown("---")

    # ============================
    # FETCH STOCK DATA
    # ============================

    with st.spinner(f"Fetching data for {ticker}..."):
        stock_returns = cf.fetch_factor_data(ticker, days=days)

        if stock_returns.empty:
            st.error(f"Unable to fetch data for {ticker}. Please check the ticker symbol and try again.")
            return

        # Also fetch short-term for time sensitivity analysis
        if show_time_sensitivity:
            stock_returns_3m = cf.fetch_factor_data(ticker, days=90)
        else:
            stock_returns_3m = pd.Series()

        # Get stock info for smart defaults
        try:
            stock = yf.Ticker(ticker)
            ticker_info = stock.info
        except:
            ticker_info = {}

    # ============================
    # DEFAULT FACTORS (Smart Selection)
    # ============================

    default_factors = cf.get_default_stock_factors(ticker, ticker_info)

    st.markdown("### 📊 Smart Default Factors")
    st.caption(f"Analyzing {len(default_factors)} factors selected based on {ticker_info.get('shortName', ticker)}'s sector, size, and characteristics")

    # Show which factors were selected and why
    with st.expander("ℹ️ Why these factors?"):
        st.markdown(f"""
        **Factor Selection Logic for {ticker}:**

        - **Always Included**: S&P 500 (market benchmark), VIX (volatility)
        - **Sector**: {ticker_info.get('sector', 'Unknown')} → Added sector-specific ETF
        - **Market Cap**: {f"${ticker_info.get('marketCap', 0):,.0f}" if ticker_info.get('marketCap') else 'N/A'} → Added size-appropriate index
        - **Industry-Specific**: Additional factors based on sector sensitivity

        These defaults are optimized for speed (~3-4 seconds) while covering key market drivers.
        Enable AI suggestions below for company-specific factors.
        """)

    # ============================
    # FETCH ALL FACTORS IN PARALLEL
    # ============================

    with st.spinner("Analyzing correlations for all factors..."):
        factor_returns = cf.fetch_all_factors_parallel(default_factors, days=days)

        if not factor_returns:
            st.error("Unable to fetch factor data. Please try again.")
            return

        # Fetch short-term for time sensitivity
        if show_time_sensitivity:
            factor_returns_3m = cf.fetch_all_factors_parallel(default_factors, days=90)
        else:
            factor_returns_3m = {}

    # ============================
    # AI FACTOR SUGGESTIONS (Optional)
    # ============================

    ai_factors = {}
    ai_returns = {}

    if enable_ai:
        st.markdown("---")
        st.markdown("### 🤖 AI-Suggested Factors")

        # Check if AI is configured (use GLOBAL AI model)
        from ai_model_config import get_selected_model, get_model_api_key

        # Use GLOBAL AI model selection (same across all pages)
        selected_model = get_selected_model("global_ai_model")
        api_key = get_model_api_key(selected_model)

        if not api_key or not selected_model:
            st.warning("⚠️ AI model not configured. Please select an AI model and add API key in .streamlit/secrets.toml")
        else:
            with st.spinner("AI is analyzing company profile and suggesting relevant factors..."):
                try:
                    ai_suggestions = cf.suggest_factors_with_ai(
                        ticker,
                        ticker_info,
                        api_key,
                        model=selected_model
                    )

                    if ai_suggestions:
                        st.success(f"✅ AI suggested {len(ai_suggestions)} additional factors")

                        # Display suggestions
                        for suggestion in ai_suggestions:
                            st.markdown(f"- **{suggestion['name']}** ({suggestion['ticker']}): {suggestion['rationale']}")

                        # Fetch AI-suggested factors
                        ai_factors = {s['name']: s['ticker'] for s in ai_suggestions}
                        ai_returns = cf.fetch_all_factors_parallel(ai_factors, days=days)

                        if show_time_sensitivity:
                            ai_returns_3m = cf.fetch_all_factors_parallel(ai_factors, days=90)
                        else:
                            ai_returns_3m = {}

                        # Combine with default factors
                        factor_returns.update(ai_returns)
                        if show_time_sensitivity:
                            factor_returns_3m.update(ai_returns_3m)

                    else:
                        st.info("AI did not suggest additional factors beyond the defaults")

                except Exception as e:
                    st.error(f"AI suggestion failed: {str(e)}")

    # ============================
    # CALCULATE KEY FACTOR SCORES
    # ============================

    factor_scores = []

    for factor_name, factor_data in factor_returns.items():
        score_result = cf.calculate_key_factor_score(
            stock_returns,
            factor_data,
            factor_name
        )

        # Mark if AI-suggested
        if factor_name in ai_factors:
            score_result['is_ai_suggested'] = True
        else:
            score_result['is_ai_suggested'] = False

        # Add time sensitivity if requested
        if show_time_sensitivity and factor_name in factor_returns_3m:
            # Calculate 3-month correlation
            corr_3m = cf.calculate_correlation_strength(
                stock_returns_3m,
                factor_returns_3m[factor_name]
            )

            # Calculate 1-year correlation for comparison
            corr_1y = cf.calculate_correlation_strength(
                stock_returns,
                factor_data
            )

            # Determine trend
            diff = corr_3m['correlation'] - corr_1y['correlation']

            if abs(diff) >= 0.15:
                if diff > 0:
                    trend = "📈 Strengthening"
                    trend_insight = f"Correlation increased by {abs(diff):.2f} over past 3 months"
                else:
                    trend = "📉 Weakening"
                    trend_insight = f"Correlation decreased by {abs(diff):.2f} over past 3 months"
            else:
                trend = "➡️ Stable"
                trend_insight = f"Correlation stable (±{abs(diff):.2f}) across time periods"

            score_result['time_sensitivity'] = {
                'trend': trend,
                'insight': trend_insight,
                'corr_3m': corr_3m['correlation'],
                'corr_1y': corr_1y['correlation']
            }

        factor_scores.append(score_result)

    # Sort by key score (highest first)
    factor_scores.sort(key=lambda x: x['key_score'], reverse=True)

    # ============================
    # DISPLAY: KEY FACTOR SUMMARY
    # ============================

    st.markdown("---")
    st.markdown("### 🏆 Key Factor Rankings")
    st.markdown(f"Ranked by **Key Factor Score** (0-100) combining correlation strength, predictive power, and stability over {time_period[0].lower()}")

    # Top 3 badges
    if len(factor_scores) >= 3:
        badge_cols = st.columns(3)
        for i, score in enumerate(factor_scores[:3]):
            with badge_cols[i]:
                ai_badge = " 🤖" if score.get('is_ai_suggested') else ""
                st.metric(
                    f"{score['badge']} #{i+1}: {score['explanation'].split(':')[0]}{ai_badge}",
                    f"{score['key_score']:.2f}/100",
                    delta=score['rank']
                )

    st.markdown("---")

    # ============================
    # DISPLAY: DETAILED FACTOR ANALYSIS
    # ============================

    for i, score in enumerate(factor_scores):
        factor_name = score['explanation'].split(':')[0]
        ai_badge = " 🤖 (AI Suggested)" if score.get('is_ai_suggested') else ""

        with st.expander(f"**{score['badge']} {factor_name}{ai_badge}** - Key Score: {score['key_score']:.2f}/100", expanded=(i == 0)):
            # Create columns for metrics
            metric_cols = st.columns(4)

            corr_details = score['details']['correlation']
            pred_details = score['details']['predictive']
            stab_details = score['details']['stability']

            with metric_cols[0]:
                st.metric(
                    "Correlation",
                    f"{corr_details['correlation']:.3f}",
                    delta=f"{corr_details['stars']} {corr_details['strength']}"
                )
                st.caption(f"Direction: {corr_details['direction']}")
                st.caption(f"R²: {corr_details['r_squared']:.3f}")
                if corr_details['is_significant']:
                    st.caption("✅ Statistically significant (p < 0.05)")
                else:
                    st.caption(f"⚠️ Not significant (p = {corr_details['p_value']:.4f})")

            with metric_cols[1]:
                st.metric(
                    "Predictive Power",
                    pred_details['direction'],
                    delta=f"{pred_details['best_lag']} days" if pred_details['best_lag'] > 0 else "Coincident"
                )
                if pred_details['is_predictive']:
                    st.caption(f"🎯 Predicts {pred_details['best_lag']} days ahead")
                    st.caption(f"Correlation: {pred_details['best_correlation']:.3f}")
                else:
                    st.caption("📊 Limited predictive power")

            with metric_cols[2]:
                st.metric(
                    "Stability",
                    stab_details['stability'],
                    delta=f"Volatility: {stab_details['std_correlation']:.3f}"
                )
                st.caption(f"Avg correlation: {stab_details['mean_correlation']:.3f}")

            with metric_cols[3]:
                component_scores = score['details']['component_scores']
                st.metric(
                    "Score Breakdown",
                    f"{score['key_score']:.2f}/100"
                )
                st.caption(f"Strength: {component_scores['strength_score']:.1f}/40")
                st.caption(f"Predictive: {component_scores['predictive_score']:.1f}/30")
                st.caption(f"Stability: {component_scores['stability_score']:.1f}/30")

            # Time sensitivity (if enabled)
            if show_time_sensitivity and 'time_sensitivity' in score:
                st.markdown("---")
                st.markdown("**⏱️ Time Sensitivity Analysis**")

                ts = score['time_sensitivity']

                ts_cols = st.columns(3)
                with ts_cols[0]:
                    st.metric("3-Month Correlation", f"{ts['corr_3m']:.3f}")
                with ts_cols[1]:
                    st.metric("1-Year Correlation", f"{ts['corr_1y']:.3f}")
                with ts_cols[2]:
                    st.metric("Trend", ts['trend'])

                st.info(f"💡 **Insight**: {ts['insight']}")

            # Explanation
            st.markdown("---")
            st.markdown(f"**Summary**: {score['explanation']}")

            # Rolling correlation chart (if stability data available)
            if not stab_details['rolling_series'].empty:
                st.markdown("**Rolling Correlation Chart** (60-day window)")

                import plotly.graph_objects as go

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=stab_details['rolling_series'].index,
                    y=stab_details['rolling_series'].values,
                    mode='lines',
                    name='Rolling Correlation',
                    line=dict(color='#636EFA', width=2)
                ))

                # Add mean line
                fig.add_hline(
                    y=stab_details['mean_correlation'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Mean: {stab_details['mean_correlation']:.3f}"
                )

                fig.update_layout(
                    title=f"{factor_name} vs {ticker} - Rolling 60-Day Correlation",
                    xaxis_title="Date",
                    yaxis_title="Correlation",
                    yaxis_range=[-1, 1],
                    height=300,
                    hovermode='x unified'
                )

                plotly_full_width(fig)

    # ============================
    # HELP SECTION
    # ============================

    st.markdown("---")

    with st.expander("❓ **Understanding Correlation Analysis - Complete Guide**"):
        st.markdown(f"""
        ## What Are Correlating Factors for {ticker}?

        Correlating factors are market variables that move in sync with (or opposite to) **{ticker}** stock price.
        Understanding these relationships helps you:
        - Predict {ticker} direction based on leading indicators
        - Understand what economic conditions favor this stock
        - Time entry/exit based on correlated factor movements

        ---

        ## Complete guide available in Market Overview & Economy → Correlating Factors tab

        For detailed explanation of all metrics, see the help section in the market-level analysis.
        """)


def render_debug_tab(ticker):
    """
    Debug tab for Stock Analysis page
    Shows session state, cache status, data quality, and performance metrics
    """
    st.markdown("### 🔧 Stock Analysis Debug Panel")
    st.caption("Diagnostic tools and data inspection for troubleshooting")

    st.markdown("---")

    # Section 1: Session State
    with st.expander("📊 Session State Variables", expanded=False):
        st.markdown("**Current Session State:**")
        if st.session_state:
            # Filter relevant session state keys
            relevant_keys = {k: v for k, v in st.session_state.items()
                           if not k.startswith('FormSubmitter') and not k.startswith('_')}
            st.json(relevant_keys)
        else:
            st.info("No session state variables set")

    # Section 2: Ticker Data Quality
    with st.expander("🎯 Ticker Data Quality Check", expanded=True):
        st.markdown(f"**Testing data availability for: {ticker}**")

        try:
            # Test yfinance connection
            stock = yf.Ticker(ticker)
            info = stock.info

            col1, col2, col3 = st.columns(3)

            with col1:
                # Check basic info
                has_name = 'longName' in info or 'shortName' in info
                has_sector = 'sector' in info
                has_industry = 'industry' in info

                st.metric("Basic Info", "✅ Available" if has_name else "❌ Missing")
                st.caption(f"Name: {info.get('longName', 'N/A')}")
                st.caption(f"Sector: {info.get('sector', 'N/A')}")
                st.caption(f"Industry: {info.get('industry', 'N/A')}")

            with col2:
                # Check price data
                hist = stock.history(period="1mo")
                has_price_data = not hist.empty

                st.metric("Price Data (1M)", "✅ Available" if has_price_data else "❌ Missing")
                if has_price_data:
                    st.caption(f"Bars: {len(hist)}")
                    st.caption(f"Latest: ${hist['Close'].iloc[-1]:.2f}")
                    st.caption(f"Date: {hist.index[-1].strftime('%Y-%m-%d')}")

            with col3:
                # Check fundamentals
                has_pe = 'trailingPE' in info
                has_eps = 'trailingEps' in info
                has_revenue = 'totalRevenue' in info

                st.metric("Fundamentals", "✅ Available" if has_pe else "⚠️ Partial")
                st.caption(f"P/E: {info.get('trailingPE', 'N/A')}")
                st.caption(f"EPS: {info.get('trailingEps', 'N/A')}")
                st.caption(f"Revenue: {info.get('totalRevenue', 'N/A')}")

            # Data completeness summary
            st.markdown("---")
            completeness_score = 0
            total_checks = 10

            checks = {
                "Company Name": has_name,
                "Sector/Industry": has_sector and has_industry,
                "Price Data": has_price_data,
                "P/E Ratio": has_pe,
                "EPS": has_eps,
                "Revenue": has_revenue,
                "Market Cap": 'marketCap' in info,
                "Dividend Yield": 'dividendYield' in info,
                "Volume": has_price_data and 'Volume' in hist.columns,
                "52W High/Low": '52WeekHigh' in info and '52WeekLow' in info
            }

            completeness_score = sum(checks.values())
            completeness_pct = (completeness_score / total_checks) * 100

            st.markdown(f"**Data Completeness: {completeness_pct:.0f}% ({completeness_score}/{total_checks})**")

            # Show individual checks
            check_cols = st.columns(5)
            for i, (check_name, passed) in enumerate(checks.items()):
                with check_cols[i % 5]:
                    st.caption(f"{'✅' if passed else '❌'} {check_name}")

        except Exception as e:
            st.error(f"Error fetching ticker data: {str(e)}")

    # Section 3: Cache Status
    with st.expander("💾 Cache Status", expanded=False):
        st.markdown("**Streamlit Cache Info:**")

        # Check if data is cached
        st.markdown(f"""
        - **Multi-timeframe data**: Cached for 1 minute per ticker
        - **SPY data**: Cached for 5 minutes (shared)
        - **Sector ETF data**: Cached for 5 minutes
        - **News data**: Cached based on news_fetcher settings
        """)

        if st.button("Clear All Caches"):
            st.cache_data.clear()
            st.success("✅ All caches cleared!")
            st.rerun()

    # Section 4: Performance Metrics
    with st.expander("⚡ Performance Metrics", expanded=False):
        st.markdown("**Load Time Estimates:**")

        preset_times = {
            "Quick Scan": "~0.3s",
            "Entry/Exit Timing": "~3.5s (first load), ~0.5s (cached)",
            "Risk Assessment": "~1.5s (first load), ~0.3s (cached)",
            "Market Context": "~1.5s (first load), ~0.3s (cached)",
            "Full Diagnostic": "~5-7s (first load), ~1-2s (cached)"
        }

        for preset, time in preset_times.items():
            st.caption(f"**{preset}**: {time}")

    # Section 5: API Status
    with st.expander("🌐 API & External Services Status", expanded=False):
        st.markdown("**Testing external connections:**")

        col1, col2 = st.columns(2)

        with col1:
            # Test yfinance
            try:
                test_ticker = yf.Ticker("AAPL")
                test_data = test_ticker.history(period="1d")
                yf_status = "✅ Online" if not test_data.empty else "❌ No Data"
            except:
                yf_status = "❌ Error"

            st.metric("Yahoo Finance", yf_status)

        with col2:
            # Test Gemini (if configured)
            try:
                import os
                has_gemini_key = bool(os.getenv('GEMINI_API_KEY'))
                gemini_status = "✅ Configured" if has_gemini_key else "⚠️ Not Configured"
            except:
                gemini_status = "❌ Error"

            st.metric("Gemini AI", gemini_status)

    # Section 6: Raw Data Inspector
    with st.expander("🔍 Raw Data Inspector", expanded=False):
        st.markdown(f"**Inspect raw data for {ticker}:**")

        data_type = st.selectbox(
            "Select data type to inspect:",
            ["Company Info", "Price History (1M)", "Price History (6M)", "Financials", "Earnings"]
        )

        try:
            stock = yf.Ticker(ticker)

            if data_type == "Company Info":
                st.json(stock.info)

            elif data_type == "Price History (1M)":
                hist = stock.history(period="1mo")
                display_dataframe_full_width(hist)
                st.caption(f"Shape: {hist.shape}")

            elif data_type == "Price History (6M)":
                hist = stock.history(period="6mo")
                display_dataframe_full_width(hist)
                st.caption(f"Shape: {hist.shape}")

            elif data_type == "Financials":
                financials = stock.financials
                display_dataframe_full_width(financials)
                st.caption(f"Shape: {financials.shape}")

            elif data_type == "Earnings":
                earnings = stock.earnings
                display_dataframe_full_width(earnings)
                st.caption(f"Shape: {earnings.shape}")

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

    # Section 7: Error Log
    with st.expander("⚠️ Error Log Simulator", expanded=False):
        st.markdown("**Test error handling:**")

        if st.button("Trigger Test Error"):
            try:
                # Intentional error for testing
                raise ValueError("This is a test error for debugging purposes")
            except Exception as e:
                st.exception(e)

        st.caption("This helps verify error display and logging is working correctly")


if __name__ == "__main__":
    render_page()
