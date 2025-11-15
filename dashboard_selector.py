"""
Dashboard Selector - Professional Analysis Modules
Clean, efficient interface for institutional-grade tools
(With just enough humor to keep you from crying when your calls expire worthless)
"""
import streamlit as st
import time
from wsb_quotes import get_dashboard_tagline, get_loading_message

def show_selector():
    """Display the professional dashboard selector"""
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            margin-bottom: 10px;
        }
        
        .main-title {
            font-size: 2.8em;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            font-size: 1.1em;
            color: #9CA3AF;
            margin-bottom: 15px;
        }
        
        .disclaimer {
            font-size: 0.85em;
            color: #6B7280;
            font-style: italic;
        }
        
        .dashboard-card {
            background: linear-gradient(135deg, #2D2D2D 0%, #1F1F1F 100%);
            border-left: 4px solid;
            border-radius: 8px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .dashboard-card:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }
        
        .stocks-card {
            border-left-color: #22C55E;
        }
        
        .stocks-card:hover {
            background: linear-gradient(135deg, #2D2D2D 0%, #1F2F1F 100%);
        }
        
        .options-card {
            border-left-color: #F59E0B;
        }
        
        .options-card:hover {
            background: linear-gradient(135deg, #2D2D2D 0%, #2F271F 100%);
        }
        
        .crypto-card {
            border-left-color: #3B82F6;
        }
        
        .crypto-card:hover {
            background: linear-gradient(135deg, #2D2D2D 0%, #1F252F 100%);
        }
        
        .advanced-card {
            border-left-color: #8B5CF6;
        }
        
        .advanced-card:hover {
            background: linear-gradient(135deg, #2D2D2D 0%, #252030 100%);
        }
        
        .portfolio-card {
            border-left-color: #EC4899;
        }
        
        .portfolio-card:hover {
            background: linear-gradient(135deg, #2D2D2D 0%, #2F1F28 100%);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .card-icon {
            font-size: 2em;
            margin-right: 16px;
            opacity: 0.9;
        }
        
        .card-title {
            font-size: 1.5em;
            font-weight: 600;
            color: #FFFFFF;
        }
        
        .card-description {
            font-size: 0.95em;
            color: #9CA3AF;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        .card-features {
            font-size: 0.85em;
            color: #6B7280;
            line-height: 1.6;
        }
        
        .feature-item {
            padding: 4px 0;
        }
        
        .feature-bullet {
            color: #22C55E;
            margin-right: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Professional header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">Market Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Select Analysis Module</p>', unsafe_allow_html=True)
    st.markdown('<p class="disclaimer">Professional tools with personality. Because stonks are serious business (but we\'re not).</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dashboard selection cards - Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card stocks-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <span class="card-title">Equity Analysis</span>
            </div>
            <div class="card-description">
                Comprehensive stock analysis with DCF, technical indicators, and sentiment tracking. Perfect for when you need to justify your terrible decisions with math.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>Valuation models (DCF, DDM, NAV)</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Technical indicators & signals</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Real-time sentiment analysis</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Risk-adjusted returns (Sharpe, Sortino)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Equity Dashboard", key="stocks", use_container_width=True, type="primary"):
            st.session_state.selected_dashboard = "stocks"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="dashboard-card options-card">
            <div class="card-header">
                <span class="card-icon">⚡</span>
                <span class="card-title">Options Trading</span>
            </div>
            <div class="card-description">
                Advanced options analytics with Greeks, volatility analysis, and unusual activity tracking. For theta gang and FD enthusiasts alike.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>Black-Scholes pricing & Greeks</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Implied volatility analysis</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Congressional trading alerts</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Unusual options flow scanner</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Options Dashboard", key="options", use_container_width=True, type="primary"):
            st.session_state.selected_dashboard = "options"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    # Row 2
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card crypto-card">
            <div class="card-header">
                <span class="card-icon">₿</span>
                <span class="card-title">Crypto Markets</span>
            </div>
            <div class="card-description">
                Digital asset analysis with on-chain metrics, Fear & Greed Index, and market sentiment. Because sometimes losing money in dollars isn't enough.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>Multi-exchange price tracking</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Fear & Greed Index monitoring</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Social sentiment analysis</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Volatility & correlation metrics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Crypto Dashboard", key="crypto", use_container_width=True, type="primary"):
            st.session_state.selected_dashboard = "crypto"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="dashboard-card advanced-card">
            <div class="card-header">
                <span class="card-icon">🔬</span>
                <span class="card-title">Quantitative Analysis</span>
            </div>
            <div class="card-description">
                AI-powered predictions, arbitrage detection, and advanced statistical modeling. Where machine learning meets your money losing strategies.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>Claude AI market predictions</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Crypto arbitrage scanner</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Statistical pairs trading</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Prophet time series forecasting</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Quantitative Dashboard", key="advanced", use_container_width=True, type="primary"):
            st.session_state.selected_dashboard = "advanced"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    # Row 3
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card portfolio-card">
            <div class="card-header">
                <span class="card-icon">💼</span>
                <span class="card-title">Portfolio Management</span>
            </div>
            <div class="card-description">
                Modern portfolio theory, risk optimization, and efficient frontier analysis. Because putting all eggs in one basket worked out great for Enron shareholders.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>Efficient frontier optimization</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Sharpe ratio maximization</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Risk-return analysis</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Auto-rebalancing suggestions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Portfolio Dashboard", key="portfolio", use_container_width=True, type="primary"):
            st.session_state.selected_dashboard = "portfolio"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="dashboard-card" style="border-color: #ef4444;">
            <div class="card-header">
                <span class="card-icon">🔧</span>
                <span class="card-title">Debugging Tools</span>
            </div>
            <div class="card-description">
                API health monitoring, data validation, and system diagnostics. For when you need to figure out why your carefully researched trade is down 80%.
            </div>
            <div class="card-features">
                <div class="feature-item"><span class="feature-bullet">▸</span>API health monitor & logs</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Data validation checks</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Cache management tools</div>
                <div class="feature-item"><span class="feature-bullet">▸</span>Session state inspector</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Launch Debug Dashboard", key="debug", use_container_width=True, type="secondary"):
            st.session_state.selected_dashboard = "debug"
            st.session_state.dashboard_selected = True
            show_rocket_animation()
            st.rerun()
    
    # Fun footer
    st.markdown("""
    <div class="ape-mode">
        <p>⚠️ Not financial advice. We're all regarded here. ⚠️</p>
        <p>💎🙌 Diamond hands only. Paper hands exit left. 🧻👎</p>
        <p>🦍 Ape together strong. Ape alone... also strong? (probably not)</p>
        <p>📉 Your losses = Our gain porn 📈</p>
    </div>
    """, unsafe_allow_html=True)


def show_rocket_animation():
    """Show a fun loading animation when dashboard is selected"""
    loading_msg = get_loading_message()
    
    st.markdown("""
    <style>
        @keyframes launch {
            0% { transform: translateY(0) rotate(45deg); opacity: 1; }
            100% { transform: translateY(-500px) rotate(45deg); opacity: 0; }
        }
        
        .rocket-launch {
            font-size: 5em;
            text-align: center;
            animation: launch 1s ease-out;
        }
        
        .loading-text {
            text-align: center;
            font-size: 1.5em;
            color: #00FF88;
            margin-top: 20px;
            font-style: italic;
        }
    </style>
    <div style="height: 300px;">
        <div class="rocket-launch">🚀</div>
        <div class="loading-text">""" + loading_msg + """</div>
    </div>
    """, unsafe_allow_html=True)
    # Removed artificial delay for better UX
    # time.sleep(0.8)


def show_dashboard_switcher():
    """Show dashboard switcher in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Switch Dashboard")
    
    current = st.session_state.get("selected_dashboard", "stocks")
    
    # Display current dashboard
    dashboard_emojis = {
        "stocks": "📈 STONKS",
        "options": "⚡ OPTIONS",
        "crypto": "🚀 CRYPTO",
        "advanced": "🔬 ADVANCED",
        "portfolio": "💼 PORTFOLIO"
    }
    
    st.sidebar.info(f"**Current:** {dashboard_emojis.get(current, 'Unknown')}")
    
    # Switch buttons - Row 1
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        if st.button("📈", key="switch_stocks", help="Stocks Dashboard", use_container_width=True):
            if current != "stocks":
                st.session_state.selected_dashboard = "stocks"
                st.rerun()
    
    with col2:
        if st.button("⚡", key="switch_options", help="Options Dashboard", use_container_width=True):
            if current != "options":
                st.session_state.selected_dashboard = "options"
                st.rerun()
    
    with col3:
        if st.button("🚀", key="switch_crypto", help="Crypto Dashboard", use_container_width=True):
            if current != "crypto":
                st.session_state.selected_dashboard = "crypto"
                st.rerun()
    
    # Switch buttons - Row 2
    col1, col2, col3 = st.sidebar.columns([1, 1, 1])
    
    with col1:
        if st.button("🔬", key="switch_advanced", help="Advanced Analytics", use_container_width=True):
            if current != "advanced":
                st.session_state.selected_dashboard = "advanced"
                st.rerun()
    
    with col2:
        if st.button("💼", key="switch_portfolio", help="Portfolio Manager", use_container_width=True):
            if current != "portfolio":
                st.session_state.selected_dashboard = "portfolio"
                st.rerun()
    
    # Reset button
    if st.sidebar.button("🏠 Back to Menu", use_container_width=True):
        st.session_state.dashboard_selected = False
        st.session_state.selected_dashboard = None
        st.rerun()
