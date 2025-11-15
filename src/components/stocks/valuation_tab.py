"""
Valuation Tab Component
Displays DCF, multiples valuation, and fair value calculations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging

from src.ui_utils.formatters import format_currency, format_percentage
from src.ui_utils.design_system import get_color

logger = logging.getLogger(__name__)


def show_valuation_tab(data, components):
    """
    Show valuation analysis (Due Diligence)
    
    Args:
        data: Dict containing ticker, fundamentals, stock_data
        components: Dict containing valuation components
    """
    st.subheader("💰 Valuation DD (Due Diligence)")
    
    try:
        info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
        
        if not info:
            st.warning("⚠️ No stock info available for valuation analysis")
            return
        
        # Calculate valuation
        valuation = components["valuation"].calculate_dcf(data.get("fundamentals", {}), info)
        if "error" in valuation:
            valuation = components["valuation"].calculate_multiples_valuation(info)
    except Exception as e:
        st.error(f"❌ Error loading valuation data: {str(e)}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_fair_value(valuation, data)
    
    with col2:
        _render_multiples(info)
    
    # Zero-FCF and enhanced valuation
    _render_advanced_valuation(data, info)


def _render_fair_value(valuation: dict, data: dict):
    """Render fair value calculation and scenarios"""
    if "error" not in valuation:
        st.markdown("### 🧮 Fair Value Calc")
        
        fair_value = valuation.get('fair_value', 0)
        current_price = valuation.get('current_price', 0)
        upside = valuation.get('upside', 0)
        
        # Check for invalid valuation
        if fair_value <= 0 or current_price <= 0:
            st.error("❌ **Cannot Calculate Fair Value**")
            st.markdown("""
            **Possible reasons:**
            - Insufficient financial data (company too new)
            - Negative or missing cash flows
            - Missing balance sheet information
            
            **What to try:**
            - Use the **🎛️ Interactive DCF** tab to manually input values
            - Check the **📐 Multiples** section for alternative valuation methods
            - Try a more established company ticker
            """)
        else:
            st.markdown(f"**Fair Value:** {format_currency(fair_value)}")
            st.markdown(f"**Current Price:** {format_currency(current_price)}")
            
            if upside > 20:
                st.success(f"**Upside:** {format_percentage(upside)} 🚀 (UNDERVALUED!)")
            elif upside > 0:
                st.info(f"**Upside:** {format_percentage(upside)} 📈")
            else:
                st.warning(f"**Downside:** {format_percentage(upside)} 📉")
            
            st.markdown(f"**Method:** {valuation.get('method', 'Unknown')}")
        
        # Scenarios chart
        if "scenarios" in valuation and fair_value > 0:
            _render_scenarios_chart(valuation, current_price)
        
        # BLS-Enhanced Valuation
        if fair_value > 0:
            try:
                from src.ui_utils.bls_valuation_display import show_bls_enhanced_valuation
                sector = data["stock_data"].get("info", {}).get('sector', 'Unknown')
                show_bls_enhanced_valuation(
                    ticker=data.get("ticker", ""),
                    sector=sector,
                    base_dcf_value=fair_value,
                    current_price=current_price
                )
            except Exception as e:
                st.info("💡 BLS employment analysis available with additional setup")
                logger.debug(f"BLS module not available: {e}")
    else:
        st.warning(f"⚠️ Valuation unavailable: {valuation.get('error', 'Unknown error')}")


def _render_scenarios_chart(valuation: dict, current_price: float):
    """Render bear/base/bull scenarios chart"""
    st.markdown("### 📊 Price Scenarios")
    try:
        scenarios_df = pd.DataFrame({
            'Scenario': ['🐻 Bear', '📊 Base', '🚀 Bull'],
            'Price': [
                valuation['scenarios']['bear'],
                valuation['scenarios']['base'],
                valuation['scenarios']['bull']
            ]
        })
        
        fig = go.Figure(data=[
            go.Bar(
                x=scenarios_df['Scenario'],
                y=scenarios_df['Price'],
                marker_color=[get_color('danger'), get_color('warning'), get_color('success')]
            )
        ])
        
        if current_price and current_price > 0:
            fig.add_hline(
                y=current_price, 
                line_dash="dash", 
                line_color="white",
                annotation_text="Current Price"
            )
        
        fig.update_layout(
            yaxis_title="Price ($)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating scenarios chart: {str(e)}")


def _render_multiples(info: dict):
    """Render valuation multiples"""
    st.markdown("### 📐 Multiples")
    
    multiples = {
        "P/E": info.get('trailingPE', 0),
        "Forward P/E": info.get('forwardPE', 0),
        "P/B": info.get('priceToBook', 0),
        "P/S": info.get('priceToSalesTrailing12Months', 0),
        "PEG": info.get('pegRatio', 0),
    }
    
    multiples = {k: v for k, v in multiples.items() if v > 0}
    
    if multiples:
        for metric, value in multiples.items():
            if metric == "PEG" and value < 1:
                st.success(f"**{metric}:** {value:.2f} (CHEAP! 🤑)")
            elif metric == "P/E" and value < 15:
                st.success(f"**{metric}:** {value:.2f} (Value play! 💰)")
            else:
                st.markdown(f"**{metric}:** {value:.2f}")
    else:
        st.info("No multiples data available")


def _render_advanced_valuation(data: dict, info: dict):
    """Render zero-FCF and enhanced valuation"""
    st.markdown("---")
    st.markdown("### 🎯 Zero-FCF Valuation (High-Growth Alternative)")
    st.markdown("*For companies with negative or minimal free cash flow*")
    
    try:
        from zero_fcf_valuation import ZeroFCFValuationEngine
        from src.ui_utils.zero_fcf_display import show_zero_fcf_valuation_tab
        
        ticker = data.get("ticker", "")
        
        if info:
            engine = ZeroFCFValuationEngine()
            
            with st.spinner("Calculating Zero-FCF valuation..."):
                result = engine.calculate_valuation(
                    ticker=ticker,
                    info=info,
                    financials=data.get("financials", {})
                )
            
            if result and "error" not in result:
                show_zero_fcf_valuation_tab(result, ticker)
            else:
                st.info("Zero-FCF valuation not available for this ticker")
    except Exception as e:
        logger.debug(f"Zero-FCF module not available: {e}")
        st.info("💡 Zero-FCF valuation available with additional setup")
