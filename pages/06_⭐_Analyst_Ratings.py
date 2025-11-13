import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Assume these are available from your project structure
from app_logic import initialize_data_and_context
from data_fetcher import get_analyst_recommendations

def render_page():
    """Main function to render the Analyst Ratings page."""
    # --- Get Ticker and Initialize Context ---
    ticker = st.query_params.get("ticker", "AAPL")
    st.title(f"⭐ Analyst Ratings for {ticker}")
    ctx = initialize_data_and_context(ticker)

    # --- Main Page Logic ---
    recommendations_df = get_analyst_recommendations(ctx.stock_object)

    if recommendations_df.empty:
        st.warning("No analyst recommendations data available for this stock.")
    else:
        # 1. Display Consensus
        st.subheader("Analyst Consensus")
        rec_key = ctx.info.get('recommendationKey', 'N/A').title()
        num_analysts = ctx.info.get('numberOfAnalystOpinions', 'N/A')
        
        col1, col2 = st.columns(2)
        col1.metric("Consensus", rec_key)
        col2.metric("Number of Opinions", num_analysts)

        st.markdown(f"**Current Recommendation:** {rec_key}")

        # 2. Display Recommendation Trends
        st.subheader("Recommendation Trends")
        # Ensure 'Date' is datetime and set as index for plotting
        if 'Date' in recommendations_df.columns:
            recommendations_df['Date'] = pd.to_datetime(recommendations_df['Date'])
            recommendations_df_sorted = recommendations_df.sort_values(by='Date')

            # Aggregate counts for each recommendation category per date
            # Fill missing dates/categories with 0 for consistent plotting
            all_dates = pd.date_range(start=recommendations_df_sorted['Date'].min(), 
                                      end=recommendations_df_sorted['Date'].max(), 
                                      freq='MS') # Monthly start frequency

            # Create a full DataFrame with all dates and categories
            unique_categories = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']
            full_index = pd.MultiIndex.from_product([all_dates, unique_categories], names=['Date', 'Category'])
            
            # Count recommendations per date
            trends_df = recommendations_df_sorted.groupby(['Date', 'toRating']).size().unstack(fill_value=0)
            
            # Reindex to ensure all dates are present
            trends_df = trends_df.reindex(all_dates, fill_value=0)
            
            # Ensure all categories are present, fill missing with 0
            for cat in unique_categories:
                if cat not in trends_df.columns:
                    trends_df[cat] = 0
            trends_df = trends_df[unique_categories] # Order columns

            # Plotting with Plotly
            fig = go.Figure()

            colors = {
                'strongBuy': 'green',
                'buy': 'lightgreen',
                'hold': 'orange',
                'sell': 'salmon',
                'strongSell': 'red'
            }

            for col in unique_categories:
                if col in trends_df.columns:
                    fig.add_trace(go.Scatter(
                        x=trends_df.index,
                        y=trends_df[col],
                        mode='lines+markers',
                        name=col.replace('strongBuy', 'Strong Buy').replace('strongSell', 'Strong Sell').title(),
                        line=dict(color=colors.get(col, 'gray'))
                    ))

            fig.update_layout(
                title=f'Analyst Recommendation Trends for {ticker}',
                xaxis_title='Date',
                yaxis_title='Number of Analysts',
                hovermode='x unified',
                legend_title='Recommendation',
                xaxis_rangeslider_visible=True
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display raw data
            st.subheader("Raw Recommendation Data")
            st.dataframe(recommendations_df_sorted.drop(columns=['fromRatingType', 'toRatingType'], errors='ignore'))
        else:
            st.warning("Date column not found in recommendations data. Cannot display trends.")

if __name__ == "__main__":
    render_page()