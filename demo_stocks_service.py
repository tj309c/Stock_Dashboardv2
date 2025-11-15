"""
Demo: StocksAnalysisService in Action
Shows how the service works with real components
"""
import sys
import io
from datetime import datetime

# Fix console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("🚀 StocksAnalysisService Demo")
print("=" * 60)
print()

# Initialize components (same as main.py)
print("📦 Initializing components...")
try:
    from data_fetcher import MarketDataFetcher
    from analysis_engine import ValuationEngine, TechnicalAnalyzer, GoodBuyAnalyzer
    from src.services.stocks_analysis_service import StocksAnalysisService
    
    components = {
        "fetcher": MarketDataFetcher(),
        "valuation": ValuationEngine(),
        "technical": TechnicalAnalyzer(),
        "goodbuy": GoodBuyAnalyzer()
    }
    
    print("✅ Components initialized")
    print()
    
except Exception as e:
    print(f"❌ Error initializing components: {e}")
    sys.exit(1)

# Create service
print("🔧 Creating StocksAnalysisService...")
service = StocksAnalysisService(components)
print("✅ Service created")
print()

# Analyze a stock
ticker = "AAPL"
print(f"📊 Analyzing {ticker}...")
print("(This will fetch real data from yfinance)")
print()

try:
    result = service.analyze_stock(ticker, include_sentiment=False)
    
    print("✅ Analysis complete!")
    print("=" * 60)
    print()
    
    # Display results
    print(f"📈 {result.ticker} Analysis Results")
    print(f"⏰ Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Price info
    print("💰 PRICE INFORMATION")
    print(f"  Current:    ${result.price.current:.2f}")
    print(f"  Open:       ${result.price.open:.2f}")
    print(f"  High:       ${result.price.high:.2f}")
    print(f"  Low:        ${result.price.low:.2f}")
    print(f"  Volume:     {result.price.volume:,}")
    print(f"  Day Change: {result.price.day_change_percent:+.2f}%")
    print(f"  52W Range:  ${result.price.week_52_low:.2f} - ${result.price.week_52_high:.2f}")
    print(f"  Position:   {result.price.get_position_in_range():.1f}% in range")
    print()
    
    # Technical indicators
    print("📊 TECHNICAL INDICATORS")
    try:
        rsi = result.technical.rsi if isinstance(result.technical.rsi, (int, float)) else result.technical.rsi.get('rsi', 50)
        print(f"  RSI:        {rsi:.1f}")
        print(f"  MACD:       {result.technical.macd:.2f}")
        print(f"  Trend:      {result.technical.get_trend().value}")
        print(f"  Momentum:   {result.technical.get_momentum_score():.1f}/100")
        print(f"  Overbought: {result.technical.is_overbought()}")
        print(f"  Oversold:   {result.technical.is_oversold()}")
    except Exception as e:
        print(f"  (Technical data format issue: {e})")
    print()
    
    # Fundamentals
    print("💼 FUNDAMENTAL METRICS")
    print(f"  P/E Ratio:  {result.fundamentals.pe_ratio if result.fundamentals.pe_ratio else 'N/A'}")
    print(f"  EPS:        ${result.fundamentals.eps if result.fundamentals.eps else 'N/A'}")
    print(f"  ROE:        {result.fundamentals.roe*100 if result.fundamentals.roe else 'N/A'}%")
    print(f"  Debt/Eq:    {result.fundamentals.debt_to_equity if result.fundamentals.debt_to_equity else 'N/A'}")
    print(f"  Quality:    {result.fundamentals.get_quality_score():.1f}/100")
    print(f"  Healthy:    {result.fundamentals.is_financially_healthy()}")
    print()
    
    # Risk metrics
    print("⚠️  RISK METRICS")
    print(f"  Sharpe:     {result.risk.sharpe_ratio:.2f}")
    print(f"  Volatility: {result.risk.volatility*100:.1f}%")
    print(f"  Max DD:     {result.risk.max_drawdown*100:.1f}%")
    print(f"  Beta:       {result.risk.beta:.2f}")
    print(f"  Risk Level: {result.risk.get_risk_level()}")
    print()
    
    # Valuation
    print("💎 VALUATION")
    print(f"  Fair Value: ${result.valuation.fair_value:.2f}")
    print(f"  Current:    ${result.valuation.current_price:.2f}")
    print(f"  Upside:     {result.valuation.upside_pct:+.1f}%")
    print(f"  Method:     {result.valuation.method.value}")
    print(f"  Confidence: {result.valuation.confidence:.0f}%")
    print(f"  Recommend:  {result.valuation.get_recommendation().value}")
    print()
    
    # Signals
    print("🎯 TRADE SIGNALS")
    for i, signal in enumerate(result.signals, 1):
        print(f"  Signal {i}:")
        print(f"    Action:     {signal.signal.value}")
        print(f"    Confidence: {signal.confidence*100:.0f}%")
        print(f"    Reasoning:  {signal.reasoning}")
        if signal.entry_price:
            print(f"    Entry:      ${signal.entry_price:.2f}")
        if signal.stop_loss:
            print(f"    Stop Loss:  ${signal.stop_loss:.2f}")
        if signal.take_profit:
            print(f"    Target:     ${signal.take_profit:.2f}")
        print()
    
    # Overall score
    print("📈 OVERALL INVESTMENT SCORE")
    score = result.get_overall_score()
    print(f"  Score: {score:.1f}/100")
    
    if score >= 70:
        print(f"  Rating: ⭐⭐⭐⭐⭐ EXCELLENT")
    elif score >= 60:
        print(f"  Rating: ⭐⭐⭐⭐ GOOD")
    elif score >= 50:
        print(f"  Rating: ⭐⭐⭐ FAIR")
    elif score >= 40:
        print(f"  Rating: ⭐⭐ POOR")
    else:
        print(f"  Rating: ⭐ AVOID")
    print()
    
    # Service methods
    print("=" * 60)
    print("🔍 Testing Service Methods")
    print("=" * 60)
    print()
    
    # Technical summary
    tech_summary = service.get_technical_summary(result)
    print("📊 Technical Summary:")
    for key, value in tech_summary.items():
        print(f"  {key}: {value}")
    print()
    
    # Valuation summary
    val_summary = service.get_valuation_summary(result)
    print("💎 Valuation Summary:")
    for key, value in val_summary.items():
        print(f"  {key}: {value}")
    print()
    
    # Buy signals
    signals = service.calculate_buy_signals(result)
    print(f"🎯 Buy Signals: {len(signals)} signal(s)")
    print()
    
    print("=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print()
    print("💡 Key Takeaways:")
    print("  • Service returns type-safe StockAnalysisResult")
    print("  • All business logic is testable (no Streamlit)")
    print("  • IDE autocomplete works perfectly")
    print("  • Easy to mock for unit tests")
    print()
    
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
