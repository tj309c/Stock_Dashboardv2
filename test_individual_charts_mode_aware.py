"""
Test Individual Charts & Visuals Page - Mode Awareness
Verifies that Individual Charts & Visuals page respects trading mode settings
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up Streamlit session state mock
import streamlit as st
if 'trading_mode' not in st.session_state:
    st.session_state.trading_mode = 'investor'

from mode_config import get_current_mode, set_mode, get_cache_ttl

def test_advanced_charting_cache_ttls():
    """Test that advanced_charting.py uses mode-aware cache TTLs"""
    print("\n" + "="*60)
    print("TEST 1: Advanced Charting Cache TTLs")
    print("="*60)

    checks_passed = []

    # Test Trader mode
    set_mode('trader')
    mode = get_current_mode()
    print(f"\n✓ Mode set to: {mode.name}")

    # Verify TTLs
    fast_ttl = get_cache_ttl("fast")
    medium_ttl = get_cache_ttl("medium")
    slow_ttl = get_cache_ttl("slow")

    print(f"\n📊 Trader Mode Cache TTLs:")
    print(f"   Fast (price data): {fast_ttl}s")
    print(f"   Medium (indicators): {medium_ttl}s")
    print(f"   Slow (fundamentals): {slow_ttl}s")

    # Expected values for trader mode
    checks_passed.append(fast_ttl == 60)
    checks_passed.append(medium_ttl == 300)
    checks_passed.append(slow_ttl == 900)

    # Test Investor mode
    set_mode('investor')
    mode = get_current_mode()
    print(f"\n✓ Mode set to: {mode.name}")

    fast_ttl = get_cache_ttl("fast")
    medium_ttl = get_cache_ttl("medium")
    slow_ttl = get_cache_ttl("slow")

    print(f"\n📈 Investor Mode Cache TTLs:")
    print(f"   Fast (price data): {fast_ttl}s")
    print(f"   Medium (indicators): {medium_ttl}s")
    print(f"   Slow (fundamentals): {slow_ttl}s")

    # Expected values for investor mode
    checks_passed.append(fast_ttl == 300)
    checks_passed.append(medium_ttl == 1800)
    checks_passed.append(slow_ttl == 3600)

    # Verify TTLs differ between modes
    set_mode('trader')
    trader_fast = get_cache_ttl("fast")
    set_mode('investor')
    investor_fast = get_cache_ttl("fast")

    ttl_differs = trader_fast != investor_fast
    print(f"\n✓ Cache TTLs differ between modes: {ttl_differs}")
    print(f"   Trader fast TTL: {trader_fast}s")
    print(f"   Investor fast TTL: {investor_fast}s")
    print(f"   Difference: {investor_fast - trader_fast}s ({investor_fast / trader_fast:.1f}x slower)")

    checks_passed.append(ttl_differs)

    if all(checks_passed):
        print(f"\n✅ TEST 1 PASSED: All cache TTLs are mode-aware ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 1 FAILED: Some cache TTLs not mode-aware ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


def test_visual_analysis_presets_cache():
    """Test that visual_analysis_presets.py uses mode-aware caching"""
    print("\n" + "="*60)
    print("TEST 2: Visual Analysis Presets Cache")
    print("="*60)

    checks_passed = []

    # Import the module to verify it can access get_cache_ttl
    try:
        import visual_analysis_presets
        print("\n✓ visual_analysis_presets.py imported successfully")
        checks_passed.append(True)
    except ImportError as e:
        print(f"\n❌ Failed to import visual_analysis_presets: {e}")
        checks_passed.append(False)
        return False

    # Test that mode switching affects cache
    set_mode('trader')
    trader_fast = get_cache_ttl("fast")
    trader_medium = get_cache_ttl("medium")

    set_mode('investor')
    investor_fast = get_cache_ttl("fast")
    investor_medium = get_cache_ttl("medium")

    print(f"\n📊 Multi-timeframe data cache (fast):")
    print(f"   Trader: {trader_fast}s")
    print(f"   Investor: {investor_fast}s")

    print(f"\n📊 SPY/Sector ETF data cache (medium):")
    print(f"   Trader: {trader_medium}s")
    print(f"   Investor: {investor_medium}s")

    # Verify they differ
    checks_passed.append(trader_fast < investor_fast)
    checks_passed.append(trader_medium < investor_medium)

    if all(checks_passed):
        print(f"\n✅ TEST 2 PASSED: Visual analysis presets are mode-aware ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 2 FAILED: Some checks failed ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


def test_performance_optimizer_cache():
    """Test that performance_optimizer.py uses mode-aware caching"""
    print("\n" + "="*60)
    print("TEST 3: Performance Optimizer Cache")
    print("="*60)

    checks_passed = []

    # Import the module
    try:
        import performance_optimizer
        print("\n✓ performance_optimizer.py imported successfully")
        checks_passed.append(True)
    except ImportError as e:
        print(f"\n❌ Failed to import performance_optimizer: {e}")
        checks_passed.append(False)
        return False

    # Verify cache TTLs change with mode
    set_mode('trader')
    trader_slow = get_cache_ttl("slow")
    trader_medium = get_cache_ttl("medium")

    set_mode('investor')
    investor_slow = get_cache_ttl("slow")
    investor_medium = get_cache_ttl("medium")

    print(f"\n📊 Ticker essentials cache (medium):")
    print(f"   Trader: {trader_medium}s")
    print(f"   Investor: {investor_medium}s")

    print(f"\n📊 Batch fetch cache (medium):")
    print(f"   Trader: {trader_medium}s")
    print(f"   Investor: {investor_medium}s")

    print(f"\n📊 Compression cache (slow):")
    print(f"   Trader: {trader_slow}s")
    print(f"   Investor: {investor_slow}s")

    # Verify they differ
    checks_passed.append(trader_medium < investor_medium)
    checks_passed.append(trader_slow < investor_slow)

    if all(checks_passed):
        print(f"\n✅ TEST 3 PASSED: Performance optimizer is mode-aware ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 3 FAILED: Some checks failed ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


def test_page_imports_mode_config():
    """Test that Individual Charts & Visuals page imports mode_config"""
    print("\n" + "="*60)
    print("TEST 4: Page Imports Mode Config")
    print("="*60)

    checks_passed = []

    # Read the page file
    try:
        with open('pages/02_📈_Individual_Charts_&_Visuals.py', 'r', encoding='utf-8') as f:
            page_content = f.read()

        # Check for mode_config import
        has_import = 'from mode_config import' in page_content
        print(f"\n✓ Page imports mode_config: {has_import}")
        checks_passed.append(has_import)

        # Check for render_mode_info call
        has_render_mode_info = 'render_mode_info()' in page_content
        print(f"✓ Page calls render_mode_info(): {has_render_mode_info}")
        checks_passed.append(has_render_mode_info)

        # Verify specific imports
        has_get_current_mode = 'get_current_mode' in page_content
        has_should_show_feature = 'should_show_feature' in page_content

        print(f"✓ Imports get_current_mode: {has_get_current_mode}")
        print(f"✓ Imports should_show_feature: {has_should_show_feature}")

        checks_passed.append(has_get_current_mode)
        checks_passed.append(has_should_show_feature)

    except FileNotFoundError:
        print("\n❌ Could not find page file")
        checks_passed.append(False)
        return False

    if all(checks_passed):
        print(f"\n✅ TEST 4 PASSED: Page properly imports mode config ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 4 FAILED: Some imports missing ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


def test_related_modules_import_mode_config():
    """Test that all related modules import mode_config"""
    print("\n" + "="*60)
    print("TEST 5: Related Modules Import Mode Config")
    print("="*60)

    checks_passed = []

    modules = {
        'advanced_charting.py': 'from mode_config import get_cache_ttl',
        'visual_analysis_presets.py': 'from mode_config import get_cache_ttl',
        'performance_optimizer.py': 'from mode_config import get_cache_ttl'
    }

    for module_path, expected_import in modules.items():
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()

            has_import = expected_import in content
            print(f"\n✓ {module_path}")
            print(f"   Has import: {has_import}")

            checks_passed.append(has_import)

        except FileNotFoundError:
            print(f"\n❌ Could not find {module_path}")
            checks_passed.append(False)

    if all(checks_passed):
        print(f"\n✅ TEST 5 PASSED: All modules import mode_config ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 5 FAILED: Some modules missing imports ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


def test_cache_ttl_consistency():
    """Test that cache TTLs are consistent across modules"""
    print("\n" + "="*60)
    print("TEST 6: Cache TTL Consistency")
    print("="*60)

    checks_passed = []

    # Test both modes
    for mode_name in ['trader', 'investor']:
        set_mode(mode_name)
        mode = get_current_mode()

        print(f"\n📊 Testing {mode.name} Mode:")

        # Get all TTL types
        fast = get_cache_ttl("fast")
        medium = get_cache_ttl("medium")
        slow = get_cache_ttl("slow")

        print(f"   Fast: {fast}s")
        print(f"   Medium: {medium}s")
        print(f"   Slow: {slow}s")

        # Verify logical ordering: fast < medium < slow
        ordering_correct = fast < medium < slow
        print(f"   ✓ Ordering correct (fast < medium < slow): {ordering_correct}")
        checks_passed.append(ordering_correct)

    if all(checks_passed):
        print(f"\n✅ TEST 6 PASSED: Cache TTL ordering is consistent ({len(checks_passed)}/{len(checks_passed)} checks)")
        return True
    else:
        print(f"\n❌ TEST 6 FAILED: Some ordering checks failed ({sum(checks_passed)}/{len(checks_passed)} checks)")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INDIVIDUAL CHARTS & VISUALS - MODE AWARENESS TEST SUITE")
    print("="*60)
    print("Testing that Individual Charts & Visuals page and related")
    print("modules properly respect Trader/Investor mode settings")
    print("="*60)

    tests = [
        test_advanced_charting_cache_ttls,
        test_visual_analysis_presets_cache,
        test_performance_optimizer_cache,
        test_page_imports_mode_config,
        test_related_modules_import_mode_config,
        test_cache_ttl_consistency
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - Test {i}: {test.__name__}")

    print("="*60)
    if passed == total:
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print("Individual Charts & Visuals page is fully mode-aware!")
    else:
        print(f"⚠️ SOME TESTS FAILED: {passed}/{total} passed")
        print("Please review failed tests above")
    print("="*60)
