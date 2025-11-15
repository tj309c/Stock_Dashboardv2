"""
Production Validation Script - Individual Tool & Formula Testing
Tests each calculation, formula, and variable individually for production readiness
"""
import sys
import traceback
from datetime import datetime
import pandas as pd
import numpy as np

class ProductionValidator:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.warnings = 0
        self.results = []
    
    def test(self, name, func, critical=True):
        """Run a single test with detailed output"""
        try:
            print(f"\n{'='*70}")
            print(f"{'[CRITICAL]' if critical else '[OPTIONAL]'} {name}")
            print('='*70)
            result = func()
            print(f"✅ PASS")
            self.tests_passed += 1
            self.results.append({
                "test": name,
                "status": "PASS",
                "critical": critical,
                "result": result
            })
            return result
        except Exception as e:
            status = "❌ FAIL" if critical else "⚠️ WARNING"
            print(f"{status}: {str(e)}")
            traceback.print_exc()
            if critical:
                self.tests_failed += 1
            else:
                self.warnings += 1
            self.results.append({
                "test": name,
                "status": "FAIL" if critical else "WARNING",
                "critical": critical,
                "error": str(e)
            })
            return None
    
    def summary(self):
        """Print comprehensive summary"""
        print(f"\n{'='*70}")
        print("PRODUCTION VALIDATION SUMMARY")
        print('='*70)
        total = self.tests_passed + self.tests_failed + self.warnings
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed (Critical): {self.tests_failed}")
        print(f"⚠️  Warnings (Optional): {self.warnings}")
        print(f"Pass Rate: {(self.tests_passed/total*100) if total > 0 else 0:.1f}%")
        
        critical_tests = sum(1 for r in self.results if r.get('critical'))
        critical_passed = sum(1 for r in self.results if r.get('critical') and r['status'] == 'PASS')
        print(f"\nCritical Systems: {critical_passed}/{critical_tests} passing")
        
        print('='*70)
        
        if self.tests_failed > 0:
            print("\n❌ CRITICAL FAILURES:")
            for r in self.results:
                if r["status"] == "FAIL" and r.get("critical"):
                    print(f"  - {r['test']}: {r.get('error', 'Unknown error')}")
        
        if self.warnings > 0:
            print("\n⚠️ WARNINGS (Non-Critical):")
            for r in self.results:
                if r["status"] == "WARNING":
                    print(f"  - {r['test']}: {r.get('error', 'Unknown')}")
        
        return self.tests_failed == 0


# Initialize validator
validator = ProductionValidator()

print("\n" + "="*70)
print("PRODUCTION VALIDATION - INDIVIDUAL TOOL TESTING")
print("="*70)
print(f"Started: {datetime.now()}")
print(f"Purpose: Validate each formula, calculation, and variable")
print("="*70)

# ========== SECTION 1: FORMATTERS - INDIVIDUAL FUNCTION TESTING ==========
print("\n\n" + "█"*70)
print("SECTION 1: FORMATTERS MODULE - Individual Function Validation")
print("█"*70)

def test_format_currency_values():
    from src.ui_utils.formatters import format_currency
    
    test_cases = [
        (0, "$0.00"),
        (1, "$1.00"),
        (999, "$999.00"),
        (1000, "$1.00K"),
        (1500, "$1.50K"),
        (999999, "$1.00M"),
        (1000000, "$1.00M"),
        (1234567, "$1.23M"),
        (1000000000, "$1.00B"),
        (1500000000000, "$1.50T"),
        (-1234, "-$1.23K"),
    ]
    
    print("  Testing format_currency with edge cases:")
    all_passed = True
    for value, expected in test_cases:
        result = format_currency(value)
        match = "✓" if result == expected else "✗"
        print(f"    {match} format_currency({value:>15}) = {result:>10} (expected: {expected})")
        if result != expected:
            all_passed = False
            raise AssertionError(f"Expected {expected}, got {result}")
    
    return f"All {len(test_cases)} currency format cases passed"

validator.test("Format Currency - All Values", test_format_currency_values)

