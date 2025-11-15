# 🏗️ Trading Dashboard Architecture - Comprehensive Refactoring Plan

## Executive Summary

This document outlines the complete architectural refactoring of the Streamlit Trading Dashboard from a monolithic structure (2,300+ lines across 6 files with 40% duplication) to a modular, testable, and maintainable system following SOLID principles and separation of concerns.

**Timeline:** 200-250 hours over 4-6 months (phased approach)  
**Strategy:** Build new architecture alongside existing code, migrate incrementally  
**Goal:** Professional-grade codebase with 80%+ test coverage

---

## 📁 1. New Project Structure

```
StocksV2/
│
├── core/                           # Core business logic (NO Streamlit imports)
│   ├── __init__.py
│   ├── types.py                    # Type definitions & dataclasses
│   ├── errors.py                   # Custom exceptions
│   ├── logging.py                  # Centralized logging
│   │
│   ├── data/                       # Data layer abstraction
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract base classes
│   │   ├── yfinance_fetcher.py    # YFinance implementation
│   │   ├── cache.py                # Caching layer
│   │   └── validators.py          # Data validation
│   │
│   └── business/                   # Pure business logic
│       ├── __init__.py
│       ├── valuation/              # Valuation models
│       │   ├── __init__.py
│       │   ├── dcf.py             # DCF calculations
│       │   ├── multiples.py       # Multiples valuation
│       │   ├── ddm.py             # Dividend discount model
│       │   └── monte_carlo.py     # Monte Carlo simulation
│       │
│       ├── technical/              # Technical analysis
│       │   ├── __init__.py
│       │   ├── indicators.py      # RSI, MACD, etc.
│       │   ├── patterns.py        # Chart patterns
│       │   └── signals.py         # Buy/sell signals
│       │
│       ├── sentiment/              # Sentiment analysis
│       │   ├── __init__.py
│       │   ├── scraper.py         # Web scraping
│       │   └── analyzer.py        # Sentiment scoring
│       │
│       └── risk/                   # Risk metrics
│           ├── __init__.py
│           ├── metrics.py         # Beta, Sharpe, etc.
│           └── portfolio.py       # Portfolio risk
│
├── services/                       # Service/orchestration layer
│   ├── __init__.py
│   ├── analysis_service.py        # Orchestrates analysis
│   ├── portfolio_service.py       # Portfolio operations
│   ├── options_service.py         # Options analysis
│   └── crypto_service.py          # Crypto analysis
│
├── ui/                             # Streamlit UI layer (ONLY UI code)
│   ├── __init__.py
│   ├── components/                 # Reusable UI components
│   │   ├── __init__.py
│   │   ├── charts.py              # Chart renderers
│   │   ├── tables.py              # Table components
│   │   ├── forms.py               # Input forms
│   │   └── alerts.py              # Alert/notification UI
│   │
│   ├── pages/                      # Dashboard pages
│   │   ├── __init__.py
│   │   ├── stocks.py              # Stocks dashboard
│   │   ├── options.py             # Options dashboard
│   │   ├── crypto.py              # Crypto dashboard
│   │   ├── portfolio.py           # Portfolio dashboard
│   │   └── advanced.py            # Advanced analytics
│   │
│   └── utils/                      # UI utilities
│       ├── __init__.py
│       ├── formatters.py          # Display formatting
│       ├── theme.py               # Theming
│       └── validators.py          # Input validation
│
├── tests/                          # Comprehensive test suite
│   ├── __init__.py
│   ├── unit/                       # Unit tests
│   │   ├── test_types.py
│   │   ├── test_data_fetchers.py
│   │   ├── test_valuation.py
│   │   ├── test_technical.py
│   │   └── test_services.py
│   │
│   ├── integration/                # Integration tests
│   │   ├── test_analysis_pipeline.py
│   │   └── test_data_pipeline.py
│   │
│   └── fixtures/                   # Test data
│       ├── mock_data.py
│       └── sample_responses.json
│
├── config/                         # Configuration
│   ├── __init__.py
│   ├── settings.py                # Application settings
│   └── constants.py               # Constants
│
├── migrations/                     # Migration scripts
│   ├── migrate_dashboards.py      # Dashboard migration
│   └── rollback.py                # Rollback utilities
│
├── docs/                           # Documentation
│   ├── api/                       # API documentation
│   ├── guides/                    # User guides
│   └── migration/                 # Migration guides
│
├── main.py                         # Current entry (LEGACY)
├── main_refactored.py             # New entry point
├── ARCHITECTURE.md                # This file
├── MIGRATION_PLAN.md              # Migration strategy
└── requirements.txt               # Dependencies
```

