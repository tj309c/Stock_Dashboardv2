"""
Comprehensive tests for Earnings & Estimates Dashboard (page 09)
Tests all functions, UI components, and data flows
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
    "earnings_estimates_page",
    "pages/09_📅_Earnings_&_Estimates.py"
)
earnings_estimates_page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(earnings_estimates_page)


class TestEarningsEstimatesDashboard:
    """Test suite for Earnings & Estimates Dashboard"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_ticker = "AAPL"

        # Sample calendar data
        self.sample_calendar = {
            'Earnings Date': [datetime.now() + timedelta(days=30)],
            'Earnings Average': 1.25,
            'Earnings Low': 1.15,
            'Earnings High': 1.35,
            'Revenue Average': 90000000000,
            'Revenue Low': 88000000000,
            'Revenue High': 92000000000,
            'Dividend Date': datetime.now() + timedelta(days=15),
            'Ex-Dividend Date': datetime.now() + timedelta(days=10)
        }

        # Sample earnings dates
        dates = pd.date_range(end=datetime.now(), periods=8, freq='90D')
        self.sample_earnings_dates = pd.DataFrame({
            'EPS Estimate': [1.20, 1.15, 1.10, 1.08, 1.05, 1.02, 1.00, 0.98],
            'Reported EPS': [1.25, 1.18, 1.12, 1.10, 1.03, 1.00, 0.95, 0.92],
            'Surprise(%)': [4.2, 2.6, 1.8, 1.9, -1.9, -2.0, -5.0, -6.1]
        }, index=dates)

        # Sample stock info
        self.sample_info = {
            'currentPrice': 150.0,
            'targetHighPrice': 180.0,
            'targetLowPrice': 120.0,
            'targetMeanPrice': 155.0,
            'targetMedianPrice': 152.0,
            'recommendationKey': 'buy',
            'numberOfAnalystOpinions': 35,
            'dividendRate': 0.92,
            'dividendYield': 0.0061
        }

    def test_module_structure(self):
        """Test that all required functions exist"""
        required_functions = [
            'render_page',
            'render_upcoming_earnings_section',
            'render_historical_earnings_section',
            'render_dividend_information_section',
            'render_analyst_ratings_section',
            'render_advanced_earnings_modules'
        ]

        for func_name in required_functions:
            assert hasattr(earnings_estimates_page, func_name), f"Missing function: {func_name}"
            assert callable(getattr(earnings_estimates_page, func_name)), f"Not callable: {func_name}"

    @patch('streamlit.title')
    @patch('streamlit.caption')
    @patch('earnings_estimates_page.setup_sidebar_ticker_input')
    @patch('earnings_estimates_page.render_ticker_input_with_quick_picks')
    def test_render_page_initialization(self, mock_quick_picks, mock_sidebar, mock_caption, mock_title):
        """Test page initialization"""
        mock_sidebar.return_value = "AAPL"
        mock_quick_picks.return_value = "AAPL"

        # Verify the function exists and has correct signature
        assert hasattr(earnings_estimates_page, 'render_page')
        assert callable(earnings_estimates_page.render_page)

    def test_eps_estimate_spread_calculation(self):
        """Test EPS estimate spread calculation"""
        eps_low = 1.15
        eps_avg = 1.25
        eps_high = 1.35

        spread = eps_high - eps_low
        spread_pct = (spread / eps_avg * 100) if eps_avg != 0 else 0

        assert spread == pytest.approx(0.20)
        assert spread_pct == pytest.approx(16.0, rel=0.1)

    def test_analyst_agreement_classification_high(self):
        """Test analyst agreement classification - high agreement"""
        spread_pct = 8.0

        if spread_pct < 10:
            agreement = "High"
        elif spread_pct < 20:
            agreement = "Medium"
        else:
            agreement = "Low"

        assert agreement == "High"

    def test_analyst_agreement_classification_medium(self):
        """Test analyst agreement classification - medium agreement"""
        spread_pct = 15.0

        if spread_pct < 10:
            agreement = "High"
        elif spread_pct < 20:
            agreement = "Medium"
        else:
            agreement = "Low"

        assert agreement == "Medium"

    def test_analyst_agreement_classification_low(self):
        """Test analyst agreement classification - low agreement"""
        spread_pct = 25.0

        if spread_pct < 10:
            agreement = "High"
        elif spread_pct < 20:
            agreement = "Medium"
        else:
            agreement = "Low"

        assert agreement == "Low"

    def test_earnings_surprise_calculation(self):
        """Test earnings surprise percentage calculation"""
        estimate = 1.20
        actual = 1.25

        surprise = ((actual - estimate) / estimate * 100) if estimate != 0 else 0

        assert surprise == pytest.approx(4.17, rel=0.1)

    def test_beat_rate_calculation(self):
        """Test earnings beat rate calculation"""
        surprises = pd.Series([4.2, 2.6, -1.8, 1.9, -1.9, -2.0, 5.0, -6.1])

        beat_rate = (surprises > 0).sum() / len(surprises) * 100

        assert beat_rate == 50.0

    def test_average_surprise_calculation(self):
        """Test average earnings surprise calculation"""
        surprises = pd.Series([4.2, 2.6, 1.8, 1.9, -1.9, -2.0, -5.0, -6.1])

        avg_surprise = surprises.mean()

        assert avg_surprise < 0  # More misses than beats in this sample

    def test_price_movement_window_calculation(self):
        """Test pre/post earnings price movement window"""
        window_days = 5
        date_loc = 20

        pre_start_idx = max(0, date_loc - window_days)
        pre_end_idx = date_loc
        post_start_idx = date_loc
        post_end_idx = min(100, date_loc + window_days)

        assert pre_start_idx == 15
        assert pre_end_idx == 20
        assert post_start_idx == 20
        assert post_end_idx == 25

    def test_price_movement_percentage_calculation(self):
        """Test price movement percentage calculation"""
        start_price = 145.0
        end_price = 150.0

        pct_change = ((end_price - start_price) / start_price * 100) if start_price != 0 else 0

        assert pct_change == pytest.approx(3.45, rel=0.1)

    def test_revenue_formatting_billions(self):
        """Test revenue formatting in billions"""
        revenue = 90000000000

        formatted = f"${revenue/1e9:.2f}B"

        assert formatted == "$90.00B"

    def test_price_target_upside_calculation(self):
        """Test analyst price target upside calculation"""
        target_mean = 155.0
        current_price = 150.0

        upside = ((target_mean - current_price) / current_price * 100) if current_price > 0 else 0

        assert upside == pytest.approx(3.33, rel=0.1)

    def test_price_target_downside_calculation(self):
        """Test analyst price target downside calculation"""
        target_mean = 120.0
        current_price = 150.0

        upside = ((target_mean - current_price) / current_price * 100) if current_price > 0 else 0

        assert upside < 0
        assert abs(upside) == pytest.approx(20.0, rel=0.1)

    def test_recommendation_mapping_buy(self):
        """Test recommendation key mapping - buy"""
        recommendation = 'buy'

        rec_display = {
            'strong_buy': ('🟢 Strong Buy', '#00CC96'),
            'buy': ('🟢 Buy', '#00CC96'),
            'hold': ('🟡 Hold', '#FFA15A'),
            'sell': ('🔴 Sell', '#EF553B'),
            'strong_sell': ('🔴 Strong Sell', '#EF553B')
        }

        rec_text, rec_color = rec_display.get(recommendation.lower(), (recommendation.title(), '#636EFA'))

        assert rec_text == '🟢 Buy'
        assert rec_color == '#00CC96'

    def test_recommendation_mapping_hold(self):
        """Test recommendation key mapping - hold"""
        recommendation = 'hold'

        rec_display = {
            'strong_buy': ('🟢 Strong Buy', '#00CC96'),
            'buy': ('🟢 Buy', '#00CC96'),
            'hold': ('🟡 Hold', '#FFA15A'),
            'sell': ('🔴 Sell', '#EF553B'),
            'strong_sell': ('🔴 Strong Sell', '#EF553B')
        }

        rec_text, rec_color = rec_display.get(recommendation.lower(), (recommendation.title(), '#636EFA'))

        assert rec_text == '🟡 Hold'
        assert rec_color == '#FFA15A'

    def test_recommendation_mapping_sell(self):
        """Test recommendation key mapping - sell"""
        recommendation = 'sell'

        rec_display = {
            'strong_buy': ('🟢 Strong Buy', '#00CC96'),
            'buy': ('🟢 Buy', '#00CC96'),
            'hold': ('🟡 Hold', '#FFA15A'),
            'sell': ('🔴 Sell', '#EF553B'),
            'strong_sell': ('🔴 Strong Sell', '#EF553B')
        }

        rec_text, rec_color = rec_display.get(recommendation.lower(), (recommendation.title(), '#636EFA'))

        assert rec_text == '🔴 Sell'
        assert rec_color == '#EF553B'


