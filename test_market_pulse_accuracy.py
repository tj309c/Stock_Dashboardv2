"""
Test script to verify Market Pulse tab accuracy and identify issues
"""

import sys
import yfinance as yf
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("MARKET PULSE TAB ACCURACY TEST")
print("=" * 80)
print()

# Test 1: Market Indices Fetching
print("TEST 1: Market Indices")
print("-" * 80)
indices = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'Dow Jones': '^DJI',
    'Russell 2000': '^RUT',
    'VIX': '^VIX'
}

indices_data = {}
for name, ticker in indices.items():
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            pct_change = (change / prev_close * 100) if prev_close != 0 else 0
            indices_data[name] = {
                'price': current_price,
                'change': change,
                'pct_change': pct_change
            }
            print(f"✓ {name}: ${current_price:.2f} ({pct_change:+.2f}%)")
        else:
            print(f"✗ {name}: NO DATA")
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")

print()

# Test 2: Market Health Score Calculation
print("TEST 2: Market Health Score")
print("-" * 80)

# Calculate breadth
try:
    spy = yf.Ticker('SPY')
    hist = spy.history(period='5d')
    if not hist.empty:
        current = hist['Close'].iloc[-1]
        avg_5d = hist['Close'].mean()
        breadth_score = (current / avg_5d - 1) * 100

        if breadth_score > 1:
            breadth_status = "Strong"
        elif breadth_score > 0:
            breadth_status = "Positive"
        elif breadth_score > -1:
            breadth_status = "Weak"
        else:
            breadth_status = "Very Weak"

        print(f"Market Breadth: {breadth_status} (Score: {breadth_score:.2f}%)")
    else:
        breadth_score = None
        breadth_status = None
        print("Market Breadth: NO DATA")
except Exception as e:
    breadth_score = None
    breadth_status = None
    print(f"Market Breadth: ERROR - {e}")

# Calculate health score
health_score = 50  # baseline

# Factor 1: S&P 500 momentum (40 points)
if 'S&P 500' in indices_data:
    sp_pct = indices_data['S&P 500']['pct_change']
    print(f"\nFactor 1 - S&P 500 Momentum: {sp_pct:+.2f}%")
    if sp_pct > 1:
        health_score += 20
        print(f"  Impact: +20 points (strong positive)")
    elif sp_pct > 0:
        health_score += 10
        print(f"  Impact: +10 points (positive)")
    elif sp_pct > -1:
        health_score -= 10
        print(f"  Impact: -10 points (slightly negative)")
    else:
        health_score -= 20
        print(f"  Impact: -20 points (strongly negative)")

# Factor 2: VIX level (30 points)
if 'VIX' in indices_data:
    vix = indices_data['VIX']['price']
    print(f"\nFactor 2 - VIX Level: {vix:.2f}")
    if vix < 15:
        health_score += 15
        print(f"  Impact: +15 points (very calm)")
    elif vix < 20:
        health_score += 10
        print(f"  Impact: +10 points (calm)")
    elif vix < 30:
        health_score -= 10
        print(f"  Impact: -10 points (elevated)")
    else:
        health_score -= 15
        print(f"  Impact: -15 points (high fear)")

# Factor 3: Market breadth (30 points)
if breadth_status:
    print(f"\nFactor 3 - Market Breadth: {breadth_status}")
    if breadth_status == 'Strong':
        health_score += 15
        print(f"  Impact: +15 points")
    elif breadth_status == 'Positive':
        health_score += 10
        print(f"  Impact: +10 points")
    elif breadth_status == 'Weak':
        health_score -= 10
        print(f"  Impact: -10 points")
    else:
        health_score -= 15
        print(f"  Impact: -15 points")

# Clamp to 0-100
health_score = max(0, min(100, health_score))

# Categorize
if health_score >= 70:
    category = "Healthy 💪"
elif health_score >= 50:
    category = "Neutral ➡️"
elif health_score >= 30:
    category = "Cautious ⚠️"
else:
    category = "Weak 🚨"

