import importlib
import pandas as pd


def make_hist(values=(10, 10.5, 11)):
    idx = pd.date_range(end=pd.Timestamp.today(), periods=len(values))
    return pd.DataFrame({'Adj Close': list(values), 'Close': list(values)}, index=idx)


def test_fetch_factor_data_uses_alias_fallback(monkeypatch):
    mod = importlib.import_module('correlation_factors')

    # Simulate primary download returning empty, alias download returning data
    def fake_download(sym, start=None, end=None, progress=False):
        if sym == 'DX-Y.NYB':
            return pd.DataFrame()
        elif sym == 'DX=F' or sym == 'DXY':
            return make_hist()
        return pd.DataFrame()

    monkeypatch.setattr('correlation_factors.yf.download', fake_download)

    series = mod.fetch_factor_data('DX-Y.NYB', days=30)

    assert not series.empty
    assert isinstance(series, pd.Series)
