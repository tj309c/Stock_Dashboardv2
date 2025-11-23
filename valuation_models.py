import dataclasses
from datetime import datetime
import numpy as np
from typing import Tuple, Dict, Optional, List
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

@dataclasses.dataclass
class DCFInputs:
    revenue_growth_rates: list[float]
    ebit_margin: float
    tax_rate: float
    depreciation_as_pct_revenue: float
    capex_as_pct_revenue: float
    nwc_as_pct_revenue: float
    terminal_growth_rate: float
    wacc: float
    cash: float
    total_debt: float
    shares_outstanding: float
    current_revenue: float # Assuming initial revenue is an input

    # Optional advanced parameters
    roic: Optional[float] = None  # Return on Invested Capital
    fade_years: Optional[int] = 5  # Years to fade margins to normalized levels
    terminal_ebit_margin: Optional[float] = None  # Normalized terminal margin
    sbc_as_pct_revenue: Optional[float] = 0.0  # Stock-based compensation
    target_dso: Optional[int] = 60  # Days Sales Outstanding for NWC
    target_dio: Optional[int] = 90  # Days Inventory Outstanding
    target_dpo: Optional[int] = 45  # Days Payables Outstanding

@dataclasses.dataclass
class WACCInputs:
    """Calculate WACC from fundamental inputs"""
    risk_free_rate: float
    beta: float
    market_risk_premium: float
    cost_of_debt: float
    tax_rate: float
    market_cap: float
    total_debt: float

def calculate_wacc(inputs: WACCInputs) -> float:
    """
    Calculate Weighted Average Cost of Capital
    WACC = (E/V * Re) + (D/V * Rd * (1-T))
    Where: Re = Rf + Beta * Market Risk Premium
    """
    try:
        # Cost of Equity (CAPM)
        cost_of_equity = inputs.risk_free_rate + (inputs.beta * inputs.market_risk_premium)

        # After-tax Cost of Debt
        after_tax_cost_of_debt = inputs.cost_of_debt * (1 - inputs.tax_rate)

        # Weights
        total_value = inputs.market_cap + inputs.total_debt
        if total_value <= 0:
            return cost_of_equity  # Fall back to cost of equity

        equity_weight = inputs.market_cap / total_value
        debt_weight = inputs.total_debt / total_value

        # WACC
        wacc = (equity_weight * cost_of_equity) + (debt_weight * after_tax_cost_of_debt)

        return max(0.01, min(wacc, 0.50))  # Clamp between 1% and 50%
    except (ZeroDivisionError, TypeError):
        return 0.10  # Default 10% if calculation fails
    
