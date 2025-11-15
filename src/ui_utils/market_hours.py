"""
Market Hours Indicator
Shows if US stock market is open/closed/pre-market/after-hours
"""

from datetime import datetime, time
from typing import Dict, Tuple
import pytz


class MarketHours:
    """Check if US stock market is open"""
    
    # US Eastern timezone
    ET = pytz.timezone('US/Eastern')
    
    # Market hours (Eastern Time)
    MARKET_OPEN = time(9, 30)
    MARKET_CLOSE = time(16, 0)
    PREMARKET_OPEN = time(4, 0)
    AFTERHOURS_CLOSE = time(20, 0)
    
    @classmethod
    def get_market_status(cls) -> Dict[str, any]:
        """
        Get current market status
        
        Returns:
            Dict with status, emoji, color, and message
        """
        now_et = datetime.now(cls.ET)
        current_time = now_et.time()
        current_day = now_et.weekday()  # Monday = 0, Sunday = 6
        
        # Weekend check
        if current_day >= 5:  # Saturday or Sunday
            return {
                "status": "closed",
                "emoji": "🛑",
                "color": "#FF3860",
                "message": "Market Closed - Weekend",
                "detail": "Markets open Monday 9:30 AM ET"
            }
        
        # Check market hours
        if cls.MARKET_OPEN <= current_time < cls.MARKET_CLOSE:
            return {
                "status": "open",
                "emoji": "🟢",
                "color": "#00FF88",
                "message": "Market Open",
                "detail": f"Closes at 4:00 PM ET ({cls._time_until_close(current_time)})"
            }
        
        # Pre-market (4:00 AM - 9:30 AM)
        elif cls.PREMARKET_OPEN <= current_time < cls.MARKET_OPEN:
            return {
                "status": "pre-market",
                "emoji": "🟡",
                "color": "#FFB627",
                "message": "Pre-Market",
                "detail": f"Market opens at 9:30 AM ET ({cls._time_until_open(current_time)})"
            }
        
        # After-hours (4:00 PM - 8:00 PM)
        elif cls.MARKET_CLOSE <= current_time < cls.AFTERHOURS_CLOSE:
            return {
                "status": "after-hours",
                "emoji": "🟠",
                "color": "#FF9500",
                "message": "After Hours",
                "detail": f"After-hours ends at 8:00 PM ET"
            }
        
        # Closed overnight
        else:
            return {
                "status": "closed",
                "emoji": "🛑",
                "color": "#FF3860",
                "message": "Market Closed",
                "detail": f"Pre-market opens at 4:00 AM ET"
            }
    
    @classmethod
    def _time_until_open(cls, current_time: time) -> str:
        """Calculate time until market opens"""
        now_minutes = current_time.hour * 60 + current_time.minute
        open_minutes = cls.MARKET_OPEN.hour * 60 + cls.MARKET_OPEN.minute
        diff = open_minutes - now_minutes
        
        hours = diff // 60
        minutes = diff % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    @classmethod
    def _time_until_close(cls, current_time: time) -> str:
        """Calculate time until market closes"""
        now_minutes = current_time.hour * 60 + current_time.minute
        close_minutes = cls.MARKET_CLOSE.hour * 60 + cls.MARKET_CLOSE.minute
        diff = close_minutes - now_minutes
        
        hours = diff // 60
        minutes = diff % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    @classmethod
    def is_market_open(cls) -> bool:
        """Simple check if market is currently open"""
        status = cls.get_market_status()
        return status["status"] == "open"
    
    @classmethod
    def get_next_market_open(cls) -> str:
        """Get human-readable time for next market open"""
        now_et = datetime.now(cls.ET)
        current_day = now_et.weekday()
        current_time = now_et.time()
        
        # If weekend, return Monday
        if current_day >= 5:
            days_until_monday = 7 - current_day
            return f"Monday at 9:30 AM ET ({days_until_monday} days)"
        
        # If before pre-market
        if current_time < cls.PREMARKET_OPEN:
            return "Today at 9:30 AM ET"
        
        # If during trading day but after close
        if current_time >= cls.MARKET_CLOSE:
            return "Tomorrow at 9:30 AM ET"
        
        # During trading hours or pre-market
        return "Market is open or opening soon"


def render_market_status_badge():
    """
    Render market status badge in Streamlit
    Returns HTML string for inline display
    """
    status = MarketHours.get_market_status()
    
    html = f"""
    <div style="
        display: inline-block;
        background: {status['color']}22;
        border: 2px solid {status['color']};
        border-radius: 20px;
        padding: 6px 16px;
        margin: 10px 0;
        font-weight: 600;
    ">
        <span style="font-size: 1.2rem;">{status['emoji']}</span>
        <span style="margin-left: 8px; color: {status['color']};">
            {status['message']}
        </span>
    </div>
    <div style="
        font-size: 0.85rem;
        color: #b0b0b0;
        margin-top: 4px;
    ">
        {status['detail']}
    </div>
    """
    
    return html


def render_compact_market_status():
    """Render compact market status for sidebar or header"""
    status = MarketHours.get_market_status()
    
    html = f"""
    <div style="
        display: inline-flex;
        align-items: center;
        background: {status['color']}15;
        border-left: 3px solid {status['color']};
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.9rem;
    ">
        <span style="margin-right: 6px;">{status['emoji']}</span>
        <span style="font-weight: 600; color: {status['color']};">
            {status['message']}
        </span>
    </div>
    """
    
    return html


# Example usage
if __name__ == "__main__":
    import streamlit as st
    
    st.set_page_config(page_title="Market Hours Demo", layout="wide")
    
    st.title("📊 Market Hours Indicator Demo")
    
    # Full badge
    st.markdown("### Full Badge")
    st.markdown(render_market_status_badge(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Compact badge
    st.markdown("### Compact Badge (for sidebar/header)")
    st.markdown(render_compact_market_status(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed info
    st.markdown("### Detailed Information")
    
    status = MarketHours.get_market_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", status['status'].replace('-', ' ').title())
    
    with col2:
        st.metric("Emoji", status['emoji'])
    
    with col3:
        st.metric("Is Open?", "Yes" if MarketHours.is_market_open() else "No")
    
    with col4:
        now_et = datetime.now(MarketHours.ET)
        st.metric("ET Time", now_et.strftime("%I:%M %p"))
    
    st.markdown("---")
    
    # Next open time
    st.info(f"**Next Market Open:** {MarketHours.get_next_market_open()}")
    
    # Refresh button
    if st.button("🔄 Refresh"):
        st.rerun()
