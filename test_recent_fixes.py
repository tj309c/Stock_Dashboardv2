"""
Test script for recent bug fixes:
1. Google API key configuration
2. Plotly annotation font bgcolor fix
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_google_api_key():
    """Test that GOOGLE_API_KEY is accessible in secrets"""
    print("=" * 60)
    print("TEST 1: Google API Key Configuration")
    print("=" * 60)

    try:
        import streamlit as st

        # Check if both keys exist
        has_gemini = 'GEMINI_API_KEY' in st.secrets
        has_google = 'GOOGLE_API_KEY' in st.secrets

        print(f"✓ GEMINI_API_KEY exists: {has_gemini}")
        print(f"✓ GOOGLE_API_KEY exists: {has_google}")

        if has_google and has_gemini:
            # Verify they're the same value
            same_value = st.secrets['GEMINI_API_KEY'] == st.secrets['GOOGLE_API_KEY']
            print(f"✓ Both keys have same value: {same_value}")

            if same_value:
                print("\n✅ TEST PASSED: Google API key is properly configured")
                return True
            else:
                print("\n❌ TEST FAILED: Keys have different values")
                return False
        else:
            print("\n❌ TEST FAILED: One or both keys missing")
            return False

    except Exception as e:
        print(f"\n❌ TEST FAILED with error: {e}")
        return False


def test_plotly_annotation_fix():
    """Test that visual_analysis_presets.py doesn't have invalid bgcolor in annotation_font"""
    print("\n" + "=" * 60)
    print("TEST 2: Plotly Annotation Font Fix")
    print("=" * 60)

    try:
        file_path = 'visual_analysis_presets.py'

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for the problematic pattern
        problematic_pattern = "annotation_font=dict(size=10, color='#FFA726', bgcolor="

        if problematic_pattern in content:
            print(f"❌ TEST FAILED: Found invalid bgcolor in annotation_font")
            print(f"   Pattern: {problematic_pattern}")
            return False
        else:
            print("✓ No invalid bgcolor in annotation_font found")

            # Check that the fix is in place (annotation_font without bgcolor)
            fixed_pattern = "annotation_font=dict(size=10, color='#FFA726')"

            if fixed_pattern in content:
                print(f"✓ Confirmed fix is in place")
                print(f"   Pattern: {fixed_pattern}")
                print("\n✅ TEST PASSED: Plotly annotation fix verified")
                return True
            else:
                print("⚠️  Warning: Expected fixed pattern not found")
                print("   This might be okay if the code was refactored differently")
                return True  # Still pass since the error pattern is gone

    except FileNotFoundError:
        print(f"❌ TEST FAILED: File {file_path} not found")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED with error: {e}")
        return False


def test_ai_model_config_supports_both_keys():
    """Test that ai_model_config.py supports both GOOGLE_API_KEY and GEMINI_API_KEY"""
    print("\n" + "=" * 60)
    print("TEST 3: AI Model Config Dual Key Support")
    print("=" * 60)

    try:
        file_path = 'ai_model_config.py'

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for dual key support patterns
        checks = {
            "Provider key list includes both": "AIProvider.GEMINI: ['GOOGLE_API_KEY', 'GEMINI_API_KEY']",
            "Checks for GOOGLE_API_KEY": "'GOOGLE_API_KEY' in st.secrets",
            "Checks for GEMINI_API_KEY": "'GEMINI_API_KEY' in st.secrets",
        }

        all_passed = True
        for check_name, pattern in checks.items():
            if pattern in content:
                print(f"✓ {check_name}")
            else:
                print(f"❌ Missing: {check_name}")
                all_passed = False

        if all_passed:
            print("\n✅ TEST PASSED: AI model config supports both key names")
            return True
        else:
            print("\n❌ TEST FAILED: Some dual key support patterns missing")
            return False

    except FileNotFoundError:
        print(f"❌ TEST FAILED: File {file_path} not found")
        return False
    except Exception as e:
        print(f"❌ TEST FAILED with error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING RECENT BUG FIX VALIDATION TESTS")
    print("=" * 60 + "\n")

    results = []

    # Run all tests
    results.append(("Google API Key Configuration", test_google_api_key()))
    results.append(("Plotly Annotation Fix", test_plotly_annotation_fix()))
    results.append(("AI Model Config Dual Key Support", test_ai_model_config_supports_both_keys()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {total} tests")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")

    if failed == 0:
        print("\n🎉 All tests passed! Bug fixes verified successfully.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        sys.exit(1)
