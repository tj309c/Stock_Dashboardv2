"""
Watchlist Manager - Favorites/Quick Access for Tickers
Allows users to save frequently viewed tickers for quick access
"""

import streamlit as st
import json
from typing import List, Dict
from datetime import datetime


class WatchlistManager:
    """Manages user's watchlist/favorites for quick ticker access"""
    
    def __init__(self):
        """Initialize watchlist from session state"""
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
        
        if 'watchlist_metadata' not in st.session_state:
            st.session_state.watchlist_metadata = {}
    
    def add_ticker(self, ticker: str, name: str = None) -> bool:
        """
        Add ticker to watchlist
        
        Args:
            ticker: Stock ticker symbol
            name: Optional company name
            
        Returns:
            True if added, False if already exists
        """
        ticker = ticker.upper().strip()
        
        if ticker in st.session_state.watchlist:
            return False
        
        st.session_state.watchlist.append(ticker)
        st.session_state.watchlist_metadata[ticker] = {
            'name': name or ticker,
            'added_date': datetime.now().isoformat(),
            'last_viewed': datetime.now().isoformat()
        }
        
        return True
    
    def remove_ticker(self, ticker: str) -> bool:
        """
        Remove ticker from watchlist
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if removed, False if not in watchlist
        """
        ticker = ticker.upper().strip()
        
        if ticker not in st.session_state.watchlist:
            return False
        
        st.session_state.watchlist.remove(ticker)
        if ticker in st.session_state.watchlist_metadata:
            del st.session_state.watchlist_metadata[ticker]
        
        return True
    
    def is_in_watchlist(self, ticker: str) -> bool:
        """Check if ticker is in watchlist"""
        return ticker.upper().strip() in st.session_state.watchlist
    
    def get_watchlist(self) -> List[str]:
        """Get all tickers in watchlist"""
        return st.session_state.watchlist.copy()
    
    def update_last_viewed(self, ticker: str):
        """Update last viewed timestamp for a ticker"""
        ticker = ticker.upper().strip()
        if ticker in st.session_state.watchlist_metadata:
            st.session_state.watchlist_metadata[ticker]['last_viewed'] = datetime.now().isoformat()
    
    def get_metadata(self, ticker: str) -> Dict:
        """Get metadata for a ticker"""
        ticker = ticker.upper().strip()
        return st.session_state.watchlist_metadata.get(ticker, {})
    
    def clear_watchlist(self):
        """Clear entire watchlist"""
        st.session_state.watchlist = []
        st.session_state.watchlist_metadata = {}
    
    def export_watchlist(self) -> str:
        """Export watchlist as JSON string"""
        data = {
            'watchlist': st.session_state.watchlist,
            'metadata': st.session_state.watchlist_metadata,
            'exported_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2)
    
    def import_watchlist(self, json_str: str) -> bool:
        """
        Import watchlist from JSON string
        
        Args:
            json_str: JSON string with watchlist data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = json.loads(json_str)
            st.session_state.watchlist = data.get('watchlist', [])
            st.session_state.watchlist_metadata = data.get('metadata', {})
            return True
        except Exception:
            return False


def render_watchlist_sidebar():
    """Render watchlist in sidebar with quick actions"""
    
    manager = WatchlistManager()
    watchlist = manager.get_watchlist()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⭐ Watchlist")
        
        if not watchlist:
            st.info("No tickers in watchlist yet.\nAdd tickers by clicking ⭐ next to ticker input.")
        else:
            # Display watchlist with quick select buttons
            for ticker in watchlist:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Quick select button
                    if st.button(f"📊 {ticker}", key=f"watchlist_select_{ticker}", use_container_width=True):
                        st.session_state.ticker = ticker
                        manager.update_last_viewed(ticker)
                        st.rerun()
                
                with col2:
                    # Remove button
                    if st.button("❌", key=f"watchlist_remove_{ticker}"):
                        manager.remove_ticker(ticker)
                        st.success(f"Removed {ticker}")
                        st.rerun()
            
            # Watchlist management
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Export", use_container_width=True):
                    json_data = manager.export_watchlist()
                    st.download_button(
                        label="Download",
                        data=json_data,
                        file_name=f"watchlist_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        key="download_watchlist"
                    )
            
            with col2:
                if st.button("🗑️ Clear All", use_container_width=True):
                    if st.session_state.get('confirm_clear_watchlist'):
                        manager.clear_watchlist()
                        st.session_state.confirm_clear_watchlist = False
                        st.success("Watchlist cleared!")
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_watchlist = True
                        st.warning("Click again to confirm")


def render_add_to_watchlist_button(ticker: str, name: str = None):
    """
    Render add/remove watchlist button next to ticker input
    
    Args:
        ticker: Current ticker symbol
        name: Optional company name
    """
    if not ticker:
        return
    
    manager = WatchlistManager()
    is_favorite = manager.is_in_watchlist(ticker)
    
    if is_favorite:
        # Remove from watchlist button
        if st.button("⭐ Remove from Watchlist", key=f"remove_watchlist_{ticker}"):
            manager.remove_ticker(ticker)
            st.success(f"Removed {ticker} from watchlist")
            st.rerun()
    else:
        # Add to watchlist button
        if st.button("☆ Add to Watchlist", key=f"add_watchlist_{ticker}"):
            manager.add_ticker(ticker, name)
            st.success(f"Added {ticker} to watchlist!")
            st.rerun()


def render_watchlist_import():
    """Render watchlist import interface"""
    
    st.markdown("### 📥 Import Watchlist")
    
    uploaded_file = st.file_uploader(
        "Upload watchlist JSON file",
        type=['json'],
        key="watchlist_import_file"
    )
    
    if uploaded_file:
        try:
            json_str = uploaded_file.read().decode('utf-8')
            manager = WatchlistManager()
            
            if manager.import_watchlist(json_str):
                st.success(f"✅ Successfully imported {len(manager.get_watchlist())} tickers!")
                st.rerun()
            else:
                st.error("❌ Invalid watchlist file format")
        except Exception as e:
            st.error(f"❌ Error importing watchlist: {str(e)}")


def get_popular_tickers() -> Dict[str, List[str]]:
    """Get categorized list of popular tickers for quick add"""
    return {
        "Tech Giants": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA"],
        "Indices": ["SPY", "QQQ", "DIA", "IWM"],
        "Crypto": ["BTC-USD", "ETH-USD", "DOGE-USD"],
        "Meme Stocks": ["GME", "AMC", "PLTR", "BBBY", "BB"],
        "Finance": ["JPM", "BAC", "GS", "WFC", "C"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "OXY"],
    }


def render_quick_add_popular():
    """Render quick add buttons for popular tickers"""
    
    st.markdown("### ⚡ Quick Add Popular Tickers")
    
    popular = get_popular_tickers()
    manager = WatchlistManager()
    
    for category, tickers in popular.items():
        with st.expander(f"📁 {category}"):
            cols = st.columns(4)
            for idx, ticker in enumerate(tickers):
                col = cols[idx % 4]
                with col:
                    is_in = manager.is_in_watchlist(ticker)
                    button_text = "⭐" if is_in else "☆"
                    
                    if st.button(f"{button_text} {ticker}", key=f"quick_add_{ticker}"):
                        if is_in:
                            manager.remove_ticker(ticker)
                            st.success(f"Removed {ticker}")
                        else:
                            manager.add_ticker(ticker)
                            st.success(f"Added {ticker}")
                        st.rerun()


# Example usage in main dashboards:
def integrate_watchlist_in_dashboard():
    """
    Example integration in main dashboard
    Add this to dashboard_stocks.py, dashboard_options.py, etc.
    """
    
    # In the ticker input section:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Stock Ticker",
            value=st.session_state.get('ticker', ''),
            placeholder="e.g., AAPL, TSLA, GME",
            key="ticker_input"
        )
    
    with col2:
        if ticker:
            render_add_to_watchlist_button(ticker)
    
    # In the sidebar:
    render_watchlist_sidebar()


if __name__ == "__main__":
    # Test/Demo mode
    st.set_page_config(page_title="Watchlist Manager Demo", layout="wide")
    
    st.title("⭐ Watchlist Manager Demo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Main Content")
        
        # Ticker input with watchlist button
        ticker_col1, ticker_col2 = st.columns([4, 1])
        
        with ticker_col1:
            ticker = st.text_input(
                "Enter Ticker",
                value="AAPL",
                key="demo_ticker"
            )
        
        with ticker_col2:
            if ticker:
                render_add_to_watchlist_button(ticker, "Apple Inc.")
        
        st.markdown("---")
        
        # Quick add popular tickers
        render_quick_add_popular()
        
        st.markdown("---")
        
        # Import watchlist
        render_watchlist_import()
    
    with col2:
        # Watchlist sidebar (rendered in actual sidebar)
        render_watchlist_sidebar()