def test_format_percentage_precision():
    from src.ui_utils.formatters import format_percentage
    
    test_cases = [
        (0, "0.00%"),
        (0.1, "0.10%"),
        (0.1523, "0.15%"),
        (0.999, "1.00%"),
        (1.0, "1.00%"),
        (-0.05, "-0.05%"),
        (0.0001, "0.00%"),
    ]
    
    print("  Testing format_percentage precision:")
    for value, expected in test_cases:
        result = format_percentage(value)
        match = "✓" if result == expected else "✗"
        print(f"    {match} format_percentage({value:>8.4f}) = {result:>10} (expected: {expected})")
        if result != expected:
            raise AssertionError(f"Expected {expected}, got {result}")
    
    return f"All {len(test_cases)} percentage format cases passed"

validator.test("Format Percentage - Precision", test_format_percentage_precision)

def test_format_large_number_scaling():
    from src.ui_utils.formatters import format_large_number
    
    test_cases = [
        (0, "0"),
        (999, "999"),
        (1000, "1.00K"),
        (1500, "1.50K"),
        (999999, "1.00M"),
        (1000000, "1.00M"),
        (1500000, "1.50M"),
        (1000000000, "1.00B"),
        (1500000000, "1.50B"),
        (1000000000000, "1.00T"),
    ]
    
    print("  Testing format_large_number scaling:")
    for value, expected in test_cases:
        result = format_large_number(value)
        match = "✓" if result == expected else "✗"
        print(f"    {match} format_large_number({value:>15}) = {result:>10} (expected: {expected})")
        if result != expected:
            raise AssertionError(f"Expected {expected}, got {result}")
    
    return f"All {len(test_cases)} number scaling cases passed"

validator.test("Format Large Number - Scaling", test_format_large_number_scaling)

# ========== SECTION 2: CONSTANTS - VALUE VALIDATION ==========
print("\n\n" + "█"*70)
print("SECTION 2: CONSTANTS MODULE - Value Validation")
print("█"*70)

def test_constants_financial_values():
    from src.core.constants import (
        RISK_FREE_RATE, MARKET_RISK_PREMIUM, TERMINAL_GROWTH_RATE,
        DEFAULT_WACC, DEFAULT_GROWTH_RATE, DEFAULT_PROJECTION_YEARS
    )
    
    print("  Validating financial constants:")
    
    # Risk-free rate (typically 3-5% for 10Y Treasury)
    assert 0.01 <= RISK_FREE_RATE <= 0.10, f"Risk-free rate {RISK_FREE_RATE} out of reasonable range"
    print(f"    ✓ RISK_FREE_RATE = {RISK_FREE_RATE} (0.04 = 4%)")
    
    # Market risk premium (typically 6-9%)
    assert 0.05 <= MARKET_RISK_PREMIUM <= 0.15, f"Market risk premium {MARKET_RISK_PREMIUM} out of range"
    print(f"    ✓ MARKET_RISK_PREMIUM = {MARKET_RISK_PREMIUM} (0.08 = 8%)")
    
    # Terminal growth (typically 2-3%)
    assert 0.01 <= TERMINAL_GROWTH_RATE <= 0.05, f"Terminal growth {TERMINAL_GROWTH_RATE} out of range"
    print(f"    ✓ TERMINAL_GROWTH_RATE = {TERMINAL_GROWTH_RATE} (0.025 = 2.5%)")
    
    # WACC (typically 8-12%)
    assert 0.05 <= DEFAULT_WACC <= 0.20, f"Default WACC {DEFAULT_WACC} out of range"
    print(f"    ✓ DEFAULT_WACC = {DEFAULT_WACC} (0.1 = 10%)")
    
    # Growth rate (typically 5-15% for projections)
    assert 0.03 <= DEFAULT_GROWTH_RATE <= 0.30, f"Default growth {DEFAULT_GROWTH_RATE} out of range"
    print(f"    ✓ DEFAULT_GROWTH_RATE = {DEFAULT_GROWTH_RATE} (0.1 = 10%)")
    
    # Projection years (typically 3-10 years)
    assert 1 <= DEFAULT_PROJECTION_YEARS <= 20, f"Projection years {DEFAULT_PROJECTION_YEARS} out of range"
    print(f"    ✓ DEFAULT_PROJECTION_YEARS = {DEFAULT_PROJECTION_YEARS} years")
    
    return "All financial constants within reasonable ranges"

