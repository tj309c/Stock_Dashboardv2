"""
Show exactly what keys are being read from secrets.toml
"""
import toml

# Read secrets directly
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

print("=== Keys Being Read from secrets.toml ===\n")

keys_to_check = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'XAI_API_KEY']

for key_name in keys_to_check:
    if key_name in secrets:
        key_value = secrets[key_name]
        print(f"{key_name}:")
        print(f"  Full key: {key_value}")
        print(f"  Length: {len(key_value)}")
        print(f"  First 20 chars: {key_value[:20]}")
        print(f"  Last 20 chars: {key_value[-20:]}")
        print()
    else:
        print(f"{key_name}: NOT FOUND")
        print()
