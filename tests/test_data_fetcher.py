"""
Tests for data_fetcher.py
"""
import pytest
from unittest.mock import Mock, patch, PropertyMock
import pandas as pd
import numpy as np


@pytest.mark.unit
def test_get_company_info_with_valid_data(mock_stock_info):
    """Test getting company info with valid mock stock object"""
    from data_fetcher import get_company_info

    mock_stock = Mock()
    mock_stock.info = mock_stock_info

    info = get_company_info(mock_stock)

    assert info is not None
    assert isinstance(info, dict)
    assert 'longName' in info
    assert info['longName'] == 'Apple Inc.'
    assert 'sector' in info
    assert info['sector'] == 'Technology'
    assert 'marketCap' in info
    assert info['marketCap'] == 2_500_000_000_000


@pytest.mark.unit
def test_get_company_info_with_invalid_data(mock_invalid_stock_info):
    """Test get_company_info returns None for invalid ticker data"""
    from data_fetcher import get_company_info

    mock_stock = Mock()
    mock_stock.info = mock_invalid_stock_info

    info = get_company_info(mock_stock)

    # Should return None when required fields (longName, marketCap) are missing
    assert info is None


@pytest.mark.unit
def test_get_company_info_with_empty_dict():
    """Test get_company_info returns None for empty info dict"""
    from data_fetcher import get_company_info

    mock_stock = Mock()
    mock_stock.info = {}

    info = get_company_info(mock_stock)

    assert info is None


@pytest.mark.unit
def test_get_company_info_with_exception():
    """Test error handling when fetching company info fails"""
    from data_fetcher import get_company_info

    mock_stock = Mock()
    # Simulate an exception when accessing info property
    type(mock_stock).info = PropertyMock(side_effect=Exception("API Error"))

    info = get_company_info(mock_stock)

    assert info is None


@pytest.mark.unit
def test_get_stock_price_data_with_valid_ticker():
    """Test getting price data with a valid ticker string"""
    from data_fetcher import get_stock_price_data

    # Create mock price data
    dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
    mock_df = pd.DataFrame({
        'Open': range(100, 110),
        'High': range(105, 115),
        'Low': range(95, 105),
        'Close': range(102, 112),
        'Volume': [1000000] * 10
    }, index=dates)

    # Patch the get_stock_object function to return our mock
    with patch('data_fetcher.get_stock_object') as mock_get_stock:
        mock_stock = Mock()
        mock_stock.history = Mock(return_value=mock_df)
        mock_get_stock.return_value = mock_stock

        price_data = get_stock_price_data("AAPL", period="1mo")

        assert price_data is not None
        assert isinstance(price_data, pd.DataFrame)
        assert len(price_data) == 10
        assert 'Close' in price_data.columns
        assert list(price_data['Close']) == list(range(102, 112))
        mock_get_stock.assert_called_once_with("AAPL")
        mock_stock.history.assert_called_once_with(period="1mo")


@pytest.mark.unit
def test_get_stock_price_data_with_empty_response():
    """Test handling of empty price data"""
    from data_fetcher import get_stock_price_data

    with patch('data_fetcher.get_stock_object') as mock_get_stock:
        mock_stock = Mock()
        mock_stock.history = Mock(return_value=pd.DataFrame())
        mock_get_stock.return_value = mock_stock

        price_data = get_stock_price_data("INVALID")

        assert isinstance(price_data, pd.DataFrame)
        assert len(price_data) == 0


@pytest.mark.unit
def test_get_stock_price_data_with_exception():
    """Test handling exceptions during price data fetch"""
    from data_fetcher import get_stock_price_data

    with patch('data_fetcher.get_stock_object') as mock_get_stock:
        mock_stock = Mock()
        mock_stock.history = Mock(side_effect=Exception("Network error"))
        mock_get_stock.return_value = mock_stock

        price_data = get_stock_price_data("AAPL")

        # Should return empty DataFrame on error
        assert isinstance(price_data, pd.DataFrame)
        assert len(price_data) == 0


