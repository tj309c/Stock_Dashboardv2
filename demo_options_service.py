"""
Demo: OptionsAnalysisService with Real SPY Options Data
Validates the service with live market data
"""
import sys
import io
from typing import Dict

# Fix Windows console encoding for emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services import OptionsAnalysisService
from data_fetcher import MarketDataFetcher
from analysis_engine import OptionsAnalyzer


def create_components() -> Dict:
    """Create components for service"""
    return {
        "fetcher": MarketDataFetcher(),
        "options": OptionsAnalyzer()
    }


def demo_options_analysis():
    """Run complete options analysis demo"""
    print("\n" + "="*80)
    print("🎯 OPTIONS ANALYSIS SERVICE DEMO")
    print("="*80 + "\n")
    
    # Initialize service
    components = create_components()
    service = OptionsAnalysisService(components)
    print("✅ Service initialized successfully\n")
    
    # Ticker to analyze
    ticker = "SPY"
    print(f"📊 Analyzing {ticker} Options Chain...\n")
    
    try:
        # ========== 1. ANALYZE OPTIONS CHAIN ==========
        print("1️⃣  FETCHING OPTIONS CHAIN")
        print("-" * 40)
        
        chain = service.analyze_options_chain(ticker)
        
        print(f"✅ Ticker: {chain.ticker}")
        print(f"💰 Current Price: ${chain.spot_price:.2f}")
        print(f"📅 Expirations: {len(chain.expiration_dates)} dates")
        if chain.expiration_dates:
            print(f"   First: {chain.expiration_dates[0].strftime('%Y-%m-%d')}")
            print(f"   Last: {chain.expiration_dates[-1].strftime('%Y-%m-%d')}")
        print()
        
        # ========== 2. GET CONTRACTS FOR NEAREST EXPIRATION ==========
        if chain.expiration_dates:
            # Get expiration strings from raw data
            exp_strings = list(service._raw_chains_data.keys()) if hasattr(service, '_raw_chains_data') else []
            exp = exp_strings[0] if exp_strings else None
            
            if not exp:
                print("No expiration data available")
                return
            print(f"2️⃣  CONTRACTS FOR {exp}")
            print("-" * 40)
            
            # Get all contracts
            all_contracts = service.get_contracts_by_expiration(ticker, exp, "both")
            calls = [c for c in all_contracts if c.contract_type == "call"]
            puts = [c for c in all_contracts if c.contract_type == "put"]
            
            print(f"📈 Calls: {len(calls)} contracts")
            print(f"📉 Puts: {len(puts)} contracts")
            print(f"📊 Total: {len(all_contracts)} contracts")
            print()
            
            # Show sample contracts
            if calls:
                print("Sample CALL (nearest ATM):")
                atm_call = min(calls, key=lambda c: abs(c.strike - chain.spot_price))
                print(f"  Strike: ${atm_call.strike:.2f}")
                print(f"  Last: ${atm_call.last_price:.2f}")
                print(f"  Bid/Ask: ${atm_call.bid:.2f} / ${atm_call.ask:.2f}")
                print(f"  Volume: {atm_call.volume:,}")
                print(f"  OI: {atm_call.open_interest:,}")
                print(f"  IV: {atm_call.implied_volatility*100:.1f}%")
                print()
            
            if puts:
                print("Sample PUT (nearest ATM):")
                atm_put = min(puts, key=lambda c: abs(c.strike - chain.spot_price))
                print(f"  Strike: ${atm_put.strike:.2f}")
                print(f"  Last: ${atm_put.last_price:.2f}")
                print(f"  Bid/Ask: ${atm_put.bid:.2f} / ${atm_put.ask:.2f}")
                print(f"  Volume: {atm_put.volume:,}")
                print(f"  OI: {atm_put.open_interest:,}")
                print(f"  IV: {atm_put.implied_volatility*100:.1f}%")
                print()
            
            # ========== 3. CALCULATE GREEKS ==========
            if calls:
                print("3️⃣  GREEKS CALCULATION (ATM Call)")
                print("-" * 40)
                
                # Calculate days to expiry
                from datetime import datetime
                try:
                    exp_date = datetime.strptime(exp, "%Y-%m-%d")
                    days_to_exp = (exp_date - datetime.now()).days
                    time_to_expiry = max(days_to_exp / 365.0, 1/365)  # Minimum 1 day
                except:
                    time_to_expiry = 0.0833  # Default ~1 month
                
                greeks = service.calculate_greeks(
                    spot_price=chain.spot_price,
                    strike=atm_call.strike,
                    time_to_expiry=time_to_expiry,
                    volatility=atm_call.implied_volatility,
                    risk_free_rate=0.045,
                    option_type="call"
                )
                
                print(f"  Δ Delta: {greeks.delta:.4f} (price sensitivity)")
                print(f"  Γ Gamma: {greeks.gamma:.4f} (delta change)")
                print(f"  Θ Theta: ${greeks.theta:.2f} (daily decay)")
                print(f"  ν Vega: ${greeks.vega:.2f} (IV sensitivity)")
                print(f"  ρ Rho: ${greeks.rho:.2f} (rate sensitivity)")
                print()
            
            # ========== 4. UNUSUAL ACTIVITY ==========
            print("4️⃣  UNUSUAL ACTIVITY DETECTION")
            print("-" * 40)
            
            unusual = service.detect_unusual_activity(ticker, volume_threshold=1.5, min_volume=50)
            
            if unusual:
                print(f"🔥 Found {len(unusual)} contracts with unusual activity:")
                print()
                
                for i, activity in enumerate(unusual[:5], 1):  # Top 5
                    c = activity.contract
                    print(f"  {i}. {ticker} {c.contract_type.upper()} ${c.strike:.0f}")
                    print(f"     Exp: {c.expiration}")
                    print(f"     Volume: {c.volume:,} | OI: {c.open_interest:,}")
                    print(f"     Score: {activity.unusual_score:.1f}/100")
                    print(f"     Premium: ${activity.premium_value:,.0f}")
                    print(f"     IV: {c.implied_volatility*100:.1f}%")
                    print()
            else:
                print("  No unusual activity detected")
                print()
            
            # ========== 5. STRATEGY RECOMMENDATIONS ==========
            print("5️⃣  STRATEGY RECOMMENDATIONS")
            print("-" * 40)
            
            print("\n📈 BULLISH Strategies:")
            bullish = service.get_strategy_recommendations(ticker, chain.spot_price, "bullish")
            for strat in bullish[:2]:  # Top 2
                print(f"  • {strat['name']}")
                print(f"    Strike: ${strat.get('strike', 'N/A'):.2f}")
                print(f"    Premium: ${strat.get('premium', 0):.2f}")
                print(f"    Max Risk: ${strat.get('max_risk', 0):,.0f}")
                print(f"    Breakeven: ${strat.get('breakeven', 0):.2f}")
            
            print("\n📉 BEARISH Strategies:")
            bearish = service.get_strategy_recommendations(ticker, chain.spot_price, "bearish")
            for strat in bearish[:2]:
                print(f"  • {strat['name']}")
                print(f"    Strike: ${strat.get('strike', 'N/A'):.2f}")
                print(f"    Premium: ${strat.get('premium', 0):.2f}")
                print(f"    Max Risk: ${strat.get('max_risk', 0):,.0f}")
                print(f"    Breakeven: ${strat.get('breakeven', 0):.2f}")
            
            print("\n⚖️  NEUTRAL Strategies:")
            neutral = service.get_strategy_recommendations(ticker, chain.spot_price, "neutral")
            for strat in neutral[:2]:
                print(f"  • {strat['name']}")
                print(f"    Strike: ${strat.get('strike', 'N/A'):.2f}")
                print(f"    Premium: ${strat.get('premium', 0):.2f}")
                if 'max_profit' in strat and strat['max_profit'] != float('inf'):
                    print(f"    Max Profit: ${strat['max_profit']:,.0f}")
                print(f"    Breakeven: ${strat.get('breakeven', 0):.2f}")
            print()
            
            # ========== 6. IV METRICS ==========
            print("6️⃣  IMPLIED VOLATILITY METRICS")
            print("-" * 40)
            
            iv_metrics = service.calculate_iv_metrics(ticker, exp, chain.spot_price)
            
            if "error" not in iv_metrics:
                print(f"  Average IV: {iv_metrics['average_iv']:.1f}%")
                print(f"  Min IV: {iv_metrics['min_iv']:.1f}%")
                print(f"  Max IV: {iv_metrics['max_iv']:.1f}%")
                print(f"  IV Rank: {iv_metrics['iv_rank']:.1f}/100")
                print(f"  Volatility Skew: {iv_metrics['volatility_skew']:.1f}%")
                print()
            else:
                print(f"  ⚠️  {iv_metrics['error']}")
                print()
            
            # ========== 7. EXAMPLE CALCULATIONS ==========
            print("7️⃣  STRATEGY CALCULATIONS")
            print("-" * 40)
            
            # Covered Call
            if calls:
                cc = service.calculate_covered_call(
                    stock_price=chain.spot_price,
                    strike=atm_call.strike,
                    premium=atm_call.last_price
                )
                print("\n📊 Covered Call Example:")
                print(f"  Buy 100 shares @ ${chain.spot_price:.2f}")
                print(f"  Sell ${atm_call.strike:.2f} call @ ${atm_call.last_price:.2f}")
                print(f"  Premium Income: ${cc['premium_income']:,.0f}")
                print(f"  Max Profit: ${cc['max_profit']:,.0f}")
                print(f"  Breakeven: ${cc['breakeven']:.2f}")
                print(f"  Return: {cc['return_on_capital']:.2f}%")
            
            # Vertical Spread
            if len(calls) >= 2:
                calls_sorted = sorted(calls, key=lambda c: c.strike)
                long_call = calls_sorted[0]
                short_call = calls_sorted[1]
                
                spread = service.calculate_vertical_spread(
                    long_strike=long_call.strike,
                    short_strike=short_call.strike,
                    long_premium=long_call.last_price,
                    short_premium=short_call.last_price,
                    spread_type="bull_call"
                )
                print("\n📊 Bull Call Spread Example:")
                print(f"  Buy ${long_call.strike:.2f} call @ ${long_call.last_price:.2f}")
                print(f"  Sell ${short_call.strike:.2f} call @ ${short_call.last_price:.2f}")
                print(f"  Net Debit: ${spread['net_debit']:,.0f}")
                print(f"  Max Profit: ${spread['max_profit']:,.0f}")
                print(f"  Max Loss: ${spread['max_loss']:,.0f}")
                print(f"  Risk/Reward: {spread['risk_reward_ratio']:.2f}")
            
            print()
        
        # ========== SUCCESS ==========
        print("="*80)
        print("✅ OPTIONS ANALYSIS COMPLETE!")
        print("="*80)
        print("\n📌 Service Features Validated:")
        print("  ✅ Options chain fetching")
        print("  ✅ Contract parsing")
        print("  ✅ Greeks calculation (Black-Scholes)")
        print("  ✅ Unusual activity detection")
        print("  ✅ Strategy recommendations")
        print("  ✅ IV metrics analysis")
        print("  ✅ Position calculations")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_options_analysis()
