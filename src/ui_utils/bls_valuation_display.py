"""
BLS-Enhanced Valuation Display Component
Shows employment-adjusted DCF valuations and sector rotation signals.

Usage in dashboard:
    from src.ui_utils.bls_valuation_display import show_bls_enhanced_valuation
    show_bls_enhanced_valuation(ticker='AAPL', sector='Technology')
"""

import streamlit as st
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def show_bls_enhanced_valuation(ticker: str, sector: str, base_dcf_value: float, current_price: float):
    """
    Display BLS-adjusted valuation with employment regime context.
    
    Args:
        ticker: Stock ticker
        sector: Stock sector (for sector-specific adjustments)
        base_dcf_value: Original DCF fair value
        current_price: Current stock price
    """
    try:
        from src.analysis.bls_trading_signals import get_bls_analyzer
        
        analyzer = get_bls_analyzer()
        
        st.markdown("---")
        st.subheader("📊 Employment-Adjusted Valuation")
        st.caption("DCF valuation adjusted for BLS employment data • Updated daily")
        
        # Get BLS adjustment
        with st.spinner("Analyzing employment data..."):
            adjustment = analyzer.get_bls_adjusted_dcf_multiplier(sector)
        
        if 'error' in adjustment or adjustment.get('multiplier') is None:
            st.warning(f"⚠️ {adjustment.get('reasoning', 'Unable to calculate BLS adjustment')}")
            return
        
        # Calculate adjusted valuation
        multiplier = adjustment['multiplier']
        adjusted_value = base_dcf_value * multiplier
        base_upside = ((base_dcf_value - current_price) / current_price * 100) if current_price > 0 else 0
        adjusted_upside = ((adjusted_value - current_price) / current_price * 100) if current_price > 0 else 0
        
        # Display comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Base DCF Fair Value",
                value=f"${base_dcf_value:.2f}",
                delta=f"{base_upside:+.1f}%",
                help="Traditional DCF valuation without macro adjustments"
            )
        
        with col2:
            # Color-code the delta based on adjustment
            delta_color = "normal" if multiplier > 1.0 else "inverse"
            st.metric(
                label="📈 Employment-Adjusted",
                value=f"${adjusted_value:.2f}",
                delta=f"{adjusted_upside:+.1f}%",
                delta_color=delta_color,
                help=f"DCF adjusted by {multiplier:.2f}x for employment regime"
            )
        
        with col3:
            st.metric(
                label="Adjustment Impact",
                value=f"{(multiplier - 1) * 100:+.1f}%",
                help="How much employment data changes fair value estimate"
            )
        
        # Explain adjustment
        regime = adjustment.get('regime', 'Unknown')
        confidence = adjustment.get('confidence', 'MEDIUM')
        reasoning = adjustment.get('reasoning', '')
        
        if multiplier > 1.05:
            st.success(f"🟢 **{regime}:** {reasoning}")
        elif multiplier < 0.95:
            st.error(f"🔴 **{regime}:** {reasoning}")
        else:
            st.info(f"⚪ **{regime}:** {reasoning}")
        
        st.caption(f"💡 Confidence: {confidence} | Sector: {sector}")
        
        # Show methodology
        with st.expander("🔍 How Employment Data Affects Valuation"):
            st.markdown(f"""
            **Methodology:**
            - Base DCF: ${base_dcf_value:.2f} (traditional calculation)
            - Employment Regime: {regime}
            - Sector Sensitivity: {sector}
            - Adjustment Multiplier: {multiplier:.2f}x
            - **Adjusted Fair Value: ${adjusted_value:.2f}**
            
            **Why This Matters:**
            - Strong employment → Higher consumer spending → Better earnings
            - Weak employment → Economic slowdown → Lower growth rates
            - Sector-specific sensitivity (e.g., discretionary > staples)
            
            **Confidence Level: {confidence}**
            - HIGH: Strong employment trend (>1% change in 6 months)
            - MEDIUM: Moderate trend (0.5-1% change)
            - LOW: Weak signal (<0.5% change)
            """)
    
    except ImportError:
        st.error("❌ BLS trading signals module not available")
    except Exception as e:
        st.error(f"❌ Error loading BLS valuation: {e}")
        logger.error(f"Error in show_bls_enhanced_valuation: {e}", exc_info=True)