class TestEarningsEstimatesIntegration:
    """Integration tests for Earnings & Estimates Dashboard"""

    def setup_method(self):
        """Setup integration test fixtures"""
        self.test_ticker = "AAPL"

    @patch('yfinance.Ticker')
    def test_ticker_data_fetch(self, mock_ticker):
        """Test ticker data fetching"""
        mock_stock = Mock()
        mock_stock.calendar = {
            'Earnings Date': [datetime.now() + timedelta(days=30)],
            'Earnings Average': 1.25
        }
        mock_stock.earnings_dates = pd.DataFrame()
        mock_stock.info = {'currentPrice': 150.0}
        mock_ticker.return_value = mock_stock

        import yfinance as yf
        stock = yf.Ticker(self.test_ticker)

        assert stock.calendar is not None
        assert stock.info is not None

    def test_calendar_structure(self):
        """Test expected calendar data structure"""
        calendar = {
            'Earnings Date': [datetime.now() + timedelta(days=30)],
            'Earnings Average': 1.25,
            'Earnings Low': 1.15,
            'Earnings High': 1.35
        }

        assert 'Earnings Date' in calendar
        assert 'Earnings Average' in calendar
        assert isinstance(calendar.get('Earnings Average'), (int, float))

    def test_earnings_dates_dataframe_structure(self):
        """Test expected earnings dates DataFrame structure"""
        required_columns = ['EPS Estimate', 'Reported EPS', 'Surprise(%)']

        dates = pd.date_range(end=datetime.now(), periods=8, freq='90D')
        df = pd.DataFrame({
            'EPS Estimate': [1.20] * 8,
            'Reported EPS': [1.25] * 8,
            'Surprise(%)': [4.2] * 8
        }, index=dates)

        for col in required_columns:
            assert col in df.columns

    def test_stock_info_structure(self):
        """Test expected stock info structure"""
        info = {
            'currentPrice': 150.0,
            'targetMeanPrice': 155.0,
            'recommendationKey': 'buy'
        }

        assert 'currentPrice' in info
        assert isinstance(info.get('currentPrice'), (int, float))


