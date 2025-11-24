"""
Test with the exact key without any string manipulation
"""
import toml

# Read secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

print("Testing with EXACT key from file...\n")

# Test OpenAI with exact key
print("OpenAI Key Test:")
openai_key = secrets['OPENAI_API_KEY']
print(f"Key type: {type(openai_key)}")
print(f"Key repr: {repr(openai_key)}")
print(f"Key has newlines: {chr(10) in openai_key or chr(13) in openai_key}")
print(f"Key has extra spaces: {openai_key != openai_key.strip()}")

if openai_key != openai_key.strip():
    print("WARNING: Key has leading/trailing whitespace!")
    openai_key = openai_key.strip()

try:
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=5
    )
    print(f"SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "="*50 + "\n")

# Test Anthropic with exact key
print("Anthropic Key Test:")
anthropic_key = secrets['ANTHROPIC_API_KEY']
print(f"Key type: {type(anthropic_key)}")
print(f"Key repr: {repr(anthropic_key)}")
print(f"Key has newlines: {chr(10) in anthropic_key or chr(13) in anthropic_key}")
print(f"Key has extra spaces: {anthropic_key != anthropic_key.strip()}")

if anthropic_key != anthropic_key.strip():
    print("WARNING: Key has leading/trailing whitespace!")
    anthropic_key = anthropic_key.strip()

try:
    import anthropic
    client = anthropic.Anthropic(api_key=anthropic_key)
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=5,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print(f"SUCCESS: {response.content[0].text}")
except Exception as e:
    print(f"FAILED: {e}")