def calculate_dcf(inputs: DCFInputs):
    """
    Professional-grade Discounted Cash Flow valuation with:
    - Detailed working capital schedule
    - Margin fade to terminal levels
    - ROIC-based reinvestment (if provided)
    - Stock-based compensation
    - Multiple terminal value methods
    """
    try:
        if inputs.shares_outstanding <= 0:
            return 0, {}

        projection_years = len(inputs.revenue_growth_rates)

        # Initialize tracking arrays
        revenue_forecast = []
        ebit_forecast = []
        nopat_forecast = []
        fcf_forecast = []
        capex_forecast = []
        depreciation_forecast = []
        nwc_forecast = []
        delta_nwc_forecast = []
        sbc_forecast = []
        ebit_margins = []

        current_revenue = inputs.current_revenue
        previous_nwc = inputs.current_revenue * inputs.nwc_as_pct_revenue

        # Determine terminal EBIT margin (for fade logic)
        terminal_margin = inputs.terminal_ebit_margin if inputs.terminal_ebit_margin else inputs.ebit_margin
        fade_years = inputs.fade_years if inputs.fade_years else projection_years

        for i in range(projection_years):
            # Revenue projection
            current_revenue *= (1 + inputs.revenue_growth_rates[i])
            revenue_forecast.append(current_revenue)

            # EBIT margin fade (linear fade to terminal margin over fade_years)
            if i < fade_years:
                fade_factor = i / fade_years
                current_ebit_margin = inputs.ebit_margin * (1 - fade_factor) + terminal_margin * fade_factor
            else:
                current_ebit_margin = terminal_margin

            ebit_margins.append(current_ebit_margin)

            # EBIT and NOPAT
            ebit = current_revenue * current_ebit_margin
            nopat = ebit * (1 - inputs.tax_rate)
            ebit_forecast.append(ebit)
            nopat_forecast.append(nopat)

            # Depreciation & Amortization
            depreciation = current_revenue * inputs.depreciation_as_pct_revenue
            depreciation_forecast.append(depreciation)

            # Stock-based compensation (non-cash expense, add back)
            sbc = current_revenue * inputs.sbc_as_pct_revenue
            sbc_forecast.append(sbc)

            # Capital Expenditures
            if inputs.roic and inputs.roic > 0:
                # ROIC-based CapEx: Reinvestment = Growth * NOPAT / ROIC
                growth_dollars = current_revenue * inputs.revenue_growth_rates[i]
                capex = (growth_dollars / (1 + inputs.revenue_growth_rates[i])) * (inputs.revenue_growth_rates[i] / inputs.roic)
                capex = max(capex, depreciation * 0.8)  # Floor at 80% of D&A
            else:
                capex = current_revenue * inputs.capex_as_pct_revenue

            capex_forecast.append(capex)

            # Net Working Capital (detailed calculation)
            # NWC = (DSO/365 * Revenue) + (DIO/365 * COGS) - (DPO/365 * COGS)
            # Simplified: NWC as % of revenue, but track delta properly
            current_nwc = current_revenue * inputs.nwc_as_pct_revenue
            delta_nwc = current_nwc - previous_nwc
            nwc_forecast.append(current_nwc)
            delta_nwc_forecast.append(delta_nwc)
            previous_nwc = current_nwc

            # Free Cash Flow = NOPAT + D&A + SBC - CapEx - Delta NWC
            fcf = nopat + depreciation + sbc - capex - delta_nwc
            fcf_forecast.append(fcf)

        # Terminal Value (Gordon Growth Model)
        terminal_value_gg = 0
        if (inputs.wacc - inputs.terminal_growth_rate) > 0 and len(fcf_forecast) > 0:
            terminal_fcf = fcf_forecast[-1] * (1 + inputs.terminal_growth_rate)
            terminal_value_gg = terminal_fcf / (inputs.wacc - inputs.terminal_growth_rate)

        # Terminal Value (Exit Multiple Method) - using EV/EBITDA of 10x as default
        # This can be enhanced with sector-specific multiples
        terminal_ebitda = ebit_forecast[-1] + depreciation_forecast[-1]
        exit_multiple = 10.0  # Conservative EV/EBITDA multiple
        terminal_value_multiple = terminal_ebitda * exit_multiple

        # Use average of both methods for conservatism
        terminal_value = (terminal_value_gg + terminal_value_multiple) / 2

        # Present value of cash flows
        discounted_fcf = [fcf / (1 + inputs.wacc)**(i + 1) for i, fcf in enumerate(fcf_forecast)]

        # Present value of terminal value
        discounted_terminal_value = terminal_value / (1 + inputs.wacc)**projection_years

        # Enterprise Value
        enterprise_value = sum(discounted_fcf) + discounted_terminal_value

        # Equity Value = EV + Cash - Debt
        equity_value = enterprise_value + inputs.cash - inputs.total_debt

        # Value per share
        value_per_share = equity_value / inputs.shares_outstanding if inputs.shares_outstanding > 0 else 0

        # Comprehensive intermediates for debugging and display
        intermediates = {
            "fcf_forecast": fcf_forecast,
            "revenue_forecast": revenue_forecast,
            "ebit_forecast": ebit_forecast,
            "nopat_forecast": nopat_forecast,
            "ebit_margins": ebit_margins,
            "depreciation_forecast": depreciation_forecast,
            "capex_forecast": capex_forecast,
            "nwc_forecast": nwc_forecast,
            "delta_nwc_forecast": delta_nwc_forecast,
            "sbc_forecast": sbc_forecast,
            "terminal_value": terminal_value,
            "terminal_value_gg": terminal_value_gg,
            "terminal_value_multiple": terminal_value_multiple,
            "discounted_fcf": discounted_fcf,
            "discounted_tv": discounted_terminal_value,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "projection_years": projection_years,
            "pv_of_explicit_period": sum(discounted_fcf),
            "terminal_value_pct": (discounted_terminal_value / enterprise_value * 100) if enterprise_value > 0 else 0
        }

        return value_per_share, intermediates

    except (TypeError, OverflowError, ZeroDivisionError) as e:
        return 0, {}