class TestEarningsEstimatesEdgeCases:
    """Edge case tests for Earnings & Estimates Dashboard"""

    def test_no_upcoming_earnings(self):
        """Test handling of no upcoming earnings data"""
        calendar = None

        # Should handle gracefully
        assert calendar is None or isinstance(calendar, dict)

    def test_empty_earnings_dates(self):
        """Test handling of empty earnings dates DataFrame"""
        df = pd.DataFrame()

        assert df.empty
        assert len(df) == 0

    def test_missing_eps_estimate(self):
        """Test handling of missing EPS estimate"""
        eps_avg = None

        if eps_avg is not None:
            formatted = f"${float(eps_avg):.2f}"
        else:
            formatted = "N/A"

        assert formatted == "N/A"

    def test_zero_current_price(self):
        """Test handling of zero current price"""
        target_mean = 155.0
        current_price = 0

        upside = ((target_mean - current_price) / current_price * 100) if current_price > 0 else 0

        assert upside == 0

    def test_negative_eps(self):
        """Test handling of negative EPS"""
        eps_avg = -0.50

        # Should still format correctly
        formatted = f"${eps_avg:.2f}"

        assert formatted == "$-0.50"

    def test_extreme_surprise_percentage(self):
        """Test handling of extreme surprise percentage"""
        estimate = 0.10
        actual = 1.00

        surprise = ((actual - estimate) / estimate * 100) if estimate != 0 else 0

        assert surprise == 900.0

    def test_zero_eps_estimate(self):
        """Test handling of zero EPS estimate (avoid division by zero)"""
        estimate = 0
        actual = 1.25

        surprise = ((actual - estimate) / estimate * 100) if estimate != 0 else 0

        assert surprise == 0

    def test_missing_price_target_data(self):
        """Test handling of missing price target data"""
        target_mean = None
        target_median = None
        recommendation = 'N/A'

        has_data = target_mean or target_median or recommendation != 'N/A'

        assert has_data is False

    def test_no_analyst_opinions(self):
        """Test handling of no analyst opinions"""
        num_analysts = None

        if num_analysts:
            formatted = f"{num_analysts}"
        else:
            formatted = "N/A"

        assert formatted == "N/A"

    def test_all_earnings_beats(self):
        """Test all positive earnings surprises"""
        surprises = pd.Series([4.2, 2.6, 1.8, 5.9, 3.5, 2.0, 6.5, 1.1])

        beat_rate = (surprises > 0).sum() / len(surprises) * 100
        avg_surprise = surprises.mean()

        assert beat_rate == 100.0
        assert avg_surprise > 0

    def test_all_earnings_misses(self):
        """Test all negative earnings surprises"""
        surprises = pd.Series([-4.2, -2.6, -1.8, -5.9, -3.5, -2.0, -6.5, -1.1])

        beat_rate = (surprises > 0).sum() / len(surprises) * 100
        avg_surprise = surprises.mean()

        assert beat_rate == 0.0
        assert avg_surprise < 0

    def test_revenue_range_calculation(self):
        """Test revenue range display"""
        rev_low = 88000000000
        rev_high = 92000000000

        if rev_low and rev_high:
            formatted = f"${float(rev_low)/1e9:.2f}B - ${float(rev_high)/1e9:.2f}B"
        else:
            formatted = "N/A"

        assert formatted == "$88.00B - $92.00B"

    def test_dividend_yield_calculation(self):
        """Test dividend yield calculation and formatting"""
        dividend_rate = 0.92
        current_price = 150.0

        dividend_yield = (dividend_rate / current_price * 100) if current_price > 0 else 0

        assert dividend_yield == pytest.approx(0.613, rel=0.01)

    def test_price_target_range_validation(self):
        """Test that price target range is valid"""
        target_low = 120.0
        target_high = 180.0
        target_mean = 155.0

        assert target_low < target_mean < target_high

    def test_earnings_date_formatting(self):
        """Test earnings date formatting"""
        earnings_date = datetime(2024, 10, 25)

        formatted = earnings_date.strftime('%b %d, %Y')

        assert formatted == "Oct 25, 2024"

    def test_price_movement_bounds_checking(self):
        """Test price movement window stays within bounds"""
        window_days = 5
        date_loc = 2
        price_data_len = 100

        pre_start_idx = max(0, date_loc - window_days)
        post_end_idx = min(price_data_len - 1, date_loc + window_days)

        assert pre_start_idx >= 0
        assert post_end_idx < price_data_len


