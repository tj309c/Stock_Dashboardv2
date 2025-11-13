import streamlit as st
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

# --- Placeholder Classes and Functions (Mimicking original context) ---

@dataclass
class Context:
    ticker_symbol: str = "AAPL"
    info: Dict[str, Any] = field(default_factory=lambda: {
        "sector": "Technology",
        "marketCap": 2800000000000,
        "sharesOutstanding": 15000000000,
        "enterpriseValue": 2700000000000,
        "freeCashFlowYield": 0.05
    })
    # Default calculated values (these would come from financial data processing)
    op_cash_flow_avg: float = 120_000_000_000  # Example value
    cash_value: float = 100_000_000_000         # Example value
    total_debt_value: float = 120_000_000_000    # Example value
    shares_outstanding_value: float = 15_000_000_000 # Example value (diluted)

    # DCF specific inputs
    fcf_input: float = 100_000_000_000
    fcf_growth_rate: float = 0.05
    discount_rate: float = 0.09
    perpetual_growth_rate: float = 0.02
    projection_years: int = 10
    high_growth_years: int = 5
    fade_years: int = 3
    enable_two_stage: bool = True

    # Other model results
    ddm_value: float = 180.0
    nav_value: float = 170.0
    nav_upside: float = 0.15

@dataclass
class DCFInputs:
    fcf: float
    cash: float
    total_debt: float
    shares_outstanding: float
    growth_rate: float
    wacc: float
    perpetual_rate: float
    years: int
    high_growth_years: int
    fade_years: int

def get_ai_comparables(ticker: str, sector: str) -> pd.DataFrame:
    """Placeholder for fetching comparable companies."""
    data = {
        'Company': [f"{sector} Co A", f"{sector} Co B", f"{sector} Co C"],
        'Market Cap': [1e12, 0.8e12, 1.5e12],
        'P/E': [25.0, 22.0, 28.0],
        'EV/EBITDA': [15.0, 14.0, 16.0],
        'FCF Yield': [0.04, 0.05, 0.035]
    }
    return pd.DataFrame(data)

def calculate_valuation_score(
    info: Dict[str, Any],
    dcf_upside: Optional[float],
    ddm_upside: Optional[float],
    fcf_yield: float,
    discount_rate: float,
    sector_comps: pd.DataFrame,
    ) -> tuple:
    """Placeholder for valuation scoring logic."""
    overall_rating = "Hold"
    final_score_num = 65
    breakdown_scores = {"DCF": 70, "DDM": 60, "Comps": 65}
    return overall_rating, final_score_num, breakdown_scores

def render_summary_tab(ctx, model_results, sector_comps, overall_rating, final_score_num, breakdown_scores):
    st.write("Summary content goes here.")
    st.write(f"Overall Rating: **{overall_rating}** (Score: {final_score_num})")
    st.write("Model Results:", model_results)
    st.write("Breakdown Scores:", breakdown_scores)
    st.write("Sector Comparables (first 3 rows):")
    st.dataframe(sector_comps.head(3))

def render_comps_tab(ctx, sector_comps, fcf_yield):
    st.write("Relative Valuation (Comps) content goes here.")
    st.subheader("Comparable Companies")
    st.dataframe(sector_comps)
    st.write(f"Company's FCF Yield: {fcf_yield:.2%}")

def render_other_models_tab(ctx, ddm_value, nav_value):
    st.write("Other Models (DDM/NAV) content goes here.")
    st.subheader("Dividend Discount Model (DDM)")
    st.metric("DDM Value per Share", f"${ddm_value:,.2f}")
    st.subheader("Net Asset Value (NAV)")
    st.metric("NAV Value per Share", f"${nav_value:,.2f}")