def calculate_scenario_analysis(base_inputs: DCFInputs) -> Dict[str, Tuple[float, dict]]:
    """
    Run bear, base, and bull case scenarios
    Returns: {scenario_name: (value_per_share, intermediates)}
    """
    scenarios = {}

    # Base Case
    base_value, base_intermediates = calculate_dcf(base_inputs)
    scenarios['base'] = (base_value, base_intermediates)

    # Bear Case: Lower growth, lower margins, higher WACC
    bear_inputs = dataclasses.replace(
        base_inputs,
        revenue_growth_rates=[max(0, g * 0.5) for g in base_inputs.revenue_growth_rates],
        ebit_margin=base_inputs.ebit_margin * 0.8,
        wacc=base_inputs.wacc * 1.2,
        terminal_growth_rate=base_inputs.terminal_growth_rate * 0.5
    )
    bear_value, bear_intermediates = calculate_dcf(bear_inputs)
    scenarios['bear'] = (bear_value, bear_intermediates)

    # Bull Case: Higher growth, higher margins, lower WACC
    bull_inputs = dataclasses.replace(
        base_inputs,
        revenue_growth_rates=[g * 1.5 for g in base_inputs.revenue_growth_rates],
        ebit_margin=min(0.5, base_inputs.ebit_margin * 1.2),
        wacc=base_inputs.wacc * 0.85,
        terminal_growth_rate=min(0.06, base_inputs.terminal_growth_rate * 1.5)
    )
    bull_value, bull_intermediates = calculate_dcf(bull_inputs)
    scenarios['bull'] = (bull_value, bull_intermediates)

    # Probability-weighted average (40% base, 30% bear, 30% bull)
    weighted_value = (base_value * 0.40) + (bear_value * 0.30) + (bull_value * 0.30)
    scenarios['weighted'] = (weighted_value, {})

    return scenarios


def calculate_sensitivity_table(
    base_inputs: DCFInputs,
    wacc_range: Tuple[float, float] = (0.07, 0.15),
    tg_range: Tuple[float, float] = (0.01, 0.05),
    steps: int = 5
) -> Tuple[np.ndarray, List[float], List[float]]:
    """
    Generate 2-way sensitivity table for WACC vs Terminal Growth
    Returns: (value_matrix, wacc_values, tg_values)
    """
    wacc_values = np.linspace(wacc_range[0], wacc_range[1], steps)
    tg_values = np.linspace(tg_range[0], tg_range[1], steps)

    value_matrix = np.zeros((steps, steps))

    for i, wacc in enumerate(wacc_values):
        for j, tg in enumerate(tg_values):
            if wacc > tg:  # Only valid if WACC > terminal growth
                test_inputs = dataclasses.replace(base_inputs, wacc=wacc, terminal_growth_rate=tg)
                value, _ = calculate_dcf(test_inputs)
                value_matrix[i, j] = value
            else:
                value_matrix[i, j] = 0

    return value_matrix, wacc_values.tolist(), tg_values.tolist()


