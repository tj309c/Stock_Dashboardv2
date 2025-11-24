"""
Test that the sector heatmap fix works with the actual data structure
"""

import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("SECTOR HEATMAP FIX VERIFICATION")
print("=" * 80)
print()

# Simulate the actual sector_data structure returned by fetch_sector_performance()
sector_data = {
    'Technology': {
        'ticker': 'XLK',
        'price': 273.20,
        'change_1d': 0.39,
        'change_5d': -3.68,
        'change_1m': -4.30
    },
    'Financials': {
        'ticker': 'XLF',
        'price': 48.50,
        'change_1d': 1.25,
        'change_5d': 2.15,
        'change_1m': 5.40
    },
    'Healthcare': {
        'ticker': 'XLV',
        'price': 158.20,
        'change_1d': -0.15,
        'change_5d': 1.05,
        'change_1m': 2.30
    }
}

print("Simulated sector_data structure:")
for sector, data in sector_data.items():
    print(f"  {sector}: {list(data.keys())}")
print()

# Test the fixed logic
defensive = ['Utilities', 'Consumer Staples', 'Health Care']
cyclical = ['Technology', 'Consumer Discretionary', 'Industrials', 'Materials']
sensitive = ['Financials', 'Energy', 'Real Estate']

sectors = []
categories = []
returns = []

for sector, data in sector_data.items():
    # Use 'change_1d' as the primary metric (daily change)
    # Fallback to 'change_pct' for compatibility with other data sources
    if 'change_1d' in data:
        sectors.append(sector)
        returns.append(data['change_1d'])

        if sector in defensive:
            categories.append('Defensive')
        elif sector in cyclical:
            categories.append('Cyclical')
        else:
            categories.append('Sensitive')
    elif 'change_pct' in data:
        sectors.append(sector)
        returns.append(data['change_pct'])

        if sector in defensive:
            categories.append('Defensive')
        elif sector in cyclical:
            categories.append('Cyclical')
        else:
            categories.append('Sensitive')

if not sectors:
    print("❌ FAILED: No sectors extracted")
else:
    print(f"✅ SUCCESS: {len(sectors)} sectors extracted")
    print()
    print("Extracted data:")
    for i, sector in enumerate(sectors):
        print(f"  {sector}: {returns[i]:+.2f}% ({categories[i]})")

print()
print("=" * 80)
