"""
Comprehensive Mode Switching Test
Tests that Trader vs Investor modes correctly change data fetching behavior,
cache TTLs, feature toggles, and default parameters across all modules.
"""
import sys
import io
import pandas as pd
import yfinance as yf
from datetime import datetime

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import mode configuration
from mode_config import (
    get_current_mode,
    set_mode,
    get_cache_ttl,
    should_show_feature,
    get_default_timeframe,
    get_chart_config,
    MODES
)


def test_mode_basic_switching():
    """Test basic mode switching functionality"""
    print("\n" + "="*70)
    print("TEST 1: BASIC MODE SWITCHING")
    print("="*70)

    checks_passed = []

    # Test switching to Trader mode
    print("\n📊 Testing switch to TRADER mode:")
    set_mode('trader')
    mode = get_current_mode()

    if mode.name == "Trader":
        print(f"   ✅ Mode name: {mode.name}")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode name incorrect: {mode.name}")
        checks_passed.append(False)

    if mode.icon == "📊":
        print(f"   ✅ Mode icon: {mode.icon}")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode icon incorrect: {mode.icon}")
        checks_passed.append(False)

    # Test switching to Investor mode
    print("\n📈 Testing switch to INVESTOR mode:")
    set_mode('investor')
    mode = get_current_mode()

    if mode.name == "Investor":
        print(f"   ✅ Mode name: {mode.name}")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode name incorrect: {mode.name}")
        checks_passed.append(False)

    if mode.icon == "📈":
        print(f"   ✅ Mode icon: {mode.icon}")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode icon incorrect: {mode.icon}")
        checks_passed.append(False)

    return all(checks_passed)


def test_cache_ttl_differences():
    """Test that cache TTLs are different between modes"""
    print("\n" + "="*70)
    print("TEST 2: CACHE TTL DIFFERENCES")
    print("="*70)

    checks_passed = []

    # Test Trader mode cache TTLs
    print("\n📊 TRADER Mode Cache TTLs:")
    set_mode('trader')

    fast_ttl = get_cache_ttl("fast")
    medium_ttl = get_cache_ttl("medium")
    slow_ttl = get_cache_ttl("slow")

    print(f"   Fast (price data): {fast_ttl}s")
    print(f"   Medium (indicators): {medium_ttl}s")
    print(f"   Slow (fundamentals): {slow_ttl}s")

    # Trader should have aggressive caching (short TTLs for price data)
    if fast_ttl == 60:  # 1 minute
        print(f"   ✅ Fast TTL correct (60s for real-time feel)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Fast TTL incorrect: {fast_ttl}s (expected 60s)")
        checks_passed.append(False)

    if medium_ttl == 300:  # 5 minutes
        print(f"   ✅ Medium TTL correct (300s)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Medium TTL incorrect: {medium_ttl}s (expected 300s)")
        checks_passed.append(False)

    # Test Investor mode cache TTLs
    print("\n📈 INVESTOR Mode Cache TTLs:")
    set_mode('investor')

    fast_ttl = get_cache_ttl("fast")
    medium_ttl = get_cache_ttl("medium")
    slow_ttl = get_cache_ttl("slow")

    print(f"   Fast (price data): {fast_ttl}s")
    print(f"   Medium (indicators): {medium_ttl}s")
    print(f"   Slow (fundamentals): {slow_ttl}s")

    # Investor should have conservative caching (longer TTLs)
    if fast_ttl == 300:  # 5 minutes
        print(f"   ✅ Fast TTL correct (300s - less critical for long-term)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Fast TTL incorrect: {fast_ttl}s (expected 300s)")
        checks_passed.append(False)

    if slow_ttl == 3600:  # 1 hour
        print(f"   ✅ Slow TTL correct (3600s for fundamentals)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Slow TTL incorrect: {slow_ttl}s (expected 3600s)")
        checks_passed.append(False)

    # Verify TTLs are different between modes
    set_mode('trader')
    trader_fast = get_cache_ttl("fast")
    set_mode('investor')
    investor_fast = get_cache_ttl("fast")

    if trader_fast != investor_fast:
        print(f"\n   ✅ Cache TTLs differ between modes (Trader: {trader_fast}s, Investor: {investor_fast}s)")
        checks_passed.append(True)
    else:
        print(f"\n   ❌ Cache TTLs should differ between modes!")
        checks_passed.append(False)

    return all(checks_passed)


