"""Quick test script to verify Google Trends is working for TSLA"""

import sys
sys.path.insert(0, r'c:\Users\603506\Desktop\Trevor_Python\Stocks')

from news_fetcher import get_google_trends_data
import json

print("Testing Google Trends for TSLA...")
print("=" * 60)

# Test with TSLA
trends_data = get_google_trends_data("TSLA", "Tesla", timeframe='today 1-m')

print("\nGoogle Trends Results for TSLA:")
print(json.dumps(trends_data, indent=2, default=str))

print("\n" + "=" * 60)
if trends_data.get('available'):
    print("SUCCESS: Google Trends is working!")
    print(f"   Current Interest: {trends_data.get('current_interest')}/100")
    print(f"   Trend: {trends_data.get('trend')}")
    print(f"   Direction: {trends_data.get('trend_direction')}")
    print(f"   Data Points: {trends_data.get('data_points')}")
    if trends_data.get('related_queries'):
        print(f"   Related Queries: {', '.join(trends_data.get('related_queries', []))}")
else:
    print("FAILED: Google Trends is not returning data")
    print("   This could be due to:")
    print("   - pytrends not installed (check requirements.txt)")
    print("   - Google blocking automated requests")
    print("   - Network connectivity issues")
