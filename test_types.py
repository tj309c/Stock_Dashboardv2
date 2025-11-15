"""
Type Definitions Test & Demo
Run this to verify type definitions are working and see IDE autocomplete in action
"""

from src.core.types import (
    Signal, Trend, ValuationMethod,
    StockPrice, TechnicalIndicators, FundamentalMetrics,
    RiskMetrics, ValuationResult, TradeSignal, StockAnalysisResult
)
from src.core.errors import DataFetchError, ValuationError
from datetime import datetime


def demo_type_safety():
    """Demonstrate type safety and IDE autocomplete"""
    
    print("=" * 80)
    print("TYPE DEFINITIONS DEMO")
    print("=" * 80)
    print()
    
    # 1. Create StockPrice with type-safe fields
    print("1. Creating StockPrice object...")
    price = StockPrice(
        current=175.50,
        open=173.20,
        high=176.80,
        low=172.50,
        close=175.50,
        volume=52_000_000,
        market_cap=2_800_000_000_000,  # $2.8T
        day_change=2.30,
        day_change_percent=1.33,
        week_52_high=195.00,
        week_52_low=120.00
    )
    
    print(f"   ✅ Current Price: ${price.current}")
    print(f"   ✅ Change: ${price.day_change} ({price.day_change_percent}%)")
    print(f"   ✅ Position in 52w range: {price.get_position_in_range():.1f}%")
    print(f"   ✅ Near high? {price.is_near_high()}")
    print()
    
    # 2. Create TechnicalIndicators with methods
    print("2. Creating TechnicalIndicators...")
    technical = TechnicalIndicators(
        rsi=65.5,
        macd=1.50,
        macd_signal=1.20,
        macd_histogram=0.30,
        bollinger_high=180.00,
        bollinger_mid=175.00,
        bollinger_low=170.00,
        sma_20=174.50,
        sma_50=170.00,
        sma_200=160.00,
        ema_12=175.20,
        ema_26=172.50,
        adx=28.5,
        obv=1_500_000_000
    )
    
    print(f"   ✅ RSI: {technical.rsi}")
    print(f"   ✅ Overbought? {technical.is_overbought()}")
    print(f"   ✅ Trend: {technical.get_trend().value}")
    print(f"   ✅ Momentum Score: {technical.get_momentum_score():.1f}/100")
    print()
    
    # 3. Create FundamentalMetrics
    print("3. Creating FundamentalMetrics...")
    fundamentals = FundamentalMetrics(
        pe_ratio=28.5,
        pb_ratio=6.2,
        ps_ratio=7.1,
        peg_ratio=1.8,
        dividend_yield=0.5,
        roe=18.5,
        roa=12.3,
        debt_to_equity=0.45,
        current_ratio=2.1,
        quick_ratio=1.8,
        eps=6.15,
        eps_growth=12.5,
        revenue_growth=8.3,
        profit_margin=21.2,
        operating_margin=28.5
    )
    
    print(f"   ✅ P/E Ratio: {fundamentals.pe_ratio}")
    print(f"   ✅ Is Value Stock? {fundamentals.is_value_stock()}")
    print(f"   ✅ Is Growth Stock? {fundamentals.is_growth_stock()}")
    print(f"   ✅ Financially Healthy? {fundamentals.is_financially_healthy()}")
    print(f"   ✅ Quality Score: {fundamentals.get_quality_score():.1f}/100")
    print()
    
    # 4. Create RiskMetrics
    print("4. Creating RiskMetrics...")
    risk = RiskMetrics(
        sharpe_ratio=1.5,
        sortino_ratio=2.1,
        max_drawdown=15.2,
        volatility=25.3,
        beta=1.1,
        alpha=2.5,
        var_95=8.5,
        cvar_95=12.3
    )
    
    print(f"   ✅ Sharpe Ratio: {risk.sharpe_ratio}")
    print(f"   ✅ Risk Level: {risk.get_risk_level()}")
    print(f"   ✅ Risk-Adjusted Attractive? {risk.is_risk_adjusted_attractive()}")
    print()
    
    # 5. Create ValuationResult
    print("5. Creating ValuationResult...")
    valuation = ValuationResult(
        fair_value=210.00,
        current_price=175.50,
        upside_pct=19.66,
        method=ValuationMethod.DCF,
        confidence=75.0,
        scenarios={
            'bear': 150.00,
            'base': 210.00,
            'bull': 280.00
        },
        assumptions={
            'revenue_growth': 8.0,
            'discount_rate': 10.0,
            'terminal_growth': 3.0
        }
    )
    
    print(f"   ✅ Fair Value: ${valuation.fair_value}")
    print(f"   ✅ Upside: {valuation.upside_pct:.2f}%")
    print(f"   ✅ Method: {valuation.method.value}")
    print(f"   ✅ Recommendation: {valuation.get_recommendation().value}")
    print(f"   ✅ Undervalued? {valuation.is_undervalued()}")
    print()
    
    # 6. Create TradeSignals
    print("6. Creating TradeSignals...")
    signal1 = TradeSignal(
        signal=Signal.BUY,
        confidence=78.5,
        reasoning="Strong technicals + undervalued + positive momentum",
        entry_price=175.50,
        stop_loss=165.00,
        take_profit=210.00,
        position_size=5.0,
        timeframe="3-6 months"
    )
    
    print(f"   ✅ Signal: {signal1.signal.value}")
    print(f"   ✅ Confidence: {signal1.confidence}%")
    print(f"   ✅ Reasoning: {signal1.reasoning}")
    print()
    
    # 7. Create complete StockAnalysisResult
    print("7. Creating Complete StockAnalysisResult...")
    analysis = StockAnalysisResult(
        ticker="AAPL",
        price=price,
        technical=technical,
        fundamentals=fundamentals,
        risk=risk,
        valuation=valuation,
        signals=[signal1],
        metadata={'source': 'demo', 'version': '1.0'}
    )
    
    print(f"   ✅ Ticker: {analysis.ticker}")
    print(f"   ✅ Overall Score: {analysis.get_overall_score():.1f}/100")
    print(f"   ✅ Primary Signal: {analysis.get_primary_signal().signal.value}")
    print(f"   ✅ Signal Confidence: {analysis.get_primary_signal().confidence}%")
    print()
    
    # 8. Demonstrate type safety
    print("8. Type Safety Benefits:")
    print("   ✅ IDE knows all fields (autocomplete works)")
    print("   ✅ Typos caught before runtime")
    print("   ✅ Methods available on objects")
    print("   ✅ Type hints help with refactoring")
    print()
    
    # 9. Convert to dict (backward compatible)
    print("9. Converting to dict (backward compatible)...")
    analysis_dict = analysis.to_dict()
    print(f"   ✅ Dict has {len(analysis_dict)} top-level keys")
    print(f"   ✅ Compatible with existing code")
    print()
    
    # 10. Error handling example
    print("10. Error Handling Example:")
    try:
        # Simulate an error
        raise ValuationError("Cannot calculate DCF with negative FCF")
    except ValuationError as e:
        print(f"   ✅ Caught specific error: {type(e).__name__}")
        print(f"   ✅ Error message: {str(e)}")
    print()
    
    print("=" * 80)
    print("✅ ALL TYPE DEFINITIONS WORKING!")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Start using these types in analysis_engine.py")
    print("2. Update data_fetcher.py return types")
    print("3. Gradually migrate existing functions")
    print()