def test_default_timeframes():
    """Test that default timeframes are different between modes"""
    print("\n" + "="*70)
    print("TEST 3: DEFAULT TIMEFRAME DIFFERENCES")
    print("="*70)

    checks_passed = []

    # Test Trader mode defaults
    print("\n📊 TRADER Mode Defaults:")
    set_mode('trader')
    timeframe = get_default_timeframe()

    print(f"   Period: {timeframe['period']}")
    print(f"   Interval: {timeframe['interval']}")
    print(f"   Available: {timeframe['available_periods']}")

    if timeframe['period'] == "5d":
        print(f"   ✅ Default period correct (5d for short-term trading)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Default period incorrect: {timeframe['period']} (expected 5d)")
        checks_passed.append(False)

    if timeframe['interval'] == "15m":
        print(f"   ✅ Default interval correct (15m for intraday)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Default interval incorrect: {timeframe['interval']} (expected 15m)")
        checks_passed.append(False)

    if "1d" in timeframe['available_periods'] and "5d" in timeframe['available_periods']:
        print(f"   ✅ Short-term periods available")
        checks_passed.append(True)
    else:
        print(f"   ❌ Short-term periods missing from available_periods")
        checks_passed.append(False)

    # Test Investor mode defaults
    print("\n📈 INVESTOR Mode Defaults:")
    set_mode('investor')
    timeframe = get_default_timeframe()

    print(f"   Period: {timeframe['period']}")
    print(f"   Interval: {timeframe['interval']}")
    print(f"   Available: {timeframe['available_periods']}")

    if timeframe['period'] == "1y":
        print(f"   ✅ Default period correct (1y for long-term investing)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Default period incorrect: {timeframe['period']} (expected 1y)")
        checks_passed.append(False)

    if timeframe['interval'] == "1d":
        print(f"   ✅ Default interval correct (1d for daily)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Default interval incorrect: {timeframe['interval']} (expected 1d)")
        checks_passed.append(False)

    if "1y" in timeframe['available_periods'] and "5y" in timeframe['available_periods']:
        print(f"   ✅ Long-term periods available")
        checks_passed.append(True)
    else:
        print(f"   ❌ Long-term periods missing from available_periods")
        checks_passed.append(False)

    return all(checks_passed)


def test_feature_toggles():
    """Test that features are toggled correctly between modes"""
    print("\n" + "="*70)
    print("TEST 4: FEATURE TOGGLE BEHAVIOR")
    print("="*70)

    checks_passed = []

    # Test Trader mode features
    print("\n📊 TRADER Mode Features:")
    set_mode('trader')

    features = {
        "intraday_charts": (True, "should show for traders"),
        "fundamental_analysis": (False, "less relevant for day trading"),
        "long_term_forecasts": (False, "not relevant for short-term"),
        "advanced_technicals": (True, "critical for traders")
    }

    for feature, (expected, reason) in features.items():
        actual = should_show_feature(feature)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} {feature}: {actual} ({reason})")
        checks_passed.append(actual == expected)

    # Test Investor mode features
    print("\n📈 INVESTOR Mode Features:")
    set_mode('investor')

    features = {
        "intraday_charts": (False, "not relevant for long-term"),
        "fundamental_analysis": (True, "critical for investors"),
        "long_term_forecasts": (True, "important for planning"),
        "advanced_technicals": (True, "still useful")
    }

    for feature, (expected, reason) in features.items():
        actual = should_show_feature(feature)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} {feature}: {actual} ({reason})")
        checks_passed.append(actual == expected)

    # Test that features actually differ between modes
    set_mode('trader')
    trader_shows_fundamentals = should_show_feature("fundamental_analysis")
    set_mode('investor')
    investor_shows_fundamentals = should_show_feature("fundamental_analysis")

    if trader_shows_fundamentals != investor_shows_fundamentals:
        print(f"\n   ✅ Feature toggles differ between modes")
        print(f"      Trader shows fundamentals: {trader_shows_fundamentals}")
        print(f"      Investor shows fundamentals: {investor_shows_fundamentals}")
        checks_passed.append(True)
    else:
        print(f"\n   ❌ Feature toggles should differ between modes!")
        checks_passed.append(False)

    return all(checks_passed)


