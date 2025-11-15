"""
Based on Gemini API documentation, the correct model names for v1beta are:

For generateContent method:
- models/gemini-pro (base model, being deprecated)
- models/gemini-1.5-flash
- models/gemini-1.5-flash-001  
- models/gemini-1.5-pro
- models/gemini-1.5-pro-001
- models/gemini-2.0-flash-exp (experimental)

The error says "models/gemini-1.5-pro-latest is not found" which means
-latest suffix doesn't exist.

We should use: models/gemini-1.5-pro or models/gemini-1.5-pro-001
"""

import os
import requests

# To check available models, paste your API key here:
API_KEY = "YOUR_API_KEY_HERE"  # Replace with actual key

if API_KEY == "YOUR_API_KEY_HERE":
    print(__doc__)
    print("\n" + "="*70)
    print("RECOMMENDED FIX:")
    print("="*70)
    print("\nUse one of these model names in global_ai_analyzer.py:")
    print("  1. gemini-1.5-pro (recommended - stable)")
    print("  2. gemini-1.5-flash (faster, cheaper)")
    print("  3. gemini-1.5-pro-001 (version-locked)")
    print("\nThe URL should be:")
    print("  https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        models = [m for m in data.get('models', []) 
                 if 'generateContent' in m.get('supportedGenerationMethods', [])]
        
        print("\n" + "="*70)
        print(f"Found {len(models)} Gemini models that support generateContent:")
        print("="*70 + "\n")
        
        for model in models:
            print(f"✓ {model['name']}")
            print(f"  Display: {model.get('displayName', 'N/A')}")
            print(f"  Description: {model.get('description', 'N/A')[:80]}...")
            print()
    else:
        print(f"Error {response.status_code}: {response.text}")
