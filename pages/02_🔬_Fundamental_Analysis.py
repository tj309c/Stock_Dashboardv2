import streamlit as st
import pandas as pd
from app_logic import initialize_data_and_context
from valuation_models import calculate_ddm, calculate_dcf
from ticker_utils import setup_sidebar_ticker_input
import datetime

def render_page():
    """Consolidated Fundamental Analysis Dashboard"""
    st.title("🔬 Fundamental Analysis")

    # Setup ticker input in sidebar
    ticker = setup_sidebar_ticker_input("fundamental_analysis")

    # Create tabs for the four fundamental sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Key Metrics",
        "💰 Valuation Models",
        "📄 Financial Statements",
        "⭐ Analyst Ratings"
    ])

    with tab1:
        render_key_metrics_tab(ticker)

    with tab2:
        render_valuation_models_tab(ticker)

    with tab3:
        render_financial_statements_tab(ticker)

    with tab4:
        render_analyst_ratings_tab(ticker)


def render_key_metrics_tab(ticker):
    """Key fundamental metrics"""
    st.subheader(f"Key Metrics for {ticker}")

    context = initialize_data_and_context(ticker)
    info = context.info if context and context.info else {}

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Profitability")
        st.metric("Profit Margin", f"{info.get('profitMargins', 0) * 100:.2f}%")
        st.metric("Operating Margin", f"{info.get('operatingMargins', 0) * 100:.2f}%")
        st.metric("ROE", f"{info.get('returnOnEquity', 0) * 100:.2f}%")
        st.metric("ROA", f"{info.get('returnOnAssets', 0) * 100:.2f}%")

    with col2:
        st.markdown("#### Growth")
        st.metric("Revenue Growth", f"{info.get('revenueGrowth', 0) * 100:.2f}%")
        st.metric("Earnings Growth", f"{info.get('earningsGrowth', 0) * 100:.2f}%")
        st.metric("Revenue (TTM)", f"${info.get('totalRevenue', 0):,.0f}")
        st.metric("Net Income", f"${info.get('netIncomeToCommon', 0):,.0f}")

    with col3:
        st.markdown("#### Valuation")
        st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
        st.metric("Forward P/E", f"{info.get('forwardPE', 'N/A')}")
        st.metric("P/B Ratio", f"{info.get('priceToBook', 'N/A')}")
        st.metric("P/S Ratio", f"{info.get('priceToSalesTrailing12Months', 'N/A')}")