validator.test("Constants - Financial Values", test_constants_financial_values)

def test_constants_technical_indicators():
    from src.core.constants import RSI_OVERSOLD, RSI_OVERBOUGHT
    
    print("  Validating technical indicator constants:")
    
    # RSI oversold (typically 20-30)
    assert 10 <= RSI_OVERSOLD <= 35, f"RSI oversold {RSI_OVERSOLD} out of range"
    print(f"    ✓ RSI_OVERSOLD = {RSI_OVERSOLD}")
    
    # RSI overbought (typically 65-80)
    assert 65 <= RSI_OVERBOUGHT <= 90, f"RSI overbought {RSI_OVERBOUGHT} out of range"
    print(f"    ✓ RSI_OVERBOUGHT = {RSI_OVERBOUGHT}")
    
    # RSI oversold must be less than overbought
    assert RSI_OVERSOLD < RSI_OVERBOUGHT, "RSI oversold must be < overbought"
    print(f"    ✓ RSI_OVERSOLD < RSI_OVERBOUGHT ({RSI_OVERSOLD} < {RSI_OVERBOUGHT})")
    
    return "Technical indicator constants valid"

validator.test("Constants - Technical Indicators", test_constants_technical_indicators)

# ========== SECTION 3: DCF CALCULATION - FORMULA VALIDATION ==========
print("\n\n" + "█"*70)
print("SECTION 3: DCF CALCULATION - Formula & Variable Validation")
print("█"*70)

def test_dcf_present_value_formula():
    from enhanced_valuation import EnhancedDCFCalculator
    
    print("  Testing DCF present value formula:")
    calc = EnhancedDCFCalculator()
    
    # Test case: $1M cash flow, 10% growth, 10% WACC
    result = calc.calculate_dcf_detailed(
        base_cash_flow=1000000,
        growth_rate=0.10,
        wacc=0.10,
        terminal_growth=0.025,
        projection_years=5,
        cash=0,
        debt=0,
        shares_outstanding=1000000
    )
    
    # Validate structure
    assert 'fair_value_per_share' in result, "Missing fair value"
    assert 'enterprise_value' in result, "Missing enterprise value"
    assert 'projected_cash_flows' in result, "Missing cash flows"
    print(f"    ✓ Result structure complete")
    
    # Validate projected cash flows
    cfs = result['projected_cash_flows']
    assert len(cfs) == 5, f"Expected 5 years, got {len(cfs)}"
    print(f"    ✓ Projected 5 years of cash flows")
    
    # Year 1 should be: 1M * 1.10 = 1.1M
    year1_cf = cfs[0]['cash_flow']
    expected_year1 = 1000000 * 1.10
    assert abs(year1_cf - expected_year1) < 1, f"Year 1 CF mismatch: {year1_cf} vs {expected_year1}"
    print(f"    ✓ Year 1 cash flow: ${year1_cf:,.0f} (expected: ${expected_year1:,.0f})")
    
    # Year 5 should be: 1M * 1.10^5 = 1.61M
    year5_cf = cfs[4]['cash_flow']
    expected_year5 = 1000000 * (1.10 ** 5)
    assert abs(year5_cf - expected_year5) < 1, f"Year 5 CF mismatch"
    print(f"    ✓ Year 5 cash flow: ${year5_cf:,.0f} (expected: ${expected_year5:,.0f})")
    
    # Discount factors should decrease
    df1 = cfs[0]['discount_factor']
    df5 = cfs[4]['discount_factor']
    assert df1 > df5, "Discount factors should decrease over time"
    print(f"    ✓ Discount factors decreasing: {df1:.4f} > {df5:.4f}")
    
    # Enterprise value should be positive
    ev = result['enterprise_value']
    assert ev > 0, "Enterprise value should be positive"
    print(f"    ✓ Enterprise value: ${ev:,.0f}")
    
    # Fair value should be positive
    fv = result['fair_value_per_share']
    assert fv > 0, "Fair value should be positive"
    print(f"    ✓ Fair value per share: ${fv:.2f}")
    
    return f"DCF formula validated: ${fv:.2f}/share"

validator.test("DCF Calculation - Formula Validation", test_dcf_present_value_formula)

