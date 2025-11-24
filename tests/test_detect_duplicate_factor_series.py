import pandas as pd
import numpy as np
import correlation_factors as cf


def _series(base):
    idx = pd.date_range('2025-01-01', periods=10)
    return pd.Series([base + i * 0.1 for i in range(10)], index=idx)


def test_detect_duplicate_series_groups():
    factors = {
        'A': _series(1.0),
        'B': _series(2.0),
        'C': _series(1.0),  # identical to A
        'D': _series(3.0)
    }

    groups = cf.detect_duplicate_factor_series(factors)

    # A should list C as duplicate (order may vary)
    assert 'A' in groups and 'C' in groups['A'] or 'C' in groups and 'A' in groups['C']