def render_valuation_models_tab(ticker):
    """Valuation models and calculations with adjustable assumptions"""
    st.subheader(f"Valuation Models for {ticker}")

    ctx = initialize_data_and_context(ticker)

    if not ctx:
        st.error("Could not load data")
        return

    # Get current market data for defaults
    info = ctx.info if ctx and ctx.info else {}
    current_revenue = info.get('totalRevenue', 1_000_000_000)
    shares_outstanding = info.get('sharesOutstanding', 1_000_000_000)
    cash = info.get('totalCash', 0)
    total_debt = info.get('totalDebt', 0)

    # Create tabs for DCF and DDM
    dcf_tab, ddm_tab = st.tabs(["📊 DCF Model", "💵 DDM Model"])

    with dcf_tab:
        st.markdown("### Professional DCF Valuation Model")
        st.markdown("**Hedge Fund-Grade Analysis with Scenario Planning, Sensitivity Analysis, and Probabilistic Modeling**")

        # Comprehensive Tutorial Section
        with st.expander("📚 DCF Tutorial & Methodology Guide", expanded=False):
            st.markdown("""
            ## 🎯 How to Use This DCF Model

            This professional-grade DCF (Discounted Cash Flow) model values a company by projecting its future free cash flows
            and discounting them back to present value. Follow these steps for accurate valuation:

            ### Step 1: Choose Your Approach
            - **🎯 AI-Powered Smart Recommendations**: Let the algorithm analyze historical performance, industry benchmarks,
              and company size to suggest optimal inputs (recommended for beginners)
            - **Manual Input**: Customize every assumption based on your own research and analysis

            ### Step 2: Review Key Assumptions

            #### **Revenue Growth Rates** (Year 1-5)
            - **What It Means**: How fast you expect the company's sales to grow annually
            - **Built-In Assumptions**:
              - Smart recommendations use a "fade" approach: higher growth in early years gradually declining toward industry average
              - Growth is adjusted based on company size (small caps can grow faster than mega caps)
            - **How to Override**: If the company is entering new markets, launching major products, or facing headwinds,
              adjust the growth rates accordingly
            - **Red Flags**: Growth rates above 30% are rarely sustainable; negative growth suggests declining business

            #### **EBIT Margin** (Operating Profit Margin)
            - **What It Means**: What percentage of revenue becomes operating profit (before interest and taxes)
            - **Built-In Assumptions**:
              - Uses company's actual operating margin if available
              - Falls back to industry average for the sector
              - Advanced mode allows margin fade to a "normalized" terminal margin
            - **How to Override**: Adjust upward if the company is implementing cost-cutting or gaining pricing power;
              adjust downward if facing margin compression
            - **Typical Ranges**:
              - Tech: 20-30%
              - Retail: 5-10%
              - Finance: 25-35%

            #### **WACC** (Weighted Average Cost of Capital)
            - **What It Means**: The required return investors demand to invest in this company (your discount rate)
            - **Built-In Assumptions**:
              - Calculated using CAPM: Cost of Equity = Risk-Free Rate + (Beta × Market Risk Premium)
              - Risk-free rate defaults to 4.5% (current 10-year Treasury)
              - Market risk premium defaults to 7% (historical equity premium)
              - Cost of debt estimated from interest expense or credit rating proxy
            - **How to Override**: Increase WACC for riskier companies or uncertain industries;
              decrease for stable, predictable businesses
            - **Typical Ranges**:
              - Stable companies: 6-8%
              - Average companies: 8-12%
              - High-risk companies: 12-20%

            #### **ROIC** (Return on Invested Capital)
            - **What It Means**: How efficiently the company generates returns on its invested capital
            - **Built-In Assumptions**:
              - Calculated as NOPAT ÷ Invested Capital from financial statements
              - Used to intelligently estimate CapEx: companies with high ROIC need less capital to grow
            - **Formula**: CapEx = (Revenue Growth × Revenue) ÷ ROIC
            - **Typical Ranges**:
              - Excellent (>20%): Asset-light businesses with moats
              - Good (12-20%): Average profitable companies
              - Poor (<12%): Capital-intensive or low-margin businesses

            #### **Terminal Growth Rate**
            - **What It Means**: The perpetual growth rate assumed after the 5-year projection period
            - **Built-In Assumptions**:
              - High-growth sectors (Tech, Healthcare): 3%
              - Moderate sectors (Industrials, Consumer): 2.5%
              - Mature sectors (Utilities, Energy): 2%
              - Never exceeds WACC × 0.9 (to avoid mathematical impossibility)
            - **How to Override**: Lower for declining industries; can be slightly higher for secular growth trends
            - **Warning**: Small changes in terminal growth dramatically impact valuation (sensitivity analysis helps!)

            ### Step 3: Run Your Analysis

            #### **Base Case Calculation**
            - Calculates intrinsic value using your assumptions
            - Shows detailed breakdown of FCF projections and terminal value
            - Compares to current market price

            #### **Scenario Analysis** (Bear/Base/Bull)
            - **Bear Case**: 50% of growth rates, 80% of margins, 120% WACC (stress test)
            - **Bull Case**: 150% of growth rates, 120% of margins, 80% WACC (optimistic)
            - **Probability-Weighted**: 30% Bear + 40% Base + 30% Bull = blended fair value

            #### **Sensitivity Analysis**
            - Shows how valuation changes with different WACC and terminal growth combinations
            - **How to Use**:
              - Find the cell with your base case assumptions
              - See how much valuation changes if you're wrong about WACC or terminal growth
              - Helps understand which assumptions matter most

            #### **Monte Carlo Simulation** (10,000 scenarios)
            - Randomly varies all input assumptions within reasonable ranges
            - Generates a distribution of possible valuations
            - **How to Interpret**:
              - Median (P50): Most likely valuation
              - P10-P90 Range: 80% confidence interval
              - If current price is below P25, potential upside opportunity
              - If current price is above P75, potential downside risk

            ### Step 4: Interpret Results

            #### **Understanding the Output**
            - **Intrinsic Value > Market Price**: Potentially undervalued (but verify your assumptions!)
            - **Intrinsic Value < Market Price**: Potentially overvalued (or market expects better growth)
            - **Intrinsic Value ≈ Market Price**: Fairly valued

            #### **Red Flags to Watch**
            - Terminal value > 80% of enterprise value (too dependent on perpetuity assumptions)
            - WACC < Terminal Growth (mathematically invalid - will show error)
            - Extremely high sensitivity to terminal growth (unstable valuation)
            - Wide divergence between scenario cases (high uncertainty)

            ### Built-In Safeguards

            1. **Growth Fade Logic**: Prevents assuming unrealistic perpetual high growth
            2. **Margin Normalization**: Fades margins to sustainable levels
            3. **ROIC-Based CapEx**: Ties capital needs to actual returns (more realistic than fixed %)
            4. **Dual Terminal Value**: Averages Gordon Growth and Exit Multiple methods
            5. **Smart Bounds**: Caps extreme values (e.g., WACC between 1-50%, Beta between 0.5-2.5)

            ### Limitations & Disclaimers

            #### **What This Model CAN'T Predict:**
            - Major M&A activity
            - Regulatory changes or lawsuits
            - Technological disruption
            - Management quality changes
            - Macroeconomic shocks
            - Black swan events

            #### **Best Practices:**
            1. **Cross-check** with management guidance from earnings calls
            2. **Compare** to analyst consensus estimates (are you more optimistic or conservative?)
            3. **Run multiple scenarios** to understand valuation range
            4. **Update quarterly** as new data becomes available
            5. **Document your thesis** - write down WHY you chose each assumption
            6. **Sanity check** against comparable company valuations

            ### Advanced Features Explained

            #### **Stock-Based Compensation (SBC)**
            - Tech companies often grant stock to employees, diluting shareholders
            - Should be treated as a real expense (not just accounting)
            - Typical ranges: 1-3% of revenue for most companies, 3-8% for high-growth tech

            #### **Margin Fade**
            - Assumes operating margins gradually normalize toward industry average
            - Prevents assuming unsustainable premium margins forever
            - Useful for fast-growing companies with temporarily high margins

            #### **Reverse DCF**
            - Calculates what terminal growth rate the market is implying at current price
            - **How to Use**: If implied growth seems too high/low, current price may be wrong

            ### Need More Help?

            - View the **Smart Recommendations Rationale** for detailed explanations of AI-generated inputs
            - Check the **DCF_SMART_RECOMMENDATIONS_GUIDE.md** file for 400+ lines of detailed methodology
            - Compare your inputs to the **Industry Benchmarks** table below
            - Run **Sensitivity Analysis** to see which assumptions matter most

            ---
            *This model is designed for educational and analytical purposes. Always conduct your own due diligence
            and consult a financial advisor before making investment decisions.*
            """)

        # Smart Recommendations Section
        use_smart_defaults = st.checkbox("🎯 Use AI-Powered Smart Recommendations (Analyzes company fundamentals + industry benchmarks)", value=False, key="use_smart")

        if use_smart_defaults:
            from dcf_helpers import get_smart_dcf_recommendations

            # Generate smart recommendations
            recommendations = get_smart_dcf_recommendations(
                info=info,
                income_data=ctx.income_data if ctx else pd.DataFrame(),
                balance_sheet=ctx.balance_sheet_data if ctx else pd.DataFrame(),
                cash_flow=ctx.cash_flow_data if ctx else pd.DataFrame(),
                market_price=ctx.market_price if ctx else 100
            )

            # Display recommendation summary
            with st.expander("📊 View Smart Recommendations Rationale", expanded=True):
                st.markdown(f"**Sector**: {recommendations['sector']}")
                st.markdown(f"**Historical Revenue CAGR (5Y)**: {recommendations['historical_revenue_cagr']:.1%}")
                st.markdown(f"**Recent Revenue Growth**: {recommendations['recent_revenue_growth']:.1%}")

                st.markdown("---")
                st.markdown("**📈 Confidence Analysis:**")
                for key, note in recommendations['confidence_notes'].items():
                    st.markdown(f"- {note}")

                st.markdown("---")
                st.markdown("**🏭 Industry Benchmarks Used:**")
                industry = recommendations['industry_benchmarks']
                st.markdown(f"- Growth Rate: {industry['growth_rate']:.1%}")
                st.markdown(f"- EBIT Margin: {industry['ebit_margin']:.1%}")
                st.markdown(f"- CapEx: {industry['capex_pct']:.1%} of revenue")
                st.markdown(f"- ROIC: {industry['roic']:.1%}")

        # Advanced mode toggle
        advanced_mode = st.checkbox("Enable Advanced Features (WACC Calculator, ROIC, Monte Carlo)", value=False)

        # Split into columns for better organization
        col1, col2 = st.columns(2)

        # Get smart defaults if enabled
        if use_smart_defaults:
            smart_growth = [r * 100 for r in recommendations['growth_rates']]
            smart_ebit_margin = recommendations['ebit_margin'] * 100
            smart_terminal_margin = recommendations['terminal_margin'] * 100
            smart_sbc = recommendations['sbc_pct'] * 100
        else:
            smart_growth = [10.0, 9.0, 8.0, 7.0, 6.0]
            smart_ebit_margin = info.get('operatingMargins', 0.2) * 100
            smart_terminal_margin = smart_ebit_margin
            smart_sbc = 2.0

        with col1:
            st.markdown("#### Growth & Margins")

            # Revenue growth rates (5-year projection)
            st.markdown("**Revenue Growth Rates (5 Years)**")
            if use_smart_defaults:
                st.info(f"💡 Smart forecast: Fading from {smart_growth[0]:.1f}% to {smart_growth[-1]:.1f}% based on historical {recommendations['historical_revenue_cagr']*100:.1f}% CAGR")

            growth_y1 = st.number_input("Year 1 Growth Rate (%)", value=smart_growth[0], min_value=-50.0, max_value=100.0, step=1.0, key="g1") / 100
            growth_y2 = st.number_input("Year 2 Growth Rate (%)", value=smart_growth[1], min_value=-50.0, max_value=100.0, step=1.0, key="g2") / 100
            growth_y3 = st.number_input("Year 3 Growth Rate (%)", value=smart_growth[2], min_value=-50.0, max_value=100.0, step=1.0, key="g3") / 100
            growth_y4 = st.number_input("Year 4 Growth Rate (%)", value=smart_growth[3], min_value=-50.0, max_value=100.0, step=1.0, key="g4") / 100
            growth_y5 = st.number_input("Year 5 Growth Rate (%)", value=smart_growth[4], min_value=-50.0, max_value=100.0, step=1.0, key="g5") / 100

            if use_smart_defaults:
                st.info(f"💡 Current EBIT margin: {info.get('operatingMargins', 0)*100:.1f}%, Industry avg: {recommendations['industry_benchmarks']['ebit_margin']*100:.1f}%")

            ebit_margin = st.number_input("EBIT Margin (%)", value=smart_ebit_margin, min_value=0.0, max_value=100.0, step=0.5) / 100
            tax_rate = st.number_input("Tax Rate (%)", value=21.0, min_value=0.0, max_value=50.0, step=0.5) / 100

            if advanced_mode:
                terminal_ebit_margin = st.number_input("Terminal EBIT Margin (%)", value=smart_terminal_margin, min_value=0.0, max_value=100.0, step=0.5) / 100
                fade_years = st.number_input("Margin Fade Period (Years)", value=5, min_value=1, max_value=10, step=1)
                sbc_pct = st.number_input("Stock-Based Comp (% of Revenue)", value=smart_sbc, min_value=0.0, max_value=20.0, step=0.5) / 100
            else:
                terminal_ebit_margin = None
                fade_years = 5
                sbc_pct = 0.0

        # Get smart defaults for right column
        if use_smart_defaults:
            smart_risk_free = recommendations['risk_free_rate'] * 100
            smart_beta = recommendations['beta']
            smart_mrp = recommendations['market_risk_premium'] * 100
            smart_cod = recommendations['cost_of_debt'] * 100
            smart_roic = recommendations['roic'] * 100
            smart_capex = recommendations['capex_pct'] * 100
            smart_nwc = recommendations['nwc_pct'] * 100
            smart_depreciation = recommendations['depreciation_pct'] * 100
            smart_terminal_growth = recommendations['terminal_growth'] * 100
        else:
            smart_risk_free = 4.5
            smart_beta = info.get('beta', 1.0)
            smart_mrp = 7.0
            smart_cod = 5.0
            smart_roic = 15.0
            smart_capex = 5.0
            smart_nwc = 2.0
            smart_depreciation = 3.0
            smart_terminal_growth = 2.5

        with col2:
            st.markdown("#### Capital Structure & Discount Rate")

            if advanced_mode:
                st.markdown("**WACC Calculator**")
                if use_smart_defaults:
                    st.info(f"💡 Estimated cost of debt: {smart_cod:.1f}% based on company financials")

                risk_free_rate = st.number_input("Risk-Free Rate (%)", value=smart_risk_free, min_value=0.0, max_value=10.0, step=0.1) / 100
                beta = st.number_input("Beta", value=smart_beta, min_value=0.0, max_value=3.0, step=0.1)
                market_risk_premium = st.number_input("Market Risk Premium (%)", value=smart_mrp, min_value=0.0, max_value=15.0, step=0.5) / 100
                cost_of_debt = st.number_input("Cost of Debt (%)", value=smart_cod, min_value=0.0, max_value=20.0, step=0.5) / 100

                # Calculate WACC
                from valuation_models import calculate_wacc, WACCInputs
                market_cap = ctx.market_price * shares_outstanding if ctx.market_price and shares_outstanding else 1e9
                wacc_inputs = WACCInputs(
                    risk_free_rate=risk_free_rate,
                    beta=beta,
                    market_risk_premium=market_risk_premium,
                    cost_of_debt=cost_of_debt,
                    tax_rate=tax_rate,
                    market_cap=market_cap,
                    total_debt=total_debt
                )
                wacc = calculate_wacc(wacc_inputs)
                st.info(f"Calculated WACC: {wacc:.2%}")

                if use_smart_defaults:
                    st.info(f"💡 Estimated ROIC: {smart_roic:.1f}% based on historical returns")

                roic = st.number_input("ROIC - Return on Invested Capital (%)", value=smart_roic, min_value=0.0, max_value=100.0, step=1.0) / 100
            else:
                wacc = st.number_input("WACC - Discount Rate (%)", value=10.0, min_value=1.0, max_value=30.0, step=0.5) / 100
                roic = None

            if use_smart_defaults:
                st.info(f"💡 Industry-typical CapEx: {recommendations['industry_benchmarks']['capex_pct']*100:.1f}% of revenue")

            depreciation_pct = st.number_input("Depreciation (% of Revenue)", value=smart_depreciation, min_value=0.0, max_value=20.0, step=0.5) / 100
            capex_pct = st.number_input("CapEx (% of Revenue)", value=smart_capex, min_value=0.0, max_value=30.0, step=0.5) / 100
            nwc_pct = st.number_input("NWC Change (% of Revenue)", value=smart_nwc, min_value=-10.0, max_value=20.0, step=0.5) / 100

            st.markdown("---")
            if use_smart_defaults:
                st.info(f"💡 Terminal growth: {smart_terminal_growth:.1f}% (GDP growth + inflation for {recommendations['sector']})")

            terminal_growth = st.number_input("Terminal Growth Rate (%)", value=smart_terminal_growth, min_value=0.0, max_value=10.0, step=0.25) / 100

        # Calculate button
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            run_base_case = st.button("Calculate Base Case", type="primary", use_container_width=True)
        with calc_col2:
            run_scenario = st.button("Run Scenario Analysis", use_container_width=True)
        with calc_col3:
            run_monte_carlo = st.button("Monte Carlo (10k sims)", use_container_width=True) if advanced_mode else False

        if run_base_case or run_scenario or run_monte_carlo:
            from valuation_models import (
                calculate_dcf, DCFInputs, calculate_scenario_analysis,
                calculate_sensitivity_table, calculate_reverse_dcf, calculate_monte_carlo_dcf,
                create_dcf_waterfall_chart, create_football_field_chart,
                create_sensitivity_heatmap, create_monte_carlo_distribution, create_fcf_projection_chart
            )

            dcf_inputs = DCFInputs(
                revenue_growth_rates=[growth_y1, growth_y2, growth_y3, growth_y4, growth_y5],
                ebit_margin=ebit_margin,
                tax_rate=tax_rate,
                depreciation_as_pct_revenue=depreciation_pct,
                capex_as_pct_revenue=capex_pct,
                nwc_as_pct_revenue=nwc_pct,
                terminal_growth_rate=terminal_growth,
                wacc=wacc,
                cash=cash,
                total_debt=total_debt,
                shares_outstanding=shares_outstanding,
                current_revenue=current_revenue,
                roic=roic,
                fade_years=fade_years,
                terminal_ebit_margin=terminal_ebit_margin,
                sbc_as_pct_revenue=sbc_pct
            )

            market_price = ctx.market_price

            # Base Case Calculation
            intrinsic_value, intermediates = calculate_dcf(dcf_inputs)

            # Display results
            st.markdown("---")
            st.markdown("### Valuation Results")

            result_col1, result_col2, result_col3, result_col4 = st.columns(4)

            with result_col1:
                st.metric("DCF Value per Share", f"${intrinsic_value:.2f}")

            with result_col2:
                st.metric("Current Market Price", f"${market_price:.2f}")

            with result_col3:
                upside = ((intrinsic_value - market_price) / market_price * 100) if market_price > 0 else 0
                st.metric("Upside/Downside", f"{upside:+.1f}%",
                         delta_color="normal" if upside > 0 else "inverse")

            with result_col4:
                terminal_val_pct = intermediates.get('terminal_value_pct', 0)
                st.metric("Terminal Value %", f"{terminal_val_pct:.1f}%")

            # Reverse DCF
            if advanced_mode:
                implied_tg = calculate_reverse_dcf(market_price, dcf_inputs, solve_for='terminal_growth')
                st.info(f"**Reverse DCF**: Market price implies a terminal growth rate of **{implied_tg:.2%}** (vs your assumption of {terminal_growth:.2%})")

            # Scenario Analysis
            if run_scenario:
                st.markdown("### Scenario Analysis")
                scenarios = calculate_scenario_analysis(dcf_inputs)

                scenario_col1, scenario_col2, scenario_col3, scenario_col4 = st.columns(4)

                with scenario_col1:
                    bear_val = scenarios['bear'][0]
                    st.metric("Bear Case", f"${bear_val:.2f}", f"{((bear_val/market_price - 1)*100):+.1f}%")

                with scenario_col2:
                    base_val = scenarios['base'][0]
                    st.metric("Base Case", f"${base_val:.2f}", f"{((base_val/market_price - 1)*100):+.1f}%")

                with scenario_col3:
                    bull_val = scenarios['bull'][0]
                    st.metric("Bull Case", f"${bull_val:.2f}", f"{((bull_val/market_price - 1)*100):+.1f}%")

                with scenario_col4:
                    weighted_val = scenarios['weighted'][0]
                    st.metric("Probability-Weighted", f"${weighted_val:.2f}", f"{((weighted_val/market_price - 1)*100):+.1f}%")

                # Football Field Chart
                st.plotly_chart(
                    create_football_field_chart(intrinsic_value, market_price, scenarios),
                    use_container_width=True
                )

            # Monte Carlo Simulation
            if run_monte_carlo and advanced_mode:
                st.markdown("### Monte Carlo Simulation")
                with st.spinner("Running 10,000 simulations..."):
                    mc_results = calculate_monte_carlo_dcf(dcf_inputs, num_simulations=10000)

                mc_col1, mc_col2, mc_col3, mc_col4 = st.columns(4)
                with mc_col1:
                    st.metric("P10 (Pessimistic)", f"${mc_results['p10']:.2f}")
                with mc_col2:
                    st.metric("Median", f"${mc_results['median']:.2f}")
                with mc_col3:
                    st.metric("P90 (Optimistic)", f"${mc_results['p90']:.2f}")
                with mc_col4:
                    st.metric("Std Dev", f"${mc_results['std']:.2f}")

                st.plotly_chart(
                    create_monte_carlo_distribution(mc_results, market_price),
                    use_container_width=True
                )

            # Sensitivity Analysis
            st.markdown("### Sensitivity Analysis")
            value_matrix, wacc_vals, tg_vals = calculate_sensitivity_table(dcf_inputs, steps=7)
            st.plotly_chart(
                create_sensitivity_heatmap(value_matrix, wacc_vals, tg_vals, market_price),
                use_container_width=True
            )

            # Visualizations
            viz_tab1, viz_tab2 = st.tabs(["Cash Flow Projection", "Waterfall Chart"])

            with viz_tab1:
                st.plotly_chart(create_fcf_projection_chart(intermediates), use_container_width=True)

            with viz_tab2:
                st.plotly_chart(create_dcf_waterfall_chart(intermediates, market_price), use_container_width=True)

            # Detailed breakdown
            with st.expander("View Detailed Calculations"):
                st.markdown("**Enterprise Value Breakdown:**")
                st.write(f"- PV of Explicit Period FCFs: ${intermediates.get('pv_of_explicit_period', 0):,.0f}")
                st.write(f"- Terminal Value (Gordon Growth): ${intermediates.get('terminal_value_gg', 0):,.0f}")
                st.write(f"- Terminal Value (Exit Multiple): ${intermediates.get('terminal_value_multiple', 0):,.0f}")
                st.write(f"- Terminal Value (Average): ${intermediates.get('terminal_value', 0):,.0f}")
                st.write(f"- Discounted Terminal Value: ${intermediates.get('discounted_tv', 0):,.0f}")
                st.write(f"- Enterprise Value: ${intermediates.get('enterprise_value', 0):,.0f}")
                st.write(f"- Plus: Cash: ${cash:,.0f}")
                st.write(f"- Minus: Total Debt: ${total_debt:,.0f}")
                st.write(f"- Equity Value: ${intermediates.get('equity_value', 0):,.0f}")
                st.write(f"- Shares Outstanding: {shares_outstanding:,.0f}")

                # Show yearly projections
                st.markdown("**5-Year Financial Projections:**")
                proj_df = pd.DataFrame({
                    'Year': list(range(1, 6)),
                    'Revenue': intermediates.get('revenue_forecast', []),
                    'EBIT Margin': [f"{m:.2%}" for m in intermediates.get('ebit_margins', [])],
                    'NOPAT': intermediates.get('nopat_forecast', []),
                    'CapEx': intermediates.get('capex_forecast', []),
                    'FCF': intermediates.get('fcf_forecast', []),
                    'Discounted FCF': intermediates.get('discounted_fcf', [])
                })
                st.dataframe(proj_df, use_container_width=True)

    with ddm_tab:
        st.markdown("### Dividend Discount Model (DDM) Valuation")

        if ctx.ddm_value > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.metric("DDM Value per Share", f"${ctx.ddm_value:.2f}")
                st.metric("Current Market Price", f"${ctx.market_price:.2f}")

            with col2:
                st.metric("DDM Upside/Downside", f"{ctx.ddm_upside:+.1f}%",
                         delta_color="normal" if ctx.ddm_upside > 0 else "inverse")

            st.info("The DDM model uses current dividend data and assumes constant growth. This model works best for stable, dividend-paying companies.")
        else:
            st.warning("DDM valuation not applicable - this stock does not pay dividends or dividend data is unavailable.")


