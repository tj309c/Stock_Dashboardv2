"""
Direct test reading from secrets.toml file
"""
import toml

# Read secrets directly
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

print("=== Testing API Keys Directly ===\n")

# Test OpenAI
print("Testing OpenAI...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello in one word"}],
        max_tokens=10
    )
    print(f"OpenAI SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"OpenAI FAILED: {str(e)[:200]}")

# Test Anthropic
print("\nTesting Anthropic...")
try:
    import anthropic
    client = anthropic.Anthropic(api_key=secrets['ANTHROPIC_API_KEY'])
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello in one word"}]
    )
    print(f"Anthropic SUCCESS: {response.content[0].text}")
except Exception as e:
    print(f"Anthropic FAILED: {str(e)[:200]}")

# Test Gemini
print("\nTesting Gemini...")
try:
    import google.generativeai as genai
    genai.configure(api_key=secrets['GEMINI_API_KEY'])
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content("Say hello in one word")
    print(f"Gemini SUCCESS: {response.text}")
except Exception as e:
    print(f"Gemini FAILED: {str(e)[:200]}")

# Test Grok
print("\nTesting Grok...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=secrets['XAI_API_KEY'], base_url="https://api.x.ai/v1")
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[{"role": "user", "content": "Say hello in one word"}],
        max_tokens=10
    )
    print(f"Grok SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"Grok FAILED: {str(e)[:200]}")
