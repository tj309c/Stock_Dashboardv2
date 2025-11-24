"""
Tests for performance_optimizer.py enhancements - time estimation features
"""
import pytest
import streamlit as st
from performance_optimizer import (
    estimate_reload_time,
    get_cache_reload_estimate
)


class TestEstimateReloadTime:
    """Test suite for estimate_reload_time function"""

    def test_empty_metrics_returns_zeros(self):
        """Should return all zeros when no metrics exist"""
        # Clear session state
        if 'performance_metrics' in st.session_state:
            del st.session_state.performance_metrics

        result = estimate_reload_time()

        assert result['min'] == 0
        assert result['max'] == 0
        assert result['avg'] == 0
        assert result['count'] == 0

    def test_returns_correct_stats_for_metrics(self):
        """Should calculate min, max, avg correctly from metrics"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': 100},
            {'operation': 'fetch_data', 'duration': 2.0, 'timestamp': 101},
            {'operation': 'fetch_data', 'duration': 3.0, 'timestamp': 102},
        ]

        result = estimate_reload_time()

        assert result['min'] == 1.0
        assert result['max'] == 3.0
        assert result['avg'] == 2.0
        assert result['count'] == 3

    def test_filters_by_operation_pattern(self):
        """Should only include operations matching the pattern"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_news', 'duration': 1.0, 'timestamp': 100},
            {'operation': 'load_data', 'duration': 2.0, 'timestamp': 101},
            {'operation': 'fetch_stock', 'duration': 3.0, 'timestamp': 102},
        ]

        result = estimate_reload_time('fetch')

        # Should only include 'fetch_news' and 'fetch_stock'
        assert result['count'] == 2
        assert result['min'] == 1.0
        assert result['max'] == 3.0
        assert result['avg'] == 2.0

    def test_case_insensitive_pattern_matching(self):
        """Pattern matching should be case-insensitive"""
        st.session_state.performance_metrics = [
            {'operation': 'FETCH_NEWS', 'duration': 1.0, 'timestamp': 100},
            {'operation': 'Fetch_Stock', 'duration': 2.0, 'timestamp': 101},
        ]

        result = estimate_reload_time('fetch')

        assert result['count'] == 2

    def test_no_matching_pattern_returns_zeros(self):
        """Should return zeros when no operations match the pattern"""
        st.session_state.performance_metrics = [
            {'operation': 'load_data', 'duration': 1.0, 'timestamp': 100},
        ]

        result = estimate_reload_time('fetch')

        assert result['count'] == 0
        assert result['min'] == 0
        assert result['max'] == 0
        assert result['avg'] == 0


class TestGetCacheReloadEstimate:
    """Test suite for get_cache_reload_estimate function"""

    def test_no_metrics_returns_default_warning(self):
        """Should return default estimates with warning when no metrics exist"""
        if 'performance_metrics' in st.session_state:
            del st.session_state.performance_metrics

        result = get_cache_reload_estimate()

        assert result['estimated_min'] == 10
        assert result['estimated_max'] == 30
        assert result['show_warning'] is True
        assert result['confidence'] == 'low'

    def test_calculates_estimates_from_fetch_operations(self):
        """Should calculate estimates based on fetch/load/init operations"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 2.0, 'timestamp': 100},
            {'operation': 'load_stocks', 'duration': 3.0, 'timestamp': 101},
            {'operation': 'init_app', 'duration': 1.0, 'timestamp': 102},
        ]

        result = get_cache_reload_estimate()

        # avg = 2.0, max = 3.0
        # estimated_min = avg * 3 = 6
        # estimated_max = max * 10 = 30
        assert result['estimated_min'] == 6
        assert result['estimated_max'] == 30

    def test_show_warning_threshold(self):
        """Should show warning when estimated_max > 15 seconds"""
        # Fast operations - no warning
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 0.5, 'timestamp': 100},
            {'operation': 'load_stocks', 'duration': 1.0, 'timestamp': 101},
        ]

        result = get_cache_reload_estimate()
        # max = 1.0, estimated_max = 10, should not warn
        assert result['show_warning'] is False

        # Slow operations - show warning
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 2.0, 'timestamp': 100},
            {'operation': 'load_stocks', 'duration': 3.0, 'timestamp': 101},
        ]

        result = get_cache_reload_estimate()
        # max = 3.0, estimated_max = 30, should warn
        assert result['show_warning'] is True

    def test_confidence_levels(self):
        """Should return high confidence with 10+ samples, medium otherwise"""
        # Low confidence (no data)
        if 'performance_metrics' in st.session_state:
            del st.session_state.performance_metrics

        result = get_cache_reload_estimate()
        assert result['confidence'] == 'low'

        # Medium confidence (< 10 samples)
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': i}
            for i in range(5)
        ]

        result = get_cache_reload_estimate()
        assert result['confidence'] == 'medium'

        # High confidence (>= 10 samples)
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': i}
            for i in range(15)
        ]

        result = get_cache_reload_estimate()
        assert result['confidence'] == 'high'

    def test_ignores_non_reload_operations(self):
        """Should only consider fetch/load/init operations"""
        st.session_state.performance_metrics = [
            {'operation': 'render_chart', 'duration': 5.0, 'timestamp': 100},
            {'operation': 'calculate_metrics', 'duration': 10.0, 'timestamp': 101},
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': 102},
        ]

        result = get_cache_reload_estimate()

        # Should only use 'fetch_data' (duration 1.0)
        # avg = 1.0, max = 1.0
        # estimated_min = 3, estimated_max = 10
        assert result['estimated_min'] == 3
        assert result['estimated_max'] == 10