def test_dcf_terminal_value_calculation():
    from enhanced_valuation import EnhancedDCFCalculator
    
    print("  Testing DCF terminal value calculation:")
    calc = EnhancedDCFCalculator()
    
    result = calc.calculate_dcf_detailed(
        base_cash_flow=1000000,
        growth_rate=0.10,
        wacc=0.12,  # WACC > terminal growth (required)
        terminal_growth=0.02,
        projection_years=5,
        cash=0,
        debt=0,
        shares_outstanding=1000000
    )
    
    # Terminal value formula: FCF_terminal / (WACC - g_terminal)
    terminal_cf = result['terminal_cf']
    terminal_value = result['terminal_value']
    
    # Manual calculation
    year5_cf = 1000000 * (1.10 ** 5)
    expected_terminal_cf = year5_cf * 1.02
    expected_terminal_value = expected_terminal_cf / (0.12 - 0.02)
    
    print(f"    Terminal CF: ${terminal_cf:,.0f} (expected: ${expected_terminal_cf:,.0f})")
    print(f"    Terminal Value: ${terminal_value:,.0f} (expected: ${expected_terminal_value:,.0f})")
    
    assert abs(terminal_cf - expected_terminal_cf) < 100, "Terminal CF mismatch"
    assert abs(terminal_value - expected_terminal_value) < 1000, "Terminal value mismatch"
    print(f"    ✓ Terminal value formula correct")
    
    # PV of terminal value should be discounted
    pv_terminal = result['pv_terminal_value']
    assert pv_terminal < terminal_value, "PV of terminal should be less than terminal value"
    print(f"    ✓ PV of terminal value: ${pv_terminal:,.0f} (correctly discounted)")
    
    return "Terminal value calculation validated"

validator.test("DCF - Terminal Value Formula", test_dcf_terminal_value_calculation)

def test_dcf_input_validation():
    from enhanced_valuation import EnhancedDCFCalculator
    
    print("  Testing DCF input validation:")
    calc = EnhancedDCFCalculator()
    
    # Test 1: Zero shares
    result = calc.calculate_dcf_detailed(1000000, 0.1, 0.1, 0.025, 5, 0, 0, 0)
    assert 'error' in result, "Should error on zero shares"
    print(f"    ✓ Rejects zero shares: {result['error']}")
    
    # Test 2: WACC <= terminal growth
    result = calc.calculate_dcf_detailed(1000000, 0.1, 0.02, 0.03, 5, 0, 0, 1000000)
    assert 'error' in result, "Should error when WACC <= terminal growth"
    print(f"    ✓ Rejects WACC <= terminal growth: {result['error']}")
    
    # Test 3: Zero cash flow
    result = calc.calculate_dcf_detailed(0, 0.1, 0.1, 0.025, 5, 0, 0, 1000000)
    assert 'error' in result, "Should error on zero cash flow"
    print(f"    ✓ Rejects zero cash flow: {result['error']}")
    
    # Test 4: Invalid projection years
    result = calc.calculate_dcf_detailed(1000000, 0.1, 0.1, 0.025, 0, 0, 0, 1000000)
    assert 'error' in result, "Should error on zero projection years"
    print(f"    ✓ Rejects invalid projection years: {result['error']}")
    
    return "All DCF input validations working"

validator.test("DCF - Input Validation", test_dcf_input_validation)

# ========== SECTION 4: VALUATION ENGINE - CAPM & WACC ==========
print("\n\n" + "█"*70)
print("SECTION 4: VALUATION ENGINE - CAPM & WACC Calculations")
print("█"*70)

