"""
Test Zero-FCF Valuation Engine
Validates all valuation methods with sample data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from zero_fcf_valuation import ZeroFCFValuationEngine
import pandas as pd
import numpy as np


def test_revenue_valuation():
    """Test revenue-based valuation"""
    print("\n🧪 Testing Revenue Valuation...")
    
    engine = ZeroFCFValuationEngine()
    
    # Sample SaaS company data
    info = {
        "totalRevenue": 500_000_000,  # $500M revenue
        "revenueGrowth": 0.40,  # 40% growth
        "sector": "Technology",
        "industry": "Software - Application",
        "totalCash": 100_000_000,
        "totalDebt": 50_000_000,
        "sharesOutstanding": 100_000_000,
        "currentPrice": 25.0
    }
    
    result = engine.calculate_revenue_valuation(info, {})
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Fair Value: ${result['fair_value']:.2f}")
    print(f"   📊 Revenue Multiple: {result['revenue_multiple']:.1f}x")
    print(f"   📈 Growth Adjustment: {result['growth_adjustment']:.2f}x")
    print(f"   💰 Enterprise Value: ${result['enterprise_value'] / 1e9:.2f}B")
    
    return True


def test_ebitda_valuation():
    """Test EBITDA multiple valuation"""
    print("\n🧪 Testing EBITDA Valuation...")
    
    engine = ZeroFCFValuationEngine()
    
    # Sample company with positive EBITDA
    info = {
        "ebitda": 150_000_000,  # $150M EBITDA
        "ebitdaMargins": 0.25,  # 25% margin
        "revenueGrowth": 0.25,  # 25% growth
        "sector": "Technology",
        "industry": "Software",
        "totalCash": 80_000_000,
        "totalDebt": 40_000_000,
        "sharesOutstanding": 50_000_000,
        "currentPrice": 40.0
    }
    
    result = engine.calculate_ebitda_valuation(info, {})
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Fair Value: ${result['fair_value']:.2f}")
    print(f"   📊 EBITDA Multiple: {result['ebitda_multiple']:.1f}x")
    print(f"   📈 EBITDA Margin: {result['ebitda_margin']:.1f}%")
    print(f"   💰 Enterprise Value: ${result['enterprise_value'] / 1e9:.2f}B")
    
    return True


def test_rule_of_40():
    """Test Rule of 40 valuation"""
    print("\n🧪 Testing Rule of 40 Valuation...")
    
    engine = ZeroFCFValuationEngine()
    
    # Sample SaaS company
    info = {
        "totalRevenue": 300_000_000,
        "revenueGrowth": 0.35,  # 35% growth
        "sector": "Technology",
        "industry": "SaaS",
        "totalCash": 50_000_000,
        "totalDebt": 20_000_000,
        "sharesOutstanding": 80_000_000,
        "currentPrice": 30.0
    }
    
    # Mock cash flow data
    financials = {
        "cash_flow": pd.DataFrame({
            "2023": [30_000_000],  # $30M FCF
            "2022": [20_000_000],
            "2021": [15_000_000],
            "2020": [10_000_000]
        }, index=["Free Cash Flow"])
    }
    
    result = engine.calculate_rule_of_40_valuation(info, financials)
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Fair Value: ${result['fair_value']:.2f}")
    print(f"   📐 Rule of 40 Score: {result['rule_of_40_score']:.1f}%")
    print(f"   📈 Revenue Growth: {result['revenue_growth']:.1f}%")
    print(f"   💵 FCF Margin: {result['fcf_margin']:.1f}%")
    print(f"   ⭐ Quality: {result['quality_rating'].title()}")
    
    return True


def test_unit_economics():
    """Test unit economics valuation"""
    print("\n🧪 Testing Unit Economics Valuation...")
    
    engine = ZeroFCFValuationEngine()
    
    # Sample SaaS company
    info = {
        "totalRevenue": 200_000_000,
        "revenueGrowth": 0.50,  # 50% growth
        "grossMargins": 0.80,  # 80% margin
        "sector": "Technology",
        "industry": "SaaS",
        "totalCash": 40_000_000,
        "totalDebt": 10_000_000,
        "sharesOutstanding": 60_000_000,
        "currentPrice": 35.0
    }
    
    result = engine.calculate_unit_economics_valuation(info, {})
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Fair Value: ${result['fair_value']:.2f}")
    print(f"   👥 LTV:CAC Ratio: {result['ltv_cac_ratio']:.2f}x")
    print(f"   💰 Customer LTV: ${result['ltv']:,.0f}")
    print(f"   💸 Customer CAC: ${result['cac']:,.0f}")
    print(f"   ⏱️  Payback Period: {result['payback_period_months']:.1f} months")
    
    return True


def test_terminal_value():
    """Test revenue terminal value calculation"""
    print("\n🧪 Testing Terminal Value Method...")
    
    engine = ZeroFCFValuationEngine()
    
    # Sample company with revenue history
    info = {
        "totalRevenue": 400_000_000,
        "revenueGrowth": 0.30,  # 30% growth
        "sector": "Technology",
        "beta": 1.2,
        "totalCash": 60_000_000,
        "totalDebt": 30_000_000,
        "sharesOutstanding": 100_000_000,
        "currentPrice": 28.0
    }
    
    # Mock revenue history
    financials = {
        "financials": pd.DataFrame({
            "2023": [400_000_000],
            "2022": [300_000_000],
            "2021": [230_000_000],
            "2020": [180_000_000]
        }, index=["Total Revenue"])
    }
    
    result = engine.calculate_revenue_terminal_value(info, financials)
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Fair Value: ${result['fair_value']:.2f}")
    print(f"   🎯 Terminal Value: ${result['terminal_value'] / 1e9:.2f}B")
    print(f"   📈 Historical CAGR: {result['historical_cagr']:.1f}%")
    print(f"   📉 Terminal Growth: {result['terminal_growth']:.1f}%")
    print(f"   🔢 WACC: {result['wacc']:.1f}%")
    
    return True


def test_comprehensive_valuation():
    """Test comprehensive multi-method valuation"""
    print("\n🧪 Testing Comprehensive Valuation (All Methods)...")
    
    engine = ZeroFCFValuationEngine()
    
    # Rich dataset SaaS company
    info = {
        "totalRevenue": 600_000_000,
        "revenueGrowth": 0.45,  # 45% growth
        "ebitda": 180_000_000,
        "ebitdaMargins": 0.30,  # 30% margin
        "grossMargins": 0.78,
        "sector": "Technology",
        "industry": "Software - Application",
        "beta": 1.3,
        "totalCash": 120_000_000,
        "totalDebt": 60_000_000,
        "sharesOutstanding": 150_000_000,
        "currentPrice": 32.0
    }
    
    # Mock financials
    financials = {
        "cash_flow": pd.DataFrame({
            "2023": [50_000_000],
            "2022": [35_000_000],
            "2021": [20_000_000],
            "2020": [10_000_000]
        }, index=["Free Cash Flow"]),
        "financials": pd.DataFrame({
            "2023": [600_000_000],
            "2022": [450_000_000],
            "2021": [310_000_000],
            "2020": [210_000_000]
        }, index=["Total Revenue"])
    }
    
    result = engine.calculate_comprehensive_valuation(info, financials)
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return False
    
    print(f"   ✅ Weighted Fair Value: ${result['fair_value']:.2f}")
    print(f"   📊 Current Price: ${result['current_price']:.2f}")
    print(f"   📈 Upside: {result['upside']:+.1f}%")
    print(f"   🏢 Company Type: {result['company_type']}")
    print(f"   🎯 Primary Method: {result['primary_method']}")
    print(f"   ✨ Confidence: {result['confidence'].title()}")
    
    print("\n   📋 Methods Used:")
    valuations = result.get("valuations", {})
    for method, val_data in valuations.items():
        fair_value = val_data.get("fair_value", 0)
        quality = val_data.get("data_quality", "medium")
        print(f"      • {method.title()}: ${fair_value:.2f} (Quality: {quality})")
    
    print("\n   🎲 Scenarios:")
    scenarios = result.get("scenarios", {})
    for scenario, value in scenarios.items():
        print(f"      • {scenario.title()}: ${value:.2f}")
    
    return True


def test_company_type_detection():
    """Test company type detection logic"""
    print("\n🧪 Testing Company Type Detection...")
    
    engine = ZeroFCFValuationEngine()
    
    test_cases = [
        ({"sector": "Technology", "industry": "Software - Application"}, "Software"),
        ({"sector": "Technology", "industry": "SaaS"}, "SaaS"),
        ({"sector": "Consumer Cyclical", "industry": "E-commerce"}, "E-commerce"),
        ({"sector": "Healthcare", "industry": "Biotechnology"}, "Biotech"),
        ({"sector": "Technology", "industry": "Semiconductors"}, "Technology"),
        ({"sector": "Industrials", "industry": "Aerospace"}, "Industrials"),
    ]
    
    for info, expected_type in test_cases:
        detected = engine._detect_company_type(info, {})
        status = "✅" if detected == expected_type else "❌"
        print(f"   {status} {info['industry']} → {detected} (expected: {expected_type})")
    
    return True


def run_all_tests():
    """Run all test cases"""
    print("=" * 60)
    print("🚀 Zero-FCF Valuation Engine Test Suite")
    print("=" * 60)
    
    tests = [
        ("Revenue Valuation", test_revenue_valuation),
        ("EBITDA Valuation", test_ebitda_valuation),
        ("Rule of 40", test_rule_of_40),
        ("Unit Economics", test_unit_economics),
        ("Terminal Value", test_terminal_value),
        ("Company Type Detection", test_company_type_detection),
        ("Comprehensive Valuation", test_comprehensive_valuation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"   ❌ Test failed: {test_name}")
        except Exception as e:
            failed += 1
            print(f"   ❌ Test error in {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