def perform_dcf_calculation(dcf_inputs: DCFInputs, ctx: Context) -> tuple[float, float]:
    """
    Placeholder for the actual DCF calculation logic.
    Returns estimated fair value per share and upside/downside.
    """
    # Simplified calculation for demonstration
    present_value_of_fcf = dcf_inputs.fcf * (1 + dcf_inputs.growth_rate) * (1 - (1 + dcf_inputs.growth_rate)**dcf_inputs.years * (1 + dcf_inputs.wacc)**dcf_inputs.years) / (dcf_inputs.wacc - dcf_inputs.growth_rate) if dcf_inputs.wacc != dcf_inputs.growth_rate else dcf_inputs.fcf * dcf_inputs.years
    terminal_value = (dcf_inputs.fcf * (1 + dcf_inputs.growth_rate)**dcf_inputs.years * (1 + dcf_inputs.perpetual_rate)) / (dcf_inputs.wacc - dcf_inputs.perpetual_rate)
    terminal_value_pv = terminal_value / ((1 + dcf_inputs.wacc)**dcf_inputs.years)

    enterprise_value = present_value_of_fcf + terminal_value_pv
    equity_value = enterprise_value + dcf_inputs.cash - dcf_inputs.total_debt
    
    if dcf_inputs.shares_outstanding > 0:
        fair_value_per_share = equity_value / dcf_inputs.shares_outstanding
    else:
        fair_value_per_share = 0.0

    # Assume ctx has current_price for upside calculation
    current_price = ctx.info.get('currentPrice', 150.0) # Example current price
    dcf_upside = (fair_value_per_share - current_price) / current_price if current_price > 0 else 0.0

    return fair_value_per_share, dcf_upside

# --- End Placeholder Functions ---


# --- Fix starts here: render_dcf_tab and session state initialization ---

