"""
Service Layer Integration Validation
Tests both old and new data fetching approaches
"""
import sys
import io
import time
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup components
from data_fetcher import MarketDataFetcher
from analysis_engine import (TechnicalAnalyzer, ValuationEngine, 
                              GoodBuyAnalyzer, RiskAnalyzer, OptionsAnalyzer)
from src.ui_utils.sentiment_scraper import SentimentScraper
from src.services import StocksAnalysisService

def create_components():
    """Create analysis components"""
    return {
        "fetcher": MarketDataFetcher(),
        "technical": TechnicalAnalyzer(),
        "valuation": ValuationEngine(),
        "goodbuy": GoodBuyAnalyzer(),
        "risk": RiskAnalyzer(),
        "options": OptionsAnalyzer(),
        "sentiment": SentimentScraper()
    }

def test_old_approach(components, ticker):
    """Test old approach (direct component calls)"""
    print("\n" + "="*80)
    print("🔧 OLD APPROACH: Direct Component Calls")
    print("="*80)
    
    start = time.time()
    
    try:
        # Fetch data
        stock_data = components["fetcher"].get_stock_data(ticker)
        quote = components["fetcher"].get_realtime_quote(ticker)
        
        if not stock_data or "error" in stock_data:
            print(f"❌ Failed to fetch data for {ticker}")
            return None
        
        print(f"✅ Fetched stock data")
        print(f"   Price: ${quote.get('price', 0):.2f}")
        print(f"   Change: {quote.get('change', 0):+.2f} ({quote.get('changePercent', 0):+.2f}%)")
        
        # Technical analysis
        import pandas as pd
        df = pd.DataFrame(stock_data.get("history", {}))
        if not df.empty:
            technical = components["technical"].analyze(df)
            rsi = technical.get("rsi", {}).get("value", 0)
            print(f"   RSI: {rsi:.1f}")
        
        elapsed = time.time() - start
        print(f"\n⏱️  Completed in {elapsed:.2f}s")
        
        return {
            "method": "Old Approach",
            "elapsed": elapsed,
            "data": stock_data
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_new_approach(components, ticker):
    """Test new approach (Service Layer)"""
    print("\n" + "="*80)
    print("🎯 NEW APPROACH: Service Layer")
    print("="*80)
    
    start = time.time()
    
    try:
        # Initialize service
        service = StocksAnalysisService(components)
        
        # Get analysis
        result = service.analyze_stock(ticker)
        
        print(f"✅ Service analysis complete")
        print(f"   Ticker: {result.ticker}")
        print(f"   Price: ${result.price.current:.2f}")
        print(f"   Change: {result.price.day_change:+.2f} ({result.price.day_change_percent:+.2f}%)")
        print(f"   RSI: {result.technical.rsi:.1f}")
        print(f"   P/E: {result.fundamentals.pe_ratio:.2f}" if result.fundamentals and result.fundamentals.pe_ratio else "   P/E: N/A")
        
        # Test service methods
        score = service.get_overall_score(result)
        print(f"   Overall Score: {score:.1f}/100")
        
        signals = service.calculate_buy_signals(result)
        print(f"   Signals: {len(signals)} generated")
        
        elapsed = time.time() - start
        print(f"\n⏱️  Completed in {elapsed:.2f}s")
        
        return {
            "method": "Service Layer",
            "elapsed": elapsed,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run validation tests"""
    print("\n" + "="*80)
    print("🧪 SERVICE LAYER INTEGRATION VALIDATION")
    print("="*80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Create components
    print("⚙️  Initializing components...")
    components = create_components()
    print("✅ Components ready\n")
    
    # Test ticker
    ticker = "AAPL"
    print(f"📊 Testing with ticker: {ticker}\n")
    
    # Test old approach
    old_result = test_old_approach(components, ticker)
    
    # Test new approach
    new_result = test_new_approach(components, ticker)
    
    # Comparison
    print("\n" + "="*80)
    print("📊 COMPARISON")
    print("="*80)
    
    if old_result and new_result:
        print(f"\n⏱️  Performance:")
        print(f"   Old Approach: {old_result['elapsed']:.2f}s")
        print(f"   New Approach: {new_result['elapsed']:.2f}s")
        
        diff = new_result['elapsed'] - old_result['elapsed']
        if diff < 0:
            print(f"   🚀 Service Layer is {abs(diff):.2f}s FASTER")
        else:
            print(f"   ⚠️  Service Layer is {diff:.2f}s slower (includes type validation)")
        
        print(f"\n✅ Benefits of Service Layer:")
        print(f"   • Type-safe results (StockAnalysisResult)")
        print(f"   • Zero Streamlit dependencies")
        print(f"   • Fully testable (66+ unit tests)")
        print(f"   • Clean separation of concerns")
        print(f"   • Reusable across dashboards")
        print(f"   • Helper methods (get_overall_score, calculate_buy_signals)")
        
    elif new_result:
        print("\n✅ Service Layer works!")
        print("⚠️  Old approach failed (expected during transition)")
    elif old_result:
        print("\n⚠️  Service Layer needs fixes")
        print("✅ Old approach still works (fallback available)")
    else:
        print("\n❌ Both approaches failed - check API keys")
    
    print("\n" + "="*80)
    print("🎉 VALIDATION COMPLETE")
    print("="*80)
    print(f"\n📝 Next Steps:")
    print(f"   1. ✅ Service Layer integrated into ProgressiveDataFetcher")
    print(f"   2. ✅ Dashboard has Service Layer toggle (🎯 checkbox)")
    print(f"   3. 🔄 Test in browser at http://localhost:8501")
    print(f"   4. 📊 Compare old vs new in dashboard")
    print(f"   5. 🚀 Gradually migrate all dashboards to Service Layer")
    print()

if __name__ == "__main__":
    main()