def calculate_reverse_dcf(
    current_market_price: float,
    inputs: DCFInputs,
    solve_for: str = 'terminal_growth'
) -> float:
    """
    Reverse DCF: What growth rate is implied by the current market price?
    solve_for: 'terminal_growth' or 'revenue_growth'
    """
    try:
        if solve_for == 'terminal_growth':
            # Binary search for implied terminal growth
            low, high = 0.0, inputs.wacc * 0.95
            tolerance = 0.0001
            max_iterations = 100

            for _ in range(max_iterations):
                mid = (low + high) / 2
                test_inputs = dataclasses.replace(inputs, terminal_growth_rate=mid)
                calculated_value, _ = calculate_dcf(test_inputs)

                if abs(calculated_value - current_market_price) < tolerance:
                    return mid

                if calculated_value < current_market_price:
                    low = mid
                else:
                    high = mid

            return mid

        elif solve_for == 'revenue_growth':
            # Find implied revenue growth (assuming constant growth across projection period)
            low, high = -0.20, 0.50
            tolerance = 0.01
            max_iterations = 100

            for _ in range(max_iterations):
                mid = (low + high) / 2
                test_growth = [mid] * len(inputs.revenue_growth_rates)
                test_inputs = dataclasses.replace(inputs, revenue_growth_rates=test_growth)
                calculated_value, _ = calculate_dcf(test_inputs)

                if abs(calculated_value - current_market_price) < tolerance:
                    return mid

                if calculated_value < current_market_price:
                    low = mid
                else:
                    high = mid

            return mid

    except (ValueError, TypeError):
        return 0.0

    return 0.0


def calculate_monte_carlo_dcf(
    base_inputs: DCFInputs,
    num_simulations: int = 10000,
    revenue_growth_std: float = 0.05,
    margin_std: float = 0.02,
    wacc_std: float = 0.01
) -> Dict[str, any]:
    """
    Monte Carlo simulation for probabilistic DCF valuation
    Returns distribution statistics and percentiles
    """
    results = []

    for _ in range(num_simulations):
        # Randomize key inputs around base case
        simulated_growth = [
            max(-0.5, min(0.5, g + np.random.normal(0, revenue_growth_std)))
            for g in base_inputs.revenue_growth_rates
        ]
        simulated_margin = max(0.01, min(0.8, base_inputs.ebit_margin + np.random.normal(0, margin_std)))
        simulated_wacc = max(0.01, min(0.5, base_inputs.wacc + np.random.normal(0, wacc_std)))
        simulated_tg = max(0.0, min(simulated_wacc * 0.9, base_inputs.terminal_growth_rate + np.random.normal(0, 0.005)))

        sim_inputs = dataclasses.replace(
            base_inputs,
            revenue_growth_rates=simulated_growth,
            ebit_margin=simulated_margin,
            wacc=simulated_wacc,
            terminal_growth_rate=simulated_tg
        )

        value, _ = calculate_dcf(sim_inputs)
        results.append(value)

    results = np.array(results)

    return {
        'mean': float(np.mean(results)),
        'median': float(np.median(results)),
        'std': float(np.std(results)),
        'p10': float(np.percentile(results, 10)),
        'p25': float(np.percentile(results, 25)),
        'p75': float(np.percentile(results, 75)),
        'p90': float(np.percentile(results, 90)),
        'min': float(np.min(results)),
        'max': float(np.max(results)),
        'distribution': results.tolist()
    }


# 78* (This is where the new/fixed function is placed)
def calculate_valuation_score(info: dict, comps: dict) -> float:
    """
    Calculates a valuation score based on comparing company multiples to sector averages.
    Lower multiples relative to the sector are generally considered better.
    The function now defaults to None for missing multiples and only compares if
    both company and sector multiples are present and positive.
    """
    score = 0
    factors_considered = 0

    # Define the valuation multiples to check
    # These keys are illustrative; adjust to actual keys in info and comps dicts
    multiples_to_compare = [
        'trailingPE',
        'priceToSalesTrailing12Months',
        'priceToBook',
        'enterpriseValueRevenue',
        'enterpriseValueEBITDA',
    ]

    for m_key in multiples_to_compare:
        # Fetch company and sector multiples, defaulting to None if not present.
        # This allows explicit checks for existence and positivity.
        company_multiple = info.get(m_key, None)
        sector_multiple = comps.get(m_key, None)

        # Only compare if both multiples are present (not None) and are positive.
        # This prevents ZeroDivisionError and ensures meaningful comparisons.
        if (company_multiple is not None and company_multiple > 0 and
            sector_multiple is not None and sector_multiple > 0):
            
            # Assuming lower multiples are generally better for valuation scoring.
            # You might adjust this logic based on specific valuation philosophies.
            if company_multiple < sector_multiple:
                score += 1
            # Could add a penalty or neutral score for higher multiples if desired
            # elif company_multiple > sector_multiple:
            #     score -= 1 # Example of a penalty
            
            factors_considered += 1
            
    return score / factors_considered if factors_considered > 0 else 0

