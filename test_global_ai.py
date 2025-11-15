"""
Quick test script for Global AI Analysis integration
"""
import streamlit as st
from src.analysis.global_ai_analyzer import get_global_ai_analyzer, AI_MODELS

def test_api_keys():
    """Test which API keys are configured"""
    print("\n" + "="*60)
    print("🔑 TESTING API KEY CONFIGURATION")
    print("="*60 + "\n")
    
    try:
        # Load secrets
        if hasattr(st, 'secrets'):
            secrets = st.secrets
            
            # Check each model
            models_status = {
                'claude': ('ANTHROPIC_API_KEY', 'Claude 3.5 Sonnet'),
                'gpt4': ('OPENAI_API_KEY', 'GPT-4 Turbo'),
                'gemini': ('GOOGLE_API_KEY', 'Gemini Pro'),
                'grok': ('XAI_API_KEY', 'Grok Beta')
            }
            
            available = []
            for model_id, (key_name, model_name) in models_status.items():
                try:
                    key = secrets.get(key_name, "")
                    if key and key.strip() and not key.startswith("#"):
                        print(f"✅ {model_name:20s} - Key configured ({len(key)} chars)")
                        available.append(model_id)
                    else:
                        print(f"❌ {model_name:20s} - Key missing or empty")
                except Exception as e:
                    print(f"❌ {model_name:20s} - Error: {e}")
            
            print(f"\n📊 Total models available: {len(available)}/4")
            print(f"   Models: {', '.join(available)}")
            
            if len(available) >= 2:
                print("\n✅ READY for multi-model consensus!")
            elif len(available) == 1:
                print("\n⚠️  Only 1 model - will work but no consensus")
            else:
                print("\n❌ No models available - add API keys to secrets.toml")
                
            return available
            
    except Exception as e:
        print(f"❌ Error loading secrets: {e}")
        return []


def test_analyzer_initialization():
    """Test if GlobalAIAnalyzer initializes correctly"""
    print("\n" + "="*60)
    print("🤖 TESTING ANALYZER INITIALIZATION")
    print("="*60 + "\n")
    
    try:
        analyzer = get_global_ai_analyzer()
        print("✅ GlobalAIAnalyzer initialized successfully")
        
        available = analyzer.get_available_models()
        print(f"✅ Available models detected: {len(available)}")
        for model_id in available:
            model = AI_MODELS[model_id]
            print(f"   • {model.name} ({model.weight*100:.0f}% weight, {model.max_tokens} tokens)")
        
        return True
    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_configs():
    """Test model configurations"""
    print("\n" + "="*60)
    print("⚙️  TESTING MODEL CONFIGURATIONS")
    print("="*60 + "\n")
    
    total_weight = sum(model.weight for model in AI_MODELS.values())
    print(f"Total weight: {total_weight*100:.0f}% {'✅' if abs(total_weight - 1.0) < 0.01 else '❌'}")
    
    print("\nModel configurations:")
    for model_id, model in AI_MODELS.items():
        print(f"\n{model.name}:")
        print(f"  Provider: {model.provider}")
        print(f"  Weight: {model.weight*100:.0f}%")
        print(f"  Max tokens: {model.max_tokens}")
        print(f"  Endpoint: {model.api_endpoint}")
        print(f"  Requires key: {model.requires_key}")


def test_ui_imports():
    """Test if UI components can be imported"""
    print("\n" + "="*60)
    print("🖥️  TESTING UI COMPONENT IMPORTS")
    print("="*60 + "\n")
    
    try:
        from src.ui_utils.global_ai_panel import (
            render_floating_ai_button,
            check_and_run_global_ai,
            render_ai_analysis_panel
        )
        print("✅ All UI components imported successfully")
        print("   • render_floating_ai_button")
        print("   • check_and_run_global_ai")
        print("   • render_ai_analysis_panel")
        return True
    except Exception as e:
        print(f"❌ UI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "GLOBAL AI ANALYSIS TEST" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run tests
    api_status = test_api_keys()
    analyzer_status = test_analyzer_initialization()
    test_model_configs()
    ui_status = test_ui_imports()
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"API Keys:      {'✅ PASS' if api_status else '❌ FAIL'} ({len(api_status)}/4 models)")
    print(f"Analyzer:      {'✅ PASS' if analyzer_status else '❌ FAIL'}")
    print(f"UI Components: {'✅ PASS' if ui_status else '❌ FAIL'}")
    
    all_pass = api_status and analyzer_status and ui_status
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL TESTS PASSED - System ready to use!")
        print("\nNext steps:")
        print("1. Run: streamlit run dashboard_selector.py")
        print("2. Navigate to Stocks dashboard")
        print("3. Enter a ticker (e.g., AAPL)")
        print("4. Click '🚀 Analyze Everything' in sidebar")
        print("5. View results in '🤖 AI Analysis' tab")
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