def render_dcf_tab(ctx, initial_dcf_inputs):
    st.header("Discounted Cash Flow (DCF) Model")

    st.subheader("Override Core Metrics")
    st.write("Adjust the core financial metrics used in the DCF calculation. Leave the override field empty or click 'Reset' to use the system's calculated values.")

    # List of metrics that can be overridden, along with their corresponding ctx attributes and session state keys
    override_metrics = [
        ("Operating Cash Flow (Annual Avg from Financials)", "op_cash_flow_avg", "override_ocf"),
        ("Current Cash & Equivalents", "cash_value", "override_cash"),
        ("Total Debt", "total_debt_value", "override_debt"),
        ("Shares Outstanding (Diluted)", "shares_outstanding_value", "override_shares"),
    ]

    # Values that will be used in the DCF calculation
    val_ocf = initial_dcf_inputs.fcf # Fallback to original dcf_inputs values
    val_cash = initial_dcf_inputs.cash
    val_debt = initial_dcf_inputs.total_debt
    val_shares = initial_dcf_inputs.shares_outstanding

    for label, ctx_attr, ss_key in override_metrics:
        default_value = getattr(ctx, ctx_attr, 0.0) # Get default from ctx, or 0.0 if not found
        
        # Determine the value to display in the number_input
        # If an override exists in session state, display that. Otherwise, display the default.
        display_value = st.session_state[ss_key] if st.session_state[ss_key] is not None else default_value

        col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
        with col1:
            st.markdown(f"**{label}**")
            st.info(f"{default_value:,.2f}")
        with col2:
            st.session_state[ss_key] = st.number_input(
                f"Override {label.split('(')[0].strip()}", # e.g., "Override Operating Cash Flow"
                value=display_value,
                key=f"dcf_{ss_key}",
                format="%.2f",
                help=f"Override the {label.lower()} for DCF calculation."
            )
        with col3:
            # Add a reset button for each override
            if st.button("Reset", key=f"reset_{ss_key}"):
                st.session_state[ss_key] = None
                st.rerun() # Rerun to update the number_input with the default value

        # Assign the actual value to be used in DCF calculation
        # If session state override is None, use the default_value from ctx
        # Otherwise, use the overridden value from session state
        if ss_key == "override_ocf":
            val_ocf = st.session_state[ss_key] if st.session_state[ss_key] is not None else default_value
        elif ss_key == "override_cash":
            val_cash = st.session_state[ss_key] if st.session_state[ss_key] is not None else default_value
        elif ss_key == "override_debt":
            val_debt = st.session_state[ss_key] if st.session_state[ss_key] is not None else default_value
        elif ss_key == "override_shares":
            val_shares = st.session_state[ss_key] if st.session_state[ss_key] is not None else default_value
    
    st.markdown("---")

    # --- Other DCF Parameters (not subject to override fix in this task, so using initial_dcf_inputs/ctx) ---
    st.subheader("DCF Growth and Discount Rates")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("FCF Growth Rate (Initial)", f"{initial_dcf_inputs.growth_rate:.2%}")
    with col2:
        st.metric("WACC", f"{initial_dcf_inputs.wacc:.2%}")
    with col3:
        st.metric("Perpetual Growth Rate", f"{initial_dcf_inputs.perpetual_rate:.2%}")

    st.subheader("Projection Periods")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Projection Years", f"{initial_dcf_inputs.years}")
    with col2:
        st.metric("High Growth Years", f"{initial_dcf_inputs.high_growth_years}")
    with col3:
        st.metric("Fade Years", f"{initial_dcf_inputs.fade_years}")

    st.markdown("---")

    # Re-create DCFInputs with potentially overridden values
    dcf_inputs_for_calc = DCFInputs(
        fcf=val_ocf,
        cash=val_cash,
        total_debt=val_debt,
        shares_outstanding=val_shares,
        growth_rate=initial_dcf_inputs.growth_rate,
        wacc=initial_dcf_inputs.wacc,
        perpetual_rate=initial_dcf_inputs.perpetual_rate,
        years=initial_dcf_inputs.years,
        high_growth_years=initial_dcf_inputs.high_growth_years,
        fade_years=initial_dcf_inputs.fade_years
    )

    # Perform DCF calculation with the updated inputs
    dcf_value_per_share, dcf_upside = perform_dcf_calculation(dcf_inputs_for_calc, ctx)

    st.subheader("DCF Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("DCF Value per Share", f"${dcf_value_per_share:,.2f}")
    with col2:
        st.metric("DCF Upside/Downside", f"{dcf_upside:+.2%}")
    
    # Placeholder for charts or more detailed breakdown
    st.write("Detailed cash flow projections, sensitivity analysis, and charts would be displayed here.")


def render_page():
    st.set_page_config(layout="wide", page_title="Valuation Models")
    st.title("💰 Valuation Models")

    # Initialize Context with dummy data
    ctx = Context()

    # --- Initialize session state variables for overrides to None ---
    # This ensures that an explicit 0.0 override is distinguishable from "no override".
    if 'override_ocf' not in st.session_state:
        st.session_state.override_ocf = None
    if 'override_cash' not in st.session_state:
        st.session_state.override_cash = None
    if 'override_debt' not in st.session_state:
        st.session_state.override_debt = None
    if 'override_shares' not in st.session_state:
        st.session_state.override_shares = None
    # Add other override variables here if they exist in the application
    # --- End of session state initialization ---

    # Placeholder for model results (would be calculated elsewhere)
    model_results = {}
    dcf_upside = 0.20 # Example dcf upside
    fcf_yield = ctx.info.get('freeCashFlowYield', 0.0)

    # Example DD M and NAV calculations (these would typically be functions returning values)
    if ctx.ddm_value > 0:
        model_results['DDM'] = {'value': ctx.ddm_value, 'upside': (ctx.ddm_value - ctx.info.get('currentPrice', 150.0)) / ctx.info.get('currentPrice', 150.0) if ctx.info.get('currentPrice', 150.0) > 0 else 0}
    if ctx.nav_value > 0:
        model_results['NAV'] = {'value': ctx.nav_value, 'upside': ctx.nav_upside}

    sector_comps = get_ai_comparables(ctx.ticker_symbol, ctx.info.get('sector', 'default'))
    
    overall_rating, final_score_num, breakdown_scores = calculate_valuation_score(
        ctx.info, dcf_upside, model_results.get('DDM', {}).get('upside', None), fcf_yield, ctx.discount_rate, sector_comps,
    )

    dcf_inputs = DCFInputs(
        fcf=ctx.fcf_input, cash=ctx.cash_value, total_debt=ctx.total_debt_value, # Ensure these match ctx attributes used in render_dcf_tab
        shares_outstanding=ctx.shares_outstanding_value, growth_rate=ctx.fcf_growth_rate,
        wacc=ctx.discount_rate, perpetual_rate=ctx.perpetual_growth_rate,
        years=ctx.projection_years,
        high_growth_years=ctx.high_growth_years if ctx.enable_two_stage else 0,
        fade_years=ctx.fade_years if ctx.enable_two_stage else 0
    )

    # --- TABS LAYOUT ---
    summary_tab, dcf_tab, comps_tab, other_tab = st.tabs([
        "Summary", "Discounted Cash Flow (DCF)", "Relative Valuation (Comps)", "Other Models (DDM/NAV)"
    ])

    with summary_tab:
        render_summary_tab(ctx, model_results, sector_comps, overall_rating, final_score_num, breakdown_scores)

    with dcf_tab:
        # Pass the initial dcf_inputs, which will be modified by overrides within render_dcf_tab
        render_dcf_tab(ctx, dcf_inputs)

    with comps_tab:
        render_comps_tab(ctx, sector_comps, fcf_yield)

    with other_tab:
        render_other_models_tab(ctx, ctx.ddm_value, ctx.nav_value)

if __name__ == "__main__":
    render_page()