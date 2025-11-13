import dataclasses
from datetime import datetime

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
    
def calculate_dcf(inputs: DCFInputs):
    """Calculates discounted cash flow valuation."""
    try:
        if inputs.shares_outstanding <= 0:
            return 0, {}
        
        # Placeholder for a more complete FCF calculation logic
        # In a real scenario, this would involve projecting revenue, EBIT, NOPAT, reinvestment, and then FCF.
        # This simplified version generates arbitrary FCFs for demonstration.
        
        projection_years = len(inputs.revenue_growth_rates)
        
        # Simple FCF projection for the sake of completing the function
        fcf_forecast = []
        current_revenue = inputs.current_revenue
        for i in range(projection_years):
            current_revenue *= (1 + inputs.revenue_growth_rates[i])
            ebit = current_revenue * inputs.ebit_margin
            nopat = ebit * (1 - inputs.tax_rate)
            depreciation = current_revenue * inputs.depreciation_as_pct_revenue
            capex = current_revenue * inputs.capex_as_pct_revenue
            
            # Simplified NWC change, assume NWC increases with revenue
            # In a real model, delta NWC would be more detailed
            nwc_change = current_revenue * inputs.nwc_as_pct_revenue - (inputs.current_revenue * inputs.nwc_as_pct_revenue if i == 0 else fcf_forecast[-1] * inputs.nwc_as_pct_revenue)
            
            # FCF = NOPAT + Depreciation - Capex - Change in NWC
            fcf = nopat + depreciation - capex - nwc_change
            fcf_forecast.append(max(0, fcf)) # Ensure FCF is not negative for simplicity
            
        terminal_value = 0
        if (inputs.wacc - inputs.terminal_growth_rate) > 0 and len(fcf_forecast) > 0:
            terminal_fcf = fcf_forecast[-1] * (1 + inputs.terminal_growth_rate)
            terminal_value = terminal_fcf / (inputs.wacc - inputs.terminal_growth_rate)
        
        # 58>
        discounted_fcf = [val / (1 + inputs.wacc)**(i + 1) for i, val in enumerate(fcf_forecast)]
        
        # 60>
        discounted_terminal_value = terminal_value / (1 + inputs.wacc)**projection_years
        
        # 62>
        enterprise_value = sum(discounted_fcf) + discounted_terminal_value
        
        # 64>
        equity_value = enterprise_value + inputs.cash - inputs.total_debt
        
        # 66>
        value_per_share = equity_value / inputs.shares_outstanding if inputs.shares_outstanding > 0 else 0
            
        # 68>
        intermediates = {
            "fcf_forecast": fcf_forecast, "terminal_value": terminal_value,
            "discounted_fcf": discounted_fcf, "discounted_tv": discounted_terminal_value,
            "enterprise_value": enterprise_value, "equity_value": equity_value, "projection_years": projection_years
        }
            
        # 74>
        return value_per_share, intermediates
        
    # 76>
    except (TypeError, OverflowError, ZeroDivisionError) as e: # Added ZeroDivisionError handling
        return 0, {}

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