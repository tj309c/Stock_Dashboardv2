"""
Enhanced Valuation UI Components
Interactive DCF calculator with sliders and Monte Carlo simulation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from enhanced_valuation import get_enhanced_dcf_calculator
from utils import format_currency, format_percentage, format_large_number

logger = logging.getLogger(__name__)


def show_enhanced_valuation_tab(data, components):
    """
    Enhanced valuation tab with interactive DCF calculator and Monte Carlo simulation
    
    Args:
        data: Stock data dictionary
        components: Components dictionary with fetcher, valuation, etc.
    """
    st.subheader("🧮 Interactive Enterprise Value Calculator")
    st.markdown("*Adjust variables to see real-time impact on intrinsic value*")
    
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    financials = data.get("fundamentals", {})
    
    if not info:
        st.warning("⚠️ No stock info available for valuation analysis")
        return
    
    # Get enhanced calculator
    calc = get_enhanced_dcf_calculator()
    
    # Extract base data
    shares_outstanding = info.get("sharesOutstanding", 0)
    current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
    cash = info.get("totalCash", 0)
    debt = info.get("totalDebt", 0)
    
    if shares_outstanding == 0:
        st.error("❌ Cannot calculate valuation: No shares outstanding data")
        return
    
    # Get base cash flow with robust error handling
    try:
        base_cash_flow = get_base_cash_flow(financials, info)
        
        if base_cash_flow == 0:
            st.warning("⚠️ No cash flow data available. Using estimated cash flow based on earnings.")
            # Estimate from net income
            net_income = info.get("netIncomeToCommon", 0)
            if net_income > 0:
                base_cash_flow = net_income * 0.8  # Rough estimate
                st.info(f"ℹ️ Using estimated FCF: {format_currency(base_cash_flow)} (80% of Net Income)")
            else:
                st.error("❌ Cannot estimate cash flow. Please try another ticker with available financial data.")
                st.markdown("**Troubleshooting:**")
                st.markdown("- Try a different ticker symbol")
                st.markdown("- Check if the company has recent financial statements")
                st.markdown("- Some companies may have limited data available via API")
                return
    except Exception as e:
        logger.error(f"Error getting base cash flow: {e}")
        st.error(f"❌ Error fetching cash flow data: {str(e)}")
        return
    
    # Create tabs for different valuation tools
    val_tab1, val_tab2, val_tab3, val_tab4 = st.tabs([
        "🎛️ Interactive DCF",
        "🎲 Monte Carlo Simulation",
        "📊 Sensitivity Analysis",
        "📈 Scenario Comparison"
    ])
    
    with val_tab1:
        show_interactive_dcf(calc, base_cash_flow, current_price, cash, debt, shares_outstanding, info)
    
    with val_tab2:
        show_monte_carlo_simulation(calc, base_cash_flow, current_price, cash, debt, shares_outstanding)
    
    with val_tab3:
        show_sensitivity_analysis(calc, base_cash_flow, current_price, cash, debt, shares_outstanding)
    
    with val_tab4:
        show_scenario_comparison(calc, base_cash_flow, current_price, cash, debt, shares_outstanding)


@st.cache_data(ttl=300, show_spinner=False)
def _calculate_dcf_cached(base_cash_flow, growth_rate, wacc, terminal_growth, projection_years, cash, debt, shares_outstanding):
    """Cached DCF calculation to avoid recomputation"""
    from enhanced_valuation import get_enhanced_dcf_calculator
    calc = get_enhanced_dcf_calculator()
    return calc.calculate_dcf_detailed(
        base_cash_flow=base_cash_flow,
        growth_rate=growth_rate,
        wacc=wacc,
        terminal_growth=terminal_growth,
        projection_years=int(projection_years),
        cash=cash,
        debt=debt,
        shares_outstanding=shares_outstanding
    )


def show_interactive_dcf(calc, base_cash_flow, current_price, cash, debt, shares_outstanding, info):
    """Interactive DCF calculator with real-time sliders"""
    
    st.markdown("### 🎛️ Adjust DCF Variables")
    st.markdown("Move the sliders below to see how different assumptions impact the intrinsic value")
    
    # Create two columns for sliders
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Growth & Discount Assumptions")
        
        growth_rate = st.slider(
            "📈 Growth Rate (Projection Period)",
            min_value=0.0,
            max_value=0.50,
            value=0.10,
            step=0.01,
            format="%.0f%%",
            help="Expected annual growth rate for free cash flow during projection period",
            key="dcf_growth"
        )
        
        wacc = st.slider(
            "💰 WACC (Discount Rate)",
            min_value=0.05,
            max_value=0.20,
            value=calc.default_params['wacc'],
            step=0.005,
            format="%.1f%%",
            help="Weighted Average Cost of Capital - the rate used to discount future cash flows",
            key="dcf_wacc"
        )
        
        terminal_growth = st.slider(
            "♾️ Terminal Growth Rate",
            min_value=0.0,
            max_value=0.05,
            value=0.025,
            step=0.005,
            format="%.1f%%",
            help="Perpetual growth rate after the projection period",
            key="dcf_terminal"
        )
    
    with col2:
        st.markdown("#### Time & Financial Structure")
        
        projection_years = st.slider(
            "📅 Projection Years",
            min_value=3,
            max_value=10,
            value=5,
            step=1,
            help="Number of years to project cash flows",
            key="dcf_years"
        )
        
        # Display base metrics
        st.markdown("#### 📊 Base Metrics")
        st.markdown(f"**Base Cash Flow:** {format_currency(base_cash_flow)}")
        st.markdown(f"**Cash on Hand:** {format_currency(cash)}")
        st.markdown(f"**Total Debt:** {format_currency(debt)}")
        st.markdown(f"**Shares Outstanding:** {format_large_number(shares_outstanding)}")
        st.markdown(f"**Current Price:** {format_currency(current_price)}")
    
    # Calculate DCF with current parameters (using cached function)
    result = _calculate_dcf_cached(
        base_cash_flow=base_cash_flow,
        growth_rate=growth_rate,
        wacc=wacc,
        terminal_growth=terminal_growth,
        projection_years=int(projection_years),
        cash=cash,
        debt=debt,
        shares_outstanding=shares_outstanding
    )
    
    if "error" in result:
        st.error(f"❌ Calculation Error: {result['error']}")
        return
    
    # Display results prominently
    st.markdown("---")
    st.markdown("### 💎 Valuation Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    fair_value = result['fair_value_per_share']
    upside = ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0
    
    with col1:
        st.metric(
            "🎯 Fair Value per Share",
            format_currency(fair_value),
            delta=format_currency(fair_value - current_price)
        )
    
    with col2:
        upside_color = "normal" if upside > 20 else "off"
        st.metric(
            "📊 Upside/Downside",
            f"{upside:+.1f}%",
            delta="UNDERVALUED! 🚀" if upside > 20 else "OVERVALUED 📉" if upside < -10 else "Fair Value"
        )
    
    with col3:
        st.metric(
            "🏢 Enterprise Value",
            format_large_number(result['enterprise_value'])
        )
    
    with col4:
        st.metric(
            "💰 Equity Value",
            format_large_number(result['equity_value'])
        )
    
    # Show detailed breakdown
    with st.expander("📋 Detailed DCF Breakdown", expanded=False):
        st.markdown("#### Cash Flow Projections")
        
        cf_data = []
        for cf in result['projected_cash_flows']:
            cf_data.append({
                'Year': cf['year'],
                'Cash Flow': format_currency(cf['cash_flow']),
                'Discount Factor': f"{cf['discount_factor']:.4f}",
                'Present Value': format_currency(cf['present_value'])
            })
        
        cf_df = pd.DataFrame(cf_data)
        st.dataframe(cf_df, use_container_width=True)
        
        st.markdown("#### Terminal Value Calculation")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Terminal Cash Flow:** {format_currency(result['terminal_cf'])}")
            st.markdown(f"**Terminal Value:** {format_currency(result['terminal_value'])}")
        with col2:
            st.markdown(f"**PV of Terminal Value:** {format_currency(result['pv_terminal_value'])}")
            st.markdown(f"**PV of Projected CFs:** {format_currency(result['pv_projected_cfs'])}")
        
        st.markdown("#### Value Bridge")
        st.markdown(f"1. **Enterprise Value:** {format_currency(result['enterprise_value'])}")
        st.markdown(f"2. **Add: Cash:** {format_currency(cash)}")
        st.markdown(f"3. **Less: Debt:** {format_currency(debt)}")
        st.markdown(f"4. **Equals: Equity Value:** {format_currency(result['equity_value'])}")
        st.markdown(f"5. **÷ Shares Outstanding:** {format_large_number(shares_outstanding)}")
        st.markdown(f"6. **= Fair Value per Share:** {format_currency(fair_value)}")
    
    # Visualization of cash flows
    st.markdown("### 📊 Cash Flow Visualization")
    
    fig = go.Figure()
    
    years = [cf['year'] for cf in result['projected_cash_flows']]
    cash_flows = [cf['cash_flow'] for cf in result['projected_cash_flows']]
    present_values = [cf['present_value'] for cf in result['projected_cash_flows']]
    
    fig.add_trace(go.Bar(
        x=years,
        y=cash_flows,
        name="Projected Cash Flow",
        marker_color='#00d4ff',
        text=[format_currency(cf) for cf in cash_flows],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=present_values,
        name="Present Value",
        marker_color='#ff6b6b',
        text=[format_currency(pv) for pv in present_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Projected Cash Flows vs Present Values",
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        template="plotly_dark",
        height=400,
        barmode='group'
    )
    
    st.plotly_chart(fig, width="stretch")


@st.cache_data(ttl=600, show_spinner=False)
def _run_monte_carlo_cached(base_cash_flow, growth_mean, growth_std, wacc_mean, wacc_std, 
                            terminal_mean, terminal_std, projection_years, cash, debt, 
                            shares_outstanding, num_simulations):
    """Cached Monte Carlo simulation to avoid expensive recomputation"""
    from enhanced_valuation import get_enhanced_dcf_calculator
    calc = get_enhanced_dcf_calculator()
    return calc.monte_carlo_dcf(
        base_cash_flow=base_cash_flow,
        growth_rate_mean=growth_mean,
        growth_rate_std=growth_std,
        wacc_mean=wacc_mean,
        wacc_std=wacc_std,
        terminal_growth_mean=terminal_mean,
        terminal_growth_std=terminal_std,
        projection_years=int(projection_years),
        cash=cash,
        debt=debt,
        shares_outstanding=shares_outstanding,
        num_simulations=int(num_simulations)
    )


def show_monte_carlo_simulation(calc, base_cash_flow, current_price, cash, debt, shares_outstanding):
    """Monte Carlo simulation for DCF valuation"""
    
    st.markdown("### 🎲 Monte Carlo Simulation")
    st.markdown("Run thousands of simulations with varying assumptions to understand the range of possible outcomes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Mean Parameters")
        growth_mean = st.slider("Growth Rate (Mean)", 0.0, 0.50, 0.10, 0.01, format="%.0f%%", key="mc_growth_mean")
        wacc_mean = st.slider("WACC (Mean)", 0.05, 0.20, 0.10, 0.005, format="%.1f%%", key="mc_wacc_mean")
        terminal_mean = st.slider("Terminal Growth (Mean)", 0.0, 0.05, 0.025, 0.005, format="%.1f%%", key="mc_terminal_mean")
    
    with col2:
        st.markdown("#### Standard Deviations")
        growth_std = st.slider("Growth Rate (Std Dev)", 0.0, 0.10, 0.03, 0.005, format="%.1f%%", key="mc_growth_std")
        wacc_std = st.slider("WACC (Std Dev)", 0.0, 0.05, 0.02, 0.005, format="%.1f%%", key="mc_wacc_std")
        terminal_std = st.slider("Terminal Growth (Std Dev)", 0.0, 0.02, 0.005, 0.001, format="%.2f%%", key="mc_terminal_std")
    
    num_simulations = st.select_slider(
        "Number of Simulations",
        options=[100, 500, 1000, 2500, 5000, 10000],
        value=1000,
        key="mc_num_sims"
    )
    
    projection_years = st.slider("Projection Years", 3, 10, 5, 1, key="mc_years")
    
    if st.button("🚀 Run Monte Carlo Simulation", type="primary", key="run_mc"):
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"🎲 Initializing {num_simulations:,} simulations...")
        progress_bar.progress(10)
        
        status_text.text(f"🔢 Running calculations... This may take {num_simulations//100} seconds")
        progress_bar.progress(30)
        
        mc_result = _run_monte_carlo_cached(
            base_cash_flow=base_cash_flow,
            growth_mean=growth_mean,
            growth_std=growth_std,
            wacc_mean=wacc_mean,
            wacc_std=wacc_std,
            terminal_mean=terminal_mean,
            terminal_std=terminal_std,
            projection_years=int(projection_years),
            cash=cash,
            debt=debt,
            shares_outstanding=shares_outstanding,
            num_simulations=int(num_simulations)
        )
        
        progress_bar.progress(90)
        status_text.text("📊 Processing results...")
        
        progress_bar.progress(100)
        status_text.text("✅ Simulation complete!")
        
        # Clean up progress indicators after a moment
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        if "error" in mc_result:
            st.error(f"❌ Simulation Error: {mc_result['error']}")
            return
        
        # Display results
        st.success(f"✅ Completed {mc_result['num_successful_simulations']} successful simulations")
        
        st.markdown("### 📊 Simulation Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean Fair Value", format_currency(mc_result['fair_value_mean']))
        with col2:
            st.metric("Median Fair Value", format_currency(mc_result['fair_value_median']))
        with col3:
            st.metric("Std Deviation", format_currency(mc_result['fair_value_std']))
        with col4:
            upside_mean = ((mc_result['fair_value_mean'] - current_price) / current_price * 100) if current_price > 0 else 0
            st.metric("Mean Upside", f"{upside_mean:+.1f}%")
        
        # Confidence intervals
        st.markdown("### 📈 Confidence Intervals")
        
        ci_data = []
        for level, (low, high) in mc_result['confidence_intervals'].items():
            ci_data.append({
                'Confidence Level': level,
                'Lower Bound': format_currency(low),
                'Upper Bound': format_currency(high),
                'Range': format_currency(high - low)
            })
        
        ci_df = pd.DataFrame(ci_data)
        st.dataframe(ci_df, use_container_width=True)
        
        # Distribution chart
        st.markdown("### 📊 Fair Value Distribution")
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=mc_result['all_fair_values'],
            nbinsx=50,
            name="Fair Value Distribution",
            marker_color='#00d4ff',
            opacity=0.7
        ))
        
        # Add current price line
        fig.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current Price: {format_currency(current_price)}"
        )
        
        # Add mean line
        fig.add_vline(
            x=mc_result['fair_value_mean'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Mean: {format_currency(mc_result['fair_value_mean'])}"
        )
        
        fig.update_layout(
            title="Distribution of Fair Value from Monte Carlo Simulation",
            xaxis_title="Fair Value per Share ($)",
            yaxis_title="Frequency",
            template="plotly_dark",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, width="stretch")
        
        # Percentiles
        st.markdown("### 📉 Percentile Breakdown")
        
        percentile_data = []
        for p, val in mc_result['fair_value_percentiles'].items():
            percentile_data.append({
                'Percentile': p,
                'Fair Value': format_currency(val),
                'vs Current': f"{((val - current_price) / current_price * 100):+.1f}%"
            })
        
        perc_df = pd.DataFrame(percentile_data)
        st.dataframe(perc_df, use_container_width=True)


def show_sensitivity_analysis(calc, base_cash_flow, current_price, cash, debt, shares_outstanding):
    """Sensitivity analysis for key parameters"""
    
    st.markdown("### 📊 Sensitivity Analysis")
    st.markdown("See how fair value changes when one variable is adjusted while keeping others constant")
    
    # Base parameters
    col1, col2 = st.columns(2)
    
    with col1:
        base_growth = st.slider("Base Growth Rate", 0.0, 0.50, 0.10, 0.01, format="%.0f%%", key="sens_base_growth")
        base_wacc = st.slider("Base WACC", 0.05, 0.20, 0.10, 0.005, format="%.1f%%", key="sens_base_wacc")
    
    with col2:
        base_terminal = st.slider("Base Terminal Growth", 0.0, 0.05, 0.025, 0.005, format="%.1f%%", key="sens_base_terminal")
        projection_years = st.slider("Projection Years", 3, 10, 5, 1, key="sens_years")
    
    # Select variable to analyze
    variable = st.selectbox(
        "Select Variable to Analyze",
        ["Growth Rate", "WACC", "Terminal Growth"],
        key="sens_variable"
    )
    
    if variable == "Growth Rate":
        param_range = np.linspace(0.0, 0.50, 21)
        param_name = "growth_rate"
    elif variable == "WACC":
        param_range = np.linspace(0.05, 0.20, 21)
        param_name = "wacc"
    else:  # Terminal Growth
        param_range = np.linspace(0.0, 0.05, 21)
        param_name = "terminal_growth"
    
    if st.button("📊 Run Sensitivity Analysis", type="primary", key="run_sens"):
        with st.spinner("Calculating sensitivity..."):
            sens_result = calc.sensitivity_analysis(
                base_cash_flow=base_cash_flow,
                base_growth_rate=base_growth,
                base_wacc=base_wacc,
                terminal_growth=base_terminal,
                projection_years=int(projection_years),
                cash=cash,
                debt=debt,
                shares_outstanding=shares_outstanding,
                param_name=param_name,
                param_range=param_range.tolist()
            )
        
        if "error" in sens_result:
            st.error(f"❌ Error: {sens_result['error']}")
            return
        
        # Plot results
        results = sens_result['results']
        param_values = [r['param_value'] for r in results]
        fair_values = [r['fair_value'] for r in results]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[p * 100 for p in param_values],
            y=fair_values,
            mode='lines+markers',
            name="Fair Value",
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=8)
        ))
        
        # Add current price line
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current: {format_currency(current_price)}"
        )
        
        fig.update_layout(
            title=f"Sensitivity Analysis: {variable}",
            xaxis_title=f"{variable} (%)",
            yaxis_title="Fair Value per Share ($)",
            template="plotly_dark",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width="stretch")
        
        # Data table
        st.markdown("### 📋 Detailed Results")
        sens_df = pd.DataFrame({
            f'{variable} (%)': [f"{p*100:.1f}%" for p in param_values],
            'Fair Value': [format_currency(fv) for fv in fair_values],
            'vs Current': [f"{((fv - current_price) / current_price * 100):+.1f}%" for fv in fair_values]
        })
        st.dataframe(sens_df, use_container_width=True)
    
    # Two-way sensitivity
    st.markdown("---")
    st.markdown("### 🎯 Two-Way Sensitivity Matrix")
    st.markdown("See how fair value varies with two parameters simultaneously")
    
    if st.button("🚀 Generate Two-Way Matrix", key="run_2way"):
        with st.spinner("Generating sensitivity matrix..."):
            growth_rates = np.linspace(0.05, 0.25, 9)
            waccs = np.linspace(0.06, 0.16, 9)
            
            matrix_df = calc.two_way_sensitivity(
                base_cash_flow=base_cash_flow,
                growth_rates=growth_rates.tolist(),
                waccs=waccs.tolist(),
                terminal_growth=base_terminal,
                projection_years=int(projection_years),
                cash=cash,
                debt=debt,
                shares_outstanding=shares_outstanding
            )
        
        if not matrix_df.empty:
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=matrix_df.values,
                x=matrix_df.columns,
                y=matrix_df.index,
                colorscale='RdYlGn',
                text=[[format_currency(val) for val in row] for row in matrix_df.values],
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Fair Value")
            ))
            
            fig.update_layout(
                title="Fair Value Sensitivity: Growth Rate vs WACC",
                xaxis_title="WACC",
                yaxis_title="Growth Rate",
                template="plotly_dark",
                height=600
            )
            
            st.plotly_chart(fig, width="stretch")


def show_scenario_comparison(calc, base_cash_flow, current_price, cash, debt, shares_outstanding):
    """Compare different valuation scenarios side-by-side"""
    
    st.markdown("### 📈 Scenario Comparison")
    st.markdown("Compare Bear, Base, and Bull scenarios with different assumptions")
    
    # Define scenarios
    scenarios = {
        "🐻 Bear Case": {
            "growth_rate": 0.05,
            "wacc": 0.12,
            "terminal_growth": 0.015,
            "projection_years": 5
        },
        "📊 Base Case": {
            "growth_rate": 0.10,
            "wacc": 0.10,
            "terminal_growth": 0.025,
            "projection_years": 5
        },
        "🚀 Bull Case": {
            "growth_rate": 0.20,
            "wacc": 0.08,
            "terminal_growth": 0.035,
            "projection_years": 5
        }
    }
    
    # Allow user to customize scenarios
    with st.expander("🎛️ Customize Scenarios", expanded=False):
        for scenario_name in scenarios.keys():
            st.markdown(f"#### {scenario_name}")
            col1, col2 = st.columns(2)
            with col1:
                scenarios[scenario_name]["growth_rate"] = st.slider(
                    "Growth Rate",
                    0.0, 0.50,
                    scenarios[scenario_name]["growth_rate"],
                    0.01,
                    format="%.0f%%",
                    key=f"scen_{scenario_name}_growth"
                )
                scenarios[scenario_name]["wacc"] = st.slider(
                    "WACC",
                    0.05, 0.20,
                    scenarios[scenario_name]["wacc"],
                    0.005,
                    format="%.1f%%",
                    key=f"scen_{scenario_name}_wacc"
                )
            with col2:
                scenarios[scenario_name]["terminal_growth"] = st.slider(
                    "Terminal Growth",
                    0.0, 0.05,
                    scenarios[scenario_name]["terminal_growth"],
                    0.005,
                    format="%.1f%%",
                    key=f"scen_{scenario_name}_terminal"
                )
    
    # Calculate all scenarios
    results = {}
    for scenario_name, params in scenarios.items():
        result = calc.calculate_dcf_detailed(
            base_cash_flow=base_cash_flow,
            growth_rate=params["growth_rate"],
            wacc=params["wacc"],
            terminal_growth=params["terminal_growth"],
            projection_years=params["projection_years"],
            cash=cash,
            debt=debt,
            shares_outstanding=shares_outstanding
        )
        
        if "error" not in result:
            results[scenario_name] = result
    
    if not results:
        st.error("❌ Could not calculate any scenarios")
        return
    
    # Display comparison metrics
    st.markdown("### 📊 Scenario Comparison")
    
    cols = st.columns(len(results))
    
    for idx, (scenario_name, result) in enumerate(results.items()):
        with cols[idx]:
            fair_value = result['fair_value_per_share']
            upside = ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0
            
            # Color code based on scenario
            if "Bear" in scenario_name:
                color = "#FF3860"
            elif "Bull" in scenario_name:
                color = "#00FF88"
            else:
                color = "#FFB700"
            
            st.markdown(f"""
            <div style="background: {color}20; border: 2px solid {color}; padding: 15px; border-radius: 10px; text-align: center;">
                <h3 style="color: {color}; margin: 0;">{scenario_name}</h3>
                <h2 style="color: white; margin: 10px 0;">{format_currency(fair_value)}</h2>
                <p style="color: white; margin: 5px 0;">Upside: {upside:+.1f}%</p>
                <p style="color: #b8b8b8; font-size: 0.9em;">EV: {format_large_number(result['enterprise_value'])}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Comparison chart
    st.markdown("### 📊 Visual Comparison")
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Fair Value Comparison", "Enterprise Value Comparison"),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    scenario_names = list(results.keys())
    fair_values = [r['fair_value_per_share'] for r in results.values()]
    enterprise_values = [r['enterprise_value'] for r in results.values()]
    colors = ['#FF3860', '#FFB700', '#00FF88']
    
    fig.add_trace(
        go.Bar(
            x=scenario_names,
            y=fair_values,
            marker_color=colors,
            text=[format_currency(fv) for fv in fair_values],
            textposition='outside',
            name="Fair Value"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=scenario_names,
            y=enterprise_values,
            marker_color=colors,
            text=[format_large_number(ev) for ev in enterprise_values],
            textposition='outside',
            name="Enterprise Value"
        ),
        row=1, col=2
    )
    
    # Add current price line to first subplot
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="white",
        row=1, col=1,
        annotation_text=f"Current: {format_currency(current_price)}"
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=500,
        showlegend=False
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Value ($)", row=1, col=2)
    
    st.plotly_chart(fig, width="stretch")
    
    # Detailed comparison table
    with st.expander("📋 Detailed Scenario Comparison", expanded=False):
        comparison_data = []
        for scenario_name, result in results.items():
            params = scenarios[scenario_name]
            comparison_data.append({
                'Scenario': scenario_name,
                'Fair Value': format_currency(result['fair_value_per_share']),
                'Enterprise Value': format_large_number(result['enterprise_value']),
                'Upside': f"{((result['fair_value_per_share'] - current_price) / current_price * 100):+.1f}%",
                'Growth Rate': f"{params['growth_rate']*100:.0f}%",
                'WACC': f"{params['wacc']*100:.1f}%",
                'Terminal Growth': f"{params['terminal_growth']*100:.1f}%"
            })
        
        comp_df = pd.DataFrame(comparison_data)
        st.dataframe(comp_df, use_container_width=True)


