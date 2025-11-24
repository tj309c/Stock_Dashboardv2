"""
Test the new Put/Call ratio fetching with multiple ticker fallback
"""

import sys
import yfinance as yf

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("PUT/CALL RATIO FIX TEST")
print("=" * 80)
print()

tickers_to_try = [
    ("^CPCE", "CBOE Equity Put/Call"),  # Most reliable
    ("^PCALL", "CBOE Total Put/Call"),
    ("^PCCE", "CBOE Equity Put/Call Alt")
]

success = False

for ticker, name in tickers_to_try:
    print(f"Trying {ticker} ({name})...")
    try:
        pcr = yf.Ticker(ticker)
        hist = pcr.history(period='5d')
        if not hist.empty and len(hist) > 0:
            ratio = hist['Close'].iloc[-1]
            # Sanity check: put/call ratios are typically between 0.3 and 2.0
            if 0.3 <= ratio <= 2.0:
                print(f"  ✓ SUCCESS! Put/Call Ratio: {ratio:.3f}")
                print(f"  Data points: {len(hist)}")
                print(f"  Last 3 values: {hist['Close'].tail(3).tolist()}")
                success = True
                break
            else:
                print(f"  ✗ Value out of range: {ratio:.3f} (expected 0.3-2.0)")
        else:
            print(f"  ✗ No data returned")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()

if not success:
    print("❌ All Put/Call ratio sources failed - using fallback value 1.0")
else:
    print()
    print("✅ Put/Call ratio successfully fetched!")

print()
print("=" * 80)
