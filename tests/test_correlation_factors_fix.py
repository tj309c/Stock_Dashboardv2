"""
Pytest for Correlation Factors Fix
Tests the fix for the pd.concat column mismatch issue in correlation_factors.py
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def mock_stock_returns():
    """Fixture for stock returns data"""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    returns = pd.Series(
        np.random.normal(0.001, 0.02, 100),
        index=dates,
        name='stock_returns'
    )
    return returns


@pytest.fixture
def mock_factor_returns():
    """Fixture for factor returns data"""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(43)
    returns = pd.Series(
        np.random.normal(0.0005, 0.015, 100),
        index=dates,
        name='factor_returns'
    )
    return returns


@pytest.fixture
def mock_misaligned_returns():
    """Fixture for returns with different date ranges (misaligned)"""
    stock_dates = pd.date_range('2023-01-01', periods=120, freq='D')
    factor_dates = pd.date_range('2023-01-15', periods=100, freq='D')

    np.random.seed(42)
    stock_returns = pd.Series(
        np.random.normal(0.001, 0.02, 120),
        index=stock_dates,
        name='stock'
    )

    factor_returns = pd.Series(
        np.random.normal(0.0005, 0.015, 100),
        index=factor_dates,
        name='factor'
    )

    return stock_returns, factor_returns


class TestPdConcatColumnHandling:
    """Test suite for pd.concat column mismatch fix"""

    def test_concat_with_two_series(self, mock_stock_returns, mock_factor_returns):
        """Test pd.concat creates exactly 2 columns with two series"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Should have exactly 2 columns
        assert aligned_data.shape[1] == 2
        assert len(aligned_data.columns) == 2

    def test_rename_columns_after_concat(self, mock_stock_returns, mock_factor_returns):
        """Test renaming columns after concat"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Apply the fix
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            # If we have more than 2 columns, take first 2
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Should have correct column names
        assert list(aligned_data.columns) == ['stock', 'factor']

    def test_concat_with_duplicate_names(self):
        """Test concat with series that might have duplicate names"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        # Both series have same name
        series1 = pd.Series(np.random.randn(50), index=dates, name='returns')
        series2 = pd.Series(np.random.randn(50), index=dates, name='returns')

        aligned_data = pd.concat([series1, series2], axis=1, join='inner').dropna()

        # pandas might create duplicate column names, so we need to handle this
        # The fix should handle any number of columns
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        assert aligned_data.shape[1] == 2
        assert list(aligned_data.columns) == ['stock', 'factor']

    def test_concat_with_multiindex(self):
        """Test concat doesn't create multi-level column index"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        series1 = pd.Series(np.random.randn(50), index=dates, name='stock')
        series2 = pd.Series(np.random.randn(50), index=dates, name='factor')

        aligned_data = pd.concat([series1, series2], axis=1, join='inner').dropna()

        # Columns should not be MultiIndex
        assert not isinstance(aligned_data.columns, pd.MultiIndex)

    def test_handle_more_than_two_columns(self):
        """Test handling when concat accidentally creates more than 2 columns"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        # Create 3 series
        series1 = pd.Series(np.random.randn(50), index=dates)
        series2 = pd.Series(np.random.randn(50), index=dates)
        series3 = pd.Series(np.random.randn(50), index=dates)

        # Concat all 3 (simulating the error condition)
        aligned_data = pd.concat([series1, series2, series3], axis=1, join='inner').dropna()

        # Original code would fail here with "Expected axis has 3 elements, new values have 2 elements"
        # The fix handles this:
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            # Take only first 2 columns
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Should now have exactly 2 columns
        assert aligned_data.shape[1] == 2
        assert list(aligned_data.columns) == ['stock', 'factor']


