"""
Test Claude/Anthropic API key specifically
"""
import toml

# Read secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

print("Testing Claude/Anthropic API Key...\n")

anthropic_key = secrets['ANTHROPIC_API_KEY']
print(f"Key starts with: {anthropic_key[:20]}")
print(f"Key ends with: {anthropic_key[-20:]}")
print(f"Key length: {len(anthropic_key)}")
print()

try:
    import anthropic

    # Test with the exact key
    client = anthropic.Anthropic(api_key=anthropic_key)

    # Try a simple request
    print("Attempting API call...")
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Using cheapest model
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello"}]
    )

    print(f"\nSUCCESS!")
    print(f"Response: {response.content[0].text}")
    print(f"\nYour Claude API key is working!")

except Exception as e:
    print(f"\nFAILED: {e}")
    print("\nPossible issues:")
    print("1. The API key might be expired or revoked")
    print("2. You might need to generate a new key at: https://console.anthropic.com/settings/keys")
    print("3. If you recently created the key, it might take a few minutes to activate")
