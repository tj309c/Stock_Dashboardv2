"""
Debug script to test Gemini model discovery
"""
import os
import sys

print("="*70)
print("GEMINI MODEL DISCOVERY DEBUG")
print("="*70)

# Test 1: Check if google.generativeai is installed
print("\n1. Testing google.generativeai import...")
try:
    import google.generativeai as genai
    print(f"   ✓ SUCCESS - Version: {genai.__version__}")
except ImportError as e:
    print(f"   ✗ FAILED - {e}")
    sys.exit(1)

# Test 2: Check for API key
print("\n2. Checking for GOOGLE_API_KEY...")
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f"   ✓ Found in environment (length: {len(api_key)})")
else:
    print("   ⚠ Not found in environment")
    
    # Try streamlit secrets
    try:
        import streamlit as st
        api_key = st.secrets.get('GOOGLE_API_KEY', '')
        if api_key:
            print(f"   ✓ Found in Streamlit secrets (length: {len(api_key)})")
        else:
            print("   ✗ Not found in Streamlit secrets either")
    except:
        print("   ⚠ Could not check Streamlit secrets")

if not api_key:
    print("\n   ERROR: No API key found. Cannot proceed.")
    sys.exit(1)

# Test 3: Configure and list models
print("\n3. Configuring Gemini SDK and listing models...")
try:
    genai.configure(api_key=api_key)
    print("   ✓ SDK configured successfully")
except Exception as e:
    print(f"   ✗ Configuration failed: {e}")
    sys.exit(1)

# Test 4: List all models
print("\n4. Listing available models...")
try:
    all_models = list(genai.list_models())
    print(f"   ✓ Found {len(all_models)} total models")
    
    # Filter for generateContent support
    generate_models = []
    for m in all_models:
        if 'generateContent' in m.supported_generation_methods:
            generate_models.append(m)
    
    print(f"   ✓ Found {len(generate_models)} models with generateContent support")
    
    if generate_models:
        print("\n5. Models supporting generateContent:")
        for i, model in enumerate(generate_models, 1):
            print(f"   {i}. {model.name}")
            print(f"      Display: {model.display_name}")
            print(f"      Methods: {', '.join(model.supported_generation_methods)}")
            print()
    else:
        print("\n   ⚠ No models found with generateContent support!")
        
except Exception as e:
    print(f"   ✗ Listing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test the discovery logic
print("\n6. Testing model discovery logic (like in GlobalAIAnalyzer)...")
try:
    gemini_1_5_pro_latest = None
    gemini_pro_models = []
    gemini_flash_models = []
    other_generative_models = []
    
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if "gemini-1.5-pro-latest" in m.name:
                gemini_1_5_pro_latest = m.name
            elif "gemini-1.5-pro" in m.name:
                gemini_pro_models.append(m.name)
            elif "gemini-1.0-pro" in m.name or "gemini-pro" in m.name:
                gemini_pro_models.append(m.name)
            elif "gemini-flash" in m.name:
                gemini_flash_models.append(m.name)
            else:
                other_generative_models.append(m.name)
    
    print(f"   1.5-pro-latest: {gemini_1_5_pro_latest or 'None'}")
    print(f"   1.5-pro models: {gemini_pro_models or 'None'}")
    print(f"   Flash models: {gemini_flash_models or 'None'}")
    print(f"   Other models: {other_generative_models or 'None'}")
    
    # Select best
    selected = None
    if gemini_1_5_pro_latest:
        selected = gemini_1_5_pro_latest
    elif gemini_pro_models:
        selected = gemini_pro_models[0]
    elif gemini_flash_models:
        selected = gemini_flash_models[0]
    elif other_generative_models:
        selected = other_generative_models[0]
    
    if selected:
        print(f"\n   ✓ SELECTED MODEL: {selected}")
        
        # Extract model ID for API endpoint
        model_id = selected.replace('models/', '') if 'models/' in selected else selected
        print(f"   ✓ MODEL ID FOR API: {model_id}")
        print(f"   ✓ API ENDPOINT: https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent")
    else:
        print("\n   ✗ ERROR: No suitable model found!")
        
except Exception as e:
    print(f"   ✗ Discovery logic failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("ALL TESTS PASSED!")
print("="*70)