---

## 🎯 2. Type Definitions

### File: `core/types.py`

**Purpose:** Define all core data structures with type safety. Replace magic dictionaries with typed dataclasses.

**Key Classes:**

```python
@dataclass
class StockData:
    """Comprehensive stock data container"""
    ticker: str
    price: float
    volume: int
    market_cap: float
    beta: float
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    history: pd.DataFrame
    timestamp: datetime

@dataclass
class ValuationResult:
    """Valuation calculation result"""
    method: str  # "DCF", "Multiples", "DDM"
    fair_value: float
    current_price: float
    upside_percent: float
    confidence: float  # 0-100
    assumptions: Dict[str, Any]
    breakdown: Dict[str, float]

@dataclass
class TechnicalAnalysis:
    """Technical analysis results"""
    indicators: Dict[str, float]  # RSI, MACD, etc.
    signals: List[Signal]
    support_levels: List[float]
    resistance_levels: List[float]
    trend: str  # "bullish", "bearish", "neutral"

@dataclass
class Signal:
    """Buy/sell signal"""
    type: str  # "buy", "sell", "hold"
    strength: float  # 0-100
    reason: str
    timestamp: datetime

@dataclass
class PortfolioPosition:
    """Single portfolio position"""
    ticker: str
    shares: float
    avg_cost: float
    current_price: float
    market_value: float
    pnl: float
    pnl_percent: float
    weight: float

@dataclass
class PortfolioMetrics:
    """Portfolio-level metrics"""
    total_value: float
    total_cost: float
    total_pnl: float
    sharpe_ratio: float
    beta: float
    volatility: float
    max_drawdown: float
    positions: List[PortfolioPosition]
```

**Dependencies:** None (pure Python + dataclasses)

**Usage Example:**
```python
from core.types import StockData, ValuationResult

# Type-safe data handling
stock = StockData(
    ticker="AAPL",
    price=175.50,
    volume=50_000_000,
    market_cap=2_800_000_000_000,
    beta=1.2,
    pe_ratio=28.5,
    dividend_yield=0.005,
    history=df,
    timestamp=datetime.now()
)

# IDE autocomplete works!
print(f"P/E Ratio: {stock.pe_ratio}")
```

---

## 🔌 3. Data Fetcher Abstraction

### File: `core/data/base.py`

**Purpose:** Abstract interface for all data sources. Makes it easy to swap yfinance for another provider without changing business logic.

**Key Classes:**

```python
class DataFetcher(ABC):
    """Abstract base class for all data fetchers"""
    
    @abstractmethod
    def get_stock_data(self, ticker: str, period: str) -> StockData:
        """Fetch comprehensive stock data"""
        pass
    
    @abstractmethod
    def get_historical_prices(self, ticker: str, start: datetime, end: datetime) -> pd.DataFrame:
        """Fetch historical price data"""
        pass
    
    @abstractmethod
    def get_financials(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """Fetch financial statements"""
        pass
    
    @abstractmethod
    def get_options_chain(self, ticker: str) -> Dict:
        """Fetch options chain data"""
        pass
    
    @abstractmethod
    def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company metadata"""
        pass
```

**Dependencies:** `core.types`, `abc`, `pandas`

---

### File: `core/data/yfinance_fetcher.py`

**Purpose:** Concrete implementation using yfinance API.

**Key Methods:**
- `get_stock_data(ticker, period)` - Comprehensive stock data
- `get_historical_prices(ticker, start, end)` - Price history
- `get_financials(ticker)` - Income statement, balance sheet, cash flow
- `get_options_chain(ticker)` - Options data
- `get_company_info(ticker)` - Company metadata
- `_handle_error(e, context)` - Centralized error handling
- `_validate_ticker(ticker)` - Input validation

**Dependencies:** `core.data.base.DataFetcher`, `core.types`, `core.errors`, `yfinance`

