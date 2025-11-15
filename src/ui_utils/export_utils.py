"""
Export Utilities - CSV and Chart Export
Allows users to download analysis results and charts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO, StringIO
from typing import Dict, List, Any
import json


class ExportManager:
    """Handles data and chart exports"""
    
    @staticmethod
    def export_dataframe_csv(df: pd.DataFrame, filename: str = None) -> str:
        """
        Export DataFrame to CSV string
        
        Args:
            df: Pandas DataFrame
            filename: Optional filename suggestion
            
        Returns:
            CSV string
        """
        if filename is None:
            filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return df.to_csv(index=True)
    
    @staticmethod
    def export_analysis_report(
        ticker: str,
        price_data: Dict,
        technical_data: Dict,
        valuation_data: Dict = None
    ) -> str:
        """
        Export comprehensive analysis report as CSV
        
        Args:
            ticker: Stock ticker
            price_data: Price information
            technical_data: Technical analysis results
            valuation_data: Optional DCF valuation data
            
        Returns:
            CSV string with full report
        """
        report_data = []
        
        # Header
        report_data.append(["Stock Analysis Report", ""])
        report_data.append(["Ticker", ticker])
        report_data.append(["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        report_data.append(["", ""])
        
        # Price Data
        report_data.append(["PRICE INFORMATION", ""])
        report_data.append(["Current Price", price_data.get('current_price', 'N/A')])
        report_data.append(["Day Change", price_data.get('change', 'N/A')])
        report_data.append(["Day Change %", price_data.get('change_pct', 'N/A')])
        report_data.append(["Volume", price_data.get('volume', 'N/A')])
        report_data.append(["Market Cap", price_data.get('market_cap', 'N/A')])
        report_data.append(["", ""])
        
        # Technical Indicators
        report_data.append(["TECHNICAL INDICATORS", ""])
        
        # RSI
        rsi_data = technical_data.get('rsi', {})
        report_data.append(["RSI Value", rsi_data.get('value', 'N/A')])
        report_data.append(["RSI Signal", rsi_data.get('signal', 'N/A')])
        
        # MACD
        macd_data = technical_data.get('macd', {})
        report_data.append(["MACD", macd_data.get('macd', 'N/A')])
        report_data.append(["MACD Signal", macd_data.get('signal', 'N/A')])
        report_data.append(["MACD Bullish", macd_data.get('bullish', 'N/A')])
        
        # Bollinger Bands
        bb_data = technical_data.get('bollinger', {})
        report_data.append(["BB Upper", bb_data.get('upper', 'N/A')])
        report_data.append(["BB Middle", bb_data.get('middle', 'N/A')])
        report_data.append(["BB Lower", bb_data.get('lower', 'N/A')])
        report_data.append(["BB Signal", bb_data.get('signal', 'N/A')])
        
        # Moving Averages
        pa_data = technical_data.get('price_action', {})
        report_data.append(["SMA 20", pa_data.get('sma_20', 'N/A')])
        report_data.append(["SMA 50", pa_data.get('sma_50', 'N/A')])
        report_data.append(["SMA 200", pa_data.get('sma_200', 'N/A')])
        report_data.append(["Above SMA 50", pa_data.get('above_sma_50', 'N/A')])
        report_data.append(["Above SMA 200", pa_data.get('above_sma_200', 'N/A')])
        
        # Support/Resistance
        sr_data = technical_data.get('support_resistance', {})
        report_data.append(["Support Level", sr_data.get('support', 'N/A')])
        report_data.append(["Resistance Level", sr_data.get('resistance', 'N/A')])
        report_data.append(["", ""])
        
        # Valuation (if available)
        if valuation_data:
            report_data.append(["VALUATION ANALYSIS", ""])
            report_data.append(["Fair Value (DCF)", valuation_data.get('fair_value', 'N/A')])
            report_data.append(["Upside/Downside", valuation_data.get('upside', 'N/A')])
            report_data.append(["Recommendation", valuation_data.get('recommendation', 'N/A')])
        
        # Convert to CSV
        df = pd.DataFrame(report_data, columns=['Metric', 'Value'])
        return df.to_csv(index=False)
    
    @staticmethod
    def export_chart_png(fig: go.Figure, filename: str = None) -> bytes:
        """
        Export Plotly chart as PNG
        
        Args:
            fig: Plotly Figure object
            filename: Optional filename suggestion
            
        Returns:
            PNG bytes
        """
        if filename is None:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Export as PNG bytes
        img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
        return img_bytes
    
    @staticmethod
    def export_chart_html(fig: go.Figure, filename: str = None) -> str:
        """
        Export Plotly chart as interactive HTML
        
        Args:
            fig: Plotly Figure object
            filename: Optional filename suggestion
            
        Returns:
            HTML string
        """
        if filename is None:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        return fig.to_html(include_plotlyjs='cdn')
    
    @staticmethod
    def export_watchlist_json(watchlist: List[str], metadata: Dict = None) -> str:
        """
        Export watchlist as JSON
        
        Args:
            watchlist: List of tickers
            metadata: Optional metadata dict
            
        Returns:
            JSON string
        """
        data = {
            'watchlist': watchlist,
            'metadata': metadata or {},
            'exported_date': datetime.now().isoformat(),
            'version': '1.0'
        }
        return json.dumps(data, indent=2)


def render_export_buttons(
    ticker: str,
    data: Dict,
    show_csv: bool = True,
    show_chart: bool = False,
    chart_fig: go.Figure = None
):
    """
    Render export buttons in Streamlit
    
    Args:
        ticker: Stock ticker
        data: Complete analysis data
        show_csv: Show CSV export button
        show_chart: Show chart export button
        chart_fig: Plotly figure for chart export
    """
    st.markdown("### 📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    # CSV Export
    if show_csv:
        with col1:
            try:
                # Extract data
                price_data = {
                    'current_price': data.get('current_price', 'N/A'),
                    'change': data.get('change', 'N/A'),
                    'change_pct': data.get('change_pct', 'N/A'),
                    'volume': data.get('volume', 'N/A'),
                    'market_cap': data.get('market_cap', 'N/A')
                }
                
                technical_data = data.get('technical', {})
                valuation_data = data.get('valuation', None)
                
                csv_data = ExportManager.export_analysis_report(
                    ticker=ticker,
                    price_data=price_data,
                    technical_data=technical_data,
                    valuation_data=valuation_data
                )
                
                filename = f"{ticker}_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
                
                st.download_button(
                    label="📊 Export Analysis (CSV)",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"export_csv_{ticker}"
                )
            except Exception as e:
                st.error(f"CSV export error: {str(e)}")
    
    # Chart Export (PNG)
    if show_chart and chart_fig:
        with col2:
            try:
                img_bytes = ExportManager.export_chart_png(
                    chart_fig,
                    f"{ticker}_chart_{datetime.now().strftime('%Y%m%d')}.png"
                )
                
                filename = f"{ticker}_chart_{datetime.now().strftime('%Y%m%d')}.png"
                
                st.download_button(
                    label="📈 Export Chart (PNG)",
                    data=img_bytes,
                    file_name=filename,
                    mime="image/png",
                    use_container_width=True,
                    key=f"export_png_{ticker}"
                )
            except Exception as e:
                st.error(f"PNG export error: {str(e)}")
    
    # Historical Data Export
    if 'df' in data and not data['df'].empty:
        with col3:
            try:
                df = data['df']
                csv_data = ExportManager.export_dataframe_csv(df)
                filename = f"{ticker}_historical_{datetime.now().strftime('%Y%m%d')}.csv"
                
                st.download_button(
                    label="📅 Export Historical (CSV)",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"export_historical_{ticker}"
                )
            except Exception as e:
                st.error(f"Historical export error: {str(e)}")


def render_bulk_export_button(tickers: List[str], data_dict: Dict[str, pd.DataFrame]):
    """
    Render bulk export for multiple tickers
    
    Args:
        tickers: List of ticker symbols
        data_dict: Dictionary mapping tickers to DataFrames
    """
    st.markdown("### 📦 Bulk Export")
    
    if st.button("📥 Export All Tickers", use_container_width=True):
        # Combine all data
        combined_df = pd.DataFrame()
        
        for ticker in tickers:
            if ticker in data_dict:
                df = data_dict[ticker].copy()
                df['Ticker'] = ticker
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        if not combined_df.empty:
            csv_data = ExportManager.export_dataframe_csv(combined_df)
            filename = f"bulk_export_{datetime.now().strftime('%Y%m%d')}.csv"
            
            st.download_button(
                label="📥 Download Bulk Export",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No data available for export")


# Example usage in dashboard
def integrate_export_in_dashboard():
    """
    Example integration in stock dashboard
    Add this to the end of each analysis tab
    """
    
    # After showing analysis
    st.markdown("---")
    
    # Export section
    render_export_buttons(
        ticker="AAPL",
        data={
            'current_price': 150.00,
            'change': 2.50,
            'change_pct': '+1.69%',
            'volume': 50000000,
            'market_cap': 2500000000000,
            'technical': {},
            'df': pd.DataFrame()  # Historical data
        },
        show_csv=True,
        show_chart=False
    )


if __name__ == "__main__":
    # Demo
    st.set_page_config(page_title="Export Demo", layout="wide")
    
    st.title("📥 Export Functionality Demo")
    
    # Create sample data
    sample_data = {
        'current_price': 150.00,
        'change': 2.50,
        'change_pct': '+1.69%',
        'volume': 50000000,
        'market_cap': 2500000000000,
        'technical': {
            'rsi': {'value': 65, 'signal': 'neutral'},
            'macd': {'macd': 1.5, 'signal': 1.2, 'bullish': True},
            'bollinger': {'upper': 155, 'middle': 150, 'lower': 145, 'signal': 'neutral'},
            'price_action': {'sma_50': 148, 'sma_200': 140, 'above_sma_50': True, 'above_sma_200': True},
            'support_resistance': {'support': 145, 'resistance': 155}
        },
        'df': pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=100),
            'Open': [150 + i for i in range(100)],
            'Close': [150 + i for i in range(100)]
        })
    }
    
    render_export_buttons(
        ticker="AAPL",
        data=sample_data,
        show_csv=True,
        show_chart=False
    )
