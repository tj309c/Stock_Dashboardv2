import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ticker_utils import setup_sidebar_ticker_input
from app_utils import create_gauge_chart, normalize_dividend_yield, plotly_full_width, display_dataframe_full_width
from mode_config import render_mode_info, should_show_feature

def render_page():
    """Main Earnings & Estimates Dashboard - Deep dive into earnings, estimates, and analyst coverage"""
    st.title("📅 Earnings & Estimates Intelligence")
    st.caption("Comprehensive analysis of earnings history, future estimates, analyst ratings, and dividend information")

    # Display current trading mode
    render_mode_info()

    # Setup sidebar ticker input
    ticker = setup_sidebar_ticker_input("earnings_estimates")

    # Fetch stock data
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        earnings_dates = stock.earnings_dates
        info = stock.info

        try:
            from data_fetcher import get_eps_estimates_list
            eps_estimates_list = get_eps_estimates_list(ticker)
        except Exception:
            eps_estimates_list = []

    except Exception as e:
        st.error(f"Could not load data for '{ticker}': {e}")
        st.stop()

    # ========================================
    # UPCOMING EARNINGS
    # ========================================
    render_upcoming_earnings_section(calendar, ticker)

    st.divider()

    # ========================================
    # HISTORICAL EARNINGS PERFORMANCE
    # ========================================
    render_historical_earnings_section(earnings_dates, stock, ticker)

    st.divider()

    # ========================================
    # DIVIDEND INFORMATION
    # ========================================
    render_dividend_information_section(calendar, stock, ticker)

    st.divider()

    # ========================================
    # ANALYST RATINGS & PRICE TARGETS
    # ========================================
    render_analyst_ratings_section(stock, ticker)

    st.divider()

    # ========================================
    # ADVANCED EARNINGS MODULES
    # ========================================
    render_advanced_earnings_modules(stock, earnings_dates, ticker)


def render_upcoming_earnings_section(calendar, ticker):
    """Render upcoming earnings section with estimates"""
    st.markdown("## 🔜 Upcoming Earnings")

    if calendar and isinstance(calendar, dict):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            earnings_date = calendar.get('Earnings Date')
            if earnings_date:
                if isinstance(earnings_date, list) and len(earnings_date) > 0:
                    earnings_date = earnings_date[0]
                st.metric("📅 Next Earnings",
                         earnings_date.strftime('%b %d, %Y') if hasattr(earnings_date, 'strftime') else str(earnings_date))

        with col2:
            eps_avg = calendar.get('Earnings Average')
            eps_low = calendar.get('Earnings Low')
            eps_high = calendar.get('Earnings High')

            if eps_avg is not None:
                try:
                    st.metric("📊 EPS Estimate", f"${float(eps_avg):.2f}",
                             delta=f"Range: ${float(eps_low):.2f} - ${float(eps_high):.2f}" if eps_low and eps_high else None)
                except Exception:
                    st.metric("📊 EPS Estimate", f"{eps_avg}")
            else:
                st.metric("📊 EPS Estimate", "N/A")

        with col3:
            rev_avg = calendar.get('Revenue Average')
            if rev_avg:
                try:
                    st.metric("💰 Revenue Estimate", f"${float(rev_avg)/1e9:.2f}B")
                except Exception:
                    st.metric("💰 Revenue Estimate", f"{rev_avg}")
            else:
                st.metric("💰 Revenue Estimate", "N/A")

        with col4:
            rev_low = calendar.get('Revenue Low')
            rev_high = calendar.get('Revenue High')
            if rev_low and rev_high:
                try:
                    st.metric("📈 Revenue Range", f"${float(rev_low)/1e9:.2f}B - ${float(rev_high)/1e9:.2f}B")
                except Exception:
                    st.metric("📈 Revenue Range", "N/A")
            else:
                st.metric("📈 Revenue Range", "N/A")

        # Analyst consensus chart
        if eps_avg is not None and eps_low is not None and eps_high is not None:
            st.markdown("### 📊 Analyst EPS Estimates")
            st.caption("Range chart shows analyst consensus: green diamond = average estimate, "
                      "red triangles = low/high range. Narrower range = higher analyst agreement.")

            eps_low_val = float(eps_low)
            eps_avg_val = float(eps_avg)
            eps_high_val = float(eps_high)

            fig = go.Figure()

            # Add vertical range bar
            fig.add_trace(go.Scatter(
                x=['EPS Estimate', 'EPS Estimate'],
                y=[eps_low_val, eps_high_val],
                mode='lines',
                line=dict(color='rgba(99, 110, 250, 0.6)', width=40),
                showlegend=False,
                hoverinfo='skip'
            ))

            # Add marker points
            fig.add_trace(go.Scatter(
                x=['EPS Estimate', 'EPS Estimate', 'EPS Estimate'],
                y=[eps_low_val, eps_avg_val, eps_high_val],
                mode='markers+text',
                marker=dict(
                    size=[12, 16, 12],
                    color=['#EF553B', '#00CC96', '#EF553B'],
                    symbol=['triangle-down', 'diamond', 'triangle-up'],
                    line=dict(width=2, color='white')
                ),
                text=[f'Low: ${eps_low_val:.2f}', f'Avg: ${eps_avg_val:.2f}', f'High: ${eps_high_val:.2f}'],
                textposition=['middle left', 'middle right', 'middle left'],
                textfont=dict(size=12, color='black'),
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            ))

            spread = eps_high_val - eps_low_val
            spread_pct = (spread / eps_avg_val * 100) if eps_avg_val != 0 else 0

            fig.update_layout(
                yaxis_title="EPS ($)",
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(range=[eps_low_val * 0.95, eps_high_val * 1.05], gridcolor='lightgray'),
                height=400,
                showlegend=False,
                margin=dict(l=80, r=150, t=60, b=60),
                plot_bgcolor='white',
                annotations=[
                    dict(
                        text=f"Analyst Agreement: {'High' if spread_pct < 10 else 'Medium' if spread_pct < 20 else 'Low'} (±{spread_pct:.1f}%)",
                        xref="paper", yref="paper",
                        x=0.5, y=1.05,
                        showarrow=False,
                        font=dict(size=12, color='#636EFA', family='Arial Black')
                    )
                ]
            )

            plotly_full_width(fig)
    else:
        st.info("No upcoming earnings calendar available")


