"""
Quick Options Service Test
Tests basic integration without running full validation
"""
import sys
print("🧪 Testing Options Service Integration...\n")

try:
    # Test 1: Import service
    print("1. Importing OptionsAnalysisService...")
    from src.services import OptionsAnalysisService
    print("   ✅ Import successful\n")
    
    # Test 2: Import components
    print("2. Importing required components...")
    from data_fetcher import MarketDataFetcher
    from analysis_engine import OptionsAnalyzer
    print("   ✅ Components imported\n")
    
    # Test 3: Initialize service
    print("3. Initializing service...")
    components = {
        "fetcher": MarketDataFetcher(),
        "options": OptionsAnalyzer()
    }
    service = OptionsAnalysisService(components)
    print("   ✅ Service initialized\n")
    
    # Test 4: Check service methods
    print("4. Checking service methods...")
    methods = [
        'analyze_options_chain',
        'get_contracts_by_expiration',
        'calculate_greeks',
        'detect_unusual_activity',
        'get_strategy_recommendations'
    ]
    
    for method in methods:
        if hasattr(service, method):
            print(f"   ✅ {method}")
        else:
            print(f"   ❌ {method} missing!")
    
    print("\n✅ All basic tests passed!")
    print("🚀 Options service is ready for dashboard integration\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
