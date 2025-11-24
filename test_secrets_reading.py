"""
Test how secrets are being read from secrets.toml
"""
import streamlit as st

# Force reload secrets
if hasattr(st, 'secrets'):
    print("\n=== Checking Secrets ===")

    # Check if keys exist
    print(f"OPENAI_API_KEY exists: {'OPENAI_API_KEY' in st.secrets}")
    print(f"ANTHROPIC_API_KEY exists: {'ANTHROPIC_API_KEY' in st.secrets}")
    print(f"GEMINI_API_KEY exists: {'GEMINI_API_KEY' in st.secrets}")
    print(f"XAI_API_KEY exists: {'XAI_API_KEY' in st.secrets}")

    # Check key lengths
    if 'OPENAI_API_KEY' in st.secrets:
        key = st.secrets['OPENAI_API_KEY']
        print(f"\nOPENAI_API_KEY:")
        print(f"  Length: {len(key)}")
        print(f"  First 10 chars: {key[:10]}")
        print(f"  Last 10 chars: {key[-10:]}")
        print(f"  Full key: {key}")

    if 'ANTHROPIC_API_KEY' in st.secrets:
        key = st.secrets['ANTHROPIC_API_KEY']
        print(f"\nANTHROPIC_API_KEY:")
        print(f"  Length: {len(key)}")
        print(f"  First 10 chars: {key[:10]}")
        print(f"  Last 10 chars: {key[-10:]}")
        print(f"  Full key: {key}")

    if 'GEMINI_API_KEY' in st.secrets:
        key = st.secrets['GEMINI_API_KEY']
        print(f"\nGEMINI_API_KEY:")
        print(f"  Length: {len(key)}")
        print(f"  First 10 chars: {key[:10]}")
        print(f"  Last 10 chars: {key[-10:]}")
else:
    print("ERROR: st.secrets not available outside streamlit run")
    print("Please run this with: streamlit run test_secrets_reading.py")
