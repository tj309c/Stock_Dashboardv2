import streamlit as st
from sentiment_analyzer import get_social_sentiment

def calculate_squeeze_score(info, price_data, include_reddit=True, is_leaderboard=False):
    """
    Calculates the Ultimate Short Squeeze Indicator (USSI) score.
    
    Returns:
        A tuple containing (final_score, dictionary_of_component_scores).
    """
    components = {}
    
    # --- 1. Short Interest Component (40% weight) ---
    short_float = info.get('shortPercentOfFloat', 0) or 0
    # Normalize score: 0 at 0% short float, 1 at 25%+ short float (capped)
    short_interest_score = min(short_float / 0.25, 1.0)
    components['Short Interest %'] = {'value': short_float, 'score': short_interest_score, 'weight': 0.4}

    # --- 2. Volume Pressure Component (30% weight) ---
    df = price_data.copy()
    df['volume_rolling_mean'] = df['Volume'].rolling(window=30).mean()
    df['volume_rolling_std'] = df['Volume'].rolling(window=30).std()
    df['volume_z'] = (df['Volume'] - df['volume_rolling_mean']) / df['volume_rolling_std']
    latest_volume_z = df['volume_z'].iloc[-1]
    # Normalize score: 0 at z-score of 0, 1 at z-score of 3+ (capped)
    volume_z_score = min(abs(latest_volume_z) / 3.0, 1.0) if not df.empty else 0.0
    components['Volume Z-Score'] = {'value': latest_volume_z, 'score': volume_z_score, 'weight': 0.3}

    # --- 3. Reddit Buzz Component (20% weight) ---
    if include_reddit:
        ticker = info.get('symbol', '')
        company_name = info.get('shortName', ticker)
        # Only show spinner on the single-ticker page, not for every ticker in the leaderboard
        if not is_leaderboard:
            with st.spinner(f"Scraping social sentiment for '{ticker}'..."):
                sentiment_data = get_social_sentiment(ticker, company_name)
        else:
            sentiment_data = get_social_sentiment(ticker, company_name)
        # The buzz index is already 0-100, so we normalize it to 0-1 for scoring
        buzz_score = sentiment_data.get('social_buzz_index', 0) / 100.0 if sentiment_data else 0
        mention_count = sentiment_data.get('mention_volume', 0)
        
        components['Social Buzz'] = {'value': f"{mention_count} mentions", 'score': buzz_score, 'weight': 0.2, 'raw_data': sentiment_data, 'display_name': 'Social Buzz'}
    else:
        # If social sentiment is disabled, set its score and weight to 0
        components['Social Buzz'] = {'value': 'Disabled', 'score': 0, 'weight': 0, 'raw_data': None, 'display_name': 'Social Buzz'}

    # --- 4. RSI Trend Component (10% weight) ---
    latest_rsi = price_data['RSI_14'].iloc[-1] if not price_data.empty else 50
    rsi_trend = price_data['RSI_14'].diff(periods=3).iloc[-1] if not price_data.empty and len(price_data) > 3 else 0 # 3-day change in RSI
    # FIX: Reward upward momentum, but not when extremely overbought. This prevents
    # rewarding a stock that is already at RSI 95 and still rising, which is risky.
    # Score is 1 if RSI is between 50-85 (strong but not extreme) and trending up.
    is_trending_up = latest_rsi > 50 and rsi_trend > 0
    is_not_extreme = latest_rsi < 85 # Don't reward momentum into extreme overbought territory
    rsi_trend_score = 1.0 if is_trending_up and is_not_extreme else 0.0
    components['RSI Trend'] = {'value': f"{latest_rsi:.1f} (Trend: {rsi_trend:.1f})", 'score': rsi_trend_score, 'weight': 0.1}

    # --- Final Score Calculation ---
    total_score = 0
    total_weight = 0
    
    for comp in components.values():
        total_score += comp['score'] * comp['weight']
        total_weight += comp['weight']
        
    # Re-normalize the final score based on the actual weights used
    # (This is important in case Reddit is disabled)
    if total_weight > 0:
        final_score = (total_score / total_weight) * 100
    else:
        final_score = 0
        
    return final_score, components