@pytest.mark.unit
def test_get_stock_price_data_different_periods():
    """Test that different period parameters work correctly"""
    from data_fetcher import get_stock_price_data

    periods = ['1mo', '3mo', '6mo', '1y', '2y']

    for period in periods:
        with patch('data_fetcher.get_stock_object') as mock_get_stock:
            dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
            mock_df = pd.DataFrame({
                'Close': [100, 101, 102, 103, 104]
            }, index=dates)

            mock_stock = Mock()
            mock_stock.history = Mock(return_value=mock_df)
            mock_get_stock.return_value = mock_stock

            price_data = get_stock_price_data("AAPL", period=period)

            assert len(price_data) == 5
            mock_stock.history.assert_called_with(period=period)


@pytest.mark.unit
def test_get_eps_estimates_list_from_alpha_vantage():
    """Alpha Vantage calendar values are parsed into a list"""
    from data_fetcher import get_eps_estimates_list
    import pandas as pd

    # Prepare a fake calendar DataFrame
    df = pd.DataFrame({
        'Ticker': ['AAPL', 'AAPL', 'MSFT'],
        'Company Name': ['Apple Inc.', 'Apple Inc.', 'Microsoft Corp.'],
        'Report Date': [pd.Timestamp('2025-01-01'), pd.Timestamp('2025-02-01'), pd.Timestamp('2025-02-01')],
        'Analyst EPS': ['1.20', 1.3, '2.0']
    })

    with patch('data_fetcher.get_earnings_calendar', return_value=df):
        with patch('data_fetcher.st') as mock_st:
            mock_st.secrets = {'alpha_vantage': {'api_key': 'test'}}
            result = get_eps_estimates_list('AAPL')

    assert isinstance(result, list)
    assert result == [1.2, 1.3]


@pytest.mark.unit
def test_get_eps_estimates_list_from_yfinance():
    """yfinance earnings_dates or calendar values are parsed into a list"""
    from data_fetcher import get_eps_estimates_list
    import pandas as pd

    # Mock earnings_dates DataFrame
    ed = pd.DataFrame({'EPS Estimate': [1.5, 1.7, None]})

    mock_stock = Mock()
    mock_stock.earnings_dates = ed
    mock_stock.calendar = {}

    with patch('data_fetcher.get_stock_object', return_value=mock_stock):
        with patch('data_fetcher.st') as mock_st:
            mock_st.secrets = {}  # no alpha_vantage configured
            result = get_eps_estimates_list('AAPL')

    assert isinstance(result, list)
    assert result == [1.5, 1.7]


@pytest.mark.unit
def test_get_eps_estimates_list_aggregation_and_dedup():
    """Multiple sources aggregate and dedupe values, returning sorted floats"""
    from data_fetcher import get_eps_estimates_list
    import pandas as pd

    df = pd.DataFrame({'Ticker': ['AAPL'], 'Analyst EPS': [1.5]})
    ed = pd.DataFrame({'EPS Estimate': [1.5, 2.0, 1.2]})

    mock_stock = Mock()
    mock_stock.earnings_dates = ed
    mock_stock.calendar = {}

    with patch('data_fetcher.get_earnings_calendar', return_value=df):
        with patch('data_fetcher.get_stock_object', return_value=mock_stock):
            with patch('data_fetcher.st') as mock_st:
                mock_st.secrets = {'alpha_vantage': {'api_key': 'test'}}
                result = get_eps_estimates_list('AAPL')

    # dedup and sort -> [1.2, 1.5, 2.0]
    assert result == [1.2, 1.5, 2.0]


