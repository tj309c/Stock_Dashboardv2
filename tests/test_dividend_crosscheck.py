import pytest
from unittest.mock import patch, Mock


@pytest.mark.unit
def test_get_dividend_values_yfinance_only():
    from data_fetcher import get_dividend_values

    mock_info = {'dividendYield': 0.038, 'dividendRate': 1.00, 'currentPrice': 26.32}

    with patch('data_fetcher.get_stock_object') as mock_get_stock:
        mock_stock = Mock()
        mock_stock.info = mock_info
        mock_get_stock.return_value = mock_stock

        # Ensure yahooquery path is not used
        with patch('data_fetcher.YAHOOQUERY_AVAILABLE', False):
            res = get_dividend_values('AAPL')

    assert 'yfinance' in res
    y = res['yfinance']
    assert isinstance(y, dict)
    expected = (1.0 / 26.32) * 100.0
    assert y.get('computedYieldPct') == pytest.approx(expected, rel=1e-6)


@pytest.mark.unit
def test_get_dividend_values_with_yahooquery_and_fmp_and_finnhub(monkeypatch):
    from data_fetcher import get_dividend_values

    # Mock yfinance info
    mock_info = {'dividendYield': None, 'dividendRate': None, 'currentPrice': 100.0}

    with patch('data_fetcher.get_stock_object') as mock_get_stock:
        mock_stock = Mock()
        mock_stock.info = mock_info
        mock_get_stock.return_value = mock_stock

        # Mock yahooquery provider by injecting a fake module into sys.modules
        mocked_yq = {'AAPL': {'dividendYield': 0.02, 'dividendRate': 2.0, 'regularMarketPrice': 100.0}}

        import sys
        fake_mod = Mock()
        fake_mod.get_multiple_tickers_info = Mock(return_value=mocked_yq)
        sys.modules['fast_data_fetcher'] = fake_mod

        with patch('data_fetcher.YAHOOQUERY_AVAILABLE', True):
            with patch('fast_data_fetcher.get_multiple_tickers_info', return_value=mocked_yq):
                # Mock FMP response
                class FakeResp:
                    def __init__(self, j):
                        self._j = j

                    @property
                    def ok(self):
                        return True

                    def json(self):
                        return self._j

                def fake_get(url, timeout):
                    if 'financialmodelingprep' in url:
                        return FakeResp([{'dividendYield': 0.021, 'lastDiv': 2.1, 'price': 100.0}])
                    if 'finnhub' in url:
                        return FakeResp([{'amount': 2.0}])
                    return FakeResp({})

                with patch('data_fetcher.requests.get', side_effect=fake_get):
                    # Provide mock secrets
                    with patch('data_fetcher.st', new=Mock(secrets={'FMP_API_KEY': 'x', 'FINNHUB_API_KEY': 'y'})):
                        res = get_dividend_values('AAPL')

    # Expect yfinance and yahooquery and fmp and finnhub keys present
    assert 'yfinance' in res and 'yahooquery' in res and 'fmp' in res and 'finnhub' in res

    # Yahooquery should give ~2.0% computed
    yq = res['yahooquery']
    assert pytest.approx(yq.get('computedYieldPct'), rel=1e-6) == 2.0


@pytest.mark.unit
def test_compare_dividend_values_flags_mismatch():
    from data_fetcher import compare_dividend_values

    div_map = {
        'a': {'computedYieldPct': 1.0},
        'b': {'computedYieldPct': 3.5},
        'c': {'computedYieldPct': None}
    }

    out = compare_dividend_values(div_map, threshold_pct_points=1.0)
    assert out['mismatch'] is True
    assert out['min'] == pytest.approx(1.0)
    assert out['max'] == pytest.approx(3.5)