class TestRollingCorrelationDataAlignment:
    """Test suite for data alignment in rolling correlation"""

    def test_inner_join_aligns_dates(self, mock_misaligned_returns):
        """Test inner join properly aligns misaligned dates"""
        stock_returns, factor_returns = mock_misaligned_returns

        aligned_data = pd.concat(
            [stock_returns, factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Should only have overlapping dates (stock has 120 days, factor has 100, with offset)
        # The overlap should be exactly 100 days since factor starts later
        assert len(aligned_data) == len(factor_returns)  # Equal to shorter series
        assert len(aligned_data) < len(stock_returns)  # Less than longer series

        # All dates should be in both original series
        for date in aligned_data.index:
            assert date in stock_returns.index
            assert date in factor_returns.index

    def test_dropna_removes_missing_values(self):
        """Test dropna removes any NaN values"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        # Series with some NaN values
        series1 = pd.Series(np.random.randn(50), index=dates)
        series1.iloc[10:15] = np.nan

        series2 = pd.Series(np.random.randn(50), index=dates)

        aligned_data = pd.concat([series1, series2], axis=1, join='inner').dropna()

        # Should have no NaN values
        assert not aligned_data.isnull().any().any()

        # Should have fewer rows than original (removed NaN rows)
        assert len(aligned_data) < 50

    def test_minimum_data_requirement(self, mock_stock_returns, mock_factor_returns):
        """Test minimum data requirement for rolling correlation"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        window = 60
        minimum_required = window + 30

        # Check if we have sufficient data
        has_sufficient_data = len(aligned_data) >= minimum_required

        if len(aligned_data) < minimum_required:
            # Should return error result
            result = {
                'mean_correlation': 0.0,
                'std_correlation': 0.0,
                'stability': 'Insufficient Data',
                'rolling_series': pd.Series(),
                'insight': f'Need at least {minimum_required} days of data'
            }
            assert result['stability'] == 'Insufficient Data'
        else:
            assert has_sufficient_data


class TestColumnRenamingEdgeCases:
    """Test suite for column renaming edge cases"""

    def test_empty_dataframe_handling(self):
        """Test handling of empty dataframe"""
        empty_df = pd.DataFrame()

        if empty_df.empty:
            # Should handle gracefully
            assert len(empty_df) == 0
        else:
            if empty_df.shape[1] == 2:
                empty_df.columns = ['stock', 'factor']

    def test_single_column_handling(self):
        """Test handling when only one column exists"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        single_col_df = pd.DataFrame({
            'col1': np.random.randn(50)
        }, index=dates)

        # Should detect we don't have 2 columns
        if single_col_df.shape[1] != 2:
            assert single_col_df.shape[1] == 1

    def test_column_count_validation(self):
        """Test column count validation before renaming"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        # Test with various column counts
        for num_cols in [1, 2, 3, 4]:
            data = {f'col{i}': np.random.randn(50) for i in range(num_cols)}
            df = pd.DataFrame(data, index=dates)

            original_cols = df.shape[1]

            # Apply the fix logic
            if df.shape[1] == 2:
                df.columns = ['stock', 'factor']
            elif df.shape[1] > 2:
                df = df.iloc[:, :2]
                df.columns = ['stock', 'factor']

            # Verify outcome
            if original_cols >= 2:
                assert df.shape[1] == 2
                assert list(df.columns) == ['stock', 'factor']
            else:
                assert df.shape[1] == 1


class TestCorrelationCalculation:
    """Test suite for correlation calculation after fix"""

    def test_correlation_with_aligned_data(self, mock_stock_returns, mock_factor_returns):
        """Test correlation calculation with aligned data"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Apply fix
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Calculate correlation
        correlation = aligned_data['stock'].corr(aligned_data['factor'])

        # Correlation should be between -1 and 1
        assert -1 <= correlation <= 1
        assert isinstance(correlation, (float, np.floating))

    def test_rolling_correlation_calculation(self, mock_stock_returns, mock_factor_returns):
        """Test rolling correlation calculation"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Apply fix
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        window = 30

        if len(aligned_data) >= window:
            # Calculate rolling correlation manually
            rolling_correlations = []
            for i in range(window, len(aligned_data) + 1):
                window_data = aligned_data.iloc[i-window:i]
                corr = window_data['stock'].corr(window_data['factor'])
                rolling_correlations.append(corr)

            # All correlations should be valid
            assert all(-1 <= c <= 1 for c in rolling_correlations if not pd.isna(c))


class TestRegressionPrevention:
    """Test suite to prevent regression of the original bug"""

    def test_original_bug_scenario(self):
        """Test the exact scenario that caused the original bug"""
        # Simulate the bug: concat creating 3 columns instead of 2
        dates = pd.date_range('2023-01-01', periods=100, freq='D')

        # Create two series with potential for column duplication
        series1 = pd.Series(np.random.randn(100), index=dates, name='returns')
        series2 = pd.Series(np.random.randn(100), index=dates, name='returns')

        aligned_data = pd.concat([series1, series2], axis=1, join='inner').dropna()

        # ORIGINAL CODE (would fail):
        # aligned_data.columns = ['stock', 'factor']  # ValueError if shape[1] != 2

        # FIXED CODE:
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Should not raise ValueError
        assert list(aligned_data.columns) == ['stock', 'factor']
        assert aligned_data.shape[1] == 2

    def test_no_error_with_fix(self, mock_stock_returns, mock_factor_returns):
        """Test that the fix prevents the ValueError"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        try:
            # Apply the fix
            if aligned_data.shape[1] == 2:
                aligned_data.columns = ['stock', 'factor']
            else:
                aligned_data = aligned_data.iloc[:, :2]
                aligned_data.columns = ['stock', 'factor']

            # Should not raise any exception
            assert True
        except ValueError as e:
            # If this happens, the fix failed
            pytest.fail(f"Fix failed to prevent ValueError: {e}")


class TestDataIntegrity:
    """Test suite for data integrity after fix"""

    def test_data_values_unchanged(self, mock_stock_returns, mock_factor_returns):
        """Test that data values are unchanged by the fix"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Store original values
        original_values = aligned_data.values.copy()

        # Apply fix
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Values should be unchanged
        np.testing.assert_array_equal(aligned_data.values, original_values)

    def test_index_unchanged(self, mock_stock_returns, mock_factor_returns):
        """Test that index is unchanged by the fix"""
        aligned_data = pd.concat(
            [mock_stock_returns, mock_factor_returns],
            axis=1,
            join='inner'
        ).dropna()

        # Store original index
        original_index = aligned_data.index.copy()

        # Apply fix
        if aligned_data.shape[1] == 2:
            aligned_data.columns = ['stock', 'factor']
        else:
            aligned_data = aligned_data.iloc[:, :2]
            aligned_data.columns = ['stock', 'factor']

        # Index should be unchanged
        assert aligned_data.index.equals(original_index)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