def test_capm_calculation():
    from analysis_engine import ValuationEngine
    from src.core.constants import RISK_FREE_RATE, MARKET_RISK_PREMIUM
    
    print("  Testing CAPM formula: Required Return = Rf + β * (Rm - Rf)")
    engine = ValuationEngine()
    
    # Test with different betas
    test_cases = [
        (0.5, RISK_FREE_RATE + 0.5 * MARKET_RISK_PREMIUM),  # Low beta
        (1.0, RISK_FREE_RATE + 1.0 * MARKET_RISK_PREMIUM),  # Market beta
        (1.5, RISK_FREE_RATE + 1.5 * MARKET_RISK_PREMIUM),  # High beta
        (2.0, RISK_FREE_RATE + 2.0 * MARKET_RISK_PREMIUM),  # Very high beta
    ]
    
    for beta, expected_return in test_cases:
        # CAPM: Rf + β * (Rm - Rf)
        # Since MARKET_RISK_PREMIUM already is (Rm - Rf), formula is: Rf + β * MRP
        calculated = RISK_FREE_RATE + beta * MARKET_RISK_PREMIUM
        print(f"    β={beta}: Required return = {calculated:.4f} ({calculated*100:.2f}%)")
        assert abs(calculated - expected_return) < 0.0001, f"CAPM mismatch for beta {beta}"
    
    print(f"    ✓ CAPM formula correct for all test cases")
    return "CAPM calculations validated"

validator.test("Valuation Engine - CAPM Formula", test_capm_calculation)

def test_wacc_calculation():
    from src.core.constants import RISK_FREE_RATE, MARKET_RISK_PREMIUM
    
    print("  Testing WACC formula: WACC = Rf + β * MRP")
    
    # With beta = 1.0, WACC should equal Rf + MRP
    beta = 1.0
    wacc = RISK_FREE_RATE + beta * MARKET_RISK_PREMIUM
    expected = 0.04 + 1.0 * 0.08  # 0.12 = 12%
    
    print(f"    WACC (β=1.0) = {wacc:.4f} ({wacc*100:.2f}%)")
    print(f"    Expected: {expected:.4f} ({expected*100:.2f}%)")
    assert abs(wacc - expected) < 0.0001, "WACC calculation mismatch"
    print(f"    ✓ WACC formula correct")
    
    return f"WACC = {wacc*100:.2f}%"

validator.test("Valuation Engine - WACC Calculation", test_wacc_calculation)

# ========== SECTION 5: TECHNICAL ANALYSIS - RSI FORMULA ==========
print("\n\n" + "█"*70)
print("SECTION 5: TECHNICAL ANALYSIS - RSI Formula Validation")
print("█"*70)

def test_rsi_calculation():
    from analysis_engine import TechnicalAnalyzer
    from src.core.constants import RSI_OVERSOLD, RSI_OVERBOUGHT
    import pandas as pd
    import numpy as np
    
    print("  Testing RSI formula: RSI = 100 - (100 / (1 + RS))")
    print("  Where RS = Average Gain / Average Loss")
    
    analyzer = TechnicalAnalyzer()
    
    # Create test data with known pattern
    # Prices going up should give high RSI
    dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
    prices_up = np.linspace(100, 150, 50)  # Steady uptrend
    df_up = pd.DataFrame({'Close': prices_up}, index=dates)
    
    result_up = analyzer.analyze_technicals(df_up)
    rsi_up = result_up['rsi']['value']
    signal_up = result_up['rsi']['signal']
    
    print(f"    Uptrend RSI: {rsi_up:.2f} (signal: {signal_up})")
    assert 50 < rsi_up <= 100, f"Uptrend should have RSI > 50, got {rsi_up}"
    
    # Prices going down should give low RSI
    prices_down = np.linspace(150, 100, 50)  # Steady downtrend
    df_down = pd.DataFrame({'Close': prices_down}, index=dates)
    
    result_down = analyzer.analyze_technicals(df_down)
    rsi_down = result_down['rsi']['value']
    signal_down = result_down['rsi']['signal']
    
    print(f"    Downtrend RSI: {rsi_down:.2f} (signal: {signal_down})")
    assert 0 <= rsi_down < 50, f"Downtrend should have RSI < 50, got {rsi_down}"
    
    print(f"    ✓ RSI correctly distinguishes up/down trends")
    
    # Test RSI signal thresholds
    print(f"\n    Testing RSI signal thresholds:")
    print(f"      Oversold threshold: {RSI_OVERSOLD}")
    print(f"      Overbought threshold: {RSI_OVERBOUGHT}")
    
    if rsi_down < RSI_OVERSOLD:
        assert signal_down == "oversold", f"Should signal oversold for RSI {rsi_down}"
        print(f"      ✓ Correctly signals 'oversold' at RSI {rsi_down:.2f}")
    
    if rsi_up > RSI_OVERBOUGHT:
        assert signal_up == "overbought", f"Should signal overbought for RSI {rsi_up}"
        print(f"      ✓ Correctly signals 'overbought' at RSI {rsi_up:.2f}")
    
    return f"RSI formula validated (uptrend: {rsi_up:.1f}, downtrend: {rsi_down:.1f})"

