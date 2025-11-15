"""
Type-safe data structures - Replace magic dictionaries
Provides IDE autocomplete and runtime validation
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class Signal(str, Enum):
    """Trading signals"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class Trend(str, Enum):
    """Market trend"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    SIDEWAYS = "SIDEWAYS"


class ValuationMethod(str, Enum):
    """Valuation calculation method"""
    DCF = "DCF"
    MULTIPLES = "MULTIPLES"
    DDM = "DDM"
    ZERO_FCF = "ZERO_FCF"
    HYBRID = "HYBRID"


# ============================================================================
# STOCK DATA
# ============================================================================

@dataclass
class StockPrice:
    """Current price information"""
    current: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    market_cap: float
    day_change: float              # Dollar change
    day_change_percent: float      # Percent change
    week_52_high: float
    week_52_low: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_position_in_range(self) -> float:
        """Get position in 52-week range (0-100%)"""
        if self.week_52_high == self.week_52_low:
            return 50.0
        return ((self.current - self.week_52_low) / 
                (self.week_52_high - self.week_52_low)) * 100
    
    def is_near_high(self, threshold: float = 0.95) -> bool:
        """Is price within threshold of 52-week high?"""
        return self.current >= (self.week_52_high * threshold)
    
    def is_near_low(self, threshold: float = 1.05) -> bool:
        """Is price within threshold of 52-week low?"""
        return self.current <= (self.week_52_low * threshold)


@dataclass
class TechnicalIndicators:
    """Technical analysis indicators"""
    rsi: float                     # Relative Strength Index (0-100)
    macd: float
    macd_signal: float
    macd_histogram: float
    bollinger_high: float
    bollinger_mid: float
    bollinger_low: float
    sma_20: float                  # 20-day Simple Moving Average
    sma_50: float
    sma_200: float
    ema_12: float
    ema_26: float
    adx: float                     # Average Directional Index (0-100)
    obv: float                     # On-Balance Volume
    atr: float = 0.0               # Average True Range
    stochastic_k: float = 0.0
    stochastic_d: float = 0.0
    cci: float = 0.0               # Commodity Channel Index
    
    def is_overbought(self, threshold: float = 70) -> bool:
        """Is RSI above overbought threshold?"""
        return self.rsi > threshold
    
    def is_oversold(self, threshold: float = 30) -> bool:
        """Is RSI below oversold threshold?"""
        return self.rsi < threshold
    
    def get_trend(self) -> Trend:
        """Determine trend from moving averages"""
        if self.sma_20 > self.sma_50 > self.sma_200:
            return Trend.BULLISH
        elif self.sma_20 < self.sma_50 < self.sma_200:
            return Trend.BEARISH
        else:
            return Trend.NEUTRAL
    
    def get_momentum_score(self) -> float:
        """Calculate momentum score (0-100)"""
        rsi_score = self.rsi
        macd_score = 50 + (self.macd_histogram * 10)  # Normalize
        macd_score = max(0, min(100, macd_score))
        adx_score = self.adx
        
        return (rsi_score * 0.4 + macd_score * 0.4 + adx_score * 0.2)


@dataclass
class FundamentalMetrics:
    """Fundamental analysis metrics"""
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    roe: Optional[float] = None               # Return on Equity
    roa: Optional[float] = None               # Return on Assets
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    eps: Optional[float] = None               # Earnings Per Share
    eps_growth: Optional[float] = None         # YoY growth %
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    def is_value_stock(self, pe_threshold: float = 15) -> bool:
        """Is this a value stock (low P/E)?"""
        return self.pe_ratio is not None and self.pe_ratio < pe_threshold
    
    def is_growth_stock(self, growth_threshold: float = 20) -> bool:
        """Is this a growth stock (high growth)?"""
        return (self.eps_growth is not None and 
                self.eps_growth > growth_threshold)
    
    def is_financially_healthy(self) -> bool:
        """Simple health check"""
        checks = []
        if self.debt_to_equity is not None:
            checks.append(self.debt_to_equity < 2.0)
        if self.current_ratio is not None:
            checks.append(self.current_ratio > 1.0)
        if self.roe is not None:
            checks.append(self.roe > 10.0)
        
        return len(checks) > 0 and sum(checks) / len(checks) > 0.66
    
    def get_quality_score(self) -> float:
        """Calculate quality score (0-100)"""
        score = 50.0  # Base score
        
        if self.roe and self.roe > 15:
            score += 15
        if self.profit_margin and self.profit_margin > 10:
            score += 10
        if self.debt_to_equity and self.debt_to_equity < 0.5:
            score += 15
        if self.current_ratio and self.current_ratio > 2.0:
            score += 10
        
        return min(100, max(0, score))


@dataclass
class RiskMetrics:
    """Risk and performance metrics"""
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0            # Annualized
    beta: float = 1.0
    alpha: float = 0.0
    var_95: float = 0.0                # Value at Risk (95%)
    cvar_95: float = 0.0               # Conditional VaR
    
    def get_risk_level(self) -> str:
        """Categorize risk level"""
        if self.volatility > 40:
            return "EXTREME"
        elif self.volatility > 30:
            return "HIGH"
        elif self.volatility > 20:
            return "MEDIUM"
        else:
            return "LOW"
    
    def is_risk_adjusted_attractive(self) -> bool:
        """Is this attractive on risk-adjusted basis?"""
        return self.sharpe_ratio > 1.0 and self.max_drawdown < 30


@dataclass
class ValuationResult:
    """Result from a valuation model"""
    fair_value: float
    current_price: float
    upside_pct: float
    method: ValuationMethod
    confidence: float                   # 0-100
    scenarios: Dict[str, float] = field(default_factory=dict)  # bear/base/bull
    assumptions: Dict[str, Any] = field(default_factory=dict)
    sensitivity: Dict[str, float] = field(default_factory=dict)
    
    def get_recommendation(self) -> Signal:
        """Get buy/sell recommendation based on upside"""
        if self.upside_pct > 30:
            return Signal.STRONG_BUY
        elif self.upside_pct > 10:
            return Signal.BUY
        elif self.upside_pct > -10:
            return Signal.HOLD
        elif self.upside_pct > -30:
            return Signal.SELL
        else:
            return Signal.STRONG_SELL
    
    def is_undervalued(self, threshold: float = 10) -> bool:
        """Is stock undervalued by threshold%?"""
        return self.upside_pct > threshold


@dataclass
class TradeSignal:
    """Buy/Sell signal"""
    signal: Signal
    confidence: float              # 0-100
    reasoning: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None  # % of portfolio
    timeframe: str = "medium-term"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            'signal': self.signal.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'timeframe': self.timeframe
        }


@dataclass
class StockAnalysisResult:
    """Complete analysis result - replaces magic dictionary"""
    ticker: str
    price: StockPrice
    technical: TechnicalIndicators
    fundamentals: FundamentalMetrics
    risk: RiskMetrics
    valuation: ValuationResult
    signals: List[TradeSignal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_primary_signal(self) -> Optional[TradeSignal]:
        """Get highest confidence signal"""
        if not self.signals:
            return None
        return max(self.signals, key=lambda s: s.confidence)
    
    def get_overall_score(self) -> float:
        """Calculate overall investment score (0-100)"""
        scores = []
        
        # Technical score
        tech_score = self.technical.get_momentum_score()
        scores.append(tech_score * 0.3)
        
        # Fundamental score
        fund_score = self.fundamentals.get_quality_score()
        scores.append(fund_score * 0.3)
        
        # Valuation score (normalized upside)
        val_score = min(100, max(0, 50 + self.valuation.upside_pct))
        scores.append(val_score * 0.3)
        
        # Risk score (inverse - lower risk = higher score)
        risk_score = 100 - (self.risk.volatility * 2)
        risk_score = max(0, min(100, risk_score))
        scores.append(risk_score * 0.1)
        
        return sum(scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (backward compatible)"""
        return {
            'ticker': self.ticker,
            'price': self.price.__dict__,
            'technical': self.technical.__dict__,
            'fundamentals': self.fundamentals.__dict__,
            'risk': self.risk.__dict__,
            'valuation': self.valuation.__dict__,
            'signals': [s.to_dict() for s in self.signals],
            'timestamp': self.timestamp.isoformat(),
            'overall_score': self.get_overall_score()
        }