def show_employment_regime_panel():
    """
    Display current employment regime and sector rotation signals.
    Can be shown as sidebar widget or dashboard section.
    """
    try:
        from src.analysis.bls_trading_signals import get_bls_analyzer
        
        analyzer = get_bls_analyzer()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Employment Regime")
        
        with st.spinner("Loading..."):
            regime = analyzer.get_employment_regime()
        
        if 'error' in regime:
            st.sidebar.warning(f"⚠️ {regime['error']}")
            return
        
        signal = regime['signal']
        regime_name = regime['regime']
        
        # Display signal with color coding
        if signal == "BULLISH":
            st.sidebar.success(f"🟢 **{regime_name}**")
        elif signal == "BEARISH":
            st.sidebar.error(f"🔴 **{regime_name}**")
        else:
            st.sidebar.info(f"⚪ **{regime_name}**")
        
        # Key metrics
        st.sidebar.markdown(f"""
        **Unemployment:** {regime['unemployment_rate']:.1f}%  
        **Labor Participation:** {regime['labor_participation']:.1f}%  
        **Confidence:** {regime['confidence']}
        """)
        
        # Sector recommendations
        sectors = regime.get('sectors', {})
        if sectors:
            st.sidebar.markdown(f"**✅ Favor:** {', '.join(sectors.get('Favor', []))}")
            st.sidebar.markdown(f"**❌ Avoid:** {', '.join(sectors.get('Avoid', []))}")
    
    except Exception as e:
        st.sidebar.error(f"Error loading regime: {e}")


def show_sector_rotation_dashboard():
    """
    Full dashboard section for sector rotation based on BLS data.
    """
    try:
        from src.analysis.bls_trading_signals import get_bls_analyzer
        
        st.subheader("🔄 BLS-Based Sector Rotation")
        st.caption("Employment data-driven sector recommendations • Updated daily")
        
        analyzer = get_bls_analyzer()
        
        with st.spinner("Analyzing employment cycle..."):
            rotation = analyzer.get_sector_rotation_signal()
        
        if 'error' in rotation:
            st.error(f"❌ {rotation['error']}")
            return
        
        # Cycle stage header
        stage = rotation['cycle_stage']
        st.markdown(f"### Current Stage: **{stage}**")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Unemployment",
                f"{rotation['unemployment_rate']:.1f}%",
                help="Current unemployment rate"
            )
        
        with col2:
            st.metric(
                "Inflation (CPI)",
                f"{rotation['inflation_rate']:.1f}%",
                help="Year-over-year inflation"
            )
        
        with col3:
            st.metric(
                "Fed Funds Rate",
                f"{rotation['fed_funds_rate']:.2f}%",
                help="Federal Reserve interest rate"
            )
        
        with col4:
            confidence = rotation['confidence']
            emoji = "🟢" if confidence == "HIGH" else ("🟡" if confidence == "MEDIUM" else "🔴")
            st.metric(
                "Signal Confidence",
                f"{emoji} {confidence}",
                help="Strength of rotation signal"
            )
        
        # Strategy recommendation
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Overweight Sectors")
            for sector in rotation['top_sectors']:
                st.markdown(f"- **{sector}**")
        
        with col2:
            st.markdown("#### ❌ Underweight Sectors")
            for sector in rotation['avoid_sectors']:
                st.markdown(f"- **{sector}**")
        
        # Strategy explanation
        st.info(f"💡 **Strategy:** {rotation['strategy']}")
        
        # Inflation alert
        inflation_alert = analyzer.get_wage_inflation_alert()
        if inflation_alert.get('alert'):
            st.warning(f"⚠️ {inflation_alert['message']}")
            
            if inflation_alert.get('impact'):
                with st.expander("📊 View Sector-Specific Impact"):
                    for sector, impact in inflation_alert['impact'].items():
                        st.markdown(f"**{sector}:** {impact}")
        
        # Last updated
        st.caption(f"Last updated: {rotation.get('updated', 'Unknown')}")
    
    except ImportError:
        st.error("❌ BLS trading signals module not available")
    except Exception as e:
        st.error(f"❌ Error loading sector rotation: {e}")
        logger.error(f"Error in show_sector_rotation_dashboard: {e}", exc_info=True)
