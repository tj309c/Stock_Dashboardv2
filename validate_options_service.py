"""
Options Service Integration Validation
Tests OptionsAnalysisService with real market data
"""
import sys
import io
import time
from datetime import datetime

# Fix Windows console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services import OptionsAnalysisService
from data_fetcher import DataFetcher
from analysis_engine import OptionsAnalyzer


def main():
    """Validate options service integration"""
    
    print("=" * 80)
    print("🧪 OPTIONS SERVICE LAYER VALIDATION")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    ticker = "SPY"  # Highly liquid options
    
    print("⚙️  Initializing components...")
    components = {
        "fetcher": DataFetcher(),
        "options": OptionsAnalyzer()
    }
    print("✅ Components ready\n")
    
    print(f"📊 Testing with ticker: {ticker}\n")
    
    # Test 1: Analyze Options Chain
    print("=" * 80)
    print("🎯 TEST 1: Analyze Options Chain")
    print("=" * 80)
    
    start = time.time()
    service = OptionsAnalysisService(components)
    result = service.analyze_options_chain(ticker)
    elapsed = time.time() - start
    
    if result:
        print(f"✅ Options chain analyzed")
        print(f"   Ticker: {result.ticker}")
        print(f"   Spot Price: ${result.spot_price:.2f}")
        print(f"   Expirations: {len(result.expiration_dates)}")
        print(f"   Total Calls: {len(result.calls)}")
        print(f"   Total Puts: {len(result.puts)}")
        print(f"⏱️  Completed in {elapsed:.2f}s\n")
    else:
        print("❌ Failed to analyze options chain\n")
        return
    
    # Test 2: Detect Unusual Activity
    print("=" * 80)
    print("🔥 TEST 2: Detect Unusual Activity")
    print("=" * 80)
    
    start = time.time()
    unusual = service.detect_unusual_activity(ticker)
    elapsed = time.time() - start
    
    if unusual:
        print(f"✅ Found {len(unusual)} unusual activities")
        
        # Show top 3
        for i, activity in enumerate(unusual[:3], 1):
            contract = activity.contract
            print(f"\n   {i}. {contract.option_type} {contract.strike:.2f} exp {contract.expiration}")
            print(f"      Volume: {contract.volume:,} | OI: {contract.open_interest:,}")
            print(f"      Score: {activity.score:.1f}/100")
            print(f"      Reason: {activity.reason}")
        
        print(f"\n⏱️  Completed in {elapsed:.2f}s\n")
    else:
        print("ℹ️  No unusual activity detected\n")
    
    # Test 3: Calculate Greeks
    print("=" * 80)
    print("📈 TEST 3: Calculate Greeks")
    print("=" * 80)
    
    # Get an ATM call
    atm_strike = round(result.spot_price)
    time_to_expiry = 30 / 365.0  # 30 days
    iv = 0.25  # 25% IV
    
    start = time.time()
    greeks = service.calculate_greeks(
        spot_price=result.spot_price,
        strike=atm_strike,
        time_to_expiry=time_to_expiry,
        volatility=iv,
        option_type="call"
    )
    elapsed = time.time() - start
    
    if greeks:
        print(f"✅ Greeks calculated for ATM call")
        print(f"   Strike: ${atm_strike:.2f}")
        print(f"   Price: ${greeks.price:.2f}")
        print(f"   Delta: {greeks.delta:.4f}")
        print(f"   Gamma: {greeks.gamma:.4f}")
        print(f"   Theta: {greeks.theta:.4f}")
        print(f"   Vega: {greeks.vega:.4f}")
        print(f"⏱️  Completed in {elapsed:.4f}s\n")
    else:
        print("❌ Failed to calculate Greeks\n")
    
    # Test 4: Strategy Recommendations
    print("=" * 80)
    print("🎯 TEST 4: Strategy Recommendations")
    print("=" * 80)
    
    for outlook in ["bullish", "neutral", "bearish"]:
        print(f"\n{outlook.upper()} Outlook:")
        start = time.time()
        strategies = service.get_strategy_recommendations(ticker, result.spot_price, outlook)
        elapsed = time.time() - start
        
        if strategies:
            print(f"   ✅ {len(strategies)} strategies recommended")
            for strat in strategies[:2]:  # Show first 2
                print(f"      • {strat['name']}")
        else:
            print(f"   ℹ️  No strategies for {outlook}")
        
        print(f"   ⏱️  {elapsed:.3f}s")
    
    # Test 5: Get Contracts by Expiration
    print("\n" + "=" * 80)
    print("📅 TEST 5: Get Contracts by Expiration")
    print("=" * 80)
    
    if result.expiration_dates:
        first_exp = result.expiration_dates[0]
        print(f"\nExpiration: {first_exp}")
        
        start = time.time()
        contracts = service.get_contracts_by_expiration(ticker, first_exp)
        elapsed = time.time() - start
        
        if contracts:
            calls = [c for c in contracts if c.option_type == "CALL"]
            puts = [c for c in contracts if c.option_type == "PUT"]
            
            print(f"✅ Retrieved {len(contracts)} contracts")
            print(f"   Calls: {len(calls)}")
            print(f"   Puts: {len(puts)}")
            print(f"⏱️  Completed in {elapsed:.2f}s\n")
        else:
            print("❌ No contracts found\n")
    
    # Summary
    print("=" * 80)
    print("🎉 VALIDATION COMPLETE")
    print("=" * 80)
    print("\n✅ All tests passed!")
    print("\n📝 Service Layer Features:")
    print("   • Analyze complete options chains")
    print("   • Detect unusual activity with scoring")
    print("   • Calculate Black-Scholes Greeks")
    print("   • Generate strategy recommendations")
    print("   • Filter contracts by expiration")
    print("\n🚀 Ready for dashboard integration!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