def render_historical_earnings_section(earnings_dates, stock, ticker):
    """Render historical earnings performance analysis"""
    st.markdown("## 📊 Historical Earnings Performance")

    if earnings_dates is not None and not earnings_dates.empty:
        historical = earnings_dates[earnings_dates['Reported EPS'].notna()].head(8)

        if not historical.empty:
            st.markdown("### 📋 Recent Earnings Results")

            display_df = historical.copy()
            display_df.index = display_df.index.strftime('%b %d, %Y')
            display_df.columns = ['Estimate', 'Actual', 'Surprise %']

            display_df['Estimate'] = display_df['Estimate'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['Actual'] = display_df['Actual'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['Surprise %'] = display_df['Surprise %'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")

            display_dataframe_full_width(display_df)

            # Earnings surprise chart
            st.markdown("### 📈 Earnings Surprise Trend with Price Impact")
            st.caption("Green bars = beat estimates | Red bars = missed estimates | Lines show stock price movement pre/post earnings")

            chart_data = historical[['EPS Estimate', 'Reported EPS', 'Surprise(%)']].dropna()

            if not chart_data.empty:
                try:
                    price_data = stock.history(period='2y', interval='1d')

                    pre_earnings_change = []
                    post_earnings_change = []

                    for earnings_date in chart_data.index:
                        try:
                            window_days = 5
                            date_loc = price_data.index.get_indexer([earnings_date], method='nearest')[0]

                            pre_start_idx = max(0, date_loc - window_days)
                            pre_end_idx = date_loc

                            post_start_idx = date_loc
                            post_end_idx = min(len(price_data) - 1, date_loc + window_days)

                            if pre_start_idx < pre_end_idx and pre_end_idx < len(price_data):
                                pre_price_start = price_data.iloc[pre_start_idx]['Close']
                                pre_price_end = price_data.iloc[pre_end_idx]['Close']
                                pre_change = ((pre_price_end - pre_price_start) / pre_price_start * 100) if pre_price_start != 0 else 0
                                pre_earnings_change.append(pre_change)
                            else:
                                pre_earnings_change.append(None)

                            if post_start_idx < post_end_idx and post_end_idx < len(price_data):
                                post_price_start = price_data.iloc[post_start_idx]['Close']
                                post_price_end = price_data.iloc[post_end_idx]['Close']
                                post_change = ((post_price_end - post_price_start) / post_price_start * 100) if post_price_start != 0 else 0
                                post_earnings_change.append(post_change)
                            else:
                                post_earnings_change.append(None)

                        except Exception:
                            pre_earnings_change.append(None)
                            post_earnings_change.append(None)

                    chart_data['Pre-Earnings Move (%)'] = pre_earnings_change
                    chart_data['Post-Earnings Move (%)'] = post_earnings_change

                except Exception as e:
                    st.warning(f"Could not calculate price movements: {e}")
                    chart_data['Pre-Earnings Move (%)'] = None
                    chart_data['Post-Earnings Move (%)'] = None

                # Create chart
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                fig.add_trace(
                    go.Bar(
                        x=chart_data.index.strftime('%b %Y'),
                        y=chart_data['Surprise(%)'],
                        name='EPS Surprise',
                        marker_color=['#00CC96' if x > 0 else '#EF553B' for x in chart_data['Surprise(%)']],
                        text=[f"{x:.1f}%" for x in chart_data['Surprise(%)']],
                        textposition='outside',
                        opacity=0.7
                    ),
                    secondary_y=False
                )

                if 'Pre-Earnings Move (%)' in chart_data.columns and chart_data['Pre-Earnings Move (%)'].notna().any():
                    fig.add_trace(
                        go.Scatter(
                            x=chart_data.index.strftime('%b %Y'),
                            y=chart_data['Pre-Earnings Move (%)'],
                            name='Pre-Earnings (5d)',
                            mode='lines+markers',
                            line=dict(color='#AB63FA', width=2, dash='dot'),
                            marker=dict(size=8, symbol='diamond')
                        ),
                        secondary_y=True
                    )

                if 'Post-Earnings Move (%)' in chart_data.columns and chart_data['Post-Earnings Move (%)'].notna().any():
                    fig.add_trace(
                        go.Scatter(
                            x=chart_data.index.strftime('%b %Y'),
                            y=chart_data['Post-Earnings Move (%)'],
                            name='Post-Earnings (5d)',
                            mode='lines+markers',
                            line=dict(color='#FFA15A', width=2),
                            marker=dict(size=8, symbol='circle')
                        ),
                        secondary_y=True
                    )

                fig.update_xaxes(title_text="Earnings Date")
                fig.update_yaxes(title_text="EPS Surprise (%)", secondary_y=False)
                fig.update_yaxes(title_text="Price Movement (%)", secondary_y=True)

                fig.update_layout(
                    height=450,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode='x unified'
                )

                plotly_full_width(fig)

                # Summary stats
                avg_surprise = chart_data['Surprise(%)'].mean()
                beat_rate = (chart_data['Surprise(%)'] > 0).sum() / len(chart_data) * 100

                if 'Pre-Earnings Move (%)' in chart_data.columns and chart_data['Pre-Earnings Move (%)'].notna().any():
                    avg_pre_move = chart_data['Pre-Earnings Move (%)'].mean()
                    avg_post_move = chart_data['Post-Earnings Move (%)'].mean()
                else:
                    avg_pre_move = None
                    avg_post_move = None

                if avg_pre_move is not None and avg_post_move is not None:
                    col1, col2, col3, col4, col5 = st.columns(5)
                else:
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 0, 0])

                with col1:
                    st.metric("📊 Avg Surprise", f"{avg_surprise:.2f}%", delta="Beat" if avg_surprise > 0 else "Miss")
                with col2:
                    st.metric("🎯 Beat Rate", f"{beat_rate:.0f}%",
                             delta=f"{int((chart_data['Surprise(%)'] > 0).sum())}/{len(chart_data)} quarters")
                with col3:
                    last_surprise = chart_data['Surprise(%)'].iloc[0]
                    st.metric("📌 Last Surprise", f"{last_surprise:.2f}%", delta="Beat" if last_surprise > 0 else "Miss")

                if avg_pre_move is not None and avg_post_move is not None:
                    with col4:
                        st.metric("📉 Avg Pre-Move", f"{avg_pre_move:.2f}%",
                                 delta="Up" if avg_pre_move > 0 else "Down",
                                 help="Average price change 5 days before earnings")
                    with col5:
                        st.metric("📈 Avg Post-Move", f"{avg_post_move:.2f}%",
                                 delta="Up" if avg_post_move > 0 else "Down",
                                 help="Average price change 5 days after earnings")
    else:
        st.info("No historical earnings data available")


def render_dividend_information_section(calendar, stock, ticker):
    """Render dividend information section"""
    st.markdown("## 💵 Dividend Information")

    if calendar and isinstance(calendar, dict):
        col1, col2, col3 = st.columns(3)

        with col1:
            div_date = calendar.get('Dividend Date')
            if div_date:
                st.metric("📅 Dividend Date", div_date.strftime('%b %d, %Y') if hasattr(div_date, 'strftime') else str(div_date))
            else:
                st.metric("📅 Dividend Date", "N/A")

        with col2:
            ex_div_date = calendar.get('Ex-Dividend Date')
            if ex_div_date:
                st.metric("📅 Ex-Dividend Date", ex_div_date.strftime('%b %d, %Y') if hasattr(ex_div_date, 'strftime') else str(ex_div_date))
            else:
                st.metric("📅 Ex-Dividend Date", "N/A")

        with col3:
            try:
                info = stock.info
                current_price = info.get('currentPrice', info.get('regularMarketPrice', None))
                div_yield_pct, source = normalize_dividend_yield(info, current_price)

                if div_yield_pct is not None:
                    delta_text = None
                    if info.get('dividendRate'):
                        try:
                            delta_text = f"${float(info.get('dividendRate')):.2f}/share"
                        except Exception:
                            delta_text = None

                    st.metric("💰 Dividend Yield", f"{div_yield_pct:.2f}%", delta=delta_text)
                    st.caption(f"Source: {source.replace('_', ' ')}")
                else:
                    st.metric("💰 Dividend Yield", "N/A")
                    if source and source.startswith('suspicious'):
                        st.caption("⚠️ Dividend data appears suspicious or implausible — cross-check provider values.")
            except Exception:
                st.metric("💰 Dividend Yield", "N/A")
    else:
        st.info("No dividend information available")


def render_analyst_ratings_section(stock, ticker):
    """Render analyst ratings and price targets"""
    st.markdown("## ⭐ Analyst Ratings & Price Targets")

    try:
        info = stock.info

        target_high = info.get('targetHighPrice')
        target_low = info.get('targetLowPrice')
        target_mean = info.get('targetMeanPrice')
        target_median = info.get('targetMedianPrice')
        recommendation = info.get('recommendationKey', 'N/A')
        num_analysts = info.get('numberOfAnalystOpinions')
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))

        if target_mean or target_median or recommendation != 'N/A':
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                if target_mean:
                    st.metric("🎯 Target Mean", f"${target_mean:.2f}",
                             delta=f"{((target_mean/current_price - 1)*100):+.1f}%" if current_price else None)
                else:
                    st.metric("🎯 Target Mean", "N/A")

            with col2:
                if target_median:
                    st.metric("📊 Target Median", f"${target_median:.2f}",
                             delta=f"{((target_median/current_price - 1)*100):+.1f}%" if current_price else None)
                else:
                    st.metric("📊 Target Median", "N/A")

            with col3:
                if target_high:
                    st.metric("📈 Target High", f"${target_high:.2f}",
                             delta=f"{((target_high/current_price - 1)*100):+.1f}%" if current_price else None)
                else:
                    st.metric("📈 Target High", "N/A")

            with col4:
                if target_low:
                    st.metric("📉 Target Low", f"${target_low:.2f}",
                             delta=f"{((target_low/current_price - 1)*100):+.1f}%" if current_price else None)
                else:
                    st.metric("📉 Target Low", "N/A")

            with col5:
                if num_analysts:
                    st.metric("👥 Analysts", f"{num_analysts}", help="Number of analysts covering this stock")
                else:
                    st.metric("👥 Analysts", "N/A")

            # Visual price target chart
            if target_low and target_high and target_mean and current_price:
                st.markdown("### 📊 Analyst Price Target Range")

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=['Price Target', 'Price Target'],
                    y=[target_low, target_high],
                    mode='lines',
                    line=dict(color='rgba(99, 110, 250, 0.5)', width=50),
                    showlegend=False,
                    hoverinfo='skip'
                ))

                fig.add_trace(go.Scatter(
                    x=['Price Target', 'Price Target', 'Price Target', 'Current Price'],
                    y=[target_low, target_mean, target_high, current_price],
                    mode='markers+text',
                    marker=dict(
                        size=[14, 18, 14, 18],
                        color=['#EF553B', '#00CC96', '#EF553B', '#FFA15A'],
                        symbol=['triangle-down', 'diamond', 'triangle-up', 'star'],
                        line=dict(width=2, color='white')
                    ),
                    text=[
                        f'Low: ${target_low:.2f}',
                        f'Mean: ${target_mean:.2f}',
                        f'High: ${target_high:.2f}',
                        f'Current: ${current_price:.2f}'
                    ],
                    textposition=['middle left', 'middle right', 'middle left', 'middle right'],
                    textfont=dict(size=12, color='black'),
                    hovertemplate='%{text}<extra></extra>',
                    showlegend=False
                ))

                mean_upside = ((target_mean - current_price) / current_price * 100) if current_price > 0 else 0

                fig.update_layout(
                    yaxis_title="Price ($)",
                    xaxis=dict(showticklabels=False, showgrid=False),
                    yaxis=dict(
                        range=[min(target_low, current_price) * 0.95, max(target_high, current_price) * 1.05],
                        gridcolor='lightgray'
                    ),
                    height=400,
                    showlegend=False,
                    margin=dict(l=80, r=150, t=60, b=60),
                    plot_bgcolor='white',
                    annotations=[
                        dict(
                            text=f"Analyst Consensus: {mean_upside:+.1f}% {'Upside' if mean_upside > 0 else 'Downside'} Potential",
                            xref="paper", yref="paper",
                            x=0.5, y=1.05,
                            showarrow=False,
                            font=dict(size=13, color='#636EFA', family='Arial Black')
                        )
                    ]
                )

                plotly_full_width(fig)

            # Recommendation display
            st.markdown("### 💡 Analyst Recommendation")

            rec_display = {
                'strong_buy': ('🟢 Strong Buy', '#00CC96'),
                'buy': ('🟢 Buy', '#00CC96'),
                'hold': ('🟡 Hold', '#FFA15A'),
                'sell': ('🔴 Sell', '#EF553B'),
                'strong_sell': ('🔴 Strong Sell', '#EF553B')
            }

            rec_text, rec_color = rec_display.get(recommendation.lower(), (recommendation.title(), '#636EFA'))

            st.markdown(
                f"""
                <div style='text-align: center; padding: 20px; background-color: {rec_color};
                     border-radius: 10px; color: white; font-size: 24px; font-weight: bold;'>
                    {rec_text}
                </div>
                """,
                unsafe_allow_html=True
            )

            if num_analysts:
                st.caption(f"Based on consensus of {num_analysts} analyst{'s' if num_analysts != 1 else ''}")

        else:
            st.info("No analyst ratings or price targets available for this ticker")

    except Exception as e:
        st.error(f"Could not load analyst ratings: {e}")


