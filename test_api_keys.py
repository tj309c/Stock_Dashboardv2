"""
API Keys Verification Script
Tests all configured API keys to verify they work
"""
import os
import sys
from dotenv import load_dotenv
import requests
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def test_news_api():
    """Test NewsAPI key"""
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key or api_key == "your_newsapi_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={api_key}&pageSize=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return {"status": "✅", "message": f"Working - {data.get('totalResults', 0)} articles available"}
            else:
                return {"status": "❌", "message": f"Error: {data.get('message', 'Unknown error')}"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 429:
            return {"status": "⚠️", "message": "Rate limit exceeded"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_fred_api():
    """Test FRED API key"""
    api_key = os.getenv('FRED_API_KEY')
    if not api_key or api_key == "your_fred_api_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={api_key}&limit=1&file_type=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'observations' in data:
                return {"status": "✅", "message": "Working - GDP data accessible"}
            else:
                return {"status": "❌", "message": f"Error: {data.get('error_message', 'Unknown error')}"}
        elif response.status_code == 400:
            return {"status": "❌", "message": "Invalid API key"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_eia_api():
    """Test EIA API key"""
    api_key = os.getenv('EIA_API_KEY')
    if not api_key or api_key == "your_eia_api_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]=RWTC&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'response' in data and 'data' in data['response']:
                return {"status": "✅", "message": "Working - Oil price data accessible"}
            else:
                return {"status": "❌", "message": "Unexpected response format"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_finnhub_api():
    """Test Finnhub API key"""
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key or api_key == "your_finnhub_api_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'c' in data and data['c'] != 0:
                return {"status": "✅", "message": f"Working - AAPL price: ${data['c']}"}
            elif 'error' in data:
                return {"status": "❌", "message": f"Error: {data['error']}"}
            else:
                return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 429:
            return {"status": "⚠️", "message": "Rate limit exceeded"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_alpha_vantage_api():
    """Test Alpha Vantage API key"""
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == "your_alpha_vantage_api_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'Global Quote' in data and data['Global Quote']:
                price = data['Global Quote'].get('05. price', 'N/A')
                return {"status": "✅", "message": f"Working - AAPL price: ${price}"}
            elif 'Note' in data:
                return {"status": "⚠️", "message": "Rate limit exceeded (5 req/min)"}
            elif 'Error Message' in data:
                return {"status": "❌", "message": "Invalid API key"}
            else:
                return {"status": "❌", "message": "Unexpected response"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_gemini_api():
    """Test Google Gemini API key"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_google_gemini_api_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'models' in data:
                model_count = len(data['models'])
                return {"status": "✅", "message": f"Working - {model_count} models available"}
            else:
                return {"status": "❌", "message": "Unexpected response"}
        elif response.status_code == 400 or response.status_code == 403:
            return {"status": "❌", "message": "Invalid API key"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_anthropic_api():
    """Test Anthropic Claude API key"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == "sk-ant-api03-your_anthropic_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Simple test message
        data = {
            "model": "claude-3-5-sonnet-20240620",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            return {"status": "✅", "message": "Working - Claude API accessible"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 429:
            return {"status": "⚠️", "message": "Rate limit exceeded"}
        else:
            error_msg = response.json().get('error', {}).get('message', f"HTTP {response.status_code}")
            return {"status": "❌", "message": error_msg}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_openai_api():
    """Test OpenAI API key"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "sk-your_openai_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # List models endpoint (doesn't consume tokens)
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return {"status": "✅", "message": f"Working - {len(data['data'])} models available"}
            else:
                return {"status": "❌", "message": "Unexpected response"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 429:
            return {"status": "⚠️", "message": "Rate limit exceeded"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_xai_api():
    """Test XAI Grok API key"""
    api_key = os.getenv('XAI_API_KEY')
    if not api_key or api_key == "your_xai_grok_key_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test with a simple completion request
        data = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": "grok-beta",
            "max_tokens": 5
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            return {"status": "✅", "message": "Working - Grok API accessible"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid API key"}
        elif response.status_code == 429:
            return {"status": "⚠️", "message": "Rate limit exceeded"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def test_reddit_api():
    """Test Reddit API credentials"""
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'StocksV3App/1.0')
    
    if not client_id or client_id == "your_reddit_client_id_here":
        return {"status": "❌", "message": "Not configured"}
    
    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'client_credentials'}
        headers = {'User-Agent': user_agent}
        
        response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            auth=auth,
            data=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            if 'access_token' in token_data:
                return {"status": "✅", "message": "Working - Authentication successful"}
            else:
                return {"status": "❌", "message": "No access token in response"}
        elif response.status_code == 401:
            return {"status": "❌", "message": "Invalid client ID or secret"}
        else:
            return {"status": "❌", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌", "message": f"Connection error: {str(e)}"}

def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("🔍 API KEYS VERIFICATION TEST")
    print("="*70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    tests = [
        ("Reddit API", test_reddit_api),
        ("News API", test_news_api),
        ("FRED API", test_fred_api),
        ("EIA API", test_eia_api),
        ("Finnhub API", test_finnhub_api),
        ("Alpha Vantage API", test_alpha_vantage_api),
        ("Google Gemini API", test_gemini_api),
        ("Anthropic Claude API", test_anthropic_api),
        ("OpenAI GPT-4 API", test_openai_api),
        ("XAI Grok API", test_xai_api),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...", end=" ")
        result = test_func()
        results.append((name, result))
        print(f"{result['status']} {result['message']}")
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    working = sum(1 for _, r in results if r['status'] == '✅')
    warning = sum(1 for _, r in results if r['status'] == '⚠️')
    failed = sum(1 for _, r in results if r['status'] == '❌')
    
    print(f"\n✅ Working: {working}")
    print(f"⚠️  Warning: {warning}")
    print(f"❌ Failed: {failed}")
    print(f"\nTotal APIs tested: {len(results)}")
    
    # Save results to JSON
    report = {
        "test_date": datetime.now().isoformat(),
        "summary": {
            "working": working,
            "warning": warning,
            "failed": failed,
            "total": len(results)
        },
        "results": {name: result for name, result in results}
    }
    
    report_file = "api_keys_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("="*70 + "\n")
    
    return working == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
