"""
Analysis Engine - Valuation, Technical Analysis, and Buy Signal Detection
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple, List
import ta
import logging
from zero_fcf_valuation import ZeroFCFValuationEngine
# Migrated to use centralized constants
from src.core.constants import (
    RISK_FREE_RATE,
    MARKET_RISK_PREMIUM,
    TERMINAL_GROWTH_RATE,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT
)

logger = logging.getLogger(__name__)

class ValuationEngine:
    """Handles all valuation calculations with auto-selection for Zero-FCF companies"""
    
    def __init__(self):
        self.risk_free_rate = RISK_FREE_RATE  # 10Y Treasury
        self.market_risk_premium = MARKET_RISK_PREMIUM
        self.terminal_growth = TERMINAL_GROWTH_RATE
        self.zero_fcf_engine = ZeroFCFValuationEngine()
    
    def calculate_valuation(self, financials: Dict, info: Dict) -> Dict:
        """
        Auto-select best valuation method based on company characteristics.
        Tries traditional DCF first, falls back to Zero-FCF methods if needed.
        """
        try:
            # Check if company has positive, consistent FCF
            has_positive_fcf = self._check_fcf_availability(financials, info)
            
            if has_positive_fcf:
                # Try traditional DCF
                dcf_result = self.calculate_dcf(financials, info)
                if "error" not in dcf_result:
                    dcf_result["valuation_type"] = "Traditional DCF"
                    return dcf_result
            
            # Fall back to Zero-FCF methods
            logger.info("Using Zero-FCF valuation methods")
            zero_fcf_result = self.zero_fcf_engine.calculate_comprehensive_valuation(info, financials)
            
            if "error" not in zero_fcf_result:
                zero_fcf_result["valuation_type"] = "Zero-FCF Multi-Method"
                return zero_fcf_result
            
            # Final fallback: multiples valuation
            multiples_result = self.calculate_multiples_valuation(info)
            if "error" not in multiples_result:
                multiples_result["valuation_type"] = "Multiples-Based"
                return multiples_result
            
            return {
                "error": "Unable to calculate valuation with available data",
                "recommendation": "More financial data needed for accurate valuation"
            }
            
        except Exception as e:
            logger.error(f"Error in auto valuation: {e}")
            return {"error": str(e)}
    
    def _check_fcf_availability(self, financials: Dict, info: Dict) -> bool:
        """Check if company has consistent positive free cash flow."""
        try:
            if "cash_flow" in financials and financials.get("cash_flow"):
                cf_data = pd.DataFrame(financials["cash_flow"])
                if not cf_data.empty and "Free Cash Flow" in cf_data.index:
                    fcf_values = cf_data.loc["Free Cash Flow"].values[:4]
                    
                    # Check if majority of recent FCF is positive
                    positive_count = sum(1 for fcf in fcf_values if fcf > 0)
                    return positive_count >= 2  # At least 2 out of 4 years positive
            
            return False
        except Exception as e:
            logger.debug(f"Error checking FCF: {e}")
            return False
    
    def calculate_dcf(self, financials: Dict, info: Dict) -> Dict:
        """Calculate Discounted Cash Flow valuation"""
        try:
            # Extract key metrics
            beta = info.get("beta", 1.0)
            shares = info.get("sharesOutstanding", 0)
            
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            # Calculate WACC
            wacc = self.risk_free_rate + beta * self.market_risk_premium
            
            # Get cash flows (simplified - using net income as proxy)
            cash_flows = []
            if "cash_flow" in financials and financials.get("cash_flow"):
                try:
                    cf_data = pd.DataFrame(financials["cash_flow"])
                    if not cf_data.empty:
                        if "Free Cash Flow" in cf_data.index:
                            cash_flows = cf_data.loc["Free Cash Flow"].values[:4]
                        elif "Operating Cash Flow" in cf_data.index:
                            cash_flows = cf_data.loc["Operating Cash Flow"].values[:4]
                except Exception as e:
                    logger.error(f"Error parsing cash flow data: {e}")
            
            if len(cash_flows) == 0 or not any(cash_flows):
                return {"error": "No cash flow data available"}
            
            # Project future cash flows
            avg_cf = np.mean(cash_flows)
            growth_rate = 0.10  # Assumed growth
            
            # 5-year projection
            projected_cfs = []
            for year in range(1, 6):
                cf = avg_cf * (1 + growth_rate) ** year
                pv = cf / (1 + wacc) ** year
                projected_cfs.append(pv)
            
            # Terminal value
            terminal_cf = avg_cf * (1 + growth_rate) ** 5 * (1 + self.terminal_growth)
            terminal_value = terminal_cf / (wacc - self.terminal_growth)
            pv_terminal = terminal_value / (1 + wacc) ** 5
            
            # Enterprise value and equity value
            enterprise_value = sum(projected_cfs) + pv_terminal
            
            # Add cash, subtract debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Fair value per share
            fair_value = equity_value / shares
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            # Calculate scenarios
            scenarios = {
                "bear": fair_value * 0.8,
                "base": fair_value,
                "bull": fair_value * 1.2
            }
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "scenarios": scenarios,
                "wacc": wacc * 100,
                "enterprise_value": enterprise_value,
                "method": "DCF"
            }
            
        except Exception as e:
            logger.error(f"Error in DCF calculation: {e}")
            return {"error": str(e)}
    
    def calculate_multiples_valuation(self, info: Dict) -> Dict:
        """Calculate valuation based on multiples"""
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            valuations = {}
            
            # P/E Valuation
            pe_ratio = info.get("trailingPE", 0)
            forward_pe = info.get("forwardPE", 0)
            industry_pe = info.get("industryPE", 20)  # Default industry P/E
            
            if pe_ratio > 0 and forward_pe > 0:
                eps = current_price / pe_ratio
                fair_value_pe = eps * min(industry_pe, 25)  # Cap at 25 P/E
                valuations["P/E"] = {
                    "fair_value": fair_value_pe,
                    "current_ratio": pe_ratio,
                    "target_ratio": industry_pe
                }
            
            # P/B Valuation
            pb_ratio = info.get("priceToBook", 0)
            if pb_ratio > 0:
                book_value = current_price / pb_ratio
                fair_value_pb = book_value * 1.5  # Target 1.5x book
                valuations["P/B"] = {
                    "fair_value": fair_value_pb,
                    "current_ratio": pb_ratio,
                    "target_ratio": 1.5
                }
            
            # PEG Valuation
            peg_ratio = info.get("pegRatio", 0)
            if peg_ratio > 0 and peg_ratio < 2:
                # PEG under 1 is undervalued
                fair_value_peg = current_price * (1 / peg_ratio)
                valuations["PEG"] = {
                    "fair_value": fair_value_peg,
                    "current_ratio": peg_ratio,
                    "target_ratio": 1.0
                }
            
            # Average fair value
            if valuations:
                avg_fair_value = np.mean([v["fair_value"] for v in valuations.values()])
                return {
                    "fair_value": avg_fair_value,
                    "current_price": current_price,
                    "upside": ((avg_fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                    "valuations": valuations,
                    "method": "Multiples"
                }
            
            return {"error": "Insufficient data for multiples valuation"}
            
        except Exception as e:
            logger.error(f"Error in multiples valuation: {e}")
            return {"error": str(e)}
    
    def calculate_ddm(self, info: Dict) -> Dict:
        """Calculate Dividend Discount Model valuation"""
        try:
            dividend = info.get("dividendYield", 0)
            if dividend == 0:
                return {"error": "No dividend data available"}
            
            # Convert yield to annual dividend amount
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            annual_dividend = current_price * dividend
            
            # Estimate dividend growth rate from payout ratio and earnings growth
            payout_ratio = info.get("payoutRatio", 0.4)
            earnings_growth = info.get("earningsGrowth", 0.05)
            dividend_growth = earnings_growth * (1 - payout_ratio)
            
            # Gordon Growth Model: Price = D1 / (r - g)
            # where D1 = next year's dividend, r = required return, g = growth rate
            required_return = self.risk_free_rate + info.get("beta", 1.0) * self.market_risk_premium
            
            if required_return <= dividend_growth:
                return {"error": "Growth rate exceeds required return"}
            
            fair_value = annual_dividend * (1 + dividend_growth) / (required_return - dividend_growth)
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "dividend_yield": dividend * 100,
                "dividend_growth": dividend_growth * 100,
                "method": "DDM"
            }
            
        except Exception as e:
            logger.error(f"Error in DDM calculation: {e}")
            return {"error": str(e)}
    
    def calculate_nav(self, info: Dict, financials: Dict) -> Dict:
        """Calculate Net Asset Value"""
        try:
            # Get balance sheet data
            total_assets = info.get("totalAssets", 0)
            total_liabilities = info.get("totalLiabilities", 0)
            shares_outstanding = info.get("sharesOutstanding", 0)
            
            if shares_outstanding == 0:
                return {"error": "No shares outstanding data"}
            
            # Calculate book value
            book_value = total_assets - total_liabilities
            nav_per_share = book_value / shares_outstanding
            
            # Tangible book value (exclude intangibles)
            intangible_assets = info.get("intangibleAssets", 0)
            tangible_book_value = book_value - intangible_assets
            tangible_nav = tangible_book_value / shares_outstanding
            
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            return {
                "fair_value": nav_per_share,
                "tangible_nav": tangible_nav,
                "current_price": current_price,
                "upside": ((nav_per_share - current_price) / current_price * 100) if current_price > 0 else 0,
                "price_to_book": current_price / nav_per_share if nav_per_share > 0 else 0,
                "method": "NAV"
            }
            
        except Exception as e:
            logger.error(f"Error in NAV calculation: {e}")
            return {"error": str(e)}
    
    def calculate_reit_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Calculate REIT valuation using FFO (Funds From Operations)
        FFO = Net Income + Depreciation - Gains on Property Sales
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            shares = info.get("sharesOutstanding", 0)
            
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            # Get income statement data
            net_income = 0
            depreciation = 0
            
            if "income_statement" in financials:
                income_stmt = financials.get("income_statement")
                if income_stmt is not None:
                    try:
                        income_data = pd.DataFrame(income_stmt) if not isinstance(income_stmt, pd.DataFrame) else income_stmt
                        if not income_data.empty:
                            if "Net Income" in income_data.index:
                                net_income = income_data.loc["Net Income"].iloc[0]
                            
                            # Depreciation might be in cash flow statement
                            if "Depreciation And Amortization" in income_data.index:
                                depreciation = income_data.loc["Depreciation And Amortization"].iloc[0]
                    except Exception as e:
                        logger.error(f"Error parsing income statement: {e}")
            
            # Calculate FFO (simplified - ignoring property sale gains)
            ffo = net_income + depreciation
            ffo_per_share = ffo / shares if shares > 0 else 0
            
            # REIT valuation using FFO multiple
            # REITs typically trade at 12-18x FFO
            avg_reit_multiple = 15.0
            fair_value = ffo_per_share * avg_reit_multiple
            
            # Also calculate based on dividend yield
            dividend_yield = info.get("dividendYield", 0)
            if dividend_yield > 0:
                annual_dividend = current_price * dividend_yield
                # REITs should yield 3-6%, use 4.5% target
                target_yield = 0.045
                fair_value_yield = annual_dividend / target_yield
                fair_value = (fair_value + fair_value_yield) / 2  # Average both methods
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "ffo_per_share": ffo_per_share,
                "ffo_multiple": current_price / ffo_per_share if ffo_per_share > 0 else 0,
                "dividend_yield": dividend_yield * 100 if dividend_yield else 0,
                "method": "REIT (FFO)"
            }
            
        except Exception as e:
            logger.error(f"Error in REIT valuation: {e}")
            return {"error": str(e)}
    
    def calculate_revenue_multiple_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Calculate valuation using revenue multiples (for pre-revenue/high-growth companies)
        Common in SaaS, biotech, early-stage tech
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            # Get Price/Sales ratio
            price_to_sales = info.get("priceToSalesTrailing12Months", 0)
            
            if price_to_sales == 0:
                return {"error": "No revenue data available"}
            
            # Get revenue
            revenue_per_share = current_price / price_to_sales if price_to_sales > 0 else 0
            
            # Industry-specific multiples
            sector = info.get("sector", "Technology")
            
            # Typical P/S multiples by sector
            target_multiples = {
                "Technology": 5.0,
                "Healthcare": 3.5,
                "Communication Services": 2.5,
                "Consumer Discretionary": 1.5,
                "Industrials": 1.2,
                "Consumer Staples": 0.8
            }
            
            target_ps = target_multiples.get(sector, 3.0)
            
            # Calculate fair value
            fair_value = revenue_per_share * target_ps
            
            # Adjust for growth rate if available
            revenue_growth = info.get("revenueGrowth", 0)
            if revenue_growth > 0.30:  # High growth > 30%
                fair_value *= 1.3  # Premium for hypergrowth
            elif revenue_growth > 0.15:  # Moderate growth 15-30%
                fair_value *= 1.1
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "price_to_sales": price_to_sales,
                "target_ps_multiple": target_ps,
                "revenue_growth": revenue_growth * 100 if revenue_growth else 0,
                "method": "Revenue Multiple (P/S)"
            }
            
        except Exception as e:
            logger.error(f"Error in revenue multiple valuation: {e}")
            return {"error": str(e)}
    
    def calculate_normalized_earnings_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Calculate valuation using normalized earnings (for cyclical companies)
        Uses mid-cycle earnings to avoid overvaluing at peak or undervaluing at trough
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            # Get historical earnings
            eps_history = []
            if "income_statement" in financials:
                income_stmt = financials.get("income_statement")
                if income_stmt is not None:
                    try:
                        income_data = pd.DataFrame(income_stmt) if not isinstance(income_stmt, pd.DataFrame) else income_stmt
                        if not income_data.empty and "Basic EPS" in income_data.index:
                            eps_history = income_data.loc["Basic EPS"].values[:5]  # Last 5 years
                    except Exception as e:
                        logger.error(f"Error parsing income statement: {e}")
            
            if len(eps_history) == 0:
                # Fallback to current EPS
                trailing_eps = info.get("trailingEps", 0)
                if trailing_eps == 0:
                    return {"error": "No earnings data available"}
                eps_history = [trailing_eps]
            
            # Calculate normalized EPS (median of historical)
            normalized_eps = float(np.median(eps_history))
            
            # Get sector-appropriate P/E multiple
            sector = info.get("sector", "Industrials")
            
            # Mid-cycle P/E multiples by sector
            mid_cycle_pe = {
                "Industrials": 16.0,
                "Materials": 14.0,
                "Energy": 12.0,
                "Consumer Discretionary": 18.0,
                "Financials": 12.0,
                "Technology": 20.0
            }
            
            target_pe = mid_cycle_pe.get(sector, 15.0)
            
            # Calculate fair value
            fair_value = normalized_eps * target_pe
            
            # Current P/E for comparison
            current_pe = info.get("trailingPE", 0)
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "normalized_eps": normalized_eps,
                "current_eps": info.get("trailingEps", 0),
                "normalized_pe": target_pe,
                "current_pe": current_pe,
                "method": "Normalized Earnings (Cyclical)"
            }
            
        except Exception as e:
            logger.error(f"Error in normalized earnings valuation: {e}")
            return {"error": str(e)}
    
    def calculate_commodity_reserve_valuation(self, info: Dict, financials: Dict, 
                                              commodity_price: float = None, 
                                              reserves_data: Dict = None) -> Dict:
        """
        Calculate valuation for commodity/energy companies using reserve-based metrics
        
        Args:
            info: Company info from yfinance
            financials: Financial statements
            commodity_price: Current commodity price ($/barrel for oil, $/oz for gold, etc.)
            reserves_data: Manual reserves data if available {
                'proven_reserves': float (MMBoe or oz),
                'production_per_day': float,
                'reserve_life': float (years)
            }
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            shares = info.get("sharesOutstanding", 0)
            enterprise_value = info.get("enterpriseValue", 0)
            
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            # Method 1: EV/Production metrics (if we have production data)
            sector = info.get("sector", "")
            
            # Get market cap and EV
            market_cap = current_price * shares
            
            # For energy companies, use industry average EV/Production multiples
            # Oil & Gas: $50,000-80,000 per BOE/day
            # Mining: Varies by metal
            
            fair_value_estimates = []
            
            # Method 1: P/B with commodity adjustment
            pb_ratio = info.get("priceToBook", 0)
            book_value_per_share = current_price / pb_ratio if pb_ratio > 0 else 0
            
            # Commodity companies typically trade at 1.0-2.0x book
            if book_value_per_share > 0:
                if "Energy" in sector or "oil" in info.get("longBusinessSummary", "").lower():
                    target_pb = 1.2  # Energy sector average
                elif "Materials" in sector or "mining" in info.get("longBusinessSummary", "").lower():
                    target_pb = 1.5  # Mining average
                else:
                    target_pb = 1.3
                
                fair_value_pb = book_value_per_share * target_pb
                fair_value_estimates.append(fair_value_pb)
            
            # Method 2: Reserve-based valuation (if data provided)
            if reserves_data:
                proven_reserves = reserves_data.get('proven_reserves', 0)
                production_per_day = reserves_data.get('production_per_day', 0)
                reserve_life = reserves_data.get('reserve_life', 0)
                
                # PV-10 approximation: Use 60% of gross reserves value
                if commodity_price and proven_reserves > 0:
                    gross_reserve_value = proven_reserves * commodity_price
                    pv10_value = gross_reserve_value * 0.60  # Discount for extraction costs, time value
                    
                    # Subtract debt, add cash
                    debt = info.get("totalDebt", 0)
                    cash = info.get("totalCash", 0)
                    equity_value = pv10_value - debt + cash
                    
                    fair_value_reserves = equity_value / shares
                    fair_value_estimates.append(fair_value_reserves)
                
                # EV/Production metric
                if production_per_day > 0 and enterprise_value > 0:
                    ev_per_boe_day = enterprise_value / production_per_day
                    
                    # Industry benchmarks: $40,000-70,000 per BOE/day
                    target_ev_per_production = 55000  # Mid-range
                    implied_ev = production_per_day * target_ev_per_production
                    
                    debt = info.get("totalDebt", 0)
                    cash = info.get("totalCash", 0)
                    implied_equity = implied_ev - debt + cash
                    fair_value_production = implied_equity / shares
                    fair_value_estimates.append(fair_value_production)
            
            # Method 3: Normalized earnings (cyclical adjustment)
            trailing_eps = info.get("trailingEps", 0)
            if trailing_eps > 0:
                # Use mid-cycle P/E for commodities (10-12x)
                mid_cycle_pe = 11.0
                fair_value_earnings = trailing_eps * mid_cycle_pe
                fair_value_estimates.append(fair_value_earnings)
            
            # Calculate average fair value
            if fair_value_estimates:
                fair_value = np.mean(fair_value_estimates)
            else:
                return {"error": "Insufficient data for commodity valuation"}
            
            # Calculate metrics
            result = {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "pb_ratio": pb_ratio,
                "method": "Commodity Reserve Valuation"
            }
            
            # Add reserve metrics if available
            if reserves_data:
                result.update({
                    "proven_reserves": reserves_data.get('proven_reserves', 0),
                    "production_per_day": reserves_data.get('production_per_day', 0),
                    "reserve_life_years": reserves_data.get('reserve_life', 0),
                    "commodity_price": commodity_price
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in commodity reserve valuation: {e}")
            return {"error": str(e)}
    
    def calculate_sum_of_parts_valuation(self, info: Dict, financials: Dict,
                                         segment_data: List[Dict] = None) -> Dict:
        """
        Calculate Sum-of-Parts valuation for conglomerates with multiple business segments
        
        Args:
            info: Company info from yfinance
            financials: Financial statements
            segment_data: List of segments with revenue/EBITDA and target multiples:
                [{
                    'name': 'Aviation',
                    'revenue': 25_000_000_000,
                    'ebitda': 5_000_000_000,
                    'ebitda_multiple': 12.0,  # Comparable peer multiple
                    'description': 'Commercial aviation'
                }]
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            shares = info.get("sharesOutstanding", 0)
            
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            # If no segment data provided, try to extract from financials or use simplified approach
            if not segment_data:
                # Fallback: Use overall company metrics with conglomerate discount removal
                enterprise_value = info.get("enterpriseValue", 0)
                
                if enterprise_value == 0:
                    return {"error": "No segment data or enterprise value available"}
                
                # Typical conglomerate discount is 15-30%
                # Remove discount to get "pure-play" value
                conglomerate_discount = 0.20  # 20% average
                implied_pure_play_ev = enterprise_value / (1 - conglomerate_discount)
                
                debt = info.get("totalDebt", 0)
                cash = info.get("totalCash", 0)
                equity_value = implied_pure_play_ev - debt + cash
                fair_value = equity_value / shares
                
                return {
                    "fair_value": fair_value,
                    "current_price": current_price,
                    "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                    "conglomerate_discount_removed": conglomerate_discount * 100,
                    "method": "Sum-of-Parts (Simplified)",
                    "note": "Using conglomerate discount removal - provide segment_data for detailed analysis"
                }
            
            # Detailed segment-by-segment valuation
            total_segment_value = 0
            segment_valuations = []
            
            for segment in segment_data:
                segment_name = segment.get('name', 'Unknown')
                ebitda = segment.get('ebitda', 0)
                ebitda_multiple = segment.get('ebitda_multiple', 10.0)
                
                # Calculate segment EV
                segment_ev = ebitda * ebitda_multiple
                total_segment_value += segment_ev
                
                segment_valuations.append({
                    'name': segment_name,
                    'ebitda': ebitda,
                    'multiple': ebitda_multiple,
                    'value': segment_ev,
                    'percentage': 0  # Will calculate after total known
                })
            
            # Calculate percentages
            for seg_val in segment_valuations:
                seg_val['percentage'] = (seg_val['value'] / total_segment_value * 100) if total_segment_value > 0 else 0
            
            # Subtract corporate overhead (typically 5-10% of total value)
            corporate_overhead_rate = 0.05  # 5%
            corporate_overhead = total_segment_value * corporate_overhead_rate
            
            # Net enterprise value
            net_ev = total_segment_value - corporate_overhead
            
            # Convert to equity value
            debt = info.get("totalDebt", 0)
            cash = info.get("totalCash", 0)
            minority_interest = info.get("minorityInterest", 0)
            
            equity_value = net_ev - debt + cash - minority_interest
            fair_value = equity_value / shares
            
            # Compare to current conglomerate discount
            current_market_cap = current_price * shares
            current_ev = current_market_cap + debt - cash
            implied_discount = ((net_ev - current_ev) / net_ev * 100) if net_ev > 0 else 0
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "total_segment_value": total_segment_value,
                "corporate_overhead": corporate_overhead,
                "net_enterprise_value": net_ev,
                "current_conglomerate_discount": implied_discount,
                "segment_breakdown": segment_valuations,
                "method": "Sum-of-Parts (Detailed)"
            }
            
        except Exception as e:
            logger.error(f"Error in sum-of-parts valuation: {e}")
            return {"error": str(e)}
    
    def calculate_biotech_pipeline_valuation(self, info: Dict, financials: Dict,
                                            pipeline_data: List[Dict] = None) -> Dict:
        """
        Calculate risk-adjusted NPV valuation for biotech/pharma companies with drug pipelines
        
        Args:
            info: Company info from yfinance
            financials: Financial statements
            pipeline_data: List of drugs in pipeline:
                [{
                    'name': 'Drug X',
                    'indication': 'Cancer',
                    'phase': 2,  # 1, 2, 3, or 'approved'
                    'peak_sales': 500_000_000,  # Estimated peak annual sales
                    'years_to_peak': 8,  # Years until peak sales
                    'patent_life': 12,  # Years of patent protection remaining
                    'launch_costs': 50_000_000,  # Marketing/launch costs
                    'probability_override': None  # Optional custom probability
                }]
        
        Phase Success Rates (Industry Standard):
        - Phase 1: 10% chance of approval
        - Phase 2: 30% chance of approval  
        - Phase 3: 60% chance of approval
        - Approved: 100% (already on market)
        """
        try:
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            shares = info.get("sharesOutstanding", 0)
            
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            # Phase success probabilities (FDA approval rates)
            phase_probabilities = {
                1: 0.10,   # Phase 1: 10%
                2: 0.30,   # Phase 2: 30%
                3: 0.60,   # Phase 3: 60%
                'approved': 1.00,  # Already approved: 100%
                'marketed': 1.00   # Already on market: 100%
            }
            
            # Discount rate for biotech (higher risk)
            discount_rate = 0.12  # 12% for biotech risk
            
            # If no pipeline data provided, use simplified revenue multiple approach
            if not pipeline_data:
                # Fallback to revenue multiple for biotechs without detailed pipeline
                revenue_result = self.calculate_revenue_multiple_valuation(info, financials)
                if "error" not in revenue_result:
                    revenue_result["method"] = "Biotech Valuation (Simplified - No Pipeline Data)"
                    revenue_result["note"] = "Using revenue multiples. Provide pipeline_data for rNPV analysis"
                return revenue_result
            
            # Calculate rNPV for each drug in pipeline
            total_pipeline_value = 0
            drug_valuations = []
            
            for drug in pipeline_data:
                drug_name = drug.get('name', 'Unknown Drug')
                phase = drug.get('phase', 1)
                peak_sales = drug.get('peak_sales', 0)
                years_to_peak = drug.get('years_to_peak', 8)
                patent_life = drug.get('patent_life', 12)
                launch_costs = drug.get('launch_costs', 50_000_000)
                
                # Get probability of success
                prob_success = drug.get('probability_override', phase_probabilities.get(phase, 0.10))
                
                # Calculate NPV of future cash flows
                drug_npv = 0
                
                # Ramp-up period (years to peak)
                for year in range(1, years_to_peak + 1):
                    # Linear ramp to peak sales
                    annual_sales = peak_sales * (year / years_to_peak)
                    # Assume 80% gross margin for drugs
                    annual_profit = annual_sales * 0.80
                    # Discount to present value
                    pv = annual_profit / ((1 + discount_rate) ** year)
                    drug_npv += pv
                
                # Peak sales period (remaining patent life)
                for year in range(years_to_peak + 1, patent_life + 1):
                    annual_profit = peak_sales * 0.80
                    pv = annual_profit / ((1 + discount_rate) ** year)
                    drug_npv += pv
                
                # Subtract launch costs (discounted to year of launch)
                launch_year = max(1, years_to_peak - 2)  # Typically 2 years before peak
                launch_cost_pv = launch_costs / ((1 + discount_rate) ** launch_year)
                drug_npv -= launch_cost_pv
                
                # Risk-adjust by probability of success
                risk_adjusted_npv = drug_npv * prob_success
                
                total_pipeline_value += risk_adjusted_npv
                
                drug_valuations.append({
                    'name': drug_name,
                    'phase': phase,
                    'probability': prob_success * 100,
                    'peak_sales': peak_sales,
                    'npv': drug_npv,
                    'risk_adjusted_npv': risk_adjusted_npv,
                    'contribution_pct': 0  # Will calculate after total known
                })
            
            # Calculate contribution percentages
            for drug_val in drug_valuations:
                if total_pipeline_value > 0:
                    drug_val['contribution_pct'] = (drug_val['risk_adjusted_npv'] / total_pipeline_value * 100)
            
            # Add current cash/assets, subtract debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            
            # For biotechs, cash is critical (runway)
            # Add cash runway value (assume 2-3 years of operations)
            current_burn_rate = 0
            if "cash_flow" in financials:
                try:
                    cf_data = pd.DataFrame(financials["cash_flow"]) if not isinstance(financials["cash_flow"], pd.DataFrame) else financials["cash_flow"]
                    if not cf_data.empty and "Operating Cash Flow" in cf_data.index:
                        # Recent operating cash flow (negative for biotechs)
                        current_burn_rate = abs(cf_data.loc["Operating Cash Flow"].iloc[0])
                except Exception as e:
                    logger.debug(f"Could not extract operating cash flow: {e}")
                    current_burn_rate = 0
            
            # If no cash flow data, estimate from R&D expense
            if current_burn_rate == 0:
                rd_expense = info.get("researchDevelopment", 100_000_000)
                current_burn_rate = rd_expense * 1.5  # R&D + SG&A approximation
            
            # Cash runway (years)
            cash_runway = cash / current_burn_rate if current_burn_rate > 0 else 2.0
            
            # Total equity value
            equity_value = total_pipeline_value + cash - debt
            fair_value = equity_value / shares
            
            # Calculate probability-weighted outcomes
            best_case = fair_value * 1.5  # If all drugs succeed
            worst_case = (cash - debt) / shares  # Liquidation value
            
            return {
                "fair_value": fair_value,
                "current_price": current_price,
                "upside": ((fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "pipeline_value": total_pipeline_value,
                "cash": cash,
                "debt": debt,
                "net_cash": cash - debt,
                "cash_runway_years": cash_runway,
                "current_burn_rate": current_burn_rate,
                "drug_count": len(drug_valuations),
                "pipeline_breakdown": drug_valuations,
                "scenarios": {
                    "bear": worst_case,
                    "base": fair_value,
                    "bull": best_case
                },
                "method": "Biotech Pipeline (rNPV)"
            }
            
        except Exception as e:
            logger.error(f"Error in biotech pipeline valuation: {e}")
            return {"error": str(e)}


class TechnicalAnalyzer:
    """Technical analysis and pattern detection"""
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """Run comprehensive technical analysis"""
        if df.empty or len(df) < 20:
            return {"error": "Insufficient data for technical analysis"}
        
        try:
            analysis = {}
            
            # Price action
            latest_price = df['Close'].iloc[-1]
            sma_20 = df['Close'].rolling(20).mean().iloc[-1]
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else sma_20
            sma_200 = df['Close'].rolling(200).mean().iloc[-1] if len(df) >= 200 else sma_50
            
            analysis["price_action"] = {
                "price": latest_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "above_sma_20": latest_price > sma_20,
                "above_sma_50": latest_price > sma_50,
                "above_sma_200": latest_price > sma_200,
            }
            
            # RSI
            rsi = ta.momentum.RSIIndicator(df['Close']).rsi().iloc[-1]
            analysis["rsi"] = {
                "value": rsi,
                "signal": "oversold" if rsi < RSI_OVERSOLD else "overbought" if rsi > RSI_OVERBOUGHT else "neutral"
            }
            
            # MACD
            macd = ta.trend.MACD(df['Close'])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            analysis["macd"] = {
                "macd": macd_line,
                "signal": signal_line,
                "histogram": macd_line - signal_line,
                "bullish": macd_line > signal_line
            }
            
            # Bollinger Bands
            bb = ta.volatility.BollingerBands(df['Close'])
            analysis["bollinger"] = {
                "upper": bb.bollinger_hband().iloc[-1],
                "middle": bb.bollinger_mavg().iloc[-1],
                "lower": bb.bollinger_lband().iloc[-1],
                "price": latest_price,
                "signal": "oversold" if latest_price < bb.bollinger_lband().iloc[-1] else 
                         "overbought" if latest_price > bb.bollinger_hband().iloc[-1] else "neutral"
            }
            
            # Support and Resistance
            highs = df['High'].rolling(20).max()
            lows = df['Low'].rolling(20).min()
            analysis["support_resistance"] = {
                "resistance": highs.iloc[-1],
                "support": lows.iloc[-1],
                "price": latest_price,
                "near_support": (latest_price - lows.iloc[-1]) / lows.iloc[-1] < 0.02,
                "near_resistance": (highs.iloc[-1] - latest_price) / latest_price < 0.02
            }
            
            # Volume analysis
            avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
            latest_volume = df['Volume'].iloc[-1]
            analysis["volume"] = {
                "current": latest_volume,
                "average": avg_volume,
                "ratio": latest_volume / avg_volume if avg_volume > 0 else 1,
                "increasing": latest_volume > avg_volume * 1.5
            }
            
            # ADX (Average Directional Index) - Trend strength
            adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'])
            analysis["adx"] = {
                "value": adx.adx().iloc[-1] if len(df) >= 14 else 0,
                "plus_di": adx.adx_pos().iloc[-1] if len(df) >= 14 else 0,
                "minus_di": adx.adx_neg().iloc[-1] if len(df) >= 14 else 0,
                "signal": "strong_trend" if adx.adx().iloc[-1] > 25 else "weak_trend" if len(df) >= 14 else "insufficient_data"
            }
            
            # OBV (On-Balance Volume) - Volume momentum
            obv = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume'])
            obv_values = obv.on_balance_volume()
            obv_ma = obv_values.rolling(20).mean()
            analysis["obv"] = {
                "value": obv_values.iloc[-1],
                "ma_20": obv_ma.iloc[-1] if len(df) >= 20 else obv_values.iloc[-1],
                "bullish": obv_values.iloc[-1] > obv_ma.iloc[-1] if len(df) >= 20 else False
            }
            
            # Trend
            analysis["trend"] = self._determine_trend(df)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {"error": str(e)}
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """Determine market trend"""
        if len(df) < 50:
            return "insufficient_data"
        
        sma_20 = df['Close'].rolling(20).mean()
        sma_50 = df['Close'].rolling(50).mean()
        
        if sma_20.iloc[-1] > sma_50.iloc[-1] and sma_20.iloc[-5] < sma_50.iloc[-5]:
            return "bullish_crossover"
        elif sma_20.iloc[-1] < sma_50.iloc[-1] and sma_20.iloc[-5] > sma_50.iloc[-5]:
            return "bearish_crossover"
        elif sma_20.iloc[-1] > sma_50.iloc[-1]:
            return "bullish"
        else:
            return "bearish"
    
    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect chart patterns"""
        patterns = []
        
        if len(df) < 50:
            return patterns
        
        # Simple pattern detection
        # Head and Shoulders
        if self._detect_head_shoulders(df):
            patterns.append({"pattern": "head_and_shoulders", "signal": "bearish"})
        
        # Double Bottom
        if self._detect_double_bottom(df):
            patterns.append({"pattern": "double_bottom", "signal": "bullish"})
        
        # Cup and Handle (simplified)
        if self._detect_cup_handle(df):
            patterns.append({"pattern": "cup_and_handle", "signal": "bullish"})
        
        return patterns
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> bool:
        """Simplified head and shoulders detection"""
        if len(df) < 60:
            return False
        
        prices = df['High'].values[-60:]
        # Find peaks
        peaks = []
        for i in range(1, len(prices)-1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                peaks.append((i, prices[i]))
        
        if len(peaks) >= 3:
            # Check if middle peak is highest (head)
            peak_values = [p[1] for p in peaks]
            max_idx = peak_values.index(max(peak_values))
            if 0 < max_idx < len(peaks) - 1:
                # Shoulders should be roughly equal
                left_shoulder = peak_values[max_idx - 1]
                right_shoulder = peak_values[max_idx + 1]
                if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                    return True
        
        return False
    
    def _detect_double_bottom(self, df: pd.DataFrame) -> bool:
        """Simplified double bottom detection"""
        if len(df) < 40:
            return False
        
        lows = df['Low'].values[-40:]
        # Find troughs
        troughs = []
        for i in range(1, len(lows)-1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                troughs.append((i, lows[i]))
        
        if len(troughs) >= 2:
            # Check if two lows are roughly equal
            for i in range(len(troughs)-1):
                if abs(troughs[i][1] - troughs[i+1][1]) / troughs[i][1] < 0.03:
                    # Check if price went up between them
                    between_high = max(lows[troughs[i][0]:troughs[i+1][0]])
                    if between_high > troughs[i][1] * 1.05:
                        return True
        
        return False
    
    def _detect_cup_handle(self, df: pd.DataFrame) -> bool:
        """Simplified cup and handle detection"""
        if len(df) < 60:
            return False
        
        prices = df['Close'].values[-60:]
        
        # Look for U-shape followed by slight decline
        mid_point = len(prices) // 2
        left_high = max(prices[:mid_point//2])
        bottom = min(prices[mid_point//2:mid_point+mid_point//2])
        right_high = max(prices[mid_point+mid_point//2:-10])
        handle = prices[-10:]
        
        # Cup shape: high-low-high
        if left_high > bottom * 1.1 and right_high > bottom * 1.1:
            # Handle: slight decline from right high
            if max(handle) < right_high and min(handle) > bottom * 1.05:
                return True
        
        return False


class GoodBuyAnalyzer:
    """Determines if a stock is a good buy"""
    
    def __init__(self):
        self.weights = {
            "valuation": 0.30,
            "technical": 0.25,
            "sentiment": 0.15,
            "momentum": 0.15,
            "fundamentals": 0.15
        }
    
    def analyze_buy_opportunity(self, 
                                ticker: str,
                                valuation: Dict,
                                technical: Dict,
                                sentiment: Dict,
                                info: Dict,
                                df: pd.DataFrame) -> Dict:
        """Determine if stock is a good buy and at what price"""
        
        scores = {}
        signals = []
        
        # 1. Valuation Score
        val_score = 0
        if "upside" in valuation and valuation["upside"] > 15:
            val_score = min(100, valuation["upside"] * 2)
            signals.append(f"Undervalued by {valuation['upside']:.1f}%")
        scores["valuation"] = val_score
        
        # 2. Technical Score
        tech_score = 0
        if technical and "error" not in technical:
            # RSI oversold
            if technical.get("rsi", {}).get("value", 50) < 35:
                tech_score += 30
                signals.append(f"RSI oversold at {technical['rsi']['value']:.1f}")
            
            # MACD bullish
            if technical.get("macd", {}).get("bullish", False):
                tech_score += 20
                signals.append("MACD bullish crossover")
            
            # Near support
            if technical.get("support_resistance", {}).get("near_support", False):
                tech_score += 30
                signals.append("Near support level")
            
            # Volume surge
            if technical.get("volume", {}).get("ratio", 1) > 1.5:
                tech_score += 20
                signals.append("Volume surge detected")
        
        scores["technical"] = min(100, tech_score)
        
        # 3. Sentiment Score
        sent_score = 50  # Neutral default
        if sentiment and "sentiment_score" in sentiment:
            if sentiment["sentiment_score"] > 20:
                sent_score = 70
                signals.append("Positive sentiment")
            elif sentiment["sentiment_score"] < -20:
                sent_score = 30
        scores["sentiment"] = sent_score
        
        # 4. Momentum Score
        mom_score = 0
        if not df.empty and len(df) > 20:
            returns_1m = ((df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1) * 100 if len(df) > 20 else 0
            returns_3m = ((df['Close'].iloc[-1] / df['Close'].iloc[-60]) - 1) * 100 if len(df) > 60 else 0
            
            # Positive but not excessive momentum
            if 0 < returns_1m < 10:
                mom_score += 50
            if -10 < returns_3m < 0:  # Recent pullback
                mom_score += 30
                signals.append("Healthy pullback in uptrend")
        
        scores["momentum"] = min(100, mom_score)
        
        # 5. Fundamentals Score
        fund_score = 50  # Default
        if info:
            pe_ratio = info.get("trailingPE", 0)
            if 0 < pe_ratio < 20:
                fund_score += 25
            
            profit_margin = info.get("profitMargins", 0)
            if profit_margin > 0.15:
                fund_score += 25
        
        scores["fundamentals"] = min(100, fund_score)
        
        # Calculate weighted score
        total_score = sum(scores[k] * self.weights[k] for k in scores)
        
        # Determine buy zones
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        
        # Calculate good buy price range
        if total_score >= 70:
            # Strong buy
            buy_range_low = current_price * 0.98
            buy_range_high = current_price * 1.02
            confidence = "HIGH"
        elif total_score >= 50:
            # Moderate buy
            buy_range_low = current_price * 0.95
            buy_range_high = current_price
            confidence = "MEDIUM"
        else:
            # Wait for better entry
            buy_range_low = current_price * 0.90
            buy_range_high = current_price * 0.95
            confidence = "LOW"
        
        # Target price
        if "fair_value" in valuation:
            target_price = valuation["fair_value"]
        else:
            # Use technical resistance
            target_price = technical.get("support_resistance", {}).get("resistance", current_price * 1.15)
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "total_score": total_score,
            "confidence": confidence,
            "buy_range": {
                "low": buy_range_low,
                "high": buy_range_high
            },
            "target_price": target_price,
            "stop_loss": buy_range_low * 0.95,
            "risk_reward_ratio": (target_price - current_price) / (current_price - buy_range_low * 0.95) if current_price > buy_range_low else 0,
            "scores": scores,
            "signals": signals,
            "recommendation": "STRONG BUY" if total_score >= 70 else "BUY" if total_score >= 50 else "HOLD"
        }


class RiskAnalyzer:
    """Risk analysis and metrics"""
    
    def calculate_risk_metrics(self, df: pd.DataFrame, info: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        if df.empty or len(df) < 30:
            return {"error": "Insufficient data for risk analysis"}
        
        try:
            # Calculate returns
            returns = df['Close'].pct_change().dropna()
            
            # Beta (already in info, but calculate for confirmation)
            beta = info.get("beta", 1.0)
            
            # Sharpe Ratio (annualized)
            risk_free_rate = 0.045  # 4.5% annual
            excess_returns = returns.mean() - (risk_free_rate / 252)  # Daily risk-free rate
            sharpe_ratio = (excess_returns / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
            
            # Sortino Ratio (only downside volatility)
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() if len(downside_returns) > 0 else returns.std()
            sortino_ratio = (excess_returns / downside_std) * np.sqrt(252) if downside_std > 0 else 0
            
            # Rolling volatility (30-day window)
            rolling_vol = returns.rolling(window=30).std() * np.sqrt(252) * 100  # Annualized %
            current_vol = rolling_vol.iloc[-1] if len(rolling_vol) > 0 else 0
            avg_vol = rolling_vol.mean() if len(rolling_vol) > 0 else 0
            
            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100  # Convert to percentage
            
            # Value at Risk (VaR) - 95% confidence
            var_95 = np.percentile(returns, 5) * 100  # 5th percentile
            
            # Expected Shortfall (CVaR) - average of worst 5%
            cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
            
            return {
                "beta": beta,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "current_volatility": current_vol,
                "average_volatility": avg_vol,
                "max_drawdown": max_drawdown,
                "var_95": var_95,
                "cvar_95": cvar_95,
                "rolling_volatility": rolling_vol.tolist()[-60:] if len(rolling_vol) >= 60 else rolling_vol.tolist(),  # Last 60 days
                "risk_rating": self._get_risk_rating(current_vol, beta, max_drawdown)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {"error": str(e)}
    
    def _get_risk_rating(self, volatility: float, beta: float, max_drawdown: float) -> str:
        """Determine overall risk rating"""
        risk_score = 0
        
        # Volatility contribution
        if volatility > 50:
            risk_score += 3
        elif volatility > 30:
            risk_score += 2
        elif volatility > 15:
            risk_score += 1
        
        # Beta contribution
        if abs(beta) > 1.5:
            risk_score += 2
        elif abs(beta) > 1.0:
            risk_score += 1
        
        # Drawdown contribution
        if abs(max_drawdown) > 50:
            risk_score += 3
        elif abs(max_drawdown) > 30:
            risk_score += 2
        elif abs(max_drawdown) > 15:
            risk_score += 1
        
        if risk_score >= 6:
            return "Very High Risk"
        elif risk_score >= 4:
            return "High Risk"
        elif risk_score >= 2:
            return "Moderate Risk"
        else:
            return "Low Risk"


class OptionsAnalyzer:
    """Analyze options for opportunities"""
    
    def find_best_opportunities(self, options_data: Dict, current_price: float) -> List[Dict]:
        """Find best options opportunities"""
        opportunities = []
        
        if not options_data or "chains" not in options_data:
            return opportunities
        
        for expiration, chain in options_data["chains"].items():
            if not chain:
                continue
            
            # Analyze calls
            if "calls" in chain and chain["calls"]:
                calls_df = pd.DataFrame(chain["calls"])
                if not calls_df.empty and "strike" in calls_df.columns:
                    # Find high volume/OI ratio
                    if "volume" in calls_df.columns and "openInterest" in calls_df.columns:
                        calls_df["vol_oi_ratio"] = calls_df["volume"] / calls_df["openInterest"].replace(0, 1)
                        unusual = calls_df[calls_df["vol_oi_ratio"] > 2]
                        
                        for _, row in unusual.iterrows():
                            opportunities.append({
                                "type": "CALL",
                                "strike": row.get("strike", 0),
                                "expiration": expiration,
                                "volume": row.get("volume", 0),
                                "oi": row.get("openInterest", 0),
                                "iv": row.get("impliedVolatility", 0),
                                "signal": "Unusual activity"
                            })
        
        return opportunities[:10]  # Top 10 opportunities