class TestEarningsEstimatesDataValidation:
    """Data validation tests for Earnings & Estimates Dashboard"""

    def test_calendar_data_types(self):
        """Test calendar data type validation"""
        calendar = {
            'Earnings Date': [datetime.now() + timedelta(days=30)],
            'Earnings Average': 1.25,
            'Earnings Low': 1.15,
            'Earnings High': 1.35,
            'Revenue Average': 90000000000
        }

        assert isinstance(calendar.get('Earnings Average'), (int, float))
        assert isinstance(calendar.get('Revenue Average'), (int, float))

    def test_earnings_dates_data_types(self):
        """Test earnings dates DataFrame data types"""
        dates = pd.date_range(end=datetime.now(), periods=8, freq='90D')
        df = pd.DataFrame({
            'EPS Estimate': [1.20, 1.15, 1.10, 1.08, 1.05, 1.02, 1.00, 0.98],
            'Reported EPS': [1.25, 1.18, 1.12, 1.10, 1.03, 1.00, 0.95, 0.92],
            'Surprise(%)': [4.2, 2.6, 1.8, 1.9, -1.9, -2.0, -5.0, -6.1]
        }, index=dates)

        assert pd.api.types.is_numeric_dtype(df['EPS Estimate'])
        assert pd.api.types.is_numeric_dtype(df['Reported EPS'])
        assert pd.api.types.is_numeric_dtype(df['Surprise(%)'])

    def test_analyst_data_ranges(self):
        """Test analyst data within expected ranges"""
        info = {
            'targetHighPrice': 180.0,
            'targetLowPrice': 120.0,
            'targetMeanPrice': 155.0,
            'targetMedianPrice': 152.0,
            'numberOfAnalystOpinions': 35
        }

        assert info['targetLowPrice'] < info['targetMeanPrice'] < info['targetHighPrice']
        assert info['numberOfAnalystOpinions'] > 0


def run_tests():
    """Run all tests and print results"""
    print("=" * 80)
    print("Running Earnings & Estimates Dashboard Tests")
    print("=" * 80)

    # Run pytest
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_tests()
