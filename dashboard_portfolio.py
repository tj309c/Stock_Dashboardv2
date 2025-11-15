"""
Portfolio Manager Dashboard 💼
Portfolio Optimization and Efficient Frontier Analysis
Modern Portfolio Theory implementation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import minimize
# Migrated to new formatters module
from src.ui_utils.formatters import (format_currency, format_percentage, format_large_number)
from utils import safe_divide


def show_portfolio_dashboard(components):
    """Display the portfolio optimization dashboard"""
    
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="margin: 0; font-size: 3em;">📊 PORTFOLIO OPTIMIZER</h1>
        <p style="color: #FFFFFF; font-size: 1.2em; margin: 10px 0;"><i>Optimize your portfolio like a pro</i> 📈</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Portfolio input
    st.markdown("### 🎯 Build Your Portfolio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Ticker input (comma-separated)
        tickers_input = st.text_input(
            "Enter Tickers (comma-separated)",
            value="AAPL,MSFT,GOOGL,TSLA,SPY",
            help="Enter 3-10 stock tickers separated by commas"
        ).upper()
        
        tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📊 Optimize Portfolio", type="primary", key="optimize_portfolio"):
            st.session_state.portfolio_tickers = tickers
    
    # Investment amount
    col1, col2, col3 = st.columns(3)
    
    with col1:
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000
        )
    
    with col2:
        risk_tolerance = st.select_slider(
            "Risk Tolerance",
            options=["Very Low", "Low", "Moderate", "High", "Very High"],
            value="Moderate"
        )
    
    with col3:
        time_horizon = st.selectbox(
            "Time Horizon",
            ["1 Year", "3 Years", "5 Years", "10 Years"],
            index=2
        )
    
    tickers = st.session_state.get("portfolio_tickers", tickers)
    
    if len(tickers) < 2:
        st.warning("Please enter at least 2 tickers for portfolio optimization")
        return
    
    # Fetch portfolio data
    with st.spinner(f"Optimizing portfolio with {len(tickers)} assets... 💼"):
        portfolio_data = fetch_portfolio_data(components, tickers)
    
    if not portfolio_data or "error" in portfolio_data:
        st.error("❌ Unable to fetch portfolio data. Check your tickers.")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Optimal Allocation",
        "📊 Efficient Frontier",
        "📈 Risk/Return Analysis",
        "💰 Rebalancing"
    ])
    
    with tab1:
        show_optimal_allocation_tab(portfolio_data, investment_amount, risk_tolerance)
    
    with tab2:
        show_efficient_frontier_tab(portfolio_data)
    
    with tab3:
        show_risk_return_tab(portfolio_data)
    
    with tab4:
        show_rebalancing_tab(portfolio_data, investment_amount)


@st.cache_data(ttl=600)
def fetch_portfolio_data(_components, tickers):
    """Fetch data for multiple tickers"""
    components = _components
    try:
        portfolio = {}
        
        for ticker in tickers:
            stock_data = components["fetcher"].get_stock_data(ticker, period="2y")
            
            if stock_data and "history" in stock_data:
                portfolio[ticker] = {
                    "history": stock_data["history"],
                    "info": stock_data.get("info", {})
                }
        
        if len(portfolio) < 2:
            return {"error": "Insufficient data"}
        
        # Calculate returns matrix
        returns_data = {}
        min_length = min([len(data["history"]) for data in portfolio.values()])
        
        for ticker, data in portfolio.items():
            # Convert dict back to DataFrame if needed (from caching)
            history = data["history"]
            if isinstance(history, dict):
                history = pd.DataFrame(history)
            
            # Align data length
            history = history.iloc[-min_length:]
            
            # Calculate returns
            if 'Close' in history.columns:
                returns = history['Close'].pct_change().dropna()
                returns_data[ticker] = returns.values
            else:
                # Handle case where Close might be index
                returns = pd.Series(history.get('Close', {})).pct_change().dropna()
                returns_data[ticker] = returns.values
        
        returns_df = pd.DataFrame(returns_data)
        
        # Sanitize for caching
        from utils import sanitize_dict_for_cache
        
        result = {
            "tickers": tickers,
            "portfolio": portfolio,
            "returns": returns_df,
            "mean_returns": returns_df.mean().to_dict(),
            "cov_matrix": returns_df.cov().to_dict(),
        }
        
        return sanitize_dict_for_cache(result)
        
    except Exception as e:
        return {"error": str(e)}


def show_optimal_allocation_tab(portfolio_data, investment, risk_tolerance):
    """Show optimal portfolio allocation"""
    st.subheader("🎯 Optimal Portfolio Allocation")
    st.markdown("*Based on Modern Portfolio Theory*")
    
    tickers = portfolio_data.get("tickers", [])
    returns_df = portfolio_data.get("returns")
    
    if returns_df is None:
        st.warning("Unable to calculate optimal allocation")
        return
    
    # Convert returns to DataFrame if needed
    if isinstance(returns_df, dict):
        returns_df = pd.DataFrame(returns_df)
    
    # Calculate optimal weights
    optimal_weights = calculate_optimal_portfolio(
        returns_df,
        risk_tolerance
    )
    
    if optimal_weights and "error" not in optimal_weights:
        # Display allocation
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Recommended Allocation")
            
            weights = optimal_weights["weights"]
            
            # Create allocation table
            allocation_data = []
            for ticker, weight in zip(tickers, weights):
                # Get latest price safely
                history = portfolio_data["portfolio"][ticker]["history"]
                if isinstance(history, dict):
                    # Handle dict from caching
                    close_prices = history.get('Close', {})
                    if isinstance(close_prices, dict):
                        latest_price = list(close_prices.values())[-1] if close_prices else 100
                    else:
                        latest_price = close_prices
                else:
                    # Handle DataFrame
                    latest_price = history['Close'].iloc[-1]
                
                allocation_data.append({
                    "Ticker": ticker,
                    "Weight": f"{weight*100:.1f}%",
                    "Amount": format_currency(investment * weight),
                    "Shares": int(investment * weight / latest_price) if latest_price > 0 else 0
                })
            
            st.dataframe(allocation_data, use_container_width=True)
        
        with col2:
            # Pie chart
            fig = go.Figure(data=[go.Pie(
                labels=tickers,
                values=weights,
                hole=0.4,
                marker=dict(colors=['#3B82F6', '#EF4444', '#22C55E', '#F59E0B', '#8B5CF6', '#EC4899'])
            )])
            
            fig.update_layout(
                title="Portfolio Allocation",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Portfolio metrics
        st.markdown("### Portfolio Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Expected Return",
                f"{optimal_weights['expected_return']*100:.2f}%",
                help="Annualized expected return"
            )
        
        with col2:
            st.metric(
                "Volatility",
                f"{optimal_weights['volatility']*100:.2f}%",
                help="Annualized standard deviation"
            )
        
        with col3:
            st.metric(
                "Sharpe Ratio",
                f"{optimal_weights['sharpe_ratio']:.2f}",
                help="Risk-adjusted return metric"
            )
        
        with col4:
            st.metric(
                "Max Drawdown",
                f"{optimal_weights.get('max_drawdown', 0)*100:.1f}%",
                help="Largest peak-to-trough decline"
            )


def calculate_optimal_portfolio(returns_df, risk_tolerance):
    """Calculate optimal portfolio weights using mean-variance optimization"""
    try:
        # Annualize returns and covariance
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(returns_df.columns)
        
        # Risk tolerance mapping
        risk_map = {
            "Very Low": 0.5,
            "Low": 1.0,
            "Moderate": 2.0,
            "High": 3.0,
            "Very High": 4.0
        }
        
        risk_aversion = risk_map.get(risk_tolerance, 2.0)
        
        # Objective function: maximize Sharpe ratio or minimize volatility
        def objective(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # Risk-adjusted return
            risk_free_rate = 0.045
            sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
            
            # Maximize Sharpe ratio (minimize negative Sharpe)
            return -sharpe / risk_aversion
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        bounds = tuple((0, 0.4) for _ in range(num_assets))  # Max 40% in any asset
        
        # Initial guess (equal weights)
        initial_weights = np.array([1/num_assets] * num_assets)
        
        # Optimize
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            weights = result.x
            
            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - 0.045) / portfolio_vol
            
            # Estimate max drawdown (simplified)
            portfolio_returns = returns_df.dot(weights)
            cumulative = (1 + portfolio_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                "weights": weights,
                "expected_return": portfolio_return,
                "volatility": portfolio_vol,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown
            }
        else:
            return {"error": "Optimization failed"}
        
    except Exception as e:
        return {"error": str(e)}


def show_efficient_frontier_tab(portfolio_data):
    """Show efficient frontier"""
    st.subheader("📊 Efficient Frontier")
    st.markdown("*Risk-Return tradeoff for different portfolio allocations*")
    
    returns_df = portfolio_data.get("returns")
    
    if returns_df is None:
        st.warning("Unable to generate efficient frontier")
        return
    
    # Convert to DataFrame if needed
    if isinstance(returns_df, dict):
        returns_df = pd.DataFrame(returns_df)
    
    # Generate efficient frontier
    frontier = generate_efficient_frontier(returns_df)
    
    if frontier and "error" not in frontier:
        # Plot efficient frontier
        fig = go.Figure()
        
        # Efficient frontier line
        fig.add_trace(go.Scatter(
            x=frontier["volatilities"],
            y=frontier["returns"],
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='#3B82F6', width=3)
        ))
        
        # Random portfolios
        fig.add_trace(go.Scatter(
            x=frontier["random_vols"],
            y=frontier["random_returns"],
            mode='markers',
            name='Random Portfolios',
            marker=dict(
                size=8,
                color=frontier["random_sharpes"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            )
        ))
        
        # Optimal portfolio
        fig.add_trace(go.Scatter(
            x=[frontier["optimal_vol"]],
            y=[frontier["optimal_return"]],
            mode='markers',
            name='Optimal Portfolio',
            marker=dict(size=15, color='red', symbol='star')
        ))
        
        fig.update_layout(
            title="Efficient Frontier - Risk vs Return",
            xaxis_title="Volatility (Risk) %",
            yaxis_title="Expected Return %",
            height=500,
            hovermode="closest"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Explanation
        st.markdown("""
        ### Understanding the Efficient Frontier
        
        - **Blue Line**: Optimal portfolios at each risk level
        - **Dots**: Randomly generated portfolios (color = Sharpe ratio)
        - **Red Star**: Maximum Sharpe ratio portfolio
        - **Goal**: Choose a point on the blue line matching your risk tolerance
        """)


def generate_efficient_frontier(returns_df, num_portfolios=1000):
    """Generate efficient frontier data"""
    try:
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        num_assets = len(returns_df.columns)
        
        # Generate random portfolios
        random_returns = []
        random_vols = []
        random_sharpes = []
        
        for _ in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= weights.sum()
            
            ret = np.dot(weights, mean_returns)
            vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (ret - 0.045) / vol
            
            random_returns.append(ret * 100)
            random_vols.append(vol * 100)
            random_sharpes.append(sharpe)
        
        # Calculate efficient frontier
        target_returns = np.linspace(min(random_returns), max(random_returns), 50)
        frontier_vols = []
        
        for target_ret in target_returns:
            def objective(weights):
                return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_ret/100}
            ]
            
            bounds = tuple((0, 1) for _ in range(num_assets))
            initial_weights = np.array([1/num_assets] * num_assets)
            
            result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                frontier_vols.append(result.fun * 100)
            else:
                frontier_vols.append(None)
        
        # Find optimal (max Sharpe)
        max_sharpe_idx = np.argmax(random_sharpes)
        
        return {
            "returns": target_returns,
            "volatilities": frontier_vols,
            "random_returns": random_returns,
            "random_vols": random_vols,
            "random_sharpes": random_sharpes,
            "optimal_return": random_returns[max_sharpe_idx],
            "optimal_vol": random_vols[max_sharpe_idx]
        }
        
    except Exception as e:
        return {"error": str(e)}


def show_risk_return_tab(portfolio_data):
    """Show individual asset risk/return analysis"""
    st.subheader("📈 Risk/Return Analysis")
    st.markdown("*Compare individual assets*")
    
    tickers = portfolio_data.get("tickers", [])
    portfolio = portfolio_data.get("portfolio", {})
    
    # Calculate metrics for each asset
    asset_metrics = []
    
    for ticker in tickers:
        hist = portfolio[ticker]["history"]
        returns = hist['Close'].pct_change().dropna()
        
        annual_return = returns.mean() * 252 * 100
        annual_vol = returns.std() * np.sqrt(252) * 100
        sharpe = (annual_return - 4.5) / annual_vol if annual_vol > 0 else 0
        
        # Max drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min() * 100
        
        asset_metrics.append({
            "Ticker": ticker,
            "Return": f"{annual_return:.2f}%",
            "Volatility": f"{annual_vol:.2f}%",
            "Sharpe Ratio": f"{sharpe:.2f}",
            "Max Drawdown": f"{max_dd:.1f}%"
        })
    
    st.dataframe(asset_metrics, use_container_width=True)
    
    # Correlation matrix
    st.markdown("### Correlation Matrix")
    st.markdown("*How assets move together (1.0 = perfect correlation)*")
    
    returns_df = portfolio_data.get("returns")
    if isinstance(returns_df, dict):
        returns_df = pd.DataFrame(returns_df)
    
    corr_matrix = returns_df.corr()
    
    # Plot correlation heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdYlGn',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Asset Correlation Matrix",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_rebalancing_tab(portfolio_data, investment):
    """Show portfolio rebalancing recommendations"""
    st.subheader("💰 Portfolio Rebalancing")
    st.markdown("*Keep your portfolio optimized over time*")
    
    st.markdown("""
    ### When to Rebalance
    
    Rebalance your portfolio when:
    - Any asset drifts more than 5% from target allocation
    - Quarterly or semi-annually (set schedule)
    - After major market movements
    - When adding new capital
    
    ### Rebalancing Strategy
    
    1. **Threshold Rebalancing**: Rebalance when allocations drift beyond tolerance
    2. **Calendar Rebalancing**: Rebalance on a fixed schedule (e.g., quarterly)
    3. **Hybrid Approach**: Combine both methods
    """)
    
    # Example rebalancing scenario
    st.markdown("### Example Rebalancing Scenario")
    
    tickers = portfolio_data.get("tickers", [])[:5]  # First 5 tickers
    
    rebalance_data = {
        "Ticker": tickers,
        "Target %": ["25%", "20%", "20%", "20%", "15%"],
        "Current %": ["30%", "18%", "22%", "15%", "15%"],
        "Drift": ["+5%", "-2%", "+2%", "-5%", "0%"],
        "Action": ["🔴 SELL", "🟢 BUY", "🟡 HOLD", "🟢 BUY", "🟡 HOLD"]
    }
    
    st.dataframe(rebalance_data, use_container_width=True)
    
    st.info("💡 **Pro Tip**: Consider tax implications when rebalancing. In taxable accounts, use new contributions to rebalance rather than selling appreciated assets.")
