"""
Test script to verify AI provider configuration and API calls
"""
import streamlit as st
from ai_model_config import (
    get_available_providers,
    get_models_by_provider,
    call_ai_model,
    is_provider_configured,
    AIProvider
)

def test_provider_configuration():
    """Test if all providers are properly configured"""
    print("\n=== Testing Provider Configuration ===")

    for provider in AIProvider:
        is_configured = is_provider_configured(provider)
        status = "CONFIGURED" if is_configured else "NOT CONFIGURED"
        print(f"{provider.value}: {status}")

    available_providers = get_available_providers()
    print(f"\nAvailable providers: {[p.value for p in available_providers]}")

    return available_providers

def test_ai_calls():
    """Test actual AI API calls"""
    print("\n=== Testing AI API Calls ===")

    # Initialize session state for testing
    if 'global_ai_model' not in st.session_state:
        st.session_state['global_ai_model'] = 'gemini-2.5-flash'

    providers = get_available_providers()

    test_prompt = "Say 'Hello, I am working!' in one sentence."

    results = {}
    for provider in providers:
        print(f"\nTesting {provider.value}...")
        try:
            models = get_models_by_provider(provider)
            if not models:
                print(f"  No models available for {provider.value}")
                results[provider.value] = "No models available"
                continue

            model_info = models[0]  # Use first model
            print(f"  Using model: {model_info.model_id}")

            response = call_ai_model(
                model_info,
                test_prompt,
                max_tokens=50,
                temperature=0.3,
                session_key="global_ai_model"
            )

            if response and not response.startswith("failed:"):
                print(f"  SUCCESS: {response[:100]}")
                results[provider.value] = "SUCCESS"
            else:
                print(f"  FAILED: {response}")
                results[provider.value] = response

        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results[provider.value] = f"Error: {str(e)}"

    return results

if __name__ == "__main__":
    print("Starting AI Provider Tests...")

    # Test configuration
    available_providers = test_provider_configuration()

    if not available_providers:
        print("\nWARNING: No AI providers are configured!")
        print("Please check your .streamlit/secrets.toml file")
    else:
        # Test actual API calls
        results = test_ai_calls()

        print("\n=== Test Summary ===")
        for provider, result in results.items():
            status = "[OK]" if result == "SUCCESS" else "[FAIL]"
            print(f"{status} {provider}: {result}")