**Usage Example:**
```python
from core.data.yfinance_fetcher import YFinanceDataFetcher

fetcher = YFinanceDataFetcher()
stock_data = fetcher.get_stock_data("AAPL", period="1y")
# Returns typed StockData object
```

---

### File: `core/data/cache.py`

**Purpose:** Centralized caching layer with TTL support.

**Key Classes:**

```python
class CacheManager:
    """Manages data caching with TTL"""
    
    def __init__(self, cache_dir: Path, default_ttl: int = 300):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        pass
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value with TTL"""
        pass
    
    def invalidate(self, key: str):
        """Invalidate cache entry"""
        pass
    
    def clear_expired(self):
        """Remove expired entries"""
        pass

@dataclass
class CacheEntry:
    """Single cache entry"""
    key: str
    value: Any
    timestamp: datetime
    ttl: int
```

**Dependencies:** `pathlib`, `datetime`, `pickle`

---

## 🎬 4. Service Layer

### File: `services/analysis_service.py`

**Purpose:** Orchestrate analysis by combining data fetching, valuation, technical analysis, and sentiment. No Streamlit imports!

**Key Methods:**

```python
class AnalysisService:
    """Orchestrates comprehensive stock analysis"""
    
    def __init__(
        self,
        data_fetcher: DataFetcher,
        cache_manager: CacheManager
    ):
        self.fetcher = data_fetcher
        self.cache = cache_manager
        self.logger = logging.getLogger(__name__)
    
    def analyze_stock(self, ticker: str, period: str = "1y") -> AnalysisResult:
        """
        Comprehensive stock analysis combining:
        - Valuation (DCF, multiples, DDM)
        - Technical analysis (indicators, patterns, signals)
        - Sentiment (news, social media)
        - Risk metrics (beta, Sharpe, volatility)
        
        Returns: AnalysisResult (typed dataclass)
        """
        pass
    
    def calculate_valuation(self, ticker: str) -> ValuationResult:
        """Calculate multi-method valuation"""
        pass
    
    def get_technical_analysis(self, ticker: str) -> TechnicalAnalysis:
        """Get technical indicators and signals"""
        pass
    
    def get_sentiment(self, ticker: str) -> SentimentResult:
        """Aggregate sentiment from multiple sources"""
        pass
    
    def get_risk_metrics(self, ticker: str) -> RiskMetrics:
        """Calculate risk metrics"""
        pass
```

**Dependencies:** `core.data.base.DataFetcher`, `core.business.*`, `core.types`, `core.errors`

**Usage Example:**
```python
from services.analysis_service import AnalysisService
from core.data.yfinance_fetcher import YFinanceDataFetcher

service = AnalysisService(
    data_fetcher=YFinanceDataFetcher(),
    cache_manager=CacheManager()
)

# Get complete analysis
result = service.analyze_stock("AAPL")

# No Streamlit dependency - pure business logic!
print(f"Fair Value: ${result.valuation.fair_value:.2f}")
print(f"Technical Signal: {result.technical.trend}")
```

---

### File: `services/portfolio_service.py`

**Purpose:** Portfolio construction, optimization, and tracking.

**Key Methods:**

```python
class PortfolioService:
    """Portfolio management and optimization"""
    
    def __init__(self, data_fetcher: DataFetcher):
        self.fetcher = data_fetcher
    
    def create_portfolio(self, positions: List[Dict]) -> Portfolio:
        """Create portfolio from positions"""
        pass
    
    def optimize_portfolio(
        self,
        tickers: List[str],
        target_return: float,
        risk_tolerance: str
    ) -> OptimizationResult:
        """Optimize portfolio allocation using Modern Portfolio Theory"""
        pass
    
    def calculate_metrics(self, portfolio: Portfolio) -> PortfolioMetrics:
        """Calculate portfolio-level metrics"""
        pass
    
    def calculate_efficient_frontier(
        self,
        tickers: List[str]
    ) -> pd.DataFrame:
        """Calculate efficient frontier data"""
        pass
    
    def rebalance(
        self,
        current_portfolio: Portfolio,
        target_weights: Dict[str, float]
    ) -> RebalanceResult:
        """Generate rebalancing recommendations"""
        pass
```

