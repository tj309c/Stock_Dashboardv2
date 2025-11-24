import importlib.util
import os

# Compatibility shim so tests can import `individual_charts_page` directly
_path = os.path.join(os.path.dirname(__file__), 'pages', '02_📈_Individual_Charts_&_Visuals.py')
spec = importlib.util.spec_from_file_location('individual_charts_page', _path)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

# Re-export public symbols
for _name in dir(_mod):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_mod, _name)

__all__ = [n for n in dir() if not n.startswith('_')]
