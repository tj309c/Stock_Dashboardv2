"""
Custom Exception Classes
Better error handling with specific exception types
"""


class StockAnalysisError(Exception):
    """Base exception for stock analysis errors"""
    pass


class DataFetchError(StockAnalysisError):
    """Error fetching market data"""
    pass


class AnalysisError(StockAnalysisError):
    """Error during analysis calculations"""
    pass


class ValuationError(StockAnalysisError):
    """Error during valuation calculations"""
    pass


class APIError(StockAnalysisError):
    """Error calling external APIs"""
    pass


class InvalidTickerError(DataFetchError):
    """Invalid ticker symbol"""
    pass


class InsufficientDataError(AnalysisError):
    """Insufficient data for analysis"""
    pass


class ConfigurationError(StockAnalysisError):
    """Configuration or setup error"""
    pass


# Usage Examples:
"""
# Example 1: Specific error handling
try:
    data = fetch_stock_data(ticker)
except InvalidTickerError as e:
    st.error(f"❌ Invalid ticker: {ticker}")
except DataFetchError as e:
    st.error(f"❌ Could not fetch data: {str(e)}")
except APIError as e:
    st.warning(f"⚠️ API temporarily unavailable: {str(e)}")

# Example 2: Raising specific errors
def calculate_dcf(financials):
    if not financials.get('free_cash_flow'):
        raise InsufficientDataError("Free cash flow data required for DCF")
    
    if financials['free_cash_flow'] < 0:
        raise ValuationError("Cannot value negative FCF with standard DCF")
"""