**Dependencies:** `core.data.base.DataFetcher`, `core.business.risk`, `scipy`, `numpy`

---

## 🧮 5. Pure Business Logic

### File: `core/business/valuation/dcf.py`

**Purpose:** Discounted Cash Flow valuation models. Pure functions, fully testable.

**Key Functions:**

```python
def calculate_dcf(
    base_cash_flow: float,
    growth_rate: float,
    wacc: float,
    terminal_growth: float,
    projection_years: int,
    cash: float = 0,
    debt: float = 0,
    shares_outstanding: float = 1
) -> ValuationResult:
    """
    Calculate DCF valuation with detailed breakdown.
    
    Pure function - no side effects, fully testable.
    """
    pass

def calculate_wacc(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float,
    tax_rate: float,
    debt_ratio: float,
    cost_of_debt: float
) -> float:
    """Calculate Weighted Average Cost of Capital"""
    pass

def project_cash_flows(
    base_cf: float,
    growth_rates: List[float],
    projection_years: int
) -> List[float]:
    """Project future cash flows"""
    pass

def calculate_terminal_value(
    final_cf: float,
    terminal_growth: float,
    wacc: float
) -> float:
    """Calculate terminal value using Gordon Growth Model"""
    pass

def discount_cash_flows(
    cash_flows: List[float],
    wacc: float
) -> List[float]:
    """Discount cash flows to present value"""
    pass
```

**Dependencies:** None (pure Python + math)

**Usage Example:**
```python
from core.business.valuation.dcf import calculate_dcf

result = calculate_dcf(
    base_cash_flow=5_000_000_000,
    growth_rate=0.10,
    wacc=0.08,
    terminal_growth=0.025,
    projection_years=5,
    cash=20_000_000_000,
    debt=10_000_000_000,
    shares_outstanding=1_000_000_000
)

# Easy to test!
assert result.fair_value > 0
assert result.method == "DCF"
```

---

### File: `core/business/valuation/monte_carlo.py`

**Purpose:** Monte Carlo simulation for probabilistic valuation.

**Key Functions:**

```python
def run_monte_carlo_dcf(
    base_params: Dict[str, float],
    param_distributions: Dict[str, Dict],  # mean, std for each param
    num_simulations: int = 10000,
    random_seed: Optional[int] = None
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation on DCF valuation.
    
    Returns probability distribution of fair values.
    """
    pass

def calculate_confidence_intervals(
    values: np.ndarray,
    confidence_levels: List[float] = [0.50, 0.80, 0.90]
) -> Dict[float, Tuple[float, float]]:
    """Calculate confidence intervals"""
    pass
```

**Dependencies:** `numpy`, `scipy.stats`

---

### File: `core/business/technical/indicators.py`

**Purpose:** Technical indicator calculations (RSI, MACD, etc.)

**Key Functions:**

```python
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    pass

def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD, signal line, and histogram"""
    pass

def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands (upper, middle, lower)"""
    pass

def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    pass

def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    pass

def detect_crossover(
    fast_ma: pd.Series,
    slow_ma: pd.Series
) -> List[Signal]:
    """Detect moving average crossovers"""
    pass
```

**Dependencies:** `pandas`, `numpy`

---

### File: `core/business/technical/patterns.py`

**Purpose:** Chart pattern detection.

**Key Functions:**

```python
def detect_head_and_shoulders(prices: pd.DataFrame) -> Optional[Pattern]:
    """Detect head and shoulders pattern"""
    pass

def detect_double_top_bottom(prices: pd.DataFrame) -> Optional[Pattern]:
    """Detect double top/bottom pattern"""
    pass

def detect_cup_and_handle(prices: pd.DataFrame) -> Optional[Pattern]:
    """Detect cup and handle pattern"""
    pass

def find_support_resistance(
    prices: pd.DataFrame,
    num_levels: int = 3
) -> Tuple[List[float], List[float]]:
    """Find support and resistance levels"""
    pass
```

**Dependencies:** `pandas`, `numpy`, `scipy.signal`

---

## 🎨 6. Streamlit UI Layer

### File: `ui/pages/stocks.py`

**Purpose:** Simplified stocks dashboard that ONLY handles UI rendering. All logic delegated to services.

**Structure:**

