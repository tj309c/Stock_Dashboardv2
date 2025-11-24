"""
Test Sector Rotation calculation accuracy and check current market conditions
"""

import sys
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("SECTOR ROTATION ACCURACY TEST")
print("=" * 80)
print()

# Fetch sector data
sectors = {
    'Technology': 'XLK',
    'Financials': 'XLF',
    'Healthcare': 'XLV',
    'Energy': 'XLE',
    'Industrials': 'XLI',
    'Consumer Discretionary': 'XLY',
    'Consumer Staples': 'XLP',
    'Utilities': 'XLU',
    'Real Estate': 'XLRE',
    'Materials': 'XLB',
    'Communication': 'XLC'
}

# Categorize
growth_sectors = ['Technology', 'Communication', 'Consumer Discretionary']
value_sectors = ['Financials', 'Energy', 'Utilities', 'Consumer Staples']

def fetch_single_sector(name, ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')

        if hist.empty:
            return name, None

        current_price = hist['Close'].iloc[-1]

        # 5-day performance
        if len(hist) >= 5:
            week_ago_price = hist['Close'].iloc[-5]
            change_5d = ((current_price - week_ago_price) / week_ago_price * 100)
        else:
            change_5d = 0

        # 1-month performance (for comparison)
        month_ago_price = hist['Close'].iloc[0]
        change_1m = ((current_price - month_ago_price) / month_ago_price * 100)

        return name, {
            'change_5d': change_5d,
            'change_1m': change_1m
        }
    except Exception as e:
        return name, None

print("Fetching sector performance data...")
print()

results = {}
with ThreadPoolExecutor(max_workers=11) as executor:
    futures = {executor.submit(fetch_single_sector, name, ticker): name
              for name, ticker in sectors.items()}

    for future in as_completed(futures):
        name, data = future.result()
        if data:
            results[name] = data

# Display results
print("SECTOR PERFORMANCE")
print("-" * 80)
print(f"{'Sector':<25} {'5-Day':<12} {'1-Month':<12} {'Category'}")
print("-" * 80)

growth_5d = []
value_5d = []
growth_1m = []
value_1m = []

for sector, data in sorted(results.items()):
    category = ""
    if sector in growth_sectors:
        category = "GROWTH"
        growth_5d.append(data['change_5d'])
        growth_1m.append(data['change_1m'])
    elif sector in value_sectors:
        category = "VALUE"
        value_5d.append(data['change_5d'])
        value_1m.append(data['change_1m'])
    else:
        category = "Other"

    print(f"{sector:<25} {data['change_5d']:+.2f}%      {data['change_1m']:+.2f}%      {category}")

print()
print("=" * 80)
print("ROTATION ANALYSIS")
print("=" * 80)

# 5-day analysis (current implementation)
if growth_5d and value_5d:
    avg_growth_5d = sum(growth_5d) / len(growth_5d)
    avg_value_5d = sum(value_5d) / len(value_5d)
    difference_5d = avg_growth_5d - avg_value_5d

    print(f"\n5-DAY ROTATION (Current Implementation):")
    print(f"  Growth average: {avg_growth_5d:+.2f}%")
    print(f"  Value average:  {avg_value_5d:+.2f}%")
    print(f"  Difference:     {difference_5d:+.2f}%")
    print(f"  Threshold:      ±1.5%")

    if difference_5d > 1.5:
        signal = "🚀 Growth Outperforming"
    elif difference_5d < -1.5:
        signal = "🏦 Value Outperforming"
    else:
        signal = "⚖️ Balanced"

    print(f"  Signal:         {signal}")

# 1-month analysis (suggested improvement)
if growth_1m and value_1m:
    avg_growth_1m = sum(growth_1m) / len(growth_1m)
    avg_value_1m = sum(value_1m) / len(value_1m)
    difference_1m = avg_growth_1m - avg_value_1m

    print(f"\n1-MONTH ROTATION (Suggested Alternative):")
    print(f"  Growth average: {avg_growth_1m:+.2f}%")
    print(f"  Value average:  {avg_value_1m:+.2f}%")
    print(f"  Difference:     {difference_1m:+.2f}%")
    print(f"  Threshold:      ±1.5%")

    if difference_1m > 1.5:
        signal_1m = "🚀 Growth Outperforming"
    elif difference_1m < -1.5:
        signal_1m = "🏦 Value Outperforming"
    else:
        signal_1m = "⚖️ Balanced"

    print(f"  Signal:         {signal_1m}")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)

if abs(difference_5d) < 1.5 and abs(difference_1m) > 1.5:
    print("⚠️ ISSUE DETECTED: 5-day shows 'Balanced' but 1-month shows clear rotation!")
    print("   The 5-day window is TOO SHORT and missing the real trend.")
    print("   Recommendation: Use 1-month performance or lower threshold.")
elif abs(difference_5d) < 1.5:
    print("✓ 5-day and 1-month both show balanced market - signal is accurate.")
else:
    print("✓ 5-day is detecting rotation - signal is working.")

print()
print("RECOMMENDATIONS:")
print("1. Use 'change_1m' instead of 'change_5d' for more stable rotation signals")
print("2. OR lower threshold from ±1.5% to ±0.75% for 5-day analysis")
print("3. Add trend arrows showing if rotation is strengthening or weakening")
print("4. Show both short-term (5d) and medium-term (1m) rotation side-by-side")

print()
print("=" * 80)
