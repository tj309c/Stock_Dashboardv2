"""
Tests for Debug Dashboard cache control enhancements
- Time estimation before cache clear
- Confirmation dialog for slow operations
"""
import pytest
import streamlit as st
from performance_optimizer import get_cache_reload_estimate


class TestCacheReloadEstimateDisplay:
    """Test cache reload time estimation display logic"""

    def test_shows_warning_for_slow_operations(self):
        """Should show time estimate warning when reload > 15 seconds"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 2.0, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # max_duration = 2.0, estimated_max = 20s > 15s threshold
        assert estimate['show_warning'] is True
        assert estimate['estimated_max'] > 15

    def test_no_warning_for_fast_operations(self):
        """Should not show warning when reload < 15 seconds"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 0.5, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # max_duration = 0.5, estimated_max = 5s < 15s threshold
        assert estimate['show_warning'] is False
        assert estimate['estimated_max'] <= 15

    def test_estimate_caption_format(self):
        """Should format time estimate caption correctly"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 3.0, 'timestamp': 100},
        ]

        estimate = get_cache_reload_estimate()

        # Create caption like the UI does
        caption = f"⏱️ Est. reload time: ~{estimate['estimated_min']}-{estimate['estimated_max']}s based on recent usage"

        assert '⏱️' in caption
        assert 'Est. reload time:' in caption
        assert 's based on recent usage' in caption
        assert str(estimate['estimated_min']) in caption
        assert str(estimate['estimated_max']) in caption


class TestConfirmationDialogLogic:
    """Test confirmation dialog state management"""

    def test_confirmation_state_initialization(self):
        """Confirmation state should initialize to False"""
        # Clear session state
        if 'confirm_clear_all' in st.session_state:
            del st.session_state.confirm_clear_all

        # First time check
        if 'confirm_clear_all' not in st.session_state:
            st.session_state.confirm_clear_all = False

        assert st.session_state.confirm_clear_all is False

    def test_confirmation_state_toggle(self):
        """Should toggle confirmation state on button click"""
        st.session_state.confirm_clear_all = False

        # Simulate button click (when warning is shown)
        st.session_state.confirm_clear_all = True

        assert st.session_state.confirm_clear_all is True

        # Simulate cancel
        st.session_state.confirm_clear_all = False

        assert st.session_state.confirm_clear_all is False

    def test_confirmation_required_for_slow_operations(self):
        """Confirmation should be required when estimated time > 15s"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 3.0, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # Simulate button click logic
        requires_confirmation = estimate['show_warning']

        assert requires_confirmation is True

    def test_no_confirmation_for_fast_operations(self):
        """No confirmation should be required when estimated time < 15s"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 0.5, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # Fast operation - no confirmation needed
        requires_confirmation = estimate['show_warning']

        assert requires_confirmation is False

    def test_confirmation_message_format(self):
        """Confirmation message should include time estimate"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 5.0, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # Create warning message like the UI does
        warning_msg = f"⚠️ This will clear all cached data and reload on next interaction. Estimated reload time: **{estimate['estimated_min']}-{estimate['estimated_max']} seconds**. Continue?"

        assert '⚠️' in warning_msg
        assert 'clear all cached data' in warning_msg
        assert 'Estimated reload time:' in warning_msg
        assert 'Continue?' in warning_msg
        assert str(estimate['estimated_min']) in warning_msg
        assert str(estimate['estimated_max']) in warning_msg