```python
from services.analysis_service import AnalysisService
from ui.components.charts import render_price_chart, render_technical_chart
from ui.components.tables import render_valuation_table
from ui.utils.formatters import format_currency, format_percentage

def show_stocks_dashboard():
    """
    Stocks dashboard - ONLY UI code!
    
    Before refactoring: 1252 lines (UI + logic mixed)
    After refactoring: ~200 lines (UI only)
    """
    st.title("📈 Stocks Dashboard")
    
    # Input
    ticker = st.text_input("Ticker", value="AAPL")
    
    if st.button("Analyze"):
        # Call service (no business logic here!)
        with st.spinner("Analyzing..."):
            result = st.session_state.analysis_service.analyze_stock(ticker)
        
        # Render results (pure UI)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Fair Value",
                format_currency(result.valuation.fair_value),
                delta=format_percentage(result.valuation.upside_percent)
            )
        
        with col2:
            st.metric("Technical Signal", result.technical.trend.upper())
        
        with col3:
            st.metric("Confidence", f"{result.valuation.confidence:.0f}%")
        
        # Render charts (delegated to components)
        render_price_chart(result.stock_data.history)
        render_technical_chart(result.technical)
        render_valuation_table(result.valuation)
```

**Dependencies:** `streamlit`, `services.*`, `ui.components.*`, `ui.utils.*`

**Key Benefit:** Dashboard is now ~200 lines instead of 1252 lines!

---

### File: `ui/components/charts.py`

**Purpose:** Reusable chart rendering components.

**Key Functions:**

```python
def render_price_chart(
    history: pd.DataFrame,
    title: str = "Price History",
    height: int = 500
) -> None:
    """Render interactive price chart with volume"""
    pass

def render_technical_chart(
    technical: TechnicalAnalysis,
    height: int = 400
) -> None:
    """Render technical indicators chart"""
    pass

def render_valuation_waterfall(
    valuation: ValuationResult,
    height: int = 400
) -> None:
    """Render DCF valuation waterfall chart"""
    pass

def render_monte_carlo_distribution(
    monte_carlo: MonteCarloResult,
    height: int = 400
) -> None:
    """Render Monte Carlo probability distribution"""
    pass
```

**Dependencies:** `plotly`, `streamlit`, `core.types`

---

### File: `ui/components/tables.py`

**Purpose:** Reusable table components.

**Key Functions:**

```python
def render_valuation_table(valuation: ValuationResult) -> None:
    """Render valuation breakdown table"""
    pass

def render_technical_indicators_table(technical: TechnicalAnalysis) -> None:
    """Render technical indicators table"""
    pass

def render_portfolio_positions_table(portfolio: Portfolio) -> None:
    """Render portfolio positions table"""
    pass
```

**Dependencies:** `streamlit`, `pandas`, `core.types`

---

## ✅ 7. Unit Tests

### File: `tests/unit/test_valuation.py`

**Purpose:** Test valuation models with known inputs/outputs.

**Key Tests:**

```python
import pytest
from core.business.valuation.dcf import calculate_dcf, calculate_wacc

class TestDCF:
    """Test DCF valuation calculations"""
    
    def test_basic_dcf_calculation(self):
        """Test DCF with known values"""
        result = calculate_dcf(
            base_cash_flow=1_000_000,
            growth_rate=0.10,
            wacc=0.08,
            terminal_growth=0.025,
            projection_years=5,
            shares_outstanding=1_000_000
        )
        
        assert result.fair_value > 0
        assert result.method == "DCF"
        assert result.current_price == 0  # No current price provided
    
    def test_dcf_with_cash_and_debt(self):
        """Test DCF with cash and debt adjustments"""
        result = calculate_dcf(
            base_cash_flow=1_000_000,
            growth_rate=0.10,
            wacc=0.08,
            terminal_growth=0.025,
            projection_years=5,
            cash=5_000_000,
            debt=2_000_000,
            shares_outstanding=1_000_000
        )
        
        # Equity value should include cash - debt
        assert result.fair_value > 0
        assert result.breakdown["cash"] == 5_000_000
        assert result.breakdown["debt"] == 2_000_000
    
    def test_dcf_validation_errors(self):
        """Test DCF input validation"""
        # WACC <= terminal growth should raise error
        with pytest.raises(ValueError):
            calculate_dcf(
                base_cash_flow=1_000_000,
                growth_rate=0.10,
                wacc=0.02,
                terminal_growth=0.025,
                projection_years=5,
                shares_outstanding=1_000_000
            )
        
        # Zero shares should raise error
        with pytest.raises(ValueError):
            calculate_dcf(
                base_cash_flow=1_000_000,
                growth_rate=0.10,
                wacc=0.08,
                terminal_growth=0.025,
                projection_years=5,
                shares_outstanding=0
            )
    
    def test_wacc_calculation(self):
        """Test WACC calculation"""
        wacc = calculate_wacc(
            risk_free_rate=0.04,
            beta=1.2,
            market_risk_premium=0.06,
            tax_rate=0.21,
            debt_ratio=0.3,
            cost_of_debt=0.05
        )
        
        # WACC should be reasonable
        assert 0 < wacc < 0.20
        assert isinstance(wacc, float)
```

