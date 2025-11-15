#!/bin/bash
# Quick API Keys Registration Helper
# Opens all API registration pages in your browser

echo "🔑 Opening API Registration Pages..."
echo ""

echo "1️⃣  Opening Reddit API registration..."
"$BROWSER" "https://www.reddit.com/prefs/apps" &
sleep 2

echo "2️⃣  Opening News API registration..."
"$BROWSER" "https://newsapi.org/register" &
sleep 2

echo "3️⃣  Opening Finnhub API registration..."
"$BROWSER" "https://finnhub.io/register" &
sleep 2

echo "4️⃣  Opening Alpha Vantage API registration..."
"$BROWSER" "https://www.alphavantage.co/support/#api-key" &
sleep 2

echo "5️⃣  Opening EIA API registration..."
"$BROWSER" "https://www.eia.gov/opendata/register.php" &
sleep 2

echo ""
echo "✅ All registration pages opened!"
echo ""
echo "📝 Follow the instructions in API_SETUP_INSTRUCTIONS.md"
echo "   After getting your keys, edit .streamlit/secrets.toml"
echo ""
