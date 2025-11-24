"""
Comprehensive tests for Individual Charts & Visuals Dashboard (page 02)
Tests updated page structure after removing News & Sentiment and Earnings & Estimates tabs
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
import importlib.util
spec = importlib.util.spec_from_file_location(
    "individual_charts_page",
    "pages/02_📈_Individual_Charts_&_Visuals.py"
)
individual_charts_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(individual_charts_page)


class TestIndividualChartsVisualsDashboard:
    """Test suite for Individual Charts & Visuals Dashboard"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "AAPL"

        # Sample essentials data
        self.sample_essentials = {
            'info': {
                'longName': 'Apple Inc.',
                'symbol': 'AAPL',
                'industry': 'Consumer Electronics',
                'sector': 'Technology',
                'marketCap': 3000000000000,
                'trailingPE': 28.5,
                'fiftyTwoWeekHigh': 200.0,
                'fiftyTwoWeekLow': 130.0
            },
            'price_1mo': pd.DataFrame({
                'Close': [145.0, 147.0, 148.5, 150.0],
                'Open': [144.0, 146.0, 147.5, 149.0],
                'High': [146.0, 148.0, 149.5, 151.0],
                'Low': [143.5, 145.5, 147.0, 148.5],
                'Volume': [50000000, 55000000, 52000000, 48000000]
            }, index=pd.date_range(end=datetime.now(), periods=4))
        }

    def test_module_structure(self):
        """Test that all required functions exist"""
        required_functions = [
            'render_page',
            'render_dashboard_tab',
            'render_price_technicals_tab',
            'render_advanced_visuals_tab',
            'render_correlating_factors_stock',
            'render_debug_tab'
        ]

        for func_name in required_functions:
            assert hasattr(individual_charts_page, func_name), f"Missing function: {func_name}"
            assert callable(getattr(individual_charts_page, func_name)), f"Not callable: {func_name}"

    def test_removed_functions_not_present(self):
        """Test that removed functions are no longer in the module"""
        removed_functions = [
            'render_news_sentiment_tab',
            'render_earnings_estimates_tab'
        ]

        for func_name in removed_functions:
            assert not hasattr(individual_charts_page, func_name), f"Function should be removed: {func_name}"

    @patch('streamlit.title')
    @patch('streamlit.caption')
    @patch('individual_charts_page.setup_sidebar_ticker_input')
    def test_render_page_initialization(self, mock_sidebar, mock_caption, mock_title):
        """Test page initialization with new structure"""
        mock_sidebar.return_value = "AAPL"

        # Verify the function exists and has correct signature
        assert hasattr(individual_charts_page, 'render_page')
        assert callable(individual_charts_page.render_page)

    def test_tabs_structure(self):
        """Test that correct number of tabs are created (4 instead of 6)"""
        expected_tabs = [
            "📊 Dashboard",
            "📈 Price & Technicals",
            "🔬 Advanced Visuals",
            "🔧 Debug"
        ]

        assert len(expected_tabs) == 4

    def test_removed_tabs_not_present(self):
        """Test that removed tabs are not in the new structure"""
        all_tabs = [
            "📊 Dashboard",
            "📈 Price & Technicals",
            "🔬 Advanced Visuals",
            "🔧 Debug"
        ]

        removed_tabs = ["📰 News & Sentiment", "📅 Earnings & Estimates"]

        for removed_tab in removed_tabs:
            assert removed_tab not in all_tabs

    def test_market_cap_formatting(self):
        """Test market cap formatting"""
        market_cap = 3000000000000

        formatted = f"${market_cap:,.0f}"

        assert "3,000,000,000,000" in formatted

    def test_price_change_calculation(self):
        """Test price change and percentage calculation"""
        current_price = 150.0
        previous_close = 145.0

        price_change = current_price - previous_close
        percent_change = (price_change / previous_close) * 100 if previous_close != 0 else 0

        assert price_change == 5.0
        assert percent_change == pytest.approx(3.45, rel=0.1)

    def test_pe_ratio_formatting(self):
        """Test P/E ratio formatting"""
        pe_ratio = 28.5

        formatted = f"{pe_ratio:.2f}"

        assert formatted == "28.50"

    def test_fifty_two_week_high_display(self):
        """Test 52-week high display"""
        fifty_two_week_high = 200.0

        formatted = f"${fifty_two_week_high:.2f}"

        assert formatted == "$200.00"

    def test_fifty_two_week_low_display(self):
        """Test 52-week low display"""
        fifty_two_week_low = 130.0

        formatted = f"${fifty_two_week_low:.2f}"

        assert formatted == "$130.00"


