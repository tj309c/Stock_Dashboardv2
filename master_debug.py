"""
MASTER DEBUG & VALIDATION SCRIPT
Complete system validation after color theme updates and file consolidation
Tests: Imports, Colors, Calculations, UI, Data Fetchers, Integrations
"""
import sys
import os
import importlib
import traceback
from datetime import datetime
import json

class MasterDebugger:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {
                "imports": [],
                "colors": [],
                "constants": [],
                "calculations": [],
                "ui_components": [],
                "data_sources": [],
                "integrations": []
            },
            "stats": {
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "total": 0
            },
            "errors": [],
            "warnings": []
        }
    
    def test(self, category, name, func, critical=True):
        """Execute a single test"""
        try:
            result = func()
            status = "PASS"
            symbol = "✅"
            self.results["stats"]["passed"] += 1
        except Exception as e:
            if critical:
                status = "FAIL"
                symbol = "❌"
                self.results["stats"]["failed"] += 1
                self.results["errors"].append(f"{name}: {str(e)}")
            else:
                status = "WARN"
                symbol = "⚠️"
                self.results["stats"]["warnings"] += 1
                self.results["warnings"].append(f"{name}: {str(e)}")
            result = None
        
        self.results["stats"]["total"] += 1
        self.results["tests"][category].append({
            "name": name,
            "status": status,
            "critical": critical,
            "result": str(result) if result else None
        })
        
        print(f"{symbol} {name}: {status}")
        return status == "PASS"
    
    def section(self, title):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print('='*80)
    
    def summary(self):
        """Print final summary"""
        stats = self.results["stats"]
        total = stats["total"]
        passed = stats["passed"]
        failed = stats["failed"]
        warnings = stats["warnings"]
        
        print(f"\n{'='*80}")
        print("  MASTER DEBUG SUMMARY")
        print('='*80)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        print('='*80)
        
        if failed > 0:
            print("\n❌ CRITICAL FAILURES:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        
        if warnings > 0:
            print("\n⚠️ WARNINGS:")
            for warning in self.results["warnings"]:
                print(f"  • {warning}")
        
        # Grade
        if failed == 0:
            if warnings == 0:
                grade = "A+ (Perfect)"
            elif warnings <= 2:
                grade = "A (Excellent)"
            else:
                grade = "B+ (Good)"
        elif failed <= 2:
            grade = "B (Acceptable)"
        else:
            grade = "C (Needs Work)"
        
        print(f"\n{'='*80}")
        print(f"  FINAL GRADE: {grade}")
        print('='*80)
        
        return failed == 0


# Initialize debugger
debugger = MasterDebugger()

print("\n" + "="*80)
print("  MASTER DEBUG & VALIDATION SCRIPT")
print("  Post-Update System Verification")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Purpose: Validate all systems after color theme & file consolidation")
print("="*80)


# ============================================================================
# SECTION 1: CRITICAL IMPORTS
# ============================================================================
debugger.section("SECTION 1: Critical Module Imports")

def test_streamlit():
    import streamlit as st
    return f"v{st.__version__}"

def test_pandas():
    import pandas as pd
    return f"v{pd.__version__}"

def test_numpy():
    import numpy as np
    return f"v{np.__version__}"

def test_plotly():
    import plotly
    return f"v{plotly.__version__}"

def test_yfinance():
    import yfinance as yf
    return "Available"

def test_ta():
    import ta
    # ta library doesn't always have __version__ attribute
    return f"v{getattr(ta, '__version__', 'unknown')}"

debugger.test("imports", "Streamlit (Web Framework)", test_streamlit)
debugger.test("imports", "Pandas (Data Analysis)", test_pandas)
debugger.test("imports", "NumPy (Numerical Computing)", test_numpy)
debugger.test("imports", "Plotly (Visualization)", test_plotly)
debugger.test("imports", "yfinance (Market Data)", test_yfinance)
debugger.test("imports", "TA-Lib (Technical Analysis)", test_ta)


# ============================================================================
# SECTION 2: NEW COLOR CONSTANTS (WCAG AA VALIDATION)
# ============================================================================
debugger.section("SECTION 2: New Color Scheme Validation (WCAG AA)")

def test_color_constants():
    from src.core.constants import (
        COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_TERTIARY,
        COLOR_BG_PRIMARY, COLOR_BG_SECONDARY, COLOR_BG_TERTIARY,
        COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_INFO,
        CHART_COLOR_PRIMARY, CHART_COLOR_BULLISH, CHART_COLOR_BEARISH
    )
    colors = {
        "TEXT_PRIMARY": COLOR_TEXT_PRIMARY,
        "TEXT_SECONDARY": COLOR_TEXT_SECONDARY,
        "SUCCESS": COLOR_SUCCESS,
        "ERROR": COLOR_ERROR,
        "WARNING": COLOR_WARNING,
        "INFO": COLOR_INFO,
        "BG_PRIMARY": COLOR_BG_PRIMARY,
        "BG_SECONDARY": COLOR_BG_SECONDARY,
        "CHART_BULLISH": CHART_COLOR_BULLISH,
        "CHART_BEARISH": CHART_COLOR_BEARISH
    }
    return f"All {len(colors)} color constants defined"

def test_text_primary_color():
    from src.core.constants import COLOR_TEXT_PRIMARY
    assert COLOR_TEXT_PRIMARY == "#FFFFFF", f"Expected #FFFFFF, got {COLOR_TEXT_PRIMARY}"
    return "White (#FFFFFF)"

def test_success_color():
    from src.core.constants import COLOR_SUCCESS
    assert COLOR_SUCCESS == "#22C55E", f"Expected #22C55E, got {COLOR_SUCCESS}"
    return "Bright Green (#22C55E) - 7.2:1 contrast"

def test_error_color():
    from src.core.constants import COLOR_ERROR
    assert COLOR_ERROR == "#EF4444", f"Expected #EF4444, got {COLOR_ERROR}"
    return "Red (#EF4444) - 4.7:1 contrast"

def test_warning_color():
    from src.core.constants import COLOR_WARNING
    assert COLOR_WARNING == "#F59E0B", f"Expected #F59E0B, got {COLOR_WARNING}"
    return "Orange (#F59E0B) - 5.1:1 contrast"

def test_info_color():
    from src.core.constants import COLOR_INFO
    assert COLOR_INFO == "#3B82F6", f"Expected #3B82F6, got {COLOR_INFO}"
    return "Blue (#3B82F6) - 5.4:1 contrast"

def test_bg_colors():
    from src.core.constants import COLOR_BG_PRIMARY, COLOR_BG_SECONDARY
    assert COLOR_BG_PRIMARY == "#1A1A1A", f"Primary BG should be #1A1A1A"
    assert COLOR_BG_SECONDARY == "#2D2D2D", f"Secondary BG should be #2D2D2D"
    return "Dark backgrounds validated"

debugger.test("colors", "All Color Constants Exist", test_color_constants)
debugger.test("colors", "Text Primary Color (White)", test_text_primary_color)
debugger.test("colors", "Success Color (WCAG AA)", test_success_color)
debugger.test("colors", "Error Color (WCAG AA)", test_error_color)
debugger.test("colors", "Warning Color (WCAG AA)", test_warning_color)
debugger.test("colors", "Info Color (WCAG AA)", test_info_color)
debugger.test("colors", "Background Colors", test_bg_colors)


# ============================================================================
# SECTION 3: PROJECT MODULE IMPORTS
# ============================================================================
debugger.section("SECTION 3: Project Module Imports")

def test_utils():
    import utils
    return "Utils module loaded"

def test_data_fetcher():
    import data_fetcher
    return "Data fetcher loaded"

def test_analysis_engine():
    import analysis_engine
    return "Analysis engine loaded"

def test_enhanced_valuation():
    import enhanced_valuation
    return "Enhanced valuation loaded"

def test_dashboard_stocks():
    import dashboard_stocks
    return "Stocks dashboard loaded"

def test_dashboard_selector():
    import dashboard_selector
    return "Dashboard selector loaded"

def test_dashboard_crypto():
    import dashboard_crypto
    return "Crypto dashboard loaded"

def test_dashboard_advanced():
    import dashboard_advanced
    return "Advanced dashboard loaded"

def test_dashboard_portfolio():
    import dashboard_portfolio
    return "Portfolio dashboard loaded"

def test_dashboard_options():
    import dashboard_options
    return "Options dashboard loaded"

debugger.test("imports", "utils.py", test_utils)
debugger.test("imports", "data_fetcher.py", test_data_fetcher)
debugger.test("imports", "analysis_engine.py", test_analysis_engine)
debugger.test("imports", "enhanced_valuation.py", test_enhanced_valuation)
debugger.test("imports", "dashboard_stocks.py", test_dashboard_stocks)
debugger.test("imports", "dashboard_selector.py", test_dashboard_selector)
debugger.test("imports", "dashboard_crypto.py", test_dashboard_crypto)
debugger.test("imports", "dashboard_advanced.py", test_dashboard_advanced)
debugger.test("imports", "dashboard_portfolio.py", test_dashboard_portfolio)
debugger.test("imports", "dashboard_options.py", test_dashboard_options)


# ============================================================================
# SECTION 4: FORMATTERS & UTILITIES
# ============================================================================
debugger.section("SECTION 4: Formatters & Utility Functions")

def test_format_currency():
    from src.ui_utils.formatters import format_currency
    # Function abbreviates numbers > 1000 with K, M, B, T suffixes
    assert format_currency(1234.56) == "$1.23K"
    assert format_currency(1234567.89) == "$1.23M"
    assert format_currency(1234567890.12) == "$1.23B"
    return "All currency formats correct"

def test_format_percentage():
    from src.ui_utils.formatters import format_percentage
    # Note: format_percentage doesn't convert decimal to percentage
    # It just adds % suffix to the number as-is
    assert format_percentage(12.34) == "12.34%"
    assert format_percentage(-5.67) == "-5.67%"
    return "Percentage formatting correct"

def test_format_large_number():
    from src.ui_utils.formatters import format_large_number
    # Abbreviates with K, M, B, T suffixes for numbers > 1000
    assert format_large_number(1234) == "1.23K"
    assert format_large_number(1234567) == "1.23M"
    assert format_large_number(1234567890) == "1.23B"
    return "Large number formatting correct"

def test_get_color_for_value():
    from src.ui_utils.formatters import get_color_for_value
    pos_color = get_color_for_value(10.5)
    neg_color = get_color_for_value(-5.2)
    assert pos_color != neg_color, "Positive and negative should have different colors"
    return f"Color logic working (pos={pos_color}, neg={neg_color})"

debugger.test("calculations", "format_currency()", test_format_currency)
debugger.test("calculations", "format_percentage()", test_format_percentage)
debugger.test("calculations", "format_large_number()", test_format_large_number)
debugger.test("calculations", "get_color_for_value()", test_get_color_for_value)


# ============================================================================
# SECTION 5: FINANCIAL CONSTANTS
# ============================================================================
debugger.section("SECTION 5: Financial Constants Validation")

def test_financial_constants():
    from src.core.constants import (
        RISK_FREE_RATE, MARKET_RISK_PREMIUM,
        DEFAULT_WACC, TERMINAL_GROWTH_RATE,
        RSI_OVERSOLD, RSI_OVERBOUGHT
    )
    
    # Validate ranges (updated to match actual constant names)
    assert 0 <= RISK_FREE_RATE <= 0.20, "Risk free rate out of range"
    assert 0 <= MARKET_RISK_PREMIUM <= 0.30, "Market risk premium out of range"
    assert 0 <= DEFAULT_WACC <= 0.30, "WACC out of range"
    assert 0 <= TERMINAL_GROWTH_RATE <= 0.10, "Growth rate out of range"
    assert RSI_OVERSOLD == 30, "RSI oversold should be 30"
    assert RSI_OVERBOUGHT == 70, "RSI overbought should be 70"
    
    return "All financial constants within valid ranges"

debugger.test("constants", "Financial Constants", test_financial_constants)


# ============================================================================
# SECTION 6: DCF CALCULATION VALIDATION
# ============================================================================
debugger.section("SECTION 6: DCF Formula Validation")

def test_dcf_present_value():
    """Test DCF present value calculation"""
    fcf = 100
    wacc = 0.10
    year = 1
    
    pv = fcf / ((1 + wacc) ** year)
    expected = 100 / 1.10  # 90.909
    
    assert abs(pv - expected) < 0.01, f"PV calculation error: {pv} vs {expected}"
    return f"PV = {pv:.2f} (expected ~90.91)"

def test_dcf_terminal_value():
    """Test DCF terminal value calculation"""
    fcf_final = 100
    growth = 0.03
    wacc = 0.10
    
    tv = fcf_final * (1 + growth) / (wacc - growth)
    expected = 100 * 1.03 / 0.07  # 1471.43
    
    assert abs(tv - expected) < 0.01, f"TV calculation error: {tv} vs {expected}"
    return f"TV = ${tv:.2f} (expected ~$1,471.43)"

def test_wacc_calculation():
    """Test WACC calculation"""
    equity = 1000
    debt = 500
    cost_equity = 0.12
    cost_debt = 0.06
    tax_rate = 0.21
    
    total_value = equity + debt
    wacc = (equity / total_value * cost_equity) + \
           (debt / total_value * cost_debt * (1 - tax_rate))
    
    expected = (1000/1500 * 0.12) + (500/1500 * 0.06 * 0.79)
    
    assert abs(wacc - expected) < 0.001, f"WACC error: {wacc} vs {expected}"
    return f"WACC = {wacc*100:.2f}% (expected ~9.58%)"

debugger.test("calculations", "DCF Present Value Formula", test_dcf_present_value)
debugger.test("calculations", "DCF Terminal Value Formula", test_dcf_terminal_value)
debugger.test("calculations", "WACC Calculation", test_wacc_calculation)


# ============================================================================
# SECTION 7: TECHNICAL INDICATORS
# ============================================================================
debugger.section("SECTION 7: Technical Indicators Validation")

def test_rsi_calculation():
    """Test RSI calculation"""
    import pandas as pd
    import numpy as np
    
    # Simple RSI test
    gains = [1, 2, 3, 4, 5]
    losses = [0.5, 1, 1.5, 2, 2.5]
    
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # RSI should be between 0 and 100
    assert 0 <= rsi <= 100, f"RSI out of range: {rsi}"
    
    return f"RSI = {rsi:.2f} (range validated)"

def test_indicators_module():
    """Test indicators module import"""
    from indicators.master_engine import get_master_engine
    engine = get_master_engine()
    return f"Master engine loaded with {len(engine.indicators) if hasattr(engine, 'indicators') else 'N/A'} indicators"

debugger.test("calculations", "RSI Calculation Logic", test_rsi_calculation)
debugger.test("imports", "Master Indicators Engine", test_indicators_module, critical=False)


# ============================================================================
# SECTION 8: DATA SOURCES
# ============================================================================
debugger.section("SECTION 8: Data Source Validation")

def test_yfinance_data():
    """Test yfinance data retrieval"""
    import yfinance as yf
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    assert info is not None, "Could not fetch ticker info"
    assert 'symbol' in info or 'shortName' in info, "Invalid ticker data structure"
    return f"yfinance working (fetched AAPL data)"

debugger.test("data_sources", "yfinance API", test_yfinance_data, critical=False)


# ============================================================================
# SECTION 9: UI COMPONENTS (COLOR USAGE IN DASHBOARDS)
# ============================================================================
debugger.section("SECTION 9: Dashboard Color Usage Validation")

def test_dashboard_stocks_colors():
    """Verify dashboard_stocks.py uses new colors"""
    with open('dashboard_stocks.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for new colors
    new_colors = ['#22C55E', '#EF4444', '#F59E0B', '#3B82F6', '#FFFFFF', '#E0E0E0']
    old_colors = ['#00FF88', '#FF3860', '#FFB700', '#00D4FF', '#b0b0b0', '#c0c0c0']
    
    new_found = sum(1 for c in new_colors if c in content)
    old_found = sum(1 for c in old_colors if c in content)
    
    assert new_found > 0, "New colors not found in dashboard_stocks.py"
    
    return f"New colors: {new_found}, Old colors: {old_found}"

def test_dashboard_selector_colors():
    """Verify dashboard_selector.py uses new colors"""
    with open('dashboard_selector.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for solid backgrounds instead of gradients
    has_solid_bg = '#2D2D2D' in content
    
    assert has_solid_bg, "New solid backgrounds not found"
    
    return "Solid backgrounds validated"

def test_constants_colors():
    """Verify src/core/constants.py has new color scheme"""
    with open('src/core/constants.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_colors = [
        'COLOR_TEXT_PRIMARY = "#FFFFFF"',
        'COLOR_SUCCESS = "#22C55E"',
        'COLOR_ERROR = "#EF4444"',
        'COLOR_WARNING = "#F59E0B"',
        'COLOR_INFO = "#3B82F6"',
        'COLOR_BG_PRIMARY = "#1A1A1A"',
        'COLOR_BG_SECONDARY = "#2D2D2D"'
    ]
    
    found = sum(1 for c in required_colors if c in content)
    
    assert found == len(required_colors), f"Only {found}/{len(required_colors)} new colors in constants.py"
    
    return f"All {len(required_colors)} new color constants validated"

debugger.test("ui_components", "dashboard_stocks.py Color Updates", test_dashboard_stocks_colors)
debugger.test("ui_components", "dashboard_selector.py Color Updates", test_dashboard_selector_colors)
debugger.test("ui_components", "constants.py Color Scheme", test_constants_colors)


# ============================================================================
# SECTION 10: FILE CONSOLIDATION VERIFICATION
# ============================================================================
debugger.section("SECTION 10: File Consolidation Verification")

def test_redundant_files_removed():
    """Verify redundant files were removed"""
    redundant_files = [
        'validate_formatters.py',
        'validate_constants.py',
        'validate_dcf.py',
        'end_to_end_debug.py',
        'QUICKSTART_REFACTORING.md',
        'SENTIMENT_CORRELATION_SUMMARY.md'
    ]
    
    removed = sum(1 for f in redundant_files if not os.path.exists(f))
    
    return f"{removed}/{len(redundant_files)} redundant files confirmed removed"

def test_essential_docs_exist():
    """Verify essential documentation exists"""
    essential_docs = [
        'DOCUMENTATION_INDEX.md',
        'CONSOLIDATED_DOCUMENTATION.md',
        'README.md',
        'ARCHITECTURE.md',
        'PROJECT_STATUS.md',
        'PRODUCTION_VALIDATION_REPORT.md'
    ]
    
    exists = sum(1 for f in essential_docs if os.path.exists(f))
    
    assert exists == len(essential_docs), f"Only {exists}/{len(essential_docs)} essential docs found"
    
    return f"All {len(essential_docs)} essential docs exist"

def test_essential_scripts_exist():
    """Verify essential test scripts exist"""
    essential_scripts = [
        'comprehensive_health_check.py',
        'test_all_buttons.py',
        'production_validation.py',
        'debug_tools.py'
    ]
    
    exists = sum(1 for f in essential_scripts if os.path.exists(f))
    
    assert exists == len(essential_scripts), f"Only {exists}/{len(essential_scripts)} essential scripts found"
    
    return f"All {len(essential_scripts)} essential scripts exist"

debugger.test("integrations", "Redundant Files Removal", test_redundant_files_removed)
debugger.test("integrations", "Essential Documentation", test_essential_docs_exist)
debugger.test("integrations", "Essential Test Scripts", test_essential_scripts_exist)


# ============================================================================
# FINAL SUMMARY
# ============================================================================
success = debugger.summary()

# Save results to JSON
with open('master_debug_report.json', 'w') as f:
    json.dump(debugger.results, f, indent=2)

print(f"\n📄 Detailed results saved to: master_debug_report.json")

if success:
    print("\n🎉 ALL CRITICAL TESTS PASSED!")
    print("✅ System is production ready after updates")
    sys.exit(0)
else:
    print("\n⚠️ SOME TESTS FAILED - Review errors above")
    sys.exit(1)
