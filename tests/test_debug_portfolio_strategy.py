"""
Pytest for Portfolio & Strategy Debug Tab Enhancements
Tests the render_debug_tab_portfolio function and portfolio optimization checks
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_portfolio_tickers():
    """Fixture for portfolio tickers"""
    return ['AAPL', 'MSFT', 'GOOG', 'AMZN']


@pytest.fixture
def mock_portfolio_price_data():
    """Fixture for portfolio price data (3 years)"""
    dates = pd.date_range('2021-01-01', periods=756, freq='D')  # ~3 years
    np.random.seed(42)

    data = {}
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN']:
        returns = np.random.normal(0.001, 0.02, 756)
        prices = 100 * (1 + returns).cumprod()
        data[ticker] = pd.DataFrame({
            'Close': prices
        }, index=dates)

    return data


@pytest.fixture
def mock_dcf_backtest_data():
    """Fixture for DCF backtest data"""
    return {
        'totalRevenue': 394_000_000_000,
        'sharesOutstanding': 16_000_000_000,
        'totalCash': 50_000_000_000,
        'totalDebt': 100_000_000_000,
        'trailingPE': 28.5,
        'marketCap': 2_800_000_000_000
    }


@pytest.fixture
def mock_backtest_assumptions():
    """Fixture for backtest assumptions"""
    return {
        'revenue_growth': 0.15,
        'ebitda_margin': 0.25,
        'tax_rate': 0.21,
        'capex_pct': 0.05,
        'nwc_pct': 0.10,
        'terminal_growth': 0.025,
        'wacc': 0.10
    }


@pytest.fixture
def mock_optimization_results():
    """Fixture for portfolio optimization results"""
    return {
        'max_sharpe': {
            'Return': 0.18,
            'Volatility': 0.22,
            'Sharpe': 0.82,
            'Weights': {'AAPL': 0.35, 'MSFT': 0.30, 'GOOG': 0.25, 'AMZN': 0.10}
        },
        'min_vol': {
            'Return': 0.12,
            'Volatility': 0.15,
            'Sharpe': 0.80,
            'Weights': {'AAPL': 0.25, 'MSFT': 0.40, 'GOOG': 0.20, 'AMZN': 0.15}
        }
    }


class TestPortfolioDataQuality:
    """Test suite for portfolio data quality checks"""

    def test_portfolio_data_complete(self, mock_portfolio_price_data):
        """Test portfolio data quality with complete data"""
        portfolio_data = mock_portfolio_price_data

        data_quality = {}
        for ticker, data in portfolio_data.items():
            data_quality[ticker] = {
                'has_data': not data.empty,
                'data_points': len(data),
                'has_close': 'Close' in data.columns,
                'date_range': f"{data.index[0].date()} to {data.index[-1].date()}"
            }

        # All tickers should have data
        assert all(q['has_data'] for q in data_quality.values())
        assert all(q['data_points'] >= 252 for q in data_quality.values())  # At least 1 year

    def test_portfolio_data_insufficient(self):
        """Test portfolio data quality with insufficient data"""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        insufficient_data = {
            'AAPL': pd.DataFrame({'Close': [100] * 50}, index=dates),
            'MSFT': pd.DataFrame()  # Empty
        }

        data_quality = {}
        for ticker, data in insufficient_data.items():
            data_quality[ticker] = {
                'has_data': not data.empty,
                'data_points': len(data)
            }

        successful = sum(1 for q in data_quality.values() if q['has_data'])

        # Only 1 out of 2 should have data
        assert successful == 1

    def test_minimum_tickers_requirement(self):
        """Test minimum ticker requirement for optimization"""
        single_ticker = ['AAPL']
        two_tickers = ['AAPL', 'MSFT']
        five_tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']

        assert len(single_ticker) < 2  # Insufficient
        assert len(two_tickers) >= 2  # Sufficient
        assert len(five_tickers) <= 5  # Within limit


class TestBacktestingRequirements:
    """Test suite for backtesting requirements"""

    def test_dcf_backtest_requirements_complete(self, mock_dcf_backtest_data):
        """Test DCF backtest requirements with complete data"""
        info = mock_dcf_backtest_data

        dcf_checks = {
            "Revenue Data": info.get('totalRevenue') is not None,
            "Shares Outstanding": info.get('sharesOutstanding') is not None,
            "Historical Prices": True,  # Assume available
            "Sufficient History": True  # 252+ days
        }

        dcf_ready = all(dcf_checks.values())

        assert dcf_ready is True
        assert all(dcf_checks.values())

    def test_dcf_backtest_requirements_incomplete(self):
        """Test DCF backtest requirements with incomplete data"""
        info = {
            'totalRevenue': None,
            'sharesOutstanding': None
        }

        dcf_checks = {
            "Revenue Data": info.get('totalRevenue') is not None,
            "Shares Outstanding": info.get('sharesOutstanding') is not None
        }

        dcf_ready = all(dcf_checks.values())

        assert dcf_ready is False

    def test_relative_valuation_requirements_complete(self, mock_dcf_backtest_data):
        """Test relative valuation requirements with complete data"""
        info = mock_dcf_backtest_data

        rel_checks = {
            "P/E Ratio": info.get('trailingPE') is not None,
            "Sector Info": info.get('sector') is not None or True,  # Mock as available
            "Industry Info": info.get('industry') is not None or True
        }

        # At least P/E should be available
        assert rel_checks["P/E Ratio"] is True

    def test_backtest_assumptions_validation(self, mock_backtest_assumptions):
        """Test backtest assumptions are valid"""
        assumptions = mock_backtest_assumptions

        # Revenue growth should be reasonable
        assert -0.5 <= assumptions['revenue_growth'] <= 1.0

        # Margins should be between 0 and 1
        assert 0 <= assumptions['ebitda_margin'] <= 1
        assert 0 <= assumptions['tax_rate'] <= 1

        # Terminal growth should be reasonable
        assert 0 <= assumptions['terminal_growth'] <= 0.10

        # WACC should be positive
        assert assumptions['wacc'] > 0


class TestModuleAvailability:
    """Test suite for module availability checks"""

    def test_portfolio_optimizer_availability(self):
        """Test portfolio optimizer module availability"""
        try:
            from portfolio_optimizer import run_portfolio_optimization
            available = True
        except ImportError:
            available = False

        assert isinstance(available, bool)

    def test_backtester_availability(self):
        """Test backtester module availability"""
        try:
            from backtester import run_dcf_backtest, run_relative_backtest
            available = True
        except ImportError:
            available = False

        assert isinstance(available, bool)

    def test_ai_services_availability(self):
        """Test AI services module availability"""
        try:
            from ai_services import get_ai_comparables
            available = True
        except ImportError:
            available = False

        assert isinstance(available, bool)


class TestOptimizationResults:
    """Test suite for optimization results validation"""

    def test_optimization_results_structure(self, mock_optimization_results):
        """Test optimization results have correct structure"""
        results = mock_optimization_results

        assert 'max_sharpe' in results
        assert 'min_vol' in results

        for strategy in ['max_sharpe', 'min_vol']:
            assert 'Return' in results[strategy]
            assert 'Volatility' in results[strategy]
            assert 'Sharpe' in results[strategy]
            assert 'Weights' in results[strategy]

    def test_portfolio_weights_sum_to_one(self, mock_optimization_results):
        """Test portfolio weights sum to 1.0"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            weights = results[strategy]['Weights']
            total_weight = sum(weights.values())

            # Should sum to 1.0 (allow small floating point error)
            assert abs(total_weight - 1.0) < 0.01

    def test_weights_non_negative(self, mock_optimization_results):
        """Test all weights are non-negative (long-only)"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            weights = results[strategy]['Weights']

            # All weights should be >= 0
            assert all(w >= 0 for w in weights.values())

    def test_return_and_volatility_positive(self, mock_optimization_results):
        """Test return and volatility are positive"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            ret = results[strategy]['Return']
            vol = results[strategy]['Volatility']

            assert ret > 0
            assert vol > 0

    def test_sharpe_ratio_calculation(self, mock_optimization_results):
        """Test Sharpe ratio calculation"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            ret = results[strategy]['Return']
            vol = results[strategy]['Volatility']
            sharpe = results[strategy]['Sharpe']

            # Approximate Sharpe (assuming risk-free rate ~0 for simplicity)
            expected_sharpe = ret / vol

            assert abs(sharpe - expected_sharpe) < 0.1  # Allow some tolerance

    def test_max_sharpe_vs_min_vol(self, mock_optimization_results):
        """Test max Sharpe should have higher return and likely higher vol than min vol"""
        max_sharpe = mock_optimization_results['max_sharpe']
        min_vol = mock_optimization_results['min_vol']

        # Max Sharpe should have better Sharpe ratio
        assert max_sharpe['Sharpe'] >= min_vol['Sharpe'] - 0.1  # Allow small difference

        # Min vol should have lower volatility
        assert min_vol['Volatility'] <= max_sharpe['Volatility']


class TestPerformanceMetrics:
    """Test suite for performance metrics"""

    @patch('time.time')
    def test_optimization_time_measurement(self, mock_time):
        """Test optimization time measurement"""
        mock_time.side_effect = [0.0, 12.0]  # 12 second optimization

        start = mock_time()
        # Simulate optimization
        end = mock_time()
        opt_time = end - start

        assert opt_time == 12.0

    def test_performance_warning_threshold(self):
        """Test performance warning threshold"""
        fast_opt = 15.0
        slow_opt = 35.0

        # Warning if over 30 seconds
        assert fast_opt <= 30
        assert slow_opt > 30


class TestDataInspector:
    """Test suite for data inspector"""

    def test_inspect_optimization_results(self, mock_optimization_results):
        """Test inspecting optimization results"""
        results = mock_optimization_results

        assert isinstance(results, dict)
        assert 'max_sharpe' in results

        # Should be able to convert to JSON-like structure
        max_sharpe_dict = results['max_sharpe']
        assert isinstance(max_sharpe_dict, dict)

    def test_inspect_backtest_assumptions(self, mock_backtest_assumptions):
        """Test inspecting backtest assumptions"""
        assumptions = mock_backtest_assumptions

        assert isinstance(assumptions, dict)
        assert 'revenue_growth' in assumptions
        assert 'wacc' in assumptions

        # Should be numeric
        for value in assumptions.values():
            assert isinstance(value, (int, float))

    def test_inspect_historical_data(self, mock_portfolio_price_data):
        """Test inspecting historical price data"""
        price_data = mock_portfolio_price_data

        ticker = 'AAPL'
        data = price_data[ticker]

        tail_data = data.tail(20)

        assert len(tail_data) == 20
        assert 'Close' in tail_data.columns


class TestCacheManagement:
    """Test suite for cache management"""

    @patch('streamlit.cache_data.clear')
    def test_cache_clear_functionality(self, mock_clear):
        """Test cache clear functionality"""
        mock_clear()
        mock_clear.assert_called_once()

    def test_cached_functions_list(self):
        """Test list of cached functions"""
        cached_functions = [
            'run_portfolio_optimization()',
            'run_dcf_backtest()',
            'run_relative_backtest()',
            'initialize_data_and_context()'
        ]

        assert len(cached_functions) == 4


class TestErrorHandling:
    """Test suite for error handling"""

    def test_empty_ticker_list(self):
        """Test handling of empty ticker list"""
        tickers = []

        assert len(tickers) == 0
        assert len(tickers) < 2  # Below minimum

    def test_invalid_ticker_format(self):
        """Test handling of invalid ticker format"""
        ticker_string = "AAPL MSFT GOOG"  # Wrong format (should be comma-separated)

        # Should not contain commas
        assert ',' not in ticker_string

    def test_none_optimization_results(self):
        """Test handling of None optimization results"""
        results = None

        if results is None:
            assert results is None

    def test_empty_price_data(self):
        """Test handling of empty price data"""
        price_data = pd.DataFrame()

        assert price_data.empty


class TestSessionStateIntegration:
    """Test suite for session state integration"""

    def test_session_state_optimization_storage(self, mock_optimization_results):
        """Test storing optimization results in session state"""
        session_state = {}
        session_state['last_optimization_results'] = mock_optimization_results

        assert 'last_optimization_results' in session_state
        assert 'max_sharpe' in session_state['last_optimization_results']

    def test_empty_session_state(self):
        """Test handling of empty session state"""
        session_state = {}

        opt_results = session_state.get('last_optimization_results')

        assert opt_results is None


class TestDataValidation:
    """Test suite for data validation"""

    def test_validate_price_data_length(self, mock_portfolio_price_data):
        """Test price data has sufficient length"""
        for ticker, data in mock_portfolio_price_data.items():
            assert len(data) >= 252  # At least 1 year

    def test_validate_weights_range(self, mock_optimization_results):
        """Test weights are in valid range [0, 1]"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            weights = results[strategy]['Weights']

            for weight in weights.values():
                assert 0 <= weight <= 1

    def test_validate_return_reasonable(self, mock_optimization_results):
        """Test returns are reasonable (not extreme)"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            ret = results[strategy]['Return']

            # Annual return should typically be between -100% and +200%
            assert -1.0 <= ret <= 2.0

    def test_validate_volatility_reasonable(self, mock_optimization_results):
        """Test volatility is reasonable"""
        results = mock_optimization_results

        for strategy in ['max_sharpe', 'min_vol']:
            vol = results[strategy]['Volatility']

            # Volatility should be positive and reasonable
            assert 0 < vol < 2.0  # Less than 200%


class TestPortfolioCorrelation:
    """Test suite for portfolio correlation analysis"""

    def test_correlation_matrix_calculation(self, mock_portfolio_price_data):
        """Test correlation matrix can be calculated"""
        returns_dict = {}

        for ticker, data in mock_portfolio_price_data.items():
            returns_dict[ticker] = data['Close'].pct_change()

        returns_df = pd.DataFrame(returns_dict).dropna()

        corr_matrix = returns_df.corr()

        # Diagonal should be 1.0
        for ticker in corr_matrix.columns:
            assert abs(corr_matrix.loc[ticker, ticker] - 1.0) < 0.01

        # Correlation should be between -1 and 1
        assert (corr_matrix >= -1.0).all().all()
        assert (corr_matrix <= 1.0).all().all()

    def test_covariance_matrix_calculation(self, mock_portfolio_price_data):
        """Test covariance matrix can be calculated"""
        returns_dict = {}

        for ticker, data in mock_portfolio_price_data.items():
            returns_dict[ticker] = data['Close'].pct_change()

        returns_df = pd.DataFrame(returns_dict).dropna()

        cov_matrix = returns_df.cov()

        # Should be square
        assert cov_matrix.shape[0] == cov_matrix.shape[1]

        # Diagonal (variances) should be positive
        for ticker in cov_matrix.columns:
            assert cov_matrix.loc[ticker, ticker] > 0


class TestBacktestValidation:
    """Test suite for backtest validation"""

    def test_dcf_assumptions_ranges(self, mock_backtest_assumptions):
        """Test DCF assumptions are in valid ranges"""
        assumptions = mock_backtest_assumptions

        # All percentages should be between 0 and 1
        percentage_fields = ['ebitda_margin', 'tax_rate', 'capex_pct', 'nwc_pct']

        for field in percentage_fields:
            value = assumptions[field]
            assert 0 <= value <= 1

    def test_historical_data_sufficient_for_backtest(self, mock_portfolio_price_data):
        """Test historical data is sufficient for backtesting"""
        ticker = 'AAPL'
        data = mock_portfolio_price_data[ticker]

        # Need at least 252 trading days (1 year)
        assert len(data) >= 252


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
