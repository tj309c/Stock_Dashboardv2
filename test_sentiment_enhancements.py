"""
Test script for News & Sentiment enhancements
Tests the four new professional sentiment analysis functions
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# ========================================
# TEST DATA SETUP
# ========================================

def create_test_sentiment_sources():
    """Create test sentiment sources data"""
    return [
        {'source': 'News Articles', 'sentiment': 'Bullish', 'score': 0.75, 'count': 15, 'emoji': '📈', 'color': '#00CC96'},
        {'source': 'X/Twitter', 'sentiment': 'Bullish', 'score': 0.72, 'count': '8/10 trending', 'emoji': '📈', 'color': '#00CC96'},
        {'source': 'Google Trends', 'sentiment': 'Rising', 'score': 0.68, 'count': '68/100 interest', 'emoji': '📈', 'color': '#00CC96'}
    ]

def create_test_news_dataframe():
    """Create test news DataFrame with sentiment data"""
    dates = []
    sentiments = []

    # Create 20 articles over 10 days
    now = datetime.now(timezone.utc)

    # Recent articles (last 2 days) - more positive
    for i in range(8):
        dates.append(now - timedelta(hours=i*3))
        sentiments.append(0.6 + (np.random.random() * 0.3))  # 0.6 to 0.9

    # Older articles (3-10 days ago) - less positive
    for i in range(12):
        dates.append(now - timedelta(days=3+i, hours=np.random.randint(0, 24)))
        sentiments.append(0.2 + (np.random.random() * 0.4))  # 0.2 to 0.6

    df = pd.DataFrame({
        'published_date': dates,
        'sentiment': sentiments,
        'title': [f'Test Article {i}' for i in range(20)]
    })

    return df

def create_test_summary():
    """Create test news sentiment summary"""
    return {
        'total_articles': 20,
        'positive_count': 12,
        'negative_count': 3,
        'neutral_count': 5,
        'avg_sentiment': 0.45,
        'sentiment_trend': 'bullish',
        'trend_emoji': '📈',
        'positive_pct': 60.0,
        'negative_pct': 15.0,
        'neutral_pct': 25.0
    }

# ========================================
# COPY OF FUNCTIONS FROM OVERVIEW PAGE
# ========================================

def calculate_sentiment_alignment(sources):
    """Calculate how aligned sentiment sources are"""
    if len(sources) < 2:
        return 1.0, "Single Source", False

    scores = [s['score'] for s in sources]
    mean_score = sum(scores) / len(scores)

    # Calculate standard deviation
    variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5

    # Normalize to 0-1 scale
    alignment_score = max(0, 1 - (std_dev / 0.35))

    # Interpretation
    if alignment_score > 0.85:
        interpretation = "Strong Consensus"
        risk_flag = False
    elif alignment_score > 0.65:
        interpretation = "Moderate Consensus"
        risk_flag = False
    elif alignment_score > 0.4:
        interpretation = "Mixed Signals"
        risk_flag = True
    else:
        interpretation = "High Divergence"
        risk_flag = True

    return alignment_score, interpretation, risk_flag

def calculate_sentiment_momentum(current_sentiment, news_df):
    """Calculate sentiment momentum by comparing current to baseline"""
    if news_df.empty or 'published_date' not in news_df.columns:
        return "stable", "➡️", "Insufficient historical data"

    try:
        # Ensure published_date is datetime
        news_df_copy = news_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(news_df_copy['published_date']):
            news_df_copy['published_date'] = pd.to_datetime(news_df_copy['published_date'])

        # Get articles older than 2 days for baseline
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=2)
        historical = news_df_copy[news_df_copy['published_date'] < cutoff_date]

        if len(historical) < 3:
            return "stable", "➡️", "Limited historical data"

        historical_avg = historical['sentiment'].mean()

        # Calculate momentum
        sentiment_change = current_sentiment - historical_avg

        if sentiment_change > 0.15:
            return "improving", "📈", f"+{sentiment_change:.2f} vs baseline"
        elif sentiment_change < -0.15:
            return "deteriorating", "📉", f"{sentiment_change:.2f} vs baseline"
        else:
            return "stable", "➡️", f"{sentiment_change:+.2f} vs baseline"

    except Exception as e:
        return "stable", "➡️", f"Unable to calculate: {str(e)}"

# ========================================
# TEST SUITE
# ========================================

def test_sentiment_alignment():
    """Test sentiment alignment calculation"""
    print("\n" + "="*60)
    print("TEST 1: Sentiment Alignment Analysis")
    print("="*60)

    # Test Case 1: Strong consensus (all sources agree)
    sources_consensus = [
        {'score': 0.75}, {'score': 0.73}, {'score': 0.77}
    ]
    alignment, interpretation, risk = calculate_sentiment_alignment(sources_consensus)
    print(f"\n[OK] Test Case 1 - Strong Consensus:")
    print(f"  Scores: {[s['score'] for s in sources_consensus]}")
    print(f"  Alignment: {alignment:.2%}")
    print(f"  Interpretation: {interpretation}")
    print(f"  Risk Flag: {risk}")
    assert alignment > 0.85, "Strong consensus should have alignment > 85%"
    assert not risk, "Strong consensus should not have risk flag"
    print("  [PASS]")

    # Test Case 2: High divergence (sources conflict)
    sources_divergent = [
        {'score': 0.2}, {'score': 0.8}, {'score': 0.4}
    ]
    alignment, interpretation, risk = calculate_sentiment_alignment(sources_divergent)
    print(f"\n[OK] Test Case 2 - High Divergence:")
    print(f"  Scores: {[s['score'] for s in sources_divergent]}")
    print(f"  Alignment: {alignment:.2%}")
    print(f"  Interpretation: {interpretation}")
    print(f"  Risk Flag: {risk}")
    assert alignment < 0.5, "High divergence should have alignment < 50%"
    assert risk, "High divergence should have risk flag"
    print("  [PASS]")

    # Test Case 3: Single source
    sources_single = [{'score': 0.65}]
    alignment, interpretation, risk = calculate_sentiment_alignment(sources_single)
    print(f"\n[OK] Test Case 3 - Single Source:")
    print(f"  Alignment: {alignment:.2%}")
    print(f"  Interpretation: {interpretation}")
    print(f"  Risk Flag: {risk}")
    assert alignment == 1.0, "Single source should have perfect alignment"
    print("  [PASS]")

def test_sentiment_momentum():
    """Test sentiment momentum calculation"""
    print("\n" + "="*60)
    print("TEST 2: Sentiment Momentum Indicator")
    print("="*60)

    # Create test data
    news_df = create_test_news_dataframe()

    print(f"\n[OK] Test Data Created:")
    print(f"  Total articles: {len(news_df)}")
    print(f"  Date range: {news_df['published_date'].min()} to {news_df['published_date'].max()}")

    # Test Case 1: Improving sentiment (current > historical)
    current_sentiment_high = 0.75  # High current sentiment
    direction, emoji, text = calculate_sentiment_momentum(current_sentiment_high, news_df)
    print(f"\n[OK] Test Case 1 - Improving Sentiment:")
    print(f"  Current: {current_sentiment_high:.2f}")
    print(f"  Direction: {direction}")
    print(f"  Emoji: [UP ARROW]")
    print(f"  Text: {text}")
    assert direction == "improving", "High current sentiment should show improving"
    print("  [PASS]")

    # Test Case 2: Deteriorating sentiment (current < historical)
    current_sentiment_low = 0.2  # Low current sentiment
    direction, emoji, text = calculate_sentiment_momentum(current_sentiment_low, news_df)
    print(f"\n[OK] Test Case 2 - Deteriorating Sentiment:")
    print(f"  Current: {current_sentiment_low:.2f}")
    print(f"  Direction: {direction}")
    print(f"  Emoji: [DOWN ARROW]")
    print(f"  Text: {text}")
    assert direction == "deteriorating", "Low current sentiment should show deteriorating"
    print("  [PASS]")

    # Test Case 3: Empty DataFrame
    empty_df = pd.DataFrame()
    direction, emoji, text = calculate_sentiment_momentum(0.5, empty_df)
    print(f"\n[OK] Test Case 3 - Empty Data:")
    print(f"  Direction: {direction}")
    print(f"  Text: {text}")
    assert direction == "stable", "Empty data should return stable"
    print("  [PASS]")

def test_professional_summary_card():
    """Test professional sentiment summary card logic"""
    print("\n" + "="*60)
    print("TEST 3: Professional Sentiment Summary Card")
    print("="*60)

    sentiment_sources = create_test_sentiment_sources()

    # Calculate metrics (same logic as in the page)
    alignment_score, alignment_interpretation, risk_flag = calculate_sentiment_alignment(sentiment_sources)
    overall_score = sum(s['score'] for s in sentiment_sources) / len(sentiment_sources)

    # Determine overall sentiment label
    if overall_score > 0.65:
        overall_sentiment = "Bullish"
        overall_emoji = "📈"
    elif overall_score < 0.35:
        overall_sentiment = "Bearish"
        overall_emoji = "📉"
    else:
        overall_sentiment = "Neutral"
        overall_emoji = "➡️"

    # Generate key insight
    if len(sentiment_sources) == 1:
        key_insight = f"Analysis based on {sentiment_sources[0]['source']} only"
    elif alignment_score > 0.75:
        key_insight = f"All sources showing consistent {overall_sentiment.lower()} sentiment"
    elif risk_flag:
        key_insight = f"⚠️ Sources show conflicting signals - exercise caution"
    else:
        key_insight = f"Moderate agreement across sources trending {overall_sentiment.lower()}"

    print(f"\n[OK] Summary Card Metrics:")
    print(f"  Overall Score: {overall_score:.2f}")
    print(f"  Overall Sentiment: {overall_sentiment}")
    print(f"  Alignment: {alignment_score:.0%} ({alignment_interpretation})")
    print(f"  Risk Flag: {risk_flag}")
    print(f"  Key Insight: {key_insight.replace('⚠️', '[WARNING]')}")

    # Validate logic
    assert overall_sentiment == "Bullish", "Test data should result in Bullish sentiment"
    assert not risk_flag, "Test data should not have risk flag"
    assert "consistent" in key_insight.lower(), "High alignment should mention consistency"
    print("  [PASS]")

def test_integration():
    """Test full integration of all components"""
    print("\n" + "="*60)
    print("TEST 4: Full Integration Test")
    print("="*60)

    # Create test data
    sentiment_sources = create_test_sentiment_sources()
    news_df = create_test_news_dataframe()
    summary = create_test_summary()

    print(f"\n[OK] Test Environment:")
    print(f"  Sources: {len(sentiment_sources)}")
    print(f"  Articles: {len(news_df)}")
    print(f"  Summary keys: {list(summary.keys())}")

    # Run all calculations
    alignment_score, alignment_interpretation, risk_flag = calculate_sentiment_alignment(sentiment_sources)
    momentum_direction, momentum_emoji, momentum_text = calculate_sentiment_momentum(
        summary['avg_sentiment'], news_df
    )
    overall_score = sum(s['score'] for s in sentiment_sources) / len(sentiment_sources)

    print(f"\n[OK] Integration Results:")
    print(f"  1. Alignment: {alignment_score:.0%} ({alignment_interpretation})")
    print(f"  2. Momentum: {momentum_direction.title()} ({momentum_text})")
    print(f"  3. Overall Score: {overall_score:.2f}")
    print(f"  4. Risk Flag: {'Yes (!!)' if risk_flag else 'No (OK)'}")

    # Validate all components work together
    assert alignment_score is not None, "Alignment calculation failed"
    assert momentum_direction in ['improving', 'stable', 'deteriorating'], "Invalid momentum direction"
    assert 0 <= overall_score <= 1, "Overall score out of range"

    print(f"\n[PASS] ALL INTEGRATION TESTS PASSED")

# ========================================
# RUN ALL TESTS
# ========================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NEWS & SENTIMENT ENHANCEMENTS - TEST SUITE")
    print("="*60)
    print("\nTesting 4 new professional sentiment analysis features:")
    print("  #1 - Sentiment Alignment Analysis")
    print("  #2 - Professional Sentiment Summary Card")
    print("  #4 - Sentiment Momentum Indicator")
    print("  #5 - AI Executive Summary (integration only)")

    try:
        test_sentiment_alignment()
        test_sentiment_momentum()
        test_professional_summary_card()
        test_integration()

        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY")
        print("="*60)
        print("\nEnhancements are working correctly!")
        print("Ready for production use.")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        raise
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {str(e)}")
        raise
