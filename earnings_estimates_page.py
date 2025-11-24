import importlib.util
import os

# Compatibility shim so tests can import `earnings_estimates_page` directly
_path = os.path.join(os.path.dirname(__file__), 'pages', '09_📅_Earnings_&_Estimates.py')
spec = importlib.util.spec_from_file_location('earnings_estimates_page', _path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

# Re-export public symbols
for _name in dir(_mod):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_mod, _name)

__all__ = [n for n in dir() if not n.startswith('_')]

# Make render_ticker_input_with_quick_picks available at module level for tests
try:
    from ticker_utils import render_ticker_input_with_quick_picks  # type: ignore
    globals()['render_ticker_input_with_quick_picks'] = render_ticker_input_with_quick_picks
except Exception:
    pass
