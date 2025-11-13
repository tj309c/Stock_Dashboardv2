import os
import importlib
from pathlib import Path

print('Running import test for all top-level .py files (excluding pages/)...')
errors = []
for p in Path('.').glob('*.py'):
    name = p.stem
    if name == '__init__':
        continue
    try:
        importlib.reload(importlib.import_module(name))
        print('OK', name)
    except Exception as e:
        print('ERROR', name, ':', type(e).__name__, e)
        errors.append((name, type(e).__name__, str(e)))

print('\nSummary:')
print(f'  Total files checked: {len(list(Path('.').glob("*.py")))-1}')
print(f'  Errors found: {len(errors)}')
for name, etype, msg in errors:
    print(f'   - {name}: {etype}: {msg}')

# Exit with non-zero if errors found
import sys
sys.exit(1 if errors else 0)
