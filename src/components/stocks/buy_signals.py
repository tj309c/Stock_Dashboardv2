"""
Buy Signals Component
Displays buy/sell recommendations with WSB-style humor
"""
import streamlit as st
import pandas as pd

from src.ui_utils.formatters import format_currency, format_percentage
from src.ui_utils.design_system import get_color
from wsb_quotes import get_confidence_message


def show_buy_signal_section(data, components, diamond_hands=True):
    """
    Display the buy signal analysis section with ape-approved metrics
    
    Args:
        data: Dict containing ticker, df, stock_data, sentiment, fundamentals
        components: Dict containing analysis components (goodbuy, valuation, technical)
        diamond_hands: Whether to show diamond hands messaging (default: True)
    """
    df = data.get("df", pd.DataFrame())
    info = data["stock_data"].get("info", {}) if data.get("stock_data") else {}
    
    # Run analysis
    valuation = components["valuation"].calculate_dcf(data["fundamentals"], info)
    if "error" in valuation:
        valuation = components["valuation"].calculate_multiples_valuation(info)
    
    technical = components["technical"].analyze(df) if not df.empty else {}
    sentiment = data["sentiment"]["stocktwits"]
    
    buy_analysis = components["goodbuy"].analyze_buy_opportunity(
        data["ticker"], valuation, technical, sentiment, info, df
    )
    
    # Display section
    st.markdown("---")
    _render_buy_metrics(buy_analysis, info)
    _render_buy_recommendation(buy_analysis)


def _render_buy_metrics(buy_analysis: dict, info: dict):
    """Render buy signal metrics in columns"""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    current_price = buy_analysis["current_price"]
    buy_low = buy_analysis["buy_range"]["low"]
    buy_high = buy_analysis["buy_range"]["high"]
    target = buy_analysis["target_price"]
    confidence = buy_analysis["total_score"]
    
    # Current price
    with col1:
        prev_close = info.get('previousClose', current_price)
        price_change = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
        price_emoji = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "⚪"
        
        st.metric(
            f"{price_emoji} Bag Holding At",
            format_currency(current_price),
            format_percentage(price_change) + (
                " (green is good)" if price_change > 0 
                else " (ouch)" if price_change < 0 
                else ""
            )
        )
    
    # Buy zone
    with col2:
        color = (
            get_color('success') if confidence >= 70 
            else get_color('warning') if confidence >= 50 
            else get_color('danger')
        )
        emoji = (
            "🚀🌕" if confidence >= 70 
            else "📈💰" if confidence >= 50 
            else "🤔🎰"
        )
        zone_label = (
            "APE ENTRY ZONE" if confidence >= 70 
            else "MAYBE BUY?" if confidence >= 50 
            else "WAIT FOR DIP"
        )
        
        st.markdown(f"""
        <div style="background: {color}20; border: 2px solid {color}; padding: 10px; border-radius: 10px; text-align: center;">
            <h3 style="color: {color}; margin: 0;">{emoji} {zone_label}</h3>
            <h2 style="color: #FFFFFF; margin: 5px 0;">{format_currency(buy_low)} - {format_currency(buy_high)}</h2>
            <p style="color: #E0E0E0; font-size: 0.8em; margin: 0;">(Not financial advice, obviously)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Target price
    with col3:
        upside = ((target - current_price) / current_price * 100) if current_price > 0 else 0
        target_label = (
            "🌕 Moon Price" if upside > 50 
            else "🎯 Realistic Target" if upside > 20 
            else "💼 Conservative"
        )
        
        st.metric(
            target_label,
            format_currency(target),
            f"+{upside:.1f}%" + (
                " 🚀🚀🚀" if upside > 50 
                else " 🚀" if upside > 20 
                else ""
            )
        )
    
    # Confidence score
    with col4:
        confidence_emoji = (
            "🔥💎" if confidence >= 70 
            else "👍📊" if confidence >= 50 
            else "🤷‍♂️🎲"
        )
        
        st.metric(
            f"{confidence_emoji} Autism Level",
            f"{confidence:.0f}/100",
            buy_analysis["confidence"] + " trust"
        )
    
    # Buy signals
    if buy_analysis.get("signals"):
        signals_text = " | ".join(buy_analysis["signals"][:3])
        st.success(f"**🦍 Ape Signals:** {signals_text}")


def _render_buy_recommendation(buy_analysis: dict):
    """Render final buy/sell recommendation with WSB humor"""
    rec = buy_analysis["recommendation"]
    confidence = buy_analysis["total_score"]
    
    rec_color = (
        get_color('success') if rec == "STRONG BUY" 
        else get_color('warning') if rec == "BUY" 
        else get_color('danger')
    )
    rec_emoji = (
        "💎🙌" if rec == "STRONG BUY" 
        else "👍" if rec == "BUY" 
        else "🧻👎"
    )
    
    # Get WSB-style message
    wsb_message = get_confidence_message(confidence)
    
    # Humor message based on recommendation
    humor_msg = (
        "HODL with diamond hands! 💎🙌" if rec == "STRONG BUY"
        else "Solid play, ape! 🦍" if rec == "BUY"
        else "Maybe wait behind the Wendy's dumpster... 🗑️"
    )
    
    st.markdown(f"""
    <div style="background: {rec_color}20; border: 2px solid {rec_color}; padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0;">
        <h1 style="color: {rec_color}; margin: 0;">{rec_emoji} {rec}</h1>
        <p style="color: #FFFFFF; font-size: 1.1em; margin: 10px 0;"><i>"{wsb_message}"</i></p>
        <p style="color: #FFFFFF;">
            Risk/Reward: {buy_analysis['risk_reward_ratio']:.2f} | 
            Stop Loss: {format_currency(buy_analysis['stop_loss'])}
        </p>
        <p style="color: #E0E0E0; font-size: 0.8em;">{humor_msg}</p>
    </div>
    """, unsafe_allow_html=True)
