"""
Unit Tests for Configuration
"""
import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.config import get_config, COLORS, DEFAULT_TICKERS
from src.config.constants import RSI_OVERSOLD, CACHE_TTL


def test_config_initialization():
    """Test configuration initialization"""
    config = get_config()
    assert config is not None
    assert hasattr(config, 'env')


def test_config_get():
    """Test getting configuration values"""
    config = get_config()
    
    # Test dot notation access
    app_name = config.get("app.name")
    assert app_name is not None
    
    # Test default value
    fake_value = config.get("fake.key", default="default")
    assert fake_value == "default"


def test_config_properties():
    """Test configuration properties"""
    config = get_config()
    
    assert isinstance(config.is_debug, bool)
    assert isinstance(config.is_cache_enabled, bool)
    assert isinstance(config.cache_ttl, int)


def test_constants():
    """Test constants are accessible"""
    assert RSI_OVERSOLD == 30
    assert CACHE_TTL == 300
    assert isinstance(COLORS, dict)
    assert "bullish_green" in COLORS


def test_default_tickers():
    """Test default tickers"""
    assert "stocks" in DEFAULT_TICKERS
    assert "options" in DEFAULT_TICKERS
    assert "crypto" in DEFAULT_TICKERS


# Run with: python tests/test_config.py
if __name__ == "__main__":
    print("🧪 Running Configuration Tests...\n")
    
    try:
        test_config_initialization()
        print("✅ test_config_initialization passed")
    except Exception as e:
        print(f"❌ test_config_initialization failed: {e}")
    
    try:
        test_config_get()
        print("✅ test_config_get passed")
    except Exception as e:
        print(f"❌ test_config_get failed: {e}")
    
    try:
        test_config_properties()
        print("✅ test_config_properties passed")
    except Exception as e:
        print(f"❌ test_config_properties failed: {e}")
    
    try:
        test_constants()
        print("✅ test_constants passed")
    except Exception as e:
        print(f"❌ test_constants failed: {e}")
    
    try:
        test_default_tickers()
        print("✅ test_default_tickers passed")
    except Exception as e:
        print(f"❌ test_default_tickers failed: {e}")
    
    print("\n✅ All tests completed!")