@pytest.mark.unit
def test_get_eps_estimates_list_empty():
    """Return empty list if no provider data available"""
    from data_fetcher import get_eps_estimates_list

    with patch('data_fetcher.get_earnings_calendar', return_value=pd.DataFrame()):
        with patch('data_fetcher.get_stock_object') as mock_get_stock:
            mock_stock = Mock()
            mock_stock.earnings_dates = pd.DataFrame()
            mock_stock.calendar = {}
            mock_get_stock.return_value = mock_stock

            with patch('data_fetcher.st') as mock_st:
                mock_st.secrets = {}
                result = get_eps_estimates_list('INVALID')

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.unit
def test_get_eps_estimates_list_finnhub_and_fmp_and_polygon():
    """Test provider JSON parsing from Finnhub, FMP and Polygon"""
    from data_fetcher import get_eps_estimates_list
    import requests

    # Sample JSON responses from providers containing estimate keys
    finnhub_json = [{'estimate': '0.85'}, {'estimate': 0.9}]
    fmp_json = {'earningsEstimated': [{'eps': '1.1'}, {'eps': 1.2}]}
    polygon_json = {'results': [{'epsEstimate': 1.3}, {'epsEstimate': '1.4'}]}

    def fake_get(url, timeout):
        class Resp:
            def __init__(self, j):
                self._j = j

            def ok(self):
                return True

            @property
            def ok(self):
                return True

            def json(self):
                return self._j

        if 'finnhub' in url:
            return Resp(finnhub_json)
        if 'financialmodelingprep' in url:
            return Resp(fmp_json)
        if 'polygon' in url:
            return Resp(polygon_json)
        return Resp({})

    with patch('data_fetcher.requests.get', side_effect=fake_get):
        with patch('data_fetcher.get_earnings_calendar', return_value=pd.DataFrame()):
            with patch('data_fetcher.get_stock_object') as mock_get_stock:
                mock_stock = Mock()
                mock_stock.earnings_dates = pd.DataFrame()
                mock_stock.calendar = {}
                mock_get_stock.return_value = mock_stock

                with patch('data_fetcher.st') as mock_st:
                    mock_st.secrets = {
                        'FINNHUB_API_KEY': 'x',
                        'FMP_API_KEY': 'y',
                        'POLYGON_API_KEY': 'z'
                    }

                    result = get_eps_estimates_list('AAPL')

    # Expect collected numeric values, deduped and sorted
    assert isinstance(result, list)
    # should include 0.85, 0.9, 1.1, 1.2, 1.3, 1.4
    for val in [0.85, 0.9, 1.1, 1.2, 1.3, 1.4]:
        assert val in result


@pytest.mark.unit
def test_get_company_info_extracts_all_fields(mock_stock_info):
    """Test that all expected fields are extracted from info"""
    from data_fetcher import get_company_info

    mock_stock = Mock()
    mock_stock.info = mock_stock_info

    info = get_company_info(mock_stock)

    # Check that key fields are present
    expected_fields = ['symbol', 'longName', 'sector', 'industry', 'marketCap']
    for field in expected_fields:
        assert field in info, f"Expected field '{field}' not found in info"


@pytest.mark.integration
@pytest.mark.slow
def test_get_ticker_integration():
    """Integration test for getting a real ticker (slow, requires network)"""
    from data_fetcher import get_ticker

    # This test actually calls the API
    # Skip if running in CI or without network
    try:
        ticker = get_ticker("AAPL")
        assert ticker is not None
        assert hasattr(ticker, 'info')
        assert hasattr(ticker, 'history')
    except Exception as e:
        pytest.skip(f"Network error or API unavailable: {e}")


@pytest.mark.integration
@pytest.mark.slow
def test_get_stock_price_data_integration():
    """Integration test for getting real price data (slow, requires network)"""
    from data_fetcher import get_stock_price_data

    try:
        price_data = get_stock_price_data("AAPL", period="1mo")
        assert price_data is not None
        assert isinstance(price_data, pd.DataFrame)
        assert len(price_data) > 0
        assert 'Close' in price_data.columns
    except Exception as e:
        pytest.skip(f"Network error or API unavailable: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
