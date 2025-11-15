"""
BLS-Enhanced Trading Signals & Valuation
Integrates Bureau of Labor Statistics data for actionable trading insights.

Key Concept:
Employment data leads stock market moves by 1-3 months. By tracking BLS metrics
(unemployment, labor participation, wage growth), we can anticipate sector rotations
and adjust DCF valuations for macro headwinds/tailwinds.

Trading Signals:
1. Employment Strength → Consumer Discretionary BULLISH
2. Wage Growth → Inflation → Tech/Growth BEARISH (higher discount rates)
3. Low Unemployment → Fed tightening risk → Rate-sensitive sectors BEARISH
4. Rising Labor Participation → Economic recovery → Cyclicals BULLISH
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
import streamlit as st

logger = logging.getLogger(__name__)


class BLSEnhancedAnalyzer:
    """
    Combines BLS employment data with stock valuation & trading signals.
    """
    
    def __init__(self):
        """Initialize with economic data pipeline."""
        try:
            from src.pipelines.get_economic_data import get_economic_data_pipeline
            self.economic_pipeline = get_economic_data_pipeline()
        except ImportError:
            logger.warning("Economic data pipeline not available")
            self.economic_pipeline = None
    
    def get_employment_regime(self) -> Dict:
        """
        Determine current employment regime for sector rotation.
        
        Returns:
            Dict with regime classification and sector recommendations
        """
        if not self.economic_pipeline:
            return {'error': 'Economic data not available'}
        
        try:
            # Get latest employment data
            employment = self.economic_pipeline.get_bls_employment_data(years=2)
            unemployment = self.economic_pipeline.get_unemployment_data(years=2)
            
            if employment is None or unemployment is None:
                return {'error': 'Unable to fetch employment data'}
            
            # Get latest values
            latest_participation = employment['labor_force_participation'].iloc[-1]
            prev_participation = employment['labor_force_participation'].iloc[-6]  # 6 months ago
            
            latest_unemployment = unemployment['unemployment_rate'].iloc[-1]
            prev_unemployment = unemployment['unemployment_rate'].iloc[-6]
            
            # Calculate trends
            participation_trend = latest_participation - prev_participation
            unemployment_trend = latest_unemployment - prev_unemployment
            
            # Classify regime
            if latest_unemployment < 4.0 and participation_trend > 0:
                regime = "Strong Employment"
                signal = "BULLISH"
                sectors = {
                    "Favor": ["Consumer Discretionary", "Financials", "Industrials"],
                    "Avoid": ["Utilities", "Consumer Staples"],
                    "Reasoning": "Low unemployment + rising participation = strong economy, favor cyclicals"
                }
            elif latest_unemployment > 6.0 or unemployment_trend > 0.5:
                regime = "Weak Employment"
                signal = "BEARISH"
                sectors = {
                    "Favor": ["Consumer Staples", "Utilities", "Healthcare"],
                    "Avoid": ["Consumer Discretionary", "Small Caps"],
                    "Reasoning": "Rising unemployment = recession risk, favor defensives"
                }
            elif participation_trend > 0.2:
                regime = "Expanding Labor Force"
                signal = "BULLISH"
                sectors = {
                    "Favor": ["Industrials", "Materials", "Financials"],
                    "Avoid": ["Bonds", "Utilities"],
                    "Reasoning": "Growing labor force = economic expansion, favor cyclicals"
                }
            else:
                regime = "Neutral Employment"
                signal = "NEUTRAL"
                sectors = {
                    "Favor": ["Balanced Portfolio", "SPY", "Diversified"],
                    "Avoid": ["None"],
                    "Reasoning": "Stable employment metrics, no strong directional signal"
                }
            
            return {
                'regime': regime,
                'signal': signal,
                'unemployment_rate': latest_unemployment,
                'unemployment_trend': unemployment_trend,
                'labor_participation': latest_participation,
                'participation_trend': participation_trend,
                'sectors': sectors,
                'confidence': self._calculate_confidence(unemployment_trend, participation_trend)
            }
            
        except Exception as e:
            logger.error(f"Error calculating employment regime: {e}")
            return {'error': str(e)}
    
    def _calculate_confidence(self, unemployment_trend: float, participation_trend: float) -> str:
        """Calculate confidence level based on trend strength."""
        combined_signal = abs(unemployment_trend) + abs(participation_trend * 2)
        
        if combined_signal > 1.0:
            return "HIGH"
        elif combined_signal > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_bls_adjusted_dcf_multiplier(self, sector: str) -> Dict:
        """
        Calculate DCF adjustment multiplier based on BLS data.
        
        Strong employment → Higher consumer spending → Higher growth rates
        Weak employment → Lower earnings → Lower terminal values
        
        Args:
            sector: Stock sector (e.g., "Consumer Discretionary", "Technology")
            
        Returns:
            Dict with adjustment multiplier and reasoning
        """
        if not self.economic_pipeline:
            return {'multiplier': 1.0, 'reasoning': 'Economic data not available'}
        
        try:
            regime = self.get_employment_regime()
            
            if 'error' in regime:
                return {'multiplier': 1.0, 'reasoning': regime['error']}
            
            # Sector sensitivity to employment
            sector_sensitivity = {
                "Consumer Discretionary": 1.5,  # High sensitivity
                "Consumer Staples": 0.5,        # Low sensitivity
                "Financials": 1.2,
                "Industrials": 1.3,
                "Technology": 0.8,
                "Healthcare": 0.6,
                "Utilities": 0.4,
                "Real Estate": 0.9,
                "Materials": 1.1,
                "Energy": 0.7
            }
            
            sensitivity = sector_sensitivity.get(sector, 1.0)
            
            # Calculate adjustment based on regime
            unemployment_impact = -regime['unemployment_trend'] * 0.1  # Lower unemployment = positive
            participation_impact = regime['participation_trend'] * 0.05  # Higher participation = positive
            
            # Apply sector sensitivity
            total_adjustment = (unemployment_impact + participation_impact) * sensitivity
            multiplier = 1.0 + total_adjustment
            
            # Clamp between 0.7 and 1.3 (±30%)
            multiplier = max(0.7, min(1.3, multiplier))
            
            # Reasoning
            if multiplier > 1.1:
                reasoning = f"Strong employment tailwind for {sector}. Upgrade growth assumptions."
            elif multiplier < 0.9:
                reasoning = f"Weak employment headwind for {sector}. Downgrade growth assumptions."
            else:
                reasoning = f"Neutral employment impact for {sector}."
            
            return {
                'multiplier': multiplier,
                'reasoning': reasoning,
                'regime': regime['regime'],
                'confidence': regime['confidence']
            }
            
        except Exception as e:
            logger.error(f"Error calculating BLS DCF multiplier: {e}")
            return {'multiplier': 1.0, 'reasoning': f'Error: {e}'}
    
    def get_wage_inflation_alert(self) -> Dict:
        """
        Check for wage inflation that could impact Fed policy & valuations.
        
        Rising wages → Inflation → Fed hikes → Higher discount rates → Lower valuations
        """
        if not self.economic_pipeline:
            return {'alert': False, 'message': 'Economic data not available'}
        
        try:
            # Get CPI data as proxy for wage growth pressure
            inflation = self.economic_pipeline.get_inflation_data(years=2)
            
            if inflation is None or len(inflation) == 0:
                return {'alert': False, 'message': 'Inflation data unavailable'}
            
            # Check latest 3-month trend
            latest_cpi = inflation['yoy_change'].iloc[-1]
            three_month_avg = inflation['yoy_change'].iloc[-3:].mean()
            
            # Alert thresholds
            if latest_cpi > 4.0 and three_month_avg > 3.5:
                alert = True
                severity = "HIGH"
                message = f"⚠️ HIGH INFLATION ALERT: {latest_cpi:.1f}% YoY. Expect Fed hawkishness."
                impact = {
                    "Growth Stocks": "BEARISH - Higher discount rates compress valuations",
                    "Value Stocks": "NEUTRAL - More resilient to rate hikes",
                    "Bonds": "BEARISH - Rising rates = falling bond prices",
                    "Commodities": "BULLISH - Inflation hedge",
                    "REITs": "BEARISH - Rate-sensitive"
                }
            elif latest_cpi > 3.0:
                alert = True
                severity = "MEDIUM"
                message = f"⚠️ Elevated inflation: {latest_cpi:.1f}% YoY. Monitor Fed commentary."
                impact = {
                    "Growth Stocks": "CAUTION - Valuations may compress",
                    "Financials": "BULLISH - Benefit from higher rates",
                    "Commodities": "BULLISH - Inflation hedge"
                }
            else:
                alert = False
                severity = "LOW"
                message = f"✅ Benign inflation: {latest_cpi:.1f}% YoY. No immediate concern."
                impact = {
                    "All Sectors": "NEUTRAL - Stable inflation environment"
                }
            
            return {
                'alert': alert,
                'severity': severity,
                'message': message,
                'current_inflation': latest_cpi,
                'three_month_avg': three_month_avg,
                'impact': impact
            }
            
        except Exception as e:
            logger.error(f"Error checking wage inflation: {e}")
            return {'alert': False, 'message': f'Error: {e}'}
    
    def get_sector_rotation_signal(self) -> Dict:
        """
        Generate sector rotation recommendations based on BLS + Fed data.
        
        Employment cycle dictates sector performance:
        - Early recovery: Cyclicals (Industrials, Materials)
        - Mid-cycle: Broad market (Tech, Discretionary)
        - Late-cycle: Defensives (Staples, Utilities)
        - Recession: Safe havens (Treasuries, Healthcare)
        """
        if not self.economic_pipeline:
            return {'error': 'Economic data not available'}
        
        try:
            regime = self.get_employment_regime()
            inflation_alert = self.get_wage_inflation_alert()
            fed_data = self.economic_pipeline.get_interest_rate_data(years=1)
            
            if 'error' in regime:
                return regime
            
            # Determine cycle stage
            unemployment = regime['unemployment_rate']
            unemployment_trend = regime['unemployment_trend']
            participation_trend = regime['participation_trend']
            
            # Get Fed rate trend
            if fed_data is not None and len(fed_data) > 0:
                latest_fed_rate = fed_data['fed_funds_rate'].iloc[-1]
                fed_trend = fed_data['fed_funds_rate'].iloc[-1] - fed_data['fed_funds_rate'].iloc[-6]
            else:
                latest_fed_rate = 5.0  # Default
                fed_trend = 0
            
            # Classify cycle stage
            if unemployment > 6.0 and unemployment_trend > 0:
                stage = "Recession/Early Recovery"
                top_sectors = ["Healthcare", "Consumer Staples", "Utilities"]
                avoid_sectors = ["Financials", "Industrials", "Consumer Discretionary"]
                strategy = "Defensive positioning. Wait for employment stabilization."
                
            elif unemployment < 5.0 and participation_trend > 0 and fed_trend <= 0:
                stage = "Early/Mid Expansion"
                top_sectors = ["Technology", "Consumer Discretionary", "Financials"]
                avoid_sectors = ["Utilities", "Consumer Staples"]
                strategy = "Aggressive growth positioning. Favor high-beta sectors."
                
            elif unemployment < 4.5 and inflation_alert['current_inflation'] > 3.5:
                stage = "Late Cycle"
                top_sectors = ["Energy", "Materials", "Financials"]
                avoid_sectors = ["Tech Growth", "Long Duration Bonds"]
                strategy = "Inflation hedge. Rotate to value and commodities."
                
            else:
                stage = "Mid Cycle"
                top_sectors = ["Broad Market (SPY)", "Quality Growth", "Dividend Aristocrats"]
                avoid_sectors = ["Speculative Growth"]
                strategy = "Balanced approach. Focus on quality and cash flow."
            
            return {
                'cycle_stage': stage,
                'top_sectors': top_sectors,
                'avoid_sectors': avoid_sectors,
                'strategy': strategy,
                'unemployment_rate': unemployment,
                'inflation_rate': inflation_alert.get('current_inflation', 0),
                'fed_funds_rate': latest_fed_rate,
                'confidence': regime.get('confidence', 'MEDIUM'),
                'updated': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error generating sector rotation signal: {e}")
            return {'error': str(e)}


# Singleton instance
_analyzer = None

def get_bls_analyzer():
    """Get or create BLS analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = BLSEnhancedAnalyzer()
    return _analyzer