---

### File: `tests/unit/test_technical.py`

**Purpose:** Test technical indicators with sample data.

**Key Tests:**

```python
import pytest
import pandas as pd
import numpy as np
from core.business.technical.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands
)

class TestTechnicalIndicators:
    """Test technical indicator calculations"""
    
    @pytest.fixture
    def sample_prices(self):
        """Generate sample price data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100)
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(100) * 2),
            index=dates
        )
        return prices
    
    def test_rsi_calculation(self, sample_prices):
        """Test RSI calculation"""
        rsi = calculate_rsi(sample_prices, period=14)
        
        # RSI should be between 0 and 100
        assert (rsi >= 0).all() and (rsi <= 100).all()
        
        # RSI should have NaN for initial period
        assert rsi.iloc[:14].isna().all()
        assert not rsi.iloc[14:].isna().any()
    
    def test_macd_calculation(self, sample_prices):
        """Test MACD calculation"""
        macd, signal, histogram = calculate_macd(sample_prices)
        
        # Should return three series
        assert len(macd) == len(signal) == len(histogram)
        
        # Histogram should equal macd - signal
        np.testing.assert_array_almost_equal(
            histogram.dropna(),
            (macd - signal).dropna()
        )
    
    def test_bollinger_bands(self, sample_prices):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = calculate_bollinger_bands(sample_prices)
        
        # Upper should be above middle, middle above lower
        assert (upper >= middle).all()
        assert (middle >= lower).all()
        
        # Middle should equal SMA
        sma = sample_prices.rolling(20).mean()
        np.testing.assert_array_almost_equal(
            middle.dropna(),
            sma.dropna()
        )
```

---

### File: `tests/unit/test_services.py`

**Purpose:** Test service layer with mocked data fetchers.

**Key Tests:**

```python
import pytest
from unittest.mock import Mock, MagicMock
from services.analysis_service import AnalysisService
from core.types import StockData

class TestAnalysisService:
    """Test analysis service orchestration"""
    
    @pytest.fixture
    def mock_fetcher(self):
        """Create mock data fetcher"""
        fetcher = Mock()
        fetcher.get_stock_data.return_value = StockData(
            ticker="AAPL",
            price=150.0,
            volume=50_000_000,
            market_cap=2_500_000_000_000,
            beta=1.2,
            pe_ratio=25.0,
            dividend_yield=0.005,
            history=pd.DataFrame(),
            timestamp=datetime.now()
        )
        return fetcher
    
    @pytest.fixture
    def service(self, mock_fetcher):
        """Create service with mock fetcher"""
        return AnalysisService(
            data_fetcher=mock_fetcher,
            cache_manager=Mock()
        )
    
    def test_analyze_stock_calls_fetcher(self, service, mock_fetcher):
        """Test that analyze_stock calls data fetcher"""
        service.analyze_stock("AAPL")
        
        # Should call fetcher
        mock_fetcher.get_stock_data.assert_called_once_with("AAPL", "1y")
    
    def test_analyze_stock_returns_analysis_result(self, service):
        """Test that analyze_stock returns AnalysisResult"""
        result = service.analyze_stock("AAPL")
        
        # Should return typed result
        assert hasattr(result, 'valuation')
        assert hasattr(result, 'technical')
        assert hasattr(result, 'sentiment')
        assert hasattr(result, 'risk')
```

