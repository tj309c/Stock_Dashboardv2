"""
Zero-FCF Valuation Engine
Alternative valuation models for companies with zero or negative free cash flow
Includes: Revenue-based, EBITDA multiples, Rule of 40, Unit Economics, and Auto-selection logic
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ZeroFCFValuationEngine:
    """
    Comprehensive valuation engine for companies with zero or negative FCF.
    Automatically selects the best valuation method based on data availability.
    """
    
    def __init__(self):
        # Industry-specific multiples
        self.revenue_multiples = {
            "Technology": 6.0,
            "Software": 8.0,
            "SaaS": 10.0,
            "E-commerce": 2.5,
            "Biotech": 5.0,
            "Healthcare": 2.0,
            "Consumer Cyclical": 1.0,
            "Consumer Defensive": 1.2,
            "Financial Services": 2.5,
            "Industrials": 1.5,
            "Energy": 1.0,
            "Materials": 1.2,
            "Real Estate": 3.0,
            "Utilities": 2.0,
            "Communication Services": 3.5,
            "Default": 2.5
        }
        
        self.ebitda_multiples = {
            "Technology": 18.0,
            "Software": 25.0,
            "SaaS": 30.0,
            "E-commerce": 12.0,
            "Biotech": 15.0,
            "Healthcare": 12.0,
            "Consumer Cyclical": 10.0,
            "Consumer Defensive": 11.0,
            "Financial Services": 8.0,
            "Industrials": 10.0,
            "Energy": 7.0,
            "Materials": 8.0,
            "Real Estate": 14.0,
            "Utilities": 9.0,
            "Communication Services": 12.0,
            "Default": 12.0
        }
        
    def calculate_comprehensive_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Auto-select and calculate the best valuation method based on available data.
        Returns comprehensive valuation with multiple scenarios.
        """
        try:
            # Detect company characteristics
            company_type = self._detect_company_type(info, financials)
            
            # Try all applicable methods
            valuations = {}
            
            # 1. Revenue-based valuation
            revenue_val = self.calculate_revenue_valuation(info, financials)
            if "error" not in revenue_val:
                valuations["revenue"] = revenue_val
            
            # 2. EBITDA multiple valuation
            ebitda_val = self.calculate_ebitda_valuation(info, financials)
            if "error" not in ebitda_val:
                valuations["ebitda"] = ebitda_val
            
            # 3. Rule of 40 valuation (for SaaS/high-growth)
            if company_type in ["SaaS", "Software", "Technology"]:
                rule40_val = self.calculate_rule_of_40_valuation(info, financials)
                if "error" not in rule40_val:
                    valuations["rule_of_40"] = rule40_val
            
            # 4. Unit Economics valuation (for SaaS)
            if company_type in ["SaaS", "Software"]:
                unit_val = self.calculate_unit_economics_valuation(info, financials)
                if "error" not in unit_val:
                    valuations["unit_economics"] = unit_val
            
            # 5. Revenue CAGR terminal value
            terminal_val = self.calculate_revenue_terminal_value(info, financials)
            if "error" not in terminal_val:
                valuations["terminal_value"] = terminal_val
            
            if not valuations:
                return {
                    "error": "Insufficient data for Zero-FCF valuation",
                    "company_type": company_type,
                    "recommendation": "Company requires positive cash flow for traditional DCF"
                }
            
            # Calculate weighted average based on data quality
            weighted_fair_value = self._calculate_weighted_valuation(valuations, company_type)
            
            current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
            
            # Generate scenarios
            scenarios = {
                "bear": weighted_fair_value * 0.7,
                "base": weighted_fair_value,
                "bull": weighted_fair_value * 1.3,
                "optimistic": weighted_fair_value * 1.5
            }
            
            return {
                "fair_value": weighted_fair_value,
                "current_price": current_price,
                "upside": ((weighted_fair_value - current_price) / current_price * 100) if current_price > 0 else 0,
                "company_type": company_type,
                "scenarios": scenarios,
                "valuations": valuations,
                "primary_method": self._select_primary_method(valuations, company_type),
                "confidence": self._calculate_confidence(valuations),
                "methodology": "Zero-FCF Multi-Method Valuation"
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive Zero-FCF valuation: {e}")
            return {"error": str(e)}
    
    def calculate_revenue_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Revenue-based valuation using industry-appropriate revenue multiples.
        Ideal for high-growth companies prioritizing top-line growth.
        """
        try:
            # Get revenue data
            revenue = info.get("totalRevenue", 0)
            revenue_growth = info.get("revenueGrowth", 0)
            
            if revenue == 0:
                # Try to get from financials
                if "financials" in financials and financials.get("financials"):
                    try:
                        income_stmt = pd.DataFrame(financials["financials"])
                        if not income_stmt.empty and "Total Revenue" in income_stmt.index:
                            revenue = income_stmt.loc["Total Revenue"].iloc[0]
                    except Exception as e:
                        logger.debug(f"Error parsing revenue from financials: {e}")
            
            if revenue == 0:
                return {"error": "No revenue data available"}
            
            # Get sector and determine multiple
            sector = info.get("sector", "Default")
            subsector = info.get("industry", "")
            
            # Refine multiple based on subsector
            if "Software" in subsector or "SaaS" in subsector:
                base_multiple = self.revenue_multiples.get("SaaS", 10.0)
            elif "E-commerce" in subsector or "Internet" in subsector:
                base_multiple = self.revenue_multiples.get("E-commerce", 2.5)
            else:
                base_multiple = self.revenue_multiples.get(sector, self.revenue_multiples["Default"])
            
            # Adjust multiple based on growth rate
            growth_adjustment = 1.0
            if revenue_growth > 0.5:  # 50%+ growth
                growth_adjustment = 1.5
            elif revenue_growth > 0.3:  # 30-50% growth
                growth_adjustment = 1.3
            elif revenue_growth > 0.15:  # 15-30% growth
                growth_adjustment = 1.1
            elif revenue_growth < 0:  # Negative growth
                growth_adjustment = 0.7
            
            adjusted_multiple = base_multiple * growth_adjustment
            
            # Calculate enterprise value
            enterprise_value = revenue * adjusted_multiple
            
            # Adjust for net cash/debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Calculate per-share value
            shares = info.get("sharesOutstanding", 0)
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            fair_value = equity_value / shares
            
            return {
                "fair_value": fair_value,
                "enterprise_value": enterprise_value,
                "revenue": revenue,
                "revenue_multiple": adjusted_multiple,
                "base_multiple": base_multiple,
                "growth_adjustment": growth_adjustment,
                "revenue_growth": revenue_growth * 100,
                "method": "Revenue Multiple",
                "data_quality": "high" if revenue_growth != 0 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error in revenue valuation: {e}")
            return {"error": str(e)}
    
    def calculate_ebitda_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        EBITDA multiple valuation for companies with positive EBITDA but negative FCF.
        Common for capital-intensive growth companies.
        """
        try:
            ebitda = info.get("ebitda", 0)
            
            if ebitda == 0:
                # Try to calculate from financials
                if "financials" in financials and financials.get("financials"):
                    try:
                        income_stmt = pd.DataFrame(financials["financials"])
                        if not income_stmt.empty:
                            # EBITDA = EBIT + D&A
                            ebit = income_stmt.loc["EBIT"].iloc[0] if "EBIT" in income_stmt.index else 0
                            if ebit == 0 and "Operating Income" in income_stmt.index:
                                ebit = income_stmt.loc["Operating Income"].iloc[0]
                            
                            # Estimate D&A if not available
                            if ebit != 0:
                                ebitda = ebit * 1.15  # Rough estimate
                    except Exception as e:
                        logger.debug(f"Error calculating EBITDA: {e}")
            
            if ebitda <= 0:
                return {"error": "No positive EBITDA available"}
            
            # Get sector and determine multiple
            sector = info.get("sector", "Default")
            subsector = info.get("industry", "")
            
            # Refine multiple based on subsector
            if "Software" in subsector or "SaaS" in subsector:
                base_multiple = self.ebitda_multiples.get("SaaS", 30.0)
            else:
                base_multiple = self.ebitda_multiples.get(sector, self.ebitda_multiples["Default"])
            
            # Adjust for growth and margins
            revenue_growth = info.get("revenueGrowth", 0)
            ebitda_margin = info.get("ebitdaMargins", 0)
            
            growth_adjustment = 1.0
            if revenue_growth > 0.3:
                growth_adjustment = 1.3
            elif revenue_growth > 0.15:
                growth_adjustment = 1.15
            elif revenue_growth < 0:
                growth_adjustment = 0.8
            
            margin_adjustment = 1.0
            if ebitda_margin > 0.3:  # 30%+ margins
                margin_adjustment = 1.2
            elif ebitda_margin > 0.2:  # 20-30% margins
                margin_adjustment = 1.1
            elif ebitda_margin < 0.1:  # <10% margins
                margin_adjustment = 0.9
            
            adjusted_multiple = base_multiple * growth_adjustment * margin_adjustment
            
            # Calculate enterprise value
            enterprise_value = ebitda * adjusted_multiple
            
            # Adjust for net cash/debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Calculate per-share value
            shares = info.get("sharesOutstanding", 0)
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            fair_value = equity_value / shares
            
            return {
                "fair_value": fair_value,
                "enterprise_value": enterprise_value,
                "ebitda": ebitda,
                "ebitda_multiple": adjusted_multiple,
                "base_multiple": base_multiple,
                "ebitda_margin": ebitda_margin * 100,
                "method": "EBITDA Multiple",
                "data_quality": "high"
            }
            
        except Exception as e:
            logger.error(f"Error in EBITDA valuation: {e}")
            return {"error": str(e)}
    
    def calculate_rule_of_40_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Rule of 40 valuation for SaaS companies.
        Rule: Revenue Growth Rate + Free Cash Flow Margin should be >= 40%
        Higher scores warrant premium valuations.
        """
        try:
            revenue_growth = info.get("revenueGrowth", 0) * 100
            
            # Try to get FCF margin
            revenue = info.get("totalRevenue", 0)
            if revenue == 0:
                return {"error": "No revenue data for Rule of 40"}
            
            # Get free cash flow
            fcf = 0
            if "cash_flow" in financials and financials.get("cash_flow") is not None:
                try:
                    cf_data = financials["cash_flow"]
                    if isinstance(cf_data, pd.DataFrame):
                        if not cf_data.empty and "Free Cash Flow" in cf_data.index:
                            fcf = cf_data.loc["Free Cash Flow"].iloc[0]
                except Exception as e:
                    logger.debug(f"Error parsing FCF: {e}")
            
            fcf_margin = (fcf / revenue * 100) if revenue > 0 else 0
            
            # Calculate Rule of 40 score
            rule_of_40_score = revenue_growth + fcf_margin
            
            # Base valuation on revenue
            base_revenue_multiple = 8.0  # Base for SaaS
            
            # Adjust multiple based on Rule of 40 score
            if rule_of_40_score >= 60:
                multiple = base_revenue_multiple * 1.5  # Premium valuation
            elif rule_of_40_score >= 40:
                multiple = base_revenue_multiple * 1.2  # Above average
            elif rule_of_40_score >= 20:
                multiple = base_revenue_multiple * 1.0  # Average
            else:
                multiple = base_revenue_multiple * 0.7  # Below average
            
            # Calculate enterprise value
            enterprise_value = revenue * multiple
            
            # Adjust for net cash/debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Calculate per-share value
            shares = info.get("sharesOutstanding", 0)
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            fair_value = equity_value / shares
            
            # Determine quality rating
            if rule_of_40_score >= 40:
                quality = "excellent"
            elif rule_of_40_score >= 20:
                quality = "good"
            elif rule_of_40_score >= 0:
                quality = "fair"
            else:
                quality = "poor"
            
            return {
                "fair_value": fair_value,
                "enterprise_value": enterprise_value,
                "rule_of_40_score": rule_of_40_score,
                "revenue_growth": revenue_growth,
                "fcf_margin": fcf_margin,
                "revenue_multiple": multiple,
                "quality_rating": quality,
                "method": "Rule of 40",
                "data_quality": "high" if fcf != 0 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error in Rule of 40 valuation: {e}")
            return {"error": str(e)}
    
    def calculate_unit_economics_valuation(self, info: Dict, financials: Dict) -> Dict:
        """
        Unit economics valuation for SaaS companies.
        Uses Customer Lifetime Value (LTV) and Customer Acquisition Cost (CAC).
        """
        try:
            revenue = info.get("totalRevenue", 0)
            revenue_growth = info.get("revenueGrowth", 0)
            
            if revenue == 0:
                return {"error": "No revenue data for unit economics"}
            
            # Estimate key metrics (in absence of direct data)
            # For SaaS: Typical metrics
            
            # Estimate gross margin
            gross_margin = info.get("grossMargins", 0.75)  # 75% typical for SaaS
            
            # Estimate churn rate based on growth
            # High growth usually means lower churn
            if revenue_growth > 0.5:
                monthly_churn = 0.03  # 3% for high-growth
            elif revenue_growth > 0.3:
                monthly_churn = 0.04  # 4% for good growth
            else:
                monthly_churn = 0.05  # 5% for average
            
            # Calculate customer lifetime (months)
            customer_lifetime = 1 / monthly_churn if monthly_churn > 0 else 33
            
            # Estimate ARPU (Annual Revenue Per User)
            # We'll estimate customer count based on revenue and typical ARPU
            estimated_arpu = 50000  # $50k annual contract value (typical mid-market SaaS)
            estimated_customers = revenue / estimated_arpu
            
            # Calculate LTV
            ltv = (estimated_arpu / 12) * customer_lifetime * gross_margin
            
            # Estimate CAC based on sales & marketing spend
            # Typical SaaS: 30-50% of revenue on S&M
            sm_spend_ratio = 0.4
            sm_spend = revenue * sm_spend_ratio
            
            # New customers = growth in revenue / ARPU
            new_customers = (revenue * revenue_growth) / estimated_arpu if revenue_growth > 0 else estimated_customers * 0.2
            
            cac = sm_spend / new_customers if new_customers > 0 else estimated_arpu * 0.3
            
            # Calculate LTV:CAC ratio
            ltv_cac_ratio = ltv / cac if cac > 0 else 3.0
            
            # Value company based on LTV:CAC efficiency
            # Good SaaS: LTV:CAC > 3
            # Great SaaS: LTV:CAC > 5
            
            base_revenue_multiple = 8.0
            
            if ltv_cac_ratio > 5:
                efficiency_multiplier = 1.5
            elif ltv_cac_ratio > 3:
                efficiency_multiplier = 1.3
            elif ltv_cac_ratio > 2:
                efficiency_multiplier = 1.1
            else:
                efficiency_multiplier = 0.8
            
            # Also factor in payback period
            # Payback period = CAC / (ARPU * Gross Margin / 12)
            monthly_profit_per_customer = (estimated_arpu * gross_margin) / 12
            payback_period = cac / monthly_profit_per_customer if monthly_profit_per_customer > 0 else 24
            
            # Good: < 12 months, Acceptable: < 18 months
            if payback_period < 12:
                payback_multiplier = 1.2
            elif payback_period < 18:
                payback_multiplier = 1.0
            else:
                payback_multiplier = 0.8
            
            adjusted_multiple = base_revenue_multiple * efficiency_multiplier * payback_multiplier
            
            # Calculate enterprise value
            enterprise_value = revenue * adjusted_multiple
            
            # Adjust for net cash/debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Calculate per-share value
            shares = info.get("sharesOutstanding", 0)
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            fair_value = equity_value / shares
            
            return {
                "fair_value": fair_value,
                "enterprise_value": enterprise_value,
                "ltv": ltv,
                "cac": cac,
                "ltv_cac_ratio": ltv_cac_ratio,
                "payback_period_months": payback_period,
                "estimated_customers": estimated_customers,
                "estimated_arpu": estimated_arpu,
                "monthly_churn": monthly_churn * 100,
                "revenue_multiple": adjusted_multiple,
                "method": "Unit Economics",
                "data_quality": "medium",  # Estimated metrics
                "note": "Metrics estimated from revenue and growth data"
            }
            
        except Exception as e:
            logger.error(f"Error in unit economics valuation: {e}")
            return {"error": str(e)}
    
    def calculate_revenue_terminal_value(self, info: Dict, financials: Dict) -> Dict:
        """
        Calculate terminal value using revenue CAGR when cash flows are unavailable.
        Projects future revenue and applies appropriate multiple.
        """
        try:
            # Get historical revenue data
            revenues = []
            if "financials" in financials and financials.get("financials") is not None:
                try:
                    income_stmt = financials["financials"]
                    if isinstance(income_stmt, pd.DataFrame):
                        if not income_stmt.empty and "Total Revenue" in income_stmt.index:
                            revenues = income_stmt.loc["Total Revenue"].values[:4]
                except Exception as e:
                    logger.debug(f"Error parsing revenue history: {e}")
            
            current_revenue = info.get("totalRevenue", 0)
            if current_revenue == 0 and len(revenues) > 0:
                current_revenue = revenues[0]
            
            if current_revenue == 0:
                return {"error": "No revenue data for terminal value calculation"}
            
            # Calculate historical CAGR if possible
            if len(revenues) >= 2:
                oldest_revenue = revenues[-1]
                years = len(revenues) - 1
                if oldest_revenue > 0:
                    historical_cagr = (current_revenue / oldest_revenue) ** (1 / years) - 1
                else:
                    historical_cagr = info.get("revenueGrowth", 0.15)
            else:
                historical_cagr = info.get("revenueGrowth", 0.15)
            
            # Project 5-year revenue
            # Assume growth rate decelerates over time
            projected_revenues = []
            growth_decay = 0.85  # Growth decelerates 15% per year
            
            current_growth = historical_cagr
            proj_revenue = current_revenue
            
            for year in range(1, 6):
                current_growth *= growth_decay
                current_growth = max(current_growth, 0.025)  # Floor at 2.5% terminal growth
                proj_revenue *= (1 + current_growth)
                projected_revenues.append(proj_revenue)
            
            terminal_revenue = projected_revenues[-1]
            
            # Apply terminal multiple based on maturity
            terminal_growth = current_growth  # Final year growth
            sector = info.get("sector", "Default")
            
            # Mature company multiples (lower than growth multiples)
            if terminal_growth < 0.05:  # Slow growth
                terminal_multiple = self.revenue_multiples.get(sector, 2.5) * 0.6
            elif terminal_growth < 0.10:  # Moderate growth
                terminal_multiple = self.revenue_multiples.get(sector, 2.5) * 0.8
            else:  # Still growing
                terminal_multiple = self.revenue_multiples.get(sector, 2.5) * 1.0
            
            # Calculate terminal value
            terminal_value = terminal_revenue * terminal_multiple
            
            # Discount to present value
            wacc = 0.10  # Assumed WACC
            beta = info.get("beta", 1.0)
            if beta > 0:
                risk_free = 0.045
                market_premium = 0.065
                wacc = risk_free + beta * market_premium
            
            pv_terminal_value = terminal_value / (1 + wacc) ** 5
            
            # Add present value of near-term revenues (simple approximation)
            pv_near_term = sum([rev / (1 + wacc) ** (i + 1) for i, rev in enumerate(projected_revenues)])
            
            # Total enterprise value
            enterprise_value = pv_terminal_value + pv_near_term * 0.3  # Weight terminal value more
            
            # Adjust for net cash/debt
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            equity_value = enterprise_value + cash - debt
            
            # Calculate per-share value
            shares = info.get("sharesOutstanding", 0)
            if shares == 0:
                return {"error": "No shares outstanding data"}
            
            fair_value = equity_value / shares
            
            return {
                "fair_value": fair_value,
                "enterprise_value": enterprise_value,
                "terminal_value": terminal_value,
                "terminal_revenue": terminal_revenue,
                "terminal_multiple": terminal_multiple,
                "historical_cagr": historical_cagr * 100,
                "terminal_growth": terminal_growth * 100,
                "projection_years": 5,
                "wacc": wacc * 100,
                "method": "Revenue Terminal Value",
                "data_quality": "high" if len(revenues) >= 3 else "medium"
            }
            
        except Exception as e:
            logger.error(f"Error in revenue terminal value calculation: {e}")
            return {"error": str(e)}
    
    def _detect_company_type(self, info: Dict, financials: Dict) -> str:
        """Detect company type based on sector, industry, and metrics."""
        sector = info.get("sector", "")
        industry = info.get("industry", "")
        
        # Check for SaaS/Software indicators
        if "Software" in industry or "SaaS" in industry:
            return "SaaS"
        elif "Technology" in sector and "Application" in industry:
            return "Software"
        elif "Internet" in industry or "E-commerce" in industry or "E-Commerce" in industry:
            return "E-commerce"
        elif sector == "Technology":
            return "Technology"
        elif sector == "Healthcare" and ("Biotech" in industry or "Pharmaceutical" in industry):
            return "Biotech"
        else:
            return sector if sector else "Default"
    
    def _calculate_weighted_valuation(self, valuations: Dict, company_type: str) -> float:
        """Calculate weighted average valuation based on method reliability."""
        if not valuations:
            return 0
        
        # Define weights based on company type and method quality
        weights = {
            "SaaS": {
                "rule_of_40": 0.35,
                "unit_economics": 0.30,
                "revenue": 0.20,
                "ebitda": 0.10,
                "terminal_value": 0.05
            },
            "Software": {
                "revenue": 0.30,
                "ebitda": 0.25,
                "rule_of_40": 0.25,
                "terminal_value": 0.15,
                "unit_economics": 0.05
            },
            "E-commerce": {
                "revenue": 0.40,
                "ebitda": 0.30,
                "terminal_value": 0.20,
                "unit_economics": 0.10,
                "rule_of_40": 0.0
            },
            "Default": {
                "ebitda": 0.35,
                "revenue": 0.30,
                "terminal_value": 0.25,
                "rule_of_40": 0.05,
                "unit_economics": 0.05
            }
        }
        
        # Get appropriate weights
        method_weights = weights.get(company_type, weights["Default"])
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for method, val_data in valuations.items():
            if "fair_value" in val_data:
                weight = method_weights.get(method, 0.1)
                
                # Adjust weight based on data quality
                quality = val_data.get("data_quality", "medium")
                if quality == "high":
                    weight *= 1.2
                elif quality == "low":
                    weight *= 0.7
                
                weighted_sum += val_data["fair_value"] * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _select_primary_method(self, valuations: Dict, company_type: str) -> str:
        """Select the primary valuation method to display."""
        # Priority based on company type
        priority_methods = {
            "SaaS": ["rule_of_40", "unit_economics", "revenue", "ebitda"],
            "Software": ["revenue", "rule_of_40", "ebitda", "terminal_value"],
            "E-commerce": ["revenue", "ebitda", "terminal_value"],
            "Default": ["ebitda", "revenue", "terminal_value"]
        }
        
        methods = priority_methods.get(company_type, priority_methods["Default"])
        
        for method in methods:
            if method in valuations:
                return method
        
        # Return first available
        return list(valuations.keys())[0] if valuations else "none"
    
    def _calculate_confidence(self, valuations: Dict) -> str:
        """Calculate confidence level based on number and quality of methods."""
        if not valuations:
            return "low"
        
        # Count high-quality methods
        high_quality_count = sum(1 for v in valuations.values() 
                                  if v.get("data_quality") == "high")
        
        total_methods = len(valuations)
        
        if total_methods >= 3 and high_quality_count >= 2:
            return "high"
        elif total_methods >= 2 and high_quality_count >= 1:
            return "medium"
        else:
            return "low"


def get_zero_fcf_engine():
    """Factory function to get ZeroFCFValuationEngine instance."""
    return ZeroFCFValuationEngine()