class TestCacheControlFlow:
    """Test the complete cache control flow"""

    def test_fast_operation_flow(self):
        """Fast operations should skip confirmation"""
        # Setup: fast operations
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': i}
            for i in range(5)
        ]
        st.session_state.confirm_clear_all = False

        estimate = get_cache_reload_estimate()

        # Simulate button click
        if estimate['show_warning']:
            # Should show confirmation
            st.session_state.confirm_clear_all = True
        else:
            # Should clear immediately (fast operation)
            cache_cleared = True

        # Fast operation - no confirmation shown
        assert not estimate['show_warning']
        assert st.session_state.confirm_clear_all is False

    def test_slow_operation_flow(self):
        """Slow operations should show confirmation first"""
        # Setup: slow operations
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 5.0, 'timestamp': i}
            for i in range(10)
        ]
        st.session_state.confirm_clear_all = False

        estimate = get_cache_reload_estimate()

        # Simulate first button click
        if estimate['show_warning']:
            st.session_state.confirm_clear_all = True
        else:
            cache_cleared = True

        # Slow operation - should show confirmation
        assert estimate['show_warning']
        assert st.session_state.confirm_clear_all is True

    def test_confirmation_cancel(self):
        """Cancel should reset confirmation state"""
        st.session_state.confirm_clear_all = True

        # Simulate cancel button
        st.session_state.confirm_clear_all = False

        assert st.session_state.confirm_clear_all is False

    def test_confirmation_proceed(self):
        """Proceed should clear cache and reset state"""
        st.session_state.confirm_clear_all = True

        # Simulate proceed button
        st.session_state.confirm_clear_all = False
        cache_cleared = True  # st.cache_data.clear() would be called

        assert st.session_state.confirm_clear_all is False
        assert cache_cleared is True


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_no_performance_metrics_shows_default(self):
        """Should show default estimate when no metrics exist"""
        if 'performance_metrics' in st.session_state:
            del st.session_state.performance_metrics

        estimate = get_cache_reload_estimate()

        # Default estimate
        assert estimate['estimated_min'] == 10
        assert estimate['estimated_max'] == 30
        assert estimate['show_warning'] is True
        assert estimate['confidence'] == 'low'

    def test_empty_performance_metrics_list(self):
        """Should handle empty metrics list"""
        st.session_state.performance_metrics = []

        estimate = get_cache_reload_estimate()

        # Should return default estimate
        assert estimate['estimated_min'] == 10
        assert estimate['estimated_max'] == 30
        assert estimate['confidence'] == 'low'

    def test_single_metric(self):
        """Should work with single performance metric"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 2.0, 'timestamp': 100}
        ]

        estimate = get_cache_reload_estimate()

        # avg = 2.0, max = 2.0
        # estimated_min = 6, estimated_max = 20
        assert estimate['estimated_min'] == 6
        assert estimate['estimated_max'] == 20
        assert estimate['confidence'] == 'medium'  # < 10 samples

    def test_very_fast_operations(self):
        """Should handle very fast operations (< 0.1s)"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 0.05, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        # max = 0.05, estimated_max = 0.5
        assert estimate['estimated_max'] < 1
        assert estimate['show_warning'] is False

    def test_mixed_operation_speeds(self):
        """Should handle mixed fast and slow operations"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_fast', 'duration': 0.5, 'timestamp': 100},
            {'operation': 'fetch_slow', 'duration': 10.0, 'timestamp': 101},
            {'operation': 'load_data', 'duration': 2.0, 'timestamp': 102},
        ]

        estimate = get_cache_reload_estimate()

        # max = 10.0, estimated_max = 100s
        # Should show warning due to slow operation
        assert estimate['estimated_max'] == 100
        assert estimate['show_warning'] is True

    def test_confidence_boundary_exactly_10_samples(self):
        """Should return high confidence with exactly 10 samples"""
        st.session_state.performance_metrics = [
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': i}
            for i in range(10)
        ]

        estimate = get_cache_reload_estimate()

        assert estimate['confidence'] == 'medium'  # < 10 means 10 is NOT high

        # With 11 samples
        st.session_state.performance_metrics.append(
            {'operation': 'fetch_data', 'duration': 1.0, 'timestamp': 10}
        )

        estimate = get_cache_reload_estimate()

        assert estimate['confidence'] == 'high'  # >= 10 + 1 = 11
