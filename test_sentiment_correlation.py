"""
Quick Test: Sentiment-Market Correlation Analyzer

Tests the correlation analyzer with sample data.
"""

print("\n" + "=" * 70)
print("SENTIMENT-MARKET CORRELATION ANALYZER TEST")
print("=" * 70 + "\n")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.analysis.sentiment_market_correlation import get_sentiment_correlation_analyzer

# Initialize analyzer
analyzer = get_sentiment_correlation_analyzer()
print("✅ Analyzer initialized\n")

# Test 1: Calculate sentiment score from sample data
print("Test 1: Sentiment Score Calculation")
print("-" * 70)

sample_sentiment = pd.DataFrame({
    'sentiment': ['positive'] * 60 + ['negative'] * 20 + ['neutral'] * 20,
    'polarity': [0.3] * 60 + [-0.2] * 20 + [0.0] * 20,
    'source': ['Reddit'] * 50 + ['News'] * 50
})

sentiment_metrics = analyzer.calculate_sentiment_score(sample_sentiment)

print(f"✅ Sentiment Metrics Calculated:")
print(f"   • Sentiment Score: {sentiment_metrics['sentiment_score']:+.1f}")
print(f"   • Positive %: {sentiment_metrics['positive_pct']:.1f}%")
print(f"   • Negative %: {sentiment_metrics['negative_pct']:.1f}%")
print(f"   • Neutral %: {sentiment_metrics['neutral_pct']:.1f}%")
print(f"   • Volume: {sentiment_metrics['volume']}")
print(f"   • Avg Polarity: {sentiment_metrics['avg_polarity']:.3f}")
print(f"   • Data Quality: {sentiment_metrics['data_quality']}")

# Test 2: Get market sentiment
print("\nTest 2: Market Sentiment Fetching")
print("-" * 70)

try:
    market_df = analyzer.get_market_sentiment(days=7)
    
    if len(market_df) > 0:
        print(f"✅ Market Data Retrieved:")
        print(f"   • Days of data: {len(market_df)}")
        print(f"   • Current SPY close: ${market_df['spy_close'].iloc[-1]:.2f}")
        print(f"   • Latest return: {market_df['spy_returns'].iloc[-1]*100:+.2f}%")
        print(f"   • Market regime: {market_df['market_regime'].iloc[-1]}")
        print(f"   • Volatility: {market_df['spy_volatility'].iloc[-1]*100:.2f}%")
    else:
        print("⚠️  No market data available (may need internet connection)")
except Exception as e:
    print(f"⚠️  Market data fetch failed: {e}")

# Test 3: Calculate price momentum
print("\nTest 3: Price Momentum Analysis")
print("-" * 70)

try:
    momentum = analyzer.calculate_price_momentum('AAPL', days=30)
    
    if 'error' not in momentum:
        print(f"✅ Momentum Calculated for AAPL:")
        print(f"   • Total Return (30d): {momentum['total_return']:+.2f}%")
        print(f"   • Avg Daily Return: {momentum['avg_daily_return']:+.2f}%")
        print(f"   • Volatility: {momentum['volatility']:.2f}%")
        print(f"   • Trend: {momentum['trend']}")
        print(f"   • Volume Surge: {momentum['volume_surge']:+.1f}%")
        print(f"   • Current Price: ${momentum['current_price']:.2f}")
    else:
        print(f"⚠️  Momentum calculation error: {momentum['error']}")
except Exception as e:
    print(f"⚠️  Momentum test failed: {e}")

# Test 4: Correlation analysis (with mock data)
print("\nTest 4: Sentiment-Price Correlation")
print("-" * 70)

# Create mock sentiment data with dates
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
mock_sentiment_df = pd.DataFrame({
    'date': dates,
    'sentiment': np.random.choice(['positive', 'negative', 'neutral'], 30, p=[0.6, 0.2, 0.2]),
    'polarity': np.random.randn(30) * 0.3 + 0.2,  # Mostly positive
    'source': ['Reddit'] * 30
})

try:
    correlation = analyzer.correlate_sentiment_to_price('AAPL', mock_sentiment_df, lookback_days=30)
    
    if 'error' not in correlation:
        print(f"✅ Correlation Analysis Complete:")
        print(f"   • Best Correlation: {correlation['best_correlation']:.3f}")
        print(f"   • Predictive Power: {correlation['predictive_power']}")
        print(f"   • Reliability: {correlation['reliability']}")
        print(f"   • Sample Size: {correlation['sample_size']}")
        
        if 'correlations' in correlation:
            print(f"\n   By Period:")
            for period, corr in correlation['correlations'].items():
                p_val = correlation['p_values'].get(period, 1.0)
                sig = "✅" if p_val < 0.05 else "❌"
                print(f"   • {period}: {corr:+.3f} (p={p_val:.3f}) {sig}")
    else:
        print(f"⚠️  Correlation analysis error: {correlation['error']}")
except Exception as e:
    print(f"⚠️  Correlation test failed: {e}")

# Test 5: Sentiment beta analysis
print("\nTest 5: Sentiment Beta Analysis")
print("-" * 70)

if len(market_df) > 0:
    try:
        sentiment_beta = analyzer.get_sentiment_market_beta('AAPL', sample_sentiment, market_df)
        
        if 'error' not in sentiment_beta:
            print(f"✅ Sentiment Beta Calculated:")
            print(f"   • Beta Type: {sentiment_beta['beta_type']}")
            print(f"   • Market Regime: {sentiment_beta['market_regime']}")
            print(f"   • Stock Sentiment: {sentiment_beta['stock_sentiment']:+.1f}")
            print(f"   • Interpretation: {sentiment_beta['interpretation']}")
        else:
            print(f"⚠️  Beta calculation error: {sentiment_beta['error']}")
    except Exception as e:
        print(f"⚠️  Beta test failed: {e}")

# Test 6: Comprehensive report generation
print("\nTest 6: Comprehensive Report Generation")
print("-" * 70)

try:
    report = analyzer.generate_comprehensive_report('AAPL', mock_sentiment_df)
    
    print(f"✅ Comprehensive Report Generated:")
    print(f"   • Ticker: {report['ticker']}")
    print(f"   • Data Sources: {', '.join(report['data_sources'])}")
    
    # Sentiment metrics
    sentiment = report.get('sentiment_metrics', {})
    print(f"\n   Sentiment:")
    print(f"   • Score: {sentiment.get('sentiment_score', 0):+.1f}")
    print(f"   • Quality: {sentiment.get('data_quality', 'unknown')}")
    
    # Trading signal
    signal = report.get('trading_signal', {})
    print(f"\n   Trading Signal:")
    print(f"   • Direction: {signal.get('direction', 'UNKNOWN')}")
    print(f"   • Strength: {signal.get('strength', 0):.1f}/100")
    print(f"   • Confidence: {signal.get('confidence', 'UNKNOWN')}")
    print(f"   • Rationale: {signal.get('rationale', 'N/A')}")
    
    # Risk factors
    risks = signal.get('risk_factors', [])
    if risks:
        print(f"\n   Risk Factors:")
        for risk in risks[:3]:  # Show first 3
            print(f"   {risk}")

except Exception as e:
    print(f"⚠️  Report generation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ SENTIMENT-MARKET CORRELATION ANALYZER TEST COMPLETE")
print("=" * 70)
print("\n💡 Next Steps:")
print("   1. Add correlation tab to dashboard_stocks.py")
print("   2. Test with real sentiment data from Stock_Scrapper")
print("   3. Compare predictions to actual price moves")
print("   4. Adjust thresholds based on stock characteristics")