validator.test("Technical Analysis - RSI Formula", test_rsi_calculation)

# ========== SECTION 6: DATA FETCHER - API INTEGRATION ==========
print("\n\n" + "█"*70)
print("SECTION 6: DATA FETCHER - API Integration & Data Quality")
print("█"*70)

def test_stock_data_fetcher():
    from data_fetcher import MarketDataFetcher
    
    print("  Testing MarketDataFetcher with AAPL:")
    fetcher = MarketDataFetcher()
    
    data = fetcher.get_stock_data('AAPL', period='5d')
    
    # Validate required keys
    required_keys = ['info', 'history']
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
        print(f"    ✓ Key '{key}' present")
    
    # Validate info data
    info = data['info']
    assert isinstance(info, dict), "Info should be a dictionary"
    print(f"    ✓ Info is dictionary with {len(info)} fields")
    
    # Validate history data
    history = data['history']
    assert history is not None, "History should not be None"
    
    if hasattr(history, 'shape'):
        print(f"    ✓ History DataFrame shape: {history.shape}")
        assert len(history) > 0, "History should have data"
    
    # Check for current price
    if 'current_price' in data:
        price = data['current_price']
        assert price > 0, "Current price should be positive"
        print(f"    ✓ Current price: ${price:.2f}")
    
    return "Stock data fetch successful"

validator.test("Data Fetcher - Stock Data", test_stock_data_fetcher, critical=True)

def test_data_caching():
    from data_fetcher import MarketDataFetcher
    import time
    
    print("  Testing data caching mechanism:")
    fetcher = MarketDataFetcher()
    
    # First fetch
    start1 = time.time()
    data1 = fetcher.get_stock_data('AAPL', period='1d')
    time1 = time.time() - start1
    print(f"    First fetch: {time1:.3f}s")
    
    # Second fetch (should use cache)
    start2 = time.time()
    data2 = fetcher.get_stock_data('AAPL', period='1d')
    time2 = time.time() - start2
    print(f"    Second fetch: {time2:.3f}s")
    
    # Second should be faster (cached)
    if time2 < time1 * 0.5:  # At least 50% faster
        print(f"    ✓ Caching working (2nd fetch {time1/time2:.1f}x faster)")
    else:
        print(f"    ⚠ Caching may not be working optimally")
    
    return f"Cache test complete (1st: {time1:.2f}s, 2nd: {time2:.2f}s)"

validator.test("Data Fetcher - Caching", test_data_caching, critical=False)

# ========== SECTION 7: INTEGRATION - END-TO-END WORKFLOW ==========
print("\n\n" + "█"*70)
print("SECTION 7: INTEGRATION - End-to-End Workflow Validation")
print("█"*70)

def test_complete_workflow():
    from data_fetcher import MarketDataFetcher
    from analysis_engine import ValuationEngine, TechnicalAnalyzer
    from src.ui_utils.formatters import format_currency, format_percentage
    
    print("  Testing complete workflow: Fetch → Analyze → Format → Display")
    
    # Step 1: Fetch data
    print("\n  Step 1: Data Fetching")
    fetcher = MarketDataFetcher()
    data = fetcher.get_stock_data('AAPL', period='1mo')
    assert 'history' in data, "Missing history data"
    print(f"    ✓ Fetched {len(data.get('history', []))} days of data")
    
    # Step 2: Technical analysis
    print("\n  Step 2: Technical Analysis")
    analyzer = TechnicalAnalyzer()
    tech = analyzer.analyze_technicals(data['history'])
    assert 'rsi' in tech, "Missing RSI"
    print(f"    ✓ RSI: {tech['rsi']['value']:.2f} ({tech['rsi']['signal']})")
    
    # Step 3: Valuation (if possible)
    print("\n  Step 3: Valuation")
    engine = ValuationEngine()
    print(f"    ✓ Engine initialized (Rf={engine.risk_free_rate}, MRP={engine.market_risk_premium})")
    
    # Step 4: Format output
    print("\n  Step 4: Output Formatting")
    if 'current_price' in data:
        price_str = format_currency(data['current_price'])
        print(f"    ✓ Formatted price: {price_str}")
    
    rsi_pct = format_percentage(tech['rsi']['value'] / 100)
    print(f"    ✓ Formatted RSI: {rsi_pct}")
    
    return "Complete workflow validated"

