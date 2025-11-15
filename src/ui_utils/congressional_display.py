"""
Congressional Trading Display Component
Shows Congressional trades for a specific stock in the dashboard.

Usage:
    from src.ui_utils.congressional_display import show_congressional_trades
    show_congressional_trades('AAPL')
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def show_congressional_trades(ticker: str, days: int = 90):
    """
    Display Congressional trading activity for a specific stock.
    
    Shows:
    - Summary metrics (buy/sell counts, sentiment)
    - Alert for unusual activity
    - Table of recent trades
    - Sentiment gauge visualization
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        days: Number of days of history to show (default 90)
    """
    try:
        from src.pipelines.get_political_data import get_political_data_pipeline
        
        # Initialize pipeline
        pipeline = get_political_data_pipeline()
        
        # Section header
        st.markdown("---")
        st.subheader(f"🏛️ Congressional Trading Activity: {ticker}")
        st.caption(f"Last {days} days • Data from House Stock Watcher & Capitol Trades")
        
        # Fetch sentiment analysis
        with st.spinner("Fetching Congressional trades..."):
            sentiment = pipeline.analyze_congressional_sentiment(ticker, days=days)
        
        # Check for errors
        if 'error' in sentiment:
            st.info(f"ℹ️ {sentiment['error']}")
            return
        
        # Summary metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Trades",
                value=sentiment['total_trades'],
                help="Number of Congressional trades in the selected period"
            )
        
        with col2:
            st.metric(
                label="Purchases",
                value=sentiment['buy_count'],
                delta=f"{sentiment['buy_count'] - sentiment['sell_count']:+d}",
                delta_color="normal",
                help="Number of buy transactions by Congress members"
            )
        
        with col3:
            st.metric(
                label="Sales",
                value=sentiment['sell_count'],
                help="Number of sell transactions by Congress members"
            )
        
        with col4:
            # Sentiment score as percentage
            sentiment_pct = int(sentiment['net_sentiment'] * 100)
            st.metric(
                label="Net Sentiment",
                value=f"{sentiment_pct:+d}%",
                delta=sentiment['signal'],
                delta_color="normal" if abs(sentiment_pct) < 30 else ("normal" if sentiment_pct > 0 else "inverse"),
                help="Positive = more buying, Negative = more selling"
            )
        
        # Alert for unusual activity
        if sentiment.get('recent_activity_flag'):
            st.warning("⚠️ **UNUSUAL ACTIVITY DETECTED:** Significant spike in Congressional trades in the last 30 days!")
        
        # Sentiment interpretation
        if sentiment['bullish']:
            st.success("📈 **Bullish Signal:** Congress is accumulating this stock (65%+ buys)")
        elif sentiment['bearish']:
            st.error("📉 **Bearish Signal:** Congress is distributing this stock (65%+ sells)")
        else:
            st.info("➡️ **Neutral Signal:** Mixed Congressional activity, no clear trend")
        
        # Show latest trades table
        if sentiment.get('latest_trades') and len(sentiment['latest_trades']) > 0:
            st.markdown("#### Recent Transactions")
            
            # Convert to DataFrame for better display
            trades_df = pd.DataFrame(sentiment['latest_trades'])
            
            # Format dates
            if 'date' in trades_df.columns:
                trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
            
            # Add emoji indicators
            if 'transaction_type' in trades_df.columns:
                trades_df['Type'] = trades_df['transaction_type'].apply(
                    lambda x: f"{'🟢 ' if x == 'Buy' else '🔴 '}{x}"
                )
                trades_df = trades_df.drop('transaction_type', axis=1)
            
            # Rename columns for display
            display_columns = {
                'date': 'Date',
                'member': 'Congress Member',
                'chamber': 'Chamber',
                'party': 'Party',
                'amount_range': 'Amount',
                'disclosure_date': 'Disclosed'
            }
            
            # Only rename columns that exist
            rename_dict = {k: v for k, v in display_columns.items() if k in trades_df.columns}
            trades_df = trades_df.rename(columns=rename_dict)
            
            # Display table
            st.dataframe(
                trades_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download button for full data
            if st.button("📥 Download Full Trade History (CSV)", key=f"download_congress_{ticker}"):
                # Fetch all trades
                all_trades = pipeline.get_congressional_trades(ticker=ticker, days=days)
                if all_trades is not None and len(all_trades) > 0:
                    csv = all_trades.to_csv(index=False)
                    st.download_button(
                        label="💾 Save CSV",
                        data=csv,
                        file_name=f"congressional_trades_{ticker}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key=f"download_congress_csv_{ticker}"
                    )
        else:
            st.info("No recent Congressional trades found for this ticker.")
        
        # Volume estimate (if available)
        if sentiment.get('total_volume_estimate') and sentiment['total_volume_estimate'] > 0:
            st.caption(f"💰 Estimated Total Volume: ${sentiment['total_volume_estimate']:,.0f}")
        
        # Data source disclaimer
        with st.expander("ℹ️ Data Source & Limitations"):
            st.markdown("""
            **Data Sources:**
            - Primary: [House Stock Watcher](https://housestockwatcher.com/) (Free API)
            - Fallback: [Capitol Trades](https://www.capitoltrades.com/) (Web scraping)
            
            **Important Notes:**
            - Congressional trades are disclosed 30-45 days after execution
            - Amount ranges are estimates (exact values not disclosed)
            - Data may not include all transactions (some are exempt)
            - This is NOT investment advice - trades may be made for personal reasons
            
            **Interpretation:**
            - High buying activity = Potential bullish signal (but not guaranteed)
            - High selling activity = Could be portfolio rebalancing (not always bearish)
            - Look for clusters of activity from multiple members
            - Cross-reference with news and fundamental analysis
            """)
    
    except ImportError:
        st.error("❌ Political data pipeline not available. Please check installation.")
        logger.error("Failed to import get_political_data_pipeline")
    except Exception as e:
        st.error(f"❌ Error loading Congressional trades: {str(e)}")
        logger.error(f"Error in show_congressional_trades: {e}", exc_info=True)


def show_congressional_watchlist(days: int = 30):
    """
    Display the most actively traded stocks by Congress in the last N days.
    
    This can be shown as a standalone dashboard section or sidebar widget.
    
    Args:
        days: Number of days to analyze (default 30)
    """
    try:
        from src.pipelines.get_political_data import get_political_data_pipeline
        
        st.subheader("🔥 Congress's Hottest Trades")
        st.caption(f"Most actively traded stocks in the last {days} days")
        
        pipeline = get_political_data_pipeline()
        
        with st.spinner("Analyzing Congressional portfolio..."):
            # Get all trades (no ticker filter)
            all_trades = pipeline.get_congressional_trades(ticker=None, days=days)
            
            if all_trades is None or len(all_trades) == 0:
                st.info("No Congressional trades found in this period.")
                return
            
            # Group by ticker and count trades
            if 'ticker' in all_trades.columns:
                ticker_counts = all_trades['ticker'].value_counts().head(10)
                
                # Calculate buy/sell ratio for each
                top_tickers = []
                for ticker in ticker_counts.index:
                    ticker_trades = all_trades[all_trades['ticker'] == ticker]
                    buys = len(ticker_trades[ticker_trades['transaction_type'] == 'Buy'])
                    sells = len(ticker_trades[ticker_trades['transaction_type'] == 'Sell'])
                    total = buys + sells
                    
                    sentiment = "🟢 Bullish" if buys > sells * 1.5 else ("🔴 Bearish" if sells > buys * 1.5 else "⚪ Mixed")
                    
                    top_tickers.append({
                        'Ticker': ticker,
                        'Total Trades': total,
                        'Buys': buys,
                        'Sells': sells,
                        'Sentiment': sentiment
                    })
                
                df = pd.DataFrame(top_tickers)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("Unable to group trades by ticker.")
    
    except Exception as e:
        st.error(f"Error loading Congressional watchlist: {e}")
        logger.error(f"Error in show_congressional_watchlist: {e}", exc_info=True)


# Singleton instance
_pipeline = None

def get_political_data_pipeline():
    """Get or create political data pipeline singleton."""
    global _pipeline
    if _pipeline is None:
        from src.pipelines.get_political_data import PoliticalDataPipeline
        _pipeline = PoliticalDataPipeline()
    return _pipeline
