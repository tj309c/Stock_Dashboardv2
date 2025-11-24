import pandas as pd
import correlation_factors as cf


def fake_fetch(ticker, days=365):
    # Return a small but unique series per ticker so we can assert correct mapping
    idx = pd.date_range(end=pd.Timestamp('2025-01-01'), periods=50)
    # Create values unique to ticker using position-weighted ASCII codes to avoid simple collisions
    base = sum((i + 1) * ord(c) for i, c in enumerate(ticker)) % 1000
    series = pd.Series([base + i * 0.01 for i in range(len(idx))], index=idx)
    return series


def test_fetch_all_factors_parallel_unique_mapping(monkeypatch):
    factors = {
        'Volatility (VIX)': '^VIX',
        '10-Year Treasury': '^TNX',
        'US Dollar (DXY)': 'DX-Y.NYB',
        'Gold': 'GC=F',
        'Oil (WTI)': 'CL=F'
    }

    # Patch the fetch_factor_data to our fake that returns distinct series per ticker
    monkeypatch.setattr(cf, 'fetch_factor_data', fake_fetch)

    results = cf.fetch_all_factors_parallel(factors, days=90)

    # Ensure returned keys match the factor names and series are unique per key
    assert set(results.keys()) == set(factors.keys())

    # Ensure series differ for at least one pair (i.e. not all identical)
    values = [list(s.values)[:3] for s in results.values()]
    unique_values = set(tuple(v) for v in values)
    assert len(unique_values) == len(values), "Expected unique series per factor"