---

## 🚨 8. Error Handling & Logging

### File: `core/errors.py`

**Purpose:** Define custom exception hierarchy for better error handling.

**Key Classes:**

```python
class TradingDashboardError(Exception):
    """Base exception for all dashboard errors"""
    pass

class DataFetchError(TradingDashboardError):
    """Error fetching data from external source"""
    def __init__(self, ticker: str, source: str, message: str):
        self.ticker = ticker
        self.source = source
        super().__init__(f"Error fetching {ticker} from {source}: {message}")

class ValidationError(TradingDashboardError):
    """Data validation error"""
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        super().__init__(f"Validation failed for {field}={value}: {reason}")

class CalculationError(TradingDashboardError):
    """Error during calculation"""
    def __init__(self, calculation: str, message: str):
        self.calculation = calculation
        super().__init__(f"Error in {calculation}: {message}")

class InsufficientDataError(TradingDashboardError):
    """Insufficient data for analysis"""
    def __init__(self, required: str, available: str):
        self.required = required
        self.available = available
        super().__init__(f"Need {required}, but only have {available}")
```

**Usage Example:**
```python
from core.errors import DataFetchError

try:
    data = fetcher.get_stock_data("INVALID")
except Exception as e:
    raise DataFetchError("INVALID", "yfinance", str(e))
```

---

### File: `core/logging.py`

**Purpose:** Centralized logging configuration with structured logging.

**Key Functions:**

```python
def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True
) -> None:
    """
    Configure centralized logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        structured: Use structured JSON logging
    """
    pass

def get_logger(name: str) -> logging.Logger:
    """Get logger with consistent configuration"""
    pass

class StructuredLogger:
    """Structured logger with context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def add_context(self, **kwargs):
        """Add context to all subsequent logs"""
        self.context.update(kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info with context"""
        self.logger.info(message, extra={**self.context, **kwargs})
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error with context and exception info"""
        self.logger.error(
            message,
            exc_info=exc_info,
            extra={**self.context, **kwargs}
        )
```

**Usage Example:**
```python
from core.logging import setup_logging, get_logger

# Setup once at app start
setup_logging(log_level="INFO", log_file=Path("logs/app.log"))

# Use in modules
logger = get_logger(__name__)
logger.info("Fetching data for ticker", ticker="AAPL", period="1y")
logger.error("Failed to fetch data", ticker="AAPL", error=str(e))
```

---

## 🔄 9. Migration Path

### Document: `MIGRATION_PLAN.md`

**Phase 1: Foundation (Weeks 1-4)**
- [ ] Create core types (`core/types.py`)
- [ ] Implement error handling (`core/errors.py`)
- [ ] Setup logging (`core/logging.py`)
- [ ] Create data fetcher abstraction (`core/data/`)
- [ ] Add unit tests for core types and data layer
- [ ] **NO changes to existing dashboards yet**

**Phase 2: Business Logic (Weeks 5-8)**
- [ ] Extract valuation logic to `core/business/valuation/`
- [ ] Extract technical logic to `core/business/technical/`
- [ ] Extract sentiment logic to `core/business/sentiment/`
- [ ] Extract risk logic to `core/business/risk/`
- [ ] Add unit tests for all business logic (target 80% coverage)
- [ ] **Existing dashboards still work unchanged**

**Phase 3: Service Layer (Weeks 9-12)**
- [ ] Create `AnalysisService` orchestrator
- [ ] Create `PortfolioService` orchestrator
- [ ] Create `OptionsService` orchestrator
- [ ] Create `CryptoService` orchestrator
- [ ] Add integration tests for services
- [ ] **Services can now be used alongside old code**

**Phase 4: UI Refactoring (Weeks 13-16)**
- [ ] Create UI components (`ui/components/`)
- [ ] Create new stocks dashboard (`ui/pages/stocks.py`)
- [ ] Add feature flag to toggle between old/new dashboards
- [ ] A/B test with users
- [ ] Migrate remaining dashboards one by one
- [ ] **Gradual rollout with rollback capability**

**Phase 5: Cleanup & Documentation (Weeks 17-20)**
- [ ] Remove old dashboard files
- [ ] Update documentation
- [ ] Add API documentation
- [ ] Create user migration guide
- [ ] Performance optimization
- [ ] Final test coverage verification

