import os
from pathlib import Path


IGNORED_DIRS = {'.git', '__pycache__', 'htmlcov', '.venv', 'venv', '.pytest_cache', 'docs', 'tests'}


def _iter_python_files(base: Path):
    for root, dirs, files in os.walk(base):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for f in files:
            if f.endswith('.py'):
                yield Path(root) / f


def test_no_use_container_width_literals_in_repo():
    """Fail if any source files contain the deprecated kwarg literal.

    This prevents accidental regressions where we reintroduce the 'use_container_width=True'
    kwarg anywhere in the repository. The search intentionally scans all .py files.
    """
    base = Path(__file__).resolve().parents[1]
    offenders = []

    for file_path in _iter_python_files(base):
        try:
            text = file_path.read_text(encoding='utf-8')
        except Exception:
            # Best-effort read; skip unreadable files
            continue

        if 'use_container_width=True' in text:
            offenders.append(str(file_path.relative_to(base)))

    assert not offenders, (
        "Found 'use_container_width=True' in the following files:\n" + "\n".join(offenders)
    )