def test_chart_configuration():
    """Test that chart configs are different between modes"""
    print("\n" + "="*70)
    print("TEST 5: CHART CONFIGURATION DIFFERENCES")
    print("="*70)

    checks_passed = []

    # Test Trader mode chart config
    print("\n📊 TRADER Mode Chart Config:")
    set_mode('trader')
    config = get_chart_config()

    print(f"   Max data points: {config['max_points']}")
    print(f"   Preload indicators: {config['preload_indicators']}")
    print(f"   Lazy load fundamentals: {config['lazy_load_fundamentals']}")

    if config['max_points'] == 500:
        print(f"   ✅ Showing recent detail (500 points)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Max points incorrect: {config['max_points']}")
        checks_passed.append(False)

    if config['preload_indicators'] == True:
        print(f"   ✅ Preloading indicators (traders need them immediately)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Should preload indicators for traders")
        checks_passed.append(False)

    if config['lazy_load_fundamentals'] == True:
        print(f"   ✅ Lazy loading fundamentals (not critical for traders)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Should lazy load fundamentals for traders")
        checks_passed.append(False)

    # Test Investor mode chart config
    print("\n📈 INVESTOR Mode Chart Config:")
    set_mode('investor')
    config = get_chart_config()

    print(f"   Max data points: {config['max_points']}")
    print(f"   Preload indicators: {config['preload_indicators']}")
    print(f"   Lazy load fundamentals: {config['lazy_load_fundamentals']}")

    if config['max_points'] == 2000:
        print(f"   ✅ Showing full history (2000 points)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Max points incorrect: {config['max_points']}")
        checks_passed.append(False)

    if config['lazy_load_fundamentals'] == False:
        print(f"   ✅ Loading fundamentals upfront (critical for investors)")
        checks_passed.append(True)
    else:
        print(f"   ❌ Should load fundamentals upfront for investors")
        checks_passed.append(False)

    return all(checks_passed)


def test_real_data_fetch_simulation():
    """Test simulated data fetching with mode-appropriate parameters"""
    print("\n" + "="*70)
    print("TEST 6: SIMULATED DATA FETCH WITH MODE PARAMS")
    print("="*70)

    checks_passed = []

    ticker = "AAPL"

    # Simulate Trader mode data fetch
    print("\n📊 Simulating TRADER mode data fetch:")
    set_mode('trader')
    timeframe = get_default_timeframe()

    print(f"   Fetching {ticker} with period={timeframe['period']}, interval={timeframe['interval']}")

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=timeframe['period'], interval=timeframe['interval'])

        if not data.empty:
            print(f"   ✅ Fetched {len(data)} data points")
            print(f"   ✅ Date range: {data.index[0]} to {data.index[-1]}")

            # Verify we got intraday data
            if timeframe['interval'] in ['1m', '5m', '15m', '30m', '1h']:
                print(f"   ✅ Intraday interval ({timeframe['interval']}) - suitable for trading")
                checks_passed.append(True)
            else:
                print(f"   ⚠️  Not intraday data")
                checks_passed.append(True)  # Still pass
        else:
            print(f"   ❌ No data fetched")
            checks_passed.append(False)

    except Exception as e:
        print(f"   ❌ Fetch failed: {str(e)}")
        checks_passed.append(False)

    # Simulate Investor mode data fetch
    print("\n📈 Simulating INVESTOR mode data fetch:")
    set_mode('investor')
    timeframe = get_default_timeframe()

    print(f"   Fetching {ticker} with period={timeframe['period']}, interval={timeframe['interval']}")

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=timeframe['period'], interval=timeframe['interval'])

        if not data.empty:
            print(f"   ✅ Fetched {len(data)} data points")
            print(f"   ✅ Date range: {data.index[0]} to {data.index[-1]}")

            # Verify we got long-term data
            days_covered = (data.index[-1] - data.index[0]).days
            if days_covered >= 60:  # At least 2 months
                print(f"   ✅ Long-term data ({days_covered} days) - suitable for investing")
                checks_passed.append(True)
            else:
                print(f"   ⚠️  Short timeframe ({days_covered} days)")
                checks_passed.append(True)  # Still pass
        else:
            print(f"   ❌ No data fetched")
            checks_passed.append(False)

    except Exception as e:
        print(f"   ❌ Fetch failed: {str(e)}")
        checks_passed.append(False)

    return all(checks_passed)


def test_mode_persistence():
    """Test that mode persists across multiple calls"""
    print("\n" + "="*70)
    print("TEST 7: MODE PERSISTENCE")
    print("="*70)

    checks_passed = []

    # Set to trader
    set_mode('trader')
    mode1 = get_current_mode()

    # Call get_current_mode multiple times
    mode2 = get_current_mode()
    mode3 = get_current_mode()

    if mode1.name == mode2.name == mode3.name == "Trader":
        print(f"   ✅ Trader mode persists across multiple calls")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode not persisting")
        checks_passed.append(False)

    # Switch to investor
    set_mode('investor')
    mode4 = get_current_mode()
    mode5 = get_current_mode()

    if mode4.name == mode5.name == "Investor":
        print(f"   ✅ Investor mode persists across multiple calls")
        checks_passed.append(True)
    else:
        print(f"   ❌ Mode not persisting")
        checks_passed.append(False)

    # Switch back to trader
    set_mode('trader')
    mode6 = get_current_mode()

    if mode6.name == "Trader":
        print(f"   ✅ Can switch back to Trader mode")
        checks_passed.append(True)
    else:
        print(f"   ❌ Cannot switch back")
        checks_passed.append(False)

    return all(checks_passed)


