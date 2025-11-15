#!/bin/bash
# Quick Setup Script for Analysis Master: One Ring To Rule Them All
# Installs all dependencies and creates necessary config files

echo "🚀 Analysis Master - Quick Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
echo "This may take a few minutes..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Create .streamlit directory if it doesn't exist
if [ ! -d ".streamlit" ]; then
    mkdir .streamlit
    echo "📁 Created .streamlit directory"
fi

# Create secrets.toml template if it doesn't exist
if [ ! -f ".streamlit/secrets.toml" ]; then
    cat > .streamlit/secrets.toml << 'EOF'
# API Keys for Analysis Master
# Get free API keys from:
# - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
# - EIA: https://www.eia.gov/opendata/register.php
# - Finnhub: https://finnhub.io/register
# - Alpha Vantage: https://www.alphavantage.co/support/#api-key
# - NewsAPI: https://newsapi.org/register
# - Anthropic (Claude): https://console.anthropic.com/

# Federal Reserve Economic Data (FRED) - Free
FRED_API_KEY = ""

# Energy Information Administration - Free
EIA_API_KEY = ""

# Finnhub (Insider Trades) - Free tier: 60 req/min
FINNHUB_API_KEY = ""

# Alpha Vantage (Fundamentals) - Free tier: 5 req/min
ALPHA_VANTAGE_API_KEY = ""

# NewsAPI (News sentiment) - Free tier: 100 req/day
NEWSAPI_KEY = ""

# Anthropic Claude (LLM Predictions) - Paid (but cheap)
# $3 per million input tokens, $15 per million output tokens
ANTHROPIC_API_KEY = ""

# Reddit API (for sentiment scraping)
# Create app at: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = "StocksAnalyzer/1.0"
EOF
    echo "📝 Created .streamlit/secrets.toml template"
    echo "⚠️  Please edit .streamlit/secrets.toml and add your API keys"
else
    echo "ℹ️  .streamlit/secrets.toml already exists"
fi

# Create config.toml if it doesn't exist
if [ ! -f ".streamlit/config.toml" ]; then
    cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#00FF88"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#1C1F26"
textColor = "#FAFAFA"
font = "sans serif"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOF
    echo "📝 Created .streamlit/config.toml"
else
    echo "ℹ️  .streamlit/config.toml already exists"
fi

echo ""
echo "==========================================="
echo "✅ Setup Complete!"
echo "==========================================="
echo ""
echo "📋 Next Steps:"
echo "1. Edit .streamlit/secrets.toml and add your API keys (see links in file)"
echo "2. Run: streamlit run main.py"
echo "3. Open browser to http://localhost:8501"
echo ""
echo "🔑 Minimum Required Keys (for basic functionality):"
echo "   - FRED_API_KEY (economic data)"
echo "   - None! App works without keys, but with limited features"
echo ""
echo "🚀 Optional Keys (for full features):"
echo "   - EIA_API_KEY (energy prices)"
echo "   - FINNHUB_API_KEY (insider trades)"
echo "   - ALPHA_VANTAGE_API_KEY (fundamentals)"
echo "   - NEWSAPI_KEY (news sentiment)"
echo "   - ANTHROPIC_API_KEY (AI predictions)"
echo ""
echo "💡 All APIs have free tiers except Anthropic (but it's cheap)"
echo "==========================================="
