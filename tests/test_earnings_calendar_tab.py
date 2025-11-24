import importlib
from unittest.mock import Mock


def test_render_earnings_calendar_handles_missing_eps_keys(monkeypatch):
    """Ensure the earnings calendar renderer doesn't raise NameError when EPS keys are absent."""
    # Import the page module where the earnings tab implementation lives
    mod = importlib.import_module('pages.02_📈_Stock_Analysis')

    # Create a mock stock with calendar that lacks EPS keys
    mock_stock = Mock()
    mock_stock.calendar = {
        'Earnings Date': None,
        'Revenue Average': 1000000000,
        # Intentionally omit 'Earnings Average', 'Earnings Low', 'Earnings High'
    }
    # earnings_dates table with at least some rows for the historical chart
    import pandas as pd
    idx = pd.to_datetime(['2024-10-30', '2024-07-30'])
    mock_stock.earnings_dates = pd.DataFrame({
        'EPS Estimate': [2.28, 1.5],
        'Reported EPS': [2.28, 1.4],
        'Surprise(%)': [2.3, -6.7]
    }, index=idx)

    # Provide a small price history covering the dates
    price_idx = pd.to_datetime(['2024-07-25', '2024-07-30', '2024-10-25', '2024-10-30'])
    mock_price_df = pd.DataFrame({'Close': [98.0, 100.0, 120.0, 124.0]}, index=price_idx)
    mock_stock.history = Mock(return_value=mock_price_df)

    # Patch yf.Ticker to return our mock
    monkeypatch.setattr(mod, 'yf', Mock(Ticker=Mock(return_value=mock_stock)))

    # Provide a dummy streamlit-like API (safely swallow calls)
    dummy_st = Mock()
    # columns should return an iterable of 4 mock column objects
    class DummyCol:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def __getattr__(self, name):
            return Mock()

    def columns_factory(n=1):
        return tuple(DummyCol() for _ in range(n))

    dummy_st.columns = lambda n=1: columns_factory(n)
    for method in ['metric', 'markdown', 'caption', 'plotly_chart', 'table', 'info', 'error', 'stop', 'divider', 'warning', 'write', 'caption']:
        setattr(dummy_st, method, Mock())

    # expander must be a context manager and controls should return values used by page
    class DummyExpander:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    dummy_st.expander = lambda *args, **kwargs: DummyExpander()
    dummy_st.checkbox = Mock(return_value=True)
    dummy_st.number_input = Mock(return_value=3)

    # Provide a basic container object so display_dataframe_full_width works
    class DummyContainer:
        def dataframe(self, *args, **kwargs):
            return None

    dummy_st.container = lambda *args, **kwargs: DummyContainer()

    monkeypatch.setattr(mod, 'st', dummy_st)
    # app_utils uses its own imported 'st' instance; patch that too so helper wrappers don't call real streamlit
    monkeypatch.setattr('app_utils.st', dummy_st)

    # Call the function — should not raise NameError
    try:
        # The Stock Analysis page implements the earnings view as render_earnings_estimates_tab
        mod.render_earnings_estimates_tab('AAPL')
    except NameError as e:
        raise AssertionError(f"NameError raised during rendering: {e}")
