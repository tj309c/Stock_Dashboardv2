import pandas as pd
import importlib
from unittest.mock import Mock


def make_sample_hist(values=(100, 101, 102)):
    idx = pd.date_range(end=pd.Timestamp.today(), periods=len(values))
    return pd.DataFrame({'Close': list(values), 'Volume': [1000] * len(values)}, index=idx)


def test_fetch_market_indices_uses_download_when_history_empty(monkeypatch):
    # Import the page module where fetch_market_indices is defined
    mod = importlib.import_module('pages.01_📊_Market_Overview_&_Economy')

    # Simulate yf.Ticker.history returning empty for the VIX (and others)
    class DummyTicker:
        def __init__(self, sym):
            self.sym = sym

        def history(self, period='5d'):
            # Return empty for all index calls to force the fallback
            return pd.DataFrame()

    # Monkeypatch yf.Ticker to our DummyTicker
    monkeypatch.setattr('pages.01_📊_Market_Overview_&_Economy.yf.Ticker', DummyTicker)

    # Monkeypatch yf.download to return a valid small history when called
    def dummy_download(sym, period='5d', progress=False):
        # Return sample data for any symbol passed
        return make_sample_hist()

    monkeypatch.setattr('pages.01_📊_Market_Overview_&_Economy.yf.download', dummy_download)

    # Call fetch_market_indices and ensure each requested index is present
    results = mod.fetch_market_indices()

    # Expect at minimum VIX to be present and include 'price' key
    assert 'VIX' in results
    assert isinstance(results['VIX']['history'], pd.DataFrame)
    assert 'Close' in results['VIX']['history'].columns
