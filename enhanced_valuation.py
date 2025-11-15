"""
Enhanced Valuation Module
Interactive DCF calculator with Monte Carlo simulation
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import logging
# Migrated to use centralized constants
from src.core.constants import (
    RISK_FREE_RATE,
    MARKET_RISK_PREMIUM,
    TERMINAL_GROWTH_RATE,
    DEFAULT_WACC,
    DEFAULT_GROWTH_RATE,
    DEFAULT_PROJECTION_YEARS
)

logger = logging.getLogger(__name__)


class EnhancedDCFCalculator:
    """Enhanced DCF calculator with interactive parameters and Monte Carlo simulation"""
    
    def __init__(self):
        self.default_params = {
            'growth_rate': DEFAULT_GROWTH_RATE,
            'wacc': DEFAULT_WACC,
            'terminal_growth': TERMINAL_GROWTH_RATE,
            'projection_years': DEFAULT_PROJECTION_YEARS,
            'risk_free_rate': RISK_FREE_RATE,
            'market_risk_premium': MARKET_RISK_PREMIUM
        }
    
    def calculate_dcf_detailed(
        self,
        base_cash_flow: float,
        growth_rate: float,
        wacc: float,
        terminal_growth: float,
        projection_years: int,
        cash: float = 0,
        debt: float = 0,
        shares_outstanding: float = 1
    ) -> Dict:
        """
        Calculate DCF with detailed breakdown of all intermediate steps
        
        Args:
            base_cash_flow: Current or average historical free cash flow
            growth_rate: Annual growth rate for projection period (e.g., 0.10 for 10%)
            wacc: Weighted Average Cost of Capital (discount rate)
            terminal_growth: Perpetual growth rate after projection period
            projection_years: Number of years to project (typically 3-10)
            cash: Cash and cash equivalents
            debt: Total debt
            shares_outstanding: Number of shares outstanding
            
        Returns:
            Dictionary with detailed DCF calculation results
        """
        try:
            # Enhanced input validation
            if shares_outstanding <= 0:
                return {"error": "Shares outstanding must be positive"}
            if wacc <= 0 or wacc > 0.5:
                return {"error": "WACC must be between 0% and 50%"}
            if wacc <= terminal_growth:
                return {"error": "WACC must be greater than terminal growth rate"}
            if terminal_growth < 0 or terminal_growth > 0.1:
                return {"error": "Terminal growth must be between 0% and 10%"}
            if base_cash_flow == 0:
                return {"error": "Base cash flow cannot be zero"}
            if growth_rate < -0.5 or growth_rate > 1.0:
                return {"error": "Growth rate must be between -50% and 100%"}
            if projection_years < 1 or projection_years > 20:
                return {"error": "Projection years must be between 1 and 20"}
            
            # Project future cash flows
            projected_cfs = []
            pv_cfs = []
            
            for year in range(1, projection_years + 1):
                # Projected cash flow for this year
                cf = base_cash_flow * (1 + growth_rate) ** year
                # Present value of this cash flow
                pv = cf / (1 + wacc) ** year
                
                projected_cfs.append({
                    'year': year,
                    'cash_flow': cf,
                    'discount_factor': 1 / (1 + wacc) ** year,
                    'present_value': pv
                })
                pv_cfs.append(pv)
            
            # Calculate terminal value
            terminal_cf = base_cash_flow * (1 + growth_rate) ** projection_years * (1 + terminal_growth)
            terminal_value = terminal_cf / (wacc - terminal_growth)
            pv_terminal = terminal_value / (1 + wacc) ** projection_years
            
            # Enterprise value
            enterprise_value = sum(pv_cfs) + pv_terminal
            
            # Equity value
            equity_value = enterprise_value + cash - debt
            
            # Fair value per share
            fair_value_per_share = equity_value / shares_outstanding
            
            return {
                'fair_value_per_share': fair_value_per_share,
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'pv_projected_cfs': sum(pv_cfs),
                'pv_terminal_value': pv_terminal,
                'terminal_value': terminal_value,
                'terminal_cf': terminal_cf,
                'projected_cash_flows': projected_cfs,
                'inputs': {
                    'base_cash_flow': base_cash_flow,
                    'growth_rate': growth_rate,
                    'wacc': wacc,
                    'terminal_growth': terminal_growth,
                    'projection_years': projection_years,
                    'cash': cash,
                    'debt': debt,
                    'shares_outstanding': shares_outstanding
                }
            }
        
        except Exception as e:
            logger.error(f"Error in DCF calculation: {e}")
            return {"error": str(e)}
    
    def monte_carlo_dcf(
        self,
        base_cash_flow: float,
        growth_rate_mean: float,
        growth_rate_std: float,
        wacc_mean: float,
        wacc_std: float,
        terminal_growth_mean: float,
        terminal_growth_std: float,
        projection_years: int,
        cash: float,
        debt: float,
        shares_outstanding: float,
        num_simulations: int = 1000
    ) -> Dict:
        """
        Run Monte Carlo simulation for DCF valuation
        
        Args:
            base_cash_flow: Base free cash flow
            growth_rate_mean: Mean growth rate
            growth_rate_std: Standard deviation of growth rate
            wacc_mean: Mean WACC
            wacc_std: Standard deviation of WACC
            terminal_growth_mean: Mean terminal growth
            terminal_growth_std: Standard deviation of terminal growth
            projection_years: Number of projection years
            cash: Cash on hand
            debt: Total debt
            shares_outstanding: Shares outstanding
            num_simulations: Number of Monte Carlo iterations
            
        Returns:
            Dictionary with simulation results and statistics
        """
        try:
            fair_values = []
            enterprise_values = []
            
            for _ in range(num_simulations):
                # Sample parameters from normal distributions
                growth_rate = np.random.normal(growth_rate_mean, growth_rate_std)
                wacc = np.random.normal(wacc_mean, wacc_std)
                terminal_growth = np.random.normal(terminal_growth_mean, terminal_growth_std)
                
                # Ensure valid ranges
                growth_rate = max(0, min(0.5, growth_rate))  # 0-50%
                wacc = max(0.05, min(0.25, wacc))  # 5-25%
                terminal_growth = max(0, min(0.05, terminal_growth))  # 0-5%
                
                # Skip if wacc <= terminal_growth
                if wacc <= terminal_growth:
                    continue
                
                # Calculate DCF for this simulation
                result = self.calculate_dcf_detailed(
                    base_cash_flow=base_cash_flow,
                    growth_rate=growth_rate,
                    wacc=wacc,
                    terminal_growth=terminal_growth,
                    projection_years=projection_years,
                    cash=cash,
                    debt=debt,
                    shares_outstanding=shares_outstanding
                )
                
                if "error" not in result:
                    fair_values.append(result['fair_value_per_share'])
                    enterprise_values.append(result['enterprise_value'])
            
            if len(fair_values) == 0:
                return {"error": "No valid simulations completed"}
            
            # Calculate statistics
            fair_values = np.array(fair_values)
            enterprise_values = np.array(enterprise_values)
            
            # Percentiles for confidence intervals
            percentiles = [5, 10, 25, 50, 75, 90, 95]
            fair_value_percentiles = {
                f"p{p}": np.percentile(fair_values, p)
                for p in percentiles
            }
            
            return {
                'fair_value_mean': np.mean(fair_values),
                'fair_value_median': np.median(fair_values),
                'fair_value_std': np.std(fair_values),
                'fair_value_min': np.min(fair_values),
                'fair_value_max': np.max(fair_values),
                'fair_value_percentiles': fair_value_percentiles,
                'enterprise_value_mean': np.mean(enterprise_values),
                'enterprise_value_median': np.median(enterprise_values),
                'all_fair_values': fair_values.tolist(),
                'all_enterprise_values': enterprise_values.tolist(),
                'num_successful_simulations': len(fair_values),
                'confidence_intervals': {
                    '50%': (fair_value_percentiles['p25'], fair_value_percentiles['p75']),
                    '80%': (fair_value_percentiles['p10'], fair_value_percentiles['p90']),
                    '90%': (fair_value_percentiles['p5'], fair_value_percentiles['p95'])
                }
            }
        
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {"error": str(e)}
    
    def sensitivity_analysis(
        self,
        base_cash_flow: float,
        base_growth_rate: float,
        base_wacc: float,
        terminal_growth: float,
        projection_years: int,
        cash: float,
        debt: float,
        shares_outstanding: float,
        param_name: str,
        param_range: List[float]
    ) -> Dict:
        """
        Perform sensitivity analysis by varying one parameter
        
        Args:
            base_cash_flow: Base cash flow
            base_growth_rate: Base growth rate
            base_wacc: Base WACC
            terminal_growth: Terminal growth rate
            projection_years: Projection years
            cash: Cash on hand
            debt: Total debt
            shares_outstanding: Shares outstanding
            param_name: Name of parameter to vary ('growth_rate', 'wacc', 'terminal_growth')
            param_range: Range of values to test for the parameter
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        try:
            results = []
            
            for param_value in param_range:
                # Set parameters
                if param_name == 'growth_rate':
                    growth_rate = param_value
                    wacc = base_wacc
                    term_growth = terminal_growth
                elif param_name == 'wacc':
                    growth_rate = base_growth_rate
                    wacc = param_value
                    term_growth = terminal_growth
                elif param_name == 'terminal_growth':
                    growth_rate = base_growth_rate
                    wacc = base_wacc
                    term_growth = param_value
                else:
                    continue
                
                # Calculate DCF
                result = self.calculate_dcf_detailed(
                    base_cash_flow=base_cash_flow,
                    growth_rate=growth_rate,
                    wacc=wacc,
                    terminal_growth=term_growth,
                    projection_years=projection_years,
                    cash=cash,
                    debt=debt,
                    shares_outstanding=shares_outstanding
                )
                
                if "error" not in result:
                    results.append({
                        'param_value': param_value,
                        'fair_value': result['fair_value_per_share'],
                        'enterprise_value': result['enterprise_value']
                    })
            
            return {
                'param_name': param_name,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Error in sensitivity analysis: {e}")
            return {"error": str(e)}
    
    def two_way_sensitivity(
        self,
        base_cash_flow: float,
        growth_rates: List[float],
        waccs: List[float],
        terminal_growth: float,
        projection_years: int,
        cash: float,
        debt: float,
        shares_outstanding: float
    ) -> pd.DataFrame:
        """
        Perform two-way sensitivity analysis (growth rate vs WACC)
        
        Returns:
            DataFrame with fair values for each combination
        """
        try:
            results = []
            
            for growth_rate in growth_rates:
                row = []
                for wacc in waccs:
                    result = self.calculate_dcf_detailed(
                        base_cash_flow=base_cash_flow,
                        growth_rate=growth_rate,
                        wacc=wacc,
                        terminal_growth=terminal_growth,
                        projection_years=projection_years,
                        cash=cash,
                        debt=debt,
                        shares_outstanding=shares_outstanding
                    )
                    
                    if "error" not in result:
                        row.append(result['fair_value_per_share'])
                    else:
                        row.append(np.nan)
                
                results.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(
                results,
                index=[f"{g*100:.1f}%" for g in growth_rates],
                columns=[f"{w*100:.1f}%" for w in waccs]
            )
            df.index.name = "Growth Rate"
            df.columns.name = "WACC"
            
            return df
        
        except Exception as e:
            logger.error(f"Error in two-way sensitivity: {e}")
            return pd.DataFrame()


def get_enhanced_dcf_calculator():
    """Factory function to get EnhancedDCFCalculator instance"""
    return EnhancedDCFCalculator()