print()
print(f"FINAL HEALTH SCORE: {health_score}/100 - {category}")
print()

# Test 3: Put/Call Ratio
print("TEST 3: Put/Call Ratio")
print("-" * 80)

try:
    pcr = yf.Ticker("^PCALL")
    hist = pcr.history(period='5d')
    if not hist.empty:
        pc_ratio = hist['Close'].iloc[-1]
        print(f"Put/Call Ratio (^PCALL): {pc_ratio:.3f}")

        # Normalize
        if pc_ratio < 0.7:
            pc_score = 100
            sentiment = "Extreme Greed"
        elif pc_ratio < 0.9:
            pc_score = 75
            sentiment = "Greed"
        elif pc_ratio < 1.1:
            pc_score = 50
            sentiment = "Neutral"
        elif pc_ratio < 1.3:
            pc_score = 25
            sentiment = "Fear"
        else:
            pc_score = 0
            sentiment = "Extreme Fear"

        print(f"Normalized Score: {pc_score}/100 ({sentiment})")
    else:
        print("✗ Put/Call Ratio: NO DATA FROM ^PCALL")
        print("\nTrying alternative ticker ^PCCE (CBOE Equity Put/Call)...")

        try:
            pcr_alt = yf.Ticker("^PCCE")
            hist_alt = pcr_alt.history(period='5d')
            if not hist_alt.empty:
                pc_ratio = hist_alt['Close'].iloc[-1]
                print(f"Put/Call Ratio (^PCCE): {pc_ratio:.3f}")
            else:
                print("✗ Put/Call Ratio: NO DATA FROM ^PCCE")
        except Exception as e:
            print(f"✗ Put/Call Ratio (^PCCE): ERROR - {e}")

except Exception as e:
    print(f"✗ Put/Call Ratio: ERROR - {e}")

print()

# Test 4: Fear & Greed Components
print("TEST 4: Fear & Greed Index Components")
print("-" * 80)

# Test VIX normalization
if 'VIX' in indices_data:
    vix = indices_data['VIX']['price']
    if vix < 12:
        vix_score = 100
    elif vix < 17:
        vix_score = 75
    elif vix < 24:
        vix_score = 50
    elif vix < 35:
        vix_score = 25
    else:
        vix_score = 0
    print(f"VIX Component: {vix:.2f} → Score: {vix_score}/100")

# Test distance from 52w high
try:
    ticker = yf.Ticker('^GSPC')
    hist = ticker.history(period='1y')
    if not hist.empty:
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        distance = (current_price / high_52w - 1) * 100

        if distance > -2:
            dist_score = 100
        elif distance > -5:
            dist_score = 75
        elif distance > -10:
            dist_score = 50
        elif distance > -15:
            dist_score = 25
        else:
            dist_score = 0

        print(f"Distance from 52W High: {distance:.2f}% → Score: {dist_score}/100")
    else:
        print("Distance from 52W High: NO DATA")
except Exception as e:
    print(f"Distance from 52W High: ERROR - {e}")

# Test safe haven demand
try:
    gold = yf.Ticker('GLD')
    spy = yf.Ticker('SPY')

    gold_hist = gold.history(period='10d')
    spy_hist = spy.history(period='10d')

    if not gold_hist.empty and not spy_hist.empty:
        gold_return = (gold_hist['Close'].iloc[-1] / gold_hist['Close'].iloc[0] - 1) * 100
        spy_return = (spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0] - 1) * 100
        relative_perf = gold_return - spy_return

        if relative_perf < -3:
            haven_score = 100
        elif relative_perf < -1:
            haven_score = 75
        elif relative_perf < 1:
            haven_score = 50
        elif relative_perf < 3:
            haven_score = 25
        else:
            haven_score = 0

        print(f"Safe Haven Demand: Gold {gold_return:+.2f}% vs SPY {spy_return:+.2f}% → Score: {haven_score}/100")
    else:
        print("Safe Haven Demand: NO DATA")
except Exception as e:
    print(f"Safe Haven Demand: ERROR - {e}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