# 79>
def calculate_ddm(dividend, wacc, growth):
    """Calculates value using the Gordon Growth Model."""
    if (wacc - growth) <= 0: return 0
    d1 = dividend * (1 + growth)
    return d1 / (wacc - growth)

# 85>
def calculate_nav(info):
    """Calculates Net Asset Value per share."""
    total_assets = info.get('totalAssets', 0)
    total_liabilities = info.get('totalLiab', 0)
    shares_outstanding = info.get('sharesOutstanding', 0)
    if total_assets > 0 and shares_outstanding > 0:
        return (total_assets - total_liabilities) / shares_outstanding
    return 0

# 94>
def generate_dcf_debug_text(ticker, inputs: DCFInputs, intermediates, result):
    text = f"--- DCF Debug Report for {ticker} ---\n"
    text += f"--- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n"
    
    # 98>
    text += "--- 1. INPUT VARIABLES ---\n"
    text += f"Current Revenue: {inputs.current_revenue:,.2f}\n"
    text += f"Revenue Growth Rates: {inputs.revenue_growth_rates}\n"
    text += f"EBIT Margin: {inputs.ebit_margin:.2%}\n"
    text += f"Tax Rate: {inputs.tax_rate:.2%}\n"
    text += f"Depreciation as % Revenue: {inputs.depreciation_as_pct_revenue:.2%}\n"
    text += f"Capex as % Revenue: {inputs.capex_as_pct_revenue:.2%}\n"
    text += f"NWC as % Revenue: {inputs.nwc_as_pct_revenue:.2%}\n"
    text += f"Terminal Growth Rate: {inputs.terminal_growth_rate:.2%}\n"
    text += f"WACC: {inputs.wacc:.2%}\n"
    text += f"Cash: {inputs.cash:,.2f}\n"
    text += f"Total Debt: {inputs.total_debt:,.2f}\n"
    text += f"Shares Outstanding: {inputs.shares_outstanding:,.2f}\n\n"

    text += "--- 2. INTERMEDIATE CALCULATIONS ---\n"
    if intermediates:
        text += f"Projection Years: {intermediates.get('projection_years', 'N/A')}\n"
        if "fcf_forecast" in intermediates:
            fcf_str = ", ".join([f"{f:.2f}" for f in intermediates["fcf_forecast"]])
            text += f"FCF Forecast: [{fcf_str}]\n"
        text += f"Terminal Value: {intermediates.get('terminal_value', 0):,.2f}\n"
        if "discounted_fcf" in intermediates:
            dfcf_str = ", ".join([f"{df:.2f}" for df in intermediates["discounted_fcf"]])
            text += f"Discounted FCF: [{dfcf_str}]\n"
        text += f"Discounted Terminal Value: {intermediates.get('discounted_tv', 0):,.2f}\n"
        text += f"Enterprise Value: {intermediates.get('enterprise_value', 0):,.2f}\n"
        text += f"Equity Value: {intermediates.get('equity_value', 0):,.2f}\n\n"
    else:
        text += "No intermediate calculations available.\n\n"

    text += "--- 3. RESULT ---\n"
    text += f"DCF Value Per Share: {result:,.2f}\n"

    return text


# Professional Visualization Functions

