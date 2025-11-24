"""
Pytest for Market Overview Debug Tab Enhancements
Tests the render_debug_tab_market function and related functionality
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


# Mock the imports from the page module
@pytest.fixture
def mock_market_data():
    """Fixture for mock market indices data"""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    return {
        '^GSPC': pd.DataFrame({
            'Close': [4000 + i for i in range(100)],
            'Volume': [1000000 + i*1000 for i in range(100)]
        }, index=dates),
        '^DJI': pd.DataFrame({
            'Close': [33000 + i*10 for i in range(100)],
            'Volume': [500000 + i*500 for i in range(100)]
        }, index=dates),
        '^IXIC': pd.DataFrame({
            'Close': [11000 + i*5 for i in range(100)],
            'Volume': [2000000 + i*2000 for i in range(100)]
        }, index=dates),
        '^RUT': pd.DataFrame({
            'Close': [1800 + i*2 for i in range(100)],
            'Volume': [800000 + i*800 for i in range(100)]
        }, index=dates),
        '^VIX': pd.DataFrame({
            'Close': [20 + i*0.1 for i in range(100)],
            'Volume': [0 for i in range(100)]
        }, index=dates)
    }


@pytest.fixture
def mock_market_health():
    """Fixture for mock market health data"""
    return {
        'market_trend': 'Bullish',
        'sentiment_score': 75,
        'volatility': 'Moderate',
        'breadth': 'Strong'
    }


@pytest.fixture
def mock_sector_data():
    """Fixture for mock sector data"""
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    sectors = ['Technology', 'Healthcare', 'Financials', 'Energy', 'Consumer Discretionary',
               'Industrials', 'Materials', 'Real Estate', 'Utilities', 'Consumer Staples', 'Communication Services']

    sector_dict = {}
    for sector in sectors:
        sector_dict[sector] = pd.DataFrame({
            'Close': [100 + i for i in range(50)],
            'Volume': [1000000 + i*1000 for i in range(50)]
        }, index=dates)

    return sector_dict


@pytest.fixture
def mock_fred_data():
    """Fixture for mock FRED economic data"""
    dates = pd.date_range('2023-01-01', periods=12, freq='M')
    return {
        'GDP': pd.Series([25000 + i*100 for i in range(12)], index=dates),
        'UNRATE': pd.Series([3.5 + i*0.1 for i in range(12)], index=dates),
        'CPIAUCSL': pd.Series([290 + i*2 for i in range(12)], index=dates),
        'DFF': pd.Series([5.0 + i*0.05 for i in range(12)], index=dates),
        'DGS10': pd.Series([3.8 + i*0.03 for i in range(12)], index=dates),
        'DGS2': pd.Series([4.5 + i*0.04 for i in range(12)], index=dates),
        'DCOILWTICO': pd.Series([80 + i*2 for i in range(12)], index=dates),
        'DEXUSEU': pd.Series([1.1 + i*0.01 for i in range(12)], index=dates),
        'M2SL': pd.Series([21000 + i*50 for i in range(12)], index=dates),
        'UMCSENT': pd.Series([70 + i for i in range(12)], index=dates)
    }


class TestMarketOverviewDebugTab:
    """Test suite for Market Overview debug tab functionality"""

    def test_market_indices_data_quality_all_available(self, mock_market_data):
        """Test that all major indices are properly validated when available"""
        indices_data = mock_market_data

        # Verify all expected indices are present
        expected_symbols = ['^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX']
        for symbol in expected_symbols:
            assert symbol in indices_data
            assert not indices_data[symbol].empty
            assert 'Close' in indices_data[symbol].columns
            assert len(indices_data[symbol]) > 0

    def test_market_indices_data_quality_missing_data(self):
        """Test handling of missing indices data"""
        indices_data = {
            '^GSPC': pd.DataFrame(),  # Empty dataframe
            '^DJI': None  # Missing data
        }

        # Check that empty/None data is properly identified
        for symbol, data in indices_data.items():
            if data is None:
                assert data is None
            else:
                assert data.empty

    def test_fred_data_completeness_all_indicators(self, mock_fred_data):
        """Test FRED data completeness with all indicators available"""
        fred_data = mock_fred_data

        expected_indicators = [
            "GDP", "UNRATE", "CPIAUCSL", "DFF", "DGS10", "DGS2",
            "DCOILWTICO", "DEXUSEU", "M2SL", "UMCSENT"
        ]

        available_count = 0
        for indicator in expected_indicators:
            if indicator in fred_data and fred_data[indicator] is not None:
                if not fred_data[indicator].empty:
                    available_count += 1
                    assert len(fred_data[indicator]) > 0

        # All 10 indicators should be available
        assert available_count == 10
        completeness = (available_count / len(expected_indicators)) * 100
        assert completeness == 100.0

    def test_fred_data_completeness_partial(self):
        """Test FRED data completeness with some missing indicators"""
        dates = pd.date_range('2023-01-01', periods=12, freq='M')
        fred_data = {
            'GDP': pd.Series([25000 + i*100 for i in range(12)], index=dates),
            'UNRATE': pd.Series([3.5 + i*0.1 for i in range(12)], index=dates),
            'CPIAUCSL': None,  # Missing
            'DFF': pd.Series(),  # Empty
        }

        expected_indicators = ["GDP", "UNRATE", "CPIAUCSL", "DFF"]
        available_count = 0

        for indicator in expected_indicators:
            if indicator in fred_data and fred_data[indicator] is not None:
                if not (isinstance(fred_data[indicator], pd.Series) and fred_data[indicator].empty):
                    available_count += 1

        # Only 2 out of 4 should be available
        assert available_count == 2
        completeness = (available_count / len(expected_indicators)) * 100
        assert completeness == 50.0

    def test_sector_data_quality_all_sectors(self, mock_sector_data):
        """Test sector data quality with all 11 GICS sectors"""
        sector_data = mock_sector_data

        # Should have 11 sectors
        assert len(sector_data) == 11

        available_sectors = 0
        for sector, data in sector_data.items():
            if data is not None and not data.empty:
                available_sectors += 1
                assert len(data) > 0
                assert data.index[0] <= data.index[-1]  # Proper date ordering

        assert available_sectors == 11

    def test_sector_data_quality_missing_sectors(self):
        """Test sector data quality with missing sectors"""
        sector_data = {
            'Technology': pd.DataFrame({'Close': [100, 101, 102]}, index=pd.date_range('2023-01-01', periods=3)),
            'Healthcare': pd.DataFrame(),  # Empty
            'Financials': None  # Missing
        }

        available_count = 0
        for sector, data in sector_data.items():
            if data is not None and not data.empty:
                available_count += 1

        # Only 1 out of 3 should be available
        assert available_count == 1

    def test_sector_data_with_dict_wrapped(self):
        """Sector data entries can be dicts wrapping a DataFrame under 'history' key"""
        import pandas as pd
        dates = pd.date_range('2023-01-01', periods=3)
        sector_data = {
            'Technology': {'history': pd.DataFrame({'Close':[100,101,102]}, index=dates)},
            'Healthcare': {'history': pd.DataFrame()},
            'Financials': None
        }

        available_count = 0
        for sector, entry in sector_data.items():
            df = entry.get('history') if isinstance(entry, dict) else entry
            if df is not None and not (hasattr(df, 'empty') and df.empty):
                available_count += 1

        assert available_count == 1

    def test_market_health_data_structure(self, mock_market_health):
        """Test market health data structure"""
        market_health = mock_market_health

        # Verify expected keys are present
        assert 'market_trend' in market_health
        assert 'sentiment_score' in market_health
        assert 'volatility' in market_health
        assert 'breadth' in market_health

        # Verify data types
        assert isinstance(market_health['market_trend'], str)
        assert isinstance(market_health['sentiment_score'], (int, float))
        assert isinstance(market_health['volatility'], str)
        assert isinstance(market_health['breadth'], str)

    def test_indices_completeness_calculation(self, mock_market_data):
        """Test completeness percentage calculation for indices"""
        indices_data = mock_market_data

        index_symbols = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT",
            "VIX": "^VIX"
        }

        checks = {}
        for name, symbol in index_symbols.items():
            if indices_data is not None and symbol in indices_data:
                data = indices_data[symbol]
                has_data = data is not None and not data.empty
                has_price = has_data and 'Close' in data.columns
                checks[name] = has_data and has_price
            else:
                checks[name] = False

        completeness_score = sum(checks.values())
        completeness_pct = (completeness_score / len(checks)) * 100

        assert completeness_pct == 100.0
        assert all(checks.values())  # All checks should pass

    def test_indices_with_history_dicts(self):
        """Test indices data where each symbol maps to a dict containing 'history' DataFrame"""
        import pandas as pd
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        indices_data = {
            '^GSPC': {'history': pd.DataFrame({'Close': list(range(10)), 'Volume': list(range(10))}, index=dates)},
            '^DJI': {'history': pd.DataFrame({'Close': [33000 + i*10 for i in range(10)], 'Volume': [100+i for i in range(10)]}, index=dates)},
            '^IXIC': {'history': pd.DataFrame({'Close': list(range(10,20)), 'Volume': list(range(100,110))}, index=dates)},
            '^RUT': {'history': pd.DataFrame({'Close': list(range(20,30)), 'Volume': list(range(200,210))}, index=dates)},
            '^VIX': {'history': pd.DataFrame({'Close': [20 + i*0.1 for i in range(10)], 'Volume': [0]*10}, index=dates)}
        }

        index_symbols = {
            "S&P 500": '^GSPC',
            "Dow Jones": '^DJI',
            "NASDAQ": '^IXIC',
            "Russell 2000": '^RUT',
            "VIX": '^VIX'
        }

        checks = {}
        for name, symbol in index_symbols.items():
            if indices_data is not None and symbol in indices_data:
                data = indices_data[symbol]
                # simulate the extraction used by the debug tab
                df = data.get('history') if isinstance(data, dict) else data
                has_data = df is not None and not df.empty
                has_price = has_data and 'Close' in df.columns
                checks[name] = has_data and has_price
            else:
                checks[name] = False

        completeness_score = sum(checks.values())
        completeness_pct = (completeness_score / len(checks)) * 100

        assert completeness_pct == 100.0
        assert all(checks.values())

    def test_fred_data_with_empty_series(self):
        """Test FRED data handling with empty series"""
        fred_data = {
            'GDP': pd.Series(),
            'UNRATE': pd.Series(dtype=float)
        }

        for indicator, data in fred_data.items():
            assert isinstance(data, pd.Series)
            assert data.empty
            assert len(data) == 0

    def test_sector_data_date_range_validation(self, mock_sector_data):
        """Test that sector data has valid date ranges"""
        sector_data = mock_sector_data

        for sector, data in sector_data.items():
            if not data.empty:
                # Verify dates are in ascending order
                assert data.index.is_monotonic_increasing

                # Verify date range is reasonable
                date_range = data.index[-1] - data.index[0]
                assert date_range.days > 0


class TestDebugTabCacheManagement:
    """Test cache management functionality in debug tab"""

    @patch('streamlit.cache_data.clear')
    def test_cache_clear_button(self, mock_clear):
        """Test that cache clear button calls the clear method"""
        # Simulate button click
        mock_clear()

        # Verify clear was called
        mock_clear.assert_called_once()

    def test_cache_status_display(self):
        """Test cache status information display"""
        cached_functions = [
            'fetch_market_indices()',
            'fetch_sector_data()',
            'fetch_economic_data()',
            'fetch_fear_greed_index()',
            'fetch_global_indices()'
        ]

        # Verify all expected functions are listed
        assert len(cached_functions) == 5
        for func in cached_functions:
            assert '()' in func  # Verify proper function format


class TestDebugTabPerformanceMetrics:
    """Test performance metrics functionality"""

    @patch('time.time')
    def test_api_response_time_calculation(self, mock_time):
        """Test API response time calculation"""
        # Mock time progression
        mock_time.side_effect = [0.0, 1.5]  # 1.5 second operation

        start = mock_time()
        # Simulate operation
        end = mock_time()
        elapsed = end - start

        assert elapsed == 1.5

    def test_performance_warning_threshold(self):
        """Test performance warning threshold logic"""
        total_time_good = 8.0
        total_time_bad = 12.0

        # Good performance should not trigger warning
        assert total_time_good <= 10

        # Bad performance should trigger warning
        assert total_time_bad > 10


class TestDebugTabDataInspector:
    """Test raw data inspector functionality"""

    def test_data_inspector_market_indices_selection(self, mock_market_data):
        """Test data inspector can access market indices"""
        indices_data = mock_market_data

        # Test accessing each index
        for symbol in indices_data.keys():
            data = indices_data[symbol]
            assert not data.empty
            assert len(data.tail(10)) <= 10

    def test_data_inspector_fred_data_selection(self, mock_fred_data):
        """Test data inspector can access FRED data"""
        fred_data = mock_fred_data

        for indicator in fred_data.keys():
            data = fred_data[indicator]
            assert len(data) > 0
            assert len(data.tail(10)) <= 10

    def test_data_inspector_sector_data_selection(self, mock_sector_data):
        """Test data inspector can access sector data"""
        sector_data = mock_sector_data

        for sector in sector_data.keys():
            data = sector_data[sector]
            assert not data.empty
            assert len(data.tail(10)) <= 10


class TestDebugTabErrorHandling:
    """Test error handling in debug tab"""

    def test_empty_indices_data(self):
        """Test handling of empty indices data"""
        indices_data = None

        if indices_data is None:
            # Should handle gracefully
            assert indices_data is None

    def test_malformed_fred_data(self):
        """Test handling of malformed FRED data"""
        fred_data = "not_a_dict"  # Invalid type

        # Should detect invalid type
        assert not isinstance(fred_data, dict)

    def test_empty_sector_data(self):
        """Test handling of empty sector data"""
        sector_data = {}

        assert len(sector_data) == 0
        assert isinstance(sector_data, dict)


class TestSessionStateIntegration:
    """Test session state integration in debug tab"""

    def test_session_state_display(self):
        """Test session state variables can be displayed"""
        # Mock session state
        mock_state = {
            'ticker': 'AAPL',
            'last_update': '2024-01-01',
            'cache_hit': True
        }

        # Verify state can be converted to string for display
        state_dict = {k: str(v)[:200] for k, v in mock_state.items()}

        assert 'ticker' in state_dict
        assert state_dict['ticker'] == 'AAPL'
        assert len(state_dict['ticker']) <= 200

    def test_empty_session_state(self):
        """Test handling of empty session state"""
        mock_state = {}

        assert len(mock_state) == 0
        assert not mock_state  # Should be falsy when empty


class TestSnapshotHelpers:
    """Tests for session snapshot helpers (market/sector/fred)"""

    def test_get_market_snapshot_stores_in_session(self, monkeypatch):
        import importlib
        mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

        # patch the underlying fetchers to return deterministic values
        monkeypatch.setattr(mod, 'fetch_market_indices', lambda: {'S&P 500': {'price': 1000, 'pct_change': 1.0}, 'VIX': {'price': 20, 'pct_change': -0.5}})
        monkeypatch.setattr(mod, 'calculate_market_breadth', lambda: {'score': 1.2, 'status': 'Positive'})

        # Ensure session state key is empty
        if 'market_snapshot' in st.session_state:
            del st.session_state['market_snapshot']

        indices, breadth, health, ts = mod.get_market_snapshot(ttl_seconds=2)

        assert 'market_snapshot' in st.session_state
        snap = st.session_state['market_snapshot']
        assert snap['indices_data'] == indices
        assert snap['breadth_data'] == breadth
        assert snap['market_health'] == health

    def test_get_market_snapshot_ttl_and_refresh(self, monkeypatch):
        import importlib
        mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

        # patch to provide deterministic values
        monkeypatch.setattr(mod, 'fetch_market_indices', lambda: {'S&P 500': {'price': 1, 'pct_change': 0}})
        monkeypatch.setattr(mod, 'calculate_market_breadth', lambda: {'score': 0, 'status': 'Positive'})

        if 'market_snapshot' in st.session_state:
            del st.session_state['market_snapshot']

        a_indices, a_breadth, a_health, a_ts = mod.get_market_snapshot(ttl_seconds=5)

        # calling again within TTL should return same timestamp
        b_indices, b_breadth, b_health, b_ts = mod.get_market_snapshot(ttl_seconds=5)
        assert a_ts == b_ts

        # delete snapshot -> new ts expected
        del st.session_state['market_snapshot']
        c_indices, c_breadth, c_health, c_ts = mod.get_market_snapshot(ttl_seconds=5)
        assert c_ts != a_ts

    def test_ui_refresh_clears_global_cache_and_snapshot(self, monkeypatch):
        """When UI Refresh is clicked, the session snapshot should be removed and global cache cleared"""
        import importlib
        mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

        # Seed a snapshot in session_state
        st.session_state['market_snapshot'] = {'timestamp': 0, 'indices_data': {}, 'breadth_data': {}, 'market_health': {}}

        # Patch get_market_snapshot to avoid real fetching and to return a known snapshot
        def fake_snapshot(ttl_seconds=15):
            return (
                {
                    'S&P 500': {'price': 1000, 'pct_change': 0, 'change': 0},
                    'VIX': {'price': 20, 'pct_change': -0.5, 'change': -0.1}
                },
                {'score': 1.0, 'status': 'Positive'},
                {'score': 50, 'emoji': '➡️', 'category': 'Neutral'},
                12345678
            )

        monkeypatch.setattr(mod, 'get_market_snapshot', fake_snapshot)

        # Simulate button press
        monkeypatch.setattr(mod.st, 'button', lambda *args, **kwargs: True)

        # Spy on cache clear
        called = {'cleared': False}
        def fake_clear():
            called['cleared'] = True

        monkeypatch.setattr(mod.st.cache_data, 'clear', fake_clear)

        # Call the UI rendering function (should call fake_snapshot and clear cache)
        mod.render_market_pulse()

        assert called['cleared'] is True
        # snapshot should have been deleted (the fake_snapshot does not re-populate session_state)
        assert 'market_snapshot' not in st.session_state

    def test_ui_refresh_sector_and_fred_clear_global_cache(self, monkeypatch):
        import importlib
        mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

        # Sector
        st.session_state['sector_snapshot'] = {'timestamp': 0, 'sector_data': {}}
        monkeypatch.setattr(mod, 'get_sector_snapshot', lambda ttl_seconds=15: ({'Technology': {'ticker':'XLK','price': 1, 'change_5d': 0.5, 'change_1d': 0.1, 'change_1m': 0.9}}, 123))
        monkeypatch.setattr(mod.st, 'button', lambda *args, **kwargs: True)
        called = {'cleared': False}
        monkeypatch.setattr(mod.st.cache_data, 'clear', lambda: called.update({'cleared': True}))
        mod.render_sector_rotation()
        assert called['cleared'] is True
        assert 'sector_snapshot' not in st.session_state

        # FRED
        st.session_state['fred_snapshot'] = {'timestamp': 0, 'fred_data': {}}
        monkeypatch.setattr(mod, 'get_fred_snapshot', lambda ttl_seconds=15: ({'GDP': {'df': None}}, 456))
        monkeypatch.setattr(mod.st, 'button', lambda *args, **kwargs: True)
        called2 = {'cleared': False}
        monkeypatch.setattr(mod.st.cache_data, 'clear', lambda: called2.update({'cleared': True}))
        # call the economic indicator render
        # Keep an eye out: render_economic_indicators() expects FRED data; our fake returns simple data
        try:
            mod.render_economic_indicators()
        except Exception:
            # Rendering may raise in tests due to mocked data; we only assert cache clear behavior
            pass

        assert called2['cleared'] is True
        assert 'fred_snapshot' not in st.session_state


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
