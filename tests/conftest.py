"""
Pytest configuration and fixtures for Stock Analysis Dashboard tests
"""
import pytest
import os
import streamlit as st

# Set environment variables before any imports
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Clear Streamlit cache before each test to ensure test isolation"""
    # Clear all Streamlit caches before each test
    st.cache_data.clear()
    st.cache_resource.clear()

    yield

    # Clear again after test
    st.cache_data.clear()
    st.cache_resource.clear()


@pytest.fixture
def mock_stock_info():
    """Fixture providing valid mock stock info data"""
    return {
        'symbol': 'AAPL',
        'longName': 'Apple Inc.',
        'shortName': 'Apple',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 2_500_000_000_000,
        'country': 'United States',
        'website': 'https://www.apple.com',
        'fullTimeEmployees': 164000
    }


@pytest.fixture
def mock_invalid_stock_info():
    """Fixture providing invalid mock stock info (missing required fields)"""
    return {
        'shortName': 'Invalid Company'
        # Missing longName and marketCap
    }
