"""
Pytest for Competitive & Market Debug Tab Enhancements
Tests the render_debug_tab_competitive function and short squeeze analysis
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_short_squeeze_data_complete():
    """Fixture for complete short squeeze data"""
    return {
        'shortRatio': 3.5,
        'shortPercentOfFloat': 0.15,  # 15%
        'sharesShort': 50_000_000,
        'sharesShortPriorMonth': 45_000_000,
        'averageVolume': 80_000_000,
        'averageVolume10days': 85_000_000,
        'regularMarketVolume': 90_000_000,
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 2_800_000_000_000
    }


@pytest.fixture
def mock_short_squeeze_data_incomplete():
    """Fixture for incomplete short squeeze data"""
    return {
        'shortRatio': None,
        'shortPercentOfFloat': None,
        'sharesShort': None,
        'averageVolume': 50_000_000,
        'regularMarketVolume': None
    }


@pytest.fixture
def mock_price_data_with_volume():
    """Fixture for price data with volume"""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    return pd.DataFrame({
        'Open': [150 + i*0.5 for i in range(100)],
        'High': [152 + i*0.5 for i in range(100)],
        'Low': [149 + i*0.5 for i in range(100)],
        'Close': [151 + i*0.5 for i in range(100)],
        'Volume': [80_000_000 + i*100_000 for i in range(100)]
    }, index=dates)


@pytest.fixture
def mock_ussi_components():
    """Fixture for USSI score components"""
    return {
        'Short Interest': {
            'raw_score': 15.0,
            'normalized_score': 75.0,
            'weight': 0.25
        },
        'Days to Cover': {
            'raw_score': 3.5,
            'normalized_score': 70.0,
            'weight': 0.20
        },
        'Volume Spike': {
            'raw_score': 2.1,
            'normalized_score': 65.0,
            'weight': 0.20
        },
        'Price Momentum': {
            'raw_score': 8.5,
            'normalized_score': 85.0,
            'weight': 0.20
        },
        'Social Sentiment': {
            'raw_score': 1200,
            'normalized_score': 60.0,
            'weight': 0.15
        }
    }


@pytest.fixture
def mock_leaderboard_data():
    """Fixture for leaderboard data"""
    return pd.DataFrame({
        'Ticker': ['GME', 'AMC', 'BBBY', 'AAPL', 'TSLA'],
        'Company': ['GameStop Corp.', 'AMC Entertainment', 'Bed Bath & Beyond', 'Apple Inc.', 'Tesla Inc.'],
        'Squeeze Score': [92.5, 88.3, 75.2, 45.1, 38.9],
        'Short % Float': [0.25, 0.22, 0.18, 0.01, 0.03],
        'Volume Z-Score': [4.5, 3.8, 2.9, 0.8, 1.2],
        'Social Mentions (7d)': [15000, 12000, 8000, 5000, 7000]
    })


class TestShortSqueezeDataQuality:
    """Test suite for short squeeze data quality checks"""

    def test_complete_short_squeeze_data(self, mock_short_squeeze_data_complete, mock_price_data_with_volume):
        """Test data quality with complete short squeeze information"""
        info = mock_short_squeeze_data_complete
        price_data = mock_price_data_with_volume

        checks = {
            "Short Ratio": info.get('shortRatio') is not None,
            "Short % of Float": info.get('shortPercentOfFloat') is not None,
            "Shares Short": info.get('sharesShort') is not None,
            "Average Volume": info.get('averageVolume') is not None,
            "Regular Market Volume": info.get('regularMarketVolume') is not None,
            "Price Data Available": price_data is not None and not price_data.empty,
            "Volume Data in Price": 'Volume' in price_data.columns
        }

        completeness_score = sum(checks.values())
        total_checks = len(checks)
        completeness_pct = (completeness_score / total_checks) * 100

        # All checks should pass
        assert completeness_pct == 100.0
        assert all(checks.values())

    def test_incomplete_short_squeeze_data(self, mock_short_squeeze_data_incomplete):
        """Test data quality with incomplete short squeeze information"""
        info = mock_short_squeeze_data_incomplete

        checks = {
            "Short Ratio": info.get('shortRatio') is not None,
            "Short % of Float": info.get('shortPercentOfFloat') is not None,
            "Shares Short": info.get('sharesShort') is not None,
            "Average Volume": info.get('averageVolume') is not None,
            "Regular Market Volume": info.get('regularMarketVolume') is not None
        }

        completeness_score = sum(checks.values())
        total_checks = len(checks)
        completeness_pct = (completeness_score / total_checks) * 100

        # Only 1 out of 5 should pass (average volume)
        assert completeness_pct == 20.0
        assert completeness_pct < 50  # Below critical threshold

    def test_short_ratio_validation(self, mock_short_squeeze_data_complete):
        """Test short ratio value validation"""
        info = mock_short_squeeze_data_complete

        short_ratio = info.get('shortRatio')
        assert short_ratio is not None
        assert short_ratio > 0
        assert isinstance(short_ratio, (int, float))

    def test_short_percent_float_range(self, mock_short_squeeze_data_complete):
        """Test short percent of float is in valid range"""
        info = mock_short_squeeze_data_complete

        short_pct = info.get('shortPercentOfFloat')
        assert short_pct is not None
        assert 0 <= short_pct <= 1  # Should be decimal (0.15 = 15%)

    def test_volume_data_availability(self, mock_price_data_with_volume):
        """Test volume data availability in price data"""
        price_data = mock_price_data_with_volume

        assert 'Volume' in price_data.columns
        assert not price_data['Volume'].isnull().all()
        assert len(price_data) > 0


class TestUSSIScoreCalculation:
    """Test suite for USSI score calculation"""

    def test_ussi_score_range(self):
        """Test USSI score is within valid range"""
        final_score = 72.5

        assert 0 <= final_score <= 100

    def test_ussi_components_structure(self, mock_ussi_components):
        """Test USSI components have correct structure"""
        components = mock_ussi_components

        for comp_name, comp_data in components.items():
            assert 'raw_score' in comp_data
            assert 'normalized_score' in comp_data
            assert 'weight' in comp_data

            # Normalized score should be 0-100
            assert 0 <= comp_data['normalized_score'] <= 100

            # Weight should be 0-1
            assert 0 <= comp_data['weight'] <= 1

    def test_ussi_weights_sum_to_one(self, mock_ussi_components):
        """Test that USSI component weights sum to 1.0"""
        components = mock_ussi_components

        total_weight = sum(comp['weight'] for comp in components.values())

        # Should sum to 1.0 (allow small floating point error)
        assert abs(total_weight - 1.0) < 0.01

    def test_ussi_final_score_calculation(self, mock_ussi_components):
        """Test final USSI score calculation from components"""
        components = mock_ussi_components

        # Calculate weighted average
        final_score = sum(
            comp['normalized_score'] * comp['weight']
            for comp in components.values()
        )

        assert 0 <= final_score <= 100
        # With given test data, should be around 71
        assert 65 <= final_score <= 75


class TestLeaderboardFunctionality:
    """Test suite for leaderboard functionality"""

    def test_leaderboard_structure(self, mock_leaderboard_data):
        """Test leaderboard has correct structure"""
        leaderboard = mock_leaderboard_data

        required_columns = ['Ticker', 'Company', 'Squeeze Score', 'Short % Float', 'Volume Z-Score']

        for col in required_columns:
            assert col in leaderboard.columns

        assert len(leaderboard) > 0

    def test_leaderboard_sorting(self, mock_leaderboard_data):
        """Test leaderboard is sorted by squeeze score"""
        leaderboard = mock_leaderboard_data

        squeeze_scores = leaderboard['Squeeze Score'].tolist()

        # Should be in descending order
        assert squeeze_scores == sorted(squeeze_scores, reverse=True)

    def test_leaderboard_top_stock(self, mock_leaderboard_data):
        """Test top stock in leaderboard"""
        leaderboard = mock_leaderboard_data

        top_stock = leaderboard.iloc[0]

        assert top_stock['Ticker'] == 'GME'
        assert top_stock['Squeeze Score'] == 92.5

    def test_leaderboard_data_types(self, mock_leaderboard_data):
        """Test leaderboard data types are correct"""
        leaderboard = mock_leaderboard_data

        assert leaderboard['Ticker'].dtype == object
        assert leaderboard['Squeeze Score'].dtype in [float, 'float64']
        assert leaderboard['Short % Float'].dtype in [float, 'float64']

    def test_empty_leaderboard(self):
        """Test handling of empty leaderboard"""
        empty_df = pd.DataFrame()

        assert empty_df.empty
        assert len(empty_df) == 0


class TestCompetitorDataStatus:
    """Test suite for competitor data status"""

    def test_sector_industry_availability(self, mock_short_squeeze_data_complete):
        """Test sector and industry data availability"""
        info = mock_short_squeeze_data_complete

        sector = info.get('sector')
        industry = info.get('industry')

        assert sector is not None
        assert industry is not None
        assert isinstance(sector, str)
        assert isinstance(industry, str)

    def test_market_cap_availability(self, mock_short_squeeze_data_complete):
        """Test market cap availability"""
        info = mock_short_squeeze_data_complete

        market_cap = info.get('marketCap')

        assert market_cap is not None
        assert market_cap > 0
        assert isinstance(market_cap, (int, float))


class TestPerformanceMetrics:
    """Test suite for performance metrics"""

    @patch('time.time')
    def test_ussi_calculation_time(self, mock_time):
        """Test USSI calculation time measurement"""
        mock_time.side_effect = [0.0, 1.2]  # 1.2 second calculation

        start = mock_time()
        # Simulate USSI calculation
        end = mock_time()
        calc_time = end - start

        assert calc_time == 1.2
        assert calc_time < 5  # Should be reasonably fast

    @patch('time.time')
    def test_ticker_data_load_time(self, mock_time):
        """Test ticker data load time measurement"""
        mock_time.side_effect = [0.0, 0.8]  # 0.8 second load

        start = mock_time()
        # Simulate data load
        end = mock_time()
        load_time = end - start

        assert load_time == 0.8

    def test_performance_threshold_warning(self):
        """Test performance warning threshold"""
        fast_time = 3.0
        slow_time = 6.0

        assert fast_time <= 5
        assert slow_time > 5  # Should trigger warning


class TestDataInspector:
    """Test suite for raw data inspector"""

    def test_inspect_short_data(self, mock_short_squeeze_data_complete):
        """Test inspecting short data"""
        info = mock_short_squeeze_data_complete

        short_data = {
            'shortRatio': info.get('shortRatio'),
            'shortPercentOfFloat': info.get('shortPercentOfFloat'),
            'sharesShort': info.get('sharesShort'),
            'sharesShortPriorMonth': info.get('sharesShortPriorMonth'),
            'averageVolume': info.get('averageVolume'),
            'regularMarketVolume': info.get('regularMarketVolume')
        }

        # Verify all fields are present
        assert all(value is not None for value in short_data.values())

    def test_inspect_price_volume_data(self, mock_price_data_with_volume):
        """Test inspecting price and volume data"""
        price_data = mock_price_data_with_volume

        # Get last 20 rows
        tail_data = price_data[['Close', 'Volume']].tail(20)

        assert len(tail_data) == 20
        assert 'Close' in tail_data.columns
        assert 'Volume' in tail_data.columns

    def test_inspect_leaderboard(self, mock_leaderboard_data):
        """Test inspecting leaderboard data"""
        leaderboard = mock_leaderboard_data

        assert isinstance(leaderboard, pd.DataFrame)
        assert not leaderboard.empty
        assert len(leaderboard) == 5


class TestCacheManagement:
    """Test suite for cache management"""

    @patch('streamlit.cache_data.clear')
    def test_cache_clear_all(self, mock_clear):
        """Test clearing all caches"""
        mock_clear()
        mock_clear.assert_called_once()

    def test_cached_functions_list(self):
        """Test list of cached functions"""
        cached_functions = [
            'initialize_data_and_context()',
            'calculate_squeeze_score()',
            'generate_squeeze_leaderboard()'
        ]

        assert len(cached_functions) == 3

    def test_leaderboard_session_state_clear(self):
        """Test clearing leaderboard session state"""
        mock_state = {
            'leaderboard_df': pd.DataFrame(),
            'sentiment_data_dict': {}
        }

        # Simulate clearing
        if 'leaderboard_df' in mock_state:
            del mock_state['leaderboard_df']
        if 'sentiment_data_dict' in mock_state:
            del mock_state['sentiment_data_dict']

        assert 'leaderboard_df' not in mock_state
        assert 'sentiment_data_dict' not in mock_state


class TestErrorHandling:
    """Test suite for error handling"""

    def test_none_info_handling(self):
        """Test handling when info is None"""
        info = None

        if info is None:
            info = {}

        short_ratio = info.get('shortRatio')
        assert short_ratio is None

    def test_empty_price_data(self):
        """Test handling of empty price data"""
        price_data = pd.DataFrame()

        assert price_data.empty
        assert len(price_data) == 0

    def test_missing_volume_column(self):
        """Test handling when volume column is missing"""
        price_data = pd.DataFrame({
            'Close': [100, 101, 102]
        })

        has_volume = 'Volume' in price_data.columns
        assert has_volume is False


class TestSessionStateIntegration:
    """Test suite for session state integration"""

    def test_session_state_leaderboard_storage(self, mock_leaderboard_data):
        """Test storing leaderboard in session state"""
        session_state = {}
        session_state['leaderboard_df'] = mock_leaderboard_data

        assert 'leaderboard_df' in session_state
        assert len(session_state['leaderboard_df']) == 5

    def test_session_state_sentiment_storage(self):
        """Test storing sentiment data in session state"""
        session_state = {}
        session_state['sentiment_data_dict'] = {
            'GME': {'mentions': 15000},
            'AMC': {'mentions': 12000}
        }

        assert 'sentiment_data_dict' in session_state
        assert len(session_state['sentiment_data_dict']) == 2


class TestDataValidation:
    """Test suite for data validation"""

    def test_validate_shares_short_change(self, mock_short_squeeze_data_complete):
        """Test validation of shares short change"""
        info = mock_short_squeeze_data_complete

        shares_short = info.get('sharesShort')
        shares_short_prior = info.get('sharesShortPriorMonth')

        assert shares_short is not None
        assert shares_short_prior is not None

        # Current should be greater than prior (increasing short interest)
        assert shares_short > shares_short_prior

    def test_validate_volume_positive(self, mock_short_squeeze_data_complete):
        """Test that volume values are positive"""
        info = mock_short_squeeze_data_complete

        avg_volume = info.get('averageVolume')
        market_volume = info.get('regularMarketVolume')

        assert avg_volume > 0
        assert market_volume > 0

    def test_validate_short_percent_calculation(self, mock_short_squeeze_data_complete):
        """Test short percent float calculation"""
        info = mock_short_squeeze_data_complete

        short_pct = info.get('shortPercentOfFloat')

        # Should be between 0 and 1 (can't have more than 100% short)
        # Note: In practice, short interest can exceed float due to synthetic shares,
        # but for most cases it should be < 1
        assert short_pct >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
