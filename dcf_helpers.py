"""
DCF Helper Functions for Smart Input Recommendations
Helps users estimate optimal DCF input variables based on company fundamentals
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional


def calculate_historical_growth_rates(income_data: pd.DataFrame, periods: int = 5) -> Dict[str, float]:
    """
    Calculate historical revenue and earnings growth rates
    Returns CAGR and recent trends
    """
    if income_data.empty or len(income_data) < 2:
        return {'revenue_cagr': 0.10, 'earnings_cagr': 0.10, 'recent_revenue_growth': 0.10}

    try:
        # Get revenue data (most recent first in yfinance)
        revenue_row = income_data.loc['Total Revenue'] if 'Total Revenue' in income_data.index else None

        if revenue_row is None or len(revenue_row) < 2:
            return {'revenue_cagr': 0.10, 'earnings_cagr': 0.10, 'recent_revenue_growth': 0.10}

        # Calculate CAGR (Compound Annual Growth Rate)
        # CAGR = (Ending Value / Beginning Value)^(1/years) - 1
        years = min(len(revenue_row) - 1, periods)

        if years > 0 and revenue_row.iloc[0] > 0 and revenue_row.iloc[years] > 0:
            revenue_cagr = (revenue_row.iloc[0] / revenue_row.iloc[years]) ** (1/years) - 1
        else:
            revenue_cagr = 0.10

        # Recent growth (YoY)
        if len(revenue_row) >= 2 and revenue_row.iloc[1] > 0:
            recent_revenue_growth = (revenue_row.iloc[0] / revenue_row.iloc[1]) - 1
        else:
            recent_revenue_growth = revenue_cagr

        # Get earnings growth if available
        net_income_row = income_data.loc['Net Income'] if 'Net Income' in income_data.index else None

        if net_income_row is not None and len(net_income_row) >= 2:
            if net_income_row.iloc[0] > 0 and net_income_row.iloc[min(years, len(net_income_row)-1)] > 0:
                earnings_cagr = (net_income_row.iloc[0] / net_income_row.iloc[min(years, len(net_income_row)-1)]) ** (1/years) - 1
            else:
                earnings_cagr = revenue_cagr
        else:
            earnings_cagr = revenue_cagr

        # Cap at reasonable limits
        revenue_cagr = max(-0.5, min(1.0, revenue_cagr))
        earnings_cagr = max(-0.5, min(1.0, earnings_cagr))
        recent_revenue_growth = max(-0.5, min(1.0, recent_revenue_growth))

        return {
            'revenue_cagr': revenue_cagr,
            'earnings_cagr': earnings_cagr,
            'recent_revenue_growth': recent_revenue_growth
        }

    except Exception as e:
        return {'revenue_cagr': 0.10, 'earnings_cagr': 0.10, 'recent_revenue_growth': 0.10}


def estimate_roic(info: dict, balance_sheet: pd.DataFrame, income_data: pd.DataFrame) -> float:
    """
    Estimate Return on Invested Capital
    ROIC = NOPAT / Invested Capital
    Where Invested Capital = Total Debt + Total Equity - Cash
    """
    try:
        # Try to get from info first
        roe = info.get('returnOnEquity', None)
        if roe and roe > 0:
            # ROIC is typically close to ROE for companies with low debt
            debt_to_equity = info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0
            if debt_to_equity < 0.5:
                return roe * 0.9  # Slight adjustment

        # Calculate from financial statements
        if not income_data.empty and not balance_sheet.empty:
            # Get EBIT
            ebit = income_data.loc['EBIT'].iloc[0] if 'EBIT' in income_data.index else None
            if ebit is None or ebit <= 0:
                operating_income = income_data.loc['Operating Income'].iloc[0] if 'Operating Income' in income_data.index else None
                ebit = operating_income if operating_income else None

            # Get Invested Capital
            total_debt = balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in balance_sheet.index else 0
            total_equity = balance_sheet.loc['Stockholders Equity'].iloc[0] if 'Stockholders Equity' in balance_sheet.index else None
            cash = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0] if 'Cash And Cash Equivalents' in balance_sheet.index else 0

            if ebit and total_equity and total_equity > 0:
                # NOPAT = EBIT * (1 - tax rate)
                tax_rate = 0.21  # Assume 21% corporate tax
                nopat = ebit * (1 - tax_rate)

                # Invested Capital
                invested_capital = total_debt + total_equity - cash

                if invested_capital > 0:
                    roic = nopat / invested_capital
                    return max(0.01, min(0.50, roic))  # Cap between 1% and 50%

        # Default: Use industry average
        return 0.15  # 15% is a reasonable default

    except Exception:
        return 0.15


def get_industry_benchmarks(sector: str) -> Dict[str, float]:
    """
    Get industry-specific benchmark metrics
    Based on typical sector characteristics
    """
    benchmarks = {
        'Technology': {
            'growth_rate': 0.15,
            'ebit_margin': 0.25,
            'capex_pct': 0.05,
            'nwc_pct': 0.10,
            'terminal_growth': 0.03,
            'roic': 0.20
        },
        'Healthcare': {
            'growth_rate': 0.12,
            'ebit_margin': 0.20,
            'capex_pct': 0.06,
            'nwc_pct': 0.15,
            'terminal_growth': 0.03,
            'roic': 0.18
        },
        'Consumer Cyclical': {
            'growth_rate': 0.08,
            'ebit_margin': 0.12,
            'capex_pct': 0.08,
            'nwc_pct': 0.12,
            'terminal_growth': 0.025,
            'roic': 0.12
        },
        'Consumer Defensive': {
            'growth_rate': 0.06,
            'ebit_margin': 0.10,
            'capex_pct': 0.06,
            'nwc_pct': 0.08,
            'terminal_growth': 0.025,
            'roic': 0.15
        },
        'Financial Services': {
            'growth_rate': 0.10,
            'ebit_margin': 0.25,
            'capex_pct': 0.03,
            'nwc_pct': 0.05,
            'terminal_growth': 0.03,
            'roic': 0.12
        },
        'Industrials': {
            'growth_rate': 0.08,
            'ebit_margin': 0.12,
            'capex_pct': 0.10,
            'nwc_pct': 0.10,
            'terminal_growth': 0.025,
            'roic': 0.14
        },
        'Energy': {
            'growth_rate': 0.05,
            'ebit_margin': 0.15,
            'capex_pct': 0.15,
            'nwc_pct': 0.08,
            'terminal_growth': 0.02,
            'roic': 0.10
        },
        'Utilities': {
            'growth_rate': 0.04,
            'ebit_margin': 0.18,
            'capex_pct': 0.12,
            'nwc_pct': 0.05,
            'terminal_growth': 0.02,
            'roic': 0.08
        },
        'Real Estate': {
            'growth_rate': 0.06,
            'ebit_margin': 0.30,
            'capex_pct': 0.08,
            'nwc_pct': 0.05,
            'terminal_growth': 0.025,
            'roic': 0.10
        },
        'Communication Services': {
            'growth_rate': 0.10,
            'ebit_margin': 0.20,
            'capex_pct': 0.08,
            'nwc_pct': 0.08,
            'terminal_growth': 0.03,
            'roic': 0.15
        },
        'Basic Materials': {
            'growth_rate': 0.06,
            'ebit_margin': 0.12,
            'capex_pct': 0.12,
            'nwc_pct': 0.10,
            'terminal_growth': 0.025,
            'roic': 0.12
        }
    }

    # Default if sector not found
    default = {
        'growth_rate': 0.08,
        'ebit_margin': 0.15,
        'capex_pct': 0.08,
        'nwc_pct': 0.10,
        'terminal_growth': 0.025,
        'roic': 0.12
    }

    return benchmarks.get(sector, default)


def generate_smart_growth_forecast(
    historical_growth: Dict[str, float],
    industry_growth: float,
    market_cap: float,
    projection_years: int = 5
) -> list[float]:
    """
    Generate intelligent growth rate forecast with fade logic
    Larger companies typically have slower growth
    Growth fades toward industry average over time
    """
    # Start with recent growth, but adjust for company size
    recent_growth = historical_growth.get('recent_revenue_growth', 0.10)
    cagr = historical_growth.get('revenue_cagr', 0.10)

    # Size adjustment (smaller companies can grow faster)
    if market_cap < 2e9:  # < $2B (small cap)
        size_multiplier = 1.2
    elif market_cap < 10e9:  # < $10B (mid cap)
        size_multiplier = 1.1
    elif market_cap < 200e9:  # < $200B (large cap)
        size_multiplier = 1.0
    else:  # Mega cap
        size_multiplier = 0.8

    # Blend recent growth with historical CAGR (70% recent, 30% CAGR)
    starting_growth = (recent_growth * 0.7 + cagr * 0.3) * size_multiplier
    starting_growth = max(-0.2, min(0.5, starting_growth))  # Cap at -20% to +50%

    # Fade to industry growth over projection period
    growth_rates = []
    for year in range(projection_years):
        fade_factor = year / (projection_years - 1) if projection_years > 1 else 1
        growth = starting_growth * (1 - fade_factor) + industry_growth * fade_factor
        growth_rates.append(growth)

    return growth_rates


def estimate_cost_of_debt(info: dict) -> float:
    """
    Estimate cost of debt based on company fundamentals
    """
    # Try to get interest expense / total debt
    interest_expense = info.get('interestExpense', None)
    total_debt = info.get('totalDebt', None)

    if interest_expense and total_debt and total_debt > 0 and interest_expense < 0:
        cost_of_debt = abs(interest_expense) / total_debt
        return max(0.02, min(0.20, cost_of_debt))  # Between 2% and 20%

    # Use credit rating proxy based on interest coverage
    ebit = info.get('ebit', None)
    if ebit and interest_expense and interest_expense < 0:
        interest_coverage = ebit / abs(interest_expense)

        # Credit rating approximation
        if interest_coverage > 8:  # AAA/AA
            return 0.04
        elif interest_coverage > 6:  # A
            return 0.05
        elif interest_coverage > 4:  # BBB
            return 0.06
        elif interest_coverage > 2.5:  # BB
            return 0.08
        elif interest_coverage > 1.5:  # B
            return 0.10
        else:  # CCC or lower
            return 0.15

    # Default to reasonable corporate bond rate
    return 0.06


def get_smart_dcf_recommendations(
    info: dict,
    income_data: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cash_flow: pd.DataFrame,
    market_price: float
) -> Dict[str, any]:
    """
    Generate comprehensive smart recommendations for all DCF inputs
    """
    # Get basic info
    sector = info.get('sector', 'Unknown')
    market_cap = info.get('marketCap', 10e9)

    # Historical growth
    historical_growth = calculate_historical_growth_rates(income_data)

    # Industry benchmarks
    industry = get_industry_benchmarks(sector)

    # Smart growth forecast
    growth_rates = generate_smart_growth_forecast(
        historical_growth,
        industry['growth_rate'],
        market_cap,
        projection_years=5
    )

    # EBIT margin (use actual or industry)
    actual_margin = info.get('operatingMargins', None)
    ebit_margin = actual_margin if actual_margin and actual_margin > 0 else industry['ebit_margin']

    # Terminal margin (fade to industry average)
    terminal_margin = industry['ebit_margin'] * 0.9  # Slightly below industry for conservatism

    # ROIC
    roic = estimate_roic(info, balance_sheet, income_data)

    # Cost of debt
    cost_of_debt = estimate_cost_of_debt(info)

    # Risk-free rate (use current 10-year Treasury as proxy)
    risk_free_rate = 0.045  # Update this based on current rates

    # Beta
    beta = info.get('beta', 1.0)
    beta = max(0.5, min(2.5, beta)) if beta else 1.0  # Reasonable bounds

    # Market risk premium (historical average)
    market_risk_premium = 0.07

    # Terminal growth (GDP growth + inflation)
    terminal_growth = industry['terminal_growth']

    # CapEx and NWC
    capex_pct = industry['capex_pct']
    nwc_pct = industry['nwc_pct']

    # Depreciation
    depreciation_pct = 0.03  # Typical 3% of revenue

    # Stock-based compensation (higher for tech)
    if sector in ['Technology', 'Communication Services']:
        sbc_pct = 0.03
    else:
        sbc_pct = 0.01

    return {
        'growth_rates': growth_rates,
        'ebit_margin': ebit_margin,
        'terminal_margin': terminal_margin,
        'roic': roic,
        'cost_of_debt': cost_of_debt,
        'risk_free_rate': risk_free_rate,
        'beta': beta,
        'market_risk_premium': market_risk_premium,
        'terminal_growth': terminal_growth,
        'capex_pct': capex_pct,
        'nwc_pct': nwc_pct,
        'depreciation_pct': depreciation_pct,
        'sbc_pct': sbc_pct,
        'fade_years': 5,
        'tax_rate': 0.21,
        'sector': sector,
        'historical_revenue_cagr': historical_growth['revenue_cagr'],
        'recent_revenue_growth': historical_growth['recent_revenue_growth'],
        'industry_benchmarks': industry,
        'confidence_notes': _generate_confidence_notes(
            historical_growth,
            industry,
            sector,
            market_cap,
            info
        )
    }


def _generate_confidence_notes(
    historical_growth: Dict[str, float],
    industry: Dict[str, float],
    sector: str,
    market_cap: float,
    info: dict
) -> Dict[str, str]:
    """
    Generate confidence notes explaining the recommendations
    """
    notes = {}

    # Growth confidence
    cagr = historical_growth['revenue_cagr']
    recent = historical_growth['recent_revenue_growth']

    if abs(cagr - recent) < 0.03:
        notes['growth'] = f"✓ Consistent growth ({cagr:.1%} CAGR matches recent trends)"
    elif recent > cagr * 1.5:
        notes['growth'] = f"⚠ Accelerating growth (recent {recent:.1%} vs {cagr:.1%} CAGR) - may not sustain"
    elif recent < cagr * 0.5:
        notes['growth'] = f"⚠ Slowing growth (recent {recent:.1%} vs {cagr:.1%} CAGR) - conservative forecast"
    else:
        notes['growth'] = f"~ Moderate variance (recent {recent:.1%} vs {cagr:.1%} CAGR)"

    # Size impact
    if market_cap < 2e9:
        notes['size'] = "✓ Small cap - higher growth potential, but higher risk"
    elif market_cap > 200e9:
        notes['size'] = "⚠ Mega cap - limited growth runway, mature company"
    else:
        notes['size'] = "✓ Mid/Large cap - balanced growth expectations"

    # Margin confidence
    actual_margin = info.get('operatingMargins', None)
    if actual_margin:
        if actual_margin > industry['ebit_margin'] * 1.2:
            notes['margins'] = f"✓ Premium margins ({actual_margin:.1%} vs {industry['ebit_margin']:.1%} industry avg)"
        elif actual_margin < industry['ebit_margin'] * 0.8:
            notes['margins'] = f"⚠ Below-average margins ({actual_margin:.1%} vs {industry['ebit_margin']:.1%} industry avg)"
        else:
            notes['margins'] = f"✓ In-line with industry ({actual_margin:.1%} vs {industry['ebit_margin']:.1%} avg)"
    else:
        notes['margins'] = f"~ Using {sector} industry average ({industry['ebit_margin']:.1%})"

    return notes
