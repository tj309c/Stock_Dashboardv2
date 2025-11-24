import importlib.util
import os

# Compatibility shim so tests can import `news_sentiment_page` directly
_path = os.path.join(os.path.dirname(__file__), 'pages', '08_📰_News_&_Sentiment.py')
spec = importlib.util.spec_from_file_location('news_sentiment_page', _path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

# Re-export public symbols
for _name in dir(_mod):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_mod, _name)

__all__ = [n for n in dir() if not n.startswith('_')]

# Expose a couple of helper entrypoints at module-level so tests can patch them
try:
    from ai_model_config import get_configured_model, call_ai_model  # type: ignore
    globals()['get_configured_model'] = get_configured_model
    globals()['call_ai_model'] = call_ai_model
except Exception:
    # Be permissive in tests where ai_model_config might be patched
    pass

try:
    from ticker_utils import render_ticker_input_with_quick_picks, setup_sidebar_ticker_input  # type: ignore
    globals()['render_ticker_input_with_quick_picks'] = render_ticker_input_with_quick_picks
    globals()['setup_sidebar_ticker_input'] = setup_sidebar_ticker_input
except Exception:
    pass
