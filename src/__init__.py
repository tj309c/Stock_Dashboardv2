"""
StocksV2 Dashboard Application
Professional stock, options, and crypto analysis platform
"""
__version__ = "2.0.0"
__author__ = "StocksV2 Team"

# Make src directory importable
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
