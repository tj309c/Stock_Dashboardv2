import json
import ast
import time
# import google.generativeai as genai # Assuming this is configured elsewhere

# Placeholder for actual Gemini setup, replace with your actual configuration
# For the purpose of providing a complete runnable file without actual API keys
# or external dependencies for the fix itself, we'll use a simple mock:
class _MockGeminiModel:
    def generate_content(self, prompt_parts, generation_config=None):
        # Simulate a response. In a real scenario, this would be an actual API call.
        # This mock provides various responses to test the fix.
        prompt_str = str(prompt_parts)
        if "empty_code_test" in prompt_str:
            return type('obj', (object,), {'text': '```python\n\n```'})()
        if "empty_json_test" in prompt_str:
            return type('obj', (object,), {'text': '```json\n\n```'})()
        if "empty_string_no_fences_test" in prompt_str:
            return type('obj', (object,), {'text': ''})()
        if "whitespace_only_test" in prompt_str:
            return type('obj', (object,), {'text': '```python\n   \n```'})()
        
        # Default good responses
        if 'python' in prompt_str.lower():
            return type('obj', (object,), {'text': '```python\n# AI generated code\nprint("Hello from AI")\n```'})()
        if 'json' in prompt_str.lower():
            return type('obj', (object,), {'text': '```json\n{"status": "success", "message": "Good result"}\n```'})()
        
        return type('obj', (object,), {'text': 'Default AI response'})()

GEMINI_MODEL = _MockGeminiModel() # Replace with actual genai.GenerativeModel(...)
MAX_LOOPS = 3 # Maximum attempts for Gemini API calls


def strip_markdown_fences(code_string: str) -> str:
    """
    Strips markdown code fences (```python or ```json) from a string.
    """
    lines = code_string.strip().split('\n')
    if len(lines) > 0 and lines[0].strip().startswith('```') and lines[-1].strip().startswith('```'):
        # Remove first and last line (fences) and strip any surrounding whitespace
        return '\n'.join(lines[1:-1]).strip()
    return code_string.strip()


def get_gemini_prompt_and_schema(code_context: str) -> tuple[str, dict]:
    """
    Generates the Gemini prompt and JSON schema for code analysis.
    """
    json_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low", "info"]},
                "file": {"type": "string", "description": "The file path where the issue was found."},
                "line": {"type": "integer", "description": "The line number in the file where the issue was found."},
                "issue_type": {"type": "string", "description": "A concise category for the issue (e.g., 'Unhandled Exception', 'Logical Error', 'Performance Bottleneck')."},
                "description": {"type": "string", "description": "A detailed explanation of the issue, including potential impact."},
                "suggestion": {"type": "string", "description": "A concrete, actionable suggestion to fix the issue, ideally with a code snippet."}
            },
            "required": ["severity", "file", "line", "issue_type", "description", "suggestion"]
        }
    }

    prompt = f"""
You are an expert-level Senior Software Engineer and Master Code Auditor, specializing in Python. I am providing you with the complete source code for a Python project. Your mission is to act as a static analysis and logical debugging tool.

Your task is to perform a comprehensive, file-by-file audit of the entire project to identify ANY and ALL issues that could:
1.  Cause a runtime crash (e.g., `AttributeError`, `KeyError`, `TypeError`, `IndexError`, unhandled exceptions).
2.  Represent a "logical fallacy" or bug in the application's behavior (e.g., incorrect calculations, flawed "if" conditions, off-by-one errors, incorrect data handling, improper state management).
3.  Prevent the code from running as intended (e.g., infinite loops, hardcoded paths that will fail, missing imports, uninitialized variables).

---
THE CODE WILL BE PROVIDED IN THE FOLLOWING FORMAT:
ANALYSIS RULES:
1.  **Analyze Holistically**: Do not just look at files in isolation. An error in `file_A.py` might be caused by its usage in `file_B.py`.
2.  **Find Root Causes**: Assume *nothing*. If a variable *could* be `None` and is then used without a check, that is a critical issue.
3.  **Find Logical Flaws**: This is your most important task. Go beyond simple syntax. Question the *logic* of the application.

{code_context}
---
Begin your analysis. I will now provide the project code.
"""
    return prompt, json_schema