def create_dcf_waterfall_chart(intermediates: dict, market_price: float) -> go.Figure:
    """
    Create a waterfall chart showing bridge from Enterprise Value to Market Price
    """
    if not intermediates:
        return go.Figure()

    # Build waterfall components
    pv_fcf = intermediates.get('pv_of_explicit_period', 0)
    pv_tv = intermediates.get('discounted_tv', 0)
    enterprise_value = intermediates.get('enterprise_value', 0)

    # Get cash and debt from intermediates if available, otherwise use 0
    # Note: These aren't in intermediates, so we'll show EV breakdown only

    measures = ["relative", "relative", "total"]
    x_labels = ["PV of FCF (5Y)", "PV of Terminal Value", "Enterprise Value"]
    y_values = [pv_fcf, pv_tv, enterprise_value]

    fig = go.Figure(go.Waterfall(
        name="DCF Valuation Bridge",
        orientation="v",
        measure=measures,
        x=x_labels,
        y=y_values,
        textposition="outside",
        text=[f"${v/1e9:.2f}B" if v > 1e9 else f"${v/1e6:.1f}M" for v in y_values],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="DCF Valuation Waterfall: Enterprise Value Build-up",
        showlegend=False,
        height=500,
        template="plotly_white"
    )

    return fig


def create_football_field_chart(
    dcf_value: float,
    market_price: float,
    scenarios: Dict[str, Tuple[float, dict]] = None,
    comparable_multiples: Dict[str, float] = None
) -> go.Figure:
    """
    Create a football field chart showing valuation ranges from different methods
    """
    methods = []
    low_values = []
    high_values = []
    mid_values = []
    colors = []

    # Add DCF scenarios if available
    if scenarios:
        bear_val = scenarios.get('bear', (0, {}))[0]
        base_val = scenarios.get('base', (dcf_value, {}))[0]
        bull_val = scenarios.get('bull', (0, {}))[0]

        if bear_val > 0 and bull_val > 0:
            methods.append("DCF Analysis")
            low_values.append(bear_val)
            mid_values.append(base_val)
            high_values.append(bull_val)
            colors.append('rgba(55, 128, 191, 0.7)')
    else:
        # Simple DCF range (±20%)
        methods.append("DCF Analysis")
        low_values.append(dcf_value * 0.8)
        mid_values.append(dcf_value)
        high_values.append(dcf_value * 1.2)
        colors.append('rgba(55, 128, 191, 0.7)')

    # Add comparable multiples if provided
    if comparable_multiples:
        for method_name, value in comparable_multiples.items():
            if value > 0:
                methods.append(method_name)
                low_values.append(value * 0.85)
                mid_values.append(value)
                high_values.append(value * 1.15)
                colors.append('rgba(219, 64, 82, 0.7)')

    # Current market price
    methods.append("Current Market Price")
    low_values.append(market_price)
    mid_values.append(market_price)
    high_values.append(market_price)
    colors.append('rgba(50, 171, 96, 0.7)')

    fig = go.Figure()

    # Add bars for each valuation method
    for i, method in enumerate(methods):
        fig.add_trace(go.Bar(
            name=method,
            y=[method],
            x=[high_values[i] - low_values[i]],
            base=low_values[i],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f"${mid_values[i]:.2f}",
            textposition='inside',
            hovertemplate=f"<b>{method}</b><br>" +
                         f"Low: ${low_values[i]:.2f}<br>" +
                         f"Mid: ${mid_values[i]:.2f}<br>" +
                         f"High: ${high_values[i]:.2f}<br>" +
                         "<extra></extra>"
        ))

    # Add vertical line for current market price
    fig.add_vline(
        x=market_price,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Market: ${market_price:.2f}",
        annotation_position="top"
    )

    fig.update_layout(
        title="Football Field Valuation Chart",
        xaxis_title="Value per Share ($)",
        showlegend=False,
        height=400,
        template="plotly_white",
        barmode='overlay'
    )

    return fig


def create_sensitivity_heatmap(
    value_matrix: np.ndarray,
    wacc_values: List[float],
    tg_values: List[float],
    current_price: float
) -> go.Figure:
    """
    Create a heatmap showing sensitivity of valuation to WACC and Terminal Growth
    """
    # Create labels with percentage formatting
    wacc_labels = [f"{w:.1%}" for w in wacc_values]
    tg_labels = [f"{tg:.1%}" for tg in tg_values]

    # Create custom colorscale based on relation to current price
    # Green = above current price, Red = below current price

    fig = go.Figure(data=go.Heatmap(
        z=value_matrix,
        x=tg_labels,
        y=wacc_labels,
        colorscale='RdYlGn',
        text=np.round(value_matrix, 2),
        texttemplate='$%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Value per Share ($)")
    ))

    fig.update_layout(
        title="Sensitivity Analysis: WACC vs Terminal Growth Rate",
        xaxis_title="Terminal Growth Rate",
        yaxis_title="WACC (Discount Rate)",
        height=500,
        template="plotly_white"
    )

    # Add annotation for current price reference
    fig.add_annotation(
        text=f"Current Market Price: ${current_price:.2f}",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=12, color="black"),
        bgcolor="rgba(255,255,255,0.8)"
    )

    return fig