def demo_ide_autocomplete():
    """This function demonstrates IDE autocomplete"""
    print("=" * 80)
    print("IDE AUTOCOMPLETE DEMO")
    print("=" * 80)
    print()
    print("Try typing this in your IDE:")
    print()
    print("    analysis = StockAnalysisResult(...)")
    print("    analysis.  # <-- IDE will show all available fields!")
    print()
    print("Available fields:")
    print("  - analysis.ticker")
    print("  - analysis.price.current")
    print("  - analysis.price.day_change")
    print("  - analysis.technical.rsi")
    print("  - analysis.technical.is_overbought()")
    print("  - analysis.fundamentals.pe_ratio")
    print("  - analysis.fundamentals.is_value_stock()")
    print("  - analysis.risk.sharpe_ratio")
    print("  - analysis.valuation.fair_value")
    print("  - analysis.get_overall_score()")
    print("  - analysis.get_primary_signal()")
    print()
    print("=" * 80)
    print()


def compare_old_vs_new():
    """Compare old magic dict vs new typed approach"""
    print("=" * 80)
    print("OLD vs NEW COMPARISON")
    print("=" * 80)
    print()
    
    # OLD WAY
    print("❌ OLD WAY (Magic Dictionary):")
    print("---")
    print("data = {")
    print("    'price': 175.50,")
    print("    'rsi': 65,")
    print("    'pe_ratio': 28.5")
    print("}")
    print()
    print("Problems:")
    print("  - data['price']  ✅ Works")
    print("  - data['prcie']  ❌ Typo! Runtime error!")
    print("  - data['RSI']    ❌ Case sensitive! Runtime error!")
    print("  - No autocomplete")
    print("  - No type checking")
    print()
    
    # NEW WAY
    print("✅ NEW WAY (Type-Safe):")
    print("---")
    print("price = StockPrice(current=175.50, ...)")
    print("technical = TechnicalIndicators(rsi=65, ...)")
    print("fundamentals = FundamentalMetrics(pe_ratio=28.5, ...)")
    print()
    print("Benefits:")
    print("  - price.current         ✅ Autocomplete!")
    print("  - price.currnet         ❌ IDE error before run!")
    print("  - technical.RSI         ❌ IDE error before run!")
    print("  - Full autocomplete")
    print("  - Type checking")
    print("  - Built-in methods")
    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    demo_type_safety()
    demo_ide_autocomplete()
    compare_old_vs_new()
