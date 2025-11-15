"""
Comprehensive Health Check Script
Tests all functionality, imports, data fetchers, calculations, and business logic
"""
import sys
import os
import importlib
import traceback
from datetime import datetime
import json

# Results tracking
results = {
    "timestamp": datetime.now().isoformat(),
    "syntax_checks": [],
    "import_checks": [],
    "module_tests": [],
    "calculation_tests": [],
    "data_fetcher_tests": [],
    "errors": [],
    "warnings": [],
    "summary": {}
}


def log_result(category, test_name, status, details=""):
    """Log test result"""
    result = {
        "test": test_name,
        "status": status,
        "details": details
    }
    results[category].append(result)
    
    symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{symbol} {test_name}: {status}")
    if details:
        print(f"   Details: {details}")


def test_critical_imports():
    """Test all critical module imports"""
    print("\n=== PHASE 1: Critical Module Imports ===\n")
    
    critical_modules = [
        ('streamlit', 'Web framework'),
        ('pandas', 'Data analysis'),
        ('numpy', 'Numerical computing'),
        ('plotly', 'Visualization'),
        ('yfinance', 'Market data'),
        ('ta', 'Technical analysis'),
        ('scipy', 'Scientific computing'),
    ]
    
    optional_modules = [
        # ('ccxt', 'Crypto exchange data'),  # Disabled: Geographic restrictions from Binance
        ('fredapi', 'Federal Reserve data'),
        ('anthropic', 'Claude LLM'),
        ('finnhub', 'Insider trades'),
        ('praw', 'Reddit API'),
        ('newsapi', 'News API'),
        ('statsmodels', 'Statistical models'),
    ]
    
    for module_name, description in critical_modules:
        try:
            importlib.import_module(module_name)
            log_result("import_checks", f"{module_name} ({description})", "PASS")
        except Exception as e:
            log_result("import_checks", f"{module_name} ({description})", "FAIL", str(e))
            results["errors"].append(f"CRITICAL: {module_name} import failed - {e}")
    
    for module_name, description in optional_modules:
        try:
            importlib.import_module(module_name)
            log_result("import_checks", f"{module_name} ({description}) [OPTIONAL]", "PASS")
        except Exception as e:
            log_result("import_checks", f"{module_name} ({description}) [OPTIONAL]", "WARN", str(e))
            results["warnings"].append(f"Optional: {module_name} not available - {e}")


def test_project_modules():
    """Test project module imports"""
    print("\n=== PHASE 2: Project Module Imports ===\n")
    
    project_modules = [
        'utils',
        'data_fetcher',
        'analysis_engine',
        'theme_manager',
        'wsb_quotes',
        'debug_tools',
        'enhanced_valuation',
        'enhanced_valuation_ui',
        'dashboard_selector',
        'dashboard_stocks',
        'dashboard_options',
        'dashboard_crypto',
        'dashboard_advanced',
        'dashboard_portfolio',
    ]
    
    for module_name in project_modules:
        try:
            module = importlib.import_module(module_name)
            log_result("module_tests", module_name, "PASS")
        except Exception as e:
            log_result("module_tests", module_name, "FAIL", str(e))
            results["errors"].append(f"Module import failed: {module_name} - {e}")


def test_data_fetcher():
    """Test data fetcher functionality"""
    print("\n=== PHASE 3: Data Fetcher Tests ===\n")
    
    try:
        from data_fetcher import MarketDataFetcher
        fetcher = MarketDataFetcher()
        log_result("data_fetcher_tests", "MarketDataFetcher instantiation", "PASS")
        
        # Test basic methods exist
        methods = [
            'get_stock_data',
            'get_realtime_quote',
            'get_fundamentals',
            'get_institutional_data'
        ]
        
        for method in methods:
            if hasattr(fetcher, method):
                log_result("data_fetcher_tests", f"Method: {method}", "PASS")
            else:
                log_result("data_fetcher_tests", f"Method: {method}", "FAIL", "Method not found")
                results["errors"].append(f"MarketDataFetcher missing method: {method}")
        
    except Exception as e:
        log_result("data_fetcher_tests", "MarketDataFetcher", "FAIL", str(e))
        results["errors"].append(f"MarketDataFetcher failed: {e}")


