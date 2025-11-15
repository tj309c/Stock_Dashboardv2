"""
Zero-FCF Valuation Display Module
UI components for displaying alternative valuation methods
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def show_zero_fcf_valuation_tab(valuation_result: Dict, ticker: str):
    """
    Display comprehensive Zero-FCF valuation results with all methods.
    Shows detailed breakdown of each valuation approach.
    """
    if not valuation_result or "error" in valuation_result:
        st.error("❌ Unable to calculate Zero-FCF valuation")
        if "recommendation" in valuation_result:
            st.info(valuation_result["recommendation"])
        return
    
    st.markdown("""
    ### 🚀 Zero-FCF Valuation Analysis
    **Alternative valuation methods for high-growth companies**
    """)
    
    # Show company type detection
    company_type = valuation_result.get("company_type", "Unknown")
    st.info(f"**Detected Company Type:** {company_type}")
    
    # Main valuation summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fair_value = valuation_result.get("fair_value", 0)
        st.metric(
            "Fair Value",
            f"${fair_value:.2f}",
            help="Weighted average across all applicable methods"
        )
    
    with col2:
        current_price = valuation_result.get("current_price", 0)
        st.metric("Current Price", f"${current_price:.2f}")
    
    with col3:
        upside = valuation_result.get("upside", 0)
        st.metric(
            "Upside Potential",
            f"{upside:+.1f}%",
            delta=f"{upside:.1f}%"
        )
    
    with col4:
        confidence = valuation_result.get("confidence", "medium")
        confidence_emoji = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴"
        }
        st.metric(
            "Confidence",
            f"{confidence_emoji.get(confidence, '🟡')} {confidence.title()}"
        )
    
    # Scenarios
    st.markdown("### 📊 Valuation Scenarios")
    scenarios = valuation_result.get("scenarios", {})
    
    if scenarios:
        scenario_cols = st.columns(len(scenarios))
        scenario_names = {
            "bear": "🐻 Bear Case",
            "base": "📊 Base Case",
            "bull": "🐂 Bull Case",
            "optimistic": "🚀 Optimistic"
        }
        
        for col, (scenario, value) in zip(scenario_cols, scenarios.items()):
            with col:
                scenario_upside = ((value - current_price) / current_price * 100) if current_price > 0 else 0
                st.metric(
                    scenario_names.get(scenario, scenario),
                    f"${value:.2f}",
                    f"{scenario_upside:+.1f}%"
                )
    
    # Detailed method breakdown
    st.markdown("### 🔬 Valuation Methods Breakdown")
    
    valuations = valuation_result.get("valuations", {})
    primary_method = valuation_result.get("primary_method", "")
    
    if not valuations:
        st.warning("No detailed valuation methods available")
        return
    
    # Create tabs for each method
    method_tabs = st.tabs([_format_method_name(method) for method in valuations.keys()])
    
    for tab, (method, val_data) in zip(method_tabs, valuations.items()):
        with tab:
            _display_method_details(method, val_data, company_type, primary_method == method)
    
    # Comparison chart
    st.markdown("### 📈 Valuation Methods Comparison")
    _show_valuation_comparison_chart(valuations, current_price, fair_value)
    
    # Methodology explanation
    with st.expander("📚 Methodology & Assumptions"):
        _show_methodology_explanation(company_type, valuations)


def _format_method_name(method: str) -> str:
    """Format method name for display."""
    name_map = {
        "revenue": "💰 Revenue Multiple",
        "ebitda": "📊 EBITDA Multiple",
        "rule_of_40": "📐 Rule of 40",
        "unit_economics": "👥 Unit Economics",
        "terminal_value": "🎯 Terminal Value"
    }
    return name_map.get(method, method.replace("_", " ").title())


def _display_method_details(method: str, val_data: Dict, company_type: str, is_primary: bool):
    """Display detailed information for a specific valuation method."""
    
    if is_primary:
        st.success("⭐ **Primary Method** - Most reliable for this company type")
    
    # Method-specific displays
    if method == "revenue":
        _display_revenue_method(val_data)
    elif method == "ebitda":
        _display_ebitda_method(val_data)
    elif method == "rule_of_40":
        _display_rule_of_40_method(val_data)
    elif method == "unit_economics":
        _display_unit_economics_method(val_data)
    elif method == "terminal_value":
        _display_terminal_value_method(val_data)
    
    # Data quality indicator
    quality = val_data.get("data_quality", "medium")
    quality_color = {
        "high": "🟢",
        "medium": "🟡",
        "low": "🔴"
    }
    st.caption(f"Data Quality: {quality_color.get(quality, '🟡')} {quality.title()}")


def _display_revenue_method(val_data: Dict):
    """Display revenue multiple valuation details."""
    st.markdown("**Revenue Multiple Valuation**")
    st.write("Valuation based on revenue multiples typical for the company's sector and growth rate.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Fair Value", f"${val_data.get('fair_value', 0):.2f}")
        st.metric("Revenue", f"${val_data.get('revenue', 0) / 1e9:.2f}B")
        st.metric("Revenue Growth", f"{val_data.get('revenue_growth', 0):.1f}%")
    
    with col2:
        st.metric("Revenue Multiple", f"{val_data.get('revenue_multiple', 0):.1f}x")
        st.metric("Base Multiple", f"{val_data.get('base_multiple', 0):.1f}x")
        st.metric("Growth Adjustment", f"{val_data.get('growth_adjustment', 1.0):.2f}x")
    
    st.markdown(f"""
    **Calculation:**
    - Enterprise Value = Revenue × Adjusted Multiple
    - Adjusted Multiple = Base Multiple × Growth Adjustment
    - Fair Value = (EV + Cash - Debt) / Shares
    """)


def _display_ebitda_method(val_data: Dict):
    """Display EBITDA multiple valuation details."""
    st.markdown("**EBITDA Multiple Valuation**")
    st.write("Valuation based on EBITDA multiples, ideal for companies with positive EBITDA but negative FCF.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Fair Value", f"${val_data.get('fair_value', 0):.2f}")
        st.metric("EBITDA", f"${val_data.get('ebitda', 0) / 1e9:.2f}B")
        st.metric("EBITDA Margin", f"{val_data.get('ebitda_margin', 0):.1f}%")
    
    with col2:
        st.metric("EBITDA Multiple", f"{val_data.get('ebitda_multiple', 0):.1f}x")
        st.metric("Base Multiple", f"{val_data.get('base_multiple', 0):.1f}x")
        st.metric("Enterprise Value", f"${val_data.get('enterprise_value', 0) / 1e9:.2f}B")
    
    st.markdown("""
    **Calculation:**
    - Enterprise Value = EBITDA × Adjusted Multiple
    - Multiple adjusted for growth rate and profit margins
    - Fair Value = (EV + Cash - Debt) / Shares
    """)


def _display_rule_of_40_method(val_data: Dict):
    """Display Rule of 40 valuation details."""
    st.markdown("**Rule of 40 Valuation (SaaS Metric)**")
    st.write("SaaS companies are valued on: Revenue Growth Rate + FCF Margin ≥ 40%")
    
    # Rule of 40 score gauge
    rule_score = val_data.get("rule_of_40_score", 0)
    quality = val_data.get("quality_rating", "fair")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Rule of 40 Score", f"{rule_score:.1f}%")
        
        # Quality indicator
        quality_emoji = {
            "excellent": "🌟",
            "good": "👍",
            "fair": "👌",
            "poor": "⚠️"
        }
        st.write(f"{quality_emoji.get(quality, '👌')} **{quality.title()}** Quality")
    
    with col2:
        st.metric("Revenue Growth", f"{val_data.get('revenue_growth', 0):.1f}%")
        st.metric("FCF Margin", f"{val_data.get('fcf_margin', 0):.1f}%")
    
    with col3:
        st.metric("Fair Value", f"${val_data.get('fair_value', 0):.2f}")
        st.metric("Revenue Multiple", f"{val_data.get('revenue_multiple', 0):.1f}x")
    
    # Score interpretation
    if rule_score >= 40:
        st.success(f"✅ **Excellent**: Score ≥ 40% indicates healthy SaaS metrics")
    elif rule_score >= 20:
        st.info(f"ℹ️ **Good**: Score between 20-40% shows growth potential")
    else:
        st.warning(f"⚠️ **Below Target**: Score < 20% may indicate challenges")
    
    st.markdown("""
    **Interpretation:**
    - **Excellent (≥60%)**: Premium valuation, 1.5x multiplier
    - **Good (≥40%)**: Above average, 1.2x multiplier
    - **Fair (≥20%)**: Average, 1.0x multiplier
    - **Poor (<20%)**: Below average, 0.7x multiplier
    """)


def _display_unit_economics_method(val_data: Dict):
    """Display unit economics valuation details."""
    st.markdown("**Unit Economics Valuation (SaaS)**")
    st.write("Valuation based on Customer Lifetime Value (LTV) and Customer Acquisition Cost (CAC).")
    
    # LTV:CAC ratio gauge
    ltv_cac = val_data.get("ltv_cac_ratio", 0)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("LTV:CAC Ratio", f"{ltv_cac:.2f}x")
        
        if ltv_cac > 5:
            st.success("🌟 Excellent (>5x)")
        elif ltv_cac > 3:
            st.success("✅ Good (>3x)")
        elif ltv_cac > 2:
            st.warning("⚠️ Acceptable (>2x)")
        else:
            st.error("❌ Poor (<2x)")
    
    with col2:
        st.metric("Customer LTV", f"${val_data.get('ltv', 0):,.0f}")
        st.metric("Customer CAC", f"${val_data.get('cac', 0):,.0f}")
    
    with col3:
        st.metric("Payback Period", f"{val_data.get('payback_period_months', 0):.1f} mo")
        st.metric("Monthly Churn", f"{val_data.get('monthly_churn', 0):.1f}%")
    
    # Additional metrics
    st.markdown("#### 📊 Customer Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Est. Customers", f"{val_data.get('estimated_customers', 0):,.0f}")
        st.metric("Est. ARPU", f"${val_data.get('estimated_arpu', 0):,.0f}/year")
    
    with col2:
        st.metric("Fair Value", f"${val_data.get('fair_value', 0):.2f}")
        st.metric("Revenue Multiple", f"{val_data.get('revenue_multiple', 0):.1f}x")
    
    if val_data.get("note"):
        st.info(f"ℹ️ {val_data['note']}")
    
    st.markdown("""
    **Benchmarks:**
    - **LTV:CAC Ratio**: >3x is good, >5x is excellent
    - **Payback Period**: <12 months is good, <18 months acceptable
    - **Monthly Churn**: <5% is good for SMB, <2% for enterprise
    """)


def _display_terminal_value_method(val_data: Dict):
    """Display terminal value calculation details."""
    st.markdown("**Revenue Terminal Value Method**")
    st.write("Projects future revenue using CAGR and applies terminal multiple.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Fair Value", f"${val_data.get('fair_value', 0):.2f}")
        st.metric("Enterprise Value", f"${val_data.get('enterprise_value', 0) / 1e9:.2f}B")
    
    with col2:
        st.metric("Historical CAGR", f"{val_data.get('historical_cagr', 0):.1f}%")
        st.metric("Terminal Growth", f"{val_data.get('terminal_growth', 0):.1f}%")
    
    with col3:
        st.metric("Terminal Revenue", f"${val_data.get('terminal_revenue', 0) / 1e9:.2f}B")
        st.metric("Terminal Multiple", f"{val_data.get('terminal_multiple', 0):.1f}x")
    
    st.markdown(f"""
    **Projection Details:**
    - Projection Period: {val_data.get('projection_years', 5)} years
    - WACC Used: {val_data.get('wacc', 10):.1f}%
    - Growth decelerates over time to terminal rate
    """)


def _show_valuation_comparison_chart(valuations: Dict, current_price: float, weighted_avg: float):
    """Create a comparison chart of different valuation methods."""
    
    methods = []
    fair_values = []
    colors = []
    
    for method, val_data in valuations.items():
        if "fair_value" in val_data:
            methods.append(_format_method_name(method))
            fair_values.append(val_data["fair_value"])
            
            # Color based on comparison to current price
            if val_data["fair_value"] > current_price * 1.2:
                colors.append("green")
            elif val_data["fair_value"] > current_price:
                colors.append("lightgreen")
            elif val_data["fair_value"] > current_price * 0.8:
                colors.append("orange")
            else:
                colors.append("red")
    
    # Create chart
    fig = go.Figure()
    
    # Fair values by method
    fig.add_trace(go.Bar(
        x=methods,
        y=fair_values,
        name="Fair Value",
        marker_color=colors,
        text=[f"${v:.2f}" for v in fair_values],
        textposition="outside"
    ))
    
    # Current price line
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="blue",
        annotation_text=f"Current Price: ${current_price:.2f}",
        annotation_position="right"
    )
    
    # Weighted average line
    fig.add_hline(
        y=weighted_avg,
        line_dash="dot",
        line_color="purple",
        annotation_text=f"Weighted Avg: ${weighted_avg:.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Valuation by Method",
        xaxis_title="Method",
        yaxis_title="Fair Value per Share ($)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def _show_methodology_explanation(company_type: str, valuations: Dict):
    """Show detailed methodology explanation."""
    
    st.markdown(f"""
    ### Valuation Approach for {company_type} Companies
    
    **Why Zero-FCF Methods?**
    
    Companies with zero or negative free cash flow require alternative valuation methods because:
    - Traditional DCF relies on positive, predictable cash flows
    - High-growth companies prioritize growth over profitability
    - Capital-intensive companies invest heavily, reducing FCF
    
    **Methods Used:**
    """)
    
    if "revenue" in valuations:
        st.markdown("""
        **1. Revenue Multiple Valuation**
        - Uses industry-appropriate revenue multiples
        - Adjusts for growth rate (faster growth = higher multiple)
        - Common for software, SaaS, e-commerce companies
        - Multiple ranges: 1x (mature) to 10x+ (high-growth SaaS)
        """)
    
    if "ebitda" in valuations:
        st.markdown("""
        **2. EBITDA Multiple Valuation**
        - Values companies with positive EBITDA but negative FCF
        - Adjusts for margins and growth
        - Industry multiples: 8x-30x depending on sector
        - Accounts for capital intensity differences
        """)
    
    if "rule_of_40" in valuations:
        st.markdown("""
        **3. Rule of 40 (SaaS Specific)**
        - SaaS benchmark: Growth Rate + FCF Margin ≥ 40%
        - Scores 40%+ indicate healthy balance of growth and profitability
        - Higher scores warrant premium valuations
        - Helps identify quality SaaS businesses
        """)
    
    if "unit_economics" in valuations:
        st.markdown("""
        **4. Unit Economics (SaaS)**
        - Analyzes customer-level profitability
        - LTV:CAC ratio measures efficiency (target: >3x)
        - Payback period measures capital efficiency (target: <12 mo)
        - Churn rate impacts long-term viability
        """)
    
    if "terminal_value" in valuations:
        st.markdown("""
        **5. Revenue Terminal Value**
        - Projects future revenue using historical CAGR
        - Growth rate decelerates over 5-year projection
        - Applies terminal multiple based on maturity
        - Discounts back to present value using WACC
        """)
    
    st.markdown("""
    ### Data Quality & Confidence
    
    **Confidence Levels:**
    - **High**: 3+ methods with high-quality data
    - **Medium**: 2+ methods with at least 1 high-quality
    - **Low**: Single method or limited data quality
    
    **Weighting Logic:**
    - Methods are weighted based on company type
    - Data quality affects method weight
    - Primary method is most reliable for the company type
    """)


def show_zero_fcf_quick_summary(valuation_result: Dict):
    """
    Show a compact summary of Zero-FCF valuation for use in main dashboard.
    """
    if not valuation_result or "error" in valuation_result:
        return
    
    st.markdown("#### 🚀 Zero-FCF Valuation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fair_value = valuation_result.get("fair_value", 0)
        current_price = valuation_result.get("current_price", 0)
        st.metric("Fair Value", f"${fair_value:.2f}")
    
    with col2:
        upside = valuation_result.get("upside", 0)
        st.metric("Upside", f"{upside:+.1f}%", delta=f"{upside:.1f}%")
    
    with col3:
        primary_method = valuation_result.get("primary_method", "N/A")
        st.metric("Primary Method", _format_method_name(primary_method))
    
    # Quick scenarios
    scenarios = valuation_result.get("scenarios", {})
    if scenarios and len(scenarios) >= 3:
        st.markdown("**Scenarios:**")
        scenario_text = " | ".join([
            f"{name.title()}: ${value:.2f}"
            for name, value in list(scenarios.items())[:3]
        ])
        st.caption(scenario_text)