---

### Migration Strategy: Parallel Operation

**File: `migrations/feature_flags.py`**

```python
class FeatureFlags:
    """Control gradual migration"""
    
    USE_NEW_STOCKS_DASHBOARD = False
    USE_NEW_OPTIONS_DASHBOARD = False
    USE_NEW_CRYPTO_DASHBOARD = False
    USE_NEW_PORTFOLIO_DASHBOARD = False
    
    @classmethod
    def enable_new_dashboard(cls, dashboard: str):
        """Enable new dashboard for specific user"""
        pass

# In main.py
if FeatureFlags.USE_NEW_STOCKS_DASHBOARD:
    from ui.pages.stocks import show_stocks_dashboard
else:
    from dashboard_stocks import show_stocks_dashboard  # Old version
```

**Benefits:**
- Can test new code with subset of users
- Easy rollback if issues found
- No downtime during migration
- Compare performance old vs new

---

## 📊 Success Metrics

**Code Quality:**
- [ ] Reduce total lines from 28K to ~15K (45% reduction)
- [ ] Reduce dashboard file sizes from 500+ to ~200 lines each
- [ ] Achieve 80%+ test coverage on core business logic
- [ ] Zero Streamlit imports in `core/` and `services/`

**Maintainability:**
- [ ] Clear separation of concerns (data → logic → UI)
- [ ] Type safety with dataclasses (no magic dicts)
- [ ] Centralized error handling
- [ ] Structured logging throughout

**Performance:**
- [ ] Maintain or improve current performance
- [ ] Efficient caching strategy
- [ ] Lazy loading where appropriate

**Migration:**
- [ ] Zero downtime during migration
- [ ] Feature flags for gradual rollout
- [ ] Clear rollback plan
- [ ] User-facing features unchanged

---

## 🔧 Development Workflow

**1. Local Development:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest, black, mypy, etc.

# Run tests
pytest tests/ -v --cov=core --cov=services

# Type checking
mypy core/ services/

# Linting
black core/ services/ ui/
flake8 core/ services/ ui/
```

**2. Pre-commit Hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/unit -v
        language: system
        pass_filenames: false
        always_run: true
      
      - id: mypy
        name: mypy
        entry: mypy core/ services/
        language: system
        types: [python]
      
      - id: black
        name: black
        entry: black
        language: system
        types: [python]
```

**3. CI/CD Pipeline:**
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/ -v --cov=core --cov=services --cov-report=xml
      - run: mypy core/ services/
      - run: black --check core/ services/ ui/
```

---

## 📚 Additional Resources

**Documentation to Create:**
1. `docs/api/core_types.md` - Type definitions reference
2. `docs/api/services.md` - Service layer API
3. `docs/guides/adding_features.md` - How to add new features
4. `docs/guides/testing.md` - Testing guide
5. `docs/migration/phase1.md` - Phase 1 migration guide
6. `docs/migration/rollback.md` - Rollback procedures

**Key Dependencies:**
```txt
# requirements-dev.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
black>=23.7.0
mypy>=1.4.0
flake8>=6.0.0
pre-commit>=3.3.0
```

---

## 🎯 Summary

This refactoring transforms a 28K line monolithic application into a professional, modular system:

**Before:**
- ❌ 6 monolithic dashboard files (500+ lines each)
- ❌ Business logic mixed with UI code
- ❌ 40% code duplication
- ❌ Magic dictionaries everywhere
- ❌ No tests, no error handling
- ❌ Tightly coupled to Streamlit

**After:**
- ✅ Clean 3-layer architecture (data → logic → UI)
- ✅ Type-safe with dataclasses
- ✅ 80%+ test coverage
- ✅ Swappable data sources
- ✅ Comprehensive error handling
- ✅ Framework-agnostic business logic

**Timeline:** 20 weeks, phased incrementally  
**Risk:** Low (parallel operation, feature flags, rollback capability)  
**Benefit:** Professional, maintainable, scalable codebase

---

**Next Steps:**
1. Review and approve architecture
2. Begin Phase 1: Foundation
3. Set up development workflow (CI/CD, pre-commit hooks)
4. Create initial test infrastructure
5. Start extracting core types and data layer