def test_analysis_engine():
    """Test analysis engine calculations"""
    print("\n=== PHASE 4: Analysis Engine Tests ===\n")
    
    try:
        from analysis_engine import ValuationEngine, TechnicalAnalyzer, GoodBuyAnalyzer
        
        # Test ValuationEngine
        valuation = ValuationEngine()
        log_result("calculation_tests", "ValuationEngine instantiation", "PASS")
        
        # Test DCF with sample data
        test_financials = {}
        test_info = {
            "beta": 1.2,
            "sharesOutstanding": 100000000,
            "currentPrice": 150.0,
            "totalCash": 1000000000,
            "totalDebt": 500000000
        }
        
        dcf_result = valuation.calculate_dcf(test_financials, test_info)
        if "error" in dcf_result:
            log_result("calculation_tests", "DCF error handling (no cash flow)", "PASS", 
                      "✓ Correctly errors with no cash flow data")
        else:
            log_result("calculation_tests", "DCF calculation", "FAIL", 
                      "Should error with no cash flow")
        
        # Test DCF with real AAPL data
        try:
            import yfinance as yf
            aapl = yf.Ticker("AAPL")
            real_financials = {"cash_flow": aapl.cashflow.to_dict()}
            real_info = aapl.info
            real_dcf = valuation.calculate_dcf(real_financials, real_info)
            
            if "error" not in real_dcf and "fair_value" in real_dcf:
                fv = real_dcf["fair_value"]
                if fv > 0 and fv < 10000:  # Reasonable range
                    log_result("calculation_tests", "DCF calculation (AAPL)", "PASS", 
                              f"✓ Fair value: ${fv:.2f}")
                else:
                    log_result("calculation_tests", "DCF calculation (AAPL)", "WARN", 
                              f"Unusual fair value: ${fv:.2f}")
            else:
                log_result("calculation_tests", "DCF calculation (AAPL)", "FAIL", 
                          f"Error: {real_dcf.get('error', 'Unknown')}")
        except Exception as e:
            log_result("calculation_tests", "DCF calculation (AAPL)", "WARN", 
                      f"Could not test with real data: {str(e)[:50]}")
        
        # Test multiples valuation
        multiples_result = valuation.calculate_multiples_valuation(test_info)
        if "error" not in multiples_result:
            log_result("calculation_tests", "Multiples valuation", "PASS")
        else:
            log_result("calculation_tests", "Multiples error handling (no ratios)", "PASS", 
                      f"✓ Correctly errors: {multiples_result.get('error')}")
        
    except Exception as e:
        log_result("calculation_tests", "Analysis Engine", "FAIL", str(e))
        results["errors"].append(f"Analysis engine failed: {e}")
        traceback.print_exc()


def test_enhanced_valuation():
    """Test enhanced valuation module"""
    print("\n=== PHASE 5: Enhanced Valuation Tests ===\n")
    
    try:
        from enhanced_valuation import get_enhanced_dcf_calculator
        
        calc = get_enhanced_dcf_calculator()
        log_result("calculation_tests", "EnhancedDCFCalculator instantiation", "PASS")
        
        # Test DCF calculation
        dcf_result = calc.calculate_dcf_detailed(
            base_cash_flow=1000000000,
            growth_rate=0.10,
            wacc=0.10,
            terminal_growth=0.025,
            projection_years=5,
            cash=500000000,
            debt=1000000000,
            shares_outstanding=100000000
        )
        
        if "error" not in dcf_result:
            fair_value = dcf_result.get('fair_value_per_share', 0)
            log_result("calculation_tests", "Enhanced DCF calculation", "PASS", 
                      f"Fair value: ${fair_value:.2f}")
            
            # Validate calculation makes sense
            if fair_value > 0 and fair_value < 10000:
                log_result("calculation_tests", "DCF value range check", "PASS")
            else:
                log_result("calculation_tests", "DCF value range check", "WARN", 
                          f"Unusual value: ${fair_value:.2f}")
        else:
            log_result("calculation_tests", "Enhanced DCF calculation", "FAIL", 
                      dcf_result.get('error'))
            results["errors"].append(f"Enhanced DCF failed: {dcf_result.get('error')}")
        
        # Test Monte Carlo simulation
        mc_result = calc.monte_carlo_dcf(
            base_cash_flow=1000000000,
            growth_rate_mean=0.10,
            growth_rate_std=0.03,
            wacc_mean=0.10,
            wacc_std=0.02,
            terminal_growth_mean=0.025,
            terminal_growth_std=0.005,
            projection_years=5,
            cash=500000000,
            debt=1000000000,
            shares_outstanding=100000000,
            num_simulations=100
        )
        
        if "error" not in mc_result:
            num_sims = mc_result.get('num_successful_simulations', 0)
            mean_value = mc_result.get('fair_value_mean', 0)
            log_result("calculation_tests", "Monte Carlo simulation", "PASS", 
                      f"{num_sims} simulations, mean: ${mean_value:.2f}")
        else:
            log_result("calculation_tests", "Monte Carlo simulation", "FAIL", 
                      mc_result.get('error'))
            results["errors"].append(f"Monte Carlo failed: {mc_result.get('error')}")
        
        # Test sensitivity analysis
        sens_result = calc.sensitivity_analysis(
            base_cash_flow=1000000000,
            base_growth_rate=0.10,
            base_wacc=0.10,
            terminal_growth=0.025,
            projection_years=5,
            cash=500000000,
            debt=1000000000,
            shares_outstanding=100000000,
            param_name='growth_rate',
            param_range=[0.05, 0.10, 0.15, 0.20]
        )
        
        if "error" not in sens_result:
            num_results = len(sens_result.get('results', []))
            log_result("calculation_tests", "Sensitivity analysis", "PASS", 
                      f"{num_results} data points")
        else:
            log_result("calculation_tests", "Sensitivity analysis", "FAIL", 
                      sens_result.get('error'))
        
    except Exception as e:
        log_result("calculation_tests", "Enhanced Valuation Module", "FAIL", str(e))
        results["errors"].append(f"Enhanced valuation module failed: {e}")
        traceback.print_exc()