# ============================================================================
# OPTIONS DATA
# ============================================================================

@dataclass
class GreeksData:
    """Option Greeks"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: float


@dataclass
class OptionContract:
    """Single option contract"""
    contract_symbol: str
    strike: float
    expiration: datetime
    option_type: str               # 'call' or 'put'
    last_price: float
    bid: float
    ask: float
    volume: int
    open_interest: int
    greeks: Optional[GreeksData] = None
    
    def is_itm(self, spot_price: float) -> bool:
        """Is option in-the-money?"""
        if self.option_type == 'call':
            return spot_price > self.strike
        else:
            return spot_price < self.strike
    
    def is_near_money(self, spot_price: float, threshold: float = 0.05) -> bool:
        """Is option near-the-money (within threshold%)?"""
        price_diff = abs(spot_price - self.strike) / spot_price
        return price_diff < threshold


@dataclass
class OptionsChain:
    """Options chain data"""
    ticker: str
    spot_price: float
    expiration_dates: List[datetime]
    calls: List[OptionContract] = field(default_factory=list)
    puts: List[OptionContract] = field(default_factory=list)
    
    def get_atm_strike(self) -> float:
        """Get at-the-money strike"""
        all_strikes = [c.strike for c in self.calls] + [p.strike for p in self.puts]
        if not all_strikes:
            return self.spot_price
        return min(all_strikes, key=lambda x: abs(x - self.spot_price))
    
    def get_put_call_ratio(self) -> float:
        """Calculate put/call ratio by volume"""
        call_vol = sum(c.volume for c in self.calls)
        put_vol = sum(p.volume for p in self.puts)
        if call_vol == 0:
            return float('inf')
        return put_vol / call_vol


@dataclass
class UnusualActivity:
    """Unusual options activity"""
    contract: OptionContract
    unusual_score: float           # 0-100
    reason: str
    premium_value: float
    detected_at: datetime = field(default_factory=datetime.now)
    
    def is_highly_unusual(self, threshold: float = 80) -> bool:
        """Is this highly unusual activity?"""
        return self.unusual_score > threshold


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# Example 1: OLD WAY (bad - magic dictionary)
def analyze_stock_old(ticker):
    result = {
        'ticker': ticker,
        'price': 100,
        'pe_ratio': 25,
        'rsi': 65
    }
    return result

analysis = analyze_stock_old("AAPL")
print(analysis["price"])        # Works
print(analysis["clos_price"])   # Bug! Typo causes runtime error 🐛

# Example 2: NEW WAY (good - type-safe)
def analyze_stock_new(ticker: str) -> StockAnalysisResult:
    price = StockPrice(
        current=100, open=98, high=102, low=97, close=100,
        volume=50000000, market_cap=2.8e12, day_change=2.0,
        day_change_percent=2.04, week_52_high=195, week_52_low=120
    )
    technical = TechnicalIndicators(
        rsi=65, macd=1.5, macd_signal=1.2, macd_histogram=0.3,
        bollinger_high=105, bollinger_mid=100, bollinger_low=95,
        sma_20=98, sma_50=95, sma_200=90, ema_12=99, ema_26=96,
        adx=25, obv=1000000
    )
    fundamentals = FundamentalMetrics(
        pe_ratio=25, pb_ratio=6, eps=4.0, roe=18.5
    )
    risk = RiskMetrics(
        sharpe_ratio=1.5, max_drawdown=15, volatility=25, beta=1.1
    )
    valuation = ValuationResult(
        fair_value=120, current_price=100, upside_pct=20,
        method=ValuationMethod.DCF, confidence=75
    )
    
    return StockAnalysisResult(
        ticker=ticker, price=price, technical=technical,
        fundamentals=fundamentals, risk=risk, valuation=valuation
    )

analysis = analyze_stock_new("AAPL")
print(analysis.price.current)           # IDE autocomplete works! ✅
print(analysis.price.clos_price)        # IDE error before run! ✅
print(analysis.technical.is_overbought())  # Type-safe methods! ✅
print(analysis.get_overall_score())     # Calculated methods! ✅

# Example 3: Using type hints in functions
def calculate_risk_adjusted_return(analysis: StockAnalysisResult) -> float:
    '''Calculate risk-adjusted return - IDE knows all fields'''
    return analysis.valuation.upside_pct / analysis.risk.volatility

# IDE autocomplete shows:
# - analysis.price.*
# - analysis.technical.*
# - analysis.fundamentals.*
# etc.
"""
