"""
Simple script to test FRED API and show Treasury yields
"""
import requests
import json
import sys

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

# Fetch 10Y Treasury
print("\n[10Y] Fetching 10-Year Treasury Yield (DGS10)...")
# Use sort_order=desc to get most recent data first
url_10y = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={fred_api_key}&file_type=json&limit=10&sort_order=desc"
response_10y = requests.get(url_10y, timeout=10)

if response_10y.status_code == 200:
    data_10y = response_10y.json()
    observations_10y = data_10y.get('observations', [])
    print(f"[OK] Received {len(observations_10y)} observations")
    print("\nLast 5 observations for 10Y Treasury:")
    for obs in observations_10y[-5:]:
        print(f"  Date: {obs['date']} | Value: {obs['value']}")

    # Get current value
    if observations_10y:
        latest_10y = observations_10y[-1]
        current_10y_value = latest_10y['value']
        current_10y_date = latest_10y['date']
        print(f"\n[OK] Current 10Y Yield: {current_10y_value}% (as of {current_10y_date})")
else:
    print(f"[ERROR] Error fetching 10Y data: HTTP {response_10y.status_code}")
    print(f"  Response: {response_10y.text[:200]}")

# Fetch 2Y Treasury
print("\n[2Y] Fetching 2-Year Treasury Yield (DGS2)...")
# Use sort_order=desc to get most recent data first
url_2y = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS2&api_key={fred_api_key}&file_type=json&limit=10&sort_order=desc"
response_2y = requests.get(url_2y, timeout=10)

if response_2y.status_code == 200:
    data_2y = response_2y.json()
    observations_2y = data_2y.get('observations', [])
    print(f"[OK] Received {len(observations_2y)} observations")
    print("\nLast 5 observations for 2Y Treasury:")
    for obs in observations_2y[-5:]:
        print(f"  Date: {obs['date']} | Value: {obs['value']}")

    # Get current value
    if observations_2y:
        latest_2y = observations_2y[-1]
        current_2y_value = latest_2y['value']
        current_2y_date = latest_2y['date']
        print(f"\n[OK] Current 2Y Yield: {current_2y_value}% (as of {current_2y_date})")
else:
    print(f"[ERROR] Error fetching 2Y data: HTTP {response_2y.status_code}")
    print(f"  Response: {response_2y.text[:200]}")

# Calculate spread
print("\n" + "="*60)
print("YIELD CURVE ANALYSIS")
print("="*60)

if response_10y.status_code == 200 and response_2y.status_code == 200:
    if observations_10y and observations_2y:
        try:
            value_10y = float(current_10y_value) if current_10y_value != '.' else None
            value_2y = float(current_2y_value) if current_2y_value != '.' else None

            if value_10y is not None and value_2y is not None:
                spread = value_10y - value_2y

                print(f"\n10-Year Yield:  {value_10y:.3f}%")
                print(f"2-Year Yield:   {value_2y:.3f}%")
                print(f"Spread (10Y-2Y): {spread:+.3f}%")

                print("\nInterpretation:")
                if spread < -0.2:
                    print("  [WARNING] INVERTED - Strong recession warning")
                elif spread < 0:
                    print("  [WARNING] NEAR INVERSION - Caution warranted")
                elif spread < 0.5:
                    print("  [CAUTION] FLAT - Economic slowdown possible")
                else:
                    print("  [NORMAL] NORMAL - Healthy yield curve")

                print(f"\nData dates:")
                print(f"  10Y: {current_10y_date}")
                print(f"  2Y:  {current_2y_date}")

                # Check if data is stale
                from datetime import datetime, timedelta
                date_10y = datetime.strptime(current_10y_date, '%Y-%m-%d')
                date_2y = datetime.strptime(current_2y_date, '%Y-%m-%d')
                today = datetime.now()

                days_old_10y = (today - date_10y).days
                days_old_2y = (today - date_2y).days

                if days_old_10y > 3 or days_old_2y > 3:
                    print(f"\n[WARNING] Data may be stale!")
                    print(f"  10Y data is {days_old_10y} days old")
                    print(f"  2Y data is {days_old_2y} days old")
                    print("\n  Possible reasons:")
                    print("  - Weekend or market holiday (no new data)")
                    print("  - FRED API not updated yet today")
                    print("  - Data feed issue")
            else:
                print("\n[ERROR] Cannot calculate spread - values contain '.' (missing data)")
                print(f"  10Y value: {current_10y_value}")
                print(f"  2Y value: {current_2y_value}")
        except Exception as e:
            print(f"\n[ERROR] Error calculating spread: {e}")
    else:
        print("\n[ERROR] No observations available")
else:
    print("\n[ERROR] Cannot calculate spread - API errors")

print("\n" + "="*60)
print("\n[INFO] To verify, check current yields at:")
print("   - https://www.treasury.gov/resource-center/data-chart-center/interest-rates/")
print("   - https://www.cnbc.com/quotes/US10Y")
print("   - https://www.cnbc.com/quotes/US2Y")