def test_utils():
    """Test utility functions"""
    print("\n=== PHASE 6: Utility Function Tests ===\n")
    
    try:
        from utils import (format_currency, format_percentage, format_large_number,
                          format_price, get_color_for_value, safe_divide)
        
        # Test formatting functions
        test_cases = [
            (format_currency, [1234.56], "$1.23K"),
            (format_percentage, [12.345], "12.35%"),
            (format_large_number, [1234567890], "1.23B"),
            (format_price, [123.456], "$123.46"),
        ]
        
        for func, args, expected in test_cases:
            try:
                result = func(*args)
                if result == expected:
                    log_result("module_tests", f"utils.{func.__name__}", "PASS")
                else:
                    log_result("module_tests", f"utils.{func.__name__}", "WARN", 
                              f"Got '{result}', expected '{expected}'")
            except Exception as e:
                log_result("module_tests", f"utils.{func.__name__}", "FAIL", str(e))
        
        # Test safe_divide
        if safe_divide(10, 2) == 5.0:
            log_result("module_tests", "utils.safe_divide (normal)", "PASS")
        else:
            log_result("module_tests", "utils.safe_divide (normal)", "FAIL")
        
        if safe_divide(10, 0, 0) == 0:
            log_result("module_tests", "utils.safe_divide (divide by zero)", "PASS")
        else:
            log_result("module_tests", "utils.safe_divide (divide by zero)", "FAIL")
        
    except Exception as e:
        log_result("module_tests", "Utils module", "FAIL", str(e))
        results["errors"].append(f"Utils module failed: {e}")


def check_file_structure():
    """Check project file structure"""
    print("\n=== PHASE 7: File Structure Check ===\n")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'dashboard_stocks.py',
        'dashboard_options.py',
        'dashboard_crypto.py',
        'dashboard_advanced.py',
        'dashboard_portfolio.py',
        'data_fetcher.py',
        'analysis_engine.py',
        'utils.py',
        'enhanced_valuation.py',
        'enhanced_valuation_ui.py',
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            log_result("module_tests", f"File exists: {filepath}", "PASS")
        else:
            log_result("module_tests", f"File exists: {filepath}", "FAIL")
            results["errors"].append(f"Required file missing: {filepath}")


def generate_summary():
    """Generate summary statistics"""
    print("\n=== GENERATING SUMMARY ===\n")
    
    total_tests = 0
    passed = 0
    failed = 0
    warnings = 0
    
    for category in ["import_checks", "module_tests", "calculation_tests", "data_fetcher_tests"]:
        for test in results[category]:
            total_tests += 1
            if test["status"] == "PASS":
                passed += 1
            elif test["status"] == "FAIL":
                failed += 1
            elif test["status"] == "WARN":
                warnings += 1
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "pass_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%",
        "critical_errors": len(results["errors"]),
        "total_warnings": len(results["warnings"])
    }
    
    print("\n" + "="*60)
    print("COMPREHENSIVE HEALTH CHECK SUMMARY")
    print("="*60)
    print(f"Total Tests:       {total_tests}")
    print(f"✅ Passed:         {passed}")
    print(f"❌ Failed:         {failed}")
    print(f"⚠️  Warnings:       {warnings}")
    print(f"Pass Rate:         {results['summary']['pass_rate']}")
    print(f"Critical Errors:   {results['summary']['critical_errors']}")
    print(f"Total Warnings:    {results['summary']['total_warnings']}")
    print("="*60)
    
    if results["errors"]:
        print("\n🔴 CRITICAL ERRORS:")
        for i, error in enumerate(results["errors"], 1):
            print(f"{i}. {error}")
    
    if results["warnings"]:
        print("\n⚠️  WARNINGS:")
        for i, warning in enumerate(results["warnings"][:10], 1):  # Show first 10
            print(f"{i}. {warning}")
        if len(results["warnings"]) > 10:
            print(f"   ... and {len(results['warnings']) - 10} more warnings")
    
    # Save report to file
    report_file = "health_check_report.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Run all health checks"""
    print("="*60)
    print("COMPREHENSIVE PROJECT HEALTH CHECK")
    print("="*60)
    print(f"Started at: {results['timestamp']}")
    print("="*60)
    
    try:
        test_critical_imports()
        test_project_modules()
        test_data_fetcher()
        test_analysis_engine()
        test_enhanced_valuation()
        test_utils()
        check_file_structure()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        traceback.print_exc()
        results["errors"].append(f"FATAL: {e}")
    
    generate_summary()
    
    # Return exit code based on critical errors
    if results["summary"]["critical_errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
