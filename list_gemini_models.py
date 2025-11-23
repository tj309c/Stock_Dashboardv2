"""
List all available Gemini models and their capabilities
"""
import streamlit as st
import google.generativeai as genai
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("AVAILABLE GEMINI MODELS")
print("=" * 80)

try:
    # Configure with API key
    if 'GOOGLE_API_KEY' in st.secrets:
        genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
    else:
        print("\n❌ ERROR: GOOGLE_API_KEY not found in .streamlit/secrets.toml")
        print("Please add your Google API key to continue.")
        exit(1)

    # List all models
    all_models = list(genai.list_models())

    if not all_models:
        print("\n⚠️  No models found. This could indicate an API issue.")
        exit(1)

    # Categorize models
    gemini_models = []
    other_models = []

    for model in all_models:
        if 'gemini' in model.name.lower():
            gemini_models.append(model)
        else:
            other_models.append(model)

    # Display Gemini models
    print(f"\n📋 GEMINI MODELS ({len(gemini_models)} found):")
    print("-" * 80)

    for idx, model in enumerate(gemini_models, 1):
        print(f"\n{idx}. {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print(f"   Supported Methods: {', '.join(model.supported_generation_methods)}")

        # Check if supports generateContent (what we need)
        if 'generateContent' in model.supported_generation_methods:
            print(f"   ✅ Supports generateContent (RECOMMENDED)")
        else:
            print(f"   ❌ Does NOT support generateContent")

        # Input/output token limits
        if hasattr(model, 'input_token_limit'):
            print(f"   Input Token Limit: {model.input_token_limit:,}")
        if hasattr(model, 'output_token_limit'):
            print(f"   Output Token Limit: {model.output_token_limit:,}")

    # Display other models (for reference)
    if other_models:
        print(f"\n\n📋 OTHER GOOGLE AI MODELS ({len(other_models)} found):")
        print("-" * 80)
        for idx, model in enumerate(other_models, 1):
            print(f"{idx}. {model.name} - {model.display_name}")

    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR THIS STOCK ANALYSIS PLATFORM:")
    print("=" * 80)

    # Find recommended models
    recommended = []
    for model in gemini_models:
        if 'generateContent' in model.supported_generation_methods:
            if '1.5-flash' in model.name.lower():
                recommended.append((model, "⭐⭐⭐ BEST CHOICE - Fast, cost-effective, good for sentiment analysis"))
            elif '1.5-pro' in model.name.lower():
                recommended.append((model, "⭐⭐ PREMIUM CHOICE - Most capable, higher cost"))
            elif 'flash' in model.name.lower():
                recommended.append((model, "⭐ GOOD - Fast and efficient"))

    if recommended:
        print("\n🎯 Recommended Models:")
        for model, reason in recommended:
            print(f"\n   Model: {model.name}")
            print(f"   {reason}")

    # Current usage in codebase
    print("\n" + "=" * 80)
    print("CURRENT CONFIGURATION:")
    print("=" * 80)
    print("\n⚙️  Your platform currently needs to use Gemini models for:")
    print("   - News sentiment analysis (news_fetcher.py)")
    print("   - AI-powered stock insights")
    print("   - Debug dashboard testing")
    print("\n📝 The model is hardcoded in these files:")
    print("   1. news_fetcher.py (line 258)")
    print("   2. pages/06_🔧_Debug_Dashboard.py (line 166)")
    print("   3. ai_services.py (dynamically selects model)")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. Review the models listed above")
    print("2. Choose the model that best fits your needs")
    print("3. Tell me which model you want to use (e.g., 'gemini-1.5-flash-latest')")
    print("4. I'll update all files in the codebase to use your chosen model")

    print("\n💡 TIP: For this application, 'gemini-1.5-flash' is recommended because:")
    print("   - Fast response times (important for user experience)")
    print("   - Lower cost per API call")
    print("   - Sufficient capability for sentiment analysis")
    print("   - Good balance of speed, cost, and quality")

    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check that your GOOGLE_API_KEY is valid")
    print("2. Ensure you have internet connectivity")
    print("3. Verify the google-generativeai library is installed: pip install google-generativeai")
    exit(1)