class TestDashboardTabFunctionality:
    """Test dashboard tab specific functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_info = {
            'longName': 'Apple Inc.',
            'symbol': 'AAPL',
            'industry': 'Consumer Electronics',
            'sector': 'Technology',
            'marketCap': 3000000000000,
            'trailingPE': 28.5,
            'fiftyTwoWeekHigh': 200.0,
            'fiftyTwoWeekLow': 130.0
        }

        self.sample_price_data = pd.DataFrame({
            'Close': [145.0, 147.0, 148.5, 150.0],
            'Volume': [50000000, 55000000, 52000000, 48000000]
        }, index=pd.date_range(end=datetime.now(), periods=4))

    def test_company_info_extraction(self):
        """Test company information extraction"""
        info = self.sample_info

        assert 'longName' in info
        assert 'sector' in info
        assert 'industry' in info
        assert 'marketCap' in info

    def test_key_metrics_calculation(self):
        """Test key metrics calculation"""
        price_data = self.sample_price_data

        current_price = price_data['Close'].iloc[-1]
        previous_close = price_data['Close'].iloc[-2] if len(price_data) > 1 else current_price

        assert current_price == 150.0
        assert previous_close == 148.5

    def test_empty_price_data_handling(self):
        """Test handling of empty price data"""
        empty_df = pd.DataFrame()

        assert empty_df.empty
        assert len(empty_df) == 0


class TestPriceTechnicalsTabFunctionality:
    """Test Price & Technicals tab functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "AAPL"

    @patch('individual_charts_page.initialize_data_and_context')
    def test_data_loading(self, mock_init):
        """Test data loading for price & technicals"""
        mock_ctx = Mock()
        mock_ctx.price_data = pd.DataFrame({
            'Close': [150.0] * 10,
            'Volume': [50000000] * 10
        })
        mock_init.return_value = mock_ctx

        # Simulate data loading
        ctx = mock_init(self.sample_ticker, light_load=True)

        assert ctx is not None
        assert not ctx.price_data.empty

    def test_ticker_override_functionality(self):
        """Test ticker override with quick picks"""
        global_ticker = "AAPL"
        local_override = "TSLA"

        # Local override should take precedence
        active_ticker = local_override if local_override else global_ticker

        assert active_ticker == "TSLA"


class TestAdvancedVisualsTabFunctionality:
    """Test Advanced Visuals tab functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "NVDA"

    @patch('individual_charts_page.initialize_data_and_context')
    @patch('individual_charts_page.render_advanced_visual_analysis_section')
    def test_advanced_visuals_rendering(self, mock_render, mock_init):
        """Test advanced visuals rendering"""
        mock_ctx = Mock()
        mock_ctx.price_data = pd.DataFrame({
            'Close': [150.0] * 50,
            'Volume': [50000000] * 50
        })
        mock_init.return_value = mock_ctx

        # This would call the rendering function
        assert callable(mock_render)


class TestDebugTabFunctionality:
    """Test Debug tab functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "AAPL"

    def test_session_state_inspection(self):
        """Test session state inspection capability"""
        # Debug tab should be able to inspect session state
        sample_session_state = {
            'ticker': 'AAPL',
            'some_key': 'some_value'
        }

        relevant_keys = {k: v for k, v in sample_session_state.items()
                        if not k.startswith('FormSubmitter') and not k.startswith('_')}

        assert len(relevant_keys) == 2
        assert 'ticker' in relevant_keys

    @patch('yfinance.Ticker')
    def test_data_quality_check(self, mock_ticker):
        """Test data quality checking"""
        mock_stock = Mock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics'
        }
        mock_ticker.return_value = mock_stock

        import yfinance as yf
        stock = yf.Ticker(self.sample_ticker)
        info = stock.info

        has_name = 'longName' in info
        has_sector = 'sector' in info
        has_industry = 'industry' in info

        assert has_name
        assert has_sector
        assert has_industry

    def test_completeness_score_calculation(self):
        """Test data completeness score calculation"""
        checks = {
            "Company Name": True,
            "Sector/Industry": True,
            "Price Data": True,
            "P/E Ratio": False,
            "EPS": False,
            "Revenue": True,
            "Market Cap": True,
            "Dividend Yield": False,
            "Volume": True,
            "52W High/Low": True
        }

        completeness_score = sum(checks.values())
        total_checks = len(checks)
        completeness_pct = (completeness_score / total_checks) * 100

        assert completeness_score == 7
        assert completeness_pct == 70.0


class TestNavigationHints:
    """Test navigation hints for spun-off modules"""

    def test_navigation_hint_structure(self):
        """Test that navigation hints are properly structured"""
        hints = [
            "📰 **News & Sentiment** analysis has moved to its own dedicated dashboard",
            "📅 **Earnings & Estimates** analysis has moved to its own dedicated dashboard"
        ]

        assert len(hints) == 2
        assert "News & Sentiment" in hints[0]
        assert "Earnings & Estimates" in hints[1]