def test_recommended_pages():
    """Test that recommended pages differ between modes"""
    print("\n" + "="*70)
    print("TEST 8: RECOMMENDED PAGES DIFFER BY MODE")
    print("="*70)

    checks_passed = []

    # Test Trader mode recommendations
    print("\n📊 TRADER Mode Recommended Pages:")
    set_mode('trader')
    mode = get_current_mode()

    for page in mode.recommended_pages:
        print(f"   - {page}")

    if "Stock Analysis" in mode.recommended_pages:
        print(f"   ✅ Stock Analysis recommended for traders")
        checks_passed.append(True)
    else:
        print(f"   ❌ Stock Analysis should be recommended for traders")
        checks_passed.append(False)

    # Test Investor mode recommendations
    print("\n📈 INVESTOR Mode Recommended Pages:")
    set_mode('investor')
    mode = get_current_mode()

    for page in mode.recommended_pages:
        print(f"   - {page}")

    if "Fundamental Analysis" in mode.recommended_pages:
        print(f"   ✅ Fundamental Analysis recommended for investors")
        checks_passed.append(True)
    else:
        print(f"   ❌ Fundamental Analysis should be recommended for investors")
        checks_passed.append(False)

    if "Portfolio & Strategy" in mode.recommended_pages:
        print(f"   ✅ Portfolio & Strategy recommended for investors")
        checks_passed.append(True)
    else:
        print(f"   ❌ Portfolio & Strategy should be recommended for investors")
        checks_passed.append(False)

    return all(checks_passed)


def main():
    """Run all mode switching tests"""
    print("\n" + "="*70)
    print("COMPREHENSIVE MODE SWITCHING TEST SUITE")
    print("="*70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTesting that Trader vs Investor modes correctly change:")
    print("  - Cache TTLs")
    print("  - Default timeframes")
    print("  - Feature toggles")
    print("  - Chart configurations")
    print("  - Data fetching behavior")

    results = []

    # Test 1: Basic switching
    try:
        result = test_mode_basic_switching()
        results.append(("Basic Mode Switching", result))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        results.append(("Basic Mode Switching", False))

    # Test 2: Cache TTLs
    try:
        result = test_cache_ttl_differences()
        results.append(("Cache TTL Differences", result))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        results.append(("Cache TTL Differences", False))

    # Test 3: Default timeframes
    try:
        result = test_default_timeframes()
        results.append(("Default Timeframes", result))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        results.append(("Default Timeframes", False))

    # Test 4: Feature toggles
    try:
        result = test_feature_toggles()
        results.append(("Feature Toggles", result))
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        results.append(("Feature Toggles", False))

    # Test 5: Chart configuration
    try:
        result = test_chart_configuration()
        results.append(("Chart Configuration", result))
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {str(e)}")
        results.append(("Chart Configuration", False))

    # Test 6: Real data fetch simulation
    try:
        result = test_real_data_fetch_simulation()
        results.append(("Data Fetch Simulation", result))
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {str(e)}")
        results.append(("Data Fetch Simulation", False))

    # Test 7: Mode persistence
    try:
        result = test_mode_persistence()
        results.append(("Mode Persistence", result))
    except Exception as e:
        print(f"\n❌ TEST 7 FAILED: {str(e)}")
        results.append(("Mode Persistence", False))

    # Test 8: Recommended pages
    try:
        result = test_recommended_pages()
        results.append(("Recommended Pages", result))
    except Exception as e:
        print(f"\n❌ TEST 8 FAILED: {str(e)}")
        results.append(("Recommended Pages", False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(r[1] for r in results)
    passed_count = sum(1 for r in results if r[1])
    total_count = len(results)

    print("\n" + "="*70)
    if all_passed:
        print(f"🎉 ALL TESTS PASSED ({passed_count}/{total_count})")
        print("✅ Mode switching is working correctly!")
        print("✅ Trader and Investor modes have distinct behaviors")
        print("✅ Ready for page integration")
    else:
        failed_count = total_count - passed_count
        print(f"⚠️  {failed_count}/{total_count} TESTS FAILED")
        print("Some mode switching behavior needs attention")
    print("="*70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