def create_monte_carlo_distribution(mc_results: Dict[str, any], current_price: float) -> go.Figure:
    """
    Create histogram of Monte Carlo simulation results with key statistics
    """
    distribution = mc_results.get('distribution', [])

    if not distribution:
        return go.Figure()

    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=distribution,
        nbinsx=50,
        name='Simulated Values',
        marker_color='rgba(55, 128, 191, 0.7)',
        hovertemplate='Value: $%{x:.2f}<br>Count: %{y}<extra></extra>'
    ))

    # Add vertical lines for key percentiles
    percentiles = [
        (mc_results.get('p10', 0), 'P10', 'red'),
        (mc_results.get('p25', 0), 'P25', 'orange'),
        (mc_results.get('median', 0), 'Median', 'blue'),
        (mc_results.get('p75', 0), 'P75', 'orange'),
        (mc_results.get('p90', 0), 'P90', 'red'),
    ]

    for value, label, color in percentiles:
        fig.add_vline(
            x=value,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{label}: ${value:.2f}",
            annotation_position="top"
        )

    # Add current market price
    fig.add_vline(
        x=current_price,
        line_dash="solid",
        line_color="green",
        line_width=2,
        annotation_text=f"Market: ${current_price:.2f}",
        annotation_position="bottom"
    )

    fig.update_layout(
        title=f"Monte Carlo Simulation Results ({len(distribution):,} simulations)",
        xaxis_title="Value per Share ($)",
        yaxis_title="Frequency",
        height=500,
        template="plotly_white",
        showlegend=False
    )

    return fig


def create_fcf_projection_chart(intermediates: dict) -> go.Figure:
    """
    Create line chart showing FCF projections over time with breakdown
    """
    if not intermediates:
        return go.Figure()

    fcf_forecast = intermediates.get('fcf_forecast', [])
    revenue_forecast = intermediates.get('revenue_forecast', [])
    nopat_forecast = intermediates.get('nopat_forecast', [])
    capex_forecast = intermediates.get('capex_forecast', [])

    years = list(range(1, len(fcf_forecast) + 1))

    fig = go.Figure()

    # FCF line
    fig.add_trace(go.Scatter(
        x=years,
        y=fcf_forecast,
        mode='lines+markers',
        name='Free Cash Flow',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))

    # NOPAT line
    fig.add_trace(go.Scatter(
        x=years,
        y=nopat_forecast,
        mode='lines+markers',
        name='NOPAT',
        line=dict(color='blue', width=2, dash='dash'),
        marker=dict(size=6)
    ))

    # CapEx line (negative for visual clarity)
    fig.add_trace(go.Scatter(
        x=years,
        y=[-c for c in capex_forecast],
        mode='lines+markers',
        name='CapEx (negative)',
        line=dict(color='red', width=2, dash='dot'),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title="Free Cash Flow Projection (5-Year Forecast)",
        xaxis_title="Year",
        yaxis_title="Value ($)",
        height=500,
        template="plotly_white",
        hovermode='x unified'
    )

    return fig