def render_advanced_earnings_modules(stock, earnings_dates, ticker):
    """Advanced modules for deeper earnings analysis"""
    st.markdown("## 🧩 Advanced Earnings Analysis Modules")

    with st.expander("🚀 **Coming Soon: Advanced Features**", expanded=False):
        st.markdown("""
        ### Future Modules:

        - **📊 Earnings Seasonality**: Identify patterns in earnings performance by quarter
        - **🎯 Beat/Miss Probability**: Predict likelihood of beating estimates based on historical patterns
        - **💹 Revenue vs EPS Analysis**: Deep dive into revenue growth vs earnings efficiency
        - **📈 Guidance Analysis**: Track management guidance accuracy over time
        - **🔔 Earnings Alerts**: Set up alerts for upcoming earnings dates and estimate changes
        - **🤖 AI Earnings Predictions**: Use ML to predict earnings outcomes
        - **📉 Earnings Quality Score**: Assess quality of earnings (cash flow vs accruals)
        - **🌐 Peer Earnings Comparison**: Compare earnings metrics vs industry peers

        These modules will provide institutional-grade earnings intelligence.
        """)

    # Earnings Calendar Export
    with st.expander("📥 **Export Options**", expanded=False):
        if earnings_dates is not None and not earnings_dates.empty:
            historical = earnings_dates[earnings_dates['Reported EPS'].notna()].head(8)
            if not historical.empty:
                csv = historical.to_csv()
                st.download_button(
                    "📥 Download Historical Earnings (CSV)",
                    csv,
                    f"{ticker}_historical_earnings.csv",
                    "text/csv",
                    key='download-earnings'
                )
        else:
            st.info("No earnings data available to export")


if __name__ == "__main__":
    render_page()
