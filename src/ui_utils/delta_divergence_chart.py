"""
Delta Divergence Options Chart
Shows market expectation through call vs put delta analysis with volume weighting
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
from typing import Dict, List, Tuple, Optional


class DeltaDivergenceAnalyzer:
    """
    Analyzes options delta divergence to determine market expectations.
    
    Delta divergence shows if market makers and traders expect upward or downward movement
    by comparing call delta exposure vs put delta exposure, weighted by volume.
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.current_price = None
        self.options_data = {}
    
    def fetch_options_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch all available options chains"""
        try:
            # Get current price
            info = self.stock.info
            self.current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            # Get all expiration dates
            expirations = self.stock.options
            
            if not expirations:
                return {}
            
            # Fetch options chains for each expiration
            for exp_date in expirations:
                try:
                    opt_chain = self.stock.option_chain(exp_date)
                    
                    # Add metadata
                    calls = opt_chain.calls.copy()
                    puts = opt_chain.puts.copy()
                    
                    calls['type'] = 'call'
                    puts['type'] = 'put'
                    calls['expiration'] = exp_date
                    puts['expiration'] = exp_date
                    
                    # Calculate days to expiration
                    exp_datetime = datetime.strptime(exp_date, '%Y-%m-%d')
                    days_to_exp = (exp_datetime - datetime.now()).days
                    
                    calls['days_to_expiration'] = days_to_exp
                    puts['days_to_expiration'] = days_to_exp
                    
                    self.options_data[exp_date] = {
                        'calls': calls,
                        'puts': puts,
                        'days_to_expiration': days_to_exp
                    }
                except Exception as e:
                    continue
            
            return self.options_data
            
        except Exception as e:
            st.error(f"Error fetching options data: {e}")
            return {}
    
    def calculate_delta_divergence(self, expiration_date: str) -> Dict:
        """
        Calculate delta divergence for a specific expiration.
        
        Returns:
            Dict with call_delta_flow, put_delta_flow, net_delta_flow, and market_expectation
        """
        if expiration_date not in self.options_data:
            return None
        
        data = self.options_data[expiration_date]
        calls = data['calls']
        puts = data['puts']
        
        # Calculate volume-weighted delta flow
        # Delta approximation: ATM options ~0.5, ITM closer to 1, OTM closer to 0
        
        # For calls: delta increases as strike decreases (more ITM)
        # For puts: delta (absolute) increases as strike increases (more ITM)
        
        call_deltas = []
        call_volumes = []
        call_strikes = []
        
        for _, row in calls.iterrows():
            strike = row['strike']
            volume = row.get('volume', 0) or 0
            open_interest = row.get('openInterest', 0) or 0
            
            # Use max of volume and 10% of OI as proxy for activity
            effective_volume = max(volume, open_interest * 0.1)
            
            if effective_volume > 0 and self.current_price:
                # Approximate delta using Black-Scholes approximation
                # Simplified: delta ≈ N(d1) where d1 relates to moneyness
                moneyness = self.current_price / strike
                
                if moneyness >= 1.2:  # Deep ITM
                    delta = 0.9
                elif moneyness >= 1.05:  # ITM
                    delta = 0.7
                elif moneyness >= 0.95:  # ATM
                    delta = 0.5
                elif moneyness >= 0.8:  # OTM
                    delta = 0.3
                else:  # Deep OTM
                    delta = 0.1
                
                call_deltas.append(delta)
                call_volumes.append(effective_volume)
                call_strikes.append(strike)
        
        put_deltas = []
        put_volumes = []
        put_strikes = []
        
        for _, row in puts.iterrows():
            strike = row['strike']
            volume = row.get('volume', 0) or 0
            open_interest = row.get('openInterest', 0) or 0
            
            effective_volume = max(volume, open_interest * 0.1)
            
            if effective_volume > 0 and self.current_price:
                # For puts, delta is negative
                moneyness = strike / self.current_price
                
                if moneyness >= 1.2:  # Deep ITM
                    delta = -0.9
                elif moneyness >= 1.05:  # ITM
                    delta = -0.7
                elif moneyness >= 0.95:  # ATM
                    delta = -0.5
                elif moneyness >= 0.8:  # OTM
                    delta = -0.3
                else:  # Deep OTM
                    delta = -0.1
                
                put_deltas.append(delta)
                put_volumes.append(effective_volume)
                put_strikes.append(strike)
        
        # Calculate volume-weighted delta flow
        call_delta_flow = sum(d * v for d, v in zip(call_deltas, call_volumes)) if call_deltas else 0
        put_delta_flow = sum(d * v for d, v in zip(put_deltas, put_volumes)) if put_deltas else 0
        
        # Net delta flow (positive = bullish, negative = bearish)
        net_delta_flow = call_delta_flow + put_delta_flow  # put_delta_flow is negative
        
        # Calculate total volume for normalization
        total_call_volume = sum(call_volumes) if call_volumes else 1
        total_put_volume = sum(put_volumes) if put_volumes else 1
        
        # Normalize by volume
        avg_call_delta = call_delta_flow / total_call_volume if total_call_volume > 0 else 0
        avg_put_delta = put_delta_flow / total_put_volume if total_put_volume > 0 else 0
        
        # Determine market expectation
        if net_delta_flow > total_call_volume * 0.1:
            market_expectation = "🟢 BULLISH - Strong Call Delta Dominance"
            sentiment = "bullish"
        elif net_delta_flow > 0:
            market_expectation = "🟡 MODERATELY BULLISH - Slight Call Bias"
            sentiment = "moderately_bullish"
        elif net_delta_flow > -total_put_volume * 0.1:
            market_expectation = "🟡 MODERATELY BEARISH - Slight Put Bias"
            sentiment = "moderately_bearish"
        else:
            market_expectation = "🔴 BEARISH - Strong Put Delta Dominance"
            sentiment = "bearish"
        
        # Calculate call/put ratio
        call_put_ratio = total_call_volume / total_put_volume if total_put_volume > 0 else 0
        
        return {
            'call_delta_flow': call_delta_flow,
            'put_delta_flow': put_delta_flow,
            'net_delta_flow': net_delta_flow,
            'avg_call_delta': avg_call_delta,
            'avg_put_delta': avg_put_delta,
            'total_call_volume': total_call_volume,
            'total_put_volume': total_put_volume,
            'call_put_ratio': call_put_ratio,
            'market_expectation': market_expectation,
            'sentiment': sentiment,
            'call_strikes': call_strikes,
            'call_deltas': call_deltas,
            'call_volumes': call_volumes,
            'put_strikes': put_strikes,
            'put_deltas': put_deltas,
            'put_volumes': put_volumes,
            'days_to_expiration': data['days_to_expiration']
        }
    
    def get_all_divergences(self) -> pd.DataFrame:
        """Calculate delta divergence for all expirations"""
        results = []
        
        for exp_date in sorted(self.options_data.keys()):
            div = self.calculate_delta_divergence(exp_date)
            if div:
                results.append({
                    'expiration': exp_date,
                    'days_to_expiration': div['days_to_expiration'],
                    'net_delta_flow': div['net_delta_flow'],
                    'call_delta_flow': div['call_delta_flow'],
                    'put_delta_flow': div['put_delta_flow'],
                    'call_put_ratio': div['call_put_ratio'],
                    'sentiment': div['sentiment'],
                    'market_expectation': div['market_expectation']
                })
        
        return pd.DataFrame(results)


def render_delta_divergence_chart(ticker: str):
    """
    Render the complete Delta Divergence Options Chart with interactive slider
    """
    st.markdown("## 📊 Delta Divergence Options Analysis")
    st.markdown("""
    **What is Delta Divergence?**  
    Delta measures how much an option's price changes relative to the underlying stock.
    By analyzing volume-weighted delta across calls vs puts, we can gauge market expectations:
    - **Positive divergence** (more call delta) → Market expects upward movement 🟢
    - **Negative divergence** (more put delta) → Market expects downward movement 🔴
    """)
    
    # Initialize analyzer
    with st.spinner(f"📡 Fetching options data for {ticker}..."):
        analyzer = DeltaDivergenceAnalyzer(ticker)
        options_data = analyzer.fetch_options_data()
    
    if not options_data:
        st.error(f"❌ No options data available for {ticker}")
        return
    
    st.success(f"✅ Loaded options data for {len(options_data)} expiration dates")
    
    # Show current price
    if analyzer.current_price:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Current Price", f"${analyzer.current_price:.2f}")
        with col2:
            st.metric("Available Expirations", len(options_data))
    
    # Calculate divergences for all expirations
    all_divergences = analyzer.get_all_divergences()
    
    if all_divergences.empty:
        st.warning("⚠️ Unable to calculate delta divergence")
        return
    
    # Expiration date slider
    st.markdown("### 🎚️ Select Expiration Date")
    
    expiration_dates = sorted(options_data.keys())
    expiration_labels = [
        f"{date} ({options_data[date]['days_to_expiration']}d)" 
        for date in expiration_dates
    ]
    
    # Create slider
    selected_index = st.select_slider(
        "Choose expiration date:",
        options=range(len(expiration_dates)),
        format_func=lambda x: expiration_labels[x],
        value=0  # Default to nearest expiration
    )
    
    selected_expiration = expiration_dates[selected_index]
    selected_data = options_data[selected_expiration]
    
    # Calculate divergence for selected expiration
    divergence = analyzer.calculate_delta_divergence(selected_expiration)
    
    if not divergence:
        st.error("Unable to calculate divergence for selected date")
        return
    
    # Display market expectation prominently
    st.markdown("---")
    expectation = divergence['market_expectation']
    sentiment = divergence['sentiment']
    
    if 'BULLISH' in expectation:
        st.success(f"### {expectation}")
    elif 'BEARISH' in expectation:
        st.error(f"### {expectation}")
    else:
        st.info(f"### {expectation}")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Net Delta Flow",
            f"{divergence['net_delta_flow']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Call/Put Ratio",
            f"{divergence['call_put_ratio']:.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "Total Call Volume",
            f"{divergence['total_call_volume']:,.0f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "Total Put Volume",
            f"{divergence['total_put_volume']:,.0f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Create diverging bar chart
    fig = create_diverging_bar_chart(divergence, analyzer.current_price)
    st.plotly_chart(fig, use_container_width=True)
    
    # Create summary chart across all expirations
    st.markdown("### 📈 Delta Divergence Across All Expirations")
    summary_fig = create_summary_chart(all_divergences)
    st.plotly_chart(summary_fig, use_container_width=True)
    
    # Detailed breakdown
    with st.expander("📊 Detailed Strike Analysis", expanded=False):
        st.markdown("#### Call Options Delta Distribution")
        
        call_df = pd.DataFrame({
            'Strike': divergence['call_strikes'],
            'Delta': divergence['call_deltas'],
            'Volume': divergence['call_volumes'],
            'Delta × Volume': [d * v for d, v in zip(divergence['call_deltas'], divergence['call_volumes'])]
        })
        
        if not call_df.empty:
            call_df = call_df.sort_values('Strike')
            st.dataframe(call_df.style.format({
                'Strike': '${:.2f}',
                'Delta': '{:.3f}',
                'Volume': '{:.0f}',
                'Delta × Volume': '{:.0f}'
            }), use_container_width=True)
        
        st.markdown("#### Put Options Delta Distribution")
        
        put_df = pd.DataFrame({
            'Strike': divergence['put_strikes'],
            'Delta': divergence['put_deltas'],
            'Volume': divergence['put_volumes'],
            'Delta × Volume': [d * v for d, v in zip(divergence['put_deltas'], divergence['put_volumes'])]
        })
        
        if not put_df.empty:
            put_df = put_df.sort_values('Strike')
            st.dataframe(put_df.style.format({
                'Strike': '${:.2f}',
                'Delta': '{:.3f}',
                'Volume': '{:.0f}',
                'Delta × Volume': '{:.0f}'
            }), use_container_width=True)
    
    # Interpretation guide
    with st.expander("📚 How to Interpret Delta Divergence", expanded=False):
        st.markdown("""
        ### Understanding the Chart
        
        **Positive (Green) Bars**: Call options delta flow
        - Indicates bullish positioning by market participants
        - Higher bars = more conviction in upward movement
        
        **Negative (Red) Bars**: Put options delta flow  
        - Indicates bearish positioning by market participants
        - Lower bars = more conviction in downward movement
        
        **Net Delta Flow**: The difference between call and put delta
        - **Positive**: Market expects stock to go UP 📈
        - **Negative**: Market expects stock to go DOWN 📉
        - **Near Zero**: Market is uncertain or neutral
        
        ### Volume Weighting
        Delta is multiplied by volume to show conviction:
        - **High volume + High delta** = Strong directional bet
        - **Low volume + High delta** = Weak signal
        
        ### Call/Put Ratio
        - **> 1.0**: More call activity (bullish)
        - **< 1.0**: More put activity (bearish)
        - **~1.0**: Balanced market
        
        ### Days to Expiration
        - **Near-term** (< 30 days): Shows immediate expectations
        - **Medium-term** (30-90 days): Shows trend expectations
        - **Long-term** (> 90 days): Shows strategic positioning
        """)


def create_diverging_bar_chart(divergence: Dict, current_price: float) -> go.Figure:
    """Create the main diverging bar chart"""
    
    # Prepare data for diverging bars
    categories = ['Call Delta Flow', 'Put Delta Flow', 'Net Delta Flow']
    values = [
        divergence['call_delta_flow'],
        divergence['put_delta_flow'],
        divergence['net_delta_flow']
    ]
    
    # Create figure with secondary y-axis for net flow
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=(
            'Volume-Weighted Delta Flow (Calls vs Puts)',
            'Net Delta Flow Trend'
        ),
        vertical_spacing=0.15
    )
    
    # Main diverging bar chart
    fig.add_trace(
        go.Bar(
            x=['Call Delta'],
            y=[divergence['call_delta_flow']],
            name='Call Delta',
            marker=dict(color='#00cc00', line=dict(color='#009900', width=2)),
            text=[f"{divergence['call_delta_flow']:,.0f}"],
            textposition='outside',
            hovertemplate='<b>Call Delta Flow</b><br>Value: %{y:,.0f}<br>Avg Delta: ' + 
                         f"{divergence['avg_call_delta']:.3f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=['Put Delta'],
            y=[divergence['put_delta_flow']],
            name='Put Delta',
            marker=dict(color='#ff3333', line=dict(color='#cc0000', width=2)),
            text=[f"{divergence['put_delta_flow']:,.0f}"],
            textposition='outside',
            hovertemplate='<b>Put Delta Flow</b><br>Value: %{y:,.0f}<br>Avg Delta: ' + 
                         f"{divergence['avg_put_delta']:.3f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Add net delta flow as a line
    fig.add_trace(
        go.Scatter(
            x=['Call Delta', 'Put Delta'],
            y=[divergence['net_delta_flow'], divergence['net_delta_flow']],
            name='Net Delta Flow',
            mode='lines+markers',
            line=dict(color='#ffaa00', width=3, dash='dash'),
            marker=dict(size=12, symbol='diamond'),
            hovertemplate='<b>Net Delta Flow</b><br>%{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add zero line
    fig.add_hline(y=0, line=dict(color='gray', width=1, dash='dot'), row=1, col=1)
    
    # Net flow indicator (bottom panel)
    net_value = divergence['net_delta_flow']
    color = '#00cc00' if net_value > 0 else '#ff3333'
    
    fig.add_trace(
        go.Bar(
            x=['Net Flow'],
            y=[net_value],
            name='Net Delta',
            marker=dict(color=color, line=dict(color='black', width=2)),
            text=[f"{net_value:,.0f}"],
            textposition='outside',
            showlegend=False,
            hovertemplate='<b>Net Delta Flow</b><br>%{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Add annotation for market expectation
    expectation_text = divergence['market_expectation']
    annotation_color = '#00cc00' if 'BULLISH' in expectation_text else '#ff3333'
    
    fig.add_annotation(
        text=f"<b>{expectation_text}</b>",
        xref="paper", yref="paper",
        x=0.5, y=1.08,
        showarrow=False,
        font=dict(size=16, color=annotation_color),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor=annotation_color,
        borderwidth=2,
        borderpad=10
    )
    
    # Update layout
    fig.update_layout(
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    # Update axes
    fig.update_xaxes(title_text="Option Type", row=1, col=1)
    fig.update_yaxes(title_text="Volume-Weighted Delta", row=1, col=1)
    
    fig.update_xaxes(title_text="", row=2, col=1)
    fig.update_yaxes(title_text="Net Delta Flow", row=2, col=1)
    
    # Add grid
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    return fig


def create_summary_chart(all_divergences: pd.DataFrame) -> go.Figure:
    """Create summary chart showing delta divergence across all expirations"""
    
    fig = go.Figure()
    
    # Sort by expiration
    df = all_divergences.sort_values('days_to_expiration')
    
    # Create color scale based on sentiment
    colors = []
    for sentiment in df['sentiment']:
        if sentiment == 'bullish':
            colors.append('#00cc00')
        elif sentiment == 'moderately_bullish':
            colors.append('#88cc00')
        elif sentiment == 'moderately_bearish':
            colors.append('#ff8800')
        else:
            colors.append('#ff3333')
    
    # Add bars
    fig.add_trace(
        go.Bar(
            x=df['expiration'],
            y=df['net_delta_flow'],
            name='Net Delta Flow',
            marker=dict(
                color=colors,
                line=dict(color='black', width=1)
            ),
            text=[f"{val:,.0f}" for val in df['net_delta_flow']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Net Delta: %{y:,.0f}<br>' +
                         'Days: ' + df['days_to_expiration'].astype(str) + 
                         '<extra></extra>'
        )
    )
    
    # Add zero line
    fig.add_hline(y=0, line=dict(color='gray', width=2, dash='dash'))
    
    # Update layout
    fig.update_layout(
        title="Net Delta Flow by Expiration Date",
        xaxis_title="Expiration Date",
        yaxis_title="Net Delta Flow",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(240,240,240,0.5)',
        paper_bgcolor='white',
        hovermode='x unified'
    )
    
    # Rotate x-axis labels
    fig.update_xaxes(tickangle=-45)
    
    return fig


def render_delta_divergence_compact(ticker: str):
    """Compact version for dashboard integration"""
    analyzer = DeltaDivergenceAnalyzer(ticker)
    options_data = analyzer.fetch_options_data()
    
    if not options_data:
        st.warning("⚠️ No options data available")
        return
    
    # Get nearest expiration
    nearest_exp = sorted(options_data.keys())[0]
    divergence = analyzer.calculate_delta_divergence(nearest_exp)
    
    if divergence:
        st.metric(
            "Delta Divergence (Nearest Exp)",
            f"{divergence['net_delta_flow']:,.0f}",
            delta=divergence['market_expectation']
        )