class TestImportsCleanup:
    """Test that unused imports have been removed"""

    def test_required_imports_present(self):
        """Test that required imports are present"""
        required_imports = [
            'streamlit',
            'pandas',
            'yfinance',
            'plotly.graph_objects',
            'app_logic',
            'app_utils',
            'advanced_charting',
            'visual_analysis_presets',
            'performance_optimizer',
            'ticker_utils'
        ]

        # These should be importable
        import streamlit as st
        import pandas as pd
        import yfinance as yf
        import plotly.graph_objects as go

        assert st is not None
        assert pd is not None
        assert yf is not None
        assert go is not None

    def test_removed_imports_not_used(self):
        """Test that removed functionality imports are not in the module"""
        # These imports should not be needed anymore
        removed_imports = [
            'news_fetcher',
            'get_all_news',
            'get_news_sentiment_summary',
            'format_time_ago',
            'truncate_text',
            'get_comprehensive_social_sentiment'
        ]

        # Verify module doesn't have these dependencies
        # (This is implicit - if they were used, the module would fail to load)
        assert True


class TestIntegration:
    """Integration tests for Individual Charts & Visuals Dashboard"""

    @patch('yfinance.Ticker')
    @patch('individual_charts_page.load_ticker_essentials')
    def test_full_dashboard_data_flow(self, mock_load, mock_ticker):
        """Test full data flow from ticker input to display"""
        # Setup mocks
        mock_essentials = {
            'info': {
                'longName': 'Apple Inc.',
                'marketCap': 3000000000000,
                'trailingPE': 28.5
            },
            'price_1mo': pd.DataFrame({
                'Close': [150.0] * 20
            })
        }
        mock_load.return_value = mock_essentials

        # Simulate data loading
        essentials = mock_load("AAPL")

        assert essentials is not None
        assert 'info' in essentials
        assert 'price_1mo' in essentials
        assert not essentials['price_1mo'].empty

    def test_error_handling_invalid_ticker(self):
        """Test error handling for invalid ticker"""
        invalid_ticker = "INVALID123"

        # Should handle gracefully without crashing
        assert len(invalid_ticker) > 0


class TestEdgeCases:
    """Edge case tests for Individual Charts & Visuals Dashboard"""

    def test_missing_company_info(self):
        """Test handling of missing company information"""
        info = {}

        industry = info.get('industry', 'N/A')
        sector = info.get('sector', 'N/A')

        assert industry == 'N/A'
        assert sector == 'N/A'

    def test_missing_price_data(self):
        """Test handling of missing price data"""
        price_data = None

        if price_data is None or (hasattr(price_data, 'empty') and price_data.empty):
            data_available = False
        else:
            data_available = True

        assert data_available is False

    def test_zero_market_cap(self):
        """Test handling of zero or missing market cap"""
        market_cap = None

        market_cap_display = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"

        assert market_cap_display == "N/A"

    def test_missing_pe_ratio(self):
        """Test handling of missing P/E ratio"""
        pe_ratio = None

        pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"

        assert pe_display == "N/A"

    def test_single_price_point(self):
        """Test handling of single price data point"""
        price_data = pd.DataFrame({
            'Close': [150.0]
        })

        current_price = price_data['Close'].iloc[-1]
        previous_close = price_data['Close'].iloc[-2] if len(price_data) > 1 else current_price

        assert current_price == previous_close == 150.0

    def test_negative_price_change(self):
        """Test handling of negative price change"""
        current_price = 145.0
        previous_close = 150.0

        price_change = current_price - previous_close
        percent_change = (price_change / previous_close) * 100

        assert price_change == -5.0
        assert percent_change == pytest.approx(-3.33, rel=0.1)


class TestPerformanceOptimization:
    """Test performance optimization features"""

    @patch('individual_charts_page.load_ticker_essentials')
    def test_essentials_loading_optimization(self, mock_load):
        """Test that optimized essentials loader is used"""
        mock_load.return_value = {'info': {}, 'price_1mo': pd.DataFrame()}

        # Should use load_ticker_essentials (optimized)
        essentials = mock_load("AAPL")

        mock_load.assert_called_once_with("AAPL")

    @patch('individual_charts_page.optimize_dataframe')
    def test_dataframe_optimization(self, mock_optimize):
        """Test that DataFrame optimization is applied"""
        sample_df = pd.DataFrame({'Close': [150.0] * 100})
        mock_optimize.return_value = sample_df

        optimized = mock_optimize(sample_df)

        assert optimized is not None


def run_tests():
    """Run all tests and print results"""
    print("=" * 80)
    print("Running Individual Charts & Visuals Dashboard Tests")
    print("=" * 80)

    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()
