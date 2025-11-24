"""
Test sector data fetching and structure
"""

import sys
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("SECTOR DATA STRUCTURE TEST")
print("=" * 80)
print()

# Fetch one sector as test
print("Fetching Technology sector (XLK)...")
try:
    stock = yf.Ticker('XLK')
    hist = stock.history(period='1mo')

    if not hist.empty:
        current_price = hist['Close'].iloc[-1]
        month_ago_price = hist['Close'].iloc[0]
        change_1m = ((current_price - month_ago_price) / month_ago_price * 100)

        # 5-day performance
        if len(hist) >= 5:
            week_ago_price = hist['Close'].iloc[-5]
            change_5d = ((current_price - week_ago_price) / week_ago_price * 100)
        else:
            change_5d = 0

        # 1-day performance
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            change_1d = ((current_price - prev_close) / prev_close * 100)
        else:
            change_1d = 0

        data = {
            'ticker': 'XLK',
            'price': current_price,
            'change_1d': change_1d,
            'change_5d': change_5d,
            'change_1m': change_1m,
        }

        print(f"✓ Successfully fetched Technology sector data")
        print(f"  Price: ${current_price:.2f}")
        print(f"  Data structure: {data.keys()}")
        print(f"  change_1d: {change_1d:+.2f}%")
        print(f"  change_5d: {change_5d:+.2f}%")
        print(f"  change_1m: {change_1m:+.2f}%")
        print()
        print("❌ PROBLEM: Data has 'change_1d', 'change_5d', 'change_1m'")
        print("❌ But render_sector_rotation_heatmap() expects 'change_pct'")
        print()
        print("MISMATCH CONFIRMED!")

    else:
        print("✗ No data returned")

except Exception as e:
    print(f"✗ Error: {e}")

print()
print("=" * 80)