def get_gemini_fix(prompt: str, response_type: str = 'python', output_schema: dict = None, verbose: bool = False) -> str | list | None:
    """
    Sends a prompt to the Gemini API, handling retries, rate limits, and response parsing.
    """
    if not GEMINI_MODEL:
        print("   ⚠️ GEMINI_MODEL is not initialized. Cannot ask Gemini for a fix.")
        return None

    for attempt in range(MAX_LOOPS):
        print(f"   🤖 Asking Gemini for a fix... (Attempt {attempt + 1}/{MAX_LOOPS})")
        try:
            if verbose:
                print("\n--- BEGIN AI PROMPT (verbose mode) ---")
                print(prompt)
                print("--- END AI PROMPT ---\n")

            generation_config = None # This is line 159 from the snippet

            # Placeholder for actual Gemini API call.
            # In a real scenario, this would be:
            # response = GEMINI_MODEL.generate_content(
            #     [prompt, output_schema] if output_schema else prompt,
            #     generation_config=generation_config
            # )
            # raw_ai_response_text = response.text

            # For the mock, we call the mock model directly
            response = GEMINI_MODEL.generate_content(
                [prompt, output_schema] if output_schema else prompt,
                generation_config=generation_config
            )
            raw_ai_response_text = response.text

            # --- START OF THE FIX ---
            # Strip markdown fences from the AI response
            fixed_code = strip_markdown_fences(raw_ai_response_text)

            # Add a specific check for an empty string *before* attempting json.loads or ast.parse.
            # This directly addresses the described issue where `json.loads('')` or `ast.parse('')` fail.
            if not fixed_code:
                raise ValueError("AI returned an empty string after stripping markdown, cannot parse.")
            # --- END OF THE FIX ---

            # Parse the response based on the expected type
            if response_type == 'json' and output_schema:
                try:
                    if verbose:
                        print(f"   Attempting to parse JSON response (Attempt {attempt + 1})...")
                        print(f"   Raw JSON string after stripping:\n---\n{fixed_code}\n---")
                    
                    parsed_response = json.loads(fixed_code)
                    
                    # Add any schema validation here if needed, e.g., using jsonschema.validate
                    # from jsonschema import validate
                    # validate(instance=parsed_response, schema=output_schema)

                    return parsed_response
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON decoding failed: {e}. AI response:\n---\n{fixed_code}\n---")
                    # This existing check (or similar) handles cases where fixed_code
                    # contains only whitespace, which `json.loads` would also fail on.
                    if not fixed_code.strip():
                        print("   (Detected AI returned only whitespace after stripping for JSON)")
                        raise ValueError("AI returned only whitespace, cannot parse as JSON.") from e
                    time.sleep(1) # Backoff
                    continue # Retry
                except ValueError as e: # Catch schema validation errors or other custom ValueErrors
                    print(f"   ❌ Validation error during JSON processing: {e}")
                    time.sleep(1) # Backoff
                    continue # Retry
                
            elif response_type == 'python':
                try:
                    if verbose:
                        print(f"   Attempting to parse Python response (Attempt {attempt + 1})...")
                        print(f"   Raw Python code after stripping:\n---\n{fixed_code}\n---")

                    ast.parse(fixed_code) # This validates Python syntax
                    return fixed_code
                except SyntaxError as e:
                    print(f"   ❌ Python syntax error: {e}. AI response:\n---\n{fixed_code}\n---")
                    # This existing check (or similar) handles cases where fixed_code
                    # contains only whitespace, which `ast.parse` would also fail on.
                    if not fixed_code.strip():
                        print("   (Detected AI returned only whitespace after stripping for Python)")
                        raise ValueError("AI returned only whitespace, cannot parse as Python.") from e
                    time.sleep(1) # Backoff
                    continue # Retry
                except ValueError as e: # Catch the custom 'empty string' error if it wasn't caught before
                    print(f"   ❌ Validation error during Python processing: {e}")
                    time.sleep(1) # Backoff
                    continue # Retry
            else:
                # For response types other than 'python' or 'json' with a schema,
                # we might just return the raw stripped text.
                print(f"   Returning raw stripped AI response for type '{response_type}'.")
                return fixed_code

        except Exception as e:
            print(f"   ⚠️ An unexpected error occurred during API call or processing: {e}")
            time.sleep(1) # Backoff
            continue # Retry

    print(f"   ❌ Failed to get a valid response after {MAX_LOOPS} attempts.")
    return None