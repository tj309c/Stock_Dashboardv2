import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from portfolio_optimizer import run_portfolio_optimization

def render_page():
    """Main function to render the Portfolio Optimization page."""
    st.title("💼 Portfolio Optimization (Modern Portfolio Theory)")
    st.write("This tool analyzes a portfolio of 2-5 stocks to find the optimal weighting for maximum risk-adjusted return (Sharpe Ratio).")
    
    tickers_input = st.text_input("Enter 2-5 Tickers (comma-separated)", "AAPL,MSFT,GOOG,AMZN")
    
    if st.button("Optimize Portfolio"):
        with st.spinner("Fetching 3 years of portfolio data and running 10,000 simulations..."):
            opt_results = run_portfolio_optimization(tickers_input)
            
            if opt_results:
                results_df, max_sharpe_stats, max_sharpe_weights, min_vol_stats, min_vol_weights, tickers = opt_results

                st.subheader("Optimal Portfolios")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🎯 Max Sharpe Ratio (Best Risk vs. Reward)")
                    
                    weights_df_sharpe = pd.DataFrame({'Ticker': tickers, 'Weight': max_sharpe_weights})
                    weights_df_sharpe = weights_df_sharpe[weights_df_sharpe['Weight'] > 0.001]
                    fig_sharpe = go.Figure(data=[go.Pie(labels=weights_df_sharpe['Ticker'], values=weights_df_sharpe['Weight'], hole=.3)])
                    fig_sharpe.update_layout(
                        title_text='Asset Allocation',
                        annotations=[dict(text=f'Sharpe<br>{max_sharpe_stats[2]:.2f}', x=0.5, y=0.5, font_size=20, showarrow=False)],
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_sharpe, use_container_width=True)
                    st.metric("Annual Return", f"{max_sharpe_stats[0]:.2%}")
                    st.metric("Annual Volatility", f"{max_sharpe_stats[1]:.2%}")
                
                with col2:
                    st.markdown("#### 🛡️ Minimum Volatility (Safest)")
                    
                    weights_df_vol = pd.DataFrame({'Ticker': tickers, 'Weight': min_vol_weights})
                    weights_df_vol = weights_df_vol[weights_df_vol['Weight'] > 0.001]
                    fig_vol = go.Figure(data=[go.Pie(labels=weights_df_vol['Ticker'], values=weights_df_vol['Weight'], hole=.3)])
                    fig_vol.update_layout(
                        title_text='Asset Allocation',
                        annotations=[dict(text=f'Return<br>{min_vol_stats[0]:.2%}', x=0.5, y=0.5, font_size=20, showarrow=False)],
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_vol, use_container_width=True, key="min_vol_pie")
                    st.metric("Annual Return", f"{min_vol_stats[0]:.2%}")
                    st.metric("Annual Volatility", f"{min_vol_stats[1]:.2%}")

                st.subheader("Efficient Frontier (10,000 Portfolios)")
                fig_frontier = go.Figure(data=go.Scatter(
                    x=results_df['Volatility'], y=results_df['Return'], mode='markers',
                    marker=dict(color=results_df['SharpeRatio'], colorscale='Viridis', showscale=True, colorbar=dict(title='Sharpe Ratio'))
                ))
                fig_frontier.add_trace(go.Scatter(x=[max_sharpe_stats[1]], y=[max_sharpe_stats[0]], mode='markers', marker=dict(color='red', size=15, symbol='star'), name='Max Sharpe'))
                fig_frontier.add_trace(go.Scatter(x=[min_vol_stats[1]], y=[min_vol_stats[0]], mode='markers', marker=dict(color='yellow', size=15, symbol='star'), name='Min Volatility'))
                fig_frontier.update_layout(xaxis_title='Volatility (Risk)', yaxis_title='Annualized Return', yaxis_tickformat='.0%', xaxis_tickformat='.0%', template="plotly_white")
                st.plotly_chart(fig_frontier, use_container_width=True)

if __name__ == "__main__":
    render_page()