def render_financial_statements_tab(ticker):
    """Raw financial statements"""
    st.subheader(f"Financial Statements for {ticker}")

    ctx = initialize_data_and_context(ticker)

    view_type = st.radio("Select View", ["Annual", "Quarterly"], horizontal=True)

    if view_type == "Annual":
        st.markdown("### Income Statement")
        if not ctx.income_data.empty:
            st.dataframe(ctx.income_data, use_container_width=True)
        else:
            st.info("No annual income statement data available")

        st.markdown("### Balance Sheet")
        if not ctx.balance_sheet_data.empty:
            st.dataframe(ctx.balance_sheet_data, use_container_width=True)
        else:
            st.info("No annual balance sheet data available")

        st.markdown("### Cash Flow Statement")
        if not ctx.cash_flow_data.empty:
            st.dataframe(ctx.cash_flow_data, use_container_width=True)
        else:
            st.info("No annual cash flow data available")
    else:
        st.markdown("### Quarterly Income Statement")
        if not ctx.quarterly_income_data.empty:
            st.dataframe(ctx.quarterly_income_data, use_container_width=True)
        else:
            st.info("No quarterly income statement data available")

        st.markdown("### Quarterly Balance Sheet")
        if not ctx.quarterly_balance_sheet.empty:
            st.dataframe(ctx.quarterly_balance_sheet, use_container_width=True)
        else:
            st.info("No quarterly balance sheet data available")

        st.markdown("### Quarterly Cash Flow Statement")
        if not ctx.quarterly_cash_flow.empty:
            st.dataframe(ctx.quarterly_cash_flow, use_container_width=True)
        else:
            st.info("No quarterly cash flow data available")


def render_analyst_ratings_tab(ticker):
    """Analyst ratings and recommendations"""
    st.subheader(f"Analyst Ratings for {ticker}")

    ctx = initialize_data_and_context(ticker, light_load=True)
    info = ctx.info if ctx and ctx.info else {}

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Recommendations")
        target_high = info.get('targetHighPrice', 'N/A')
        target_low = info.get('targetLowPrice', 'N/A')
        target_mean = info.get('targetMeanPrice', 'N/A')
        target_median = info.get('targetMedianPrice', 'N/A')

        st.metric("Target High", f"${target_high}" if target_high != 'N/A' else "N/A")
        st.metric("Target Low", f"${target_low}" if target_low != 'N/A' else "N/A")
        st.metric("Target Mean", f"${target_mean}" if target_mean != 'N/A' else "N/A")
        st.metric("Target Median", f"${target_median}" if target_median != 'N/A' else "N/A")

    with col2:
        st.markdown("#### Consensus")
        recommendation = info.get('recommendationKey', 'N/A')
        num_analysts = info.get('numberOfAnalystOpinions', 'N/A')

        st.info(f"**Recommendation:** {recommendation}")
        st.info(f"**Number of Analysts:** {num_analysts}")


if __name__ == "__main__":
    render_page()
