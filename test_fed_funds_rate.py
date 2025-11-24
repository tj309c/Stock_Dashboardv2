"""
Simple script to check Fed Funds Rate from FRED API
"""
import requests
import sys
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read FRED API key from secrets
try:
    with open('.streamlit/secrets.toml', 'r') as f:
        content = f.read()
        # Extract FRED_API_KEY
        for line in content.split('\n'):
            if 'FRED_API_KEY' in line:
                fred_api_key = line.split('=')[1].strip().strip('"').strip("'")
                break
except Exception as e:
    print(f"Error reading secrets: {e}")
    print("Please ensure .streamlit/secrets.toml exists with FRED_API_KEY")
    exit(1)

print(f"[OK] FRED API Key found: {fred_api_key[:10]}...")

# Fetch Fed Funds Rate
print("\n[FED FUNDS] Fetching Federal Funds Rate (FEDFUNDS)...")
print("Note: FEDFUNDS is the EFFECTIVE Federal Funds Rate (actual rate in the market)")
print("      This is different from the Fed's TARGET rate range")

# Use sort_order=desc to get most recent data first
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={fred_api_key}&file_type=json&limit=20&sort_order=desc"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    observations = data.get('observations', [])
    print(f"[OK] Received {len(observations)} observations")

    print("\nLast 10 observations for Fed Funds Rate:")
    print("(Monthly data - last day of each month)")
    print("(Sorted by FRED API with sort_order=desc, newest first):")
    for i, obs in enumerate(observations[:10]):  # Show first 10 from the desc-sorted list
        print(f"  [{i}] Date: {obs['date']} | Value: {obs['value']}%")

    # Get current value
    if observations:
        # Find the most recent non-missing value
        current_value = None
        current_date = None

        for obs in observations:
            if obs['value'] != '.':
                current_value = obs['value']
                current_date = obs['date']
                break

        if current_value:
            print(f"\n[OK] Current Fed Funds Rate: {current_value}% (as of {current_date})")

            # Check how old the data is
            date_obj = datetime.strptime(current_date, '%Y-%m-%d')
            today = datetime.now()
            days_old = (today - date_obj).days

            print(f"\n[INFO] Data age: {days_old} days old")

            if days_old > 45:
                print(f"[WARNING] Data is quite old!")
                print("  Note: Fed Funds Rate is updated MONTHLY, not daily")
                print("  Data is typically 2-3 weeks delayed after month end")
else:
    print(f"[ERROR] Error fetching data: HTTP {response.status_code}")
    print(f"  Response: {response.text[:200]}")

print("\n" + "="*70)
print("UNDERSTANDING FED FUNDS RATE")
print("="*70)

print("""
There are TWO different "Fed Funds Rate" concepts:

1. EFFECTIVE Fed Funds Rate (FEDFUNDS) - shown above
   - This is what FRED returns
   - The actual overnight rate banks charge each other
   - Updated MONTHLY (last day of month)
   - Typically 2-3 weeks delayed

2. Federal Reserve TARGET Rate Range
   - This is what you see in news headlines
   - Set by the Federal Reserve at FOMC meetings
   - Currently a RANGE (e.g., 4.50% - 4.75%)
   - Updated immediately when Fed changes policy
   - NOT directly available from FRED's FEDFUNDS series

The EFFECTIVE rate (FEDFUNDS) usually trades within the TARGET range.

EXAMPLE:
- Fed announces target range: 4.50% - 4.75%
- Effective rate (FEDFUNDS): ~4.58% (trades within the range)
- Headlines say "Fed rate is 4.75%" (referring to top of target range)
- FRED shows "4.58%" (the actual effective rate)

Both are correct, but they're measuring different things!
""")

print("="*70)
print("\n[INFO] To verify current Fed policy:")
print("   - https://www.federalreserve.gov/monetarypolicy/openmarket.htm")
print("   - https://www.newyorkfed.org/markets/reference-rates/effr")
print("   - https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html")
print("\n[INFO] Google 'current fed funds rate' shows:")
print("   - Usually the TOP of the target range (e.g., 4.75%)")
print("   - Or sometimes the midpoint of the range (e.g., 4.625%)")
print("   - Rarely shows the effective rate")
