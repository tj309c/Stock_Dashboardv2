"""
Simplified Debug Panel for Sidebar
Quick health check widget - full diagnostics available in Debug Dashboard
"""
import streamlit as st
from pathlib import Path


def quick_health_check():
    """Quick health check for sidebar"""
    issues = []
    
    # Check critical dependencies
    try:
        import yfinance
        import pandas
        import streamlit
        import plotly
    except ImportError as e:
        issues.append(f"Missing dependency: {str(e).split('No module named ')[-1]}")
    
    # Check data directory
    if not Path('data').exists():
        issues.append("Data directory missing")
    
    # Check critical files
    critical_files = ['main.py', 'data_fetcher.py', 'analysis_engine.py']
    missing_files = [f for f in critical_files if not Path(f).exists()]
    if missing_files:
        issues.append(f"Missing files: {', '.join(missing_files)}")
    
    return len(issues) == 0, issues


def show_debug_panel():
    """Show simplified debug panel in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 System Status")
    
    healthy, issues = quick_health_check()
    
    if healthy:
        st.sidebar.success("✅ All systems operational")
    else:
        st.sidebar.error(f"⚠️ {len(issues)} issue(s) detected")
        for issue in issues:
            st.sidebar.caption(f"• {issue}")
    
    # Link to full debug dashboard
    if st.sidebar.button("🔍 Full Diagnostics", use_container_width=True):
        st.session_state.selected_dashboard = "debug"
        st.session_state.dashboard_selected = True
        st.rerun()