def get_base_cash_flow(financials: dict, info: dict) -> float:
    """
    Extract base cash flow from financial data
    
    Args:
        financials: Dictionary containing financial statements
        info: Dictionary containing stock info
        
    Returns:
        float: Base free cash flow (positive value), or 0 if not available
    """
    try:
        # Try to get free cash flow from financials
        if "cash_flow" in financials and financials.get("cash_flow"):
            cf_data = pd.DataFrame(financials["cash_flow"])
            if not cf_data.empty:
                if "Free Cash Flow" in cf_data.index:
                    fcf_values = cf_data.loc["Free Cash Flow"].values
                    # Get average of last 3-4 years
                    fcf_values = [v for v in fcf_values[:4] if v and not pd.isna(v)]
                    if fcf_values:
                        return abs(np.mean(fcf_values))
                
                if "Operating Cash Flow" in cf_data.index:
                    ocf_values = cf_data.loc["Operating Cash Flow"].values
                    ocf_values = [v for v in ocf_values[:4] if v and not pd.isna(v)]
                    if ocf_values:
                        # Estimate FCF as 80% of OCF
                        return abs(np.mean(ocf_values) * 0.8)
        
        # Fallback: estimate from info
        fcf = info.get("freeCashflow", 0)
        if fcf and fcf > 0:
            return abs(fcf)
        
        # Last resort: estimate from operating cash flow
        ocf = info.get("operatingCashflow", 0)
        if ocf and ocf > 0:
            return abs(ocf * 0.8)
        
        return 0
    
    except Exception as e:
        logger.error(f"Error extracting base cash flow: {e}")
        return 0