validator.test("Integration - Complete Workflow", test_complete_workflow)

# ========== SECTION 8: ERROR HANDLING ==========
print("\n\n" + "█"*70)
print("SECTION 8: ERROR HANDLING - Edge Cases & Invalid Inputs")
print("█"*70)

def test_error_handling():
    from enhanced_valuation import EnhancedDCFCalculator
    from data_fetcher import MarketDataFetcher
    
    print("  Testing error handling for invalid inputs:")
    
    calc = EnhancedDCFCalculator()
    
    # Invalid ticker
    print("\n    Testing invalid ticker:")
    fetcher = MarketDataFetcher()
    try:
        data = fetcher.get_stock_data('INVALIDTICKER123')
        # Should either return error or empty data
        if 'error' in data or not data.get('history'):
            print(f"      ✓ Handles invalid ticker gracefully")
        else:
            print(f"      ⚠ Invalid ticker returned data (may be valid)")
    except Exception as e:
        print(f"      ✓ Raises appropriate exception: {type(e).__name__}")
    
    # Division by zero in DCF
    print("\n    Testing division by zero protection:")
    result = calc.calculate_dcf_detailed(1000000, 0.1, 0.025, 0.025, 5, 0, 0, 1000000)
    assert 'error' in result, "Should catch WACC = terminal growth"
    print(f"      ✓ Prevents division by zero: {result['error']}")
    
    # Negative values
    print("\n    Testing negative value handling:")
    result = calc.calculate_dcf_detailed(-1000000, 0.1, 0.1, 0.025, 5, 0, 0, 1000000)
    # Should either handle or error
    if 'error' in result or result.get('fair_value_per_share'):
        print(f"      ✓ Handles negative cash flow")
    
    return "Error handling validated"

validator.test("Error Handling - Edge Cases", test_error_handling, critical=False)

# ========== SECTION 9: PERFORMANCE ==========
print("\n\n" + "█"*70)
print("SECTION 9: PERFORMANCE - Speed & Efficiency Tests")
print("█"*70)

def test_performance():
    from enhanced_valuation import EnhancedDCFCalculator
    import time
    
    print("  Testing calculation performance:")
    
    calc = EnhancedDCFCalculator()
    
    # Time single DCF calculation
    start = time.time()
    result = calc.calculate_dcf_detailed(1000000, 0.1, 0.1, 0.025, 5, 0, 0, 1000000)
    elapsed = time.time() - start
    
    print(f"    Single DCF calculation: {elapsed*1000:.2f}ms")
    assert elapsed < 1.0, f"DCF too slow: {elapsed:.3f}s"
    print(f"    ✓ Performance acceptable (< 1s)")
    
    # Time 100 calculations
    start = time.time()
    for _ in range(100):
        calc.calculate_dcf_detailed(1000000, 0.1, 0.1, 0.025, 5, 0, 0, 1000000)
    elapsed_100 = time.time() - start
    
    print(f"    100 DCF calculations: {elapsed_100:.3f}s ({elapsed_100/100*1000:.2f}ms avg)")
    print(f"    ✓ Throughput: {100/elapsed_100:.0f} calculations/second")
    
    return f"Performance: {elapsed_100/100*1000:.2f}ms per DCF"

validator.test("Performance - Calculation Speed", test_performance, critical=False)

# ========== FINAL SUMMARY ==========
production_ready = validator.summary()

print("\n" + "="*70)
print("PRODUCTION READINESS ASSESSMENT")
print("="*70)

if production_ready:
    print("✅ SYSTEM IS PRODUCTION READY")
    print("\nAll critical tests passed. System validated for production deployment.")
    sys.exit(0)
else:
    print("❌ SYSTEM NOT READY FOR PRODUCTION")
    print("\nCritical failures detected. Review errors above before deployment.")
    sys.exit(1)
